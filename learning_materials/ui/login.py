"""Login and registration screen."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from learning_materials.database import Database, UserRecord
from learning_materials.ui.logo import AppLogo
from learning_materials.ui.messages import show_message


class LoginWidget(QWidget):
    def __init__(self, db: Database, on_success: Callable[[UserRecord], None]) -> None:
        super().__init__()
        self._db = db
        self._on_success = on_success
        self._guest_callback: Optional[Callable[[], None]] = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(AppLogo(height=110))
        title = QLabel('Информационная система — «УМ»')
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addWidget(QLabel("Тестовые входы: admin/admin, teacher/teacher, student/student"))

        form = QFormLayout()
        self._login = QLineEdit()
        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Логин", self._login)
        form.addRow("Пароль", self._password)
        layout.addLayout(form)

        row = QHBoxLayout()
        login_btn = QPushButton("Войти")
        login_btn.setObjectName("primaryBtn")
        login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        login_btn.clicked.connect(self._try_login)
        guest_btn = QPushButton("Каталог как гость")
        guest_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        guest_btn.clicked.connect(self._guest)
        register_btn = QPushButton("Регистрация студента")
        register_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        register_btn.clicked.connect(self._register)
        row.addWidget(login_btn)
        row.addWidget(guest_btn)
        row.addWidget(register_btn)
        layout.addLayout(row)

    def set_guest_handler(self, callback: Callable[[], None]) -> None:
        self._guest_callback = callback

    def _try_login(self) -> None:
        user = self._db.verify_credentials(self._login.text().strip(), self._password.text())
        if user is None:
            show_message(
                self,
                "Ошибка авторизации",
                "Неверный логин или пароль.",
                QMessageBox.Icon.Warning,
            )
            return
        self._on_success(user)

    def _guest(self) -> None:
        if self._guest_callback is not None:
            self._guest_callback()

    def _register(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Регистрация студента")
        form = QFormLayout(dialog)
        full_name = QLineEdit()
        login = QLineEdit()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("ФИО", full_name)
        form.addRow("Логин", login)
        form.addRow("Пароль", password)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            self._db.insert_user(
                self._db.get_role_id("student"),
                full_name.text().strip(),
                login.text().strip(),
                password.text(),
            )
        except Exception as exc:  # noqa: BLE001
            show_message(self, "Ошибка", str(exc), QMessageBox.Icon.Critical)
            return
        show_message(
            self, "Готово", "Студент зарегистрирован. Теперь выполните вход.", QMessageBox.Icon.Information
        )
