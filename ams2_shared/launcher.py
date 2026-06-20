"""Suite launcher — pick AI Creator or Skin Manager."""

from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ams2_shared import __version__
from ams2_shared.logging_config import setup_logging
from ams2_shared.ui.theme import SPACING_INNER, SPACING_OUTER, SPACING_SECTION, apply_theme
from ams2_shared.util.assets import icon_png_path

logger = logging.getLogger("ams2.launcher")

TOOL_AI = "ai"
TOOL_SKINS = "skins"
SETTINGS_KEY = "launcher/last_tool"
SETTINGS_REMEMBER = "launcher/remember_choice"


class LauncherWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"AMS2 Creator v{__version__}")
        self.setMinimumSize(480, 360)
        self.resize(520, 400)
        self._choice: str | None = None

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(SPACING_OUTER, SPACING_OUTER, SPACING_OUTER, SPACING_OUTER)
        layout.setSpacing(SPACING_SECTION)

        title = QLabel("AMS2 Creator")
        title.setObjectName("sectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Choose a tool to open")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        icon_path = icon_png_path()
        if icon_path.is_file():
            from PySide6.QtGui import QPixmap

            icon_label = QLabel()
            pixmap = QPixmap(str(icon_path)).scaled(
                96,
                96,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)

        layout.addSpacing(SPACING_INNER)

        ai_btn = QPushButton("AI Creator")
        ai_btn.setObjectName("primaryButton")
        ai_btn.setMinimumHeight(44)
        ai_btn.clicked.connect(lambda: self._pick(TOOL_AI))
        layout.addWidget(ai_btn)

        skins_btn = QPushButton("Skin Manager")
        skins_btn.setObjectName("secondaryButton")
        skins_btn.setMinimumHeight(44)
        skins_btn.clicked.connect(lambda: self._pick(TOOL_SKINS))
        layout.addWidget(skins_btn)

        self.remember_check = QCheckBox("Remember my choice")
        self.remember_check.setChecked(QSettings().value(SETTINGS_REMEMBER, False, type=bool))
        layout.addWidget(self.remember_check)

        layout.addStretch()
        self.setCentralWidget(central)

    def _pick(self, tool: str) -> None:
        settings = QSettings()
        if self.remember_check.isChecked():
            settings.setValue(SETTINGS_REMEMBER, True)
            settings.setValue(SETTINGS_KEY, tool)
        else:
            settings.setValue(SETTINGS_REMEMBER, False)
            settings.remove(SETTINGS_KEY)
        self._choice = tool
        self.close()

    def chosen_tool(self) -> str | None:
        return self._choice


def remembered_tool() -> str | None:
    settings = QSettings()
    if not settings.value(SETTINGS_REMEMBER, False, type=bool):
        return None
    tool = settings.value(SETTINGS_KEY, "")
    if tool in (TOOL_AI, TOOL_SKINS):
        return tool
    return None


def run_launcher(app: QApplication) -> str | None:
    window = LauncherWindow()
    window.show()
    app.processEvents()
    while window.isVisible():
        app.processEvents()
    return window.chosen_tool()


def launch_tool(app: QApplication, tool: str) -> int:
    if tool == TOOL_AI:
        from ams2_ai.ui.app import main as ai_main

        return ai_main(app=app)
    if tool == TOOL_SKINS:
        from ams2_skins.ui.app import main as skins_main

        return skins_main(app=app)
    logger.error("Unknown tool: %s", tool)
    return 1


def main() -> int:
    setup_logging()
    logger.info("Starting AMS2 Creator suite v%s", __version__)

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("AMS2 Creator")
    app.setOrganizationName("ams2-creator")
    app.setApplicationVersion(__version__)
    apply_theme(app)

    tool = remembered_tool()
    if tool is None:
        tool = run_launcher(app)
    if tool is None:
        return 0

    exit_code = launch_tool(app, tool)
    logger.info("Application exited with code %s", exit_code)
    return exit_code
