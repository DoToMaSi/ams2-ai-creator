"""Parse AMS2 override _dist.xml templates."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BaseLiverySpec:
    name: str
    description: str = ""
    texture_names: list[str] = field(default_factory=list)


@dataclass
class DistMetadata:
    car_id: str
    base_liveries: list[BaseLiverySpec] = field(default_factory=list)
    helmet_bases: list[str] = field(default_factory=list)
    helmet_texture_names: list[str] = field(default_factory=list)


_BASE_LIVERY_LINE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9]*)\s*:\s*(.*)$")
_TEXTURE_LINE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s+-")
_HELMET_BASE = re.compile(r"BASEHELMET\s*=\s*[\"'](\w+)[\"']", re.IGNORECASE)
_HELMET_TEXTURE = re.compile(r'<TEXTURE\s+NAME="(\w+)"', re.IGNORECASE)

DEFAULT_HELMET_BASES = ("DEFAULT",)
DEFAULT_HELMET_TEXTURES = ("HELMET",)


def parse_dist_file(path: Path, *, car_id: str | None = None) -> DistMetadata:
    text = path.read_text(encoding="utf-8")
    folder_id = car_id or path.parent.name
    if folder_id.endswith("_dist"):
        folder_id = folder_id[: -len("_dist")]
    if path.stem.endswith("_dist"):
        folder_id = path.stem[: -len("_dist")]

    base_liveries = _parse_base_liveries(text)
    helmet_bases, helmet_textures = _parse_helmet_metadata(text)

    if not base_liveries:
        base_liveries = [BaseLiverySpec(name="Default", texture_names=["BODY", "WINDSCREEN"])]

    return DistMetadata(
        car_id=folder_id,
        base_liveries=base_liveries,
        helmet_bases=helmet_bases or list(DEFAULT_HELMET_BASES),
        helmet_texture_names=helmet_textures or list(DEFAULT_HELMET_TEXTURES),
    )


def _parse_base_liveries(text: str) -> list[BaseLiverySpec]:
    section = _extract_section(text, "AVAILABLE BASE LIVERIES")
    if not section:
        return []

    liveries: list[BaseLiverySpec] = []
    current: BaseLiverySpec | None = None
    in_textures = False

    for line in section.splitlines():
        if "Available textures" in line:
            in_textures = True
            continue

        base_match = _BASE_LIVERY_LINE.match(line)
        if base_match:
            if current is not None:
                liveries.append(current)
            current = BaseLiverySpec(
                name=base_match.group(1),
                description=base_match.group(2).strip(),
            )
            in_textures = False
            continue

        if in_textures and current is not None:
            texture_match = _TEXTURE_LINE.match(line)
            if texture_match:
                name = texture_match.group(1)
                if name not in current.texture_names:
                    current.texture_names.append(name)
            elif line.strip() and not line.strip().startswith("-"):
                in_textures = False

    if current is not None:
        liveries.append(current)

    return liveries


def _parse_helmet_metadata(text: str) -> tuple[list[str], list[str]]:
    bases = list(dict.fromkeys(_HELMET_BASE.findall(text)))
    textures = list(dict.fromkeys(_HELMET_TEXTURE.findall(text)))

    helmet_section = _extract_section(text, "HELMET")
    if helmet_section:
        for line in helmet_section.splitlines():
            texture_match = _TEXTURE_LINE.match(line)
            if texture_match:
                name = texture_match.group(1)
                if name not in textures:
                    textures.append(name)

    return bases, textures


def _extract_section(text: str, marker: str) -> str:
    upper = text.upper()
    marker_upper = marker.upper()
    start = upper.find(marker_upper)
    if start < 0:
        return ""
    tail = text[start + len(marker) :]
    end_markers = ("EXAMPLES", "<!--", "</USER_OVERRIDES>")
    end = len(tail)
    for end_marker in end_markers:
        idx = tail.upper().find(end_marker.upper())
        if idx >= 0:
            end = min(end, idx)
    return tail[:end]
