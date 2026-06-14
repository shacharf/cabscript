import csv
import io
import json
from typing import Any
from pydantic import BaseModel
from ..model.project import ResolvedProject


class CutListItem(BaseModel):
    part_ids: list[str]
    name: str
    kind: str
    material: str
    length: float
    width: float
    thickness: float
    quantity: int
    grain_direction: str
    edge_banding: list[str]


def generate_cutlist(project: ResolvedProject) -> list[CutListItem]:
    groups: dict[tuple, CutListItem] = {}

    for part in project.parts:
        key = (
            part.kind,
            part.material,
            round(part.length, 2),
            round(part.width, 2),
            round(part.thickness, 2),
            part.grain_direction,
            tuple(sorted(part.edge_banding)),
        )
        if key in groups:
            existing = groups[key]
            existing.part_ids.append(part.id)
            existing.quantity += 1
        else:
            groups[key] = CutListItem(
                part_ids=[part.id],
                name=part.name,
                kind=part.kind,
                material=part.material,
                length=part.length,
                width=part.width,
                thickness=part.thickness,
                quantity=1,
                grain_direction=part.grain_direction,
                edge_banding=list(part.edge_banding),
            )

    return list(groups.values())


def cutlist_to_json(items: list[CutListItem]) -> str:
    return json.dumps([item.model_dump() for item in items], indent=2)


def cutlist_to_csv(items: list[CutListItem]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "quantity",
            "name",
            "kind",
            "material",
            "length",
            "width",
            "thickness",
            "grain_direction",
            "edge_banding",
            "part_ids",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.quantity,
                item.name,
                item.kind,
                item.material,
                item.length,
                item.width,
                item.thickness,
                item.grain_direction,
                "|".join(item.edge_banding),
                "|".join(item.part_ids),
            ]
        )
    return output.getvalue()
