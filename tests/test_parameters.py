from ams2_ai.models.parameters import ui_to_xml, xml_to_ui


def test_unit_round_trip():
    assert xml_to_ui("race_skill", ui_to_xml("race_skill", 75)) == 75


def test_scalar_mapping():
    assert ui_to_xml("weight_scalar", 100) == 1.0
    assert xml_to_ui("weight_scalar", 1.0) == 100
    assert ui_to_xml("weight_scalar", 90) == 0.9
    assert ui_to_xml("weight_scalar", 110) == 1.1


def test_optional_parameter_defaults_match_ams2_neutral():
    from ams2_ai.models.driver import DriverEntry
    from ams2_ai.models.parameters import default_ui_value

    assert default_ui_value("weight_scalar") == 100
    assert default_ui_value("power_scalar") == 100
    assert default_ui_value("drag_scalar") == 100
    assert default_ui_value("setup_downforce") == 50
    assert default_ui_value("setup_downforce_randomness") == 0
    assert default_ui_value("race_skill") == 50

    entry = DriverEntry()
    assert entry.get_ui_value("weight_scalar") == 100
    assert entry.get_ui_value("setup_downforce") == 50
    assert entry.get_ui_value("setup_downforce_randomness") == 0
