"""User management screen."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from learning_materials.database import Database, UserRecord
from learning_materials.theme import apply_table_header_style
from learning_materials.ui.messages import show_message


class UsersWidget(QWidget):
    def __init__(self, db: Database, admin: UserRecord) -> None:
        super().__init__()
        self._db = db
        self._admin = admin
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Пользователи системы"))
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["ID", "ФИО", "Логин", "Роль"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._table)
        bar = QHBoxLayout()
        add_btn = QPushButton("Добавить пользователя")
        add_btn.setObjectName("primaryBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add)
        delete_btn = QPushButton("Удалить выбранного")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self._delete)
        bar.addWidget(add_btn)
        bar.addWidget(delete_btn)
        layout.addLayout(bar)
        self.reload()

    def reload(self) -> None:
        apply_table_header_style(self._table)
        self._table.setRowCount(0)
        for user in self._db.list_users():
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
            self._table.setItem(row, 1, QTableWidgetItem(str(user["full_name"])))
            self._table.setItem(row, 2, QTableWidgetItem(str(user["login"])))
            self._table.setItem(row, 3, QTableWidgetItem(str(user["role_name"])))

    def _add(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Новый пользователь")
        form = QFormLayout(dialog)
        full_name = QLineEdit()
        login = QLineEdit()
        password = QLineEdit()
        password.setEchoMode(QLineEdit.EchoMode.Password)
        role = QComboBox()
        role.addItem("Студент", "student")
        role.addItem("Преподаватель", "teacher")
        role.addItem("Администратор", "admin")
        form.addRow("ФИО", full_name)
        form.addRow("Логин", login)
        form.addRow("Пароль", password)
        form.addRow("Роль", role)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        if not full_name.text().strip() or not login.text().strip():
            show_message(self, "Ошибка", "Заполните ФИО и логин.", QMessageBox.Icon.Warning)
            return
        try:
            role_id = self._db.get_role_id(str(role.currentData()))
            self._db.insert_user(
                role_id, full_name.text().strip(), login.text().strip(), password.text()
            )
        except Exception as exc:  # noqa: BLE001
            show_message(self, "Ошибка", str(exc), QMessageBox.Icon.Critical)
            return
        self.reload()

    def _delete(self) -> None:
        row = self._table.currentRow()
        if row < 0:
            return
        user_id = int(self._table.item(row, 0).text())
        if user_id == self._admin.id:
            show_message(
                self,
                "Запрещено",
                "Нельзя удалить собственную учетную запись администратора.",
                QMessageBox.Icon.Warning,
            )
            return
        name = self._table.item(row, 1).text()
        extra = ""
        if self._db.user_has_requests(user_id):
            extra = "\n\nУ пользователя есть заявки — они тоже будут удалены."
        confirm = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить пользователя «{name}»?{extra}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        try:
            self._db.delete_user(user_id)
        except Exception as exc:  # noqa: BLE001
            show_message(
                self,
                "Ошибка удаления",
                f"Не удалось удалить пользователя: {exc}",
                QMessageBox.Icon.Critical,
            )
            return
        self.reload()
