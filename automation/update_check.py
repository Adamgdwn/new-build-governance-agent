#!/usr/bin/env python3
"""Read-only update checks for New Build Governance Agent."""

from __future__ import annotations

import argparse
import json
import re
import socket
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Callable

from version import GITHUB_REPO_URL, PRODUCT_NAME, REPO_FULL_NAME, get_version

GITHUB_API_ROOT = "https://api.github.com"
USER_AGENT = "new-build-governance-agent-update-check"
STATUS_CURRENT = "current"
STATUS_BEHIND = "behind"
STATUS_AHEAD = "ahead"
STATUS_UNABLE = "unable_to_check"

_SEMVER_RE = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


@dataclass(frozen=True)
class RemoteVersion:
    version: str
    source: str
    url: str


@dataclass(frozen=True)
class UpdateCheckResult:
    status: str
    local_version: str
    latest_version: str | None = None
    source: str | None = None
    repository: str = REPO_FULL_NAME
    repository_url: str = GITHUB_REPO_URL
    checked_url: str | None = None
    message: str = ""
    error: str | None = None


class UpdateCheckError(RuntimeError):
    """Raised when a remote update source cannot provide a version."""


FetchJson = Callable[[str, float], Any]


def parse_semver(value: str) -> tuple[int, int, int] | None:
    match = _SEMVER_RE.match(value.strip())
    if not match:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return (major, minor, patch)


def normalize_version(value: str) -> str:
    return value.strip().lstrip("v")


def default_fetch_json(url: str, timeout: float) -> Any:
    request = urllib.request.Request(
        url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _release_url(repository: str) -> str:
    return f"{GITHUB_API_ROOT}/repos/{repository}/releases/latest"


def _tags_url(repository: str) -> str:
    return f"{GITHUB_API_ROOT}/repos/{repository}/tags?per_page=50"


def _latest_from_release(repository: str, fetch_json: FetchJson, timeout: float) -> RemoteVersion:
    url = _release_url(repository)
    payload = fetch_json(url, timeout)
    tag_name = str(payload.get("tag_name", "")).strip()
    parsed = parse_semver(tag_name)
    if not parsed:
        raise UpdateCheckError("latest GitHub release did not have a semantic version tag")
    return RemoteVersion(version=normalize_version(tag_name), source="GitHub release", url=url)


def _latest_from_tags(repository: str, fetch_json: FetchJson, timeout: float) -> RemoteVersion:
    url = _tags_url(repository)
    payload = fetch_json(url, timeout)
    if not isinstance(payload, list):
        raise UpdateCheckError("GitHub tags response was not a list")

    versions: list[tuple[tuple[int, int, int], str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        parsed = parse_semver(name)
        if parsed:
            versions.append((parsed, normalize_version(name)))

    if not versions:
        raise UpdateCheckError("no semantic version tags were found on GitHub")

    _, latest = max(versions, key=lambda item: item[0])
    return RemoteVersion(version=latest, source="GitHub tags", url=url)


def fetch_latest_remote_version(
    repository: str = REPO_FULL_NAME,
    fetch_json: FetchJson = default_fetch_json,
    timeout: float = 5.0,
) -> RemoteVersion:
    errors: list[str] = []
    for loader in (_latest_from_release, _latest_from_tags):
        try:
            return loader(repository, fetch_json, timeout)
        except urllib.error.HTTPError as exc:
            errors.append(f"{exc.code} from {exc.url}")
        except (
            urllib.error.URLError,
            TimeoutError,
            socket.timeout,
            json.JSONDecodeError,
            UpdateCheckError,
        ) as exc:
            errors.append(str(exc))
    detail = (
        "; ".join(error for error in errors if error) or "unable to read GitHub releases or tags"
    )
    raise UpdateCheckError(detail)


def check_for_updates(
    local_version: str | None = None,
    repository: str = REPO_FULL_NAME,
    fetch_json: FetchJson = default_fetch_json,
    timeout: float = 5.0,
) -> UpdateCheckResult:
    local = normalize_version(local_version or get_version())
    local_parsed = parse_semver(local)
    if not local_parsed:
        return UpdateCheckResult(
            status=STATUS_UNABLE,
            local_version=local,
            message="Unable to check for updates because the local VERSION is not semantic.",
            error=f"invalid local version: {local}",
        )

    try:
        remote = fetch_latest_remote_version(
            repository=repository, fetch_json=fetch_json, timeout=timeout
        )
    except UpdateCheckError as exc:
        return UpdateCheckResult(
            status=STATUS_UNABLE,
            local_version=local,
            checked_url=f"{GITHUB_API_ROOT}/repos/{repository}",
            message="Unable to check GitHub releases or tags.",
            error=str(exc),
        )

    remote_parsed = parse_semver(remote.version)
    if remote_parsed is None:
        return UpdateCheckResult(
            status=STATUS_UNABLE,
            local_version=local,
            latest_version=remote.version,
            source=remote.source,
            checked_url=remote.url,
            message="Unable to compare against a non-semantic remote version.",
            error=f"invalid remote version: {remote.version}",
        )

    if local_parsed == remote_parsed:
        status = STATUS_CURRENT
        message = "Installed version is current."
    elif local_parsed < remote_parsed:
        status = STATUS_BEHIND
        message = f"Installed version is behind {remote.version}."
    else:
        status = STATUS_AHEAD
        message = f"Installed version is ahead of the latest published version {remote.version}."

    return UpdateCheckResult(
        status=status,
        local_version=local,
        latest_version=remote.version,
        source=remote.source,
        checked_url=remote.url,
        message=message,
    )


def format_result(result: UpdateCheckResult) -> str:
    lines = [
        f"{PRODUCT_NAME} update check",
        f"Local version: {result.local_version}",
    ]
    if result.latest_version:
        source = f" ({result.source})" if result.source else ""
        lines.append(f"Latest version: {result.latest_version}{source}")
    lines.append(f"Status: {result.status}")
    if result.message:
        lines.append(result.message)
    if result.error:
        lines.append(f"Reason: {result.error}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check GitHub releases or tags for available updates."
    )
    parser.add_argument(
        "--json", action="store_true", help="Print the update check result as JSON."
    )
    parser.add_argument("--timeout", type=float, default=5.0, help="Network timeout in seconds.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = check_for_updates(timeout=args.timeout)
    if args.json:
        print(json.dumps(asdict(result), sort_keys=True))
    else:
        print(format_result(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
