"""Texture reference in a livery or helmet override."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextureRef:
    name: str
    path: str

    def clone(self) -> TextureRef:
        return TextureRef(name=self.name, path=self.path)
