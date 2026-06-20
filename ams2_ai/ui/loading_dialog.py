"""Progress dialog shown while loading large XML files."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QProgressDialog, QWidget


class LoadingDialog:
    """Modal loading indicator that stays responsive via processEvents."""

    def __init__(self, parent: QWidget | None, *, title: str = "Loading"):
        self._dialog = QProgressDialog(parent)
        self._dialog.setWindowTitle(title)
        self._dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._dialog.setMinimumDuration(0)
        self._dialog.setCancelButton(None)
        self._dialog.setRange(0, 0)
        self._dialog.setMinimumWidth(420)

    def show(self, message: str) -> None:
        self.set_message(message)
        self._dialog.show()
        QApplication.processEvents()

    def set_message(self, message: str) -> None:
        self._dialog.setLabelText(message)
        QApplication.processEvents()

    def close(self) -> None:
        self._dialog.close()
        QApplication.processEvents()


def run_with_loading(
    parent: QWidget | None,
    message: str,
    task: Callable[[Callable[[str], None]], None],
    *,
    title: str = "Loading",
) -> None:
    """Run a task on the UI thread while showing progress updates."""
    dialog = LoadingDialog(parent, title=title)
    dialog.show(message)
    try:
        task(dialog.set_message)
    finally:
        dialog.close()
