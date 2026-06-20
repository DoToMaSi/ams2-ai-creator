"""Main panel with collapsible driver profile editors."""

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
from ams2_ai.models.driver_profile import DriverProfile
from ams2_ai.ui.collapsible_section import CollapsibleSection
from ams2_ai.ui.driver_editor import DriverEditor


class DriverAccordionPanel(QWidget):
    """Scrollable accordion list of driver profile editors."""

    driverChanged = Signal()
    addDriverRequested = Signal()
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
        expand_profile_id: str | None = None,
    ) -> None:
        self._clear_sections()
        self._document = document

        if not document or not document.profiles():
            self.empty_label.setVisible(True)
            self.scroll.setVisible(False)
            return

        self.empty_label.setVisible(False)
        self.scroll.setVisible(True)

        for index, profile in enumerate(document.profiles(), start=1):
            expanded = profile.profile_id == expand_profile_id
            self._add_section(profile, index=index, expanded=expanded)

        if expand_profile_id is None:
            profiles = document.profiles()
            if profiles:
                first = self._sections.get(profiles[0].profile_id)
                if first:
                    first.set_expanded(True)

    def refresh_titles(self) -> None:
        if not self._document:
            return
        for index, profile in enumerate(self._document.profiles(), start=1):
            section = self._sections.get(profile.profile_id)
            if section:
                section.set_index(index)
                section.set_title(profile.display_name())

    def current_profile_id(self) -> str | None:
        for profile_id, section in self._sections.items():
            if section.is_expanded():
                return profile_id
        profiles = self._document.profiles() if self._document else []
        if profiles:
            return profiles[0].profile_id
        return None

    def _add_section(
        self,
        profile: DriverProfile,
        *,
        index: int = 1,
        expanded: bool = False,
    ) -> None:
        editor = DriverEditor()
        editor.set_profile(profile, self._document)
        editor.driverChanged.connect(lambda _pid=profile.profile_id: self._on_editor_changed(_pid))

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
            editor,
            index=index,
            header_actions=[dup_btn, remove_btn],
        )
        section.set_expanded(expanded)

        self._sections[profile.profile_id] = section
        self._editors[profile.profile_id] = editor
        self.scroll_layout.addWidget(section)

    def _on_editor_changed(self, profile_id: str) -> None:
        section = self._sections.get(profile_id)
        if self._document:
            profile = self._document.get_profile(profile_id)
            if profile and section:
                section.set_title(profile.display_name())
        self.driverChanged.emit()

    def _clear_sections(self) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._sections.clear()
        self._editors.clear()
