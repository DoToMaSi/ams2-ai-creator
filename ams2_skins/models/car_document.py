"""One car override XML document."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path

from ams2_skins.models.livery_override import HelmetOverride, LiveryOverride
from ams2_skins.models.livery_slot import LiverySlot, build_slots, flatten_slots


@dataclass
class CarOverrideDocument:
    car_id: str
    folder_path: Path | None = None
    xml_path: Path | None = None
    liveries: list[LiveryOverride] = field(default_factory=list)
    helmets: list[HelmetOverride] = field(default_factory=list)
    dirty: bool = False
    saved_xml: str | None = field(default=None, repr=False, compare=False)
    _slots: list[LiverySlot] | None = field(default=None, repr=False, compare=False)

    @property
    def display_name(self) -> str:
        return self.car_id

    def slots(self) -> list[LiverySlot]:
        if self._slots is None:
            self._slots = build_slots(self.liveries, self.helmets)
        return self._slots

    def invalidate_slots(self) -> None:
        self._slots = None

    def replace_slots(self, slots: list[LiverySlot]) -> None:
        self.liveries, self.helmets = flatten_slots(slots)
        self._slots = copy.deepcopy(slots)
        self.dirty = True

    def add_slot(self, livery_id: int, *, base_livery: str = "Default") -> LiverySlot:
        slot = LiverySlot.create(livery_id, base_livery=base_livery)
        slots = self.slots()
        slots.append(slot)
        self.replace_slots(slots)
        return slot

    def remove_slot(self, slot_id: str) -> None:
        slots = [slot for slot in self.slots() if slot.slot_id != slot_id]
        self.replace_slots(slots)

    def get_slot(self, slot_id: str) -> LiverySlot | None:
        for slot in self.slots():
            if slot.slot_id == slot_id:
                return slot
        return None

    def mark_dirty(self) -> None:
        self.dirty = True
        self.invalidate_slots()

    def mark_clean(self) -> None:
        self.dirty = False

    def commit_saved_state(self, xml_content: str) -> None:
        self.saved_xml = xml_content
        self.mark_clean()

    @property
    def xml_directory(self) -> Path | None:
        if self.xml_path:
            return self.xml_path.parent
        if self.folder_path:
            return self.folder_path
        return None

    def resolve_texture_path(self, relative_path: str) -> Path | None:
        base = self.xml_directory
        if not base or not relative_path.strip():
            return None
        return (base / relative_path.replace("\\", "/")).resolve()
