"""Driver profile editor with Global and per-track tabs."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
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
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.data import load_countries, load_tracks
from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver_profile import DriverProfile
from ams2_ai.smart.derivation import apply_smart_derivation
from ams2_ai.smart.presets import PRESET_NAMES, apply_preset
from ams2_ai.ui.dialogs import SingleTrackPickerDialog
from ams2_ai.ui.parameter_panel import ParameterPanel


class DriverEditor(QWidget):
    driverChanged = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._profile: DriverProfile | None = None
        self._document: AIDocument | None = None
        self._loading = False
        self._track_panels: dict[str, ParameterPanel] = {}
        self._track_tabs: dict[str, QWidget] = {}

        root = QVBoxLayout(self)

        identity_box = QGroupBox("Identity")
        identity_form = QFormLayout(identity_box)
        self.livery_edit = QLineEdit()
        self.livery_edit.textChanged.connect(self._on_identity_changed)
        identity_form.addRow("Livery Name:", self.livery_edit)

        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._on_identity_changed)
        identity_form.addRow("Driver Name:", self.name_edit)

        self.country_combo = QComboBox()
        self.country_combo.setEditable(True)
        self.country_combo.addItems(load_countries())
        self.country_combo.currentTextChanged.connect(self._on_identity_changed)
        identity_form.addRow("Country:", self.country_combo)
        root.addWidget(identity_box)

        self.tabs = QTabWidget()

        self.global_tab = QWidget()
        global_layout = QVBoxLayout(self.global_tab)

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
        global_layout.addLayout(mode_row)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Presets:"))
        for name in PRESET_NAMES:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _checked=False, n=name: self._apply_preset(n))
            preset_row.addWidget(btn)
        preset_row.addStretch()
        global_layout.addLayout(preset_row)

        self.global_panel = ParameterPanel(per_track=False)
        self.global_panel.changed.connect(self._on_global_changed)
        global_layout.addWidget(self.global_panel, stretch=1)

        self.tabs.addTab(self.global_tab, "Global")

        add_track_btn = QToolButton()
        add_track_btn.setText("+")
        add_track_btn.setToolTip("Add track override")
        add_track_btn.clicked.connect(self._add_track_tab)
        self.tabs.setCornerWidget(add_track_btn, Qt.Corner.TopRightCorner)

        root.addWidget(self.tabs, stretch=1)

        self.smart_radio.toggled.connect(self._on_mode_changed)
        self.custom_radio.toggled.connect(self._on_mode_changed)

    def set_profile(
        self,
        profile: DriverProfile | None,
        document: AIDocument | None = None,
    ) -> None:
        self._loading = True
        self._profile = profile
        self._document = document
        enabled = profile is not None
        self.setEnabled(enabled)

        self._clear_track_tabs()

        if not profile:
            self._loading = False
            return

        self.livery_edit.setText(profile.base.livery_name)
        self.name_edit.setText(profile.base.name)
        self.country_combo.setCurrentText(profile.base.country)

        if profile.base.mode == "smart":
            self.smart_radio.setChecked(True)
        else:
            self.custom_radio.setChecked(True)

        self.global_panel.set_entry(profile.base)

        for override in profile.track_overrides:
            self._create_track_tab(override)

        self._loading = False

    def _clear_track_tabs(self) -> None:
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        self._track_panels.clear()
        self._track_tabs.clear()

    def _create_track_tab(self, override) -> None:
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)

        header = QHBoxLayout()
        header.addWidget(QLabel(f"Track: {override.tracks}"))
        header.addStretch()
        remove_btn = QPushButton("Remove track")
        remove_btn.clicked.connect(
            lambda _checked=False, eid=override.entry_id: self._remove_track_tab(eid)
        )
        header.addWidget(remove_btn)
        tab_layout.addLayout(header)

        panel = ParameterPanel(per_track=True)
        panel.set_entry(override)
        panel.changed.connect(self._on_track_changed)
        tab_layout.addWidget(panel, stretch=1)

        self._track_panels[override.entry_id] = panel
        self._track_tabs[override.entry_id] = tab
        self.tabs.addTab(tab, override.tracks)

    def _add_track_tab(self) -> None:
        if not self._profile:
            return
        existing = {o.tracks for o in self._profile.track_overrides}
        dialog = SingleTrackPickerDialog(load_tracks(), existing, self)
        if not dialog.exec():
            return
        track = dialog.selected_track()
        override = self._profile.add_track(track)
        if not override:
            return
        self._create_track_tab(override)
        self.tabs.setCurrentWidget(self._track_tabs[override.entry_id])
        self._sync_profile()

    def _remove_track_tab(self, entry_id: str) -> None:
        if not self._profile:
            return
        index = self.tabs.indexOf(self._track_tabs.get(entry_id, QWidget()))
        if index >= 0:
            self.tabs.removeTab(index)
        self._track_panels.pop(entry_id, None)
        self._track_tabs.pop(entry_id, None)
        self._profile.remove_track(entry_id)
        self._sync_profile()

    def _on_identity_changed(self) -> None:
        if self._loading or not self._profile:
            return
        base = self._profile.base
        base.livery_name = self.livery_edit.text()
        base.name = self.name_edit.text()
        base.country = self.country_combo.currentText().strip().upper()
        if base.name:
            base.set_fields.add("name")
        else:
            base.set_fields.discard("name")
        if base.country:
            base.set_fields.add("country")
        else:
            base.set_fields.discard("country")
        self._profile.sync_livery_to_overrides()
        self._sync_profile()

    def _on_mode_changed(self) -> None:
        if self._loading or not self._profile:
            return
        base = self._profile.base
        base.mode = "smart" if self.smart_radio.isChecked() else "custom"
        if base.mode == "smart":
            apply_smart_derivation(base, preserve_independent=True)
            self.global_panel.refresh_values()
        self.global_panel.apply_smart_locks(base.mode == "smart")
        self._sync_profile()

    def _on_global_changed(self) -> None:
        if self._loading or not self._profile:
            return
        self.global_panel.apply_smart_locks(self._profile.base.mode == "smart")
        self._sync_profile()

    def _on_track_changed(self) -> None:
        if self._loading:
            return
        self._sync_profile()

    def _apply_preset(self, preset_name: str) -> None:
        if not self._profile:
            return
        apply_preset(self._profile.base, preset_name)
        self.global_panel.set_entry(self._profile.base)
        self.global_panel.apply_smart_locks(self._profile.base.mode == "smart")
        self._sync_profile()

    def _sync_profile(self) -> None:
        if self._document and self._profile:
            self._document.replace_profile(self._profile)
        self.driverChanged.emit()
