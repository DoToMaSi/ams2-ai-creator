"""Skin Manager dialogs."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
)

from ams2_shared.ui.theme import MARGINS_DIALOG, SPACING_INNER
from ams2_skins.catalog.entry import VehicleCatalogEntry


def warn_validation_errors(parent, errors: list[str]) -> None:
    text = "\n".join(f"• {error}" for error in errors)
    QMessageBox.warning(parent, "Validation Errors", text)


def confirm_unsaved(parent, label: str) -> bool:
    result = QMessageBox.question(
        parent,
        "Unsaved Changes",
        f"{label} has unsaved changes. Continue anyway?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return result == QMessageBox.StandardButton.Yes


def confirm_export_with_warnings(parent, warnings: list[str]) -> bool:
    text = "Some validation warnings were found:\n\n" + "\n".join(f"• {w}" for w in warnings)
    text += "\n\nExport anyway?"
    result = QMessageBox.question(
        parent,
        "Export Warnings",
        text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return result == QMessageBox.StandardButton.Yes


class PickCarDialog(QDialog):
    def __init__(
        self,
        entries: list[VehicleCatalogEntry],
        *,
        exclude: set[str] | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Add Car to Skinpack")
        self.resize(420, 480)
        self._selected: VehicleCatalogEntry | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(*MARGINS_DIALOG)
        layout.setSpacing(SPACING_INNER)
        layout.addWidget(QLabel("Select a vehicle from your AMS2 install:"))

        self.list_widget = QListWidget()
        exclude = exclude or set()
        for entry in entries:
            if entry.folder_id in exclude:
                continue
            label = entry.display_name
            if entry.has_livery_limit:
                label += f" (IDs 51–{entry.max_livery_id})"
            else:
                label += " (max livery ID unknown)"
            item = QListWidgetItem(label)
            item.setData(256, entry)
            self.list_widget.addItem(item)
        self.list_widget.itemDoubleClicked.connect(self._accept_selection)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._accept_selection)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _accept_selection(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        self._selected = item.data(256)
        self.accept()

    def selected_entry(self) -> VehicleCatalogEntry | None:
        return self._selected


class PickLiverySlotDialog(QDialog):
    def __init__(
        self,
        *,
        min_id: int,
        max_id: int | None,
        used_ids: set[int],
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Add Livery Slot")
        layout = QFormLayout(self)
        layout.setContentsMargins(*MARGINS_DIALOG)

        self.id_spin = QSpinBox()
        self.id_spin.setMinimum(min_id)
        self.id_spin.setMaximum(max_id or min_id + 100)
        for livery_id in range(self.id_spin.minimum(), self.id_spin.maximum() + 1):
            if livery_id not in used_ids:
                self.id_spin.setValue(livery_id)
                break
        layout.addRow("Livery ID:", self.id_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def livery_id(self) -> int:
        return self.id_spin.value()


class CustomMaxLiveryDialog(QDialog):
    def __init__(self, car_id: str, current: int | None = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Set Max Livery ID — {car_id}")
        layout = QFormLayout(self)
        layout.setContentsMargins(*MARGINS_DIALOG)

        self.max_spin = QSpinBox()
        self.max_spin.setMinimum(51)
        self.max_spin.setMaximum(999)
        self.max_spin.setValue(current or 73)
        layout.addRow("Max livery ID:", self.max_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def max_livery_id(self) -> int:
        return self.max_spin.value()
