"""AI document model — one XML file with multiple drivers."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.driver_profile import (
    DriverProfile,
    flatten_profiles,
    group_drivers,
    replace_profile_entries,
)
from ams2_ai.models.header_meta import HeaderMeta, build_header_comment, parse_header_comment


@dataclass
class AIDocument:
    path: Path | None = None
    drivers: list[DriverEntry] = field(default_factory=list)
    header_comment: str = ""
    set_name: str = ""
    vehicle_class: str = ""
    custom_class_name: str = ""
    header_comment_body: str = ""
    dirty: bool = False
    saved_xml: str | None = field(default=None, repr=False, compare=False)
    _profiles: list[DriverProfile] | None = field(default=None, repr=False, compare=False)

    def invalidate_profiles(self) -> None:
        self._profiles = None

    def profiles(self) -> list[DriverProfile]:
        if self._profiles is None:
            self._profiles = group_drivers(self.drivers)
        return self._profiles

    @property
    def display_name(self) -> str:
        filename = self.path.name if self.path else "Untitled.xml"
        label = self.set_name.strip() or self._set_name_from_comment()
        if label:
            return f"{label} ({filename})"
        return filename

    def _set_name_from_comment(self) -> str:
        meta = parse_header_comment(self.header_comment)
        return meta.name

    def apply_header_meta(self, *, path_stem: str = "") -> None:
        """Load structured header fields and infer class from filename when needed."""
        meta = parse_header_comment(self.header_comment)
        self.set_name = meta.name
        self.vehicle_class = meta.vehicle_class or path_stem
        self.custom_class_name = meta.custom_class_name
        self.header_comment_body = meta.body

    def header_meta(self) -> HeaderMeta:
        return HeaderMeta(
            name=self.set_name.strip(),
            vehicle_class=self.vehicle_class.strip(),
            custom_class_name=self.custom_class_name.strip(),
            body=self.header_comment_body.strip(),
        )

    def sync_header_comment(self) -> None:
        """Write document metadata into the XML header comment."""
        self.header_comment = build_header_comment(self.header_meta())

    def effective_filename(self) -> str:
        """Return the export filename for this document."""
        if self.custom_class_name.strip():
            filename = self.custom_class_name.strip()
        elif self.vehicle_class.strip():
            filename = self.vehicle_class.strip()
        elif self.path:
            return self.path.name
        else:
            return "custom_ai.xml"
        if not filename.lower().endswith(".xml"):
            filename = f"{filename}.xml"
        return filename

    def mark_clean(self) -> None:
        self.dirty = False

    def commit_saved_state(self, xml_content: str) -> None:
        """Store a validated XML snapshot and clear the dirty flag."""
        self.saved_xml = xml_content
        self.mark_clean()

    def mark_dirty(self) -> None:
        self.dirty = True
        self.invalidate_profiles()

    def get_profile(self, profile_id: str) -> DriverProfile | None:
        for profile in self.profiles():
            if profile.profile_id == profile_id:
                return profile
        return None

    def replace_profile(self, profile: DriverProfile) -> None:
        replace_profile_entries(self.drivers, profile)
        self.mark_dirty()

    def remove_profile(self, profile_id: str) -> None:
        profile = self.get_profile(profile_id)
        if not profile:
            return
        remove_ids = {profile.base.entry_id, *(o.entry_id for o in profile.track_overrides)}
        self.drivers = [d for d in self.drivers if d.entry_id not in remove_ids]
        self.mark_dirty()

    def duplicate_profile(self, profile_id: str) -> DriverProfile | None:
        profile = self.get_profile(profile_id)
        if not profile:
            return None
        cloned = profile.clone()
        self.drivers.extend(flatten_profiles([cloned]))
        self.mark_dirty()
        return cloned

    def add_profile(self, profile: DriverProfile | None = None) -> DriverProfile:
        if profile is None:
            profile = DriverProfile(base=DriverEntry())
        self.drivers.extend(flatten_profiles([profile]))
        self.mark_dirty()
        return profile

    def clone(self) -> AIDocument:
        return copy.deepcopy(self)
