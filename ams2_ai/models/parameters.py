"""Parameter definitions and UI/XML value conversion."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class ParamKind(str, Enum):
    UNIT = "unit"  # 0-1 XML -> 0-100 UI
    SCALAR = "scalar"  # 0.900-1.100 XML -> 90-110 UI
    RELIABILITY = "reliability"  # unbounded float, UI 0-100 default display


@dataclass(frozen=True)
class ParameterDef:
    key: str
    label: str
    kind: ParamKind
    group: str
    tooltip: str
    ui_min: int = 0
    ui_max: int = 100
    xml_min: float = 0.0
    xml_max: float = 1.0
    ui_default: int | None = None


PARAMETER_GROUPS = [
    "Core Skill",
    "Racecraft",
    "Strategy",
    "Mistakes",
    "Vehicle Performance",
    "Setup",
    "Reliability",
]

PARAMETERS: list[ParameterDef] = [
    ParameterDef(
        "race_skill",
        "Race Skill",
        ParamKind.UNIT,
        "Core Skill",
        "Race session driver skill. Mapped by the Opponent Skill Level slider in AMS2.",
    ),
    ParameterDef(
        "qualifying_skill",
        "Qualifying Skill",
        ParamKind.UNIT,
        "Core Skill",
        "Practice/qualifying skill. Independent from race skill. "
        "Lower values increase qualifying mistakes.",
    ),
    ParameterDef(
        "wet_skill",
        "Wet Skill",
        ParamKind.UNIT,
        "Core Skill",
        "Wet track performance. Lower values mean more slowdown in wet corners "
        "and more wet mistakes.",
    ),
    ParameterDef(
        "aggression",
        "Aggression",
        ParamKind.UNIT,
        "Racecraft",
        "Driver aggression, scaled by the Opponent Aggression setting in AMS2.",
    ),
    ParameterDef(
        "defending",
        "Defending",
        ParamKind.UNIT,
        "Racecraft",
        "How much the driver defends position. Also scaled by Opponent Aggression.",
    ),
    ParameterDef(
        "consistency",
        "Consistency",
        ParamKind.UNIT,
        "Racecraft",
        "Lower consistency means more random skill loss per weekend and per lap.",
    ),
    ParameterDef(
        "stamina",
        "Stamina",
        ParamKind.UNIT,
        "Racecraft",
        "Lower stamina means earlier fatigue and more skill loss during the session.",
    ),
    ParameterDef(
        "start_reactions",
        "Start Reactions",
        ParamKind.UNIT,
        "Racecraft",
        "Lower values mean slower green-flag reactions and more start mistakes.",
    ),
    ParameterDef(
        "tyre_management",
        "Tyre Management",
        ParamKind.UNIT,
        "Strategy",
        "Higher values reduce tyre wear without changing driving style.",
    ),
    ParameterDef(
        "fuel_management",
        "Fuel Management",
        ParamKind.UNIT,
        "Strategy",
        "Oval tracks only for now. Higher values mean more fuel saving in strategic situations.",
    ),
    ParameterDef(
        "blue_flag_conceding",
        "Blue Flag Conceding",
        ParamKind.UNIT,
        "Strategy",
        "Higher values mean the driver works harder to concede under blue flags.",
    ),
    ParameterDef(
        "weather_tyre_changes",
        "Weather Tyre Changes",
        ParamKind.UNIT,
        "Strategy",
        "Likelihood to pit for tyres when track wetness changes. A characteristic, not pure skill.",
    ),
    ParameterDef(
        "avoidance_of_mistakes",
        "Avoidance of Mistakes",
        ParamKind.UNIT,
        "Mistakes",
        "Lower values increase general programmed mistakes during the session.",
    ),
    ParameterDef(
        "avoidance_of_forced_mistakes",
        "Avoidance of Forced Mistakes",
        ParamKind.UNIT,
        "Mistakes",
        "Lower values increase mistake chances when under pressure while defending.",
    ),
    ParameterDef(
        "weight_scalar",
        "Weight Scalar",
        ParamKind.SCALAR,
        "Vehicle Performance",
        "Multiplies vehicle mass (0.900–1.100). 1.000 is neutral. "
        "Also affects the player car when using this livery.",
        ui_min=90,
        ui_max=110,
        xml_min=0.900,
        xml_max=1.100,
        ui_default=100,
    ),
    ParameterDef(
        "power_scalar",
        "Power Scalar",
        ParamKind.SCALAR,
        "Vehicle Performance",
        "Multiplies engine power (0.900–1.100). 1.000 is neutral. "
        "Also affects the player car when using this livery.",
        ui_min=90,
        ui_max=110,
        xml_min=0.900,
        xml_max=1.100,
        ui_default=100,
    ),
    ParameterDef(
        "drag_scalar",
        "Drag Scalar",
        ParamKind.SCALAR,
        "Vehicle Performance",
        "Multiplies aerodynamic drag (0.900–1.100). 1.000 is neutral. "
        "Also affects the player car when using this livery.",
        ui_min=90,
        ui_max=110,
        xml_min=0.900,
        xml_max=1.100,
        ui_default=100,
    ),
    ParameterDef(
        "setup_downforce",
        "Setup Downforce",
        ParamKind.UNIT,
        "Setup",
        "Preferred downforce bias (0.000–1.000). 0.500 is neutral; "
        "lower favors low downforce, higher favors high downforce.",
        ui_default=50,
    ),
    ParameterDef(
        "setup_downforce_randomness",
        "Setup Downforce Randomness",
        ParamKind.UNIT,
        "Setup",
        "Per-weekend setup variation (0.000–1.000). 0.000 = no randomness; "
        "higher values allow wider swings from the preferred bias.",
        ui_default=0,
    ),
    ParameterDef(
        "vehicle_reliability",
        "Vehicle Reliability",
        ParamKind.RELIABILITY,
        "Reliability",
        "Reliability ratio for the class. Values above 0.6 are generally good; can exceed 1.0.",
    ),
]

PARAMETER_BY_KEY = {p.key: p for p in PARAMETERS}
NUMERIC_KEYS = [p.key for p in PARAMETERS]

OPTIONAL_PARAMETER_GROUPS: dict[str, tuple[str, ...]] = {
    "Vehicle Performance": (
        "weight_scalar",
        "power_scalar",
        "drag_scalar",
    ),
    "Setup": (
        "setup_downforce",
        "setup_downforce_randomness",
    ),
}
OPTIONAL_PARAMETER_KEYS = frozenset(
    key for keys in OPTIONAL_PARAMETER_GROUPS.values() for key in keys
)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def default_ui_value(key: str) -> int:
    """UI default when a parameter is unset in the entry."""
    param = PARAMETER_BY_KEY[key]
    if param.ui_default is not None:
        return param.ui_default
    return 50


def ui_to_xml(key: str, ui_value: int | float) -> float:
    param = PARAMETER_BY_KEY[key]
    if param.kind == ParamKind.SCALAR:
        return round(clamp(float(ui_value) / 100.0, param.xml_min, param.xml_max), 3)
    if param.kind == ParamKind.RELIABILITY:
        return round(float(ui_value) / 100.0, 3)
    return round(clamp(float(ui_value) / 100.0, param.xml_min, param.xml_max), 3)


def xml_to_ui(key: str, xml_value: float) -> int:
    param = PARAMETER_BY_KEY[key]
    if param.kind == ParamKind.SCALAR:
        return int(round(clamp(xml_value * 100.0, param.ui_min, param.ui_max)))
    if param.kind == ParamKind.RELIABILITY:
        return int(round(xml_value * 100.0))
    return int(round(clamp(xml_value * 100.0, param.ui_min, param.ui_max)))


def format_xml_value(key: str, xml_value: float) -> str:
    param = PARAMETER_BY_KEY[key]
    if param.kind == ParamKind.SCALAR:
        return f"{xml_value:.3f}"
    if param.kind == ParamKind.RELIABILITY:
        decimals = 3 if abs(xml_value) < 10 else 2
        return f"{xml_value:.{decimals}f}".rstrip("0").rstrip(".")
    text = f"{xml_value:.3f}".rstrip("0").rstrip(".")
    return text if text else "0"


def validate_country(country: str) -> bool:
    return len(country.strip()) == 3


ModeType = Literal["smart", "custom"]
