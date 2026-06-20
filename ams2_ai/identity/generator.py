"""Offline random driver identity generation."""

from __future__ import annotations

import random
from functools import lru_cache

from faker import Faker

from ams2_ai.data import get_country_meta, load_country_codes
from ams2_ai.identity.romanize import romanize_name
from ams2_ai.models.driver import DriverEntry
from ams2_ai.smart.presets import PRESET_NAMES, apply_preset

FALLBACK_LOCALE = "en_US"


@lru_cache(maxsize=32)
def _faker_for_locale(locale: str) -> Faker:
    try:
        return Faker(locale)
    except Exception:
        return Faker(FALLBACK_LOCALE)


def _random_name(locale: str) -> str:
    faker = _faker_for_locale(locale)
    return faker.name()


def randomize_new_driver(entry: DriverEntry) -> None:
    """Assign a random country, locale-appropriate name, and preset-tier skills."""
    country = random.choice(load_country_codes())
    meta = get_country_meta(country)
    locale = meta.locale if meta else FALLBACK_LOCALE

    entry.name = romanize_name(_random_name(locale))
    entry.country = country
    entry.set_fields.add("name")
    entry.set_fields.add("country")

    tier = random.choice(PRESET_NAMES)
    apply_preset(entry, tier)
