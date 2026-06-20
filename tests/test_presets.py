from ams2_ai.models.driver import DriverEntry
from ams2_ai.smart.presets import PRESET_NAMES, PRESET_TIERS, apply_preset


def test_all_presets_exist():
    assert len(PRESET_NAMES) == 6
    for name in PRESET_NAMES:
        assert name in PRESET_TIERS


def test_smart_preset_sets_skill_and_aggression():
    driver = DriverEntry(mode="smart")
    apply_preset(driver, "Pro")
    tier = PRESET_TIERS["Pro"]
    skill = driver.get_skill_ui()
    aggression = driver.get_aggression_ui()
    assert tier.skill_min <= skill <= tier.skill_max
    assert tier.aggression_min <= aggression <= tier.aggression_max
