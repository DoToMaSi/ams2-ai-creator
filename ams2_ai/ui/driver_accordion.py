"""Driver list and full-height editor panel."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ams2_ai.models.document import AIDocument
from ams2_ai.ui.theme import SPACING_INNER, SPACING_OUTER, SPACING_SECTION
from ams2_ai.models.driver_profile import DriverProfile
from ams2_ai.ui.collapsible_section import CollapsibleSection
from ams2_ai.ui.driver_editor import DriverEditor
from ams2_ai.ui.icons import duplicate_icon
from ams2_ai.ui.xml_properties_panel import XmlPropertiesPanel

BUILD_BATCH_SIZE = 30
SYNC_BUILD_THRESHOLD = 25


class DriverAccordionPanel(QWidget):
    """Compact driver list above a shared full-height editor."""

    driverChanged = Signal()
    documentPropertiesChanged = Signal()
    addDriverRequested = Signal()
    removeDriverRequested = Signal(str)
    duplicateDriverRequested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._document: AIDocument | None = None
        self._active_profile_id: str | None = None
        self._sections: dict[str, CollapsibleSection] = {}
        self._build_queue: list[tuple[int, DriverProfile]] = []
        self._build_total = 0
        self._expand_profile_id: str | None = None
        self._progress: Callable[[str], None] | None = None
        self._finished: Callable[[], None] | None = None
        self._build_timer = QTimer(self)
        self._build_timer.timeout.connect(self._build_next_batch)

        root = QVBoxLayout(self)
        root.setContentsMargins(SPACING_INNER, SPACING_INNER, SPACING_INNER, SPACING_INNER)
        root.setSpacing(SPACING_SECTION)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.xml_properties = XmlPropertiesPanel()
        self.xml_properties.propertiesChanged.connect(self.documentPropertiesChanged.emit)
        root.addWidget(self.xml_properties, 0)

        self.drivers_toolbar = QWidget()
        toolbar = QHBoxLayout(self.drivers_toolbar)
        toolbar.setContentsMargins(SPACING_INNER, 0, SPACING_INNER, 0)
        self.drivers_label = QLabel("Drivers")
        self.drivers_label.setObjectName("sectionTitle")
        toolbar.addWidget(self.drivers_label)
        toolbar.addStretch()
        self.add_driver_btn = QPushButton("+ Driver")
        self.add_driver_btn.clicked.connect(self.addDriverRequested.emit)
        toolbar.addWidget(self.add_driver_btn)
        root.addWidget(self.drivers_toolbar, 0)

        self.empty_label = QLabel("No drivers yet. Add a driver or open an XML file.")
        self.empty_label.setObjectName("mutedLabel")
        self.empty_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.empty_label.setContentsMargins(
            SPACING_SECTION, SPACING_INNER, SPACING_SECTION, SPACING_INNER
        )
        self.empty_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        root.addWidget(self.empty_label, 0)

        self.splitter = QSplitter(Qt.Orientation.Vertical)

        self.list_scroll = QScrollArea()
        self.list_scroll.setWidgetResizable(True)
        self.list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_content = QWidget()
        self.list_layout = QVBoxLayout(self.list_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.list_scroll.setWidget(self.list_content)
        self.list_scroll.setMinimumHeight(200)
        self.splitter.addWidget(self.list_scroll)

        self.editor = DriverEditor()
        self.editor.driverChanged.connect(self._on_editor_changed)
        self.splitter.addWidget(self.editor)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([200, 760])
        root.addWidget(self.splitter, stretch=1)

        self.editor_container = self.splitter
        self.editor_container.setVisible(False)
        self.drivers_toolbar.setVisible(False)
        self.empty_label.setVisible(False)

    def _make_driver_action_buttons(self, profile_id: str) -> list[QToolButton]:
        style = QApplication.style()
        if style is None:
            style = self.style()

        dup_btn = QToolButton()
        dup_btn.setObjectName("compactActionButton")
        dup_btn.setIcon(duplicate_icon(20))
        dup_btn.setToolTip("Duplicate driver")
        dup_btn.setFixedSize(34, 34)
        dup_btn.clicked.connect(
            lambda _checked=False, pid=profile_id: self.duplicateDriverRequested.emit(pid)
        )

        remove_btn = QToolButton()
        remove_btn.setObjectName("compactActionButton")
        remove_btn.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
        remove_btn.setToolTip("Remove driver")
        remove_btn.setFixedSize(34, 34)
        remove_btn.clicked.connect(
            lambda _checked=False, pid=profile_id: self.removeDriverRequested.emit(pid)
        )
        return [dup_btn, remove_btn]

    def _set_document_ui_visible(self, document: AIDocument | None) -> None:
        has_document = document is not None
        self.xml_properties.setVisible(has_document)
        self.drivers_toolbar.setVisible(has_document)

    def set_document(
        self,
        document: AIDocument | None,
        *,
        expand_profile_id: str | None = None,
        progress: Callable[[str], None] | None = None,
        finished: Callable[[], None] | None = None,
    ) -> None:
        self._stop_build()
        self._clear_sections()
        self._document = document
        self._active_profile_id = None
        self._progress = progress
        self._finished = finished
        self._expand_profile_id = expand_profile_id
        self._set_document_ui_visible(document)
        self.xml_properties.set_document(document)

        if document is None:
            self.empty_label.setVisible(False)
            self.editor_container.setVisible(False)
            self.editor.set_profile(None, None)
            self._emit_finished()
            return

        if not document.profiles():
            self.empty_label.setVisible(True)
            self.editor_container.setVisible(False)
            self.editor.set_profile(None, None)
            self._emit_finished()
            return

        self.empty_label.setVisible(False)
        self.editor_container.setVisible(True)

        profiles = document.profiles()
        if len(profiles) <= SYNC_BUILD_THRESHOLD:
            for index, profile in enumerate(profiles, start=1):
                self._add_section(profile, index=index)
            self._finish_set_document()
            return

        self._build_total = len(profiles)
        self._build_queue = [(index, profile) for index, profile in enumerate(profiles, start=1)]
        self._report_progress(f"Building driver list (0/{self._build_total})…")
        self._build_timer.start(0)

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

    def _stop_build(self) -> None:
        self._build_timer.stop()
        self._build_queue.clear()
        self._progress = None
        self._finished = None

    def _build_next_batch(self) -> None:
        for _ in range(BUILD_BATCH_SIZE):
            if not self._build_queue:
                self._build_timer.stop()
                self._finish_set_document()
                return
            index, profile = self._build_queue.pop(0)
            self._add_section(profile, index=index)

        done = self._build_total - len(self._build_queue)
        self._report_progress(f"Building driver list ({done}/{self._build_total})…")
        QApplication.processEvents()

    def _finish_set_document(self) -> None:
        selected_id = self._expand_profile_id
        if selected_id is None and self._document:
            profiles = self._document.profiles()
            if profiles:
                selected_id = profiles[0].profile_id

        if selected_id:
            self._select_profile(selected_id)

        self._emit_finished()

    def _emit_finished(self) -> None:
        if self._finished:
            callback = self._finished
            self._finished = None
            self._progress = None
            callback()

    def _report_progress(self, message: str) -> None:
        if self._progress:
            self._progress(message)

    def _add_section(self, profile: DriverProfile, *, index: int = 1) -> None:
        actions = self._make_driver_action_buttons(profile.profile_id)

        section = CollapsibleSection(
            profile.display_name(),
            index=index,
            header_actions=actions,
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
        self._scroll_to_profile(profile_id)

    def _scroll_to_profile(self, profile_id: str) -> None:
        section = self._sections.get(profile_id)
        if section is None:
            return

        def scroll() -> None:
            self.list_scroll.ensureWidgetVisible(section, 50, 50)

        QTimer.singleShot(0, scroll)

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
