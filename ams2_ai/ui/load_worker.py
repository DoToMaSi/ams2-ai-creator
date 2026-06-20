"""Background XML loading for the UI."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, Signal

from ams2_ai.xml.reader import load_document


class DocumentLoadWorker(QObject):
    """Load an AI XML document on a worker thread."""

    finished = Signal(object, object)
    failed = Signal(str, object)

    def __init__(self, path: Path):
        super().__init__()
        self._path = path

    def run(self) -> None:
        try:
            document = load_document(self._path)
            self.finished.emit(document, self._path)
        except Exception as exc:
            self.failed.emit(str(exc), self._path)
