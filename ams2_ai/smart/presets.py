"""Skill tier presets with randomized values."""

from __future__ import annotations

import random
from dataclasses import dataclass

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import NUMERIC_KEYS, clamp
from ams2_ai.smart.derivation import apply_smart_derivation

PRESET_NAMES = ["Junior", "Amateur", "Pro-Am", "Pro", "Elite", "Master"]


@dataclass(frozen=True)
class PresetTier:
    name: str
    skill_min: int
    skill_max: int
    aggression_min: int
    aggression_max: int


PRESET_TIERS: dict[str, PresetTier] = {
    "Junior": PresetTier("Junior", 5, 22, 15, 35),
    "Amateur": PresetTier("Amateur", 22, 40, 25, 45),
    "Pro-Am": PresetTier("Pro-Am", 40, 58, 30, 55),
    "Pro": PresetTier("Pro", 58, 75, 35, 65),
    "Elite": PresetTier("Elite", 75, 90, 40, 72),
    "Master": PresetTier("Master", 88, 100, 50, 85),
}


def _rand_int(low: int, high: int) -> int:
    return random.randint(low, high)


def _tier_center(tier: PresetTier) -> tuple[int, int]:
    skill = (tier.skill_min + tier.skill_max) // 2
    aggression = (tier.aggression_min + tier.aggression_max) // 2
    return skill, aggression


def apply_preset(driver: DriverEntry, preset_name: str) -> None:
    tier = PRESET_TIERS[preset_name]
    skill = _rand_int(tier.skill_min, tier.skill_max)
    aggression = _rand_int(tier.aggression_min, tier.aggression_max)

    if driver.mode == "smart":
        driver.set_ui_value("race_skill", skill)
        driver.set_ui_value("aggression", aggression)
        apply_smart_derivation(driver)
        return

    center_skill, center_aggression = _tier_center(tier)
    spread = max(8, (tier.skill_max - tier.skill_min) // 3)

    for key in NUMERIC_KEYS:
        if key == "race_skill":
            driver.set_ui_value(key, skill)
        elif key == "aggression":
            driver.set_ui_value(key, aggression)
        elif key in {"weight_scalar", "power_scalar", "drag_scalar"}:
            if preset_name == "Junior":
                driver.set_ui_value(key, _rand_int(97, 103))
            else:
                driver.set_ui_value(key, _rand_int(98, 102))
        elif key == "setup_downforce":
            driver.set_ui_value(key, _rand_int(40, 60))
        elif key == "setup_downforce_randomness":
            driver.set_ui_value(key, _rand_int(10, 35))
        elif key == "vehicle_reliability":
            rel = clamp(center_skill + random.randint(-10, 10), 40, 100)
            driver.set_ui_value(key, rel)
        elif key in {"fuel_management", "weather_tyre_changes"}:
            driver.set_ui_value(key, _rand_int(20, 80))
        else:
            base = center_skill if key != "defending" else center_aggression
            value = clamp(base + random.randint(-spread, spread), 0, 100)
            driver.set_ui_value(key, value)
