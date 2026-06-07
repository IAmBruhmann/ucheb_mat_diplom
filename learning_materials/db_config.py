"""SQLite database path (no separate server required)."""

from __future__ import annotations

import os
from pathlib import Path

from learning_materials.constants import ROOT_DIR


def sqlite_path() -> Path:
    custom = os.getenv("SQLITE_PATH", "").strip()
    if custom:
        return Path(custom)
    return ROOT_DIR / "data" / "app.db"
