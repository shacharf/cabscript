from typing import Literal, Any
from pydantic import BaseModel, Field
from .primitives import Mm


class BayFunction(BaseModel):
    kind: Literal["shelves", "hanging", "drawers", "drawers_no_front", "shoes", "storage", "hooks", "empty"]
    params: dict[str, Any] = Field(default_factory=dict)


class ColumnSpec(BaseModel):
    width: Mm | Literal["*"]
    function: BayFunction


class RowSpec(BaseModel):
    height: Mm | Literal["*"]
    columns: list[ColumnSpec]


class LayoutSpec(BaseModel):
    rows: list[RowSpec]


class ResolvedBay(BaseModel):
    id: str
    module_id: str
    row_index: int
    col_index: int
    x: Mm
    y: Mm
    z: Mm
    width: Mm
    depth: Mm
    height: Mm
    function: BayFunction
