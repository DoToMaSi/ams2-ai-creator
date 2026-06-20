"""Main panel with collapsible driver editors."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver import DriverEntry
from ams2_ai.ui.collapsible_section import CollapsibleSection
from ams2_ai.ui.driver_editor import DriverEditor


class DriverAccordionPanel(QWidget):
    """Scrollable accordion list of driver editors for the active document."""

    driverChanged = Signal()
    addDriverRequested = Signal()
    addOverrideRequested = Signal()
    removeDriverRequested = Signal(str)
    duplicateDriverRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._document: AIDocument | None = None
        self._sections: dict[str, CollapsibleSection] = {}
        self._editors: dict[str, DriverEditor] = {}

        root = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Drivers"))
        toolbar.addStretch()
        add_driver_btn = QPushButton("+ Driver")
        add_driver_btn.clicked.connect(self.addDriverRequested.emit)
        toolbar.addWidget(add_driver_btn)
        add_override_btn = QPushButton("+ Override")
        add_override_btn.clicked.connect(self.addOverrideRequested.emit)
        toolbar.addWidget(add_override_btn)
        root.addLayout(toolbar)

        self.empty_label = QLabel("No drivers yet. Add a driver or open an XML file.")
        self.empty_label.setStyleSheet("color: gray; padding: 16px;")
        root.addWidget(self.empty_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        root.addWidget(self.scroll, stretch=1)

    def set_document(
        self,
        document: AIDocument | None,
        *,
        expand_entry_id: str | None = None,
    ) -> None:
        self._clear_sections()
        self._document = document

        if not document or not document.drivers:
            self.empty_label.setVisible(True)
            self.scroll.setVisible(False)
            return

        self.empty_label.setVisible(False)
        self.scroll.setVisible(True)

        for driver in document.drivers:
            self._add_section(driver, expanded=driver.entry_id == expand_entry_id)

        if expand_entry_id is None and document.drivers:
            first = self._sections.get(document.drivers[0].entry_id)
            if first:
                first.set_expanded(True)

    def refresh_titles(self) -> None:
        if not self._document:
            return
        for driver in self._document.drivers:
            section = self._sections.get(driver.entry_id)
            if section:
                section.set_title(self._section_title(driver))

    def expand_driver(self, entry_id: str) -> None:
        section = self._sections.get(entry_id)
        if section:
            section.set_expanded(True)

    def current_driver_id(self) -> str | None:
        for entry_id, section in self._sections.items():
            if section.is_expanded():
                return entry_id
        if self._document and self._document.drivers:
            return self._document.drivers[0].entry_id
        return None

    def _section_title(self, driver: DriverEntry) -> str:
        suffix = " (track override)" if driver.is_track_override else ""
        return f"{driver.display_name()}{suffix}"

    def _add_section(self, driver: DriverEntry, *, expanded: bool = False) -> None:
        editor = DriverEditor()
        editor.set_driver(driver)
        editor.driverChanged.connect(lambda _eid=driver.entry_id: self._on_editor_changed(_eid))

        section_widget = QWidget()
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(4, 4, 4, 8)
        section_layout.addWidget(editor)

        action_row = QHBoxLayout()
        action_row.addStretch()
        dup_btn = QPushButton("Duplicate")
        dup_btn.clicked.connect(
            lambda _checked=False, eid=driver.entry_id: self.duplicateDriverRequested.emit(eid)
        )
        action_row.addWidget(dup_btn)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(
            lambda _checked=False, eid=driver.entry_id: self.removeDriverRequested.emit(eid)
        )
        action_row.addWidget(remove_btn)
        section_layout.addLayout(action_row)

        section = CollapsibleSection(self._section_title(driver), section_widget)
        section.set_expanded(expanded)

        self._sections[driver.entry_id] = section
        self._editors[driver.entry_id] = editor
        self.scroll_layout.addWidget(section)

    def _on_editor_changed(self, entry_id: str) -> None:
        section = self._sections.get(entry_id)
        if self._document:
            driver = self._document.get_driver(entry_id)
            if driver and section:
                section.set_title(self._section_title(driver))
        self.driverChanged.emit()

    def _clear_sections(self) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._sections.clear()
        self._editors.clear()
