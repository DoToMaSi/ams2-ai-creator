"""Slider + spinbox parameter row widget."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QSlider,
    QSpinBox,
    QToolButton,
    QWidget,
)

from ams2_ai.models.parameters import ParameterDef


def param_help_html(param: ParameterDef) -> str:
    return (
        f"<b>{param.label}</b><br>"
        f"{param.description}<br><br>"
        f"<b>Low:</b> {param.low_hint}<br>"
        f"<b>High:</b> {param.high_hint}"
    )


def param_help_plain(param: ParameterDef) -> str:
    return f"{param.description}\n\nLow: {param.low_hint}\nHigh: {param.high_hint}"


class ParameterRow(QWidget):
    valueChanged = Signal(str, int)

    def __init__(self, param: ParameterDef, parent: QWidget | None = None):
        super().__init__(parent)
        self.param = param
        self._blocked = False
        self.setObjectName("parameterRow")
        self.setProperty("editable", True)
        self.setMinimumHeight(32)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)

        self.label = QLabel(param.label)
        self.label.setMinimumWidth(200)
        layout.addWidget(self.label)

        self.slider = QSlider()
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setMinimum(param.ui_min)
        self.slider.setMaximum(param.ui_max)
        layout.addWidget(self.slider, stretch=1)

        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(param.ui_min)
        self.spinbox.setMaximum(param.ui_max)
        self.spinbox.setFixedWidth(88)
        self.spinbox.setObjectName("paramSpinBox")
        layout.addWidget(self.spinbox)

        self._help_btn = self._make_help_button(param)
        layout.addWidget(self._help_btn)

        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)

    def _make_help_button(self, param: ParameterDef) -> QToolButton:
        btn = QToolButton()
        btn.setObjectName("helpButton")
        btn.setText("?")
        btn.setToolTip(param_help_html(param))
        btn.setAutoRaise(True)
        btn.clicked.connect(lambda: self._show_help_dialog(param))
        return btn

    def _show_help_dialog(self, param: ParameterDef) -> None:
        QMessageBox.information(self, param.label, param_help_plain(param))

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
        self.setProperty("editable", enabled)
        self.style().unpolish(self)
        self.style().polish(self)


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
