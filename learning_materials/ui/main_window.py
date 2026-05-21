"""Main application window."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from learning_materials.database import Database, UserRecord
from learning_materials.theme import apply_theme, toggle_button_label
from learning_materials.ui.catalog import CatalogWidget
from learning_materials.ui.login import LoginWidget
from learning_materials.ui.main_shell import MainShell


class MainWindow(QMainWindow):
    def __init__(self, db: Database) -> None:
        super().__init__()
        self._db = db
        self.setWindowTitle("Учебные материалы")

        self._container = QWidget()
        self.setCentralWidget(self._container)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self._stack = QStackedWidget()
        container_layout.addWidget(self._stack)

        self._theme_btn = QPushButton(toggle_button_label(), self._container)
        self._theme_btn.setObjectName("themeToggle")
        self._theme_btn.setFixedHeight(32)
        self._theme_btn.clicked.connect(self._toggle_theme)
        self._position_theme_button()

        self._login = LoginWidget(db, self._enter_shell)
        self._login.set_guest_handler(self._enter_guest)
        self._stack.addWidget(self._login)

        self._guest_page = QWidget()
        guest_layout = QVBoxLayout(self._guest_page)
        back_btn = QPushButton("Назад к входу")
        back_btn.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        guest_layout.addWidget(back_btn)
        self._guest_catalog = CatalogWidget(db, "guest", None, lambda _id: None)
        guest_layout.addWidget(self._guest_catalog)
        self._stack.addWidget(self._guest_page)

        self._shell: Optional[MainShell] = None

    def resizeEvent(self, event: QResizeEvent | None) -> None:
        super().resizeEvent(event)
        self._position_theme_button()

    def _position_theme_button(self) -> None:
        margin = 12
        self._theme_btn.adjustSize()
        width = max(self._theme_btn.sizeHint().width(), 110)
        self._theme_btn.setFixedWidth(width)
        self._theme_btn.move(
            self._container.width() - width - margin,
            margin,
        )
        self._theme_btn.raise_()

    def _toggle_theme(self) -> None:
        app = QApplication.instance()
        if app is None or not isinstance(app, QApplication):
            return
        apply_theme(app)
        self._theme_btn.setText(toggle_button_label())
        self._refresh_catalogs()

    def _refresh_catalogs(self) -> None:
        self._guest_catalog.reload()
        if self._shell is not None:
            self._shell.refresh_catalog()

    def _enter_guest(self) -> None:
        self._guest_catalog.reload()
        self._stack.setCurrentIndex(1)

    def _enter_shell(self, user: UserRecord) -> None:
        if self._shell is not None:
            self._stack.removeWidget(self._shell)
            self._shell.deleteLater()
            self._shell = None
        self._shell = MainShell(self._db, user)
        self._shell.set_logout_handler(self._logout)
        self._stack.addWidget(self._shell)
        self._stack.setCurrentWidget(self._shell)

    def _logout(self) -> None:
        self._stack.setCurrentIndex(0)
