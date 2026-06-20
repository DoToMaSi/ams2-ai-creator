"""Document-level XML metadata editor."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QLineEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import load_vehicle_classes
from ams2_ai.models.document import AIDocument
from ams2_ai.ui.collapsible_section import CollapsibleBlock
from ams2_ai.ui.theme import SPACING_INNER, SPACING_SECTION


class XmlPropertiesPanel(QWidget):
    propertiesChanged = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._document: AIDocument | None = None
        self._loading = False
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        form_host = QFrame()
        form_host.setObjectName("collapsibleContent")
        form = QFormLayout(form_host)
        form.setContentsMargins(SPACING_SECTION, SPACING_INNER, SPACING_SECTION, SPACING_SECTION)
        form.setHorizontalSpacing(SPACING_SECTION)
        form.setVerticalSpacing(SPACING_INNER)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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
        self.custom_name_edit.setPlaceholderText(
            "Optional modded class filename, e.g. MyMod_GT3.xml"
        )
        self.custom_name_edit.textChanged.connect(self._on_changed)
        form.addRow("Custom Name:", self.custom_name_edit)

        self._block = CollapsibleBlock("XML Properties", form_host, expanded=False)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._block)

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
