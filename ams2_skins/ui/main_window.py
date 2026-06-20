"""Skin Manager main window."""

from __future__ import annotations

import logging
import os
import shutil
from pathlib import Path

from PySide6.QtCore import QSettings, Qt, QThread
from PySide6.QtGui import QAction, QGuiApplication, QIcon, QKeySequence
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

from ams2_shared import __version__ as SUITE_VERSION
from ams2_shared.logging_config import get_log_dir
from ams2_shared.ui.theme import SPACING_INNER, SPACING_OUTER
from ams2_shared.util.assets import icon_ico_path, icon_png_path
from ams2_skins import __version__ as SKINS_VERSION
from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.export.skinpack import (
    export_car_xml,
    export_skinpack_to_ams2,
    export_skinpack_to_folder,
    load_skinpack_from_folder,
    scaffold_car_in_pack,
)
from ams2_skins.models.skinpack import SkinpackDocument
from ams2_skins.ui.catalog_worker import CatalogScanWorker
from ams2_skins.ui.dialogs import (
    CustomMaxLiveryDialog,
    PickCarDialog,
    PickLiverySlotDialog,
    confirm_export_with_warnings,
    confirm_unsaved,
    warn_validation_errors,
)
from ams2_skins.ui.livery_panel import LiveryPanel
from ams2_skins.ui.pack_sidebar import PackSidebar
from ams2_skins.ui.setup_bar import SetupBar
from ams2_skins.ui.validation_panel import ValidationPanel
from ams2_skins.validation import split_validation_messages, validate_skinpack
from ams2_skins.xml.writer import serialize_car_document

