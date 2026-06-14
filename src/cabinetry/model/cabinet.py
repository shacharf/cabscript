from typing import Literal
from pydantic import BaseModel
from .primitives import Mm


class ModuleSpec(BaseModel):
    id: str
    height: Mm | Literal["*"]


class CabinetRequest(BaseModel):
    type: Literal["built_in", "standing", "kitchen_base", "kitchen_wall", "wardrobe"]
    width: Mm | Literal["auto"] = "auto"
    height: Mm | Literal["auto"] = "auto"
    depth: Mm | Literal["auto"] = "auto"
    split: Literal["auto", "none"] | list[Mm] = "auto"
    base: str | None = None
    modules: list[ModuleSpec] | None = None


class ResolvedModule(BaseModel):
    id: str
    name: str
    x: Mm
    y: Mm
    z: Mm
    width: Mm
    depth: Mm
    height: Mm
