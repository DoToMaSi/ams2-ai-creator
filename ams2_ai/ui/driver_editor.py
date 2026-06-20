"""Driver parameter editor panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import load_countries, load_tracks
from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import PARAMETER_GROUPS, PARAMETERS, ParameterDef
from ams2_ai.smart.derivation import INDEPENDENT_KEYS, apply_smart_derivation
from ams2_ai.smart.presets import PRESET_NAMES, apply_preset
from ams2_ai.ui.dialogs import TrackPickerDialog
from ams2_ai.ui.parameter_row import ParameterRow


class DriverEditor(QWidget):
    driverChanged = Signal()

    SMART_PRIMARY = {"race_skill", "aggression"}

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._driver: DriverEntry | None = None
        self._loading = False
        self._rows: dict[str, ParameterRow] = {}

        root = QVBoxLayout(self)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.smart_radio = QRadioButton("Smart")
        self.custom_radio = QRadioButton("Custom")
        self.smart_radio.setChecked(True)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.smart_radio)
        self.mode_group.addButton(self.custom_radio)
        mode_row.addWidget(self.smart_radio)
        mode_row.addWidget(self.custom_radio)
        mode_row.addStretch()
        root.addLayout(mode_row)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Presets:"))
        self.preset_buttons: dict[str, QPushButton] = {}
        for name in PRESET_NAMES:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _checked=False, n=name: self._apply_preset(n))
            self.preset_buttons[name] = btn
            preset_row.addWidget(btn)
        preset_row.addStretch()
        root.addLayout(preset_row)

        identity_box = QGroupBox("Identity")
        identity_form = QFormLayout(identity_box)
        self.livery_edit = QLineEdit()
        self.livery_edit.textChanged.connect(self._on_identity_changed)
        identity_form.addRow("Livery Name:", self.livery_edit)

        tracks_row = QHBoxLayout()
        self.tracks_edit = QLineEdit()
        self.tracks_edit.setPlaceholderText("Optional — comma-separated track IDs for overrides")
        self.tracks_edit.textChanged.connect(self._on_identity_changed)
        tracks_row.addWidget(self.tracks_edit)
        pick_tracks_btn = QPushButton("Pick…")
        pick_tracks_btn.clicked.connect(self._pick_tracks)
        tracks_row.addWidget(pick_tracks_btn)
        identity_form.addRow("Tracks:", tracks_row)

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_identity_changed)
        identity_form.addRow("Driver Name:", self.name_edit)

        self.country_combo = QComboBox()
        self.country_combo.setEditable(True)
        self.country_combo.addItems(load_countries())
        self.country_combo.currentTextChanged.connect(self._on_identity_changed)
        identity_form.addRow("Country:", self.country_combo)
        root.addWidget(identity_box)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        grouped: dict[str, list[ParameterDef]] = {g: [] for g in PARAMETER_GROUPS}
        for param in PARAMETERS:
            grouped[param.group].append(param)

        for group_name in PARAMETER_GROUPS:
            box = QGroupBox(group_name)
            box_layout = QVBoxLayout(box)
            for param in grouped[group_name]:
                row = ParameterRow(param)
                row.valueChanged.connect(self._on_parameter_changed)
                self._rows[param.key] = row
                box_layout.addWidget(row)
            scroll_layout.addWidget(box)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        root.addWidget(scroll, stretch=1)

        self.smart_radio.toggled.connect(self._on_mode_changed)
        self.custom_radio.toggled.connect(self._on_mode_changed)

    def set_driver(self, driver: DriverEntry | None) -> None:
        self._loading = True
        self._driver = driver
        enabled = driver is not None
        self.setEnabled(enabled)
        if not driver:
            self._loading = False
            return

        self.livery_edit.setText(driver.livery_name)
        self.tracks_edit.setText(driver.tracks)
        self.name_edit.setText(driver.name)
        self.country_combo.setCurrentText(driver.country)

        if driver.mode == "smart":
            self.smart_radio.setChecked(True)
        else:
            self.custom_radio.setChecked(True)

        for key, row in self._rows.items():
            row.set_value(driver.get_ui_value(key))

        self._update_field_locks()
        self._loading = False

    def _update_field_locks(self) -> None:
        smart = self.smart_radio.isChecked()
        for key, row in self._rows.items():
            if not smart:
                editable = True
            else:
                editable = key in self.SMART_PRIMARY or key in INDEPENDENT_KEYS
            row.set_enabled_editable(editable)

    def _on_mode_changed(self) -> None:
        if self._loading or not self._driver:
            return
        self._driver.mode = "smart" if self.smart_radio.isChecked() else "custom"
        if self._driver.mode == "smart":
            apply_smart_derivation(self._driver, preserve_independent=True)
            self._loading = True
            for key, row in self._rows.items():
                if key not in self.SMART_PRIMARY and key not in INDEPENDENT_KEYS:
                    row.set_value(self._driver.get_ui_value(key))
            self._loading = False
        self._update_field_locks()
        self.driverChanged.emit()

    def _on_identity_changed(self) -> None:
        if self._loading or not self._driver:
            return
        self._driver.livery_name = self.livery_edit.text()
        self._driver.tracks = self.tracks_edit.text()
        self._driver.is_track_override = bool(self._driver.tracks.strip())
        self._driver.name = self.name_edit.text()
        self._driver.country = self.country_combo.currentText().strip().upper()
        if self._driver.name:
            self._driver.set_fields.add("name")
        else:
            self._driver.set_fields.discard("name")
        if self._driver.country:
            self._driver.set_fields.add("country")
        else:
            self._driver.set_fields.discard("country")
        self.driverChanged.emit()

    def _on_parameter_changed(self, key: str, ui_value: int) -> None:
        if self._loading or not self._driver:
            return
        self._driver.set_ui_value(key, ui_value)
        if self._driver.mode == "smart" and key in self.SMART_PRIMARY:
            apply_smart_derivation(self._driver, preserve_independent=True)
            self._loading = True
            for row_key, row in self._rows.items():
                if row_key not in self.SMART_PRIMARY and row_key not in INDEPENDENT_KEYS:
                    row.set_value(self._driver.get_ui_value(row_key))
            self._loading = False
        self.driverChanged.emit()

    def _apply_preset(self, preset_name: str) -> None:
        if not self._driver:
            return
        apply_preset(self._driver, preset_name)
        self._loading = True
        for key, row in self._rows.items():
            row.set_value(self._driver.get_ui_value(key))
        self._loading = False
        self._update_field_locks()
        self.driverChanged.emit()

    def _pick_tracks(self) -> None:
        if not self._driver:
            return
        dialog = TrackPickerDialog(load_tracks(), self.tracks_edit.text(), self)
        if dialog.exec():
            self.tracks_edit.setText(dialog.selected_tracks())
