"""Scrollable grouped parameter editor."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGroupBox, QScrollArea, QVBoxLayout, QWidget

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import PARAMETER_GROUPS, PARAMETERS, ParameterDef
from ams2_ai.smart.derivation import INDEPENDENT_KEYS, apply_smart_derivation
from ams2_ai.ui.parameter_row import OverrideParameterRow, ParameterRow


class ParameterPanel(QWidget):
    """Parameter groups for global or per-track editing."""

    changed = Signal()

    SMART_PRIMARY = {"race_skill", "aggression"}

    def __init__(
        self,
        *,
        per_track: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._per_track = per_track
        self._entry: DriverEntry | None = None
        self._base_entry: DriverEntry | None = None
        self._loading = False
        self._rows: dict[str, ParameterRow | OverrideParameterRow] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)

        grouped: dict[str, list[ParameterDef]] = {g: [] for g in PARAMETER_GROUPS}
        for param in PARAMETERS:
            grouped[param.group].append(param)

        for group_name in PARAMETER_GROUPS:
            box = QGroupBox(group_name)
            box_layout = QVBoxLayout(box)
            for param in grouped[group_name]:
                if per_track:
                    row = OverrideParameterRow(param)
                    row.overrideToggled.connect(self._on_override_toggled)
                else:
                    row = ParameterRow(param)
                row.valueChanged.connect(self._on_value_changed)
                self._rows[param.key] = row
                box_layout.addWidget(row)
            content_layout.addWidget(box)

        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)

    def set_entry(
        self,
        entry: DriverEntry | None,
        base_entry: DriverEntry | None = None,
    ) -> None:
        self._loading = True
        self._entry = entry
        if self._per_track:
            self._base_entry = base_entry
        if not entry:
            self._loading = False
            return

        for key, row in self._rows.items():
            row.set_value(self._display_ui_value(key))
            if self._per_track and isinstance(row, OverrideParameterRow):
                enabled = key in entry.set_fields and key in entry.values
                row.set_override_enabled(enabled)
                row.set_controls_enabled(enabled)

        if not self._per_track:
            self._update_smart_locks()
        self._loading = False

    def refresh_from_base(self, base_entry: DriverEntry) -> None:
        """Reload per-track rows after global settings change."""
        if not self._per_track or not self._entry:
            return
        self.set_entry(self._entry, base_entry)
        if not self._entry:
            return
        self._loading = True
        for key, row in self._rows.items():
            row.set_value(self._display_ui_value(key))
        self._loading = False

    def _display_ui_value(self, key: str) -> int:
        if not self._entry:
            return 50
        if self._per_track and key not in self._entry.set_fields and self._base_entry:
            return self._base_entry.get_ui_value(key)
        return self._entry.get_ui_value(key)

    def apply_smart_locks(self, smart: bool) -> None:
        if self._per_track:
            return
        for key, row in self._rows.items():
            if not smart:
                editable = True
            else:
                editable = key in self.SMART_PRIMARY or key in INDEPENDENT_KEYS
            row.set_enabled_editable(editable)

    def _update_smart_locks(self) -> None:
        if not self._entry or self._per_track:
            return
        self.apply_smart_locks(self._entry.mode == "smart")

    def _on_value_changed(self, key: str, ui_value: int) -> None:
        if self._loading or not self._entry:
            return
        self._entry.set_ui_value(key, ui_value)
        if not self._per_track and self._entry.mode == "smart" and key in self.SMART_PRIMARY:
            apply_smart_derivation(self._entry, preserve_independent=True)
            self._loading = True
            for row_key, row in self._rows.items():
                if row_key not in self.SMART_PRIMARY and row_key not in INDEPENDENT_KEYS:
                    row.set_value(self._entry.get_ui_value(row_key))
            self._loading = False
        self.changed.emit()

    def _on_override_toggled(self, key: str, enabled: bool) -> None:
        if self._loading or not self._entry:
            return
        row = self._rows[key]
        if enabled:
            ui_value = self._display_ui_value(key)
            self._entry.set_ui_value(key, ui_value)
            row.set_value(ui_value)
        else:
            self._entry.clear_field(key)
            row.set_value(self._display_ui_value(key))
        if isinstance(row, OverrideParameterRow):
            row.set_controls_enabled(enabled)
        self.changed.emit()
