"""Saw-cut nesting: pack cabinet parts onto stock boards.

Groups parts by (material, thickness) since parts of differing thickness cannot
share a board, then runs a shelf-based First-Fit-Decreasing guillotine packing
for each group. Parts that carry a grain direction keep their orientation; parts
with no grain may be rotated 90 degrees to fit.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..model.project import ResolvedProject
from ..stdlib.loader import StdLib

# Saw blade kerf added as a gutter around every placement (mm).
KERF = 3.0

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


def _board_size(stdlib: StdLib, material: str) -> tuple[float, float]:
    try:
        spec = stdlib.get_material(material)
        return float(spec.max_board.length), float(spec.max_board.width)
    except Exception:
        return DEFAULT_BOARD


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


def _orient(rect: _PartRect, board_w: float, board_h: float) -> tuple[float, float, bool]:
    """Choose a board-space orientation (w along x, h along y).

    Board grain runs along its length (the x / ``board_w`` axis). A part with a
    grain direction must keep that edge parallel to the board grain, so its
    orientation is fixed. Grain-free parts may rotate; we prefer the longer side
    along x and fall back to a 90° turn only when needed to fit the board height.
    Returns (w, h, rotated).
    """
    length, width = rect.length, rect.width
    if rect.grain == "length":
        return length, width, False
    if rect.grain == "width":
        return width, length, False
    # Grain-free: prefer larger x-extent that still fits within the board.
    candidates = [(length, width, False), (width, length, True)]
    for w, h, rotated in sorted(candidates, key=lambda c: -c[0]):
        if w <= board_w + 1e-6 and h <= board_h + 1e-6:
            return w, h, rotated
    return candidates[0]


def _pack_group(
    material: str,
    thickness: float,
    rects: list[_PartRect],
    board_w: float,
    board_h: float,
    start_index: int,
) -> list[Board]:
    """Shelf-based FFD packing of one (material, thickness) group."""
    # Largest first so shelves are seeded by the biggest parts.
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
        w, h, rotated = _orient(rect, board_w, board_h)
        pw, ph = w + KERF, h + KERF  # footprint including kerf gutter
        placed = False

        # Try existing shelves (first fit).
        for board, shelf in shelves:
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
            continue

        # Open a new shelf on an existing board if it fits vertically.
        for board in boards:
            board_used_h = max(
                (s.y + s.height for b, s in shelves if b is board),
                default=0.0,
            )
            if board_used_h + ph <= board_h + 1e-6 and pw <= board_w + 1e-6:
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
        board_w, board_h = _board_size(stdlib, material)
        boards = _pack_group(
            material, thickness, rects, board_w, board_h, next_index
        )
        all_boards.extend(boards)
        next_index += len(boards)
    return all_boards
