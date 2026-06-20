"""Validate driver entries before save."""

from __future__ import annotations

from ams2_ai.models.document import AIDocument
from ams2_ai.models.parameters import NUMERIC_KEYS, PARAMETER_BY_KEY, validate_country


def validate_document(document: AIDocument) -> list[str]:
    errors: list[str] = []
    if not document.drivers:
        errors.append("Document has no driver entries.")

    for index, driver in enumerate(document.drivers, start=1):
        label = driver.display_name() or f"Driver #{index}"
        if not driver.livery_name.strip():
            errors.append(f"{label}: livery_name is required.")
        if driver.country and not validate_country(driver.country):
            errors.append(f"{label}: country must be a 3-letter code.")
        if driver.is_track_override and not driver.tracks.strip():
            errors.append(f"{label}: track override requires a track name.")
        if driver.is_track_override and not any(
            key in driver.set_fields for key in NUMERIC_KEYS
        ):
            continue

        for key in driver.set_fields:
            if key not in PARAMETER_BY_KEY or key not in driver.values:
                continue
            param = PARAMETER_BY_KEY[key]
            value = driver.values[key]
            if value < param.xml_min or value > param.xml_max:
                if param.key != "vehicle_reliability":
                    errors.append(
                        f"{label}: {param.label} must be between "
                        f"{param.xml_min} and {param.xml_max}."
                    )

    return errors
