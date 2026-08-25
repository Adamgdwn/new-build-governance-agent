#!/usr/bin/env python3
"""Canonical project naming, classification, and initial-scope rules.

Single source of truth for:
- slugify and slug validation (reserved OS names, minimum length),
- governance-level <-> risk-tier mapping and valid value sets,
- INITIAL_SCOPE.md rendering.

new_build_headless.py, new_build_gui.py, scaffold_project.py, and
new_build.sh (via the small CLI at the bottom) all import from here.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime

MIN_SLUG_LENGTH = 2

RESERVED_OS_NAMES = frozenset(
    {
        "con",
        "prn",
        "aux",
        "nul",
        "com1",
        "com2",
        "com3",
        "com4",
        "com5",
        "com6",
        "com7",
        "com8",
        "com9",
        "lpt1",
        "lpt2",
        "lpt3",
        "lpt4",
        "lpt5",
        "lpt6",
        "lpt7",
        "lpt8",
        "lpt9",
    }
)

GOV_TYPES = frozenset(
    {
        "application",
        "website",
        "service",
        "internal-tool",
        "automation",
        "infrastructure",
        "documentation",
        "agent",
        "agentic-harness",
    }
)
GOVERNANCE_LEVELS = frozenset({"0", "1", "2", "3", "4"})
RISK_TIERS = frozenset({"low", "medium", "high", "critical"})
GOVERNANCE_TO_RISK = {
    "0": "low",
    "1": "low",
    "2": "medium",
    "3": "high",
    "4": "critical",
}
RISK_TO_GOVERNANCE = {
    "low": "1",
    "medium": "2",
    "high": "3",
    "critical": "4",
}
BUILD_TYPE_GOV_MAP = {
    "app": "application",
    "agent": "agent",
    "tool": "internal-tool",
    "other": "internal-tool",
}


def slugify(name: str) -> str:
    """Normalize a project name to a filesystem-safe lowercase slug."""
    s = name.lower()
    s = re.sub(r"[ _/]+", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def slug_error(name: str, slug: str) -> str | None:
    """Return a human-readable rejection reason for slug, or None if valid."""
    if not slug:
        return (
            f"project_name {name!r} produced an empty slug after normalization; "
            "use ASCII letters, digits, spaces, or hyphens"
        )
    if len(slug) < MIN_SLUG_LENGTH:
        return (
            f"project_name {name!r} produced a single-character slug {slug!r}; "
            "provide a more descriptive name"
        )
    if "/" in slug or "\\" in slug:
        return f"slug {slug!r} contains a path separator; this should not be possible after slugify"
    if slug.lower() in RESERVED_OS_NAMES:
        return f"slug {slug!r} is a reserved OS name; choose a different project name"
    return None


def validate_project_name(name: str) -> tuple[str, str | None]:
    """Slugify name and validate the result. Returns (slug, error-or-None)."""
    slug = slugify(name)
    return slug, slug_error(name, slug)


def resolve_governance(value: str | int | None = None) -> tuple[str, str]:
    """Resolve a governance level or legacy risk tier to (level, risk_tier)."""
    raw = str(value if value is not None else "2").strip()
    if raw in GOVERNANCE_LEVELS:
        return raw, GOVERNANCE_TO_RISK[raw]
    if raw in RISK_TIERS:
        return RISK_TO_GOVERNANCE[raw], raw
    raise ValueError(
        "Unsupported governance level. Use 0, 1, 2, 3, 4, "
        "or legacy risk tiers low/medium/high/critical."
    )


def render_initial_scope(
    project_name: str,
    slug: str,
    governance_type: str,
    governance_level: str,
    risk_tier: str,
    stack: str,
    primary_builder: str,
    target_dir: str,
    scope_problem: str = "",
    scope_user: str = "",
    scope_mvp: str = "",
    generated_at: str | None = None,
) -> str:
    """Render the canonical INITIAL_SCOPE.md content."""
    if generated_at is None:
        generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    lines = [
        f"# Initial Scope — {project_name}",
        "",
        f"Generated: {generated_at}",
        "",
        "## Classification",
        "",
        "| Field          | Value |",
        "|----------------|-------|",
        f"| Project name   | {project_name} |",
        f"| Slug / dir     | {slug} |",
        f"| Type           | {governance_type} |",
        f"| Governance     | {governance_level} |",
        f"| Risk tier      | {risk_tier} |",
        f"| Stack          | {stack} |",
        f"| Primary model  | {primary_builder} |",
        f"| Location       | {target_dir} |",
        "",
        "## Build approach",
        "",
        f"Primary builder: **{primary_builder}**",
        "",
    ]

    if scope_problem:
        lines += [
            "## Scope brief",
            "",
            f"**Problem:** {scope_problem}",
            "",
            f"**User / consumer:** {scope_user}",
            "",
            f"**MVP:** {scope_mvp}",
            "",
        ]
    else:
        lines += [
            "## Scope brief",
            "",
            "Not captured at intake. Fill in before the first coding session.",
            "",
            "- **Problem:**",
            "- **Primary user / consumer:**",
            "- **MVP:**",
            "",
        ]

    lines += [
        "## First session checklist",
        "",
        "- [ ] Read `START_HERE.md`",
        "- [ ] Review `docs/current-build-pathway.md`",
        "- [ ] Review `docs/standards/README.md`",
        "- [ ] Review `docs/standards/engineering-governance-by-use-case.md`",
        "- [ ] Review `docs/policy/durable-development-engineering-policy.md`",
        "- [ ] Review `docs/standards/ship-ready-engineering-standard.md`",
        "- [ ] Fill in commands in `AI_BOOTSTRAP.md`",
        "- [ ] Confirm governance level and risk tier in `project-control.yaml`",
        "- [ ] Add first ADR if architecture decisions were made at intake",
        "- [ ] Run governance preflight: `bash scripts/governance-preflight.sh`",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    """Small CLI so shell wrappers can reuse the canonical rules."""
    parser = argparse.ArgumentParser(description="Canonical project naming helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    slug_cmd = subparsers.add_parser("slug", help="Print the validated slug for a project name.")
    slug_cmd.add_argument("name", help="Raw project name")

    risk_cmd = subparsers.add_parser(
        "risk-tier", help="Print the default risk tier for a governance level."
    )
    risk_cmd.add_argument("level", help="Governance level 0-4 or legacy risk tier")

    args = parser.parse_args(argv)
    if args.command == "slug":
        slug, error = validate_project_name(args.name)
        if error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        print(slug)
        return 0
    if args.command == "risk-tier":
        try:
            _, risk_tier = resolve_governance(args.level)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        print(risk_tier)
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
