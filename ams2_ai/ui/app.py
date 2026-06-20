"""Application bootstrap and global exception handling."""

from __future__ import annotations

import logging
import sys
import traceback

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from ams2_ai import __version__
from ams2_ai.logging_config import setup_logging
from ams2_ai.ui.dialogs import ErrorDialog
from ams2_ai.ui.main_window import MainWindow

logger = logging.getLogger("ams2_ai.ui.app")


def _show_exception_dialog(exc_type, exc_value, exc_tb) -> None:
    text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.error("Unhandled exception:\n%s", text)
    app = QApplication.instance()
    if app is not None:
        dialog = ErrorDialog(str(exc_value), text)
        dialog.exec()


def install_exception_hooks() -> None:
    sys.excepthook = _show_exception_dialog


def main() -> int:
    setup_logging()
    logger.info(
        "Starting AMS2 AI Creator v%s (Python %s)",
        __version__,
        sys.version.split()[0],
    )

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("AMS2 AI Creator")
    app.setOrganizationName("ams2-ai-creator")
    app.setApplicationVersion(__version__)

    install_exception_hooks()

    window = MainWindow()
    window.show()

    exit_code = app.exec()
    logger.info("Application exited with code %s", exit_code)
    return exit_code
