from __future__ import annotations

import os
from pathlib import Path

ENV_CODE_ROOT = "NEW_BUILD_CODE_ROOT"


def default_code_root(governance_home: Path | None = None) -> Path:
    configured = os.environ.get(ENV_CODE_ROOT, "").strip()
    if configured:
        return Path(configured).expanduser()

    if governance_home is not None:
        parent = governance_home.resolve().parent
        if parent.name.lower() in {"code", "01. code projects"}:
            return parent

    return Path.home() / "code"


def category_roots(governance_home: Path | None = None) -> tuple[Path, Path]:
    code_root = default_code_root(governance_home)
    return code_root / "agents", code_root / "Applications"


def ensure_category_roots(governance_home: Path | None = None) -> tuple[Path, Path]:
    agents_root, apps_root = category_roots(governance_home)
    agents_root.mkdir(parents=True, exist_ok=True)
    apps_root.mkdir(parents=True, exist_ok=True)
    return agents_root, apps_root
