"""Derive AI personality parameters from skill and aggression."""

from __future__ import annotations

import random

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import NUMERIC_KEYS, clamp, ui_to_xml


def _noise(low: float, high: float) -> float:
    return random.uniform(low, high)


def derive_from_skill_aggression(
    skill_ui: int,
    aggression_ui: int,
    *,
    apply_randomness: bool = True,
) -> dict[str, float]:
    """Return XML values for all numeric parameters derived from skill/aggression."""
    n = _noise if apply_randomness else lambda _l, _h: 0.0

    qualifying_ui = clamp(skill_ui + n(-5, 8), 0, 100)
    defending_ui = clamp(0.6 * aggression_ui + 0.25 * skill_ui + n(-5, 5), 0, 100)
    consistency_ui = clamp(20 + 0.75 * skill_ui + n(-8, 8), 0, 100)
    stamina_ui = clamp(30 + 0.65 * skill_ui + n(-5, 5), 0, 100)
    start_reactions_ui = clamp(25 + 0.70 * skill_ui + n(-5, 5), 0, 100)
    wet_skill_ui = clamp(15 + 0.75 * skill_ui + n(-10, 10), 0, 100)
    tyre_mgmt_ui = clamp(40 + 0.50 * skill_ui + n(-5, 5), 0, 100)
    fuel_mgmt_ui = clamp(50 + n(-15, 15), 0, 100)
    blue_flag_ui = clamp(50 + 0.40 * skill_ui + n(-10, 10), 0, 100)
    weather_tyre_ui = clamp(20 + n(0, 50), 0, 100)
    avoid_mistakes_ui = clamp(20 + 0.60 * skill_ui + n(-5, 5), 0, 100)
    avoid_forced_ui = clamp(15 + 0.50 * skill_ui + 0.20 * aggression_ui + n(-5, 5), 0, 100)
    reliability_ui = clamp(50 + 0.45 * skill_ui + n(-5, 5), 0, 100)

    ui_values = {
        "race_skill": skill_ui,
        "qualifying_skill": int(round(qualifying_ui)),
        "aggression": aggression_ui,
        "defending": int(round(defending_ui)),
        "consistency": int(round(consistency_ui)),
        "stamina": int(round(stamina_ui)),
        "start_reactions": int(round(start_reactions_ui)),
        "wet_skill": int(round(wet_skill_ui)),
        "tyre_management": int(round(tyre_mgmt_ui)),
        "fuel_management": int(round(fuel_mgmt_ui)),
        "blue_flag_conceding": int(round(blue_flag_ui)),
        "weather_tyre_changes": int(round(weather_tyre_ui)),
        "avoidance_of_mistakes": int(round(avoid_mistakes_ui)),
        "avoidance_of_forced_mistakes": int(round(avoid_forced_ui)),
        "vehicle_reliability": int(round(reliability_ui)),
        "weight_scalar": 100,
        "power_scalar": 100,
        "drag_scalar": 100,
        "setup_downforce": 50,
        "setup_downforce_randomness": 20,
    }

    return {key: ui_to_xml(key, ui_values[key]) for key in NUMERIC_KEYS}


def apply_smart_derivation(driver: DriverEntry, *, apply_randomness: bool = False) -> None:
    skill = driver.get_skill_ui()
    aggression = driver.get_aggression_ui()
    derived = derive_from_skill_aggression(skill, aggression, apply_randomness=apply_randomness)
    for key, xml_value in derived.items():
        driver.set_xml_value(key, xml_value)
