"""Shared dialogs."""

from __future__ import annotations

import subprocess
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import (
    group_tracks_by_venue,
    load_vehicle_classes,
    track_display_label,
    track_search_blob,
)
from ams2_ai.logging_config import get_log_dir, get_log_file_path
from ams2_ai.util.filenames import xml_filename_from_label


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
        self.set_name_edit.textChanged.connect(self._on_name_changed)
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
        self.custom_file_edit.setPlaceholderText("Defaults from Name; edit if needed")
        self.custom_file_edit.textEdited.connect(self._on_custom_filename_edited)
        custom_row_layout.addRow("Custom filename:", self.custom_file_edit)
        layout.addRow(self.custom_file_row)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self._custom_filename_edited = False
        self._on_class_changed(self.class_combo.currentText())

    def _on_custom_filename_edited(self, _text: str) -> None:
        self._custom_filename_edited = True

    def _on_name_changed(self, _text: str) -> None:
        if self.is_custom_class() and not self._custom_filename_edited:
            self._sync_custom_filename_from_name()

    def _sync_custom_filename_from_name(self) -> None:
        suggested = xml_filename_from_label(self.set_name_edit.text())
        self.custom_file_edit.blockSignals(True)
        self.custom_file_edit.setText(suggested)
        self.custom_file_edit.blockSignals(False)

    def _on_class_changed(self, text: str) -> None:
        is_custom = text == CUSTOM_CLASS_OPTION
        self.custom_file_row.setVisible(is_custom)
        if is_custom:
            self._custom_filename_edited = False
            self._sync_custom_filename_from_name()

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


class SingleTrackPickerDialog(QDialog):
    def __init__(
        self,
        tracks: list[str],
        existing: set[str] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Add Track Override")
        self.resize(520, 560)
        self._selected = ""
        existing = existing or set()
        available = [track for track in tracks if track not in existing]

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a track for per-track AI overrides:"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search track name, layout, or code…")
        self.search_edit.textChanged.connect(self._apply_filter)
        layout.addWidget(self.search_edit)

        self.track_tree = QTreeWidget()
        self.track_tree.setHeaderHidden(True)
        self.track_tree.setRootIsDecorated(True)
        self._populate_tree(available)
        self.track_tree.itemDoubleClicked.connect(self._on_item_activated)
        layout.addWidget(self.track_tree)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept_current)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_tree(self, tracks: list[str]) -> None:
        self.track_tree.clear()
        grouped = group_tracks_by_venue(tracks)
        for venue, codes in grouped.items():
            venue_item = QTreeWidgetItem([venue])
            venue_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            font = QFont(venue_item.font(0))
            font.setBold(True)
            venue_item.setFont(0, font)
            for code in codes:
                child = QTreeWidgetItem([track_display_label(code)])
                child.setData(0, Qt.ItemDataRole.UserRole, code)
                child.setToolTip(0, code)
                venue_item.addChild(child)
            self.track_tree.addTopLevelItem(venue_item)
            venue_item.setExpanded(True)

    def _apply_filter(self, text: str) -> None:
        query = text.strip().casefold()
        for index in range(self.track_tree.topLevelItemCount()):
            venue_item = self.track_tree.topLevelItem(index)
            if venue_item is None:
                continue
            any_visible = False
            for child_index in range(venue_item.childCount()):
                child = venue_item.child(child_index)
                code = child.data(0, Qt.ItemDataRole.UserRole)
                visible = not query or query in track_search_blob(str(code))
                child.setHidden(not visible)
                if visible:
                    any_visible = True
            venue_item.setHidden(not any_visible)

    def _on_item_activated(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.data(0, Qt.ItemDataRole.UserRole):
            self.track_tree.setCurrentItem(item)
            self._accept_current()

    def _accept_current(self) -> None:
        item = self.track_tree.currentItem()
        if item is None:
            QMessageBox.warning(self, "Add Track", "Select a track layout from the list.")
            return
        code = item.data(0, Qt.ItemDataRole.UserRole)
        if not code:
            QMessageBox.warning(self, "Add Track", "Select a track layout, not the venue group.")
            return
        self._selected = str(code)
        self.accept()

    def selected_track(self) -> str:
        return self._selected


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
