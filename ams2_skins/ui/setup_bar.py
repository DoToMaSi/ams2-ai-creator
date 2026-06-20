"""AMS2 path and catalog controls."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget

from ams2_shared.ui.theme import SPACING_INNER, SPACING_SECTION


class SetupBar(QWidget):
    ams2BrowseRequested = Signal()
    rescanRequested = Signal()
    openPackRequested = Signal()
    newPackRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_INNER)

        layout.addWidget(QLabel("AMS2 install:"))
        self.ams2_path_edit = QLineEdit()
        self.ams2_path_edit.setReadOnly(True)
        self.ams2_path_edit.setPlaceholderText("Select your Automobilista 2 folder…")
        layout.addWidget(self.ams2_path_edit, stretch=1)

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self.ams2BrowseRequested.emit)
        layout.addWidget(browse_btn)

        rescan_btn = QPushButton("Rescan")
        rescan_btn.clicked.connect(self.rescanRequested.emit)
        layout.addWidget(rescan_btn)

        layout.addSpacing(SPACING_SECTION)

        open_btn = QPushButton("Open Skinpack")
        open_btn.clicked.connect(self.openPackRequested.emit)
        layout.addWidget(open_btn)

        new_btn = QPushButton("New Skinpack")
        new_btn.clicked.connect(self.newPackRequested.emit)
        layout.addWidget(new_btn)

    def set_ams2_path(self, path: str) -> None:
        self.ams2_path_edit.setText(path)
