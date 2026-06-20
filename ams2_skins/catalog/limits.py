"""Load bundled livery limit metadata."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path


def _limits_path() -> Path:
    if getattr(sys, "frozen", False):
        frozen = Path(sys._MEIPASS) / "ams2_skins" / "data" / "livery_limits.json"
        if frozen.is_file():
            return frozen
    return Path(__file__).resolve().parent.parent / "data" / "livery_limits.json"


@lru_cache(maxsize=1)
def load_livery_limits() -> dict[str, dict]:
    path = _limits_path()
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return data


def get_livery_limit(folder_id: str) -> dict | None:
    entry = load_livery_limits().get(folder_id)
    if isinstance(entry, dict):
        return entry
    return None
