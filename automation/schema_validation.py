#!/usr/bin/env python3
"""Validate governed project control files and promotion plans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_TYPES = {
    "application",
    "website",
    "service",
    "internal-tool",
    "automation",
    "infrastructure",
    "documentation",
    "agent",
}
RISK_TIERS = {"low", "medium", "high", "critical"}
REPOSITORY_MODELS = {"single-repo", "monorepo"}
COMPLEXITY_MODES = {"advisory", "no-regression", "enforced"}
ALIGNMENT_MODES = {"review-before-apply"}
PROMOTION_STAGES = [
    "local_compliance",
    "pre_promotion_checks",
    "prepare_external_sync",
    "approve_and_execute",
    "post_promotion_checks",
    "rollback_readiness",
]


class SimpleYamlError(ValueError):
    """Raised when the supported project-control YAML subset cannot be parsed."""


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value == '""' or value == "''":
        return ""
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value.isdigit():
        return int(value)
    return value


def next_container(lines: list[tuple[int, str]], start: int, indent: int) -> Any:
    for next_indent, next_content in lines[start + 1 :]:
        if next_indent <= indent:
            break
        return [] if next_content.startswith("- ") else {}
    return {}


def parse_simple_yaml(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if indent % 2 != 0:
            raise SimpleYamlError(f"Unsupported odd indentation: {raw!r}")
        lines.append((indent, raw.strip()))

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    for index, (indent, content) in enumerate(lines):
        while indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if content.startswith("- "):
            if not isinstance(parent, list):
                raise SimpleYamlError(f"List item found outside a list: {content!r}")
            parent.append(parse_scalar(content[2:]))
            continue

        key, separator, raw_value = content.partition(":")
        if not separator or not key.strip():
            raise SimpleYamlError(f"Expected key/value line: {content!r}")
        key = key.strip()
        raw_value = raw_value.strip()
        if not isinstance(parent, dict):
            raise SimpleYamlError(f"Mapping entry found inside a scalar list: {content!r}")

        if raw_value:
            parent[key] = parse_scalar(raw_value)
        else:
            container = next_container(lines, index, indent)
            parent[key] = container
            stack.append((indent, container))
    return root


def get_path(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def require_string(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    value = get_path(data, dotted)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{dotted} must be a non-empty string")


def require_bool(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    if not isinstance(get_path(data, dotted), bool):
        errors.append(f"{dotted} must be true or false")


def require_string_value(data: dict[str, Any], dotted: str, errors: list[str]) -> None:
    if not isinstance(get_path(data, dotted), str):
        errors.append(f"{dotted} must be a string")


def require_string_list(
    data: dict[str, Any], dotted: str, errors: list[str], *, allow_empty: bool = True
) -> None:
    value = get_path(data, dotted)
    if not isinstance(value, list):
        errors.append(f"{dotted} must be a list")
        return
    if not allow_empty and not value:
        errors.append(f"{dotted} must include at least one item")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{dotted}[{index}] must be a non-empty string")


def validate_complexity_control(data: dict[str, Any], errors: list[str]) -> None:
    complexity = get_path(data, "quality_controls.cyclomatic_complexity")
    if complexity is None:
        return
    if not isinstance(complexity, dict):
        errors.append("quality_controls.cyclomatic_complexity must be a mapping")
        return

    mode = get_path(data, "quality_controls.cyclomatic_complexity.mode")
    if mode not in COMPLEXITY_MODES:
        errors.append(
            "quality_controls.cyclomatic_complexity.mode must be one of: "
            + ", ".join(sorted(COMPLEXITY_MODES))
        )
    review_above = get_path(data, "quality_controls.cyclomatic_complexity.review_above")
    decision_above = get_path(
        data,
        "quality_controls.cyclomatic_complexity.refactor_or_exception_above",
    )
    if not isinstance(review_above, int) or review_above < 1:
        errors.append(
            "quality_controls.cyclomatic_complexity.review_above must be a positive integer"
        )
    if not isinstance(decision_above, int) or decision_above < 1:
        errors.append(
            "quality_controls.cyclomatic_complexity.refactor_or_exception_above "
            "must be a positive integer"
        )
    if (
        isinstance(review_above, int)
        and isinstance(decision_above, int)
        and decision_above < review_above
    ):
        errors.append(
            "quality_controls.cyclomatic_complexity.refactor_or_exception_above "
            "must be greater than or equal to review_above"
        )
    require_string(data, "quality_controls.cyclomatic_complexity.scope", errors)


def validate_governance_alignment(data: dict[str, Any], errors: list[str]) -> None:
    alignment = get_path(data, "governance_alignment")
    if alignment is None:
        return
    if not isinstance(alignment, dict):
        errors.append("governance_alignment must be a mapping")
        return

    require_string(data, "governance_alignment.source", errors)
    alignment_mode = get_path(data, "governance_alignment.mode")
    if alignment_mode not in ALIGNMENT_MODES:
        errors.append(
            "governance_alignment.mode must be one of: " + ", ".join(sorted(ALIGNMENT_MODES))
        )
    cadence = get_path(data, "governance_alignment.review_cadence_days")
    if not isinstance(cadence, int) or cadence < 1:
        errors.append("governance_alignment.review_cadence_days must be a positive integer")
    require_string_value(data, "governance_alignment.last_reviewed", errors)


def validate_project_control_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in [
        "project_name",
        "project_type",
        "use_case.primary",
        "risk_tier",
        "repository_model",
        "owner.name",
        "owner.role",
        "technical_lead.name",
        "technical_lead.role",
        "status",
    ]:
        require_string(data, field, errors)

    project_type = get_path(data, "project_type")
    if isinstance(project_type, str) and project_type not in PROJECT_TYPES:
        errors.append(f"project_type must be one of: {', '.join(sorted(PROJECT_TYPES))}")

    risk_tier = get_path(data, "risk_tier")
    if isinstance(risk_tier, str) and risk_tier not in RISK_TIERS:
        errors.append(f"risk_tier must be one of: {', '.join(sorted(RISK_TIERS))}")

    governance_level = get_path(data, "governance_level")
    if not isinstance(governance_level, int) or not 0 <= governance_level <= 4:
        errors.append("governance_level must be an integer from 0 through 4")

    repository_model = get_path(data, "repository_model")
    if isinstance(repository_model, str) and repository_model not in REPOSITORY_MODELS:
        errors.append(f"repository_model must be one of: {', '.join(sorted(REPOSITORY_MODELS))}")

    require_string_list(data, "use_case.secondary", errors)
    require_bool(data, "data_classification.handles_sensitive_data", errors)
    require_bool(data, "data_classification.handles_money", errors)
    require_string_value(data, "data_classification.notes", errors)
    require_string_list(data, "controls.required_docs", errors, allow_empty=False)
    require_string_list(data, "controls.machine_enforcement", errors)
    validate_complexity_control(data, errors)
    validate_governance_alignment(data, errors)

    exceptions = get_path(data, "exceptions")
    if not isinstance(exceptions, list):
        errors.append("exceptions must be a list")

    agent_controls = get_path(data, "agent_controls")
    if not isinstance(agent_controls, dict):
        errors.append("agent_controls must be a mapping")
    else:
        require_bool(data, "agent_controls.applicable", errors)
        require_string(data, "agent_controls.autonomy_level", errors)
        require_string_list(data, "agent_controls.model_registry", errors)
        require_string_list(data, "agent_controls.prompt_registry", errors)

    if project_type == "agent" and get_path(data, "agent_controls.applicable") is not True:
        errors.append("agent projects must set agent_controls.applicable to true")

    return errors


def load_project_control(path: Path) -> dict[str, Any]:
    try:
        return parse_simple_yaml(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SimpleYamlError(f"Could not read {path}: {exc}") from exc


def validate_project_control(path: Path) -> list[str]:
    try:
        data = load_project_control(path)
    except SimpleYamlError as exc:
        return [str(exc)]
    return validate_project_control_data(data)


def require_plan_string(plan: dict[str, Any], dotted: str, errors: list[str]) -> None:
    require_string(plan, dotted, errors)


def validate_check(check: Any, path: str, errors: list[str]) -> None:
    if not isinstance(check, dict):
        errors.append(f"{path} must be a mapping")
        return
    for field in ["name", "command", "kind", "reason"]:
        if not isinstance(check.get(field), str) or not check.get(field, "").strip():
            errors.append(f"{path}.{field} must be a non-empty string")
    kind = check.get("kind")
    if kind not in {"automated", "automated_if_available", "manual"}:
        errors.append(f"{path}.kind has unsupported value: {kind!r}")
    if kind != "manual":
        argv = check.get("argv")
        if (
            not isinstance(argv, list)
            or not argv
            or not all(isinstance(item, str) and item for item in argv)
        ):
            errors.append(f"{path}.argv must be a non-empty string list for automated checks")


def validate_promotion_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["promotion plan must be a JSON object"]

    if not isinstance(plan.get("plan_version"), int) or plan["plan_version"] < 3:
        errors.append("plan_version must be an integer greater than or equal to 3")
    for field in ["generated_at", "project_path", "project_slug", "purpose"]:
        require_plan_string(plan, field, errors)

    policy = plan.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be a mapping")
    else:
        for field in [
            "local_changes_allowed",
            "external_pushes_allowed_by_default",
            "require_explicit_approval_per_target",
        ]:
            if not isinstance(policy.get(field), bool):
                errors.append(f"policy.{field} must be true or false")
        if (
            not isinstance(policy.get("rollback_expectation"), str)
            or not policy.get("rollback_expectation", "").strip()
        ):
            errors.append("policy.rollback_expectation must be a non-empty string")

    stages = plan.get("stages")
    if not isinstance(stages, list) or not stages:
        errors.append("stages must be a non-empty list")
        return errors

    stages_by_name: dict[str, dict[str, Any]] = {}
    for index, stage in enumerate(stages):
        if not isinstance(stage, dict):
            errors.append(f"stages[{index}] must be a mapping")
            continue
        name = stage.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"stages[{index}].name must be a non-empty string")
            continue
        if name in stages_by_name:
            errors.append(f"duplicate stage name: {name}")
        stages_by_name[name] = stage
        if not isinstance(stage.get("status"), str) or not stage.get("status", "").strip():
            errors.append(f"stage {name}.status must be a non-empty string")

    missing = [name for name in PROMOTION_STAGES if name not in stages_by_name]
    if missing:
        errors.append(f"missing required stages: {', '.join(missing)}")

    local = stages_by_name.get("local_compliance", {})
    if local and not isinstance(local.get("missing_items"), list):
        errors.append("stage local_compliance.missing_items must be a list")

    for stage_name in ["pre_promotion_checks", "post_promotion_checks"]:
        stage = stages_by_name.get(stage_name)
        if not stage:
            continue
        checks = stage.get("checks")
        if not isinstance(checks, list) or not checks:
            errors.append(f"stage {stage_name}.checks must be a non-empty list")
            continue
        for index, check in enumerate(checks):
            validate_check(check, f"stage {stage_name}.checks[{index}]", errors)

    for stage_name in ["prepare_external_sync", "approve_and_execute"]:
        stage = stages_by_name.get(stage_name)
        if stage and not isinstance(stage.get("targets"), dict):
            errors.append(f"stage {stage_name}.targets must be a mapping")

    return errors


def validate_promotion_plan_file(path: Path) -> list[str]:
    try:
        plan = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"Could not read promotion plan {path}: {exc}"]
    return validate_promotion_plan(plan)


def print_errors(label: str, errors: list[str]) -> None:
    if not errors:
        print(f"PASS: {label}")
        return
    print(f"FAIL: {label}")
    for error in errors:
        print(f"  - {error}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate New Build Governance Agent governance schemas."
    )
    parser.add_argument("--project", help="Project directory containing project-control.yaml")
    parser.add_argument("--project-control", help="Specific project-control.yaml path")
    parser.add_argument(
        "--promotion-plan",
        action="append",
        default=[],
        help="Promotion plan JSON path; can be passed more than once",
    )
    args = parser.parse_args()

    checks: list[tuple[str, list[str]]] = []
    if args.project:
        checks.append(
            (
                "project-control.yaml schema",
                validate_project_control(Path(args.project) / "project-control.yaml"),
            )
        )
    if args.project_control:
        checks.append(
            ("project-control.yaml schema", validate_project_control(Path(args.project_control)))
        )
    for plan_path in args.promotion_plan:
        checks.append(
            (f"promotion plan schema: {plan_path}", validate_promotion_plan_file(Path(plan_path)))
        )

    if not checks:
        parser.error("Provide --project, --project-control, or --promotion-plan")

    failed = False
    for label, errors in checks:
        print_errors(label, errors)
        failed = failed or bool(errors)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
