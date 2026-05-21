"""Light and dark themes for the application."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QTableWidget

ThemeName = Literal["dark", "light"]


@dataclass(frozen=True)
class ThemePalette:
    bg: str
    bg_alt: str
    bg_input: str
    text: str
    accent: str
    accent_hover: str
    bar: str
    header_bg: str
    header_text: str
    border: str
    discount_row: QColor
    no_access: QColor


DARK = ThemePalette(
    bg="#1a1a1a",
    bg_alt="#2b2b2b",
    bg_input="#3a3a3a",
    text="#e8e8e8",
    accent="#4d4d4d",
    accent_hover="#5c5c5c",
    bar="#0d0d0d",
    header_bg="#252525",
    header_text="#e8e8e8",
    border="#404040",
    discount_row=QColor("#2d3a2d"),
    no_access=QColor("#2a3038"),
)

LIGHT = ThemePalette(
    bg="#f5f5f5",
    bg_alt="#ffffff",
    bg_input="#ffffff",
    text="#1a1a1a",
    accent="#e0e0e0",
    accent_hover="#d0d0d0",
    bar="#eeeeee",
    header_bg="#ffffff",
    header_text="#1a1a1a",
    border="#d0d0d0",
    discount_row=QColor("#dff4e4"),
    no_access=QColor("#dcebff"),
)

_current: ThemeName = "dark"


def current_theme() -> ThemeName:
    return _current


def current_palette() -> ThemePalette:
    return DARK if _current == "dark" else LIGHT


def build_stylesheet(palette: ThemePalette) -> str:
    p = palette
    return f"""
QWidget {{
    background-color: {p.bg};
    color: {p.text};
}}
QMainWindow, QDialog {{
    background-color: {p.bg};
}}
QLabel {{
    color: {p.text};
    background: transparent;
}}
#topBar {{
    background-color: {p.bar};
    color: {p.text};
    padding: 8px;
    border-bottom: 1px solid {p.border};
}}
#pageTitle {{
    font-weight: bold;
    font-size: 16px;
    color: {p.text};
}}
QPushButton {{
    background-color: {p.accent};
    color: {p.text};
    border: 1px solid {p.border};
    padding: 6px 14px;
    border-radius: 4px;
}}
QPushButton:hover {{
    background-color: {p.accent_hover};
}}
QPushButton:pressed {{
    background-color: {p.accent_hover};
}}
#themeToggle {{
    background-color: {p.accent};
    color: {p.text};
    font-weight: bold;
}}
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {p.bg_input};
    color: {p.text};
    border: 1px solid {p.border};
    padding: 4px;
    border-radius: 3px;
}}
QComboBox QAbstractItemView {{
    background-color: {p.bg_input};
    color: {p.text};
    selection-background-color: {p.accent_hover};
    selection-color: {p.text};
}}
QTableWidget {{
    background-color: {p.bg_alt};
    color: {p.text};
    gridline-color: {p.border};
    border: 1px solid {p.border};
}}
QTableWidget::item {{
    background-color: {p.bg_alt};
    color: {p.text};
}}
QTableWidget::item:selected {{
    background-color: {p.accent_hover};
    color: {p.text};
}}
QHeaderView {{
    background-color: {p.header_bg};
}}
QHeaderView::section {{
    background-color: {p.header_bg};
    color: {p.header_text};
    padding: 6px;
    border: 1px solid {p.border};
}}
QTableCornerButton::section {{
    background-color: {p.header_bg};
    border: 1px solid {p.border};
}}
QMessageBox {{
    background-color: {p.bg};
    color: {p.text};
}}
"""


def apply_table_header_style(table: QTableWidget) -> None:
    """Apply header colors directly (Qt sometimes ignores global QSS on headers)."""
    p = current_palette()
    section_style = f"""
    QHeaderView::section {{
        background-color: {p.header_bg};
        color: {p.header_text};
        border: 1px solid {p.border};
        padding: 6px;
    }}
    """
    table.horizontalHeader().setStyleSheet(section_style)
    table.verticalHeader().setStyleSheet(section_style)


def toggle_button_label() -> str:
    return "☀ Светлая" if _current == "dark" else "🌙 Тёмная"


def apply_theme(app: QApplication, name: ThemeName | None = None) -> ThemeName:
    global _current
    if name is not None:
        _current = name
    else:
        _current = "light" if _current == "dark" else "dark"
    app.setStyleSheet(build_stylesheet(current_palette()))
    return _current
