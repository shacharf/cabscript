from pydantic import BaseModel
from .primitives import Mm


class SheetSize(BaseModel):
    length: Mm
    width: Mm


class MaterialSpec(BaseModel):
    name: str = ""
    body_thickness: Mm
    shelf_thickness: Mm
    door_thickness: Mm
    back_thickness: Mm
    max_board: SheetSize
    cut_width: float = 2.0
    density_kg_m3: float | None = None
    default_finish: str | None = None
