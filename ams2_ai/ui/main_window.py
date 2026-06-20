"""Main application window."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

from PySide6.QtCore import QSettings, QThread
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ams2_ai import __version__
from ams2_ai.identity.generator import randomize_new_driver
from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.driver_profile import DriverProfile
from ams2_ai.ui.dialogs import (
    NewFileDialog,
    confirm_unsaved,
    open_log_folder,
    warn_validation_errors,
)
from ams2_ai.ui.driver_accordion import DriverAccordionPanel
from ams2_ai.ui.file_sidebar import FileSidebar
from ams2_ai.ui.load_worker import DocumentLoadWorker
from ams2_ai.ui.loading_dialog import LoadingDialog
from ams2_ai.validation import validate_document
from ams2_ai.xml.writer import save_document, serialize_document

logger = logging.getLogger("ams2_ai.ui.main_window")

LARGE_DOCUMENT_THRESHOLD = 25


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AMS2 AI Creator v{__version__}")
        self.resize(1200, 960)
        self.setMinimumSize(960, 720)

        self._documents: dict[str, AIDocument] = {}
        self._active_doc_id: str | None = None
        self._settings = QSettings()
        self._open_paths_queue: list[Path] = []
        self._loading_dialog: LoadingDialog | None = None
        self._load_thread: QThread | None = None
        self._load_worker: DocumentLoadWorker | None = None
        self._pending_open_doc_id: str | None = None

        self.sidebar = FileSidebar()
        self.driver_panel = DriverAccordionPanel()

        splitter = QSplitter()
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.driver_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 920])

        footer = QHBoxLayout()
        footer.addStretch()
        self.save_btn = QPushButton("Save")
        self.save_btn.setShortcut(QKeySequence.Save)
        self.save_btn.clicked.connect(self.save_active)
        footer.addWidget(self.save_btn)
        self.export_xml_btn = QPushButton("Export AI XML")
        self.export_xml_btn.clicked.connect(self.export_ai_xml)
        footer.addWidget(self.export_xml_btn)

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(splitter, stretch=1)
        central_layout.addLayout(footer)
        self.setCentralWidget(central)

        self.setStatusBar(QStatusBar())
        self._build_menu()
        self._connect_signals()
        self._sync_driver_panel()
        self._refresh_save_state()

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

        export_xml_action = QAction("Export AI &XML…", self)
        export_xml_action.triggered.connect(self.export_ai_xml)
        file_menu.addAction(export_xml_action)

        export_action = QAction("Export to &AMS2…", self)
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

    def _sync_driver_panel(self, *, expand_profile_id: str | None = None) -> None:
        document = self._active_document()
        self.driver_panel.setEnabled(document is not None)
        self._populate_driver_panel(document, expand_profile_id=expand_profile_id)

    def _populate_driver_panel(
        self,
        document: AIDocument | None,
        *,
        expand_profile_id: str | None = None,
    ) -> None:
        if document is None:
            self.driver_panel.set_document(None)
            return

        if len(document.profiles()) <= LARGE_DOCUMENT_THRESHOLD:
            self.driver_panel.set_document(document, expand_profile_id=expand_profile_id)
            return

        self._show_loading_dialog(f"Building driver list for {document.display_name}…")
        self.driver_panel.set_document(
            document,
            expand_profile_id=expand_profile_id,
            progress=self._loading_dialog.set_message if self._loading_dialog else None,
            finished=self._finish_loading_dialog,
        )

    def _show_loading_dialog(self, message: str) -> None:
        self._loading_dialog = LoadingDialog(self, title="Loading")
        self._loading_dialog.show(message)
        self.setEnabled(False)

    def _finish_loading_dialog(self) -> None:
        if self._loading_dialog:
            self._loading_dialog.close()
            self._loading_dialog = None
        self.setEnabled(True)

    def _cleanup_load_thread(self) -> None:
        if self._load_thread is not None:
            self._load_thread.quit()
            self._load_thread.wait()
        self._load_thread = None
        self._load_worker = None

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
        if not paths:
            return

        if self._active_doc_id:
            previous = self._active_document()
            if previous and previous.dirty:
                result = confirm_unsaved(self, previous.display_name)
                if result == QMessageBox.Save:
                    if not self.save_active():
                        return
                elif result == QMessageBox.Cancel:
                    return

        self._open_paths_queue = [Path(path_str) for path_str in paths]
        remaining = len(self._open_paths_queue)
        self._show_loading_dialog(
            f"Preparing to open {remaining} file{'s' if remaining != 1 else ''}…"
        )
        self._load_next_open_path()

    def _load_next_open_path(self) -> None:
        if not self._open_paths_queue:
            self._finish_open_sequence()
            return

        path = self._open_paths_queue[0]
        if self._loading_dialog:
            self._loading_dialog.set_message(f"Reading {path.name}…")

        self._cleanup_load_thread()
        self._load_thread = QThread(self)
        self._load_worker = DocumentLoadWorker(path)
        self._load_worker.moveToThread(self._load_thread)
        self._load_thread.started.connect(self._load_worker.run)
        self._load_worker.finished.connect(self._on_document_loaded)
        self._load_worker.failed.connect(self._on_document_load_failed)
        self._load_thread.start()

    def _on_document_loaded(self, document: AIDocument, path: Path) -> None:
        self._cleanup_load_thread()
        if not self._open_paths_queue or self._open_paths_queue[0] != path:
            return

        self._open_paths_queue.pop(0)
        for profile in document.profiles():
            profile.base.mode = "custom"
        document.commit_saved_state(serialize_document(document))
        doc_id = self._register_document(document)

        if self._open_paths_queue:
            if self._loading_dialog:
                remaining = len(self._open_paths_queue)
                suffix = "s" if remaining != 1 else ""
                self._loading_dialog.set_message(
                    f"Loaded {path.name}. {remaining} file{suffix} remaining…"
                )
            self._load_next_open_path()
            return

        self._pending_open_doc_id = doc_id
        if self._loading_dialog:
            driver_count = len(document.profiles())
            self._loading_dialog.set_message(
                f"Building driver list for {path.name} ({driver_count} drivers)…"
            )
        self.driver_panel.set_document(
            document,
            progress=self._loading_dialog.set_message if self._loading_dialog else None,
            finished=self._finish_open_sequence,
        )

    def _on_document_load_failed(self, message: str, path: Path) -> None:
        self._cleanup_load_thread()
        if self._open_paths_queue and self._open_paths_queue[0] == path:
            self._open_paths_queue.pop(0)
        logger.warning("Failed to open %s: %s", path, message)
        QMessageBox.warning(self, "Open Failed", f"{path.name}: {message}")
        if self._open_paths_queue:
            self._load_next_open_path()
            return
        self._finish_open_sequence()

    def _finish_open_sequence(self) -> None:
        doc_id = self._pending_open_doc_id
        self._pending_open_doc_id = None
        self._open_paths_queue = []
        self._finish_loading_dialog()

        if doc_id:
            document = self._documents.get(doc_id)
            self._apply_active_document(doc_id, sync_panel=False)
            if document:
                self.statusBar().showMessage(f"Opened {document.display_name}", 3000)

    def save_active(self) -> bool:
        """Validate and store the current document state in memory."""
        document = self._active_document()
        if not document:
            return False
        errors = validate_document(document)
        if errors:
            warn_validation_errors(self, errors)
            return False
        document.commit_saved_state(serialize_document(document))
        self._refresh_save_state()
        self.statusBar().showMessage(f"Saved {document.display_name}", 3000)
        logger.info("Internally saved document: %s", document.display_name)
        return True

    def export_ai_xml(self) -> bool:
        """Write the active document to an AI XML file on disk."""
        document = self._active_document()
        if not document:
            return False
        default_name = document.path.name if document.path else "custom_ai.xml"
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Export AI XML File",
            default_name,
            "XML Files (*.xml)",
        )
        if not path_str:
            return False
        return self._export_document_to_path(document, Path(path_str))

    def _export_document_to_path(self, document: AIDocument, path: Path) -> bool:
        errors = validate_document(document)
        if errors:
            warn_validation_errors(self, errors)
            return False
        try:
            save_document(document, path)
            document.commit_saved_state(serialize_document(document))
        except OSError as exc:
            logger.exception("Export failed: %s", path)
            QMessageBox.critical(self, "Export Failed", str(exc))
            return False
        self._refresh_save_state()
        self.statusBar().showMessage(f"Exported {path.name}", 3000)
        logger.info("Exported document: %s", path)
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

        errors = validate_document(document)
        if errors:
            warn_validation_errors(self, errors)
            return False

        if document.path:
            target = Path(folder) / document.path.name
        else:
            target = Path(folder) / "custom_ai.xml"
        try:
            target.write_text(serialize_document(document), encoding="utf-8")
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
        profile = DriverProfile(base=DriverEntry())
        profile.base.mode = "smart"
        randomize_new_driver(profile.base)
        document.add_profile(profile)
        self._refresh_after_profile_change(profile.profile_id)

    def remove_driver(self, profile_id: str) -> None:
        document = self._active_document()
        if not document:
            return
        document.remove_profile(profile_id)
        self._sync_driver_panel()
        self._refresh_save_state()
        self.statusBar().showMessage("Driver removed", 2000)

    def duplicate_driver(self, profile_id: str) -> None:
        document = self._active_document()
        if not document:
            return
        cloned = document.duplicate_profile(profile_id)
        if cloned:
            self._refresh_after_profile_change(cloned.profile_id)

    def _refresh_after_profile_change(self, profile_id: str) -> None:
        self._sync_driver_panel(expand_profile_id=profile_id)
        self._refresh_save_state()

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

        self._apply_active_document(doc_id, sync_panel=True)

    def _apply_active_document(
        self,
        doc_id: str,
        *,
        sync_panel: bool = True,
        expand_profile_id: str | None = None,
    ) -> None:
        self._active_doc_id = doc_id
        self.sidebar.set_active_document(doc_id)
        document = self._active_document()
        self.driver_panel.setEnabled(document is not None)
        if sync_panel:
            self._populate_driver_panel(document, expand_profile_id=expand_profile_id)
        title = document.display_name if document else "No file"
        self.setWindowTitle(f"AMS2 AI Creator v{__version__} — {title}")
        self._refresh_save_state()

    def _refresh_save_state(self) -> None:
        has_document = self._active_document() is not None
        self.save_btn.setEnabled(has_document)
        self.export_xml_btn.setEnabled(has_document)
        self.sidebar.refresh_file_labels()

    def _on_driver_edited(self) -> None:
        document = self._active_document()
        if document:
            document.mark_dirty()
            self.driver_panel.refresh_titles()
            self._refresh_save_state()

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
