"""Load bundled reference data."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib import resources


@lru_cache(maxsize=1)
def load_vehicle_classes() -> list[str]:
    path = resources.files("ams2_ai.data").joinpath("vehicle_classes.json")
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def load_tracks() -> list[str]:
    text = resources.files("ams2_ai.data").joinpath("tracks.json").read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def load_countries() -> list[str]:
    text = resources.files("ams2_ai.data").joinpath("countries.json").read_text(encoding="utf-8")
    return json.loads(text)
