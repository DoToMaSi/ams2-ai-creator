"""Filename helpers for AI XML export."""

from __future__ import annotations

_INVALID_FILENAME_CHARS = '<>:"/\\|?*'


def xml_filename_from_label(label: str) -> str:
    """Build a safe .xml filename from a human-readable set name."""
    stripped = label.strip()
    if not stripped:
        return ""
    safe = "".join("_" if char in _INVALID_FILENAME_CHARS else char for char in stripped)
    safe = safe.strip(". ")
    if not safe:
        return ""
    if not safe.lower().endswith(".xml"):
        safe = f"{safe}.xml"
    return safe
