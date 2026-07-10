#!/usr/bin/env python3
"""Repair missing local test tooling for staged promotion checks."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-governance-agent" / "exports"


def build_env(project_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    path_parts = [
        str(project_path / ".venv" / "bin"),
        str(project_path / "venv" / "bin"),
        str(project_path / "env" / "bin"),
        str(project_path / ".direnv" / "python-venv" / "bin"),
        env.get("PATH", ""),
        "/usr/local/sbin",
        "/usr/local/bin",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
    ]
    cleaned: list[str] = []
    for part in path_parts:
        if not part:
            continue
        for piece in part.split(":"):
            if piece and piece not in cleaned:
                cleaned.append(piece)
    env["PATH"] = ":".join(cleaned)
    env.setdefault("GOVERNANCE_HOME", str(REPO_ROOT))
    return env


def load_plan(plan_path: Path) -> dict:
    return json.loads(plan_path.read_text(encoding="utf-8"))


def choose_python(project_path: Path) -> list[str]:
    candidates = [
        project_path / ".venv" / "bin" / "python",
        project_path / "venv" / "bin" / "python",
        project_path / "env" / "bin" / "python",
        project_path / ".direnv" / "python-venv" / "bin" / "python",
    ]
    for candidate in candidates:
        if candidate.exists():
            return [str(candidate)]
    return ["python3"]


def run(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def write_report(report: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = EXPORT_ROOT / f"remediation-{report['project_slug']}-{stamp}.json"
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def remediate_pytest(plan: dict) -> dict:
    project_path = Path(plan["project_path"]).expanduser().resolve()
    env = build_env(project_path)
    python_cmd = choose_python(project_path)

    probe = run([*python_cmd, "-m", "pytest", "--version"], project_path, env)
    if probe.returncode == 0:
        return {
            "status": "already_present",
            "project_path": str(project_path),
            "project_slug": plan["project_slug"],
            "python_command": python_cmd,
            "tool": "pytest",
            "stdout": probe.stdout.strip(),
            "stderr": probe.stderr.strip(),
            "installed": False,
        }

    install = run([*python_cmd, "-m", "pip", "install", "pytest"], project_path, env)
    if install.returncode != 0:
        raise RuntimeError(
            install.stderr.strip() or install.stdout.strip() or "Unable to install pytest"
        )

    verify = run([*python_cmd, "-m", "pytest", "--version"], project_path, env)
    if verify.returncode != 0:
        raise RuntimeError(
            verify.stderr.strip()
            or verify.stdout.strip()
            or "pytest still unavailable after install"
        )

    return {
        "status": "installed",
        "project_path": str(project_path),
        "project_slug": plan["project_slug"],
        "python_command": python_cmd,
        "tool": "pytest",
        "stdout": verify.stdout.strip(),
        "stderr": verify.stderr.strip(),
        "installed": True,
        "install_stdout": install.stdout.strip(),
        "install_stderr": install.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Repair missing local test tooling for promotion checks."
    )
    parser.add_argument("--plan", required=True, help="Path to the promotion plan JSON")
    parser.add_argument("--tool", default="pytest", choices=["pytest"], help="Tool to remediate")
    parser.add_argument("--output", help="Optional output path for the remediation report JSON")
    args = parser.parse_args()

    plan_path = Path(args.plan).expanduser().resolve()
    plan = load_plan(plan_path)
    try:
        if args.tool == "pytest":
            result = remediate_pytest(plan)
        else:
            raise RuntimeError(f"Unsupported remediation tool: {args.tool}")
        report = {
            "report_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "plan_path": str(plan_path),
            **result,
        }
        output = write_report(report, Path(args.output) if args.output else None)
        print(output)
        return 0
    except Exception as exc:
        report = {
            "report_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "plan_path": str(plan_path),
            "project_path": plan.get("project_path", ""),
            "project_slug": plan.get("project_slug", plan_path.stem),
            "tool": args.tool,
            "status": "failed",
            "error": str(exc),
        }
        output = write_report(report, Path(args.output) if args.output else None)
        print(output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
