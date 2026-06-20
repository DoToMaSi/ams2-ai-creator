"""Serialize AMS2 custom AI driver XML files."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

from ams2_ai.models.document import AIDocument
from ams2_ai.models.parameters import format_xml_value

logger = logging.getLogger("ams2_ai.xml.writer")

ROOT_TAG = "custom_ai_drivers"
DRIVER_TAG = "driver"


def serialize_document(document: AIDocument) -> str:
    """Build valid AI XML text in memory without writing a file."""
    root = ET.Element(ROOT_TAG)

    for driver in document.drivers:
        attrs: dict[str, str] = {"livery_name": driver.livery_name}
        if driver.tracks.strip():
            attrs["tracks"] = driver.tracks.strip()
        driver_el = ET.SubElement(root, DRIVER_TAG, attrs)

        if "name" in driver.set_fields and driver.name:
            name_el = ET.SubElement(driver_el, "name")
            name_el.text = driver.name
        if "country" in driver.set_fields and driver.country:
            country_el = ET.SubElement(driver_el, "country")
            country_el.text = driver.country

        for key in sorted(driver.set_fields):
            if key in {"name", "country", "livery_name", "tracks"}:
                continue
            if key not in driver.values:
                continue
            child = ET.SubElement(driver_el, key)
            child.text = format_xml_value(key, driver.values[key])

    xml_body = ET.tostring(root, encoding="unicode")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    if document.header_comment:
        lines.append(f"<!--{document.header_comment}-->")
    lines.append(xml_body)
    return "\n".join(lines) + "\n"


def save_document(document: AIDocument, path: Path) -> None:
    logger.info("Saving document: %s (%d drivers)", path, len(document.drivers))
    path.write_text(serialize_document(document), encoding="utf-8")
    document.path = path
    document.sync_header_comment()
    logger.info("Saved document: %s", path)
