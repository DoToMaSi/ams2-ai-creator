from ams2_ai.models.document import AIDocument
from ams2_ai.models.header_meta import build_header_comment, parse_header_comment


def test_parse_structured_header():
    comment = """Name: F1 1991 Season
Class: F-Classic_Gen4
Custom Name:

*** Changelog ***
v0.6 update"""
    meta = parse_header_comment(comment)
    assert meta.name == "F1 1991 Season"
    assert meta.vehicle_class == "F-Classic_Gen4"
    assert meta.custom_class_name == ""
    assert "Changelog" in meta.body


def test_parse_legacy_header():
    comment = """Custom AI by jusk - F1 1991 Season (F-Classic_Gen4)

*** Changelog ***"""
    meta = parse_header_comment(comment)
    assert meta.name.startswith("Custom AI by jusk")
    assert meta.vehicle_class == ""
    assert "Changelog" in meta.body


def test_build_header_preserves_body():
    document = AIDocument(
        set_name="SEX",
        vehicle_class="F-V8_Gen1",
        custom_class_name="",
        header_comment_body="Notes line",
    )
    document.sync_header_comment()
    meta = parse_header_comment(document.header_comment)
    assert meta.name == "SEX"
    assert meta.vehicle_class == "F-V8_Gen1"
    assert meta.body == "Notes line"
    assert "Created with the AMS2 AI Tool by RockettSally" in document.header_comment


def test_build_header_includes_tool_attribution():
    document = AIDocument(
        set_name="F1 2005",
        vehicle_class="F-V10_Gen2",
        custom_class_name="F1 2005.xml",
    )
    document.sync_header_comment()
    lines = document.header_comment.splitlines()
    assert lines[0] == "Name: F1 2005"
    assert lines[1] == "Class: F-V10_Gen2"
    assert lines[2] == "Custom Name: F1 2005.xml"
    assert lines[3] == "Created with the AMS2 AI Tool by RockettSally"


def test_effective_filename_prefers_custom_name():
    document = AIDocument(vehicle_class="GT3", custom_class_name="MyMod.xml")
    assert document.effective_filename() == "MyMod.xml"


def test_effective_filename_uses_class():
    document = AIDocument(vehicle_class="StockCarV8")
    assert document.effective_filename() == "StockCarV8.xml"
