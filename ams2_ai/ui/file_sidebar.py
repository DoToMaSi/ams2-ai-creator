"""Left sidebar with open files and driver list."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.models.document import AIDocument


class FileSidebar(QWidget):
    documentSelected = Signal(str)
    driverSelected = Signal(str)
    addDocumentRequested = Signal()
    addDriverRequested = Signal()
    addOverrideRequested = Signal()
    removeDriverRequested = Signal()
    duplicateDriverRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._documents: dict[str, AIDocument] = {}
        self._active_doc_id: str | None = None

        layout = QVBoxLayout(self)

        files_header = QHBoxLayout()
        files_header.addWidget(QLabel("XML Files"))
        files_header.addStretch()
        open_btn = QPushButton("+ Open")
        open_btn.clicked.connect(self.addDocumentRequested.emit)
        files_header.addWidget(open_btn)
        layout.addLayout(files_header)

        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self._on_file_changed)
        layout.addWidget(self.file_list, stretch=1)

        drivers_header = QHBoxLayout()
        drivers_header.addWidget(QLabel("Drivers"))
        drivers_header.addStretch()
        layout.addLayout(drivers_header)

        driver_btn_row = QHBoxLayout()
        add_driver_btn = QPushButton("+ Driver")
        add_driver_btn.clicked.connect(self.addDriverRequested.emit)
        driver_btn_row.addWidget(add_driver_btn)
        add_override_btn = QPushButton("+ Override")
        add_override_btn.clicked.connect(self.addOverrideRequested.emit)
        driver_btn_row.addWidget(add_override_btn)
        layout.addLayout(driver_btn_row)

        self.driver_list = QListWidget()
        self.driver_list.currentItemChanged.connect(self._on_driver_changed)
        layout.addWidget(self.driver_list, stretch=1)

        action_row = QHBoxLayout()
        dup_btn = QPushButton("Duplicate")
        dup_btn.clicked.connect(self.duplicateDriverRequested.emit)
        action_row.addWidget(dup_btn)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.removeDriverRequested.emit)
        action_row.addWidget(remove_btn)
        layout.addLayout(action_row)

    def set_documents(self, documents: dict[str, AIDocument]) -> None:
        self._documents = documents
        self.file_list.blockSignals(True)
        self.file_list.clear()
        for doc_id, document in documents.items():
            item = QListWidgetItem(self._file_label(document))
            item.setData(256, doc_id)
            self.file_list.addItem(item)
            if doc_id == self._active_doc_id:
                self.file_list.setCurrentItem(item)
        self.file_list.blockSignals(False)
        self.refresh_drivers()

    def set_active_document(self, doc_id: str | None) -> None:
        self._active_doc_id = doc_id
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.data(256) == doc_id:
                self.file_list.setCurrentItem(item)
                break
        self.refresh_drivers()

    def refresh_drivers(self) -> None:
        self.driver_list.blockSignals(True)
        self.driver_list.clear()
        document = self._documents.get(self._active_doc_id or "", None)
        if document:
            for driver in document.drivers:
                item = QListWidgetItem(driver.display_name())
                item.setData(256, driver.entry_id)
                if driver.is_track_override:
                    item.setToolTip(driver.tracks)
                self.driver_list.addItem(item)
        self.driver_list.blockSignals(False)

    def refresh_file_labels(self) -> None:
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            doc_id = item.data(256)
            document = self._documents.get(doc_id)
            if document:
                item.setText(self._file_label(document))

    def select_driver(self, entry_id: str | None) -> None:
        if not entry_id:
            return
        for index in range(self.driver_list.count()):
            item = self.driver_list.item(index)
            if item.data(256) == entry_id:
                self.driver_list.setCurrentItem(item)
                break

    def current_document_id(self) -> str | None:
        item = self.file_list.currentItem()
        return item.data(256) if item else None

    def current_driver_id(self) -> str | None:
        item = self.driver_list.currentItem()
        return item.data(256) if item else None

    def _file_label(self, document: AIDocument) -> str:
        suffix = " *" if document.dirty else ""
        return f"{document.display_name}{suffix}"

    def _on_file_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current:
            self.documentSelected.emit(current.data(256))

    def _on_driver_changed(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None,
    ) -> None:
        if current:
            self.driverSelected.emit(current.data(256))
