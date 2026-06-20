"""Slider + spinbox parameter row widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QSlider, QSpinBox, QWidget

from ams2_ai.models.parameters import ParameterDef


class ParameterRow(QWidget):
    valueChanged = Signal(str, int)

    def __init__(self, param: ParameterDef, parent: QWidget | None = None):
        super().__init__(parent)
        self.param = param
        self._blocked = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(param.label)
        label.setMinimumWidth(180)
        label.setToolTip(param.tooltip)
        layout.addWidget(label)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setMinimum(param.ui_min)
        self.slider.setMaximum(param.ui_max)
        self.slider.setToolTip(param.tooltip)
        layout.addWidget(self.slider, stretch=1)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(param.ui_min)
        self.spinbox.setMaximum(param.ui_max)
        self.spinbox.setToolTip(param.tooltip)
        layout.addWidget(self.spinbox)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _on_slider_changed(self, value: int) -> None:
        if self._blocked:
            return
        self._blocked = True
        self.spinbox.setValue(value)
        self._blocked = False
        self.valueChanged.emit(self.param.key, value)

    def _on_spinbox_changed(self, value: int) -> None:
        if self._blocked:
            return
        self._blocked = True
        self.slider.setValue(value)
        self._blocked = False
        self.valueChanged.emit(self.param.key, value)

    def set_value(self, value: int) -> None:
        self._blocked = True
        self.slider.setValue(value)
        self.spinbox.setValue(value)
        self._blocked = False

    def value(self) -> int:
        return self.spinbox.value()

    def set_enabled_editable(self, enabled: bool) -> None:
        self.slider.setEnabled(enabled)
        self.spinbox.setEnabled(enabled)


class OverrideParameterRow(ParameterRow):
    """Parameter row with an override checkbox (per-track tabs)."""

    overrideToggled = Signal(str, bool)

    def __init__(self, param: ParameterDef, parent: QWidget | None = None):
        super().__init__(param, parent)
        layout = self.layout()
        self.override_check = QCheckBox()
        self.override_check.setToolTip(
            "Enable override for this track; checked fields follow Global when it changes"
        )
        self.override_check.toggled.connect(self._on_override_toggled)
        layout.insertWidget(0, self.override_check)
        self.set_controls_enabled(False)

    def _on_override_toggled(self, checked: bool) -> None:
        if self._blocked:
            return
        self.overrideToggled.emit(self.param.key, checked)
        if checked:
            self.valueChanged.emit(self.param.key, self.value())

    def set_override_enabled(self, enabled: bool) -> None:
        self._blocked = True
        self.override_check.setChecked(enabled)
        self._blocked = False

    def set_controls_enabled(self, enabled: bool) -> None:
        self.set_enabled_editable(enabled)
