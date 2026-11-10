#!/usr/bin/env python3
"""Canonical .env file parsing, formatting, and update helpers.

This is the single implementation of env-file handling for the governance
automation. env_sync.py, master_env.py, and stripe_provision.py all import
from here instead of carrying their own copies.

Secret files are written through write_private_text, the one place that
restricts them to the current user on every platform.
"""

from __future__ import annotations

import ctypes
import ntpath
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

ENV_KEY_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_ASSIGNMENT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
_SID_RE = re.compile(r"S-1-\d+(?:-\d+)+")
_TOOL_TIMEOUT_SECONDS = 30
# Windows SDK values: SDDL_REVISION_1 (sddl.h), SE_FILE_OBJECT (accctrl.h), and
# DACL_SECURITY_INFORMATION | PROTECTED_DACL_SECURITY_INFORMATION (winnt.h).
_SDDL_REVISION_1 = 1
_SE_FILE_OBJECT = 1
_PROTECTED_DACL_INFORMATION = 0x00000004 | 0x80000000


class SecretFileProtectionError(OSError):
    """Raised when a secret file cannot be restricted to the current user."""


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


def _is_windows() -> bool:
    # A plain function rather than a sys.platform check, so mypy checks both
    # branches on every OS and tests can force the Windows branch.
    return os.name == "nt"


def _system_tool(name: str) -> str:
    # Absolute System32 path, so a same-named program in the working
    # directory cannot be run in place of the Windows tool.
    system_root = os.environ.get("SystemRoot") or r"C:\Windows"
    return ntpath.join(system_root, "System32", name)


def _protection_error(path: Path, detail: str) -> SecretFileProtectionError:
    hint = "Keep secret files in a folder you own, on a local drive that supports permissions"
    if _is_windows():
        # The literal user name, because %USERNAME% does not expand in PowerShell.
        user = os.environ.get("USERNAME") or "<your user name>"
        hint += f', or run: icacls "{path}" /inheritance:r /grant:r "{user}:F"'
    return SecretFileProtectionError(
        f"could not restrict {path} to the current user ({detail}). {hint}."
    )


