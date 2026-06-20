"""Tests for skin override XML roundtrip."""

from pathlib import Path

from ams2_skins.models.livery_override import HelmetOverride
from ams2_skins.models.texture import TextureRef
from ams2_skins.xml.reader import load_car_document
from ams2_skins.xml.writer import serialize_car_document

EXAMPLE_XML = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "example_skinpacks"
    / "StockCar STOCKPAP 2020"
    / "Vehicles"
    / "Textures"
    / "CustomLiveries"
    / "Overrides"
    / "stock_cruze_20"
    / "stock_cruze_20.xml"
)


def test_skin_xml_roundtrip_example_pack():
    original = load_car_document(EXAMPLE_XML, car_id="stock_cruze_20")
    assert len(original.liveries) == 23
    assert original.liveries[0].livery_id == 51
    assert original.liveries[0].name.startswith("#06")

    xml_text = serialize_car_document(original)
    reloaded = load_car_document_from_text(xml_text, car_id="stock_cruze_20")

    assert len(reloaded.liveries) == len(original.liveries)
    assert reloaded.liveries[0].name == original.liveries[0].name
    assert reloaded.liveries[0].textures[0].path == original.liveries[0].textures[0].path


def test_skin_xml_includes_helmet_override():
    from ams2_skins.models.car_document import CarOverrideDocument
    from ams2_skins.models.livery_override import LiveryOverride

    doc = CarOverrideDocument(
        car_id="test_car",
        liveries=[
            LiveryOverride(
                livery_id=51,
                name="Team #51",
                base_livery="Default",
                textures=[TextureRef("BODY", "team/body.dds")],
            )
        ],
        helmets=[
            HelmetOverride(
                livery_id=51,
                base_helmet="DEFAULT",
                enabled=True,
                textures=[TextureRef("HELMET", "team/helmet.dds")],
            )
        ],
    )
    xml_text = serialize_car_document(doc)
    assert "HELMET_OVERRIDE" in xml_text
    reloaded = load_car_document_from_text(xml_text, car_id="test_car")
    assert len(reloaded.helmets) == 1
    assert reloaded.helmets[0].textures[0].path == "team/helmet.dds"


def load_car_document_from_text(text: str, *, car_id: str):
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False, encoding="utf-8") as handle:
        handle.write(text)
        path = Path(handle.name)
    try:
        return load_car_document(path, car_id=car_id)
    finally:
        path.unlink(missing_ok=True)
