"""Validate skin override documents before save/export."""

from __future__ import annotations

from ams2_skins.catalog.entry import VehicleCatalogEntry
from ams2_skins.models.car_document import CarOverrideDocument
from ams2_skins.models.skinpack import SkinpackDocument

MIN_LIVERY_ID = 51


def split_validation_messages(messages: list[str]) -> tuple[list[str], list[str]]:
    errors = [item for item in messages if not item.startswith("Warning:")]
    warnings = [item.removeprefix("Warning: ") for item in messages if item.startswith("Warning:")]
    return errors, warnings


def validate_car_document(
    document: CarOverrideDocument,
    *,
    catalog_entry: VehicleCatalogEntry | None = None,
    check_files: bool = False,
) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[int] = set()
    max_id = catalog_entry.max_livery_id if catalog_entry else None

    if catalog_entry and not catalog_entry.has_livery_limit:
        errors.append(
            f"{document.car_id}: max livery ID unknown — add entry to livery_limits.json "
            "or set a custom max in the UI."
        )

    for livery in document.liveries:
        label = f"Livery {livery.livery_id}"
        if livery.livery_id in seen_ids:
            errors.append(f"{label}: duplicate livery ID.")
        seen_ids.add(livery.livery_id)

        if livery.livery_id < MIN_LIVERY_ID:
            errors.append(f"{label}: livery ID must be >= {MIN_LIVERY_ID}.")
        if max_id is not None and livery.livery_id > max_id:
            errors.append(f"{label}: livery ID exceeds max ({max_id}).")
        if not livery.name.strip():
            errors.append(f"{label}: NAME is required.")

        if catalog_entry and livery.base_livery not in {
            spec.name for spec in catalog_entry.base_liveries
        }:
            warnings.append(f"{label}: unknown base livery {livery.base_livery!r}.")

        if check_files:
            _check_texture_paths(document, livery.preview_path, f"{label} preview", warnings)
            for texture in livery.textures:
                _check_texture_paths(document, texture.path, f"{label} {texture.name}", warnings)

    for helmet in document.helmets:
        label = f"Helmet {helmet.livery_id}"
        if not helmet.textures:
            errors.append(
                f"{label}: at least one texture is required when helmet override is enabled."
            )
        if check_files:
            for texture in helmet.textures:
                _check_texture_paths(document, texture.path, f"{label} {texture.name}", warnings)

    return errors + [f"Warning: {item}" for item in warnings]


def validate_skinpack(
    pack: SkinpackDocument,
    *,
    catalog: dict[str, VehicleCatalogEntry] | None = None,
    check_files: bool = False,
) -> list[str]:
    if not pack.cars:
        return ["Skinpack has no cars."]
    errors: list[str] = []
    for car in pack.cars:
        entry = catalog.get(car.car_id) if catalog else None
        errors.extend(validate_car_document(car, catalog_entry=entry, check_files=check_files))
    return errors


def _check_texture_paths(
    document: CarOverrideDocument,
    relative_path: str,
    label: str,
    warnings: list[str],
) -> None:
    if not relative_path.strip():
        return
    if not relative_path.lower().endswith(".dds"):
        warnings.append(f"{label}: path should reference a .dds file.")
    resolved = document.resolve_texture_path(relative_path)
    if resolved is None:
        warnings.append(f"{label}: cannot resolve path {relative_path!r}.")
    elif not resolved.is_file():
        warnings.append(f"{label}: missing file {relative_path!r}.")