def _current_user_sid(path: Path) -> str:
    command = [_system_tool("whoami.exe"), "/user", "/fo", "csv", "/nh"]
    try:
        result = subprocess.run(
            command, capture_output=True, timeout=_TOOL_TIMEOUT_SECONDS, check=False
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise _protection_error(path, f"whoami failed: {exc}") from exc
    # Console code-page output: the SID is ASCII, a user name may not be.
    sids = _SID_RE.findall(result.stdout.decode("utf-8", errors="replace"))
    if result.returncode != 0 or not sids:
        raise _protection_error(path, f"whoami exit {result.returncode} reported no SID")
    return sids[-1]


class _SecurityApi(NamedTuple):
    """The Windows calls _restrict_windows makes. Tests substitute fakes."""

    string_to_descriptor: Callable[..., int]  # ConvertStringSecurityDescriptorToSecurityDescriptorW
    get_dacl: Callable[..., int]  # GetSecurityDescriptorDacl
    set_named_security_info: Callable[..., int]  # SetNamedSecurityInfoW
    local_free: Callable[..., object]  # LocalFree
    last_error: Callable[[], int]
    format_error: Callable[[int], str]


def _load_security_api() -> _SecurityApi:
    # ctypes defines WinDLL, get_last_error and FormatError only on Windows,
    # so this is the one sys.platform check: mypy checks the body when it runs
    # on Windows (validate.ps1). Private WinDLL objects keep these signatures
    # out of the shared ctypes.windll cache.
    if sys.platform != "win32":
        raise OSError("the Windows security functions exist only on Windows")
    advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    pointer = ctypes.c_void_p
    out_pointer = ctypes.POINTER(ctypes.c_void_p)
    out_bool = ctypes.POINTER(ctypes.c_int)
    build = advapi32.ConvertStringSecurityDescriptorToSecurityDescriptorW
    build.argtypes = (ctypes.c_wchar_p, ctypes.c_uint32, out_pointer, pointer)
    build.restype = ctypes.c_int
    get_dacl = advapi32.GetSecurityDescriptorDacl
    get_dacl.argtypes = (pointer, out_bool, out_pointer, out_bool)
    get_dacl.restype = ctypes.c_int
    set_info = advapi32.SetNamedSecurityInfoW
    set_info.argtypes = (ctypes.c_wchar_p, ctypes.c_int, ctypes.c_uint32) + (pointer,) * 4
    set_info.restype = ctypes.c_uint32
    local_free = kernel32.LocalFree
    local_free.argtypes = (pointer,)
    local_free.restype = pointer
    return _SecurityApi(
        build, get_dacl, set_info, local_free, ctypes.get_last_error, ctypes.FormatError
    )


def _restrict_windows(path: Path) -> None:
    # One call replaces the whole access-control list with a protected list
    # that holds one entry: full control for the current user. Inherited and
    # explicit entries both go, including ones another tool added and the
    # copies a new file receives from a parent folder whose list is not
    # auto-inherited (Python's temp folders pass on SYSTEM, Administrators
    # and Owner Rights this way). No step in between widens access.
    sid = _current_user_sid(path)
    try:
        api = _load_security_api()
    except OSError as exc:
        raise _protection_error(path, f"Windows security functions unavailable: {exc}") from exc
    descriptor = ctypes.c_void_p()
    sddl = f"D:P(A;;FA;;;{sid})"
    if not api.string_to_descriptor(sddl, _SDDL_REVISION_1, ctypes.pointer(descriptor), None):
        raise _protection_error(
            path, f"could not build the access list, Windows error {api.last_error()}"
        )
    try:
        present, defaulted, dacl = ctypes.c_int(), ctypes.c_int(), ctypes.c_void_p()
        found = api.get_dacl(
            descriptor, ctypes.pointer(present), ctypes.pointer(dacl), ctypes.pointer(defaulted)
        )
        # A NULL list would grant everyone full control, so never pass one on.
        if not (found and present.value and dacl.value):
            raise _protection_error(
                path, f"could not read the new access list, Windows error {api.last_error()}"
            )
        # SetNamedSecurityInfoW takes the list without its descriptor, so the
        # "P" above does not reach the file: the protected flag blocks inheritance.
        code = api.set_named_security_info(
            os.path.abspath(path),
            _SE_FILE_OBJECT,
            _PROTECTED_DACL_INFORMATION,
            None,
            None,
            dacl,
            None,
        )
        if code:
            detail = " ".join(api.format_error(code).split())
            raise _protection_error(path, f"SetNamedSecurityInfoW error {code}: {detail}")
    finally:
        api.local_free(descriptor)


def restrict_to_owner(path: Path) -> None:
    """Restrict an existing file to the current user.

    POSIX sets mode 0600. On Windows, where chmod cannot do this, the file's
    access-control list is replaced with one protected entry: full control
    for the current user (see _restrict_windows). Raises
    SecretFileProtectionError when the restriction cannot be applied, for
    example on a FAT or exFAT drive.
    """
    if _is_windows():
        _restrict_windows(path)
        return
    try:
        os.chmod(path, 0o600)
    except OSError as exc:
        raise _protection_error(path, f"chmod 0600 failed: {exc}") from exc


def write_private_text(path: Path, text: str) -> None:
    """Write a secret file restricted to the current user (see restrict_to_owner).

    The file is restricted before any content is written. When the
    restriction fails, nothing is written: a file this call created is
    removed again, an existing file keeps its content, and the
    SecretFileProtectionError is raised to the caller.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_dir():
        raise IsADirectoryError(f"secret file path is a directory: {path}")
    created = False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        os.close(fd)
        created = True
    try:
        restrict_to_owner(path)
    except SecretFileProtectionError:
        if created:
            path.unlink(missing_ok=True)
        raise
    path.write_text(text, encoding="utf-8")


def write_env_lines(path: Path, lines: list[str]) -> None:
    """Write env lines with a trailing newline, restricted to the current user."""
    write_private_text(path, "\n".join(lines).rstrip() + "\n")


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
