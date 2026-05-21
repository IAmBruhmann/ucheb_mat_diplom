"""Shared constants and paths for the application."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

Mode = Literal["guest", "student", "teacher", "admin"]

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "data" / "learning_materials.sqlite3"
