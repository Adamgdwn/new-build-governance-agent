#!/usr/bin/env python3
"""Cross-platform project scaffolding for New Build Governance Agent."""

from __future__ import annotations

import argparse
import os
import shutil
import stat
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from project_naming import (  # noqa: F401
    GOV_TYPES,
    GOVERNANCE_LEVELS,
    GOVERNANCE_TO_RISK,
    RISK_TIERS,
    RISK_TO_GOVERNANCE,
    resolve_governance,
)
from version import get_version_string

GOVERNANCE_HOME = Path(__file__).resolve().parent.parent
TEMPLATE_ROOT = GOVERNANCE_HOME / "templates" / "project"

USE_CASE_BY_TYPE = {
    "application": "Web application / SaaS",
    "website": "Static / marketing website",
    "service": "Backend API / integration service",
    "internal-tool": "Internal utility / script",
    "automation": "Workflow automation",
    "infrastructure": "Infrastructure / deployment code",
    "documentation": "Static / marketing website",
    "agent": "AI agent with tools",
}
AUTONOMY_BY_GOVERNANCE = {
    "0": "A2",
    "1": "A2",
    "2": "A1",
    "3": "A1",
    "4": "A0",
}


@dataclass
class ScaffoldResult:
    target_dir: Path
    project_type: str
    governance_level: str
    risk_tier: str
    created: list[Path] = field(default_factory=list)
    kept: list[Path] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


def _copy_if_missing(src: Path, dest: Path, result: ScaffoldResult) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        result.kept.append(dest)
        result.messages.append(f"Keeping existing file: {dest}")
        return
    shutil.copyfile(src, dest)
    result.created.append(dest)
    result.messages.append(f"Created: {dest}")


def _make_executable(path: Path) -> None:
    if os.name == "nt" or not path.exists():
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _patch_project_control(
    project_control: Path,
    project_type: str,
    risk_tier: str,
    governance_level: str,
    target_dir: Path,
) -> None:
    project_name = target_dir.name
    text = project_control.read_text(encoding="utf-8")
    text = text.replace("example-project", project_name)
    text = text.replace("project_type: application", f"project_type: {project_type}")
    text = text.replace(
        "primary: Web application / SaaS", f"primary: {USE_CASE_BY_TYPE[project_type]}"
    )
    text = text.replace("risk_tier: medium", f"risk_tier: {risk_tier}")
    text = text.replace("governance_level: 2", f"governance_level: {governance_level}")
    if project_type == "agent":
        text = text.replace("applicable: false", "applicable: true")
        text = text.replace(
            "autonomy_level: A0", f"autonomy_level: {AUTONOMY_BY_GOVERNANCE[governance_level]}"
        )
    project_control.write_text(text, encoding="utf-8")


def _patch_generated_dates(target_dir: Path) -> None:
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    for relative_path in ["START_HERE.md", "docs/current-build-pathway.md"]:
        path = target_dir / relative_path
        if path.exists():
            body = path.read_text(encoding="utf-8")
            body = body.replace("YYYY-MM-DD", generated_at)
            path.write_text(body, encoding="utf-8")


