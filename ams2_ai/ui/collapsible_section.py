"""Selectable driver header row for the driver list."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget

from ams2_ai.ui.theme import SPACING_INNER


class CollapsibleSection(QWidget):
    """Driver list row with index, title toggle, and optional header actions."""

    toggled = Signal(bool)

    def __init__(
        self,
        title: str,
        *,
        index: int = 1,
        header_actions: list[QWidget] | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._selected = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, SPACING_INNER // 2)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("driverHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(SPACING_INNER, 6, SPACING_INNER, 6)
        header_layout.setSpacing(SPACING_INNER)

        self.index_label = QLabel()
        self.index_label.setMinimumWidth(28)
        self.set_index(index)
        header_layout.addWidget(self.index_label)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setText(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_btn.toggled.connect(self._on_toggled)
        header_layout.addWidget(self.toggle_btn, stretch=1)

        for action in header_actions or []:
            header_layout.addWidget(action)

        layout.addWidget(self.header)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.header.setObjectName("driverHeaderSelected" if selected else "driverHeader")
        self.header.style().unpolish(self.header)
        self.header.style().polish(self.header)

    def set_index(self, index: int) -> None:
        self.index_label.setText(f"{index}.")

    def set_title(self, title: str) -> None:
        self.toggle_btn.setText(title)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.blockSignals(False)
        self.set_selected(expanded)
        self._update_arrow(expanded)

    def is_expanded(self) -> bool:
        return self.toggle_btn.isChecked()

    def _on_toggled(self, expanded: bool) -> None:
        self._update_arrow(expanded)
        self.toggled.emit(expanded)

    def _update_arrow(self, expanded: bool) -> None:
        self.toggle_btn.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
