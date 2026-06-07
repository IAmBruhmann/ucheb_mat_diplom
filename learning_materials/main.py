#!/usr/bin/env python3
"""Entry point for the educational materials catalog application."""

from __future__ import annotations

import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from learning_materials.theme import apply_theme
from learning_materials.database import Database
from learning_materials.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    apply_theme(app, "dark")

    try:
        db = Database.from_env()
        db.initialize()
    except Exception as exc:  # noqa: BLE001
        print(
            "Не удалось подключиться к MySQL. Установите сервер MySQL, задайте переменные "
            "MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE и выполните "
            "python build_database.py",
            file=sys.stderr,
        )
        print(exc, file=sys.stderr)
        sys.exit(1)
    window = MainWindow(db)
    window.resize(1200, 720)
    window.show()
    exit_code = app.exec()
    db.close()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
