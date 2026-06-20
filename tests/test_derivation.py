from ams2_ai.models.parameters import xml_to_ui
from ams2_ai.smart.derivation import calculate_smart_ai, derive_from_skill_aggression


def test_derive_clamps_to_valid_ranges():
    result = derive_from_skill_aggression(50, 50, apply_randomness=False)
    independent = {
        "weight_scalar",
        "power_scalar",
        "drag_scalar",
        "setup_downforce",
        "setup_downforce_randomness",
        "vehicle_reliability",
    }
    for key, value in result.items():
        if key in {"weight_scalar", "power_scalar", "drag_scalar"}:
            assert 0.9 <= value <= 1.1
        elif key in independent:
            assert 0.0 <= value <= 1.0
        else:
            assert 0.0 <= value <= 1.0


def test_high_skill_produces_high_consistency():
    low = derive_from_skill_aggression(20, 30, apply_randomness=False)
    high = derive_from_skill_aggression(90, 50, apply_randomness=False)
    assert high["consistency"] > low["consistency"]


def test_calculate_smart_ai_example_values():
    result = calculate_smart_ai(0.85, 0.90)
    assert result["qualifying_skill"] == 0.89
    assert result["start_reactions"] == 0.875
    assert result["defending"] == 0.89
    assert "setup_downforce_randomness" not in result


def test_setup_and_reliability_are_independent_defaults():
    result = derive_from_skill_aggression(85, 90, apply_randomness=False)
    assert result["setup_downforce"] == 0.5
    assert result["setup_downforce_randomness"] == 0.0
    assert result["vehicle_reliability"] == 0.5


def test_aggressive_low_skill_penalizes_mistakes():
    calm_skilled = calculate_smart_ai(0.90, 0.20)
    hot_rookie = calculate_smart_ai(0.20, 0.90)
    assert calm_skilled["avoidance_of_mistakes"] > hot_rookie["avoidance_of_mistakes"]
    assert calm_skilled["consistency"] > hot_rookie["consistency"]
