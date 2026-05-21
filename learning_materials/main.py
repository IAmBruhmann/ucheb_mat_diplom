#!/usr/bin/env python3
"""Entry point for the educational materials catalog application."""

from __future__ import annotations

import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from learning_materials.constants import DB_PATH
from learning_materials.theme import apply_theme
from learning_materials.database import Database
from learning_materials.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 11))
    apply_theme(app, "dark")

    db = Database(DB_PATH)
    db.initialize()
    window = MainWindow(db)
    window.resize(1200, 720)
    window.show()
    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
