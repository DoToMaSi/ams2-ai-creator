"""Vehicle catalog entry from AMS2 Overrides scan."""

from __future__ import annotations

from dataclasses import dataclass, field

from ams2_skins.xml.dist_parser import BaseLiverySpec


@dataclass
class VehicleCatalogEntry:
    folder_id: str
    xml_filename: str
    display_name: str
    dist_path: str
    base_liveries: list[BaseLiverySpec] = field(default_factory=list)
    helmet_bases: list[str] = field(default_factory=list)
    helmet_texture_names: list[str] = field(default_factory=list)
    min_livery_id: int = 51
    max_livery_id: int | None = None
    has_livery_limit: bool = False

    def texture_names_for_base(self, base_livery: str) -> list[str]:
        for spec in self.base_liveries:
            if spec.name == base_livery:
                return list(spec.texture_names)
        if self.base_liveries:
            return list(self.base_liveries[0].texture_names)
        return ["BODY", "WINDSCREEN"]

    def sort_key(self) -> tuple[str, str]:
        return (self.display_name.lower(), self.folder_id.lower())
