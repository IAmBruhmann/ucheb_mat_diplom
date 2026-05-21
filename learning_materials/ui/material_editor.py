"""Dialog for adding and editing educational materials."""

from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from learning_materials.database import Database
from learning_materials.ui.messages import show_message


class MaterialEditorDialog(QDialog):
    _open_flag = False

    @classmethod
    def try_open(
        cls,
        parent: QWidget,
        db: Database,
        material_id: Optional[int],
    ) -> bool:
        if cls._open_flag:
            show_message(
                parent,
                "Редактирование",
                "Уже открыта форма материала. Завершите её перед открытием новой.",
                QMessageBox.Icon.Information,
            )
            return False
        cls._open_flag = True
        dlg = cls(parent, db, material_id)
        dlg.exec()
        cls._open_flag = False
        return dlg.result() == QDialog.DialogCode.Accepted

    def __init__(self, parent: QWidget, db: Database, material_id: Optional[int]) -> None:
        super().__init__(parent)
        self._db = db
        self._material_id = material_id
        is_add = material_id is None
        self.setWindowTitle(
            "Добавление учебного материала" if is_add else "Редактирование учебного материала"
        )

        root = QVBoxLayout(self)
        form = QFormLayout()

        self._code = QLineEdit()
        self._title = QLineEdit()
        self._subject = QComboBox()
        self._type = QComboBox()
        self._author = QComboBox()
        self._provider = QComboBox()
        self._description = QTextEdit()
        self._description.setFixedHeight(90)
        self._format = QLineEdit()
        self._pages = QSpinBox()
        self._pages.setMaximum(100_000)
        self._available = QSpinBox()
        self._available.setMaximum(100_000)
        self._price = QDoubleSpinBox()
        self._price.setMaximum(9_999_999)
        self._price.setDecimals(2)
        self._discount = QDoubleSpinBox()
        self._discount.setMaximum(100)
        self._discount.setDecimals(2)

        form.addRow("Код", self._code)
        form.addRow("Название", self._title)
        form.addRow("Предмет", self._subject)
        form.addRow("Тип материала", self._type)
        form.addRow("Автор", self._author)
        form.addRow("Поставщик", self._provider)
        form.addRow("Описание", self._description)
        form.addRow("Формат", self._format)
        form.addRow("Страниц", self._pages)
        form.addRow("Доступно, шт.", self._available)
        form.addRow("Стоимость, ₽", self._price)
        form.addRow("Скидка, %", self._discount)
        root.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

        self._fill_refs()
        if is_add:
            self._code.setText(db.next_material_code())
            self._format.setText("PDF")
        else:
            self._load(material_id)

    def _fill_refs(self) -> None:
        for box, table in (
            (self._subject, "subjects"),
            (self._type, "material_types"),
            (self._author, "authors"),
            (self._provider, "providers"),
        ):
            box.clear()
            for item_id, name in self._db.list_reference(table):
                box.addItem(name, item_id)

    def _select_combo(self, box: QComboBox, text: str) -> None:
        for i in range(box.count()):
            if box.itemText(i) == text:
                box.setCurrentIndex(i)
                return

    def _load(self, material_id: int) -> None:
        material = self._db.get_material(material_id)
        if material is None:
            return
        self._code.setText(material.code)
        self._title.setText(material.title)
        self._select_combo(self._subject, material.subject)
        self._select_combo(self._type, material.material_type)
        self._select_combo(self._author, material.author)
        self._select_combo(self._provider, material.provider)
        self._description.setPlainText(material.description)
        self._format.setText(material.format_name)
        self._pages.setValue(material.pages)
        self._available.setValue(material.available_count)
        self._price.setValue(material.price)
        self._discount.setValue(material.discount_percent)

    def _save(self) -> None:
        title = self._title.text().strip()
        code = self._code.text().strip()
        if not code or not title:
            show_message(
                self,
                "Ошибка ввода",
                "Заполните код и название учебного материала.",
                QMessageBox.Icon.Warning,
            )
            return

        args = (
            code,
            title,
            self._description.toPlainText().strip(),
            self._format.text().strip() or "PDF",
            int(self._pages.value()),
            int(self._available.value()),
            float(self._price.value()),
            float(self._discount.value()),
            int(self._subject.currentData()),
            int(self._type.currentData()),
            int(self._author.currentData()),
            int(self._provider.currentData()),
        )
        try:
            if self._material_id is None:
                self._db.insert_material(*args)
            else:
                self._db.update_material(self._material_id, *args)
        except Exception as exc:  # noqa: BLE001
            show_message(self, "Ошибка сохранения", str(exc), QMessageBox.Icon.Critical)
            return
        self.accept()
