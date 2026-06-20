"""Livery and helmet override entries."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from ams2_skins.models.texture import TextureRef


@dataclass
class LiveryOverride:
    livery_id: int
    name: str = ""
    base_livery: str = "Default"
    preview_path: str = ""
    textures: list[TextureRef] = field(default_factory=list)
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def clone(self) -> LiveryOverride:
        return LiveryOverride(
            livery_id=self.livery_id,
            name=self.name,
            base_livery=self.base_livery,
            preview_path=self.preview_path,
            textures=[texture.clone() for texture in self.textures],
            entry_id=str(uuid.uuid4()),
        )


@dataclass
class HelmetOverride:
    livery_id: int
    base_helmet: str = "DEFAULT"
    textures: list[TextureRef] = field(default_factory=list)
    enabled: bool = False
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def clone(self) -> HelmetOverride:
        return HelmetOverride(
            livery_id=self.livery_id,
            base_helmet=self.base_helmet,
            textures=[texture.clone() for texture in self.textures],
            enabled=self.enabled,
            entry_id=str(uuid.uuid4()),
        )
