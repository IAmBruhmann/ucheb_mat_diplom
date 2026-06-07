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
    text_muted: str
    accent: str
    accent_hover: str
    primary: str
    primary_hover: str
    primary_pressed: str
    bar: str
    header_bg: str
    header_text: str
    border: str
    border_focus: str
    row_hover: str
    nav_hover: str
    discount_row: QColor
    no_access: QColor


DARK = ThemePalette(
    bg="#141820",
    bg_alt="#1c2330",
    bg_input="#252d3d",
    text="#eef2ff",
    text_muted="#9aa8c7",
    accent="#2d3748",
    accent_hover="#3d4d66",
    primary="#4f8cff",
    primary_hover="#6ba1ff",
    primary_pressed="#3a6fd6",
    bar="#0f131a",
    header_bg="#1a2230",
    header_text="#eef2ff",
    border="#334155",
    border_focus="#4f8cff",
    row_hover="#243049",
    nav_hover="#2a3550",
    discount_row=QColor("#1f3d2f"),
    no_access=QColor("#1f2a3d"),
)

LIGHT = ThemePalette(
    bg="#f0f4fa",
    bg_alt="#ffffff",
    bg_input="#ffffff",
    text="#1e293b",
    text_muted="#64748b",
    accent="#e2e8f0",
    accent_hover="#cbd5e1",
    primary="#2563eb",
    primary_hover="#3b82f6",
    primary_pressed="#1d4ed8",
    bar="#ffffff",
    header_bg="#f8fafc",
    header_text="#1e293b",
    border="#cbd5e1",
    border_focus="#2563eb",
    row_hover="#e8f0fe",
    nav_hover="#e2e8f0",
    discount_row=QColor("#dcfce7"),
    no_access=QColor("#dbeafe"),
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
    font-size: 11pt;
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
    padding: 10px 14px;
    border-bottom: 2px solid {p.border};
}}
#appLogo {{
    background: transparent;
}}
#pageTitle {{
    font-weight: 700;
    font-size: 18pt;
    color: {p.text};
    padding: 4px 0;
}}
QPushButton {{
    background-color: {p.accent};
    color: {p.text};
    border: 1px solid {p.border};
    padding: 8px 16px;
    border-radius: 8px;
    min-height: 20px;
}}
QPushButton:hover {{
    background-color: {p.accent_hover};
    border-color: {p.primary};
}}
QPushButton:pressed {{
    background-color: {p.primary_pressed};
    padding-top: 9px;
    padding-bottom: 7px;
}}
QPushButton:disabled {{
    color: {p.text_muted};
    background-color: {p.bg_input};
}}
#primaryBtn {{
    background-color: {p.primary};
    color: #ffffff;
    border: 1px solid {p.primary_hover};
    font-weight: 600;
}}
#primaryBtn:hover {{
    background-color: {p.primary_hover};
    border-color: {p.primary_hover};
}}
#primaryBtn:pressed {{
    background-color: {p.primary_pressed};
}}
#navBtn {{
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}}
#navBtn:hover {{
    background-color: {p.nav_hover};
    border-color: {p.border};
}}
#navBtn:pressed {{
    background-color: {p.accent};
}}
#navBtn[active=true] {{
    background-color: {p.primary};
    color: #ffffff;
    border-color: {p.primary_hover};
}}
#navBtn[active=true]:hover {{
    background-color: {p.primary_hover};
}}
#logoutBtn {{
    background-color: {p.accent};
    border-radius: 20px;
    padding: 8px 22px;
    font-weight: 600;
}}
#logoutBtn:hover {{
    background-color: {p.primary};
    color: #ffffff;
    border-color: {p.primary_hover};
}}
#themeToggle {{
    background-color: {p.accent};
    color: {p.text};
    font-weight: 700;
    border-radius: 16px;
    padding: 6px 14px;
}}
#themeToggle:hover {{
    background-color: {p.primary};
    color: #ffffff;
}}
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {p.bg_input};
    color: {p.text};
    border: 1px solid {p.border};
    padding: 7px 10px;
    border-radius: 8px;
    selection-background-color: {p.primary};
    selection-color: #ffffff;
}}
QLineEdit:hover, QTextEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover, QComboBox:hover {{
    border-color: {p.primary_hover};
}}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 2px solid {p.border_focus};
    padding: 6px 9px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {p.bg_input};
    color: {p.text};
    border: 1px solid {p.border};
    selection-background-color: {p.primary};
    selection-color: #ffffff;
    outline: none;
}}
QTableWidget {{
    background-color: {p.bg_alt};
    color: {p.text};
    gridline-color: {p.border};
    border: 1px solid {p.border};
    border-radius: 10px;
    alternate-background-color: {p.bg};
}}
QTableWidget::item {{
    padding: 6px;
}}
QTableWidget::item:hover {{
    background-color: {p.row_hover};
}}
QTableWidget::item:selected {{
    background-color: {p.primary};
    color: #ffffff;
}}
QHeaderView {{
    background-color: {p.header_bg};
}}
QHeaderView::section {{
    background-color: {p.header_bg};
    color: {p.header_text};
    padding: 8px;
    border: none;
    border-bottom: 2px solid {p.border};
    font-weight: 600;
}}
QTableCornerButton::section {{
    background-color: {p.header_bg};
    border: none;
}}
QScrollBar:vertical {{
    background: {p.bg};
    width: 10px;
    margin: 0;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {p.accent_hover};
    min-height: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical:hover {{
    background: {p.primary};
}}
QScrollBar:horizontal {{
    background: {p.bg};
    height: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal {{
    background: {p.accent_hover};
    min-width: 24px;
    border-radius: 5px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {p.primary};
}}
QMessageBox {{
    background-color: {p.bg};
    color: {p.text};
}}
"""


def apply_table_header_style(table: QTableWidget) -> None:
    p = current_palette()
    section_style = f"""
    QHeaderView::section {{
        background-color: {p.header_bg};
        color: {p.header_text};
        border: none;
        border-bottom: 2px solid {p.border};
        padding: 8px;
        font-weight: 600;
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
