"""Small themed icons drawn in code (consistent across platforms)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


def duplicate_icon(size: int = 20) -> QIcon:
    """Two overlapping pages — reads as duplicate, not a shortcut link."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    stroke = QPen(QColor("#E8ECF1"))
    stroke.setWidthF(1.2)
    painter.setPen(stroke)
    painter.setBrush(QColor("#1C2230"))

    back = size * 0.62
    front = size * 0.62
    offset = size * 0.18
    margin = size * 0.12

    painter.drawRoundedRect(
        int(margin + offset),
        int(margin),
        int(back),
        int(back),
        2,
        2,
    )
    painter.drawRoundedRect(
        int(margin),
        int(margin + offset),
        int(front),
        int(front),
        2,
        2,
    )
    painter.end()
    return QIcon(pixmap)
