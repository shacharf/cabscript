from pydantic import BaseModel, Field
from .cabinet import ResolvedModule
from .layout import ResolvedBay
from .parts import Part
from .hardware import HardwareItem
from .validation import ValidationMessage


class ResolvedProject(BaseModel):
    units: str = "mm"
    standard: str
    material: str
    width: float
    height: float
    depth: float
    modules: list[ResolvedModule] = Field(default_factory=list)
    bays: list[ResolvedBay] = Field(default_factory=list)
    parts: list[Part] = Field(default_factory=list)
    hardware: list[HardwareItem] = Field(default_factory=list)
    warnings: list[ValidationMessage] = Field(default_factory=list)
