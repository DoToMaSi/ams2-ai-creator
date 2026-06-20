"""Left sidebar listing open XML files."""

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
    newDocumentRequested = Signal()
    openDocumentRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._documents: dict[str, AIDocument] = {}
        self._active_doc_id: str | None = None

        layout = QVBoxLayout(self)

        files_header = QHBoxLayout()
        files_header.addWidget(QLabel("XML Files"))
        files_header.addStretch()
        new_btn = QPushButton("+ New")
        new_btn.clicked.connect(self.newDocumentRequested.emit)
        files_header.addWidget(new_btn)
        open_btn = QPushButton("+ Open")
        open_btn.clicked.connect(self.openDocumentRequested.emit)
        files_header.addWidget(open_btn)
        layout.addLayout(files_header)

        self.file_list = QListWidget()
        self.file_list.currentItemChanged.connect(self._on_file_changed)
        layout.addWidget(self.file_list, stretch=1)

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

    def set_active_document(self, doc_id: str | None) -> None:
        self._active_doc_id = doc_id
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.data(256) == doc_id:
                self.file_list.setCurrentItem(item)
                break

    def refresh_file_labels(self) -> None:
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            doc_id = item.data(256)
            document = self._documents.get(doc_id)
            if document:
                item.setText(self._file_label(document))

    def current_document_id(self) -> str | None:
        item = self.file_list.currentItem()
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
