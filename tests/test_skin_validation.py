"""Tests for skin validation."""

from pathlib import Path

from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.livery_override import LiveryOverride
from ams2_skins.models.skinpack import SkinpackDocument
from ams2_skins.validation import validate_car_document, validate_skinpack
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


def _catalog_entry() -> VehicleCatalogEntry:
    metadata = parse_dist_file(DIST_XML, car_id="stock_cruze_20")
    return VehicleCatalogEntry(
        folder_id="stock_cruze_20",
        xml_filename="stock_cruze_20.xml",
        display_name="Stock Car 2020 Cruze",
        dist_path=str(DIST_XML),
        base_liveries=metadata.base_liveries,
        helmet_bases=metadata.helmet_bases,
        helmet_texture_names=metadata.helmet_texture_names,
        max_livery_id=73,
        has_livery_limit=True,
    )


def test_validate_requires_name():
    car = CarOverrideDocument(
        car_id="stock_cruze_20",
        liveries=[LiveryOverride(livery_id=51, name="", base_livery="Default")],
    )
    errors = validate_car_document(car, catalog_entry=_catalog_entry())
    assert any("NAME is required" in error for error in errors)


def test_validate_livery_id_range():
    car = CarOverrideDocument(
        car_id="stock_cruze_20",
        liveries=[LiveryOverride(livery_id=999, name="Too high", base_livery="Default")],
    )
    errors = validate_car_document(car, catalog_entry=_catalog_entry())
    assert any("exceeds max" in error for error in errors)


def test_validate_empty_skinpack():
    pack = SkinpackDocument()
    errors = validate_skinpack(pack)
    assert errors == ["Skinpack has no cars."]
