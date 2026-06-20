"""Driver list and full-height editor panel."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver_profile import DriverProfile
from ams2_ai.ui.collapsible_section import CollapsibleSection
from ams2_ai.ui.driver_editor import DriverEditor


class DriverAccordionPanel(QWidget):
    """Compact driver list above a shared full-height editor."""

    driverChanged = Signal()
    addDriverRequested = Signal()
    removeDriverRequested = Signal(str)
    duplicateDriverRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._document: AIDocument | None = None
        self._active_profile_id: str | None = None
        self._sections: dict[str, CollapsibleSection] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("Drivers"))
        toolbar.addStretch()
        add_driver_btn = QPushButton("+ Driver")
        add_driver_btn.clicked.connect(self.addDriverRequested.emit)
        toolbar.addWidget(add_driver_btn)
        root.addLayout(toolbar)

        self.empty_label = QLabel("No drivers yet. Add a driver or open an XML file.")
        self.empty_label.setStyleSheet("color: gray; padding: 16px;")
        root.addWidget(self.empty_label)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.list_scroll = QScrollArea()
        self.list_scroll.setWidgetResizable(True)
        self.list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_content = QWidget()
        self.list_layout = QVBoxLayout(self.list_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_scroll.setWidget(self.list_content)
        self.splitter.addWidget(self.list_scroll)

        self.editor = DriverEditor()
        self.editor.driverChanged.connect(self._on_editor_changed)
        self.splitter.addWidget(self.editor)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([180, 720])
        root.addWidget(self.splitter, stretch=1)

        self.editor_container = self.splitter
        self.editor_container.setVisible(False)

    def set_document(
        self,
        document: AIDocument | None,
        *,
        expand_profile_id: str | None = None,
    ) -> None:
        self._clear_sections()
        self._document = document
        self._active_profile_id = None

        if not document or not document.profiles():
            self.empty_label.setVisible(True)
            self.editor_container.setVisible(False)
            self.editor.set_profile(None, None)
            return

        self.empty_label.setVisible(False)
        self.editor_container.setVisible(True)

        for index, profile in enumerate(document.profiles(), start=1):
            self._add_section(profile, index=index)

        selected_id = expand_profile_id
        if selected_id is None:
            profiles = document.profiles()
            if profiles:
                selected_id = profiles[0].profile_id

        if selected_id:
            self._select_profile(selected_id)

    def refresh_titles(self) -> None:
        if not self._document:
            return
        for index, profile in enumerate(self._document.profiles(), start=1):
            section = self._sections.get(profile.profile_id)
            if section:
                section.set_index(index)
                section.set_title(profile.display_name())

    def current_profile_id(self) -> str | None:
        return self._active_profile_id

    def _add_section(self, profile: DriverProfile, *, index: int = 1) -> None:
        dup_btn = QPushButton("Duplicate")
        dup_btn.clicked.connect(
            lambda _checked=False, pid=profile.profile_id: self.duplicateDriverRequested.emit(pid)
        )
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(
            lambda _checked=False, pid=profile.profile_id: self.removeDriverRequested.emit(pid)
        )

        section = CollapsibleSection(
            profile.display_name(),
            index=index,
            header_actions=[dup_btn, remove_btn],
        )
        section.toggled.connect(
            lambda expanded, pid=profile.profile_id: self._on_section_toggled(pid, expanded)
        )

        self._sections[profile.profile_id] = section
        self.list_layout.addWidget(section)

    def _on_section_toggled(self, profile_id: str, expanded: bool) -> None:
        if expanded:
            self._select_profile(profile_id)
            return

        if self._active_profile_id == profile_id:
            section = self._sections.get(profile_id)
            if section:
                section.set_expanded(True)

    def _select_profile(self, profile_id: str) -> None:
        if not self._document:
            return

        profile = self._document.get_profile(profile_id)
        if profile is None:
            return

        self._active_profile_id = profile_id
        for pid, section in self._sections.items():
            section.set_expanded(pid == profile_id)

        self.editor.set_profile(profile, self._document)

    def _on_editor_changed(self) -> None:
        if self._document and self._active_profile_id:
            profile = self._document.get_profile(self._active_profile_id)
            section = self._sections.get(self._active_profile_id)
            if profile and section:
                section.set_title(profile.display_name())
        self.driverChanged.emit()

    def _clear_sections(self) -> None:
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._sections.clear()
