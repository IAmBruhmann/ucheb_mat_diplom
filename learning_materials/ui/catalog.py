"""Catalog of educational materials."""

from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from learning_materials.constants import Mode
from learning_materials.theme import apply_table_header_style, current_palette
from learning_materials.database import Database, MaterialRecord, UserRecord
from learning_materials.ui.logo import AppLogo
from learning_materials.ui.messages import show_message


class CatalogWidget(QWidget):
    def __init__(
        self,
        db: Database,
        mode: Mode,
        user: Optional[UserRecord],
        open_editor: Callable[[Optional[int]], None],
    ) -> None:
        super().__init__()
        self._db = db
        self._mode = mode
        self._user = user
        self._open_editor = open_editor
        self._all: list[MaterialRecord] = []

        layout = QVBoxLayout(self)
        header = QHBoxLayout()
        header.setSpacing(14)
        header.addWidget(AppLogo(height=76, centered=False))
        self._title = QLabel()
        self._title.setObjectName("pageTitle")
        self._title.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        header.addWidget(self._title, stretch=1)
        header_widget = QWidget()
        header_widget.setLayout(header)
        layout.addWidget(header_widget)

        controls = QGridLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Поиск по названию, описанию, автору, предмету...")
        self._subject_filter = QComboBox()
        self._type_filter = QComboBox()
        self._provider_filter = QComboBox()
        self._price_max = QDoubleSpinBox()
        self._price_max.setMaximum(9_999_999)
        self._price_max.setSpecialValueText("без ограничения")
        self._sort = QComboBox()
        self._sort.addItem("Без сортировки", "none")
        self._sort.addItem("Стоимость ↑", "price_asc")
        self._sort.addItem("Стоимость ↓", "price_desc")
        self._sort.addItem("Название А-Я", "title_asc")
        self._sort.addItem("Доступность ↑", "available_asc")
        self._sort.addItem("Доступность ↓", "available_desc")

        controls.addWidget(QLabel("Поиск"), 0, 0)
        controls.addWidget(self._search, 0, 1, 1, 3)
        controls.addWidget(QLabel("Предмет"), 1, 0)
        controls.addWidget(self._subject_filter, 1, 1)
        controls.addWidget(QLabel("Тип"), 1, 2)
        controls.addWidget(self._type_filter, 1, 3)
        controls.addWidget(QLabel("Поставщик"), 2, 0)
        controls.addWidget(self._provider_filter, 2, 1)
        controls.addWidget(QLabel("Стоимость до"), 2, 2)
        controls.addWidget(self._price_max, 2, 3)
        controls.addWidget(QLabel("Сортировка"), 3, 0)
        controls.addWidget(self._sort, 3, 1)

        self._controls_widget = QWidget()
        self._controls_widget.setLayout(controls)
        layout.addWidget(self._controls_widget)

        admin_bar = QHBoxLayout()
        self._btn_add = QPushButton("Добавить материал")
        self._btn_add.setObjectName("primaryBtn")
        self._btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_add.clicked.connect(lambda: self._open_editor(None))
        self._btn_delete = QPushButton("Удалить выбранный")
        self._btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_delete.clicked.connect(self._delete_selected)
        admin_bar.addWidget(self._btn_add)
        admin_bar.addWidget(self._btn_delete)
        self._admin_widget = QWidget()
        self._admin_widget.setLayout(admin_bar)
        layout.addWidget(self._admin_widget)

        student_bar = QHBoxLayout()
        self._btn_request = QPushButton("Оформить заявку на выбранный материал")
        self._btn_request.setObjectName("primaryBtn")
        self._btn_request.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_request.clicked.connect(self._create_request)
        student_bar.addWidget(self._btn_request)
        self._student_widget = QWidget()
        self._student_widget.setLayout(student_bar)
        layout.addWidget(self._student_widget)

        self._table = QTableWidget(0, 11)
        self._table.setHorizontalHeaderLabels(
            [
                "Код",
                "Название",
                "Предмет",
                "Тип",
                "Автор",
                "Поставщик",
                "Формат",
                "Страниц",
                "Доступно",
                "Стоимость",
                "Скидка %",
            ]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

        self._wire_controls()
        self.set_mode(mode)

    def _wire_controls(self) -> None:
        self._search.textChanged.connect(lambda _text: self.reload())
        self._subject_filter.currentIndexChanged.connect(lambda _index: self.reload())
        self._type_filter.currentIndexChanged.connect(lambda _index: self.reload())
        self._provider_filter.currentIndexChanged.connect(lambda _index: self.reload())
        self._price_max.valueChanged.connect(lambda _value: self.reload())
        self._sort.currentIndexChanged.connect(lambda _index: self.reload())

    def set_mode(self, mode: Mode) -> None:
        self._mode = mode
        self._controls_widget.setVisible(mode != "guest")
        self._admin_widget.setVisible(mode == "admin")
        self._student_widget.setVisible(mode == "student")
        titles = {
            "guest": "Каталог учебных материалов (гость)",
            "student": "Каталог учебных материалов - студент",
            "teacher": "Каталог учебных материалов - преподаватель",
            "admin": "Каталог учебных материалов - администратор",
        }
        self._title.setText(titles[mode])
        self._fill_filters()
        self.reload()

    def _fill_filters(self) -> None:
        materials = self._db.list_materials()

        def fill(box: QComboBox, values: list[str], all_label: str) -> None:
            box.blockSignals(True)
            box.clear()
            box.addItem(all_label, None)
            for value in sorted(set(values)):
                box.addItem(value, value)
            box.blockSignals(False)

        fill(self._subject_filter, [m.subject for m in materials], "Все предметы")
        fill(self._type_filter, [m.material_type for m in materials], "Все типы")
        fill(self._provider_filter, [m.provider for m in materials], "Все поставщики")

    def reload(self) -> None:
        apply_table_header_style(self._table)
        self._all = self._db.list_materials()
        rows = self._filtered_sorted()
        self._table.setRowCount(0)
        for material in rows:
            row = self._table.rowCount()
            self._table.insertRow(row)
            values = [
                material.code,
                material.title,
                material.subject,
                material.material_type,
                material.author,
                material.provider,
                material.format_name,
                str(material.pages),
                str(material.available_count),
                f"{material.final_price:.2f} ₽",
                f"{material.discount_percent:g}",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 1:
                    item.setData(Qt.ItemDataRole.UserRole, material.id)
                self._table.setItem(row, col, item)
            self._style_row(row, material)

    def _filtered_sorted(self) -> list[MaterialRecord]:
        if self._mode == "guest":
            return list(self._all)

        items = list(self._all)
        subject = self._subject_filter.currentData()
        material_type = self._type_filter.currentData()
        provider = self._provider_filter.currentData()
        max_price = float(self._price_max.value())
        query = self._search.text().strip().lower()

        if subject:
            items = [m for m in items if m.subject == subject]
        if material_type:
            items = [m for m in items if m.material_type == material_type]
        if provider:
            items = [m for m in items if m.provider == provider]
        if max_price > 0:
            items = [m for m in items if m.final_price <= max_price]
        if query:
            items = [m for m in items if query in self._text_blob(m)]

        sort_key = self._sort.currentData()
        if sort_key == "price_asc":
            items.sort(key=lambda m: (m.final_price, m.title.lower()))
        elif sort_key == "price_desc":
            items.sort(key=lambda m: (-m.final_price, m.title.lower()))
        elif sort_key == "title_asc":
            items.sort(key=lambda m: m.title.lower())
        elif sort_key == "available_asc":
            items.sort(key=lambda m: (m.available_count, m.title.lower()))
        elif sort_key == "available_desc":
            items.sort(key=lambda m: (-m.available_count, m.title.lower()))
        return items

    def _text_blob(self, material: MaterialRecord) -> str:
        return " ".join(
            [
                material.code,
                material.title,
                material.subject,
                material.material_type,
                material.author,
                material.provider,
                material.description,
                material.format_name,
            ]
        ).lower()

    def _style_row(self, row: int, material: MaterialRecord) -> None:
        palette = current_palette()
        color: Optional[QColor] = None
        if material.available_count == 0:
            color = palette.no_access
        elif material.discount_percent > 15:
            color = palette.discount_row
        if color is None:
            return
        for col in range(self._table.columnCount()):
            item = self._table.item(row, col)
            if item is not None:
                item.setBackground(color)

    def _selected_material_id(self) -> Optional[int]:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 1)
        if item is None:
            return None
        value = item.data(Qt.ItemDataRole.UserRole)
        return int(value) if value is not None else None

    def _on_double_click(self) -> None:
        if self._mode != "admin":
            return
        material_id = self._selected_material_id()
        if material_id is not None:
            self._open_editor(material_id)

    def _delete_selected(self) -> None:
        material_id = self._selected_material_id()
        if material_id is None:
            show_message(self, "Удаление", "Выберите материал в таблице.", QMessageBox.Icon.Warning)
            return
        answer = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить выбранный учебный материал?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        ok, reason = self._db.delete_material(material_id)
        if not ok:
            show_message(self, "Удаление невозможно", reason, QMessageBox.Icon.Warning)
        self._fill_filters()
        self.reload()

    def _create_request(self) -> None:
        if self._user is None:
            return
        material_id = self._selected_material_id()
        if material_id is None:
            show_message(self, "Заявка", "Выберите материал в таблице.", QMessageBox.Icon.Warning)
            return
        quantity, ok = QInputDialog.getInt(self, "Заявка", "Количество экземпляров:", 1, 1, 100)
        if not ok:
            return
        self._db.create_request(self._user.id, material_id, quantity)
        show_message(self, "Готово", "Заявка создана.", QMessageBox.Icon.Information)
