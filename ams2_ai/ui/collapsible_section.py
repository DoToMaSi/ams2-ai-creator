"""Collapsible section widget for driver accordions."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QToolButton, QVBoxLayout, QWidget


class CollapsibleSection(QWidget):
    """Expand/collapse container with a clickable header."""

    def __init__(self, title: str, content: QWidget, parent: QWidget | None = None):
        super().__init__(parent)
        self._content = content

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setFrameShape(QFrame.Shape.StyledPanel)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setText(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.DownArrow)
        self.toggle_btn.setStyleSheet("QToolButton { font-weight: bold; }")
        self.toggle_btn.toggled.connect(self._on_toggled)
        header_layout.addWidget(self.toggle_btn, stretch=1)

        layout.addWidget(header)
        layout.addWidget(content)

    def set_title(self, title: str) -> None:
        self.toggle_btn.setText(title)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_btn.setChecked(expanded)

    def is_expanded(self) -> bool:
        return self.toggle_btn.isChecked()

    def _on_toggled(self, expanded: bool) -> None:
        self._content.setVisible(expanded)
        self.toggle_btn.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
