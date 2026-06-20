"""Scaffold skinpack folders and export to disk."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.skinpack import OVERRIDES_SUFFIX, SkinpackDocument
from ams2_skins.xml.writer import save_car_document, serialize_car_document

logger = logging.getLogger("ams2_skins.export.skinpack")

EMPTY_OVERRIDES_XML = (
    '<?xml version="1.0" encoding="utf-8" ?>\n<USER_OVERRIDES>\n</USER_OVERRIDES>\n'
)


def car_folder_in_pack(pack_root: Path, car_id: str) -> Path:
    return pack_root / OVERRIDES_SUFFIX / car_id


def scaffold_car_in_pack(
    pack_root: Path,
    car_id: str,
    *,
    dist_source: Path | None = None,
) -> CarOverrideDocument:
    folder = car_folder_in_pack(pack_root, car_id)
    folder.mkdir(parents=True, exist_ok=True)

    if dist_source and dist_source.is_file():
        target_dist = folder / dist_source.name
        if not target_dist.exists():
            shutil.copy2(dist_source, target_dist)
    else:
        target_dist = folder / f"{car_id}_dist.xml"

    xml_path = folder / f"{car_id}.xml"
    if not xml_path.is_file():
        xml_path.write_text(EMPTY_OVERRIDES_XML, encoding="utf-8")

    return CarOverrideDocument(
        car_id=car_id,
        folder_path=folder,
        xml_path=xml_path,
    )


def scaffold_texture_folders(
    car: CarOverrideDocument,
    *,
    pack_label: str,
    slot_names: list[str],
) -> None:
    base = car.xml_directory
    if base is None:
        return
    for slot_name in slot_names:
        folder = base / pack_label / slot_name
        folder.mkdir(parents=True, exist_ok=True)


def export_car_xml(car: CarOverrideDocument) -> None:
    if car.xml_path is None:
        raise ValueError(f"No xml path for car {car.car_id}")
    save_car_document(car, car.xml_path)


def export_skinpack_to_folder(pack: SkinpackDocument, destination: Path) -> None:
    if pack.root_path is None:
        raise ValueError("Skinpack has no root path.")
    overrides_src = pack.overrides_root
    if overrides_src is None or not overrides_src.is_dir():
        raise ValueError("Skinpack overrides folder not found.")

    overrides_dest = destination / OVERRIDES_SUFFIX
    for car in pack.cars:
        car_src = overrides_src / car.car_id
        car_dest = overrides_dest / car.car_id
        car_dest.mkdir(parents=True, exist_ok=True)
        if car.xml_path and car.xml_path.is_file():
            content = serialize_car_document(car)
            (car_dest / car.xml_path.name).write_text(content, encoding="utf-8")
        for item in car_src.iterdir():
            if item.name == car.xml_path.name if car.xml_path else False:
                continue
            target = car_dest / item.name
            if item.is_dir():
                if target.exists():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copytree(item, target)
            elif item.name.endswith("_dist.xml"):
                if not target.exists():
                    shutil.copy2(item, target)
            elif not target.exists():
                shutil.copy2(item, target)


def export_skinpack_to_ams2(pack: SkinpackDocument, ams2_root: Path) -> None:
    export_skinpack_to_folder(pack, ams2_root)


def load_skinpack_from_folder(root: Path) -> SkinpackDocument:
    from ams2_skins.xml.reader import load_car_document

    overrides_root = root / OVERRIDES_SUFFIX
    pack = SkinpackDocument(root_path=root, name=root.name)
    if not overrides_root.is_dir():
        return pack

    for folder in sorted(overrides_root.iterdir()):
        if not folder.is_dir():
            continue
        xml_candidates = [p for p in folder.glob("*.xml") if not p.name.endswith("_dist.xml")]
        if not xml_candidates:
            continue
        xml_path = xml_candidates[0]
        car_id = xml_path.stem
        car = load_car_document(xml_path, car_id=car_id)
        pack.cars.append(car)

    return pack
