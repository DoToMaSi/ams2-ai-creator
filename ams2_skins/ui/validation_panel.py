"""Validation messages panel."""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from ams2_shared.ui.theme import SPACING_INNER, SPACING_SECTION


class ValidationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACING_SECTION, SPACING_INNER, SPACING_SECTION, SPACING_INNER)
        layout.setSpacing(SPACING_INNER)

        title = QLabel("Validation")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

    def set_messages(self, messages: list[str]) -> None:
        self.list_widget.clear()
        for message in messages:
            self.list_widget.addItem(message)
