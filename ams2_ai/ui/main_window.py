"""Main application window."""

from __future__ import annotations

import logging
import shutil
import uuid
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
)

from ams2_ai import __version__
from ams2_ai.models.document import AIDocument
from ams2_ai.smart.derivation import apply_smart_derivation
from ams2_ai.ui.dialogs import (
    NewFileDialog,
    confirm_unsaved,
    open_log_folder,
    warn_validation_errors,
)
from ams2_ai.ui.driver_accordion import DriverAccordionPanel
from ams2_ai.ui.file_sidebar import FileSidebar
from ams2_ai.validation import validate_document
from ams2_ai.xml.reader import load_document
from ams2_ai.xml.writer import save_document

logger = logging.getLogger("ams2_ai.ui.main_window")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AMS2 AI Creator v{__version__}")
        self.resize(1200, 780)

        self._documents: dict[str, AIDocument] = {}
        self._active_doc_id: str | None = None
        self._settings = QSettings()

        self.sidebar = FileSidebar()
        self.driver_panel = DriverAccordionPanel()

        splitter = QSplitter()
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.driver_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 920])
        self.setCentralWidget(splitter)

        self.setStatusBar(QStatusBar())
        self._build_menu()
        self._connect_signals()
        self._sync_driver_panel()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")

        new_action = QAction("&New File", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Open…", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_active)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As…", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_active_as)
        file_menu.addAction(save_as_action)

        export_action = QAction("&Export to AMS2…", self)
        export_action.triggered.connect(self.export_to_ams2)
        file_menu.addAction(export_action)

        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu("&Help")
        log_action = QAction("Open &Log Folder", self)
        log_action.triggered.connect(lambda: open_log_folder(self))
        help_menu.addAction(log_action)

    def _connect_signals(self) -> None:
        self.sidebar.newDocumentRequested.connect(self.new_file)
        self.sidebar.openDocumentRequested.connect(self.open_files)
        self.sidebar.documentSelected.connect(self._select_document)
        self.driver_panel.addDriverRequested.connect(self.add_driver)
        self.driver_panel.addOverrideRequested.connect(self.add_track_override)
        self.driver_panel.removeDriverRequested.connect(self.remove_driver)
        self.driver_panel.duplicateDriverRequested.connect(self.duplicate_driver)
        self.driver_panel.driverChanged.connect(self._on_driver_edited)

    def _active_document(self) -> AIDocument | None:
        if not self._active_doc_id:
            return None
        return self._documents.get(self._active_doc_id)

    def _register_document(self, document: AIDocument) -> str:
        doc_id = str(uuid.uuid4())
        self._documents[doc_id] = document
        self.sidebar.set_documents(self._documents)
        return doc_id

    def _sync_driver_panel(self, *, expand_entry_id: str | None = None) -> None:
        document = self._active_document()
        self.driver_panel.setEnabled(document is not None)
        self.driver_panel.set_document(document, expand_entry_id=expand_entry_id)

    def new_file(self) -> None:
        dialog = NewFileDialog(self)
        if not dialog.exec():
            return
        filename = dialog.selected_filename()
        path = Path(filename)
        document = AIDocument(path=path, set_name=dialog.set_name())
        document.sync_header_comment()
        doc_id = self._register_document(document)
        self._select_document(doc_id)
        self.statusBar().showMessage(f"Created {document.display_name}", 3000)

    def open_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Open AI XML Files",
            "",
            "XML Files (*.xml)",
        )
        for path_str in paths:
            path = Path(path_str)
            try:
                document = load_document(path)
            except ValueError as exc:
                logger.warning("Failed to open %s: %s", path, exc)
                QMessageBox.warning(self, "Open Failed", str(exc))
                continue
            for driver in document.drivers:
                driver.mode = "custom"
            doc_id = self._register_document(document)
            self._select_document(doc_id)
            self.statusBar().showMessage(f"Opened {document.display_name}", 3000)

    def save_active(self) -> bool:
        document = self._active_document()
        if not document:
            return False
        if not document.path:
            return self.save_active_as()
        return self._save_document(document, document.path)

    def save_active_as(self) -> bool:
        document = self._active_document()
        if not document:
            return False
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Save AI XML File",
            document.path.name if document.path else "custom_ai.xml",
            "XML Files (*.xml)",
        )
        if not path_str:
            return False
        return self._save_document(document, Path(path_str))

    def _save_document(self, document: AIDocument, path: Path) -> bool:
        errors = validate_document(document)
        if errors:
            warn_validation_errors(self, errors)
            return False
        try:
            save_document(document, path)
        except OSError as exc:
            logger.exception("Save failed: %s", path)
            QMessageBox.critical(self, "Save Failed", str(exc))
            return False
        self.sidebar.refresh_file_labels()
        self.statusBar().showMessage(f"Saved {path.name}", 3000)
        logger.info("Saved document: %s", path)
        return True

    def export_to_ams2(self) -> bool:
        document = self._active_document()
        if not document:
            return False

        default_dir = self._settings.value("ams2/custom_ai_dir", "")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select AMS2 CustomAIDrivers Folder",
            str(default_dir),
        )
        if not folder:
            return False
        self._settings.setValue("ams2/custom_ai_dir", folder)

        if not self.save_active():
            return False

        if document.path:
            target = Path(folder) / document.path.name
        else:
            target = Path(folder) / "custom_ai.xml"
        try:
            shutil.copy2(document.path, target)
        except OSError as exc:
            logger.exception("Export failed")
            QMessageBox.critical(self, "Export Failed", str(exc))
            return False

        self.statusBar().showMessage(f"Exported to {target}", 5000)
        logger.info("Exported to AMS2 folder: %s", target)
        return True

    def add_driver(self) -> None:
        document = self._active_document()
        if not document:
            return
        driver = document.add_driver()
        driver.mode = "smart"
        apply_smart_derivation(driver, preserve_independent=False)
        self._refresh_after_driver_change(driver.entry_id)

    def add_track_override(self) -> None:
        document = self._active_document()
        if not document:
            return
        base_id = self.driver_panel.current_driver_id()
        base = document.get_driver(base_id) if base_id else None
        driver = document.add_driver()
        driver.mode = base.mode if base else "smart"
        driver.is_track_override = True
        if base:
            driver.livery_name = base.livery_name
        if driver.mode == "smart":
            apply_smart_derivation(driver, preserve_independent=False)
        self._refresh_after_driver_change(driver.entry_id)

    def remove_driver(self, entry_id: str) -> None:
        document = self._active_document()
        if not document:
            return
        document.remove_driver(entry_id)
        self._sync_driver_panel()
        self.sidebar.refresh_file_labels()
        self.statusBar().showMessage("Driver removed", 2000)

    def duplicate_driver(self, entry_id: str) -> None:
        document = self._active_document()
        if not document:
            return
        cloned = document.duplicate_driver(entry_id)
        if cloned:
            self._refresh_after_driver_change(cloned.entry_id)

    def _refresh_after_driver_change(self, entry_id: str) -> None:
        self._sync_driver_panel(expand_entry_id=entry_id)
        self.sidebar.refresh_file_labels()

    def _select_document(self, doc_id: str) -> None:
        if doc_id == self._active_doc_id:
            return
        previous = self._active_document()
        if previous and previous.dirty:
            result = confirm_unsaved(self, previous.display_name)
            if result == QMessageBox.Save:
                if not self.save_active():
                    self.sidebar.set_active_document(self._active_doc_id)
                    return
            elif result == QMessageBox.Cancel:
                self.sidebar.set_active_document(self._active_doc_id)
                return

        self._active_doc_id = doc_id
        self.sidebar.set_active_document(doc_id)
        document = self._active_document()
        self._sync_driver_panel()
        title = document.display_name if document else "No file"
        self.setWindowTitle(f"AMS2 AI Creator v{__version__} — {title}")

    def _on_driver_edited(self) -> None:
        document = self._active_document()
        if document:
            document.mark_dirty()
            self.driver_panel.refresh_titles()
            self.sidebar.refresh_file_labels()

    def closeEvent(self, event) -> None:
        dirty_docs = [doc for doc in self._documents.values() if doc.dirty]
        if dirty_docs:
            names = ", ".join(doc.display_name for doc in dirty_docs)
            result = QMessageBox.question(
                self,
                "Unsaved Changes",
                f"The following files have unsaved changes:\n{names}\n\nExit anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if result != QMessageBox.Yes:
                event.ignore()
                return
        event.accept()
