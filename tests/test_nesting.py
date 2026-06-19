from cabinetry.compiler.compile import compile_dsl
from cabinetry.outputs.nesting import nest_parts, KERF

DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 1000 x 2000 x 580
cabinet:
  type: built_in
  split: none
  base: legs 80
layout:
  main:
    columns:
      "*": shelves 3
"""


def _boards():
    _, project = compile_dsl(DSL)
    return nest_parts(project)


def test_produces_boards():
    boards = _boards()
    assert len(boards) >= 1
    assert all(b.placements for b in boards)


def test_placements_within_bounds():
    for board in _boards():
        for p in board.placements:
            assert p.x >= -1e-6
            assert p.y >= -1e-6
            assert p.x + p.w <= board.board_w + 1e-6
            assert p.y + p.h <= board.board_h + 1e-6


def test_placements_do_not_overlap():
    for board in _boards():
        placed = board.placements
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                a, b = placed[i], placed[j]
                # Rectangles (including kerf gutter) must not overlap.
                separated = (
                    a.x + a.w + KERF <= b.x + 1e-6
                    or b.x + b.w + KERF <= a.x + 1e-6
                    or a.y + a.h + KERF <= b.y + 1e-6
                    or b.y + b.h + KERF <= a.y + 1e-6
                )
                assert separated, f"{a.part_id} overlaps {b.part_id}"


def test_grain_parts_not_rotated():
    _, project = compile_dsl(DSL)
    grained = {p.id for p in project.parts if p.grain_direction != "none"}
    for board in nest_parts(project):
        for p in board.placements:
            if p.part_id in grained:
                assert not p.rotated
