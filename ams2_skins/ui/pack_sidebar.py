"""Skinpack car list sidebar."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ams2_shared.ui.theme import SPACING_INNER, SPACING_SECTION
from ams2_skins.models.car_document import CarOverrideDocument


class PackSidebar(QWidget):
    carSelected = Signal(str)
    addCarRequested = Signal()
    removeCarRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        margins = SPACING_SECTION
        layout.setContentsMargins(margins, margins, margins, margins)
        layout.setSpacing(SPACING_INNER)

        header = QHBoxLayout()
        title = QLabel("Cars in Pack")
        title.setObjectName("sectionTitle")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("+ Car")
        add_btn.clicked.connect(self.addCarRequested.emit)
        header.addWidget(add_btn)
        layout.addLayout(header)

        self.pack_label = QLabel("No skinpack open")
        self.pack_label.setWordWrap(True)
        layout.addWidget(self.pack_label)

        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.list_widget, stretch=1)

        self.remove_btn = QPushButton("Remove Car")
        self.remove_btn.clicked.connect(self._remove_current)
        layout.addWidget(self.remove_btn)

    def set_pack_name(self, name: str) -> None:
        self.pack_label.setText(name)

    def set_cars(self, cars: list[CarOverrideDocument], *, active_car_id: str | None) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        selected_row = 0
        for index, car in enumerate(cars):
            slots = len(car.slots())
            item = QListWidgetItem(f"{car.car_id} ({slots} liveries)")
            item.setData(256, car.car_id)
            self.list_widget.addItem(item)
            if car.car_id == active_car_id:
                selected_row = index
        if self.list_widget.count():
            self.list_widget.setCurrentRow(selected_row)
        self.list_widget.blockSignals(False)
        self.remove_btn.setEnabled(bool(cars))

    def _on_selection_changed(self, current: QListWidgetItem | None, _previous) -> None:
        if current is None:
            return
        car_id = current.data(256)
        if car_id:
            self.carSelected.emit(car_id)

    def _remove_current(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        car_id = item.data(256)
        if car_id:
            self.removeCarRequested.emit(car_id)
