"""Background AMS2 catalog scan worker."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from ams2_skins.catalog.scanner import scan_ams2_catalog


class CatalogScanWorker(QThread):
    finished_scan = Signal(list)
    failed = Signal(str)

    def __init__(self, ams2_root: Path):
        super().__init__()
        self._ams2_root = ams2_root

    def run(self) -> None:
        try:
            entries = scan_ams2_catalog(self._ams2_root)
            self.finished_scan.emit(entries)
        except OSError as exc:
            self.failed.emit(str(exc))
