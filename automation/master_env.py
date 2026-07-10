#!/usr/bin/env python3
"""Safely inspect and populate the local master env file without printing secrets."""

from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automation"))
from env_file import parse_env_file, update_env_values  # noqa: E402
from workspace_paths import default_code_root  # noqa: E402

DEFAULT_MASTER = default_code_root(REPO_ROOT) / ".env.master"
MASTER_FILE_HEADER = [
    "# Master environment inventory",
    "# Keep this file private. Do not commit it.",
    "",
]
CONTROL_PLANE_KEYS = [
    "SUPABASE_ACCESS_TOKEN",
    "SUPABASE_ORG_ID",
    "VERCEL_TOKEN",
    "VERCEL_TEAM_ID",
    "VERCEL_ORG_ID",
    "GITHUB_TOKEN",
    "GITHUB_APP_ID",
    "GITHUB_APP_PRIVATE_KEY",
    "GITHUB_INSTALLATION_ID",
    "STRIPE_SECRET_KEY",
    "STRIPE_RESTRICTED_KEY",
    "STRIPE_ACCOUNT_ID",
    "RESEND_API_KEY",
    "CLOUDFLARE_API_TOKEN",
    "CLOUDFLARE_ACCOUNT_ID",
    "CLOUDFLARE_ZONE_ID",
    "NAMECHEAP_API_USER",
    "NAMECHEAP_API_KEY",
    "NAMECHEAP_USERNAME",
    "NAMECHEAP_CLIENT_IP",
    "OPENAI_ADMIN_KEY",
    "OPENAI_ORG_ID",
    "OPENAI_PROJECT_ID",
]

PRIORITY_KEYS = [
    "SUPABASE_ACCESS_TOKEN",
    "SUPABASE_ORG_ID",
    "SUPABASE_PROJECT_REF",
    "SUPABASE_URL",
    "SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_DB_PASSWORD",
    "DATABASE_URL",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "PERPLEXITY_API_KEY",
    "RESEND_API_KEY",
    "STRIPE_SECRET_KEY",
    "STRIPE_RESTRICTED_KEY",
    "STRIPE_ACCOUNT_ID",
    "STRIPE_WEBHOOK_SECRET",
    "VERCEL_TOKEN",
    "VERCEL_TEAM_ID",
    "VERCEL_ORG_ID",
    "GITHUB_TOKEN",
]


def update_values(path: Path, updates: dict[str, str], overwrite: bool) -> dict[str, str]:
    return update_env_values(
        path,
        updates,
        overwrite,
        section_comment="# ===== Added by master_env.py =====",
        missing_file_header=MASTER_FILE_HEADER,
    )


def cmd_status(args: argparse.Namespace) -> int:
    values = parse_env_file(Path(args.master).expanduser())
    keys = args.key or (CONTROL_PLANE_KEYS if args.control_plane else PRIORITY_KEYS)
    for key in keys:
        value = values.get(key, "")
        state = "set" if value else "missing"
        print(f"{state}\t{key}")
    return 0


def cmd_missing(args: argparse.Namespace) -> int:
    values = parse_env_file(Path(args.master).expanduser())
    keys = [key for key, value in values.items() if not value]
    if args.control_plane:
        keys = [key for key in CONTROL_PLANE_KEYS if not values.get(key)]
    if args.priority:
        keys = [key for key in PRIORITY_KEYS if not values.get(key)]
    for key in keys:
        print(key)
    return 0


def read_prompted_value(key: str, visible: bool) -> str:
    prompt = f"{key}: "
    if visible:
        return input(prompt).strip()
    return getpass.getpass(prompt).strip()


def cmd_set(args: argparse.Namespace) -> int:
    master = Path(args.master).expanduser()
    updates: dict[str, str] = {}
    for key in args.key:
        value = args.value
        if value is None:
            value = read_prompted_value(key, args.visible)
        if not value:
            print(f"Skipped {key}: blank value", file=sys.stderr)
            continue
        updates[key] = value
    applied = update_values(master, updates, args.overwrite)
    for key in updates:
        print(f"{applied.get(key, 'skipped')}\t{key}")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    master = Path(args.master).expanduser()
    source = Path(args.source).expanduser()
    source_values = parse_env_file(source)
    if args.key:
        source_values = {key: source_values[key] for key in args.key if source_values.get(key)}
    applied = update_values(master, source_values, args.overwrite)
    print(f"source\t{source}")
    print(f"candidate_keys\t{len(source_values)}")
    print(f"applied_keys\t{len(applied)}")
    for key, action in sorted(applied.items()):
        print(f"{action}\t{key}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Populate and inspect .env.master without printing secret values."
    )
    parser.add_argument("--master", default=str(DEFAULT_MASTER), help="Path to the master env file")
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show redacted set/missing status")
    status.add_argument("--key", action="append", help="Specific key to check")
    status.add_argument(
        "--control-plane", action="store_true", help="Show account/provider-level automation keys"
    )
    status.set_defaults(func=cmd_status)

    missing = subparsers.add_parser("missing", help="List blank keys")
    missing.add_argument(
        "--priority", action="store_true", help="Only list priority automation keys"
    )
    missing.add_argument(
        "--control-plane",
        action="store_true",
        help="Only list account/provider-level automation keys",
    )
    missing.set_defaults(func=cmd_missing)

    set_cmd = subparsers.add_parser(
        "set", help="Set one or more keys, prompting without echo by default"
    )
    set_cmd.add_argument("key", nargs="+", help="Env key(s) to set")
    set_cmd.add_argument(
        "--value", help="Value to use for a single key; less safe because shells may record it"
    )
    set_cmd.add_argument("--visible", action="store_true", help="Show typed input while prompting")
    set_cmd.add_argument("--overwrite", action="store_true", help="Overwrite existing values")
    set_cmd.set_defaults(func=cmd_set)

    merge = subparsers.add_parser("merge", help="Merge values from another env file")
    merge.add_argument("--source", required=True, help="Source env file")
    merge.add_argument("--key", action="append", help="Only merge a specific key")
    merge.add_argument("--overwrite", action="store_true", help="Overwrite existing values")
    merge.set_defaults(func=cmd_merge)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "set" and args.value is not None and len(args.key) != 1:
        parser.error("set --value can only be used with one key")
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
