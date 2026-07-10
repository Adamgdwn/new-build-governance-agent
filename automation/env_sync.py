#!/usr/bin/env python3
"""Governed environment sync from a local master env file into a project env file."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-governance-agent" / "exports"
sys.path.insert(0, str(REPO_ROOT / "automation"))
from workspace_paths import default_code_root  # noqa: E402

DEFAULT_MASTER = default_code_root(REPO_ROOT) / ".env.master"
DEFAULT_TARGET = ".env.local"
ENV_TEMPLATE_NAMES = [
    ".env.example",
    ".env.local.example",
    ".env.template",
    "config/secrets.example.env",
]
CODE_REF_PATTERNS = [
    re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\bprocess\.env\[['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\]"),
    re.compile(r"\bimport\.meta\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"\b(?:os\.)?getenv\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\)"),
    re.compile(r"\bDeno\.env\.get\(['\"]([A-Za-z_][A-Za-z0-9_]*)['\"]\)"),
]
SECRET_MARKERS = (
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PRIVATE",
    "SERVICE_ROLE",
    "DATABASE_URL",
    "DB_PASSWORD",
    "WEBHOOK",
    "ACCESS_KEY",
    "REFRESH_TOKEN",
    "CONNECTION_STRING",
)
PUBLIC_MARKERS = (
    "ANON_KEY",
    "PUBLISHABLE",
    "PUBLIC_",
    "VITE_",
)
SCAN_SUFFIXES = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".py",
    ".md",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
}
IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    "target",
    ".venv",
    "venv",
    "__pycache__",
    ".local-data",
    ".cxx",
}
IGNORED_CODE_REF_KEYS = {
    "CI",
    "DEBUG",
    "DISPLAY",
    "HOME",
    "NODE_ENV",
    "PATH",
    "PWD",
    "SHELL",
    "TERM",
    "USER",
    "WAYLAND_DISPLAY",
}


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


def is_privileged_key(key: str) -> bool:
    upper = key.upper()
    if any(marker in upper for marker in PUBLIC_MARKERS):
        return False
    return any(marker in upper for marker in SECRET_MARKERS)


def should_scan(path: Path) -> bool:
    if any(part in IGNORE_DIRS for part in path.parts):
        return False
    if not path.is_file():
        return False
    if path.name.startswith(".env") or path.name.endswith(".env"):
        return True
    return path.suffix in SCAN_SUFFIXES


def discover_required_keys(project: Path, include_code_refs: bool) -> dict[str, list[str]]:
    required: dict[str, list[str]] = {}

    def add(key: str, source: str) -> None:
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            return
        required.setdefault(key, [])
        if source not in required[key]:
            required[key].append(source)

    for relative in ENV_TEMPLATE_NAMES:
        template = project / relative
        if not template.exists():
            continue
        for key in parse_env_file(template):
            add(key, relative)

    if include_code_refs:
        for path in project.rglob("*"):
            if not should_scan(path):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            relative = str(path.relative_to(project))
            for pattern in CODE_REF_PATTERNS:
                for match in pattern.finditer(content):
                    key = match.group(1)
                    if key not in IGNORED_CODE_REF_KEYS:
                        add(key, relative)

    return dict(sorted(required.items()))


def build_sync_plan(
    project: Path,
    master: Path,
    target: str,
    include_code_refs: bool,
    requested_keys: list[str],
) -> dict:
    project = project.expanduser().resolve()
    master = master.expanduser().resolve()
    master_values = parse_env_file(master)
    project_target = project / target
    try:
        project_target.resolve().relative_to(project)
    except ValueError:
        raise ValueError(
            f"--target {target!r} resolves outside the project root; path traversal is not allowed"
        )
    target_values = parse_env_file(project_target)
    required = discover_required_keys(project, include_code_refs)
    for key in requested_keys:
        required.setdefault(key, ["manual-request"])

    entries = []
    for key, sources in required.items():
        in_master = key in master_values and bool(master_values[key])
        already_set = key in target_values and bool(target_values[key])
        privileged = is_privileged_key(key)
        if already_set:
            status = "already_set"
        elif in_master:
            status = "ready"
        else:
            status = "missing_from_master"
        entries.append(
            {
                "key": key,
                "status": status,
                "privileged": privileged,
                "sources": sources,
            }
        )

    return {
        "plan_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": str(project),
        "master_env": str(master),
        "target_env": str(project_target),
        "policy": {
            "prints_secret_values": False,
            "writes_only_required_keys": True,
            "privileged_keys_require_include_privileged": True,
            "overwrite_existing_values_by_default": False,
        },
        "summary": {
            "required_keys": len(entries),
            "ready": sum(1 for entry in entries if entry["status"] == "ready"),
            "already_set": sum(1 for entry in entries if entry["status"] == "already_set"),
            "missing_from_master": sum(1 for entry in entries if entry["status"] == "missing_from_master"),
            "privileged_ready": sum(
                1 for entry in entries if entry["status"] == "ready" and entry["privileged"]
            ),
        },
        "entries": entries,
    }


def write_plan(plan: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        slug = Path(plan["project_path"]).name
        output = EXPORT_ROOT / f"env-sync-{slug}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def apply_sync(
    plan: dict,
    include_privileged: bool,
    overwrite: bool,
) -> dict:
    master = Path(plan["master_env"])
    target = Path(plan["target_env"])
    project_root = Path(plan["project_path"]).resolve()
    try:
        target.resolve().relative_to(project_root)
    except ValueError:
        raise ValueError(
            f"target env path {str(target)!r} resolves outside the project root; aborting"
        )
    master_values = parse_env_file(master)
    existing = parse_env_file(target)
    target.parent.mkdir(parents=True, exist_ok=True)

    applied: list[str] = []
    skipped: list[dict[str, str]] = []
    for entry in plan["entries"]:
        key = entry["key"]
        if entry["status"] != "ready":
            skipped.append({"key": key, "reason": entry["status"]})
            continue
        if entry["privileged"] and not include_privileged:
            skipped.append({"key": key, "reason": "privileged_requires_include_privileged"})
            continue
        if key in existing and existing[key] and not overwrite:
            skipped.append({"key": key, "reason": "already_set"})
            continue
        existing[key] = master_values[key]
        applied.append(key)

    lines: list[str] = []
    if target.exists():
        seen: set[str] = set()
        for line in target.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)=", line)
            if match and match.group(1) in existing:
                key = match.group(1)
                seen.add(key)
                lines.append(f"{key}={format_env_value(existing[key])}")
            else:
                lines.append(line)
        missing_lines = [key for key in applied if key not in seen]
    else:
        lines = [
            "# Generated by New Build Governance Agent env_sync.py from a local master env.",
            "# Keep this file private and out of source control.",
            "",
        ]
        missing_lines = applied

    if missing_lines:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# Synced from governed master env")
        for key in missing_lines:
            lines.append(f"{key}={format_env_value(existing[key])}")

    target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.chmod(target, 0o600)
    return {
        "applied_count": len(applied),
        "applied_keys": applied,
        "skipped": skipped,
        "target_env": str(target),
    }


def cmd_plan(args: argparse.Namespace) -> int:
    plan = build_sync_plan(
        Path(args.project),
        Path(args.master),
        args.target,
        args.include_code_refs,
        args.key,
    )
    output = write_plan(plan, Path(args.output) if args.output else None)
    print(output)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    if args.plan:
        plan = json.loads(Path(args.plan).expanduser().read_text(encoding="utf-8"))
    else:
        plan = build_sync_plan(
            Path(args.project),
            Path(args.master),
            args.target,
            args.include_code_refs,
            args.key,
        )
    result = apply_sync(plan, args.include_privileged, args.overwrite)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Governed env sync from .env.master into a project env file.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_cmd = subparsers.add_parser("plan", help="Create a redacted sync plan without writing project env values.")
    plan_cmd.add_argument("--project", required=True, help="Path to the target project")
    plan_cmd.add_argument("--master", default=str(DEFAULT_MASTER), help="Path to the master env file")
    plan_cmd.add_argument("--target", default=DEFAULT_TARGET, help="Target env file relative to the project")
    plan_cmd.add_argument("--key", action="append", default=[], help="Additional required key to include")
    plan_cmd.add_argument("--include-code-refs", action="store_true", help="Also inspect code for env references")
    plan_cmd.add_argument("--output", help="Optional output path for the JSON plan")
    plan_cmd.set_defaults(func=cmd_plan)

    apply_cmd = subparsers.add_parser("apply", help="Apply a sync plan or generate-and-apply one.")
    apply_cmd.add_argument("--plan", help="Path to an env sync plan JSON")
    apply_cmd.add_argument("--project", help="Path to the target project, required when --plan is omitted")
    apply_cmd.add_argument("--master", default=str(DEFAULT_MASTER), help="Path to the master env file")
    apply_cmd.add_argument("--target", default=DEFAULT_TARGET, help="Target env file relative to the project")
    apply_cmd.add_argument("--key", action="append", default=[], help="Additional required key to include")
    apply_cmd.add_argument("--include-code-refs", action="store_true", help="Also inspect code for env references")
    apply_cmd.add_argument("--include-privileged", action="store_true", help="Allow copying privileged/admin keys")
    apply_cmd.add_argument("--overwrite", action="store_true", help="Overwrite existing target env values")
    apply_cmd.set_defaults(func=cmd_apply)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "apply" and not args.plan and not args.project:
        parser.error("apply requires --plan or --project")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
