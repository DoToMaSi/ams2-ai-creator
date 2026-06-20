"""Scan AMS2 install Overrides folder for vehicle metadata."""

from __future__ import annotations

import logging
from pathlib import Path

from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.catalog.limits import get_livery_limit
from ams2_skins.xml.dist_parser import parse_dist_file

logger = logging.getLogger("ams2_skins.catalog.scanner")

OVERRIDES_RELATIVE = Path("Vehicles/Textures/CustomLiveries/Overrides")


def overrides_path(ams2_root: Path) -> Path:
    return ams2_root / OVERRIDES_RELATIVE


def scan_ams2_catalog(ams2_root: Path) -> list[VehicleCatalogEntry]:
    root = overrides_path(ams2_root)
    if not root.is_dir():
        logger.warning("Overrides folder not found: %s", root)
        return []

    entries: list[VehicleCatalogEntry] = []
    for folder in sorted(root.iterdir()):
        if not folder.is_dir():
            continue
        dist_files = list(folder.glob("*_dist.xml"))
        if not dist_files:
            continue
        dist_path = dist_files[0]
        if dist_path.stem.endswith("_dist"):
            folder_id = dist_path.stem[: -len("_dist")]
        else:
            folder_id = folder.name
        try:
            metadata = parse_dist_file(dist_path, car_id=folder_id)
        except OSError as exc:
            logger.warning("Failed to parse dist for %s: %s", folder_id, exc)
            continue

        limit = get_livery_limit(folder_id)
        display_name = folder_id.replace("_", " ").title()
        max_livery_id = None
        has_limit = False
        if limit:
            display_name = str(limit.get("display_name") or display_name)
            raw_max = limit.get("max_livery_id")
            if raw_max is not None:
                max_livery_id = int(raw_max)
                has_limit = True

        entries.append(
            VehicleCatalogEntry(
                folder_id=folder_id,
                xml_filename=f"{folder_id}.xml",
                display_name=display_name,
                dist_path=str(dist_path),
                base_liveries=metadata.base_liveries,
                helmet_bases=metadata.helmet_bases,
                helmet_texture_names=metadata.helmet_texture_names,
                max_livery_id=max_livery_id,
                has_livery_limit=has_limit,
            )
        )

    entries.sort(key=lambda item: item.sort_key())
    logger.info("Scanned %d vehicles from %s", len(entries), root)
    return entries
