"""Editor for one livery slot (car livery + helmet)."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ams2_shared.ui.theme import SPACING_INNER, SPACING_SECTION
from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.models.livery_slot import LiverySlot
from ams2_skins.models.texture import TextureRef


class TextureRow(QWidget):
    pathChanged = Signal()

    def __init__(self, texture_name: str, parent=None):
        super().__init__(parent)
        self.texture_name = texture_name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING_INNER)

        layout.addWidget(QLabel(texture_name))
        self.path_edit = QLineEdit()
        self.path_edit.textChanged.connect(self.pathChanged.emit)
        layout.addWidget(self.path_edit, stretch=1)

        browse_btn = QPushButton("Browse…")
        browse_btn.clicked.connect(self._browse)
        layout.addWidget(browse_btn)
        self._browse_callback = None

    def set_browse_callback(self, callback) -> None:
        self._browse_callback = callback

    def _browse(self) -> None:
        if self._browse_callback:
            path = self._browse_callback()
            if path:
                self.path_edit.setText(path)

    def set_path(self, path: str) -> None:
        self.path_edit.blockSignals(True)
        self.path_edit.setText(path)
        self.path_edit.blockSignals(False)

    def path(self) -> str:
        return self.path_edit.text().strip()


class LiverySlotEditor(QWidget):
    slotChanged = Signal()
    removeRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slot: LiverySlot | None = None
        self._catalog_entry: VehicleCatalogEntry | None = None
        self._texture_rows: dict[str, TextureRow] = {}
        self._helmet_rows: dict[str, TextureRow] = {}
        self._loading = False

        layout = QVBoxLayout(self)
        margins = SPACING_SECTION
        layout.setContentsMargins(margins, margins, margins, margins)
        layout.setSpacing(SPACING_SECTION)

        header = QHBoxLayout()
        self.title_label = QLabel("Livery Slot")
        self.title_label.setObjectName("sectionTitle")
        header.addWidget(self.title_label)
        header.addStretch()
        remove_btn = QPushButton("Remove Slot")
        remove_btn.clicked.connect(self.removeRequested.emit)
        header.addWidget(remove_btn)
        layout.addLayout(header)

        form = QFormLayout()
        self.id_label = QLabel("")
        form.addRow("Livery ID:", self.id_label)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self._emit_changed)
        form.addRow("Display Name:", self.name_edit)
        self.base_livery_combo = QComboBox()
        self.base_livery_combo.currentTextChanged.connect(self._on_base_livery_changed)
        form.addRow("Base Livery:", self.base_livery_combo)
        layout.addLayout(form)

        preview_row = QHBoxLayout()
        preview_row.addWidget(QLabel("Preview Image"))
        self.preview_edit = QLineEdit()
        self.preview_edit.textChanged.connect(self._emit_changed)
        preview_row.addWidget(self.preview_edit, stretch=1)
        preview_browse = QPushButton("Browse…")
        preview_browse.clicked.connect(lambda: self._pick_file(self.preview_edit))
        preview_row.addWidget(preview_browse)
        layout.addLayout(preview_row)
        layout.addWidget(QLabel("Preview: 2048×600 DDS for in-game UI (optional but recommended)."))

        textures_group = QGroupBox("Car Textures")
        self.textures_layout = QVBoxLayout(textures_group)
        layout.addWidget(textures_group)

        helmet_group = QGroupBox("Helmet Override")
        helmet_layout = QVBoxLayout(helmet_group)
        self.helmet_enabled = QCheckBox("Enable helmet override for this livery")
        self.helmet_enabled.toggled.connect(self._on_helmet_toggled)
        helmet_layout.addWidget(self.helmet_enabled)

        helmet_form = QFormLayout()
        self.base_helmet_combo = QComboBox()
        self.base_helmet_combo.currentTextChanged.connect(self._emit_changed)
        helmet_form.addRow("Base Helmet:", self.base_helmet_combo)
        helmet_layout.addLayout(helmet_form)

        self.helmet_textures_layout = QVBoxLayout()
        helmet_layout.addLayout(self.helmet_textures_layout)
        layout.addWidget(helmet_group)
        layout.addStretch()

    def set_catalog_entry(self, entry: VehicleCatalogEntry | None) -> None:
        self._catalog_entry = entry

    def set_slot(self, slot: LiverySlot) -> None:
        self._loading = True
        self._slot = slot
        self.title_label.setText(slot.display_title)
        self.id_label.setText(str(slot.livery.livery_id))
        self.name_edit.setText(slot.livery.name)
        self.preview_edit.setText(slot.livery.preview_path)

        self.base_livery_combo.blockSignals(True)
        self.base_livery_combo.clear()
        if self._catalog_entry:
            for spec in self._catalog_entry.base_liveries:
                self.base_livery_combo.addItem(spec.name)
        else:
            self.base_livery_combo.addItem(slot.livery.base_livery or "Default")
        index = self.base_livery_combo.findText(slot.livery.base_livery)
        if index >= 0:
            self.base_livery_combo.setCurrentIndex(index)
        self.base_livery_combo.blockSignals(False)

        self._rebuild_texture_rows(slot.livery.base_livery, slot.livery.textures)

        self.base_helmet_combo.blockSignals(True)
        self.base_helmet_combo.clear()
        helmet_bases = self._catalog_entry.helmet_bases if self._catalog_entry else ["DEFAULT"]
        for base in helmet_bases:
            self.base_helmet_combo.addItem(base)
        helmet_index = self.base_helmet_combo.findText(slot.helmet.base_helmet)
        if helmet_index >= 0:
            self.base_helmet_combo.setCurrentIndex(helmet_index)
        self.base_helmet_combo.blockSignals(False)

        self.helmet_enabled.blockSignals(True)
        self.helmet_enabled.setChecked(slot.helmet.enabled)
        self.helmet_enabled.blockSignals(False)
        self._rebuild_helmet_rows(slot.helmet.textures)
        self._update_helmet_enabled_state()
        self._loading = False

    def collect_slot(self) -> LiverySlot | None:
        if self._slot is None:
            return None
        slot = self._slot
        slot.livery.name = self.name_edit.text()
        slot.livery.base_livery = self.base_livery_combo.currentText()
        slot.livery.preview_path = self.preview_edit.text().strip()
        slot.livery.textures = [
            TextureRef(name=name, path=row.path())
            for name, row in self._texture_rows.items()
            if row.path()
        ]
        slot.helmet.enabled = self.helmet_enabled.isChecked()
        slot.helmet.base_helmet = self.base_helmet_combo.currentText()
        slot.helmet.textures = [
            TextureRef(name=name, path=row.path())
            for name, row in self._helmet_rows.items()
            if row.path()
        ]
        slot.livery.name = self.name_edit.text()
        return slot

    def _on_base_livery_changed(self, base_livery: str) -> None:
        if self._loading or self._slot is None:
            return
        existing = {texture.name: texture.path for texture in self._slot.livery.textures}
        textures = [
            TextureRef(name=name, path=existing.get(name, ""))
            for name in self._texture_names_for_base(base_livery)
        ]
        self._rebuild_texture_rows(base_livery, textures)
        self._emit_changed()

    def _texture_names_for_base(self, base_livery: str) -> list[str]:
        if self._catalog_entry:
            return self._catalog_entry.texture_names_for_base(base_livery)
        return ["BODY", "WINDSCREEN"]

    def _rebuild_texture_rows(self, base_livery: str, textures: list[TextureRef]) -> None:
        while self.textures_layout.count():
            item = self.textures_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._texture_rows.clear()

        by_name = {texture.name: texture.path for texture in textures}
        for name in self._texture_names_for_base(base_livery):
            row = TextureRow(name)
            row.set_path(by_name.get(name, ""))
            row.set_browse_callback(lambda n=name: self._browse_texture(n, car=True))
            row.pathChanged.connect(self._emit_changed)
            self.textures_layout.addWidget(row)
            self._texture_rows[name] = row

    def _rebuild_helmet_rows(self, textures: list[TextureRef]) -> None:
        while self.helmet_textures_layout.count():
            item = self.helmet_textures_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._helmet_rows.clear()

        names = self._catalog_entry.helmet_texture_names if self._catalog_entry else ["HELMET"]
        by_name = {texture.name: texture.path for texture in textures}
        for name in names:
            row = TextureRow(name)
            row.set_path(by_name.get(name, ""))
            row.set_browse_callback(lambda n=name: self._browse_texture(n, car=False))
            row.pathChanged.connect(self._emit_changed)
            self.helmet_textures_layout.addWidget(row)
            self._helmet_rows[name] = row

    def _on_helmet_toggled(self, _checked: bool) -> None:
        self._update_helmet_enabled_state()
        self._emit_changed()

    def _update_helmet_enabled_state(self) -> None:
        enabled = self.helmet_enabled.isChecked()
        self.base_helmet_combo.setEnabled(enabled)
        for row in self._helmet_rows.values():
            row.setEnabled(enabled)

    def _pick_file(self, target: QLineEdit) -> None:
        path = self._browse_texture("", car=True, allow_any=True)
        if path:
            target.setText(path)

    def _browse_texture(self, _name: str, *, car: bool, allow_any: bool = False) -> str | None:
        from PySide6.QtWidgets import QFileDialog

        start_dir = ""
        if self._slot and self._catalog_entry is None:
            pass
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Select DDS Texture",
            start_dir,
            "DDS Files (*.dds);;All Files (*.*)" if allow_any else "DDS Files (*.dds)",
        )
        if not path_str:
            return None
        return self._to_relative_path(path_str)

    def _to_relative_path(self, absolute_path: str) -> str:
        from pathlib import Path

        abs_path = Path(absolute_path)
        if self._slot is None:
            return abs_path.name
        # Relative path resolved by main window via car document
        self._pending_absolute = abs_path
        return abs_path.name

    def consume_pending_absolute(self):
        pending = getattr(self, "_pending_absolute", None)
        self._pending_absolute = None
        return pending

    def _emit_changed(self) -> None:
        if not self._loading:
            self.slotChanged.emit()
