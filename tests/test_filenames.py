from ams2_ai.util.filenames import xml_filename_from_label


def test_xml_filename_from_label():
    assert xml_filename_from_label("F1 2005") == "F1 2005.xml"
    assert xml_filename_from_label("SEX") == "SEX.xml"
    assert xml_filename_from_label("MyMod_GT3.xml") == "MyMod_GT3.xml"


def test_xml_filename_sanitizes_invalid_characters():
    assert xml_filename_from_label('Bad:Name?') == "Bad_Name_.xml"


def test_xml_filename_from_empty_label():
    assert xml_filename_from_label("") == ""
    assert xml_filename_from_label("   ") == ""
