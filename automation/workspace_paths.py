"""Where governed projects live: the code root and its category folders.

This is the one implementation every entry point uses: the GUI, the headless
wrapper (and therefore the terminal launchers, which preview through
``new_build_headless.py --plan``), and the env tools that locate
``.env.master``.

Folder names may carry a numeric ordering prefix, such as ``01. Code`` or
``03. Agents``. The prefix is ignored when a folder is recognised, and an
existing category folder is always reused rather than creating a parallel one
beside it.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ENV_CODE_ROOT = "NEW_BUILD_CODE_ROOT"

_ORDER_PREFIX = re.compile(r"^\d+\.\s*")
_CODE_ROOT_KINDS = frozenset({"code", "code projects"})
_AGENTS = "agents"
_APPLICATIONS = "applications"
_DEFAULT_CATEGORY_DIRS = {_AGENTS: "agents", _APPLICATIONS: "Applications"}


def folder_kind(name: str) -> str:
    """Return a folder name without its numeric ordering prefix, lower-cased."""
    return _ORDER_PREFIX.sub("", name).strip().lower()


def default_code_root(governance_home: Path | None = None) -> Path:
    configured = os.environ.get(ENV_CODE_ROOT, "").strip()
    if configured:
        return Path(configured).expanduser()

    if governance_home is not None:
        parent = governance_home.resolve().parent
        kind = folder_kind(parent.name)
        if kind in _CODE_ROOT_KINDS:
            return parent
        if kind in _DEFAULT_CATEGORY_DIRS:
            # Installed inside a category folder: <code root>/03. Agents/<this repo>.
            return parent.parent

    return Path.home() / "code"


def _category_dir(code_root: Path, kind: str) -> Path:
    """Reuse an existing category folder, preferring real folders over aliases.

    Falls back to the default folder name when none exists. Never creates
    anything; ``ensure_category_roots`` is the only function that writes.
    """
    try:
        matches = sorted(
            (
                child
                for child in code_root.iterdir()
                if child.is_dir() and folder_kind(child.name) == kind
            ),
            key=lambda child: (child.is_symlink(), child.name),
        )
    except OSError:
        matches = []
    return matches[0] if matches else code_root / _DEFAULT_CATEGORY_DIRS[kind]


def category_roots(governance_home: Path | None = None) -> tuple[Path, Path]:
    code_root = default_code_root(governance_home)
    return _category_dir(code_root, _AGENTS), _category_dir(code_root, _APPLICATIONS)


def ensure_category_roots(governance_home: Path | None = None) -> tuple[Path, Path]:
    agents_root, apps_root = category_roots(governance_home)
    agents_root.mkdir(parents=True, exist_ok=True)
    apps_root.mkdir(parents=True, exist_ok=True)
    return agents_root, apps_root
