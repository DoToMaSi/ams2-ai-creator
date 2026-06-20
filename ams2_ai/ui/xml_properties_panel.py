"""Document-level XML metadata editor."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import load_vehicle_classes
from ams2_ai.models.document import AIDocument


class XmlPropertiesPanel(QGroupBox):
    propertiesChanged = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__("XML Properties", parent)
        self._document: AIDocument | None = None
        self._loading = False

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Set name shown in the file list")
        self.name_edit.textChanged.connect(self._on_changed)
        form.addRow("Name:", self.name_edit)

        self.class_combo = QComboBox()
        self.class_combo.setEditable(True)
        self.class_combo.addItems(load_vehicle_classes())
        line_edit = self.class_combo.lineEdit()
        if line_edit is not None:
            line_edit.textChanged.connect(self._on_changed)
        form.addRow("Class:", self.class_combo)

        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("Optional modded class filename, e.g. MyMod_GT3.xml")
        self.custom_name_edit.textChanged.connect(self._on_changed)
        form.addRow("Custom Name:", self.custom_name_edit)

        layout = QVBoxLayout(self)
        layout.addLayout(form)

    def set_document(self, document: AIDocument | None) -> None:
        self._loading = True
        self._document = document
        enabled = document is not None
        self.setEnabled(enabled)
        if not document:
            self.name_edit.clear()
            self.class_combo.setCurrentText("")
            self.custom_name_edit.clear()
            self._loading = False
            return

        self.name_edit.setText(document.set_name)
        self.class_combo.setCurrentText(document.vehicle_class)
        self.custom_name_edit.setText(document.custom_class_name)
        self._loading = False

    def _on_changed(self) -> None:
        if self._loading or not self._document:
            return
        self._document.set_name = self.name_edit.text().strip()
        self._document.vehicle_class = self.class_combo.currentText().strip()
        self._document.custom_class_name = self.custom_name_edit.text().strip()
        self._document.sync_header_comment()
        self.propertiesChanged.emit()
