"""Collapsible UI blocks for the driver list and document panels."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.ui.theme import SPACING_INNER, SPACING_SECTION


class CollapsibleBlock(QWidget):
    """Expand/collapse header with arbitrary content below."""

    toggled = Signal(bool)

    def __init__(
        self,
        title: str,
        content: QWidget,
        *,
        expanded: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._content = content

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("collapsibleHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(SPACING_SECTION, SPACING_INNER, SPACING_SECTION, SPACING_INNER)
        header_layout.setSpacing(SPACING_INNER)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setObjectName("collapsibleToggle")
        self.toggle_btn.setText(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self.toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_btn.toggled.connect(self._on_toggled)
        header_layout.addWidget(self.toggle_btn, stretch=1)

        layout.addWidget(self.header)
        layout.addWidget(self._content)
        self._content.setVisible(expanded)

    def set_expanded(self, expanded: bool) -> None:
        self.toggle_btn.blockSignals(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.blockSignals(False)
        self._content.setVisible(expanded)
        self._update_arrow(expanded)

    def is_expanded(self) -> bool:
        return self.toggle_btn.isChecked()

    def _on_toggled(self, expanded: bool) -> None:
        self._content.setVisible(expanded)
        self._update_arrow(expanded)
        self.toggled.emit(expanded)

    def _update_arrow(self, expanded: bool) -> None:
        self.toggle_btn.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )


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
        header_layout.setContentsMargins(SPACING_SECTION, SPACING_INNER, SPACING_SECTION, SPACING_INNER)
        header_layout.setSpacing(SPACING_INNER)

        self.index_label = QLabel()
        self.index_label.setObjectName("driverIndex")
        self.index_label.setMinimumWidth(32)
        self.set_index(index)
        header_layout.addWidget(self.index_label)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setObjectName("driverToggle")
        self.toggle_btn.setText(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_btn.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_btn.setMinimumHeight(34)
        self.toggle_btn.toggled.connect(self._on_toggled)
        header_layout.addWidget(self.toggle_btn, stretch=1)

        for action in header_actions or []:
            header_layout.addWidget(action, 0)

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
