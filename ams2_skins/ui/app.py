"""Skin Manager application bootstrap."""

from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from ams2_shared.logging_config import setup_logging
from ams2_shared.ui.theme import apply_theme
from ams2_skins import __version__
from ams2_skins.ui.main_window import MainWindow

logger = logging.getLogger("ams2_skins.ui.app")


def _show_exception_dialog(exc_type, exc_value, exc_tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error("Unhandled exception:\n%s", text)
    app = QApplication.instance()
    if app is not None:
        QMessageBox.critical(None, "Unexpected Error", str(exc_value))


def install_exception_hooks() -> None:
    sys.excepthook = _show_exception_dialog


def main(app: QApplication | None = None) -> int:
    owns_app = app is None
    if owns_app:
        setup_logging()
        logger.info(
            "Starting AMS2 Skin Manager v%s (Python %s)",
            __version__,
            sys.version.split()[0],
        )
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        app = QApplication(sys.argv)
        app.setApplicationName("AMS2 Skin Manager")
        app.setOrganizationName("ams2-creator")
        app.setApplicationVersion(__version__)
        apply_theme(app)

    install_exception_hooks()

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    if owns_app:
        logger.info("Application exited with code %s", exit_code)
    return exit_code
