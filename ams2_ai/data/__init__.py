"""Load bundled reference data."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path


@dataclass(frozen=True)
class CountryMeta:
    code: str
    iso2: str
    locale: str


# Non-NATO legacy codes seen in older XML or informal usage → STANAG 1059 trigrams.
LEGACY_COUNTRY_ALIASES: dict[str, str] = {
    "GER": "DEU",
    "UK": "GBR",
    "POR": "PRT",
    "MON": "MCO",
    "UAE": "ARE",
}


def normalize_country_code(code: str) -> str:
    """Return the NATO STANAG 1059 trigram for a country code."""
    normalized = code.strip().upper()
    return LEGACY_COUNTRY_ALIASES.get(normalized, normalized)


def _data_file(name: str) -> Path:
    """Resolve a bundled file under ams2_ai/data in dev and PyInstaller builds."""
    if getattr(sys, "frozen", False):
        frozen_path = Path(sys._MEIPASS) / "ams2_ai" / "data" / name
        if frozen_path.is_file():
            return frozen_path

    package_path = resources.files("ams2_ai.data").joinpath(name)
    return Path(package_path)


def _flag_file(iso2: str) -> Path:
    name = f"flags/{iso2.lower()}.png"
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
def _load_country_meta_list() -> list[CountryMeta]:
    raw = _read_json("country_meta.json")
    return [CountryMeta(**entry) for entry in raw]


@lru_cache(maxsize=1)
def _country_meta_by_code() -> dict[str, CountryMeta]:
    return {entry.code: entry for entry in _load_country_meta_list()}


@lru_cache(maxsize=1)
def load_country_codes() -> list[str]:
    return [entry.code for entry in _load_country_meta_list()]


@lru_cache(maxsize=1)
def load_countries() -> list[str]:
    """Backward-compatible alias for load_country_codes()."""
    return load_country_codes()


def get_country_meta(code: str) -> CountryMeta | None:
    normalized = normalize_country_code(code)
    if not normalized:
        return None
    return _country_meta_by_code().get(normalized)


def flag_icon_path(code: str) -> Path | None:
    meta = get_country_meta(code)
    if meta is None:
        return None
    path = _flag_file(meta.iso2)
    return path if path.is_file() else None
