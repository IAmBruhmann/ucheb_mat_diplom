"""Requests for educational materials."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from learning_materials.database import Database, UserRecord
from learning_materials.theme import apply_table_header_style


class RequestsWidget(QWidget):
    def __init__(self, db: Database, user: UserRecord) -> None:
        super().__init__()
        self._db = db
        self._user = user

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Заявки на учебные материалы"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск по студенту, материалу, статусу...")
        layout.addWidget(self._search)
        self._table = QTableWidget(0, 7)
        self._table.setHorizontalHeaderLabels(
            ["№", "Пользователь", "Код", "Материал", "Дата", "Кол-во", "Статус"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)
        self._search.textChanged.connect(lambda _text: self.reload())
        self.reload()

    def reload(self) -> None:
        apply_table_header_style(self._table)
        rows = self._db.list_requests(self._user)
        query = self._search.text().strip().lower()
        self._table.setRowCount(0)
        for request in rows:
            blob = " ".join(
                str(request[key]) for key in ("full_name", "code", "title", "status")
            ).lower()
            if query and query not in blob:
                continue
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                request["request_number"],
                request["full_name"],
                request["code"],
                request["title"],
                request["request_date"],
                request["quantity"],
                request["status"],
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 0:
                    item.setData(Qt.ItemDataRole.UserRole, int(request["id"]))
                self._table.setItem(row, col, item)

    def _on_double_click(self) -> None:
        if self._user.role_code not in {"teacher", "admin"}:
            return
        row = self._table.currentRow()
        if row < 0:
            return
        number_item = self._table.item(row, 0)
        status_item = self._table.item(row, 6)
        if number_item is None or status_item is None:
            return
        request_id = int(number_item.data(Qt.ItemDataRole.UserRole))
        statuses = ["Новая", "В работе", "Выдано", "Отклонено"]
        current = status_item.text()
        current_index = statuses.index(current) if current in statuses else 0
        value, ok = QInputDialog.getItem(
            self,
            "Статус заявки",
            "Выберите новый статус:",
            statuses,
            current_index,
            False,
        )
        if ok and value:
            self._db.update_request_status(request_id, value)
            self.reload()
