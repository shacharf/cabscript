from typing import Literal
from pydantic import BaseModel, Field
from .primitives import Mm, Vec3


class HardwareItem(BaseModel):
    id: str
    kind: Literal["hinge", "shelf_pin", "rod", "leg", "handle", "drawer_slide", "screw"]
    name: str
    position: Vec3 | None = None
    params: dict = Field(default_factory=dict)
