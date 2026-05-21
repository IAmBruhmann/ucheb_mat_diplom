"""Authenticated user workspace with navigation."""

from __future__ import annotations

from typing import Callable, Optional, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from learning_materials.constants import Mode
from learning_materials.database import Database, UserRecord
from learning_materials.ui.catalog import CatalogWidget
from learning_materials.ui.material_editor import MaterialEditorDialog
from learning_materials.ui.requests import RequestsWidget
from learning_materials.ui.users import UsersWidget


class MainShell(QWidget):
    def __init__(self, db: Database, user: UserRecord) -> None:
        super().__init__()
        self._db = db
        self._user = user
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        top.addStretch()
        logout = QPushButton("Выйти")
        logout.clicked.connect(self._logout_request)
        top.addWidget(logout, alignment=Qt.AlignmentFlag.AlignCenter)
        top.addStretch()
        top_bar = QWidget()
        top_bar.setLayout(top)
        top_bar.setObjectName("topBar")
        layout.addWidget(top_bar)

        nav = QHBoxLayout()
        nav.addWidget(QLabel(f"«Учебные материалы» - {user.full_name}"))
        nav.addStretch()
        self._btn_catalog = QPushButton("Каталог")
        self._btn_requests = QPushButton("Заявки")
        self._btn_users = QPushButton("Пользователи")
        nav.addWidget(self._btn_catalog)
        nav.addWidget(self._btn_requests)
        nav.addWidget(self._btn_users)
        layout.addLayout(nav)

        mode: Mode = (
            cast(Mode, user.role_code)
            if user.role_code in {"student", "teacher", "admin"}
            else "student"
        )
        self._stack = QStackedWidget()
        self._catalog = CatalogWidget(db, mode, user, self._open_editor)
        self._requests = RequestsWidget(db, user)
        self._users = UsersWidget(db, user)
        self._stack.addWidget(self._catalog)
        self._stack.addWidget(self._requests)
        self._stack.addWidget(self._users)
        layout.addWidget(self._stack)

        self._btn_catalog.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        self._btn_requests.clicked.connect(self._open_requests)
        self._btn_users.clicked.connect(lambda: self._stack.setCurrentIndex(2))
        self._btn_users.setVisible(user.role_code == "admin")
        self._logout_callback: Optional[Callable[[], None]] = None

    def set_logout_handler(self, callback: Callable[[], None]) -> None:
        self._logout_callback = callback

    def _logout_request(self) -> None:
        if self._logout_callback is not None:
            self._logout_callback()

    def _open_requests(self) -> None:
        self._requests.reload()
        self._stack.setCurrentIndex(1)

    def refresh_catalog(self) -> None:
        self._catalog._fill_filters()
        self._catalog.reload()
        self._requests.reload()
        self._users.reload()

    def _open_editor(self, material_id: Optional[int]) -> None:
        if self._user.role_code != "admin":
            return
        if MaterialEditorDialog.try_open(self, self._db, material_id):
            self.refresh_catalog()