logger = logging.getLogger("ams2_skins.ui.main_window")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AMS2 Skin Manager v{SKINS_VERSION}")
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            self.setGeometry(screen.availableGeometry())
        else:
            self.resize(1400, 1000)
        self.setMinimumSize(1080, 800)
        for icon_path in (icon_ico_path(), icon_png_path()):
            if icon_path.is_file():
                self.setWindowIcon(QIcon(str(icon_path)))
                break

        self._settings = QSettings()
        self._pack = SkinpackDocument()
        self._active_car_id: str | None = None
        self._catalog: dict[str, VehicleCatalogEntry] = {}
        self._custom_max: dict[str, int] = {}
        self._scan_thread: QThread | None = None
        self._scan_worker: CatalogScanWorker | None = None

        self.setup_bar = SetupBar()
        self.sidebar = PackSidebar()
        self.livery_panel = LiveryPanel()
        self.validation_panel = ValidationPanel()

        center_splitter = QSplitter()
        center_splitter.addWidget(self.sidebar)
        center_splitter.addWidget(self.livery_panel)
        center_splitter.setStretchFactor(0, 0)
        center_splitter.setStretchFactor(1, 1)
        center_splitter.setSizes([280, 1120])

        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(self.validation_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 0)
        main_splitter.setSizes([820, 160])

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(SPACING_OUTER, SPACING_OUTER, SPACING_OUTER, SPACING_INNER)
        root_layout.setSpacing(SPACING_INNER)
        root_layout.addWidget(self.setup_bar)
        root_layout.addWidget(main_splitter, stretch=1)

        footer = QHBoxLayout()
        footer.addStretch()
        self.save_btn = QPushButton("Save")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setShortcut(QKeySequence.Save)
        self.save_btn.clicked.connect(self.save_active)
        footer.addWidget(self.save_btn)
        self.export_xml_btn = QPushButton("Export Skin XML")
        self.export_xml_btn.setObjectName("secondaryButton")
        self.export_xml_btn.clicked.connect(self.export_skin_xml)
        footer.addWidget(self.export_xml_btn)
        self.export_pack_btn = QPushButton("Export Skinpack")
        self.export_pack_btn.clicked.connect(self.export_skinpack)
        footer.addWidget(self.export_pack_btn)
        root_layout.addLayout(footer)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())
        self._build_menu()

        self.setup_bar.ams2BrowseRequested.connect(self.browse_ams2_root)
        self.setup_bar.rescanRequested.connect(self.rescan_catalog)
        self.setup_bar.openPackRequested.connect(self.open_skinpack)
        self.setup_bar.newPackRequested.connect(self.new_skinpack)
        self.sidebar.carSelected.connect(self.select_car)
        self.sidebar.addCarRequested.connect(self.add_car)
        self.sidebar.removeCarRequested.connect(self.remove_car)
        self.livery_panel.slotsChanged.connect(self._on_slots_changed)
        self.livery_panel.addSlotRequested.connect(self.add_livery_slot)
        self.livery_panel.setMaxLiveryRequested.connect(self.set_custom_max_livery)

        ams2_root = self._settings.value("ams2/root_dir", "")
        if ams2_root:
            self.setup_bar.set_ams2_path(str(ams2_root))
            self.rescan_catalog()

        self._refresh_ui()

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&File")
        export_ams2 = QAction("Export to AMS2…", self)
        export_ams2.triggered.connect(self.export_to_ams2)
        file_menu.addAction(export_ams2)
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu("&Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        log_action = QAction("Open Log Folder", self)
        log_action.triggered.connect(lambda: os.startfile(get_log_dir()))
        help_menu.addAction(log_action)

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "About AMS2 Skin Manager",
            (
                f"<b>AMS2 Skin Manager</b> v{SKINS_VERSION}<br>"
                f"Part of AMS2 Creator suite v{SUITE_VERSION}<br><br>"
                "Editor for Automobilista 2 custom livery override skinpacks."
            ),
        )

    def _catalog_entry_for(self, car_id: str) -> VehicleCatalogEntry | None:
        entry = self._catalog.get(car_id)
        if entry is None:
            return None
        if car_id in self._custom_max:
            entry = VehicleCatalogEntry(
                folder_id=entry.folder_id,
                xml_filename=entry.xml_filename,
                display_name=entry.display_name,
                dist_path=entry.dist_path,
                base_liveries=entry.base_liveries,
                helmet_bases=entry.helmet_bases,
                helmet_texture_names=entry.helmet_texture_names,
                min_livery_id=entry.min_livery_id,
                max_livery_id=self._custom_max[car_id],
                has_livery_limit=True,
            )
        return entry

    def browse_ams2_root(self) -> None:
        current = self._settings.value("ams2/root_dir", "")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Automobilista 2 Folder",
            str(current),
        )
        if not folder:
            return
        self._settings.setValue("ams2/root_dir", folder)
        self.setup_bar.set_ams2_path(folder)
        self.rescan_catalog()

    def rescan_catalog(self) -> None:
        ams2_root = self._settings.value("ams2/root_dir", "")
        if not ams2_root:
            QMessageBox.information(
                self,
                "AMS2 Path Required",
                "Select your AMS2 install folder first.",
            )
            return
        if self._scan_thread is not None:
            return
        self.statusBar().showMessage("Scanning AMS2 Overrides catalog…")
        self._scan_worker = CatalogScanWorker(Path(str(ams2_root)))
        self._scan_thread = QThread()
        self._scan_worker.moveToThread(self._scan_thread)
        self._scan_thread.started.connect(self._scan_worker.run)
        self._scan_worker.finished_scan.connect(self._on_catalog_scanned)
        self._scan_worker.failed.connect(self._on_catalog_failed)
        self._scan_worker.finished_scan.connect(self._scan_thread.quit)
        self._scan_worker.failed.connect(self._scan_thread.quit)
        self._scan_thread.finished.connect(self._cleanup_scan)
        self._scan_thread.start()

    def _cleanup_scan(self) -> None:
        if self._scan_worker:
            self._scan_worker.deleteLater()
            self._scan_worker = None
        if self._scan_thread:
            self._scan_thread.deleteLater()
            self._scan_thread = None

    def _on_catalog_scanned(self, entries: list) -> None:
        self._catalog = {entry.folder_id: entry for entry in entries}
        self.statusBar().showMessage(f"Catalog: {len(entries)} vehicles", 5000)
        self._refresh_ui()

    def _on_catalog_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Catalog Scan Failed", message)
        self.statusBar().clearMessage()

    def new_skinpack(self) -> None:
        if self._pack.dirty and not confirm_unsaved(self, self._pack.display_name):
            return
        folder = QFileDialog.getExistingDirectory(self, "Choose Skinpack Root Folder")
        if not folder:
            return
        root = Path(folder)
        self._pack = SkinpackDocument(root_path=root, name=root.name)
        self._active_car_id = None
        self._refresh_ui()

    def open_skinpack(self) -> None:
        if self._pack.dirty and not confirm_unsaved(self, self._pack.display_name):
            return
        folder = QFileDialog.getExistingDirectory(self, "Open Skinpack Folder")
        if not folder:
            return
        root = Path(folder)
        self._pack = load_skinpack_from_folder(root)
        self._pack.name = root.name
        self._active_car_id = self._pack.cars[0].car_id if self._pack.cars else None
        self._refresh_ui()

    def add_car(self) -> None:
        if self._pack.root_path is None:
            QMessageBox.information(self, "No Skinpack", "Create or open a skinpack first.")
            return
        if not self._catalog:
            QMessageBox.information(
                self,
                "No Catalog",
                "Scan your AMS2 install before adding cars.",
            )
            return
        exclude = {car.car_id for car in self._pack.cars}
        dialog = PickCarDialog(list(self._catalog.values()), exclude=exclude, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        entry = dialog.selected_entry()
        if entry is None:
            return
        dist_source = Path(entry.dist_path) if entry.dist_path else None
        car = scaffold_car_in_pack(self._pack.root_path, entry.folder_id, dist_source=dist_source)
        self._pack.add_car(car)
        self._active_car_id = car.car_id
        self._refresh_ui()

    def remove_car(self, car_id: str) -> None:
        if (
            QMessageBox.question(
                self,
                "Remove Car",
                f"Remove {car_id} from this skinpack?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._pack.remove_car(car_id)
        if self._active_car_id == car_id:
            self._active_car_id = self._pack.cars[0].car_id if self._pack.cars else None
        self._refresh_ui()

    def select_car(self, car_id: str) -> None:
        self.livery_panel._flush_editor()
        self._active_car_id = car_id
        self._refresh_car_panel()

    def add_livery_slot(self) -> None:
        car = self._active_car()
        if car is None:
            return
        entry = self._catalog_entry_for(car.car_id)
        max_id = entry.max_livery_id if entry and entry.has_livery_limit else None
        if entry and not entry.has_livery_limit:
            QMessageBox.warning(
                self,
                "Max Livery ID Required",
                "Set a max livery ID for this car before adding slots.",
            )
            return
        used = {slot.livery.livery_id for slot in car.slots()}
        dialog = PickLiverySlotDialog(min_id=51, max_id=max_id, used_ids=used, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        livery_id = dialog.livery_id()
        if livery_id in used:
            QMessageBox.warning(self, "Duplicate ID", f"Livery ID {livery_id} is already used.")
            return
        base = entry.base_liveries[0].name if entry and entry.base_liveries else "Default"
        car.add_slot(livery_id, base_livery=base)
        self._pack.mark_dirty()
        self.livery_panel.refresh_after_external_change()
        self._update_validation()

    def set_custom_max_livery(self) -> None:
        car = self._active_car()
        if car is None:
            return
        entry = self._catalog_entry_for(car.car_id)
        current = entry.max_livery_id if entry else None
        dialog = CustomMaxLiveryDialog(car.car_id, current=current, parent=self)
        if dialog.exec() != dialog.DialogCode.Accepted:
            return
        self._custom_max[car.car_id] = dialog.max_livery_id()
        self._refresh_car_panel()
        self._update_validation()

    def _on_slots_changed(self) -> None:
        self._pack.mark_dirty()
        self._update_validation()

    def _active_car(self):
        if self._active_car_id is None:
            return None
        return self._pack.get_car(self._active_car_id)

    def _refresh_car_panel(self) -> None:
        car = self._active_car()
        entry = self._catalog_entry_for(car.car_id) if car else None
        self.livery_panel.set_car(car, entry)

    def _refresh_ui(self) -> None:
        self.sidebar.set_pack_name(self._pack.display_name)
        self.sidebar.set_cars(self._pack.cars, active_car_id=self._active_car_id)
        if self._pack.cars and self._active_car_id is None:
            self._active_car_id = self._pack.cars[0].car_id
        self._refresh_car_panel()
        self._update_validation()
        self.save_btn.setEnabled(bool(self._pack.cars))

    def _pack_catalog(self) -> dict[str, VehicleCatalogEntry]:
        catalog = {car.car_id: self._catalog_entry_for(car.car_id) for car in self._pack.cars}
        return {key: value for key, value in catalog.items() if value is not None}

    def _validate_pack(self, *, check_files: bool = False) -> tuple[list[str], list[str]]:
        return split_validation_messages(
            validate_skinpack(self._pack, catalog=self._pack_catalog(), check_files=check_files)
        )

    def _update_validation(self) -> None:
        catalog = {car_id: self._catalog_entry_for(car_id) for car_id in self._catalog}
        catalog = {k: v for k, v in catalog.items() if v is not None}
        messages = validate_skinpack(self._pack, catalog=catalog, check_files=True)
        self.validation_panel.set_messages(messages or ["No validation issues."])

    def save_active(self) -> bool:
        self.livery_panel._flush_editor()
        errors, _warnings = self._validate_pack()
        if errors:
            warn_validation_errors(self, errors)
            return False
        for car in self._pack.cars:
            if car.xml_path:
                content = serialize_car_document(car)
                car.commit_saved_state(content)
        self._pack.mark_clean()
        self.statusBar().showMessage("Saved (in memory)", 3000)
        return True

    def export_skin_xml(self) -> bool:
        self.livery_panel._flush_editor()
        car = self._active_car()
        if car is None or car.xml_path is None:
            return False
        entry = self._catalog_entry_for(car.car_id)
        from ams2_skins.validation import validate_car_document

        messages = validate_car_document(car, catalog_entry=entry, check_files=True)
        errors, warnings = split_validation_messages(messages)
        if errors:
            warn_validation_errors(self, errors)
            return False
        if warnings and not confirm_export_with_warnings(self, warnings):
            return False
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Export Skin XML",
            str(car.xml_path),
            "XML Files (*.xml)",
        )
        if not path_str:
            return False
        try:
            export_car_xml(car)
            if Path(path_str) != car.xml_path:
                shutil.copy2(car.xml_path, path_str)
            car.commit_saved_state(serialize_car_document(car))
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            return False
        self.statusBar().showMessage(f"Exported {Path(path_str).name}", 3000)
        return True

    def export_skinpack(self) -> bool:
        self.livery_panel._flush_editor()
        if not self._pack.root_path:
            return False
        errors, warnings = self._validate_pack(check_files=True)
        if errors:
            warn_validation_errors(self, errors)
            return False
        if warnings and not confirm_export_with_warnings(self, warnings):
            return False
        for car in self._pack.cars:
            export_car_xml(car)
        folder = QFileDialog.getExistingDirectory(
            self,
            "Export Skinpack To Folder",
            str(self._pack.root_path),
        )
        if not folder:
            return False
        target_root = Path(folder)
        try:
            export_skinpack_to_folder(self._pack, target_root)
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            return False
        self._pack.mark_clean()
        self.statusBar().showMessage(f"Exported skinpack to {target_root}", 5000)
        return True

    def export_to_ams2(self) -> bool:
        self.livery_panel._flush_editor()
        ams2_root = self._settings.value("ams2/root_dir", "")
        if not ams2_root:
            self.browse_ams2_root()
            ams2_root = self._settings.value("ams2/root_dir", "")
        if not ams2_root:
            return False
        errors, warnings = self._validate_pack(check_files=True)
        if errors:
            warn_validation_errors(self, errors)
            return False
        if warnings and not confirm_export_with_warnings(self, warnings):
            return False
        if (
            QMessageBox.question(
                self,
                "Export to AMS2",
                "Copy skinpack car folders into your AMS2 Overrides directory?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return False
        for car in self._pack.cars:
            export_car_xml(car)
        try:
            export_skinpack_to_ams2(self._pack, Path(str(ams2_root)))
        except OSError as exc:
            QMessageBox.critical(self, "Export Failed", str(exc))
            return False
        self._pack.mark_clean()
        self.statusBar().showMessage("Exported to AMS2 Overrides", 5000)
        return True

    def closeEvent(self, event) -> None:
        if self._pack.dirty:
            if not confirm_unsaved(self, self._pack.display_name):
                event.ignore()
                return
        super().closeEvent(event)
