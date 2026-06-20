import random

from ams2_ai.data import flag_icon_path, get_country_meta, load_country_codes
from ams2_ai.identity.generator import randomize_new_driver
from ams2_ai.models.driver import DriverEntry
from ams2_ai.smart.presets import PRESET_TIERS


def test_load_country_codes_matches_legacy_count():
    codes = load_country_codes()
    assert len(codes) == 36
    assert "BRA" in codes
    assert "USA" in codes


def test_every_country_has_meta_and_flag():
    seen_iso2: set[str] = set()
    for code in load_country_codes():
        meta = get_country_meta(code)
        assert meta is not None, code
        assert meta.code == code
        assert len(meta.iso2) == 2
        assert meta.locale
        flag = flag_icon_path(code)
        assert flag is not None, code
        assert flag.is_file(), code
        seen_iso2.add(meta.iso2)
    assert len(seen_iso2) == 34


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
