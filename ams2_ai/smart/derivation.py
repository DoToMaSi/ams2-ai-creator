"""Derive AI personality parameters from skill and aggression."""

from __future__ import annotations

from ams2_ai.models.driver import DriverEntry
from ams2_ai.models.parameters import NUMERIC_KEYS, clamp, ui_to_xml


def _clamp01(value: float) -> float:
    return clamp(value, 0.0, 1.0)

# Vehicle performance, setup, and reliability are car-specific — editable independently in Smart mode.
INDEPENDENT_KEYS = frozenset(
    {
        "weight_scalar",
        "power_scalar",
        "drag_scalar",
        "setup_downforce",
        "setup_downforce_randomness",
        "vehicle_reliability",
    }
)

DERIVED_PERSONALITY_KEYS = frozenset(NUMERIC_KEYS) - INDEPENDENT_KEYS - {"race_skill", "aggression"}


def calculate_smart_ai(skill: float, aggression: float) -> dict[str, float]:
    """
    Derive AMS2 AI personality parameters from Skill (S) and Aggression (A).

    Both inputs are floats from 0.0 to 1.0. Output values are clamped to 0.0–1.0
    and rounded to three decimal places for XML output.
    """
    s = _clamp01(skill)
    a = _clamp01(aggression)
    inv_penalty = a * (1.0 - s)

    params = {
        "qualifying_skill": _clamp01(s + (a - 0.5) * 0.1),
        "start_reactions": _clamp01(s * 0.5 + a * 0.5),
        "wet_skill": _clamp01(s - inv_penalty * 0.4),
        "consistency": _clamp01(s - inv_penalty * 0.6),
        "avoidance_of_mistakes": _clamp01(s - inv_penalty * 0.8),
        "avoidance_of_forced_mistakes": _clamp01(s - inv_penalty * 0.5),
        "defending": _clamp01(a * 0.8 + s * 0.2),
        "blue_flag_conceding": _clamp01((1.0 - a) * 0.7 + s * 0.3),
        "tyre_management": _clamp01(s * 0.5 + (1.0 - a) * 0.5),
        "fuel_management": _clamp01(s * 0.6 + (1.0 - a) * 0.4),
        "stamina": _clamp01(s * 0.7 + (1.0 - a) * 0.3),
        "weather_tyre_changes": _clamp01(s * 0.7 + (1.0 - a) * 0.3),
    }

    return {key: round(value, 3) for key, value in params.items()}


def derive_from_skill_aggression(
    skill_ui: int,
    aggression_ui: int,
    *,
    apply_randomness: bool = False,
) -> dict[str, float]:
    """Return XML values for all numeric parameters derived from skill/aggression UI (0–100)."""
    del apply_randomness  # deterministic formulas; presets randomize inputs only

    s = _clamp01(skill_ui / 100.0)
    a = _clamp01(aggression_ui / 100.0)

    derived = calculate_smart_ai(s, a)
    derived["race_skill"] = round(s, 3)
    derived["aggression"] = round(a, 3)
    derived["weight_scalar"] = 1.0
    derived["power_scalar"] = 1.0
    derived["drag_scalar"] = 1.0
    derived["setup_downforce"] = 0.5
    derived["setup_downforce_randomness"] = 0.0
    derived["vehicle_reliability"] = 0.5

    return {key: derived[key] for key in NUMERIC_KEYS}


def apply_smart_derivation(
    driver: DriverEntry,
    *,
    apply_randomness: bool = False,
    preserve_independent: bool = True,
) -> None:
    skill = driver.get_skill_ui()
    aggression = driver.get_aggression_ui()
    derived = derive_from_skill_aggression(skill, aggression, apply_randomness=apply_randomness)

    for key, xml_value in derived.items():
        if preserve_independent and key in INDEPENDENT_KEYS and key in driver.set_fields:
            continue
        driver.set_xml_value(key, xml_value)
