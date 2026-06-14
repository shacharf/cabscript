from typing import Literal
from pydantic import BaseModel

Mm = float


class Vec3(BaseModel):
    x: Mm
    y: Mm
    z: Mm


class Size3(BaseModel):
    width: Mm
    depth: Mm
    height: Mm


AxisName = Literal["x", "y", "z"]


class PartAxes(BaseModel):
    length_axis: AxisName
    width_axis: AxisName
    thickness_axis: AxisName
