"""Livery slot list and editor host."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ams2_shared.ui.theme import SPACING_INNER, SPACING_SECTION
from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.livery_slot import LiverySlot
from ams2_skins.ui.livery_slot_editor import LiverySlotEditor


class LiveryPanel(QWidget):
    slotsChanged = Signal()
    addSlotRequested = Signal()
    setMaxLiveryRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._car: CarOverrideDocument | None = None
        self._catalog_entry: VehicleCatalogEntry | None = None
        self._active_slot_id: str | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QHBoxLayout()
        header.setContentsMargins(SPACING_SECTION, SPACING_SECTION, SPACING_SECTION, SPACING_INNER)
        self.car_title = QLabel("Select a car")
        self.car_title.setObjectName("sectionTitle")
        header.addWidget(self.car_title)
        header.addStretch()
        self.max_label = QLabel("")
        header.addWidget(self.max_label)
        max_btn = QPushButton("Set Max ID…")
        max_btn.clicked.connect(self.setMaxLiveryRequested.emit)
        header.addWidget(max_btn)
        add_btn = QPushButton("+ Livery Slot")
        add_btn.clicked.connect(self.addSlotRequested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(SPACING_SECTION, 0, SPACING_INNER, SPACING_SECTION)
        self.slot_list = QListWidget()
        self.slot_list.currentItemChanged.connect(self._on_slot_selected)
        left_layout.addWidget(self.slot_list)
        splitter.addWidget(left)

        self.editor = LiverySlotEditor()
        self.editor.slotChanged.connect(self._on_editor_changed)
        self.editor.removeRequested.connect(self._remove_active_slot)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([260, 900])
        layout.addWidget(splitter, stretch=1)

    def set_car(
        self,
        car: CarOverrideDocument | None,
        catalog_entry: VehicleCatalogEntry | None,
    ) -> None:
        self._flush_editor()
        self._car = car
        self._catalog_entry = catalog_entry
        self.editor.set_catalog_entry(catalog_entry)

        if car is None:
            self.car_title.setText("Select a car")
            self.max_label.setText("")
            self.slot_list.clear()
            return

        self.car_title.setText(car.car_id)
        if catalog_entry and catalog_entry.has_livery_limit:
            self.max_label.setText(f"IDs 51–{catalog_entry.max_livery_id}")
        elif catalog_entry:
            self.max_label.setText("Max livery ID unknown")
        else:
            self.max_label.setText("")

        self._refresh_slot_list(car, self._active_slot_id)

    def active_slot(self) -> LiverySlot | None:
        self._flush_editor()
        if self._car is None or self._active_slot_id is None:
            return None
        return self._car.get_slot(self._active_slot_id)

    def _refresh_slot_list(self, car: CarOverrideDocument, active_slot_id: str | None) -> None:
        self.slot_list.blockSignals(True)
        self.slot_list.clear()
        selected_row = 0
        slots = car.slots()
        for index, slot in enumerate(slots):
            item = QListWidgetItem(slot.display_title)
            item.setData(256, slot.slot_id)
            self.slot_list.addItem(item)
            if slot.slot_id == active_slot_id:
                selected_row = index
        if self.slot_list.count():
            self.slot_list.setCurrentRow(selected_row if active_slot_id else 0)
            item = self.slot_list.currentItem()
            if item:
                self._active_slot_id = item.data(256)
                slot = car.get_slot(self._active_slot_id)
                if slot:
                    self.editor.set_slot(slot)
        else:
            self._active_slot_id = None
        self.slot_list.blockSignals(False)

    def _on_slot_selected(self, current: QListWidgetItem | None, _previous) -> None:
        if self._car is None:
            return
        self._flush_editor()
        if current is None:
            return
        slot_id = current.data(256)
        self._active_slot_id = slot_id
        slot = self._car.get_slot(slot_id)
        if slot:
            self.editor.set_slot(slot)

    def _on_editor_changed(self) -> None:
        self._flush_editor()
        self.slotsChanged.emit()

    def _flush_editor(self) -> None:
        if self._car is None or self._active_slot_id is None:
            return
        collected = self.editor.collect_slot()
        if collected is None:
            return
        slots = self._car.slots()
        for index, slot in enumerate(slots):
            if slot.slot_id == self._active_slot_id:
                slots[index] = collected
                break
        self._car.replace_slots(slots)
        item = self.slot_list.currentItem()
        if item:
            item.setText(collected.display_title)

    def _remove_active_slot(self) -> None:
        if self._car is None or self._active_slot_id is None:
            return
        slot_id = self._active_slot_id
        self._car.remove_slot(slot_id)
        self._active_slot_id = None
        self._refresh_slot_list(self._car, None)
        self.slotsChanged.emit()

    def refresh_after_external_change(self) -> None:
        if self._car:
            self._refresh_slot_list(self._car, self._active_slot_id)
