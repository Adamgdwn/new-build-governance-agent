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
    "agentic-harness": "AI / ML harness",
}

HARNESS_TOPOLOGY_LABELS = {
    "single-llm": "Single LLM",
    "multi-llm": "Multi-LLM",
    "non-llm": "Non-LLM AI",
    "combination": "Combination (LLM + Non-LLM)",
}

HARNESS_PROFILE_BY_TOPOLOGY = {
    "single-llm": "single-agent",
    "multi-llm": "multi-agent",
    "non-llm": "non-llm-specialist",
    "combination": "multi-model",
}

HARNESS_PROFILE_RULES = {
    "single-agent": (
        "One language model handles the complete task. "
        "Governance requirements: one model entry in `docs/model-registry.md`, "
        "all prompts in `docs/prompt-register.md`, tool permissions in "
        "`docs/tool-permission-matrix.md`, and a human review gate before any "
        "external action the model can trigger."
    ),
    "multi-agent": (
        "Multiple language models with defined roles work in sequence or parallel. "
        "Governance requirements: one entry per participant in `docs/agent-inventory.md`, "
        "a defined coordinator role, explicit handoff contracts between agents, "
        "and a human review gate before any participant can take an external action."
    ),
    "non-llm-specialist": (
        "Machine learning without a generative language model (e.g. vision models, "
        "classifiers, speech recognition, forecasting). "
        "Governance requirements: model entry in `docs/model-registry.md` with "
        "version and provenance, inference boundary documented, and output validation "
        "before any result affects state or is shown to users."
    ),
    "multi-model": (
        "Both language models and other ML models (vision, audio, forecasting, etc.) "
        "participate in the product. "
        "Governance requirements: every participant in `docs/agent-inventory.md`, "
        "model entries for each distinct inference call in `docs/model-registry.md`, "
        "and explicit boundary contracts between LLM and non-LLM subsystems."
    ),
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
    if project_type in {"agent", "agentic-harness"}:
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


def _apply_harness_to_project_control(
    project_control: Path,
    harness_profile: str,
    harness_topology: str,
) -> None:
    text = project_control.read_text(encoding="utf-8")
    text = text.replace("harness_profile: none", f"harness_profile: {harness_profile}")
    text = text.replace(
        "activation_mode: build_only", "activation_mode: build_only"
    )
    project_control.write_text(text, encoding="utf-8")


def _write_harness_readme(
    target_dir: Path,
    harness_profile: str,
    harness_topology: str,
    harness_description: str,
    generated_at: str,
) -> None:
    template = TEMPLATE_ROOT / "docs" / "harness" / "README.harness.template.md"
    if not template.exists():
        return
    dest_dir = target_dir / "docs" / "harness"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "README.md"
    if dest.exists():
        return
    text = template.read_text(encoding="utf-8")
    topology_label = HARNESS_TOPOLOGY_LABELS.get(harness_topology, harness_topology)
    profile_rules = HARNESS_PROFILE_RULES.get(harness_profile, "See project-control.yaml for profile details.")
    description = harness_description.strip() or "No description provided."
    text = text.replace("{{HARNESS_PROFILE}}", harness_profile)
    text = text.replace("{{HARNESS_TOPOLOGY}}", harness_topology)
    text = text.replace("{{HARNESS_TOPOLOGY_LABEL}}", topology_label)
    text = text.replace("{{HARNESS_DESCRIPTION}}", description)
    text = text.replace("{{HARNESS_PROFILE_RULES}}", profile_rules)
    text = text.replace("{{GENERATED_AT}}", generated_at)
    dest.write_text(text, encoding="utf-8")


def scaffold_project(
    target_dir: Path | str,
    project_type: str,
    governance_input: str | int | None = "2",
    *,
    harness_topology: str = "",
    harness_description: str = "",
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

    ai_registers = project_type in {"agent", "agentic-harness"}
    if ai_registers:
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

    if project_type == "agentic-harness" and harness_topology:
        harness_profile = HARNESS_PROFILE_BY_TOPOLOGY.get(harness_topology, "single-agent")
        generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
        _apply_harness_to_project_control(project_control, harness_profile, harness_topology)
        _write_harness_readme(
            target, harness_profile, harness_topology, harness_description, generated_at
        )
        result.messages.append(f"Created: docs/harness/README.md (profile: {harness_profile})")

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
