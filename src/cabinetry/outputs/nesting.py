"""Saw-cut nesting: pack cabinet parts onto stock boards.

Groups parts by (material, thickness) since parts of differing thickness cannot
share a board, then packs each group using opcut's guillotine optimiser when
available, or a shelf-based First-Fit-Decreasing heuristic otherwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

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

try:
    import opcut.common as _oc
    from opcut.csp import calculate as _opcut_calculate
    _OPCUT_AVAILABLE = True
except ImportError:
    _OPCUT_AVAILABLE = False


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
class _Shelf:
    """A horizontal band on the board into which parts are packed left to right."""

    y: float
    height: float
    cursor_x: float = 0.0


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


# ---------------------------------------------------------------------------
# Heuristic packer (shelf-based FFD, always available)
# ---------------------------------------------------------------------------

def _free_orients(
    rect: _PartRect, board_w: float, board_h: float, cut_width: float
) -> list[tuple[float, float, bool]]:
    """All orientations valid for grain-free placement on this board size.

    For fixed-grain parts returns the single required orientation.  For
    grain-free parts returns both orientations that physically fit the board,
    sorted so the one that yields the most pieces per board-width row comes
    first (better global utilisation).
    """
    length, width = rect.length, rect.width
    if rect.grain == "length":
        return [(length, width, False)]
    if rect.grain == "width":
        return [(width, length, False)]
    candidates: list[tuple[float, float, bool]] = []
    if length <= board_w + 1e-6 and width <= board_h + 1e-6:
        candidates.append((length, width, False))
    if (width, length) != (length, width) and width <= board_w + 1e-6 and length <= board_h + 1e-6:
        candidates.append((width, length, True))
    if not candidates:
        return [(length, width, False)]
    return sorted(candidates, key=lambda c: -(board_w // (c[0] + cut_width)))


def _pack_group_heuristic(
    material: str,
    thickness: float,
    rects: list[_PartRect],
    board_w: float,
    board_h: float,
    cut_width: float,
    start_index: int,
) -> list[Board]:
    """Shelf-based FFD packing of one (material, thickness) group."""
    ordered = sorted(rects, key=lambda r: r.long_side, reverse=True)

    boards: list[Board] = []
    shelves: list[tuple[Board, _Shelf]] = []
    index = start_index

    def new_board() -> Board:
        nonlocal index
        board = Board(
            index=index,
            material=material,
            thickness=thickness,
            board_w=board_w,
            board_h=board_h,
        )
        boards.append(board)
        index += 1
        return board

    for rect in ordered:
        orients = _free_orients(rect, board_w, board_h, cut_width)
        placed = False

        # Try existing shelves (first fit) — try all valid orientations.
        for board, shelf in shelves:
            for w, h, rotated in orients:
                pw, ph = w + cut_width, h + cut_width
                if shelf.cursor_x + pw <= board_w + 1e-6 and ph <= shelf.height + 1e-6:
                    board.placements.append(
                        PlacedPart(
                            part_id=rect.part_id,
                            label=rect.label,
                            x=shelf.cursor_x,
                            y=shelf.y,
                            w=w,
                            h=h,
                            rotated=rotated,
                            formica_side=rect.formica_side,
                        )
                    )
                    shelf.cursor_x += pw
                    placed = True
                    break
            if placed:
                break
        if placed:
            continue

        # Open a new shelf on an existing board.
        for board in boards:
            board_used_h = max(
                (s.y + s.height for b, s in shelves if b is board),
                default=0.0,
            )
            best: tuple[float, float, bool, float, float] | None = None
            for w, h, rotated in orients:
                pw, ph = w + cut_width, h + cut_width
                if board_used_h + ph <= board_h + 1e-6 and pw <= board_w + 1e-6:
                    best = (w, h, rotated, pw, ph)
                    break
            if best is not None:
                w, h, rotated, pw, ph = best
                shelf = _Shelf(y=board_used_h, height=ph, cursor_x=pw)
                board.placements.append(
                    PlacedPart(
                        part_id=rect.part_id,
                        label=rect.label,
                        x=0.0,
                        y=shelf.y,
                        w=w,
                        h=h,
                        rotated=rotated,
                        formica_side=rect.formica_side,
                    )
                )
                shelves.append((board, shelf))
                placed = True
                break
        if placed:
            continue

        # New board, new shelf.
        w, h, rotated = orients[0]
        pw, ph = w + cut_width, h + cut_width
        board = new_board()
        shelf = _Shelf(y=0.0, height=ph, cursor_x=pw)
        board.placements.append(
            PlacedPart(
                part_id=rect.part_id,
                label=rect.label,
                x=0.0,
                y=0.0,
                w=w,
                h=h,
                rotated=rotated,
                formica_side=rect.formica_side,
            )
        )
        shelves.append((board, shelf))

    return boards


# ---------------------------------------------------------------------------
# opcut packer (guillotine optimiser, Linux x86-64 only)
# ---------------------------------------------------------------------------

def _pack_group_opcut(
    material: str,
    thickness: float,
    rects: list[_PartRect],
    board_w: float,
    board_h: float,
    cut_width: float,
    start_index: int,
) -> list[Board]:
    """Pack via opcut's guillotine optimiser.

    Tries the fewest panels the area lower-bound implies, then increments
    until opcut finds a valid arrangement.
    """
    def _item_dims(rect: _PartRect) -> tuple[float, float]:
        if rect.grain == "width":
            return rect.width, rect.length
        return rect.length, rect.width

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

        sorted_boards = sorted(boards_map.items(), key=lambda kv: int(kv[0]))
        boards = []
        for i, (_, board) in enumerate(sorted_boards):
            board.index = start_index + i
            boards.append(board)
        return boards

    raise RuntimeError(f"opcut could not pack {len(rects)} parts onto {len(rects)} boards")


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def _pack_group(
    material: str,
    thickness: float,
    rects: list[_PartRect],
    board_w: float,
    board_h: float,
    cut_width: float,
    start_index: int,
) -> list[Board]:
    if _OPCUT_AVAILABLE:
        return _pack_group_opcut(
            material, thickness, rects, board_w, board_h, cut_width, start_index
        )
    return _pack_group_heuristic(
        material, thickness, rects, board_w, board_h, cut_width, start_index
    )


def nest_parts(
    project: ResolvedProject,
    stdlib: StdLib | None = None,
    ignore_grain: bool = False,
) -> list[Board]:
    """Pack all nestable parts onto stock boards, returning boards in index order.

    Uses opcut's guillotine optimiser when available (Linux), otherwise falls
    back to a shelf-based FFD heuristic.  When ``ignore_grain`` is True every
    part is treated as freely rotatable, typically reducing board count.
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
