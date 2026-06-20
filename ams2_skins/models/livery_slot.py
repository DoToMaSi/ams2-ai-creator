"""Group livery and helmet overrides for one livery slot."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from ams2_skins.models.livery_override import HelmetOverride, LiveryOverride


@dataclass
class LiverySlot:
    livery: LiveryOverride
    helmet: HelmetOverride
    slot_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def create(cls, livery_id: int, *, base_livery: str = "Default") -> LiverySlot:
        livery = LiveryOverride(livery_id=livery_id, base_livery=base_livery)
        helmet = HelmetOverride(livery_id=livery_id, enabled=False)
        return cls(livery=livery, helmet=helmet)

    @property
    def display_title(self) -> str:
        name = self.livery.name.strip()
        if name:
            return f"#{self.livery.livery_id} {name}"
        return f"Livery {self.livery.livery_id}"

    def clone(self) -> LiverySlot:
        return LiverySlot(
            livery=self.livery.clone(),
            helmet=self.helmet.clone(),
            slot_id=str(uuid.uuid4()),
        )


def build_slots(
    liveries: list[LiveryOverride],
    helmets: list[HelmetOverride],
) -> list[LiverySlot]:
    helmet_by_id = {helmet.livery_id: helmet for helmet in helmets}
    slots: list[LiverySlot] = []
    for livery in sorted(liveries, key=lambda item: item.livery_id):
        helmet = helmet_by_id.get(livery.livery_id)
        if helmet is None:
            helmet = HelmetOverride(livery_id=livery.livery_id, enabled=False)
        else:
            helmet = HelmetOverride(
                livery_id=helmet.livery_id,
                base_helmet=helmet.base_helmet,
                textures=[texture.clone() for texture in helmet.textures],
                enabled=True,
                entry_id=helmet.entry_id,
            )
        slots.append(LiverySlot(livery=livery, helmet=helmet))
    return slots


def flatten_slots(slots: list[LiverySlot]) -> tuple[list[LiveryOverride], list[HelmetOverride]]:
    liveries = [slot.livery for slot in slots]
    helmets = [slot.helmet for slot in slots if slot.helmet.enabled and slot.helmet.textures]
    return liveries, helmets
