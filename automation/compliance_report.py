#!/usr/bin/env python3
"""Build categorized governance compliance reports for governed projects."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from schema_validation import SimpleYamlError, get_path, load_project_control, validate_project_control_data


FINDING_CATEGORIES = [
    "required_gaps",
    "recommended_improvements",
    "design_quality_warnings",
    "owner_decisions_needed",
    "accepted_exceptions",
]

BASELINE_REQUIRED_FILES = [
    "README.md",
    "START_HERE.md",
    "project-control.yaml",
    "CARRY_FORWARD.md",
    "docs/architecture.md",
    "docs/context-map.md",
    "docs/current-build-pathway.md",
    "docs/policy/durable-development-engineering-policy.md",
    "docs/standards/README.md",
    "docs/standards/engineering-governance-by-use-case.md",
    "docs/standards/ship-ready-engineering-standard.md",
    "docs/risks/risk-register.md",
]

AGENT_REQUIRED_FILES = [
    "docs/agent-inventory.md",
    "docs/model-registry.md",
    "docs/prompt-register.md",
    "docs/tool-permission-matrix.md",
]

RECOMMENDED_FILES = [
    ("docs/domain-language.md", "Recommended when the project has meaningful domain logic or repeated domain terms."),
    ("docs/standards/context-hygiene-standard.md", "Recommended for agent-assisted work, long sessions, scoped context, compaction, and handoffs."),
    (".env.example", "Recommended when setup or deployment depends on environment variables."),
    ("SECURITY.md", "Recommended for vulnerability reporting and secret-handling expectations."),
]

COMMAND_LABELS = {
    "Lint": "lint command",
    "Test": "test command",
    "Build": "build command",
}

SUSPICIOUS_NAMES = {
    "common",
    "data",
    "general",
    "handler",
    "helpers",
    "helper",
    "manager",
    "misc",
    "processor",
    "stuff",
    "temp",
    "thing",
    "utils",
}

USE_CASE_MINIMUM_REVIEW_LEVEL = {
    "AI agent with tools": 3,
    "Infrastructure / deployment code": 3,
    "Backend API / integration service": 3,
    "Web application / SaaS": 2,
    "Workflow automation": 2,
    "Data / analytics tool": 2,
    "AI assistant / chat interface": 2,
}


@dataclass
class Finding:
    category: str
    message: str
    path: str | None = None


def project_file(project_path: Path, relative_path: str) -> Path:
    return project_path / relative_path


def file_exists(project_path: Path, relative_path: str) -> bool:
    return project_file(project_path, relative_path).is_file()


def load_control(project_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    control_path = project_path / "project-control.yaml"
    if not control_path.exists():
        return None, ["project-control.yaml is missing"]
    try:
        data = load_project_control(control_path)
    except SimpleYamlError as exc:
        return None, [str(exc)]
    return data, validate_project_control_data(data)


def required_files_from_control(control: dict[str, Any] | None) -> list[str]:
    if not control:
        return BASELINE_REQUIRED_FILES
    configured = get_path(control, "controls.required_docs")
    required = list(BASELINE_REQUIRED_FILES)
    if isinstance(configured, list):
        required.extend(str(item) for item in configured if isinstance(item, str) and item.strip())
    if get_path(control, "project_type") == "agent":
        required.extend(AGENT_REQUIRED_FILES)
    return sorted(set(required))


def command_is_placeholder(line: str) -> bool:
    lowered = line.lower()
    return "<fill in>" in lowered or "todo" in lowered or "replace these" in lowered


def has_command(ai_bootstrap: str, label: str) -> bool:
    prefix = f"- {label}:"
    for line in ai_bootstrap.splitlines():
        if line.strip().startswith(prefix):
            return bool(line.split(":", 1)[1].strip()) and not command_is_placeholder(line)
    return False


def find_suspicious_names(project_path: Path) -> list[str]:
    ignored_dirs = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".venv",
        "__pycache__",
        "node_modules",
        "venv",
    }
    findings: list[str] = []
    for path in project_path.rglob("*"):
        try:
            relative = path.relative_to(project_path)
        except ValueError:
            continue
        parts = set(relative.parts)
        if parts & ignored_dirs:
            continue
        stem = path.stem.lower()
        name = path.name.lower()
        if stem in SUSPICIOUS_NAMES or name in SUSPICIOUS_NAMES:
            findings.append(str(relative))
        if len(findings) >= 20:
            break
    return sorted(findings)


def governance_mismatch_findings(control: dict[str, Any] | None) -> list[Finding]:
    if not control:
        return []
    findings: list[Finding] = []
    governance_level = get_path(control, "governance_level")
    primary = get_path(control, "use_case.primary")
    if isinstance(primary, str) and isinstance(governance_level, int):
        recommended = USE_CASE_MINIMUM_REVIEW_LEVEL.get(primary)
        if recommended is not None and governance_level < recommended:
            findings.append(
                Finding(
                    "owner_decisions_needed",
                    (
                        f"Governance mismatch warning: use case {primary!r} commonly needs governance level "
                        f"{recommended} or stronger, but selected governance_level is {governance_level}. "
                        "The selected level remains unchanged unless the owner explicitly approves a change."
                    ),
                    "project-control.yaml",
                )
            )
    if get_path(control, "data_classification.handles_money") is True and isinstance(governance_level, int) and governance_level < 3:
        findings.append(
            Finding(
                "owner_decisions_needed",
                "Money-handling projects should confirm whether governance_level should remain below 3.",
                "project-control.yaml",
            )
        )
    if get_path(control, "data_classification.handles_sensitive_data") is True and isinstance(governance_level, int) and governance_level < 3:
        findings.append(
            Finding(
                "owner_decisions_needed",
                "Sensitive-data projects should confirm whether governance_level should remain below 3.",
                "project-control.yaml",
            )
        )
    return findings


def build_compliance_report(project_path: Path | str) -> dict[str, Any]:
    project = Path(project_path).expanduser().resolve()
    if not project.is_dir():
        raise NotADirectoryError(f"Project path does not exist: {project}")

    control, schema_errors = load_control(project)
    findings = {category: [] for category in FINDING_CATEGORIES}
    passes: list[str] = []

    for relative_path in required_files_from_control(control):
        if file_exists(project, relative_path):
            passes.append(f"Required file present: {relative_path}")
        else:
            findings["required_gaps"].append(
                Finding("required_gaps", f"Missing required file: {relative_path}", relative_path)
            )

    for error in schema_errors:
        findings["required_gaps"].append(
            Finding("required_gaps", f"project-control.yaml schema gap: {error}", "project-control.yaml")
        )

    for relative_path, reason in RECOMMENDED_FILES:
        if file_exists(project, relative_path):
            passes.append(f"Recommended file present: {relative_path}")
        else:
            findings["recommended_improvements"].append(
                Finding("recommended_improvements", f"Missing {relative_path}. {reason}", relative_path)
            )

    ai_bootstrap_path = project / "AI_BOOTSTRAP.md"
    if ai_bootstrap_path.exists():
        ai_bootstrap = ai_bootstrap_path.read_text(encoding="utf-8", errors="ignore")
        for label, description in COMMAND_LABELS.items():
            if not has_command(ai_bootstrap, label):
                findings["recommended_improvements"].append(
                    Finding(
                        "recommended_improvements",
                        f"AI_BOOTSTRAP.md is missing a concrete {description}.",
                        "AI_BOOTSTRAP.md",
                    )
                )
    else:
        findings["recommended_improvements"].append(
            Finding("recommended_improvements", "AI_BOOTSTRAP.md is recommended for agent-readable commands.", "AI_BOOTSTRAP.md")
        )

    for relative_path in find_suspicious_names(project):
        findings["design_quality_warnings"].append(
            Finding(
                "design_quality_warnings",
                "Suspicious generic name found; confirm it owns a clear responsibility.",
                relative_path,
            )
        )

    for finding in governance_mismatch_findings(control):
        findings[finding.category].append(finding)

    exceptions = get_path(control, "exceptions") if control else []
    if isinstance(exceptions, list):
        for exception in exceptions:
            findings["accepted_exceptions"].append(
                Finding("accepted_exceptions", f"Accepted exception recorded: {exception}", "project-control.yaml")
            )

    serialized_findings = {
        category: [asdict(finding) for finding in category_findings]
        for category, category_findings in findings.items()
    }
    overall_status = "failed" if serialized_findings["required_gaps"] else "passed"
    return {
        "report_version": 1,
        "project_path": str(project),
        "overall_status": overall_status,
        "passes": passes,
        "findings": serialized_findings,
        "summary": {category: len(items) for category, items in serialized_findings.items()},
    }


def print_report(report: dict[str, Any]) -> None:
    for item in report["passes"]:
        print(f"PASS: {item}")

    labels = {
        "required_gaps": "Required gaps",
        "recommended_improvements": "Recommended improvements",
        "design_quality_warnings": "Design quality warnings",
        "owner_decisions_needed": "Owner decisions needed",
        "accepted_exceptions": "Accepted exceptions",
    }
    prefixes = {
        "required_gaps": "REQUIRED GAP",
        "recommended_improvements": "RECOMMENDED",
        "design_quality_warnings": "DESIGN WARNING",
        "owner_decisions_needed": "OWNER DECISION",
        "accepted_exceptions": "ACCEPTED EXCEPTION",
    }
    for category in FINDING_CATEGORIES:
        print()
        print(f"{labels[category]}:")
        items = report["findings"][category]
        if not items:
            print("  None.")
            continue
        for item in items:
            path = f" [{item['path']}]" if item.get("path") else ""
            print(f"  {prefixes[category]}:{path} {item['message']}")

    print()
    print("Compliance summary:")
    for category in FINDING_CATEGORIES:
        print(f"- {labels[category]}: {report['summary'][category]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a categorized governance compliance report.")
    parser.add_argument("project", help="Path to the governed project")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of human-readable output")
    args = parser.parse_args()

    try:
        report = build_compliance_report(args.project)
    except NotADirectoryError as exc:
        print(exc)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_report(report)

    return 0 if report["overall_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
