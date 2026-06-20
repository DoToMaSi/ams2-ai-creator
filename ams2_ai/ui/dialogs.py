"""Shared dialogs."""

from __future__ import annotations

import subprocess
import sys

from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import load_vehicle_classes
from ams2_ai.logging_config import get_log_dir, get_log_file_path


class ErrorDialog(QDialog):
    def __init__(self, summary: str, traceback_text: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Unexpected Error")
        self.resize(560, 360)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("An unexpected error occurred:"))
        layout.addWidget(QLabel(summary))

        self.traceback_edit = QTextEdit()
        self.traceback_edit.setReadOnly(True)
        self.traceback_edit.setPlainText(traceback_text)
        layout.addWidget(self.traceback_edit)

        button_row = QHBoxLayout()
        copy_log_btn = QPushButton("Copy Log Path")
        copy_log_btn.clicked.connect(self._copy_log_path)
        button_row.addWidget(copy_log_btn)
        button_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

    def _copy_log_path(self) -> None:
        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(str(get_log_file_path()))


CUSTOM_CLASS_OPTION = "Custom…"


class NewFileDialog(QDialog):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("New AI File")
        self.resize(460, 200)

        layout = QFormLayout(self)

        self.set_name_edit = QLineEdit()
        self.set_name_edit.setPlaceholderText('e.g. "F1 2005" — shown in the file list')
        layout.addRow("Name:", self.set_name_edit)

        self.class_combo = QComboBox()
        self.class_combo.addItem(CUSTOM_CLASS_OPTION)
        self.class_combo.addItems(load_vehicle_classes())
        self.class_combo.currentTextChanged.connect(self._on_class_changed)
        layout.addRow("Vehicle class file:", self.class_combo)

        self.custom_file_row = QWidget()
        custom_row_layout = QFormLayout(self.custom_file_row)
        custom_row_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_file_edit = QLineEdit()
        self.custom_file_edit.setPlaceholderText("Modded class filename, e.g. MyMod_GT3.xml")
        custom_row_layout.addRow("Custom filename:", self.custom_file_edit)
        layout.addRow(self.custom_file_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self._on_class_changed(self.class_combo.currentText())

    def _on_class_changed(self, text: str) -> None:
        self.custom_file_row.setVisible(text == CUSTOM_CLASS_OPTION)

    def _validate_and_accept(self) -> None:
        if self.is_custom_class() and not self.custom_file_edit.text().strip():
            QMessageBox.warning(self, "New AI File", "Enter a custom XML filename.")
            return
        if not self.selected_filename():
            QMessageBox.warning(self, "New AI File", "Select or enter a vehicle class filename.")
            return
        self.accept()

    def is_custom_class(self) -> bool:
        return self.class_combo.currentText() == CUSTOM_CLASS_OPTION

    def set_name(self) -> str:
        return self.set_name_edit.text().strip()

    def selected_filename(self) -> str:
        if self.is_custom_class():
            text = self.custom_file_edit.text().strip()
        else:
            text = self.class_combo.currentText().strip()
        if not text or text == CUSTOM_CLASS_OPTION:
            return ""
        if not text.endswith(".xml"):
            text = f"{text}.xml"
        return text


class TrackPickerDialog(QDialog):
    def __init__(self, tracks: list[str], selected: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Select Tracks")
        self.resize(480, 420)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Enter comma-separated track IDs (case-sensitive):"))

        from PySide6.QtWidgets import QListWidget, QListWidgetItem

        self.track_list = QListWidget()
        self.track_list.setSelectionMode(QListWidget.MultiSelection)
        selected_set = {t.strip() for t in selected.split(",") if t.strip()}
        for track in tracks:
            item = QListWidgetItem(track)
            self.track_list.addItem(item)
            if track in selected_set:
                item.setSelected(True)
        layout.addWidget(self.track_list)

        self.manual_edit = QLineEdit(selected)
        layout.addWidget(QLabel("Selected tracks:"))
        layout.addWidget(self.manual_edit)

        def sync_from_list() -> None:
            names = [item.text() for item in self.track_list.selectedItems()]
            self.manual_edit.setText(",".join(names))

        self.track_list.itemSelectionChanged.connect(sync_from_list)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def selected_tracks(self) -> str:
        return self.manual_edit.text().strip()


def confirm_unsaved(parent: QWidget, filename: str) -> QMessageBox.StandardButton:
    return QMessageBox.question(
        parent,
        "Unsaved Changes",
        f"'{filename}' has unsaved changes. Save before continuing?",
        QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        QMessageBox.Save,
    )


def warn_validation_errors(parent: QWidget, errors: list[str]) -> None:
    QMessageBox.warning(parent, "Validation Errors", "\n".join(errors))


def open_log_folder(parent: QWidget | None = None) -> None:
    log_dir = get_log_dir()
    url = log_dir.as_uri()
    if sys.platform == "win32":
        subprocess.run(["explorer", str(log_dir)], check=False)
    else:
        QDesktopServices.openUrl(url)
