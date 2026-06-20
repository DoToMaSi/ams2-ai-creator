"""Group base drivers and per-track overrides for the UI."""

from __future__ import annotations

from dataclasses import dataclass, field

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import NUMERIC_KEYS


@dataclass
class DriverProfile:
    """One livery: global (base) settings plus optional per-track overrides."""

    base: DriverEntry
    track_overrides: list[DriverEntry] = field(default_factory=list)

    @property
    def profile_id(self) -> str:
        return self.base.entry_id

    def all_entries(self) -> list[DriverEntry]:
        return [self.base] + self.track_overrides

    def display_name(self) -> str:
        name = self.base.display_name()
        if self.track_overrides:
            return f"{name} (+{len(self.track_overrides)} track(s))"
        return name

    def sync_livery_to_overrides(self) -> None:
        for override in self.track_overrides:
            override.livery_name = self.base.livery_name

    def add_track(self, track_name: str) -> DriverEntry | None:
        track_name = track_name.strip()
        if not track_name:
            return None
        if any(o.tracks == track_name for o in self.track_overrides):
            return None
        entry = DriverEntry(
            livery_name=self.base.livery_name,
            tracks=track_name,
            is_track_override=True,
            mode="custom",
        )
        self.track_overrides.append(entry)
        return entry

    def remove_track(self, entry_id: str) -> None:
        self.track_overrides = [o for o in self.track_overrides if o.entry_id != entry_id]

    def clone(self) -> DriverProfile:
        cloned_base = self.base.clone()
        cloned_overrides = []
        for override in self.track_overrides:
            cloned = override.clone()
            cloned.livery_name = cloned_base.livery_name
            cloned_overrides.append(cloned)
        return DriverProfile(base=cloned_base, track_overrides=cloned_overrides)


def normalize_document_drivers(drivers: list[DriverEntry]) -> list[DriverEntry]:
    """Split comma-separated track attributes into separate entries in the document."""
    normalized: list[DriverEntry] = []
    for driver in drivers:
        tracks = [t.strip() for t in driver.tracks.split(",") if t.strip()]
        if len(tracks) <= 1:
            if tracks:
                driver.tracks = tracks[0]
                driver.is_track_override = True
            normalized.append(driver)
            continue
        for track in tracks:
            clone = driver.clone()
            clone.tracks = track
            clone.is_track_override = True
            normalized.append(clone)
    return normalized


def group_drivers(drivers: list[DriverEntry]) -> list[DriverProfile]:
    profiles: list[DriverProfile] = []
    livery_to_profile: dict[str, DriverProfile] = {}

    for entry in drivers:
        if entry.tracks.strip():
            profile = livery_to_profile.get(entry.livery_name)
            if profile is None:
                base = DriverEntry(livery_name=entry.livery_name, mode="custom")
                profile = DriverProfile(base=base, track_overrides=[entry])
                profiles.append(profile)
                livery_to_profile[entry.livery_name] = profile
            else:
                profile.track_overrides.append(entry)
            continue

        profile = DriverProfile(base=entry, track_overrides=[])
        profiles.append(profile)
        livery_to_profile[entry.livery_name] = profile

    return profiles


def track_override_has_overrides(entry: DriverEntry) -> bool:
    numeric = any(key in entry.set_fields for key in NUMERIC_KEYS)
    return numeric


def flatten_profiles(profiles: list[DriverProfile]) -> list[DriverEntry]:
    flat: list[DriverEntry] = []
    for profile in profiles:
        flat.append(profile.base)
        for override in profile.track_overrides:
            if track_override_has_overrides(override):
                flat.append(override)
    return flat


def replace_profile_entries(document_drivers: list[DriverEntry], profile: DriverProfile) -> None:
    remove_ids = {profile.base.entry_id, *(o.entry_id for o in profile.track_overrides)}
    kept = [d for d in document_drivers if d.entry_id not in remove_ids]
    kept.extend(flatten_profiles([profile]))
    document_drivers[:] = kept
