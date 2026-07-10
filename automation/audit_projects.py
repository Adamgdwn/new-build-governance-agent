#!/usr/bin/env python3
"""
Audit governed projects created by New Build Governance Agent.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def read_project_metadata(path: Path) -> dict:
    control = path / "project-control.yaml"
    metadata = {
        "project_name": path.name,
        "project_type": "unknown",
        "risk_tier": "unknown",
        "governance_level": "",
        "builder": "unknown",
        "stack": "not specified",
    }
    if not control.exists():
        return metadata
    for line in control.read_text(encoding="utf-8").splitlines():
        if line.startswith("project_name:"):
            metadata["project_name"] = line.split(":", 1)[1].strip() or path.name
        elif line.startswith("project_type:"):
            metadata["project_type"] = line.split(":", 1)[1].strip() or "unknown"
        elif line.startswith("risk_tier:"):
            metadata["risk_tier"] = line.split(":", 1)[1].strip() or "unknown"
        elif line.startswith("governance_level:"):
            metadata["governance_level"] = line.split(":", 1)[1].strip()
    return metadata


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "automation"))
from workspace_paths import category_roots  # noqa: E402

PROJECT_ROOTS = list(category_roots(REPO_ROOT))
CHECKER = REPO_ROOT / "automation" / "governance_check.sh"
REGISTRY = REPO_ROOT / "automation" / "project_registry.py"


def build_subprocess_env() -> dict[str, str]:
    env = os.environ.copy()
    preferred = [
        "/usr/local/sbin",
        "/usr/local/bin",
        "/usr/sbin",
        "/usr/bin",
        "/sbin",
        "/bin",
    ]
    existing = [item for item in env.get("PATH", "").split(":") if item]
    merged: list[str] = []
    for item in preferred + existing:
        if item not in merged:
            merged.append(item)
    env["PATH"] = ":".join(merged)
    env.setdefault("GOVERNANCE_HOME", str(REPO_ROOT))
    return env


def discover_projects() -> list[Path]:
    projects: list[Path] = []
    seen: set[Path] = set()
    for root in PROJECT_ROOTS:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            resolved = child.resolve()
            if resolved in seen:
                continue
            if child.is_dir() and (child / "project-control.yaml").exists():
                projects.append(child)
                seen.add(resolved)
    return projects


def audit_project(path: Path) -> dict:
    proc = subprocess.run(
        ["bash", str(CHECKER), str(path)],
        capture_output=True,
        text=True,
        check=False,
        env=build_subprocess_env(),
    )
    stdout_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    missing = []
    warnings = []
    for line in stdout_lines:
        if line.startswith("FAIL: Missing required file "):
            missing.append(line.removeprefix("FAIL: Missing required file "))
        elif line.startswith("WARN: "):
            warnings.append(line.removeprefix("WARN: "))
    status = "pass" if proc.returncode == 0 else "fail"
    return {
        "path": str(path),
        "slug": path.name,
        "status": status,
        "missing_files": missing,
        "warnings": warnings,
        "output": stdout_lines,
    }


def register_project(path: Path) -> None:
    metadata = read_project_metadata(path)
    subprocess.run(
        [
            sys.executable,
            str(REGISTRY),
            "register",
            "--project-name",
            metadata["project_name"],
            "--slug",
            path.name,
            "--path",
            str(path),
            "--project-type",
            metadata["project_type"],
            "--risk-tier",
            metadata["risk_tier"],
            "--governance-level",
            metadata["governance_level"],
            "--builder",
            metadata["builder"],
            "--stack",
            metadata["stack"],
        ],
        check=True,
        env=build_subprocess_env(),
    )


def record_audit(result: dict) -> None:
    subprocess.run(
        [
            sys.executable,
            str(REGISTRY),
            "record-audit",
            "--slug",
            result["slug"],
            "--path",
            result["path"],
            "--status",
            result["status"],
            "--missing-files",
            *result["missing_files"],
            "--warnings",
            *result["warnings"],
        ],
        check=True,
        env=build_subprocess_env(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit governed projects under the standard workspace roots.")
    parser.add_argument("--json", action="store_true", help="Print JSON lines instead of human output.")
    args = parser.parse_args()

    for project in discover_projects():
        register_project(project)
        result = audit_project(project)
        record_audit(result)
        if args.json:
            print(json.dumps(result, sort_keys=True))
        else:
            print(f"[{result['status'].upper()}] {result['path']}")
            if result["missing_files"]:
                print("  Missing:", ", ".join(result["missing_files"]))
            if result["warnings"]:
                print("  Warnings:", "; ".join(result["warnings"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
