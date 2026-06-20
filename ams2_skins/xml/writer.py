"""Write AMS2 livery override XML files."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.livery_override import HelmetOverride, LiveryOverride

logger = logging.getLogger("ams2_skins.xml.writer")

ROOT_TAG = "USER_OVERRIDES"
INDENT = "    "


def serialize_car_document(document: CarOverrideDocument) -> str:
    root = ET.Element(ROOT_TAG)

    for livery in sorted(document.liveries, key=lambda item: item.livery_id):
        root.append(_build_livery_element(livery))

    for helmet in sorted(document.helmets, key=lambda item: item.livery_id):
        if helmet.textures:
            root.append(_build_helmet_element(helmet))

    ET.indent(root, space=INDENT)
    lines = ['<?xml version="1.0" encoding="utf-8" ?>', ET.tostring(root, encoding="unicode")]
    return "\n".join(lines) + "\n"


def save_car_document(document: CarOverrideDocument, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = serialize_car_document(document)
    path.write_text(content, encoding="utf-8")
    logger.info("Saved car override: %s", path)


def _build_livery_element(livery: LiveryOverride) -> ET.Element:
    element = ET.Element(
        "LIVERY_OVERRIDE",
        {
            "LIVERY": str(livery.livery_id),
            "NAME": livery.name,
            "BASELIVERY": livery.base_livery,
        },
    )
    if livery.preview_path.strip():
        ET.SubElement(element, "PREVIEWIMAGE", {"PATH": livery.preview_path.strip()})
    for texture in livery.textures:
        if texture.path.strip():
            ET.SubElement(
                element,
                "TEXTURE",
                {"NAME": texture.name, "PATH": texture.path.strip()},
            )
    return element


def _build_helmet_element(helmet: HelmetOverride) -> ET.Element:
    element = ET.Element(
        "HELMET_OVERRIDE",
        {
            "LIVERY": str(helmet.livery_id),
            "BASEHELMET": helmet.base_helmet,
        },
    )
    for texture in helmet.textures:
        if texture.path.strip():
            ET.SubElement(
                element,
                "TEXTURE",
                {"NAME": texture.name, "PATH": texture.path.strip()},
            )
    return element
