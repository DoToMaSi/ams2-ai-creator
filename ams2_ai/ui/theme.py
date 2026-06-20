"""AMS2-inspired application theme."""

from __future__ import annotations

import logging

from PySide6.QtGui import QFont, QFontDatabase, QIcon
from PySide6.QtWidgets import QApplication

from ams2_ai.util.assets import font_paths, icon_ico_path, icon_png_path, stylesheet_path

logger = logging.getLogger("ams2_ai.ui.theme")

FONT_FAMILY = "Rubik"
BASE_FONT_SIZE = 11
HEADER_FONT_SIZE = 12

SPACING_INNER = 8
SPACING_SECTION = 12
SPACING_OUTER = 16


def apply_theme(app: QApplication) -> None:
    """Load font, stylesheet, and window icon."""
    _load_font(app)
    _load_stylesheet(app)
    _load_icon(app)


def _load_font(app: QApplication) -> None:
    loaded_family: str | None = None
    for path in font_paths():
        if not path.is_file():
            logger.warning("UI font not found: %s", path)
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            logger.warning("Failed to load UI font: %s", path)
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            loaded_family = families[0]

    if not loaded_family:
        logger.warning("No Rubik fonts loaded; using system default")
        return

    font = QFont(loaded_family, BASE_FONT_SIZE)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)


def _load_stylesheet(app: QApplication) -> None:
    path = stylesheet_path()
    if not path.is_file():
        logger.warning("Stylesheet not found: %s", path)
        return
    app.setStyleSheet(path.read_text(encoding="utf-8"))


def _load_icon(app: QApplication) -> None:
    for path in (icon_ico_path(), icon_png_path()):
        if path.is_file():
            app.setWindowIcon(QIcon(str(path)))
            return
    logger.warning("Application icon not found under assets/icon/")
