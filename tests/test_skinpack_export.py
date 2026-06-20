"""Minimal skinpack fixture for export tests."""

from __future__ import annotations

from pathlib import Path

from ams2_skins.export.skinpack import (
    export_car_xml,
    export_skinpack_to_folder,
    load_skinpack_from_folder,
)
from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.livery_override import LiveryOverride
from ams2_skins.models.skinpack import SkinpackDocument
from ams2_skins.models.texture import TextureRef

FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1] / "docs" / "example_skinpacks" / "minimal_fixture"
)


def test_export_minimal_skinpack(tmp_path: Path):
    source_root = FIXTURE_ROOT
    if not source_root.is_dir():
        return

    pack = load_skinpack_from_folder(source_root)
    export_skinpack_to_folder(pack, tmp_path / "exported")
    exported_xml = (
        tmp_path
        / "exported"
        / "Vehicles"
        / "Textures"
        / "CustomLiveries"
        / "Overrides"
        / "stock_cruze_20"
        / "stock_cruze_20.xml"
    )
    assert exported_xml.is_file()


def test_scaffold_and_export_programmatic(tmp_path: Path):
    pack_root = tmp_path / "MyPack"
    pack = SkinpackDocument(root_path=pack_root, name="MyPack")
    car = CarOverrideDocument(
        car_id="demo_car",
        folder_path=pack_root / "Vehicles/Textures/CustomLiveries/Overrides/demo_car",
        xml_path=pack_root / "Vehicles/Textures/CustomLiveries/Overrides/demo_car/demo_car.xml",
        liveries=[
            LiveryOverride(
                livery_id=51,
                name="Demo #51",
                base_livery="Default",
                preview_path="demo/preview.dds",
                textures=[TextureRef("BODY", "demo/body.dds")],
            )
        ],
    )
    car.folder_path.mkdir(parents=True, exist_ok=True)
    pack.cars.append(car)
    export_car_xml(car)
    assert car.xml_path.is_file()

    export_skinpack_to_folder(pack, tmp_path / "out")
    out_xml = (
        tmp_path
        / "out"
        / "Vehicles"
        / "Textures"
        / "CustomLiveries"
        / "Overrides"
        / "demo_car"
        / "demo_car.xml"
    )
    assert out_xml.is_file()
