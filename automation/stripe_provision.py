#!/usr/bin/env python3
"""Plan and apply governed Stripe product, price, and webhook provisioning."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-governance-agent" / "exports"
sys.path.insert(0, str(REPO_ROOT / "automation"))
from workspace_paths import default_code_root  # noqa: E402

DEFAULT_MASTER = default_code_root(REPO_ROOT) / ".env.master"
DEFAULT_MANIFEST = "stripe.billing.json"
STRIPE_API_BASE = "https://api.stripe.com/v1"

DEFAULT_WEBHOOK_EVENTS = [
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.paid",
    "invoice.payment_failed",
]


def parse_env_value(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    if value[:1] in {"'", '"'}:
        try:
            return shlex.split(value, comments=False)[0]
        except ValueError:
            return value.strip("'\"")
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.removeprefix("export ").strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            values[key] = parse_env_value(raw_value)
    return values


def format_env_value(value: str) -> str:
    if not value:
        return ""
    if re.search(r"\s|#", value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def update_env_file(path: Path, updates: dict[str, str], overwrite: bool) -> dict[str, str]:
    existing = parse_env_file(path)
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines() if path.exists() else []
    rendered: list[str] = []
    seen: set[str] = set()
    applied: dict[str, str] = {}
    for line in lines:
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$", line)
        if not match:
            rendered.append(line)
            continue
        key = match.group(1)
        seen.add(key)
        if key in updates and (overwrite or not existing.get(key)):
            rendered.append(f"{key}={format_env_value(updates[key])}")
            applied[key] = "updated" if existing.get(key) else "filled"
        else:
            rendered.append(line)
    missing = [key for key in updates if key not in seen]
    if missing:
        if rendered and rendered[-1].strip():
            rendered.append("")
        rendered.append("# ===== Stripe provisioned values =====")
        for key in missing:
            rendered.append(f"{key}={format_env_value(updates[key])}")
            applied[key] = "added"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(rendered).rstrip() + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    return applied


def load_manifest(project: Path, manifest_path: Path | None) -> dict[str, Any]:
    path = manifest_path or (project / DEFAULT_MANIFEST)
    if not path.exists():
        raise FileNotFoundError(f"Stripe billing manifest not found: {path}")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Stripe billing manifest must be a JSON object.")
    return manifest


def default_manifest(project: Path) -> dict[str, Any]:
    slug = project.name
    return {
        "project_slug": slug,
        "mode": "test",
        "currency": "cad",
        "provision_prices": True,
        "products": [
            {
                "key": "starter",
                "name": f"{slug} Starter",
                "description": "Starter subscription plan.",
                "prices": [
                    {
                        "key": "starter_monthly",
                        "env": "STRIPE_PRICE_STARTER",
                        "lookup_key": f"{slug}_starter_monthly",
                        "unit_amount": 900,
                        "currency": "cad",
                        "interval": "month",
                    }
                ],
            }
        ],
        "webhook": {
            "url": "https://example.com/api/stripe/webhook",
            "secret_env": "STRIPE_WEBHOOK_SECRET",
            "events": DEFAULT_WEBHOOK_EVENTS,
        },
        "notes": [
            "Edit this manifest before applying.",
            "Use test mode first, then intentionally repeat for live mode.",
        ],
    }


def write_manifest_template(project: Path, output: Path | None) -> Path:
    target = output or (project / DEFAULT_MANIFEST)
    if target.exists():
        raise FileExistsError(f"Refusing to overwrite existing manifest: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(default_manifest(project), indent=2) + "\n", encoding="utf-8")
    return target


def flatten_params(data: dict[str, Any], prefix: str | None = None) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for key, value in data.items():
        name = f"{prefix}[{key}]" if prefix else key
        if value is None:
            continue
        if isinstance(value, dict):
            pairs.extend(flatten_params(value, name))
        elif isinstance(value, list):
            for item in value:
                pairs.append((f"{name}[]", str(item)))
        elif isinstance(value, bool):
            pairs.append((name, "true" if value else "false"))
        else:
            pairs.append((name, str(value)))
    return pairs


class StripeClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        encoded = urllib.parse.urlencode(flatten_params(params or {})).encode("utf-8")
        url = f"{STRIPE_API_BASE}{path}"
        if method == "GET" and encoded:
            url = f"{url}?{encoded.decode('utf-8')}"
            body = None
        else:
            body = encoded if method != "GET" else None
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body_text = error.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Stripe API {method} {path} failed with {error.code}: {body_text}") from error


def stripe_key_for_mode(values: dict[str, str], mode: str) -> tuple[str, str]:
    candidates = ["STRIPE_RESTRICTED_KEY", "STRIPE_SECRET_KEY"]
    for key in candidates:
        value = values.get(key, "")
        if not value:
            continue
        if mode == "test" and "_live_" in value:
            continue
        if mode == "live" and "_test_" in value:
            continue
        return key, value
    raise ValueError(f"No Stripe API key for mode {mode!r}; set STRIPE_RESTRICTED_KEY or STRIPE_SECRET_KEY.")


def price_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for product in manifest.get("products", []):
        for price in product.get("prices", []):
            merged = dict(price)
            merged["product_key"] = product.get("key") or product.get("name")
            merged["product_name"] = product.get("name")
            merged["product_description"] = product.get("description")
            entries.append(merged)
    return entries


def build_plan(project: Path, master: Path, manifest_path: Path | None, mode: str | None) -> dict[str, Any]:
    project = project.expanduser().resolve()
    master = master.expanduser().resolve()
    manifest = load_manifest(project, manifest_path)
    selected_mode = mode or manifest.get("mode", "test")
    master_values = parse_env_file(master)
    key_name = None
    key_available = False
    try:
        key_name, _ = stripe_key_for_mode(master_values, selected_mode)
        key_available = True
    except ValueError:
        pass
    webhook = manifest.get("webhook") or {}
    prices = price_entries(manifest) if manifest.get("provision_prices", True) else []
    return {
        "plan_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project),
        "master_env": str(master),
        "manifest": manifest,
        "mode": selected_mode,
        "policy": {
            "test_mode_first": True,
            "prints_secret_values": False,
            "requires_apply": True,
            "writes_generated_values_to_master_env": True,
        },
        "stripe_key": {
            "available": key_available,
            "env": key_name,
        },
        "planned_actions": {
            "products": [
                {
                    "key": product.get("key"),
                    "name": product.get("name"),
                    "prices": [price.get("lookup_key") or price.get("key") for price in product.get("prices", [])],
                }
                for product in manifest.get("products", [])
            ]
            if manifest.get("provision_prices", True)
            else [],
            "webhook": {
                "url": webhook.get("url"),
                "events": webhook.get("events", DEFAULT_WEBHOOK_EVENTS),
                "secret_env": webhook.get("secret_env", "STRIPE_WEBHOOK_SECRET"),
            }
            if webhook
            else None,
        },
        "summary": {
            "project_slug": manifest.get("project_slug", project.name),
            "mode": selected_mode,
            "price_count": len(prices),
            "webhook_requested": bool(webhook),
            "ready_for_apply": key_available,
        },
    }


def write_plan(plan: dict[str, Any], output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = plan["summary"]["project_slug"]
        output = EXPORT_ROOT / f"stripe-{slug}-{plan['mode']}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def search_product(client: StripeClient, project_slug: str, product_key: str) -> dict[str, Any] | None:
    query = f"metadata['project_slug']:'{project_slug}' AND metadata['manifest_key']:'{product_key}'"
    result = client.request("GET", "/products/search", {"query": query, "limit": 1})
    data = result.get("data", [])
    return data[0] if data else None


def ensure_product(client: StripeClient, manifest: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    project_slug = manifest.get("project_slug", "unknown-project")
    product_key = product.get("key") or re.sub(r"\W+", "_", product.get("name", "product")).strip("_").lower()
    existing = search_product(client, project_slug, product_key)
    if existing:
        return existing
    return client.request(
        "POST",
        "/products",
        {
            "name": product["name"],
            "description": product.get("description"),
            "active": product.get("active", True),
            "metadata": {
                "project_slug": project_slug,
                "manifest_key": product_key,
            },
        },
    )


def find_price_by_lookup_key(client: StripeClient, lookup_key: str) -> dict[str, Any] | None:
    result = client.request("GET", "/prices", {"lookup_keys": [lookup_key], "active": True, "limit": 1})
    data = result.get("data", [])
    return data[0] if data else None


def ensure_price(client: StripeClient, manifest: dict[str, Any], product_id: str, price: dict[str, Any]) -> dict[str, Any]:
    lookup_key = price.get("lookup_key") or price.get("key")
    if lookup_key:
        existing = find_price_by_lookup_key(client, lookup_key)
        if existing:
            return existing
    params: dict[str, Any] = {
        "product": product_id,
        "currency": price.get("currency", manifest.get("currency", "cad")),
        "unit_amount": price["unit_amount"],
        "nickname": price.get("nickname") or price.get("key"),
        "lookup_key": lookup_key,
        "metadata": {
            "project_slug": manifest.get("project_slug", "unknown-project"),
            "manifest_key": price.get("key") or lookup_key,
        },
    }
    interval = price.get("interval")
    if interval:
        params["recurring"] = {"interval": interval}
        if price.get("interval_count"):
            params["recurring"]["interval_count"] = price["interval_count"]
    return client.request("POST", "/prices", params)


def find_webhook(client: StripeClient, url: str) -> dict[str, Any] | None:
    result = client.request("GET", "/webhook_endpoints", {"limit": 100})
    for endpoint in result.get("data", []):
        if endpoint.get("url") == url and not endpoint.get("deleted"):
            return endpoint
    return None


def ensure_webhook(client: StripeClient, webhook: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    url = webhook["url"]
    events = webhook.get("events") or DEFAULT_WEBHOOK_EVENTS
    existing = find_webhook(client, url)
    if existing:
        updated = client.request(
            "POST",
            f"/webhook_endpoints/{existing['id']}",
            {
                "enabled_events": events,
                "description": webhook.get("description"),
            },
        )
        return updated, False
    created = client.request(
        "POST",
        "/webhook_endpoints",
        {
            "url": url,
            "enabled_events": events,
            "description": webhook.get("description"),
            "metadata": webhook.get("metadata", {}),
        },
    )
    return created, True


def apply_plan(plan: dict[str, Any], master: Path, overwrite_env: bool) -> dict[str, Any]:
    master_values = parse_env_file(master)
    key_name, key_value = stripe_key_for_mode(master_values, plan["mode"])
    client = StripeClient(key_value)
    manifest = plan["manifest"]
    generated: dict[str, str] = {}
    product_results: list[dict[str, str]] = []
    price_results: list[dict[str, str]] = []

    if manifest.get("provision_prices", True):
        for product in manifest.get("products", []):
            stripe_product = ensure_product(client, manifest, product)
            product_results.append({"key": product.get("key", ""), "id": stripe_product["id"]})
            for price in product.get("prices", []):
                stripe_price = ensure_price(client, manifest, stripe_product["id"], price)
                price_results.append({"key": price.get("key", ""), "id": stripe_price["id"]})
                env_key = price.get("env")
                if env_key:
                    generated[env_key] = stripe_price["id"]

    webhook_result: dict[str, Any] | None = None
    webhook = manifest.get("webhook") or None
    if webhook:
        endpoint, created = ensure_webhook(client, webhook)
        webhook_result = {"id": endpoint["id"], "created": created, "url": endpoint.get("url")}
        if created and endpoint.get("secret") and webhook.get("secret_env"):
            generated[webhook.get("secret_env", "STRIPE_WEBHOOK_SECRET")] = endpoint["secret"]
        elif webhook.get("secret_env"):
            webhook_result["secret_note"] = "Existing Stripe webhook secrets are not retrievable; keep the current env value or rotate the endpoint secret manually."

    applied = update_env_file(master, generated, overwrite_env) if generated else {}
    return {
        "mode": plan["mode"],
        "stripe_key_env": key_name,
        "products": product_results,
        "prices": price_results,
        "webhook": webhook_result,
        "master_env_updates": applied,
        "secret_values_printed": False,
    }


def cmd_init(args: argparse.Namespace) -> int:
    output = write_manifest_template(Path(args.project).expanduser().resolve(), Path(args.output).expanduser() if args.output else None)
    print(output)
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    plan = build_plan(
        Path(args.project),
        Path(args.master),
        Path(args.manifest).expanduser() if args.manifest else None,
        args.mode,
    )
    output = write_plan(plan, Path(args.output) if args.output else None)
    print(output)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    if plan["mode"] == "live" and not args.allow_live:
        raise SystemExit("Refusing live Stripe provisioning without --allow-live.")
    result = apply_plan(plan, Path(plan["master_env"]).expanduser(), args.overwrite_env)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed Stripe provisioning from a project billing manifest.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a starter stripe.billing.json manifest.")
    init.add_argument("--project", required=True, help="Path to the target project")
    init.add_argument("--output", help="Optional manifest output path")
    init.set_defaults(func=cmd_init)

    plan = subparsers.add_parser("plan", help="Create a redacted Stripe provisioning plan.")
    plan.add_argument("--project", required=True, help="Path to the target project")
    plan.add_argument("--manifest", help="Path to stripe.billing.json")
    plan.add_argument("--master", default=str(DEFAULT_MASTER), help="Path to .env.master")
    plan.add_argument("--mode", choices=["test", "live"], help="Override manifest mode")
    plan.add_argument("--output", help="Optional plan output path")
    plan.set_defaults(func=cmd_plan)

    apply_cmd = subparsers.add_parser("apply", help="Apply a Stripe provisioning plan.")
    apply_cmd.add_argument("--plan", required=True, help="Path to a Stripe provisioning plan JSON")
    apply_cmd.add_argument("--allow-live", action="store_true", help="Allow live-mode provisioning")
    apply_cmd.add_argument("--overwrite-env", action="store_true", help="Overwrite generated values already present in .env.master")
    apply_cmd.set_defaults(func=cmd_apply)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
