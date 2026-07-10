#!/usr/bin/env python3
"""Execute approved promotion targets from a generated promotion plan."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXPORT_ROOT = REPO_ROOT / "data" / "new-build-governance-agent" / "exports"
SECRET_PATH_PATTERNS = (
    ".env",
    ".env.",
    ".pem",
    ".key",
    "id_rsa",
    "id_ed25519",
    "secrets.",
)


def build_exec_env(project_path: Path) -> dict[str, str]:
    env = dict(os.environ)
    path_parts = [
        str(project_path / "node_modules" / ".bin"),
        str(Path.home() / ".local" / "bin"),
        str(Path.home() / "bin"),
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


def stage_by_name(plan: dict, name: str) -> dict:
    for stage in plan.get("stages", []):
        if stage.get("name") == name:
            return stage
    raise ValueError(f"Stage not found: {name}")


def run_cmd(command: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def git(project_path: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return run_cmd(["git", *args], project_path, env)


def gh(project_path: Path, env: dict[str, str], *args: str) -> subprocess.CompletedProcess[str]:
    return run_cmd(["gh", *args], project_path, env)


def require_success(proc: subprocess.CompletedProcess[str], message: str) -> None:
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "No output"
        raise RuntimeError(f"{message}: {detail}")


def parse_porcelain_path(line: str) -> str:
    path = line[3:].strip()
    if " -> " in path:
        path = path.split(" -> ", 1)[1]
    return path


def secret_like_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    name = Path(normalized).name
    return any(
        name == pattern or name.startswith(pattern) or name.endswith(pattern)
        for pattern in SECRET_PATH_PATTERNS
    )


def choose_stage_files(
    changed_files: list[str],
    include_files: list[str] | None,
    allow_stage_all: bool,
) -> tuple[str, list[str]]:
    changed_paths = [parse_porcelain_path(line) for line in changed_files]
    changed_set = set(changed_paths)
    blocked = [path for path in changed_paths if secret_like_path(path)]
    if blocked:
        raise RuntimeError(
            "Refusing to stage secret-like paths. Review or ignore these files first: "
            + ", ".join(sorted(blocked))
        )

    if include_files:
        requested = [path.strip() for path in include_files if path.strip()]
        unknown = [path for path in requested if path not in changed_set]
        if unknown:
            raise RuntimeError(
                "Requested include files are not present in git status: "
                + ", ".join(sorted(unknown))
            )
        return "explicit_file_list", requested

    if allow_stage_all:
        return "approved_full_working_tree", changed_paths

    raise RuntimeError(
        "GitHub execution requires an explicit staged file decision. "
        "Pass one or more --include-file values, or pass --allow-stage-all after reviewing git status."
    )


def execute_github(
    plan: dict,
    commit_message: str | None,
    include_files: list[str] | None,
    allow_stage_all: bool,
) -> dict:
    project_path = Path(plan["project_path"]).expanduser().resolve()
    env = build_exec_env(project_path)

    sync_stage = stage_by_name(plan, "prepare_external_sync")
    github_target = sync_stage.get("targets", {}).get("github", {})
    if not github_target.get("relevant"):
        raise RuntimeError("GitHub is not a relevant target for this plan.")

    require_success(
        git(project_path, env, "rev-parse", "--show-toplevel"), "Project is not a git repository"
    )
    require_success(gh(project_path, env, "auth", "status"), "GitHub CLI is not authenticated")

    status_proc = git(project_path, env, "status", "--porcelain")
    require_success(status_proc, "Unable to inspect git status")
    changed_files = [line for line in status_proc.stdout.splitlines() if line.strip()]
    if not changed_files:
        raise RuntimeError("No local changes detected to commit and push.")
    stage_mode, staged_files = choose_stage_files(changed_files, include_files, allow_stage_all)

    branch_proc = git(project_path, env, "branch", "--show-current")
    require_success(branch_proc, "Unable to determine current git branch")
    branch = branch_proc.stdout.strip()
    if not branch:
        raise RuntimeError(
            "Detached HEAD is not supported for execute mode. Check out a branch first."
        )

    remote_proc = git(project_path, env, "remote", "get-url", "origin")
    require_success(remote_proc, "Unable to resolve git remote 'origin'")
    remote_url = remote_proc.stdout.strip()

    repo_proc = gh(project_path, env, "repo", "view", "--json", "nameWithOwner,defaultBranchRef")
    require_success(repo_proc, "Unable to resolve GitHub repository metadata")
    repo_data = json.loads(repo_proc.stdout)
    repo_name = repo_data["nameWithOwner"]
    default_branch = repo_data["defaultBranchRef"]["name"]

    head_proc = git(project_path, env, "rev-parse", "HEAD")
    require_success(head_proc, "Unable to capture pre-push commit")
    previous_head = head_proc.stdout.strip()

    add_proc = git(project_path, env, "add", "--", *staged_files)
    require_success(add_proc, "Unable to stage local changes")

    message = (
        commit_message.strip()
        if commit_message and commit_message.strip()
        else f"Promote {plan['project_slug']} via New Build Governance Agent"
    )
    commit_proc = git(project_path, env, "commit", "-m", message)
    require_success(commit_proc, "Unable to create git commit")

    new_head_proc = git(project_path, env, "rev-parse", "HEAD")
    require_success(new_head_proc, "Unable to capture new commit")
    new_head = new_head_proc.stdout.strip()

    push_proc = git(project_path, env, "push", "-u", "origin", branch)
    require_success(push_proc, "Unable to push branch to GitHub")

    pr_url = ""
    if branch != default_branch:
        pr_view = gh(project_path, env, "pr", "view", "--json", "url")
        if pr_view.returncode == 0 and pr_view.stdout.strip():
            pr_url = json.loads(pr_view.stdout).get("url", "")
        else:
            pr_create = gh(
                project_path,
                env,
                "pr",
                "create",
                "--draft",
                "--base",
                default_branch,
                "--head",
                branch,
                "--title",
                f"[nba] Promote {plan['project_slug']}",
                "--body",
                (
                    "Promotion executed from New Build Governance Agent.\n\n"
                    f"- Project: {plan['project_slug']}\n"
                    f"- Commit: {new_head}\n"
                    f"- Rollback point: {previous_head}\n"
                ),
            )
            require_success(pr_create, "Unable to create draft pull request")
            pr_url = pr_create.stdout.strip()

    rollback_commands = [
        f"git checkout {branch}",
        f"git revert {new_head}",
        f"git push origin {branch}",
    ]
    if branch == default_branch:
        rollback_note = "The current branch is the default branch, so rollback is a revert commit that pushes a new correction to production."
    else:
        rollback_note = "The current branch is not the default branch, so rollback can be handled by closing the draft PR or reverting the pushed branch commit before merge."

    return {
        "target": "github",
        "project_path": str(project_path),
        "repo_name": repo_name,
        "remote_url": remote_url,
        "branch": branch,
        "default_branch": default_branch,
        "commit_message": message,
        "previous_head": previous_head,
        "new_head": new_head,
        "pr_url": pr_url,
        "changed_files": changed_files,
        "stage_mode": stage_mode,
        "staged_files": staged_files,
        "stdout": {
            "commit": commit_proc.stdout.strip(),
            "push": push_proc.stdout.strip(),
        },
        "rollback_note": rollback_note,
        "rollback_commands": rollback_commands,
    }


def write_report(report: dict, output: Path | None) -> Path:
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    if output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = (
            EXPORT_ROOT
            / f"execute-{report['target']}-{Path(report['project_path']).name}-{stamp}.json"
        )
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute an approved target from a promotion plan."
    )
    parser.add_argument("--plan", required=True, help="Path to the promotion plan JSON")
    parser.add_argument(
        "--target", required=True, choices=["github"], help="Which target to execute"
    )
    parser.add_argument("--commit-message", help="Commit message to use for the publish step")
    parser.add_argument(
        "--include-file",
        action="append",
        default=[],
        help="Changed file path to stage. Repeat for multiple files.",
    )
    parser.add_argument(
        "--allow-stage-all",
        action="store_true",
        help="After reviewing git status, explicitly approve staging every changed file except secret-like paths.",
    )
    parser.add_argument("--output", help="Optional output path for the execution report JSON")
    args = parser.parse_args()

    plan_path = Path(args.plan).expanduser().resolve()
    plan = load_plan(plan_path)
    try:
        if args.target == "github":
            result = execute_github(
                plan, args.commit_message, args.include_file, args.allow_stage_all
            )
        else:
            raise RuntimeError(f"Unsupported target: {args.target}")
        report = {
            "report_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "plan_path": str(plan_path),
            "project_slug": plan["project_slug"],
            "target": args.target,
            "status": "executed",
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
            "project_slug": plan.get("project_slug", plan_path.stem),
            "target": args.target,
            "status": "failed",
            "error": str(exc),
            "project_path": plan.get("project_path", ""),
            "stage_mode": "not_staged",
        }
        output = write_report(report, Path(args.output) if args.output else None)
        print(output)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
