#!/usr/bin/env python3
"""Run staged promotion checks from a generated promotion plan."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from schema_validation import validate_promotion_plan

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-governance-agent" / "exports"

_OUTPUT_CAP = 8192
_REDACT_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]*=.+$", re.MULTILINE)


def _cap_output(text: str) -> str:
    if len(text) > _OUTPUT_CAP:
        return text[:_OUTPUT_CAP] + "\n[truncated]"
    return text


def _redact_output(text: str) -> str:
    return _REDACT_PATTERN.sub("[redacted]", text)


def build_check_env(project_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    nvm_versions = Path.home() / ".nvm" / "versions" / "node"
    nvm_bins = []
    if nvm_versions.exists():
        for child in sorted(nvm_versions.iterdir(), reverse=True):
            candidate = child / "bin"
            if candidate.exists():
                nvm_bins.append(str(candidate))
    project_bins = []
    for candidate in [
        project_path / ".venv" / "bin",
        project_path / "venv" / "bin",
        project_path / "env" / "bin",
        project_path / ".direnv" / "python-venv" / "bin",
        project_path / "node_modules" / ".bin",
    ]:
        if candidate.exists():
            project_bins.append(str(candidate))
    path_parts = [
        *project_bins,
        *nvm_bins,
        str(Path.home() / ".local" / "bin"),
        str(Path.home() / "bin"),
        str(Path.home() / ".pyenv" / "shims"),
        str(Path.home() / ".pyenv" / "bin"),
        env.get("PATH", ""),
        "/usr/local/sbin",
        "/usr/local/bin",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
    ]
    cleaned = []
    for part in path_parts:
        if not part:
            continue
        for piece in part.split(":"):
            if piece and piece not in cleaned:
                cleaned.append(piece)
    env["PATH"] = ":".join(cleaned)
    env.setdefault("GOVERNANCE_HOME", str(REPO_ROOT))
    return env


def missing_runtime(result: dict) -> bool:
    text = "\n".join(
        str(part) for part in [result.get("stdout", ""), result.get("stderr", "")]
    ).lower()
    if result.get("returncode") == 127:
        return True
    patterns = [
        "no module named pytest",
        "no module named",
        "command not found",
        "not found",
        "executable file not found",
        "npm: not found",
        "pytest: not found",
    ]
    return any(pattern in text for pattern in patterns)


def detect_missing_prerequisites(project_path: Path, argv: list[str], command: str) -> str | None:
    normalized = command.strip().lower()
    executable = argv[0] if argv else ""
    if (normalized.startswith("npm ") or executable == "npm") and (project_path / "package.json").exists():
        node_modules = project_path / "node_modules"
        if not node_modules.exists():
            return (
                "JavaScript dependencies are not installed for this project yet. "
                "The repo has a package.json, but node_modules is missing, so local package binaries such as `next` are unavailable. "
                "Run `npm install` in the project before re-running automated checks."
            )
    return None


def load_plan(plan_path: Path) -> dict:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    schema_errors = validate_promotion_plan(plan)
    if schema_errors:
        joined = "\n- ".join(schema_errors)
        raise ValueError(f"Invalid promotion plan schema:\n- {joined}")
    return plan


def find_stage(plan: dict, stage_name: str) -> dict:
    for stage in plan.get("stages", []):
        if stage.get("name") == stage_name:
            return stage
    raise ValueError(f"Stage not found: {stage_name}")


def resolve_argv(check: dict) -> list[str] | None:
    argv = check.get("argv")
    if isinstance(argv, list) and argv and all(isinstance(item, str) and item for item in argv):
        return argv

    command = check.get("command", "")
    safe_commands = {
        "bash scripts/governance-preflight.sh",
        "python3 -m pytest -q",
        "npm run lint",
        "npm test",
        "npm run build",
    }
    if command in safe_commands:
        return shlex.split(command)
    return None


def run_check(project_path: Path, check: dict) -> dict:
    kind = check.get("kind", "manual")
    command = check.get("command", "")
    argv = resolve_argv(check)
    result = {
        "name": check.get("name", "unknown"),
        "kind": kind,
        "command": command,
        "argv": argv or [],
        "reason": check.get("reason", ""),
        "status": "skipped",
        "stdout": "",
        "stderr": "",
        "returncode": None,
    }
    if kind == "manual" or command == "manual review":
        result["status"] = "manual_required"
        return result
    if argv is None:
        result["status"] = "manual_required"
        result["reason"] = (
            (result["reason"] + " ") if result.get("reason") else ""
        ) + "This check does not include a safe argv form and must be reviewed manually."
        return result

    prerequisite_issue = detect_missing_prerequisites(project_path, argv, command)
    if prerequisite_issue:
        result["status"] = "manual_required"
        result["reason"] = (
            (result["reason"] + " ") if result.get("reason") else ""
        ) + prerequisite_issue
        return result

    try:
        proc = subprocess.run(
            argv,
            cwd=str(project_path),
            text=True,
            capture_output=True,
            check=False,
            env=build_check_env(project_path),
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        result["status"] = "timed_out"
        result["reason"] = (
            (result["reason"] + " ") if result.get("reason") else ""
        ) + "Check timed out after 300 seconds and was not completed."
        return result
    result["stdout"] = _redact_output(_cap_output(proc.stdout))
    result["stderr"] = _redact_output(_cap_output(proc.stderr))
    result["returncode"] = proc.returncode
    if proc.returncode == 0:
        result["status"] = "passed"
    elif kind == "automated_if_available" and missing_runtime(result):
        result["status"] = "manual_required"
        result["reason"] = (
            result["reason"]
            + " Automated execution was skipped because the required runtime or test tool was not available in the detected environment."
        )
    else:
        result["status"] = "failed"
    return result


def categorize_check_result(result: dict) -> str:
    if result.get("status") in ("failed", "timed_out"):
        return "required_gaps"
    if result.get("status") == "manual_required":
        return "owner_decisions_needed"
    return "passed_checks"


def build_report(plan: dict, plan_path: Path, stage_name: str) -> dict:
    project_path = Path(plan["project_path"])
    stage = find_stage(plan, stage_name)
    checks = stage.get("checks", [])
    results = [run_check(project_path, check) for check in checks]
    for result in results:
        result["finding_category"] = categorize_check_result(result)
    overall = "passed"
    if any(item["status"] == "failed" for item in results):
        overall = "failed"
    elif any(item["status"] == "manual_required" for item in results):
        overall = "manual_required"
    category_summary: dict[str, int] = {
        "required_gaps": 0,
        "recommended_improvements": 0,
        "design_quality_warnings": 0,
        "owner_decisions_needed": 0,
        "accepted_exceptions": 0,
        "passed_checks": 0,
    }
    for result in results:
        category_summary[result["finding_category"]] += 1
    return {
        "report_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_path": plan["project_path"],
        "project_slug": plan["project_slug"],
        "plan_path": str(plan_path),
        "stage_name": stage_name,
        "overall_status": overall,
        "category_summary": category_summary,
        "results": results,
    }


def write_report(report: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = EXPORT_ROOT / f"check-report-{report['project_slug']}-{report['stage_name']}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pre/post promotion checks from a promotion plan.")
    parser.add_argument("--plan", required=True, help="Path to the promotion plan JSON")
    parser.add_argument("--stage", default="pre_promotion_checks", choices=["pre_promotion_checks", "post_promotion_checks"], help="Which check stage to run")
    parser.add_argument("--output", help="Optional output path for the check report JSON")
    args = parser.parse_args()

    plan_path = Path(args.plan).expanduser().resolve()
    plan = load_plan(plan_path)
    report = build_report(plan, plan_path, args.stage)
    output = write_report(report, Path(args.output) if args.output else None)
    print(output)
    return 0 if report["overall_status"] != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
