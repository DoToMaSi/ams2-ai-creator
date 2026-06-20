"""Driver entry model."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any

from ams2_ai.models.parameters import NUMERIC_KEYS, ModeType


@dataclass
class DriverEntry:
    """One <driver> element in a custom AI XML file."""

    livery_name: str = ""
    tracks: str = ""
    name: str = ""
    country: str = ""
    values: dict[str, float] = field(default_factory=dict)
    set_fields: set[str] = field(default_factory=set)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mode: ModeType = "smart"
    is_track_override: bool = False

    def display_name(self) -> str:
        if self.name:
            base = self.name
        elif self.livery_name:
            base = self.livery_name
        else:
            base = "Unnamed Driver"
        if self.tracks:
            track_count = len([t for t in self.tracks.split(",") if t.strip()])
            return f"{base} [{track_count} track(s)]"
        return base

    def get_ui_value(self, key: str, default: int = 50) -> int:
        from ams2_ai.models.parameters import xml_to_ui

        if key in self.values:
            return xml_to_ui(key, self.values[key])
        return default

    def set_ui_value(self, key: str, ui_value: int | float) -> None:
        from ams2_ai.models.parameters import ui_to_xml

        self.values[key] = ui_to_xml(key, ui_value)
        self.set_fields.add(key)

    def set_xml_value(self, key: str, xml_value: float) -> None:
        self.values[key] = xml_value
        self.set_fields.add(key)

    def clear_field(self, key: str) -> None:
        self.values.pop(key, None)
        self.set_fields.discard(key)

    def get_skill_ui(self) -> int:
        return self.get_ui_value("race_skill", 50)

    def get_aggression_ui(self) -> int:
        return self.get_ui_value("aggression", 50)

    def clone(self) -> DriverEntry:
        cloned = copy.deepcopy(self)
        cloned.entry_id = str(uuid.uuid4())
        return cloned

    def to_export_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if self.name:
            data["name"] = self.name
        if self.country:
            data["country"] = self.country
        for key in NUMERIC_KEYS:
            if key in self.set_fields and key in self.values:
                data[key] = self.values[key]
        return data
