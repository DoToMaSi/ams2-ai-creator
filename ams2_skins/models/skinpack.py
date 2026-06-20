"""Skinpack project containing one or more car override documents."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ams2_skins.models.car_document import CarOverrideDocument

OVERRIDES_SUFFIX = Path("Vehicles/Textures/CustomLiveries/Overrides")


@dataclass
class SkinpackDocument:
    root_path: Path | None = None
    name: str = ""
    notes: str = ""
    cars: list[CarOverrideDocument] = field(default_factory=list)
    dirty: bool = False

    @property
    def display_name(self) -> str:
        if self.name.strip():
            return self.name.strip()
        if self.root_path:
            return self.root_path.name
        return "Untitled Skinpack"

    @property
    def overrides_root(self) -> Path | None:
        if not self.root_path:
            return None
        return self.root_path / OVERRIDES_SUFFIX

    def mark_dirty(self) -> None:
        self.dirty = True

    def mark_clean(self) -> None:
        self.dirty = False

    def get_car(self, car_id: str) -> CarOverrideDocument | None:
        for car in self.cars:
            if car.car_id == car_id:
                return car
        return None

    def add_car(self, car: CarOverrideDocument) -> None:
        if self.get_car(car.car_id):
            raise ValueError(f"Car already in pack: {car.car_id}")
        self.cars.append(car)
        self.mark_dirty()

    def remove_car(self, car_id: str) -> None:
        self.cars = [car for car in self.cars if car.car_id != car_id]
        self.mark_dirty()