def scaffold_project(
    target_dir: Path | str, project_type: str, governance_input: str | int | None = "2"
) -> ScaffoldResult:
    target = Path(target_dir).expanduser()
    project_type = project_type.strip()
    if project_type not in GOV_TYPES:
        raise ValueError(f"Unsupported project type: {project_type}")

    governance_level, risk_tier = resolve_governance(governance_input)
    result = ScaffoldResult(
        target_dir=target,
        project_type=project_type,
        governance_level=governance_level,
        risk_tier=risk_tier,
    )

    target.mkdir(parents=True, exist_ok=True)
    for relative_dir in ["docs/policy", "docs/standards", "docs/risks", "scripts"]:
        (target / relative_dir).mkdir(parents=True, exist_ok=True)

    copies = [
        ("README.template.md", "README.md"),
        ("START_HERE.template.md", "START_HERE.md"),
        ("project-control.template.yaml", "project-control.yaml"),
        ("AGENTS.template.md", "AGENTS.md"),
        ("CLAUDE.template.md", "CLAUDE.md"),
        ("CARRY_FORWARD.template.md", "CARRY_FORWARD.md"),
        ("AI_BOOTSTRAP.template.md", "AI_BOOTSTRAP.md"),
        ("docs/architecture.template.md", "docs/architecture.md"),
        ("docs/context-map.template.md", "docs/context-map.md"),
        ("docs/domain-language.template.md", "docs/domain-language.md"),
        ("docs/manual.template.md", "docs/manual.md"),
        ("docs/roadmap.template.md", "docs/roadmap.md"),
        ("docs/current-build-pathway.template.md", "docs/current-build-pathway.md"),
        ("docs/standards/README.template.md", "docs/standards/README.md"),
        (
            "docs/policy/durable-development-engineering-policy.template.md",
            "docs/policy/durable-development-engineering-policy.md",
        ),
        (
            "docs/standards/engineering-governance-by-use-case.template.md",
            "docs/standards/engineering-governance-by-use-case.md",
        ),
        (
            "docs/standards/ship-ready-engineering-standard.template.md",
            "docs/standards/ship-ready-engineering-standard.md",
        ),
        (
            "docs/standards/context-hygiene-standard.template.md",
            "docs/standards/context-hygiene-standard.md",
        ),
        ("docs/risk-register.template.md", "docs/risks/risk-register.md"),
        ("docs/CHANGELOG.template.md", "docs/CHANGELOG.md"),
        ("docs/adr.template.md", "docs/adr-template.md"),
        ("docs/exception-record.template.md", "docs/exception-record-template.md"),
        ("scripts/governance-check.template.sh", "scripts/governance-check.sh"),
        ("scripts/governance-preflight.template.sh", "scripts/governance-preflight.sh"),
    ]

    if project_type != "documentation":
        copies.extend(
            [
                ("docs/deployment-guide.template.md", "docs/deployment-guide.md"),
                ("docs/runbook.template.md", "docs/runbook.md"),
            ]
        )

    if project_type == "agent":
        copies.extend(
            [
                ("docs/agent-inventory.template.md", "docs/agent-inventory.md"),
                ("docs/model-registry.template.md", "docs/model-registry.md"),
                ("docs/prompt-register.template.md", "docs/prompt-register.md"),
                ("docs/tool-permission-matrix.template.md", "docs/tool-permission-matrix.md"),
            ]
        )

    for src_relative, dest_relative in copies:
        _copy_if_missing(TEMPLATE_ROOT / src_relative, target / dest_relative, result)

    project_control = target / "project-control.yaml"
    project_control_text = project_control.read_text(encoding="utf-8")
    if project_control in result.created or "example-project" in project_control_text:
        _patch_project_control(
            project_control,
            project_type,
            risk_tier,
            governance_level,
            target,
        )
    else:
        result.messages.append(f"Keeping existing project-control metadata: {project_control}")
    _patch_generated_dates(target)
    _make_executable(target / "scripts" / "governance-check.sh")
    _make_executable(target / "scripts" / "governance-preflight.sh")

    result.messages.extend(
        [
            "",
            f"Bootstrap complete for {target}",
            "Next steps:",
            "  1. Review project-control.yaml",
            '  2. Run: bash "scripts/governance-preflight.sh" from the project root',
            f"  3. Optionally set GOVERNANCE_HOME={GOVERNANCE_HOME} to use the central governance repository.",
        ]
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or update a governed project scaffold.")
    parser.add_argument("--version", action="version", version=get_version_string())
    parser.add_argument("target_dir")
    parser.add_argument("project_type")
    parser.add_argument("governance_level", nargs="?", default="2")
    args = parser.parse_args()

    try:
        result = scaffold_project(args.target_dir, args.project_type, args.governance_level)
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1

    for message in result.messages:
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
