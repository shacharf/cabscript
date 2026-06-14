from __future__ import annotations
from pydantic import BaseModel
from ..model.primitives import Mm


class CabinetDefaults(BaseModel):
    default_depth: Mm


class ClearancesSpec(BaseModel):
    side_each: Mm
    top: Mm
    back: Mm
    door_gap: Mm


class FillersSpec(BaseModel):
    side: str
    top: str


class CarcassSpec(BaseModel):
    top_panel: bool
    bottom_panel: bool
    back_panel: bool
    back_panel_method: str


class ModuleSplitSpec(BaseModel):
    mode: str
    default_main_height: Mm
    min_top_module_height: Mm
    max_single_module_height_margin: Mm


class ShelfDefaultsSpec(BaseModel):
    default_support: str
    adjustable_shelf_clearance: Mm


class DoorDefaultsSpec(BaseModel):
    default_system: str
    default_style: str


class StandardSpec(BaseModel):
    construction: str
    cabinet: CabinetDefaults
    clearances: ClearancesSpec
    fillers: FillersSpec
    carcass: CarcassSpec
    module_split: ModuleSplitSpec
    shelf: ShelfDefaultsSpec
    doors: DoorDefaultsSpec


class HingeCountRule(BaseModel):
    max_height: Mm
    count: int


class DoorSystemSpec(BaseModel):
    hinge_type: str
    overlay: str
    gap: Mm
    cup_diameter: Mm
    cup_depth: Mm
    default_cup_distance_from_edge: Mm
    hinge_count_rule: list[HingeCountRule]


class MiddleRailSpec(BaseModel):
    min_height: Mm
    count: int


class DoorStyleSpec(BaseModel):
    type: str
    frame_width: Mm | None = None
    frame_thickness: Mm | None = None
    panel_thickness: Mm | None = None
    groove_depth: Mm | None = None
    middle_rail: MiddleRailSpec | None = None


class ShelfSystemSpec(BaseModel):
    type: str
    pin_diameter: Mm | None = None
    hole_spacing: Mm | None = None
    front_offset: Mm | None = None
    back_offset: Mm | None = None
    hole_depth: Mm | None = None
    cleat_height: Mm | None = None
    cleat_thickness: Mm | None = None


class BaseSystemSpec(BaseModel):
    type: str
    height: Mm
    plinth: str | None = None
    front_setback: Mm | None = None


class ColorSpec(BaseModel):
    rgba: tuple[int, int, int, int]
    description: str | None = None
