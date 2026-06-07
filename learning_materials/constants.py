"""Shared constants and paths for the application."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

Mode = Literal["guest", "student", "teacher", "admin"]

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_PNG_PATH = ASSETS_DIR / "logo.png"
LOGO_SVG_PATH = ASSETS_DIR / "logo.svg"
LOGO_PATH = LOGO_PNG_PATH if LOGO_PNG_PATH.exists() else LOGO_SVG_PATH
LOGO_COLOR = "#499BB6"
