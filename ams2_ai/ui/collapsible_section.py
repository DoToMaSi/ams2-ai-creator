"""Selectable driver header row for the driver list."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QToolButton, QVBoxLayout, QWidget


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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(8)

        self.index_label = QLabel()
        self.index_label.setMinimumWidth(24)
        self.set_index(index)
        header_layout.addWidget(self.index_label)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setText(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_btn.setStyleSheet("QToolButton { font-weight: bold; }")
        self.toggle_btn.toggled.connect(self._on_toggled)
        header_layout.addWidget(self.toggle_btn)

        header_layout.addStretch()

        for action in header_actions or []:
            header_layout.addWidget(action)

        layout.addWidget(header)

    def set_index(self, index: int) -> None:
        self.index_label.setText(f"{index}.")

    def set_title(self, title: str) -> None:
        self.toggle_btn.setText(title)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.blockSignals(False)
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
