#!/usr/bin/env python3
"""Version helpers for New Build Governance Agent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PRODUCT_NAME = "New Build Governance Agent"
REPO_SLUG = "new-build-governance-agent"
REPO_OWNER = "Adamgdwn"
REPO_FULL_NAME = f"{REPO_OWNER}/{REPO_SLUG}"
GITHUB_REPO_URL = f"https://github.com/{REPO_FULL_NAME}"
REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "VERSION"


def get_version() -> str:
    return VERSION_FILE.read_text(encoding="utf-8").strip()


def get_version_string() -> str:
    return f"{PRODUCT_NAME} {get_version()}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print the installed New Build Governance Agent version."
    )
    parser.add_argument("--plain", action="store_true", help="Print only the version number.")
    parser.add_argument("--json", action="store_true", help="Print product metadata as JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    version = get_version()
    if args.json:
        print(
            json.dumps(
                {
                    "name": PRODUCT_NAME,
                    "slug": REPO_SLUG,
                    "repository": REPO_FULL_NAME,
                    "repository_url": GITHUB_REPO_URL,
                    "version": version,
                },
                sort_keys=True,
            )
        )
    elif args.plain:
        print(version)
    else:
        print(f"{PRODUCT_NAME} version {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
