#!/usr/bin/env python3
"""Guarded fast-forward self-update for New Build Governance Agent."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

from version import PRODUCT_NAME, REPO_ROOT

STATUS_UPDATED = "updated"
STATUS_UP_TO_DATE = "up_to_date"
STATUS_WOULD_UPDATE = "would_update"
STATUS_REFUSED = "refused"
STATUS_FAILED = "failed"


@dataclass(frozen=True)
class SelfUpdateResult:
    status: str
    message: str
    repo: str
    branch: str | None = None
    upstream: str | None = None
    before: str | None = None
    after: str | None = None
    dirty_files: list[str] | None = None
    error: str | None = None


class GitError(RuntimeError):
    """Raised when a git command fails."""


def run_git(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed"
        raise GitError(detail)
    return proc


def git_stdout(repo: Path, args: list[str]) -> str:
    return run_git(repo, args).stdout.strip()


def list_dirty_files(repo: Path) -> list[str]:
    output = git_stdout(repo, ["status", "--porcelain"])
    return [line for line in output.splitlines() if line.strip()]


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    proc = run_git(repo, ["merge-base", "--is-ancestor", ancestor, descendant], check=False)
    return proc.returncode == 0


def current_branch(repo: Path) -> str:
    branch = git_stdout(repo, ["branch", "--show-current"])
    if not branch:
        raise GitError("checkout is detached; self-update requires a named branch")
    return branch


def current_upstream(repo: Path) -> str:
    proc = run_git(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], check=False)
    if proc.returncode != 0:
        raise GitError("current branch has no upstream tracking branch")
    return proc.stdout.strip()


def remote_from_upstream(upstream: str) -> str:
    remote, _, branch = upstream.partition("/")
    if not remote or not branch:
        raise GitError(f"unable to determine remote from upstream: {upstream}")
    return remote


def self_update(repo: Path | str = REPO_ROOT, dry_run: bool = False) -> SelfUpdateResult:
    repo_path = Path(repo).resolve()
    try:
        git_stdout(repo_path, ["rev-parse", "--is-inside-work-tree"])
        branch = current_branch(repo_path)
        upstream = current_upstream(repo_path)
        dirty_files = list_dirty_files(repo_path)
        if dirty_files:
            return SelfUpdateResult(
                status=STATUS_REFUSED,
                message="Refusing to update because the working tree has local changes.",
                repo=str(repo_path),
                branch=branch,
                upstream=upstream,
                dirty_files=dirty_files,
            )

        remote = remote_from_upstream(upstream)
        before = git_stdout(repo_path, ["rev-parse", "HEAD"])
        run_git(repo_path, ["fetch", "--prune", "--tags", remote])
        upstream_sha = git_stdout(repo_path, ["rev-parse", upstream])

        if before == upstream_sha:
            return SelfUpdateResult(
                status=STATUS_UP_TO_DATE,
                message="Checkout is already up to date.",
                repo=str(repo_path),
                branch=branch,
                upstream=upstream,
                before=before,
                after=before,
            )

        if is_ancestor(repo_path, before, upstream_sha):
            if dry_run:
                return SelfUpdateResult(
                    status=STATUS_WOULD_UPDATE,
                    message="Checkout can be updated with a fast-forward merge.",
                    repo=str(repo_path),
                    branch=branch,
                    upstream=upstream,
                    before=before,
                    after=upstream_sha,
                )

            run_git(repo_path, ["merge", "--ff-only", upstream])
            after = git_stdout(repo_path, ["rev-parse", "HEAD"])
            return SelfUpdateResult(
                status=STATUS_UPDATED,
                message="Checkout updated with a fast-forward merge.",
                repo=str(repo_path),
                branch=branch,
                upstream=upstream,
                before=before,
                after=after,
            )

        if is_ancestor(repo_path, upstream_sha, before):
            message = "Refusing to update because the local branch is ahead of its upstream."
        else:
            message = "Refusing to update because the local branch has diverged from its upstream."
        return SelfUpdateResult(
            status=STATUS_REFUSED,
            message=message,
            repo=str(repo_path),
            branch=branch,
            upstream=upstream,
            before=before,
            after=upstream_sha,
        )
    except (GitError, OSError) as exc:
        return SelfUpdateResult(
            status=STATUS_FAILED,
            message="Self-update could not run.",
            repo=str(repo_path),
            error=str(exc),
        )


def format_result(result: SelfUpdateResult) -> str:
    lines = [f"{PRODUCT_NAME} self-update", f"Status: {result.status}", result.message]
    if result.branch:
        lines.append(f"Branch: {result.branch}")
    if result.upstream:
        lines.append(f"Upstream: {result.upstream}")
    if result.before:
        lines.append(f"Before: {result.before[:12]}")
    if result.after:
        lines.append(f"After: {result.after[:12]}")
    if result.dirty_files:
        lines.append("Local changes:")
        lines.extend(f"  {item}" for item in result.dirty_files)
    if result.error:
        lines.append(f"Reason: {result.error}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely fast-forward this checkout from its upstream branch."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Report whether a fast-forward update is possible."
    )
    parser.add_argument("--json", action="store_true", help="Print the self-update result as JSON.")
    parser.add_argument("--repo", default=str(REPO_ROOT), help="Repository path to update.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = self_update(repo=args.repo, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(asdict(result), sort_keys=True))
    else:
        print(format_result(result))
    return 0 if result.status in {STATUS_UPDATED, STATUS_UP_TO_DATE, STATUS_WOULD_UPDATE} else 2


if __name__ == "__main__":
    raise SystemExit(main())
