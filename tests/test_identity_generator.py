import random

from ams2_ai.data import (
    country_display_label,
    flag_icon_path,
    get_country_meta,
    load_country_codes,
    normalize_country_code,
    parse_country_selection,
)
from ams2_ai.identity.generator import randomize_new_driver
from ams2_ai.models.driver import DriverEntry
from ams2_ai.smart.presets import PRESET_TIERS


def test_load_country_codes_are_nato_trigrams():
    codes = load_country_codes()
    assert len(codes) == 34
    assert "BRA" in codes
    assert "USA" in codes
    assert "DEU" in codes
    assert "PRT" in codes
    assert "ARE" in codes
    assert "GER" not in codes
    assert "UK" not in codes
    assert "POR" not in codes
    assert "MON" not in codes
    assert "UAE" not in codes


def test_normalize_legacy_country_codes():
    assert normalize_country_code("ger") == "DEU"
    assert normalize_country_code("UK") == "GBR"
    assert normalize_country_code("POR") == "PRT"
    assert normalize_country_code("MON") == "MCO"
    assert normalize_country_code("UAE") == "ARE"
    assert normalize_country_code("BRA") == "BRA"


def test_every_country_has_meta_and_flag():
    seen_iso2: set[str] = set()
    for code in load_country_codes():
        meta = get_country_meta(code)
        assert meta is not None, code
        assert meta.code == code
        assert meta.name.strip()
        assert len(meta.iso2) == 2
        assert meta.locale
        assert country_display_label(code).endswith(f"({code})")
        flag = flag_icon_path(code)
        assert flag is not None, code
        assert flag.is_file(), code
        seen_iso2.add(meta.iso2)
    assert len(seen_iso2) == 34


def test_country_display_and_parse():
    assert country_display_label("BRA") == "Brazil (BRA)"
    assert parse_country_selection("Brazil (BRA)") == "BRA"
    assert parse_country_selection("GER") == "DEU"
    assert parse_country_selection("United Kingdom (GBR)") == "GBR"


def test_randomize_new_driver_sets_identity_and_skills():
    random.seed(42)
    entry = DriverEntry(mode="smart")
    randomize_new_driver(entry)

    assert entry.name.strip()
    assert entry.country in load_country_codes()
    assert "name" in entry.set_fields
    assert "country" in entry.set_fields
    assert "race_skill" in entry.set_fields
    assert "aggression" in entry.set_fields
    assert 0 <= entry.get_skill_ui() <= 100
    assert 0 <= entry.get_aggression_ui() <= 100


def test_randomize_new_driver_skill_within_preset_bounds():
    random.seed(123)
    entry = DriverEntry(mode="smart")
    randomize_new_driver(entry)

    skill = entry.get_skill_ui()
    aggression = entry.get_aggression_ui()
    in_tier = any(
        tier.skill_min <= skill <= tier.skill_max
        and tier.aggression_min <= aggression <= tier.aggression_max
        for tier in PRESET_TIERS.values()
    )
    assert in_tier
