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


def empty_drivers_icon(size: int = 56) -> QIcon:
    """Muted driver silhouette for the empty driver list state."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    accent = QColor("#E10600")
    muted = QColor("#8B95A8")
    fill = QColor("#1C2230")

    ring_pen = QPen(accent)
    ring_pen.setWidthF(2.0)
    painter.setPen(ring_pen)
    painter.setBrush(fill)
    painter.drawEllipse(int(size * 0.18), int(size * 0.12), int(size * 0.64), int(size * 0.64))

    head_radius = size * 0.12
    cx = size * 0.5
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(muted)
    painter.drawEllipse(
        int(cx - head_radius),
        int(size * 0.28),
        int(head_radius * 2),
        int(head_radius * 2),
    )

    body_w = size * 0.34
    body_h = size * 0.22
    painter.drawRoundedRect(
        int(cx - body_w / 2),
        int(size * 0.48),
        int(body_w),
        int(body_h),
        6,
        6,
    )

    plus_pen = QPen(accent)
    plus_pen.setWidthF(2.4)
    plus_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(plus_pen)
    plus_x = size * 0.72
    plus_y = size * 0.72
    plus_r = size * 0.11
    painter.drawLine(int(plus_x - plus_r), int(plus_y), int(plus_x + plus_r), int(plus_y))
    painter.drawLine(int(plus_x), int(plus_y - plus_r), int(plus_x), int(plus_y + plus_r))

    painter.end()
    return QIcon(pixmap)
