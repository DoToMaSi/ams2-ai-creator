"""AI document model — one XML file with multiple drivers."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path

from ams2_ai.models.driver import DriverEntry


@dataclass
class AIDocument:
    path: Path | None = None
    drivers: list[DriverEntry] = field(default_factory=list)
    header_comment: str = ""
    dirty: bool = False

    @property
    def display_name(self) -> str:
        if self.path:
            return self.path.name
        return "Untitled.xml"

    def mark_clean(self) -> None:
        self.dirty = False

    def mark_dirty(self) -> None:
        self.dirty = True

    def add_driver(self, driver: DriverEntry | None = None) -> DriverEntry:
        entry = driver or DriverEntry()
        self.drivers.append(entry)
        self.mark_dirty()
        return entry

    def remove_driver(self, entry_id: str) -> None:
        self.drivers = [d for d in self.drivers if d.entry_id != entry_id]
        self.mark_dirty()

    def get_driver(self, entry_id: str) -> DriverEntry | None:
        for driver in self.drivers:
            if driver.entry_id == entry_id:
                return driver
        return None

    def duplicate_driver(self, entry_id: str) -> DriverEntry | None:
        driver = self.get_driver(entry_id)
        if not driver:
            return None
        cloned = driver.clone()
        self.drivers.append(cloned)
        self.mark_dirty()
        return cloned

    def clone(self) -> AIDocument:
        return copy.deepcopy(self)
