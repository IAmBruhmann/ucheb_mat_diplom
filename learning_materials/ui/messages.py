"""Common message dialogs."""

from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


def show_message(parent: QWidget, title: str, text: str, icon: QMessageBox.Icon) -> None:
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(icon)
    box.exec()
