#!/usr/bin/env python3
"""
New Build Governance Agent — headless wrapper.

Reads one JSON object from stdin, scaffolds a governed project, emits one JSON
object to stdout as the last line. Progress lines go to stderr.

Called by the Freedom dispatcher via params_transport: stdin_json.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
REGISTRY = GOVERNANCE_HOME / "automation" / "project_registry.py"
AGENTS_ROOT = Path.home() / "code" / "agents"
APPS_ROOT = Path.home() / "code" / "Applications"

sys.path.insert(0, str(GOVERNANCE_HOME / "automation"))
from scaffold_project import scaffold_project  # noqa: E402
from version import get_version_string  # noqa: E402
from update_check import check_for_updates, format_result  # noqa: E402
from self_update import self_update, format_result as format_self_update_result  # noqa: E402

GOV_TYPES = {
    "application", "website", "service", "internal-tool",
    "automation", "infrastructure", "documentation", "agent",
}
GOVERNANCE_LEVELS = {"0", "1", "2", "3", "4"}
RISK_TIERS = {"low", "medium", "high", "critical"}
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
BUILD_TYPE_GOV_MAP = {"app": "application", "agent": "agent", "tool": "internal-tool", "other": "internal-tool"}


def progress(msg: str) -> None:
    print(f"[new-build-governance-agent] {msg}", file=sys.stderr, flush=True)


RESERVED_OS_NAMES = {
    "con", "prn", "aux", "nul",
    "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
    "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
}


def fail(msg: str, slug: str = "", project_path: str = "") -> None:
    print(
        json.dumps({"status": "failed", "project_path": project_path, "slug": slug, "files_created": [], "error": msg}),
        flush=True,
    )
    sys.exit(1)


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[ _/]", "-", s)
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def resolve_target_root(build_type: str, governance_type: str) -> Path:
    if build_type == "agent" or governance_type == "agent":
        return AGENTS_ROOT
    return APPS_ROOT


def resolve_governance_level(params: dict) -> tuple[str, str]:
    raw_level = str(params.get("governance_level", "")).strip()
    if raw_level:
        if raw_level not in GOVERNANCE_LEVELS:
            fail(f"governance_level must be one of {sorted(GOVERNANCE_LEVELS)}, got: {raw_level!r}")
        return raw_level, GOVERNANCE_TO_RISK[raw_level]

    raw_tier = str(params.get("risk_tier", "2")).strip()
    if raw_tier in GOVERNANCE_LEVELS:
        return raw_tier, GOVERNANCE_TO_RISK[raw_tier]
    if raw_tier in RISK_TIERS:
        return RISK_TO_GOVERNANCE[raw_tier], raw_tier

    fail(
        "risk_tier must be a governance level 0-4 or one of "
        f"{sorted(RISK_TIERS)}, got: {raw_tier!r}"
    )
    raise AssertionError("unreachable")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--version", "-V"}:
        print(get_version_string())
        return
    if len(sys.argv) > 1 and sys.argv[1] in {"--check-updates", "--update-check"}:
        print(format_result(check_for_updates()))
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--self-update":
        result = self_update()
        print(format_self_update_result(result))
        if result.status not in {"updated", "up_to_date", "would_update"}:
            sys.exit(2)
        return

    raw = sys.stdin.read()
    try:
        params = json.loads(raw)
    except json.JSONDecodeError as e:
        fail(f"Invalid JSON input: {e}")
        return

    project_name = params.get("project_name", "").strip()
    build_type = params.get("build_type", "").strip()

    if not project_name:
        fail("project_name is required")
        return
    if build_type not in {"app", "agent", "tool", "other"}:
        fail(f"build_type must be one of app/agent/tool/other, got: {build_type!r}")
        return

    governance_type = params.get("governance_type", "").strip() or BUILD_TYPE_GOV_MAP.get(build_type, "internal-tool")
    if governance_type not in GOV_TYPES:
        fail(f"governance_type {governance_type!r} not valid; must be one of: {sorted(GOV_TYPES)}")
        return

    governance_level, risk_tier = resolve_governance_level(params)

    primary_builder = params.get("primary_builder", "codex session").strip() or "codex session"
    stack = params.get("stack", "not specified").strip() or "not specified"
    scope_problem = params.get("scope_problem", "").strip()
    scope_user = params.get("scope_user", "").strip()
    scope_mvp = params.get("scope_mvp", "").strip()
    audit_correlation_id = params.get("audit_correlation_id", "")

    slug = slugify(project_name)
    if not slug:
        fail(
            f"project_name {project_name!r} produced an empty slug after normalization; "
            "use ASCII letters, digits, spaces, or hyphens"
        )
    if len(slug) < 2:
        fail(
            f"project_name {project_name!r} produced a single-character slug {slug!r}; "
            "provide a more descriptive name"
        )
    if "/" in slug or "\\" in slug:
        fail(f"slug {slug!r} contains a path separator; this should not be possible after slugify")
    if slug.lower() in RESERVED_OS_NAMES:
        fail(f"slug {slug!r} is a reserved OS name; choose a different project name")

    root = resolve_target_root(build_type, governance_type)
    target_dir = root / slug

    progress(
        f"name={project_name!r} slug={slug!r} type={governance_type} "
        f"governance_level={governance_level} target={target_dir}"
    )

    if target_dir.exists():
        progress("Directory already exists — returning already-existed.")
        existing = sorted(str(f) for f in target_dir.rglob("*") if f.is_file())[:50]
        print(json.dumps({
            "status": "already-existed",
            "project_path": str(target_dir),
            "slug": slug,
            "files_created": [],
            "warnings": [f"{target_dir} already existed; no files were overwritten."],
            "existing_file_count": len(existing),
        }), flush=True)
        return

    # ── bootstrap ─────────────────────────────────────────────────────────────

    progress("Scaffolding project...")
    try:
        scaffold_result = scaffold_project(target_dir, governance_type, governance_level)
        for message in scaffold_result.messages:
            progress(message)
    except Exception as e:
        fail(f"project scaffolding failed: {e}")
        return

    for extra in ["docs/adr", "docs/specs", "docs/runbooks", "archive"]:
        (target_dir / extra).mkdir(parents=True, exist_ok=True)
    progress("Created extra dirs: docs/adr docs/specs docs/runbooks archive")

    # ── project-control.yaml ──────────────────────────────────────────────────

    pc = target_dir / "project-control.yaml"
    if pc.exists():
        text = pc.read_text()
        text = text.replace("name: Technical Lead", f"name: {primary_builder}")
        pc.write_text(text)

    # ── INITIAL_SCOPE.md ──────────────────────────────────────────────────────

    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    scope_lines = [
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
        scope_lines += [
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
        scope_lines += [
            "## Scope brief",
            "",
            "Not captured at intake. Fill in before the first coding session.",
            "",
            "- **Problem:**",
            "- **Primary user / consumer:**",
            "- **MVP:**",
            "",
        ]

    scope_lines += [
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

    (target_dir / "INITIAL_SCOPE.md").write_text("\n".join(scope_lines) + "\n")
    progress("Created: INITIAL_SCOPE.md")

    # ── project registry ──────────────────────────────────────────────────────

    registry_id = None
    if REGISTRY.exists():
        try:
            reg = subprocess.run(
                [
                    sys.executable, str(REGISTRY), "register",
                    "--project-name", project_name,
                    "--slug", slug,
                    "--path", str(target_dir),
                    "--project-type", governance_type,
                    "--risk-tier", risk_tier,
                    "--governance-level", governance_level,
                    "--builder", primary_builder,
                    "--stack", stack,
                    "--problem", scope_problem,
                    "--user-desc", scope_user,
                    "--mvp", scope_mvp,
                ],
                capture_output=True,
                text=True,
            )
            if reg.returncode == 0:
                progress(f"Registered: {slug}")
                for line in reg.stdout.splitlines():
                    m = re.search(r'"id"\s*:\s*(\d+)', line)
                    if m:
                        registry_id = int(m.group(1))
            else:
                progress(f"Registry non-fatal warning: {reg.stderr.strip()}")
        except Exception as e:
            progress(f"Registry non-fatal error: {e}")

    # ── result ────────────────────────────────────────────────────────────────

    files_created = sorted(str(f) for f in target_dir.rglob("*") if f.is_file())
    result: dict = {
        "status": "created",
        "project_path": str(target_dir),
        "slug": slug,
        "governance_level": governance_level,
        "risk_tier": risk_tier,
        "files_created": files_created,
        "warnings": [],
    }
    if registry_id is not None:
        result["registry_id"] = registry_id
    if audit_correlation_id:
        result["audit_correlation_id"] = audit_correlation_id

    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
