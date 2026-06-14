from __future__ import annotations
import yaml
from pathlib import Path
from ..model.materials import MaterialSpec
from ..dsl.errors import StdLibLookupError
from .specs import (
    StandardSpec,
    DoorSystemSpec,
    DoorStyleSpec,
    ShelfSystemSpec,
    BaseSystemSpec,
    ColorSpec,
)

_STDLIB_DIR = Path(__file__).parent


def _load_yaml(filename: str) -> dict:
    path = _STDLIB_DIR / filename
    with open(path) as f:
        return yaml.safe_load(f) or {}


class StdLib:
    def __init__(self) -> None:
        self._standards: dict | None = None
        self._materials: dict | None = None
        self._door_systems: dict | None = None
        self._door_styles: dict | None = None
        self._shelf_systems: dict | None = None
        self._base_systems: dict | None = None
        self._colors: dict | None = None

    def _standards_data(self) -> dict:
        if self._standards is None:
            self._standards = _load_yaml("standards.yaml")
        return self._standards

    def _materials_data(self) -> dict:
        if self._materials is None:
            self._materials = _load_yaml("materials.yaml")
        return self._materials

    def _door_systems_data(self) -> dict:
        if self._door_systems is None:
            self._door_systems = _load_yaml("door_systems.yaml")
        return self._door_systems

    def _door_styles_data(self) -> dict:
        if self._door_styles is None:
            self._door_styles = _load_yaml("door_styles.yaml")
        return self._door_styles

    def _shelf_systems_data(self) -> dict:
        if self._shelf_systems is None:
            self._shelf_systems = _load_yaml("shelf_systems.yaml")
        return self._shelf_systems

    def _base_systems_data(self) -> dict:
        if self._base_systems is None:
            self._base_systems = _load_yaml("base_systems.yaml")
        return self._base_systems

    def _colors_data(self) -> dict:
        if self._colors is None:
            self._colors = _load_yaml("colors.yaml")
        return self._colors

    def _lookup(self, data: dict, name: str, label: str) -> dict:
        if name not in data:
            available = ", ".join(sorted(data.keys()))
            raise StdLibLookupError(
                f"Unknown {label}: {name!r}. Available: {available}"
            )
        return data[name]

    def get_standard(self, name: str) -> StandardSpec:
        data = self._lookup(self._standards_data(), name, "standard")
        return StandardSpec(**data)

    def get_material(self, name: str) -> MaterialSpec:
        data = self._lookup(self._materials_data(), name, "material")
        return MaterialSpec(name=name, **data)

    def get_door_system(self, name: str) -> DoorSystemSpec:
        data = self._lookup(self._door_systems_data(), name, "door_system")
        return DoorSystemSpec(**data)

    def get_door_style(self, name: str) -> DoorStyleSpec:
        data = self._lookup(self._door_styles_data(), name, "door_style")
        return DoorStyleSpec(**data)

    def get_shelf_system(self, name: str) -> ShelfSystemSpec:
        data = self._lookup(self._shelf_systems_data(), name, "shelf_system")
        return ShelfSystemSpec(**data)

    def get_base_system(self, name: str) -> BaseSystemSpec:
        data = self._lookup(self._base_systems_data(), name, "base_system")
        return BaseSystemSpec(**data)

    def get_color(self, name: str) -> ColorSpec:
        data = self._lookup(self._colors_data(), name, "color")
        return ColorSpec(**data)

    def all_standards(self) -> list[str]:
        return sorted(self._standards_data().keys())

    def all_materials(self) -> list[str]:
        return sorted(self._materials_data().keys())

    def all_colors(self) -> dict:
        return dict(self._colors_data())
