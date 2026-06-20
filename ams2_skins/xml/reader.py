"""Read AMS2 livery override XML files."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.livery_override import HelmetOverride, LiveryOverride
from ams2_skins.models.texture import TextureRef

logger = logging.getLogger("ams2_skins.xml.reader")

ROOT_TAG = "USER_OVERRIDES"


def load_car_document(path: Path, *, car_id: str | None = None) -> CarOverrideDocument:
    tree = ET.parse(path)
    root = tree.getroot()
    if root.tag != ROOT_TAG:
        raise ValueError(f"Expected root tag {ROOT_TAG!r}, got {root.tag!r}")

    folder_id = car_id or path.stem
    if folder_id.endswith("_dist"):
        folder_id = folder_id[: -len("_dist")]

    liveries: list[LiveryOverride] = []
    helmets: list[HelmetOverride] = []

    for element in root:
        tag = element.tag.upper()
        if tag == "LIVERY_OVERRIDE":
            liveries.append(_parse_livery(element))
        elif tag == "HELMET_OVERRIDE":
            helmets.append(_parse_helmet(element))

    doc = CarOverrideDocument(
        car_id=folder_id,
        folder_path=path.parent,
        xml_path=path,
        liveries=liveries,
        helmets=helmets,
    )
    logger.debug("Loaded %s with %d liveries", path.name, len(liveries))
    return doc


def _parse_livery(element: ET.Element) -> LiveryOverride:
    livery_id = int(element.get("LIVERY", "0"))
    override = LiveryOverride(
        livery_id=livery_id,
        name=element.get("NAME", ""),
        base_livery=element.get("BASELIVERY", "Default"),
    )
    for child in element:
        tag = child.tag.upper()
        if tag == "PREVIEWIMAGE":
            override.preview_path = child.get("PATH", "")
        elif tag == "TEXTURE":
            override.textures.append(
                TextureRef(name=child.get("NAME", ""), path=child.get("PATH", ""))
            )
    return override


def _parse_helmet(element: ET.Element) -> HelmetOverride:
    livery_id = int(element.get("LIVERY", "0"))
    override = HelmetOverride(
        livery_id=livery_id,
        base_helmet=element.get("BASEHELMET", "DEFAULT"),
        enabled=True,
    )
    for child in element:
        if child.tag.upper() == "TEXTURE":
            override.textures.append(
                TextureRef(name=child.get("NAME", ""), path=child.get("PATH", ""))
            )
    return override
