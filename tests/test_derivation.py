from ams2_ai.models.parameters import xml_to_ui
from ams2_ai.smart.derivation import derive_from_skill_aggression


def test_derive_clamps_to_valid_ranges():
    result = derive_from_skill_aggression(50, 50, apply_randomness=False)
    for key, value in result.items():
        ui = xml_to_ui(key, value)
        assert 0 <= ui <= 110


def test_high_skill_produces_high_consistency():
    low = derive_from_skill_aggression(20, 30, apply_randomness=False)
    high = derive_from_skill_aggression(90, 50, apply_randomness=False)
    assert high["consistency"] > low["consistency"]
