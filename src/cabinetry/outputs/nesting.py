"""Saw-cut nesting: pack cabinet parts onto stock boards.

Groups parts by (material, thickness) since parts of differing thickness cannot
share a board, then uses opcut's guillotine optimizer to minimise the number of
boards required for each group.  Parts that carry a grain direction keep their
orientation; parts with no grain may be rotated 90 degrees.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import opcut.common as _oc
from opcut.csp import calculate as _opcut_calculate

from ..model.project import ResolvedProject
from ..stdlib.loader import StdLib

# Saw blade kerf / cut width (mm) used when the material spec has no cut_width.
KERF = 2.0

# Fallback board size when a material has no max_board (mm).
DEFAULT_BOARD = (2400.0, 1200.0)

# Part kinds that have real board geometry worth nesting.
NESTABLE_KINDS = {
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
}


@dataclass
class PlacedPart:
    part_id: str
    label: str
    x: float
    y: float
    w: float
    h: float
    rotated: bool
    formica_side: str


@dataclass
class Board:
    index: int
    material: str
    thickness: float
    board_w: float
    board_h: float
    placements: list[PlacedPart] = field(default_factory=list)

    @property
    def used_area(self) -> float:
        return sum(p.w * p.h for p in self.placements)

    @property
    def waste_pct(self) -> float:
        total = self.board_w * self.board_h
        if total <= 0:
            return 0.0
        return 100.0 * (1.0 - self.used_area / total)


@dataclass
class _PartRect:
    part_id: str
    label: str
    length: float
    width: float
    grain: str
    formica_side: str

    @property
    def long_side(self) -> float:
        return max(self.length, self.width)


def _board_size(stdlib: StdLib, material: str) -> tuple[float, float, float]:
    """Return (board_w, board_h, cut_width) for *material*."""
    try:
        spec = stdlib.get_material(material)
        cut_width = float(getattr(spec, "cut_width", KERF))
        return float(spec.max_board.length), float(spec.max_board.width), cut_width
    except Exception:
        return DEFAULT_BOARD[0], DEFAULT_BOARD[1], KERF


def _part_rects(
    project: ResolvedProject, ignore_grain: bool = False
) -> dict[tuple[str, float], list[_PartRect]]:
    """Bucket nestable parts by (material, thickness) into packable rectangles."""
    groups: dict[tuple[str, float], list[_PartRect]] = {}
    for part in project.parts:
        if part.kind not in NESTABLE_KINDS:
            continue
        w = round(part.width, 2)
        h = round(part.length, 2)
        if w <= 0 or h <= 0:
            continue
        key = (part.material, round(part.thickness, 2))
        groups.setdefault(key, []).append(
            _PartRect(
                part_id=part.id,
                label=part.name,
                length=h,
                width=w,
                grain="none" if ignore_grain else part.grain_direction,
                formica_side="|".join(part.edge_banding),
            )
        )
    return groups


def _pack_group(
    material: str,
    thickness: float,
    rects: list[_PartRect],
    board_w: float,
    board_h: float,
    cut_width: float,
    start_index: int,
) -> list[Board]:
    """Pack one (material, thickness) group onto boards using opcut.

    Tries the fewest panels that the area lower-bound implies, then increments
    until opcut finds a valid arrangement or every piece gets its own board.
    """
    # Build opcut items.  Grain direction fixes can_rotate.
    # For grain="width" we swap dims so the item's natural orientation places
    # rect.width along the board's x-axis (matching _orient's original intent).
    def _item_dims(rect: _PartRect) -> tuple[float, float]:
        if rect.grain == "width":
            return rect.width, rect.length  # width along x, not rotatable
        return rect.length, rect.width      # length along x (default / grain="length")

    items = [
        _oc.Item(
            id=rect.part_id,
            width=iw,
            height=ih,
            can_rotate=(rect.grain == "none"),
        )
        for rect, (iw, ih) in ((r, _item_dims(r)) for r in rects)
    ]
    rect_by_id = {r.part_id: r for r in rects}

    total_area = sum(iw * ih for _, (iw, ih) in ((r, _item_dims(r)) for r in rects))
    board_area = board_w * board_h
    min_panels = max(1, math.ceil(total_area / board_area))

    for n_panels in range(min_panels, len(rects) + 1):
        panels = [
            _oc.Panel(id=str(i), width=board_w, height=board_h)
            for i in range(n_panels)
        ]
        params = _oc.Params(cut_width=cut_width, panels=panels, items=items)
        try:
            result = _opcut_calculate(params, _oc.Method.FORWARD_GREEDY)
        except _oc.UnresolvableError:
            continue

        # Group placements by panel id (preserving panel order).
        boards_map: dict[str, Board] = {}
        for used in result.used:
            pid = used.panel.id
            if pid not in boards_map:
                boards_map[pid] = Board(
                    index=0,
                    material=material,
                    thickness=thickness,
                    board_w=board_w,
                    board_h=board_h,
                )
            rect = rect_by_id[used.item.id]
            # Dimensions after opcut rotation: rotate swaps width↔height.
            if used.rotate:
                placed_w, placed_h = used.item.height, used.item.width
            else:
                placed_w, placed_h = used.item.width, used.item.height
            boards_map[pid].placements.append(
                PlacedPart(
                    part_id=used.item.id,
                    label=rect.label,
                    x=used.x,
                    y=used.y,
                    w=placed_w,
                    h=placed_h,
                    rotated=used.rotate,
                    formica_side=rect.formica_side,
                )
            )

        # Re-index boards sequentially starting from start_index.
        sorted_boards = sorted(boards_map.items(), key=lambda kv: int(kv[0]))
        boards = []
        for i, (_, board) in enumerate(sorted_boards):
            board.index = start_index + i
            boards.append(board)
        return boards

    # Fallback: should never be reached (n_panels == len(rects) always works).
    raise RuntimeError(f"opcut could not pack {len(rects)} parts onto {len(rects)} boards")


def nest_parts(
    project: ResolvedProject,
    stdlib: StdLib | None = None,
    ignore_grain: bool = False,
) -> list[Board]:
    """Pack all nestable parts onto stock boards, returning boards in index order.

    When ``ignore_grain`` is True every part is treated as freely rotatable,
    which typically reduces the number of boards needed at the cost of parts
    potentially being cut cross-grain.
    """
    stdlib = stdlib or StdLib()
    groups = _part_rects(project, ignore_grain=ignore_grain)
    all_boards: list[Board] = []
    next_index = 1
    for (material, thickness), rects in sorted(groups.items()):
        board_w, board_h, cut_width = _board_size(stdlib, material)
        boards = _pack_group(
            material, thickness, rects, board_w, board_h, cut_width, next_index
        )
        all_boards.extend(boards)
        next_index += len(boards)
    return all_boards
