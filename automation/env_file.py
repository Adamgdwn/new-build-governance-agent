#!/usr/bin/env python3
"""Canonical .env file parsing, formatting, and update helpers.

This is the single implementation of env-file handling for the governance
automation. env_sync.py, master_env.py, and stripe_provision.py all import
from here instead of carrying their own copies.
"""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path

ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")


def is_valid_env_key(key: str) -> bool:
    """Return True when key is a valid environment variable name."""
    return ENV_KEY_RE.fullmatch(key) is not None


def parse_env_value(raw: str) -> str:
    """Parse the value portion of a KEY=VALUE env line.

    Handles single/double quoting via shlex and strips trailing
    whitespace-delimited comments from unquoted values.
    """
    value = raw.strip()
    if not value:
        return ""
    if value[:1] in {"'", '"'}:
        try:
            return shlex.split(value, comments=False)[0]
        except ValueError:
            return value.strip("'\"")
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse an env file into a dict, skipping comments and malformed lines.

    Accepts an optional ``export `` prefix on keys. Returns an empty dict when
    the file does not exist.
    """
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.removeprefix("export ").strip()
        if is_valid_env_key(key):
            values[key] = parse_env_value(raw_value)
    return values


def format_env_value(value: str) -> str:
    """Format a value for writing to an env file, quoting when needed."""
    if not value:
        return ""
    if re.search(r"\s|#", value):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def read_env_lines(path: Path, missing_file_header: list[str] | None = None) -> list[str]:
    """Read an env file as raw lines, returning a header block when absent."""
    if not path.exists():
        return list(missing_file_header or [])
    return path.read_text(encoding="utf-8", errors="ignore").splitlines()


def write_env_lines(path: Path, lines: list[str]) -> None:
    """Write env lines with a trailing newline and owner-only permissions."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    os.chmod(path, 0o600)


def update_env_values(
    path: Path,
    updates: dict[str, str],
    overwrite: bool,
    section_comment: str = "# ===== Added by env_file.py =====",
    missing_file_header: list[str] | None = None,
) -> dict[str, str]:
    """Update KEY=VALUE lines in place, appending new keys under a comment.

    Existing keys are rewritten only when ``overwrite`` is True or their
    current value is blank. Non-assignment lines (comments, blanks) are kept
    verbatim. Returns a map of key -> "filled" | "updated" | "added".
    """
    lines = read_env_lines(path, missing_file_header)
    existing = parse_env_file(path)
    applied: dict[str, str] = {}
    seen: set[str] = set()
    rendered: list[str] = []

    for line in lines:
        match = _ASSIGNMENT_RE.match(line)
        if not match:
            rendered.append(line)
            continue
        key = match.group(1)
        seen.add(key)
        if key in updates and (overwrite or not existing.get(key)):
            rendered.append(f"{key}={format_env_value(updates[key])}")
            applied[key] = "updated" if existing.get(key) else "filled"
        else:
            rendered.append(line)

    missing = [key for key in updates if key not in seen]
    if missing:
        if rendered and rendered[-1].strip():
            rendered.append("")
        rendered.append(section_comment)
        for key in missing:
            rendered.append(f"{key}={format_env_value(updates[key])}")
            applied[key] = "added"

    write_env_lines(path, rendered)
    return applied
