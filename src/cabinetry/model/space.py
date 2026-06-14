from typing import Literal
from pydantic import BaseModel
from .primitives import Mm


class NicheSpec(BaseModel):
    width: Mm
    height: Mm
    depth: Mm


class SpaceSpec(BaseModel):
    kind: Literal["niche", "free"]
    niche: NicheSpec | None = None
