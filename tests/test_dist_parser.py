"""Tests for _dist.xml parsing."""

from pathlib import Path

from ams2_skins.xml.dist_parser import parse_dist_file

DIST_XML = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "example_skinpacks"
    / "StockCar STOCKPAP 2020"
    / "Vehicles"
    / "Textures"
    / "CustomLiveries"
    / "Overrides"
    / "stock_cruze_20"
    / "stock_cruze_20_dist.xml"
)


def test_parse_stock_cruze_dist():
    metadata = parse_dist_file(DIST_XML, car_id="stock_cruze_20")
    names = [spec.name for spec in metadata.base_liveries]
    assert "Default" in names
    assert "Matte" in names
    assert "Chrome" in names

    default = next(spec for spec in metadata.base_liveries if spec.name == "Default")
    assert "BODY" in default.texture_names
    assert "WINDSCREEN" in default.texture_names
