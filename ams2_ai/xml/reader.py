"""Parse AMS2 custom AI driver XML files."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ams2_ai.models.document import AIDocument
from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.driver_profile import normalize_document_drivers
from ams2_ai.models.parameters import PARAMETER_BY_KEY

logger = logging.getLogger("ams2_ai.xml.reader")

TEXT_FIELDS = {"name", "country"}
DRIVER_TAG = "driver"
ROOT_TAG = "custom_ai_drivers"


def _extract_header_comment(text: str) -> str:
    match = re.search(r"<!--([\s\S]*?)-->", text)
    if match and match.start() < text.find(f"<{ROOT_TAG}"):
        return match.group(1).strip()
    return ""


def _strip_xml_comments(text: str) -> str:
    """Remove XML comments so malformed comment bodies do not break parsing."""
    return re.sub(r"<!--[\s\S]*?-->", "", text)


def load_document(path: Path) -> AIDocument:
    logger.info("Loading document: %s", path)
    raw_text = path.read_text(encoding="utf-8")
    header_comment = _extract_header_comment(raw_text)
    parse_text = _strip_xml_comments(raw_text)

    try:
        root = ET.fromstring(parse_text)
    except ET.ParseError as exc:
        logger.exception("Failed to parse XML: %s", path)
        raise ValueError(f"Invalid XML in {path.name}: {exc}") from exc

    if root.tag != ROOT_TAG:
        raise ValueError(f"Expected root element <{ROOT_TAG}>, got <{root.tag}>")

    document = AIDocument(path=path, header_comment=header_comment)
    document.set_name = document._set_name_from_comment()
    for driver_el in root.findall(DRIVER_TAG):
        entry = _parse_driver_element(driver_el)
        document.drivers.append(entry)

    document.drivers = normalize_document_drivers(document.drivers)

    logger.info("Loaded %d driver entries from %s", len(document.drivers), path.name)
    document.mark_clean()
    return document


def _parse_driver_element(element: ET.Element) -> DriverEntry:
    livery_name = element.get("livery_name", "")
    tracks = element.get("tracks", "")
    entry = DriverEntry(
        livery_name=livery_name,
        tracks=tracks,
        is_track_override=bool(tracks.strip()),
        mode="custom",
    )

    for child in element:
        tag = child.tag
        text = (child.text or "").strip()
        if not text:
            continue
        if tag in TEXT_FIELDS:
            setattr(entry, tag, text)
            entry.set_fields.add(tag)
        elif tag in PARAMETER_BY_KEY:
            try:
                entry.set_xml_value(tag, float(text))
            except ValueError:
                logger.warning("Invalid numeric value for %s: %r", tag, text)

    return entry
