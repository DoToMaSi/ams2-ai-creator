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
    description: str
    low_hint: str
    high_hint: str
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
        "Race-session driver skill. Scaled by the Opponent Skill Level slider in AMS2.",
        "Slower lap times, more race mistakes, and weaker wheel-to-wheel pace.",
        "Faster lap times, cleaner driving, and stronger race pace.",
    ),
    ParameterDef(
        "qualifying_skill",
        "Qualifying Skill",
        ParamKind.UNIT,
        "Core Skill",
        "Practice and qualifying skill, independent from race skill.",
        "Slower single-lap pace and more qualifying-specific mistakes.",
        "Stronger one-lap pace and fewer qualifying mistakes.",
    ),
    ParameterDef(
        "wet_skill",
        "Wet Skill",
        ParamKind.UNIT,
        "Core Skill",
        "Performance on wet or damp track surfaces.",
        "More slowdown in wet corners and more wet-weather mistakes.",
        "Better wet grip, confidence, and consistency in the rain.",
    ),
    ParameterDef(
        "aggression",
        "Aggression",
        ParamKind.UNIT,
        "Racecraft",
        "How aggressively the driver attacks and fights for position. "
        "Scaled by the Opponent Aggression setting in AMS2.",
        "More cautious overtakes and less willingness to challenge rivals.",
        "More assertive overtakes, closer racing, and higher incident risk.",
    ),
    ParameterDef(
        "defending",
        "Defending",
        ParamKind.UNIT,
        "Racecraft",
        "How hard the driver defends position when under pressure. "
        "Also scaled by Opponent Aggression.",
        "Easier to pass; gives up position sooner under attack.",
        "Holds lines longer and makes overtakes harder to complete.",
    ),
    ParameterDef(
        "consistency",
        "Consistency",
        ParamKind.UNIT,
        "Racecraft",
        "How stable the driver's performance is from weekend to weekend and lap to lap.",
        "More random skill swings between sessions and within a stint.",
        "More predictable pace with fewer unexplained performance drops.",
    ),
    ParameterDef(
        "stamina",
        "Stamina",
        ParamKind.UNIT,
        "Racecraft",
        "Resistance to fatigue over longer stints and races.",
        "Earlier fatigue and more skill loss as the session progresses.",
        "Maintains pace deeper into stints with less late-race drop-off.",
    ),
    ParameterDef(
        "start_reactions",
        "Start Reactions",
        ParamKind.UNIT,
        "Racecraft",
        "Green-flag start reaction time and start-line execution.",
        "Slower reactions off the line and more start mistakes.",
        "Quicker launches and cleaner getaway from the grid.",
    ),
    ParameterDef(
        "tyre_management",
        "Tyre Management",
        ParamKind.UNIT,
        "Strategy",
        "How gently the driver uses tyres without changing overall driving style.",
        "Higher tyre wear and faster degradation over a stint.",
        "Lower tyre wear and longer stint life on the same compound.",
    ),
    ParameterDef(
        "fuel_management",
        "Fuel Management",
        ParamKind.UNIT,
        "Strategy",
        "Fuel-saving behavior on ovals and in strategic fuel-save situations.",
        "Uses more fuel; less willingness to lift and coast for strategy.",
        "Saves more fuel when needed without being told to pit.",
    ),
    ParameterDef(
        "blue_flag_conceding",
        "Blue Flag Conceding",
        ParamKind.UNIT,
        "Strategy",
        "How readily the driver yields when shown a blue flag.",
        "Slower or reluctant to let faster cars through.",
        "Works harder to move aside promptly for lapped traffic.",
    ),
    ParameterDef(
        "weather_tyre_changes",
        "Weather Tyre Changes",
        ParamKind.UNIT,
        "Strategy",
        "Likelihood of pitting for tyres when track wetness changes. "
        "A driver characteristic, not pure pace skill.",
        "Stays out longer in the wrong conditions or delays tyre calls.",
        "Pits earlier and adapts compound choice more readily to weather.",
    ),
    ParameterDef(
        "avoidance_of_mistakes",
        "Avoidance of Mistakes",
        ParamKind.UNIT,
        "Mistakes",
        "General resistance to unforced driving errors during a session.",
        "More spins, lockups, and off-track moments.",
        "Fewer self-inflicted mistakes across the session.",
    ),
    ParameterDef(
        "avoidance_of_forced_mistakes",
        "Avoidance of Forced Mistakes",
        ParamKind.UNIT,
        "Mistakes",
        "Resistance to mistakes caused by pressure while defending or racing closely.",
        "More errors when under attack or in tight battles.",
        "Stays calmer under pressure with fewer defensive mistakes.",
    ),
    ParameterDef(
        "weight_scalar",
        "Weight Scalar",
        ParamKind.SCALAR,
        "Vehicle Performance",
        "Multiplies vehicle mass (0.900–1.100 XML; 1.000 is neutral). "
        "Also affects the player car when using this livery.",
        "Lighter car — slightly better acceleration and braking.",
        "Heavier car — slightly worse acceleration and braking.",
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
        "Multiplies engine power (0.900–1.100 XML; 1.000 is neutral). "
        "Also affects the player car when using this livery.",
        "Less engine power and slower straight-line speed.",
        "More engine power and stronger acceleration.",
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
        "Multiplies aerodynamic drag (0.900–1.100 XML; 1.000 is neutral). "
        "Also affects the player car when using this livery.",
        "Lower drag — higher top speed, less aero resistance.",
        "Higher drag — lower top speed, more aero resistance.",
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
        "Preferred downforce bias (0.000–1.000 XML; 0.500 is neutral).",
        "Prefers lower-downforce setups — more straight-line speed, less grip.",
        "Prefers higher-downforce setups — more cornering grip, less top speed.",
        ui_default=50,
    ),
    ParameterDef(
        "setup_downforce_randomness",
        "Setup Downforce Randomness",
        ParamKind.UNIT,
        "Setup",
        "Per-weekend variation around the preferred downforce bias (0.000–1.000 XML).",
        "No randomness — setup stays at the preferred bias every weekend.",
        "Wider weekend-to-weekend swings from the preferred downforce bias.",
        ui_default=0,
    ),
    ParameterDef(
        "vehicle_reliability",
        "Vehicle Reliability",
        ParamKind.RELIABILITY,
        "Reliability",
        "Reliability ratio for the class. Values above 0.6 are generally good; "
        "can exceed 1.0 depending on class norms.",
        "More mechanical failures and retirements over a season.",
        "Fewer breakdowns and stronger finishing reliability.",
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
