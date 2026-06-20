"""Convert driver names to Latin ASCII for AMS2 XML."""

from __future__ import annotations

import re

from unidecode import unidecode

_NON_ASCII = re.compile(r"[^\x00-\x7F]")


def romanize_name(name: str) -> str:
    """Return a Latin ASCII form suitable for <name> tags."""
    stripped = name.strip()
    if not stripped:
        return ""
    if not _NON_ASCII.search(stripped):
        return " ".join(stripped.split())
    return " ".join(unidecode(stripped).split())
