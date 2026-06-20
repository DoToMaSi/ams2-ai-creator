"""Scrollable grouped parameter editor."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QGroupBox, QScrollArea, QVBoxLayout, QWidget

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import (
    OPTIONAL_PARAMETER_GROUPS,
    OPTIONAL_PARAMETER_KEYS,
    PARAMETER_GROUPS,
    PARAMETERS,
    ParameterDef,
    default_ui_value,
)
from ams2_ai.smart.derivation import INDEPENDENT_KEYS, apply_smart_derivation
from ams2_ai.ui.parameter_row import OverrideParameterRow, ParameterRow
from ams2_ai.ui.theme import SPACING_INNER, SPACING_SECTION


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
        self._group_boxes: dict[str, QGroupBox] = {}
        self._group_keys: dict[str, list[str]] = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(
            SPACING_SECTION, SPACING_SECTION, SPACING_SECTION, SPACING_SECTION
        )
        content_layout.setSpacing(SPACING_INNER)

        grouped: dict[str, list[ParameterDef]] = {g: [] for g in PARAMETER_GROUPS}
        for param in PARAMETERS:
            grouped[param.group].append(param)

        for group_name in PARAMETER_GROUPS:
            box = QGroupBox(group_name)
            if group_name in OPTIONAL_PARAMETER_GROUPS and not per_track:
                box.setCheckable(True)
                box.setChecked(False)
                box.setToolTip("Include these parameters in the exported XML")
                box.toggled.connect(
                    lambda checked, group=group_name: self._on_group_toggled(group, checked)
                )
                self._group_boxes[group_name] = box
                self._group_keys[group_name] = list(OPTIONAL_PARAMETER_GROUPS[group_name])
            box_layout = QVBoxLayout(box)
            box_layout.setSpacing(SPACING_INNER)
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

        smart = entry.mode == "smart"
        for group_name, box in self._group_boxes.items():
            keys = self._group_keys[group_name]
            group_enabled = any(key in entry.set_fields for key in keys)
            box.setChecked(group_enabled)
            for key in keys:
                row = self._rows[key]
                row.set_value(self._display_ui_value(key))
                row.set_enabled_editable(
                    group_enabled and self._is_row_editable(key, smart)
                )

        for key, row in self._rows.items():
            if key in OPTIONAL_PARAMETER_KEYS and not self._per_track:
                continue
            row.set_value(self._display_ui_value(key))
            if self._per_track and isinstance(row, OverrideParameterRow):
                globally_enabled = self._global_optional_enabled(key)
                enabled = key in entry.set_fields and key in entry.values
                row.set_override_enabled(enabled)
                row.set_controls_enabled(enabled and globally_enabled)
                row.override_check.setEnabled(globally_enabled)
            elif not self._per_track:
                row.set_enabled_editable(self._is_row_editable(key, smart))

        if not self._per_track:
            self._update_smart_locks()
        self._loading = False

    def refresh_values(self) -> None:
        if not self._entry:
            return
        self._loading = True
        for key, row in self._rows.items():
            row.set_value(self._display_ui_value(key))
        self._loading = False

    def refresh_from_base(self, base_entry: DriverEntry) -> None:
        """Reload per-track rows after global settings change."""
        if not self._per_track or not self._entry:
            return
        self._base_entry = base_entry
        self.refresh_values()

    def _display_ui_value(self, key: str) -> int:
        if not self._entry:
            return default_ui_value(key)
        if self._per_track and key not in self._entry.set_fields and self._base_entry:
            return self._base_entry.get_ui_value(key)
        return self._entry.get_ui_value(key)

    def _global_optional_enabled(self, key: str) -> bool:
        if key not in OPTIONAL_PARAMETER_KEYS:
            return True
        if not self._base_entry:
            return False
        return key in self._base_entry.set_fields

    def _is_group_enabled_for_key(self, key: str) -> bool:
        if key not in OPTIONAL_PARAMETER_KEYS:
            return True
        for group_name, keys in self._group_keys.items():
            if key in keys:
                box = self._group_boxes.get(group_name)
                return box.isChecked() if box else False
        return True

    def _smart_mode_editable(self, key: str, smart: bool) -> bool:
        if not smart:
            return True
        return key in self.SMART_PRIMARY or key in INDEPENDENT_KEYS

    def _is_row_editable(self, key: str, smart: bool) -> bool:
        if key in OPTIONAL_PARAMETER_KEYS and not self._is_group_enabled_for_key(key):
            return False
        return self._smart_mode_editable(key, smart)

    def apply_smart_locks(self, smart: bool) -> None:
        if self._per_track:
            return
        for key, row in self._rows.items():
            row.set_enabled_editable(self._is_row_editable(key, smart))

    def _update_smart_locks(self) -> None:
        if not self._entry or self._per_track:
            return
        self.apply_smart_locks(self._entry.mode == "smart")

    def _on_group_toggled(self, group_name: str, checked: bool) -> None:
        if self._loading or not self._entry:
            return
        smart = self._entry.mode == "smart"
        for key in self._group_keys[group_name]:
            row = self._rows[key]
            if checked:
                self._entry.set_ui_value(key, row.value())
            else:
                self._entry.clear_field(key)
                row.set_value(self._display_ui_value(key))
            row.set_enabled_editable(checked and self._is_row_editable(key, smart))
        self.changed.emit()

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
            row.set_controls_enabled(enabled and self._global_optional_enabled(key))
        self.changed.emit()
