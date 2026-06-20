"""Load bundled reference data."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from importlib import resources
from pathlib import Path


def _data_file(name: str) -> Path:
    """Resolve a bundled JSON file in dev and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        frozen_path = Path(sys._MEIPASS) / "ams2_ai" / "data" / name
        if frozen_path.is_file():
            return frozen_path

    package_path = resources.files("ams2_ai.data").joinpath(name)
    return Path(package_path)


def _read_json(name: str):
    return json.loads(_data_file(name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_vehicle_classes() -> list[str]:
    return _read_json("vehicle_classes.json")


@lru_cache(maxsize=1)
def load_tracks() -> list[str]:
    return _read_json("tracks.json")


@lru_cache(maxsize=1)
def load_countries() -> list[str]:
    return _read_json("countries.json")
