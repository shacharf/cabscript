from typing import Literal
from pydantic import BaseModel, Field
from .primitives import Mm, Vec3, PartAxes

PartKind = Literal[
    "side_panel",
    "top_panel",
    "bottom_panel",
    "shelf",
    "divider",
    "back_panel",
    "door",
    "drawer_front",
    "filler",
    "plinth",
    "rail",
    "cleat",
]

EdgeName = Literal["front", "back", "left", "right", "top", "bottom"]


class Operation(BaseModel):
    kind: str
    params: dict = Field(default_factory=dict)


class Part(BaseModel):
    id: str
    name: str
    kind: PartKind
    module_id: str | None = None
    material: str

    length: Mm
    width: Mm
    thickness: Mm

    origin: Vec3
    axes: PartAxes

    grain_direction: Literal["length", "width", "none"] = "none"
    edge_banding: list[EdgeName] = Field(default_factory=list)
    operations: list[Operation] = Field(default_factory=list)
