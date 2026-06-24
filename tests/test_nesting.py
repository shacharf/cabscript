from cabinetry.compiler.compile import compile_dsl
from cabinetry.outputs.nesting import nest_parts, KERF, _PartRect, _pack_group

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


def test_opcut_packs_mixed_parts_onto_two_boards():
    """Regression: opcut must fit 3×(650×1150) + 2×(697×650) + 2×(691×588)
    onto exactly 2 boards (2420×1220).  The shelf-FFD heuristic used to need 3.

    Board layout found by opcut (FORWARD_GREEDY):
      Board 0: 3 portrait talls side by side  → 1950 × 1150
      Board 1: 2 landscape mids left + 2 smalls stacked on right
               (697+697=1394 wide / 588+2+588=1178 tall in right column)
    """
    rects = (
        [_PartRect(f"tall_{i}", f"Tall {i}", 1150.0, 650.0, "none", "") for i in range(3)]
        + [_PartRect(f"mid_{i}", f"Mid {i}", 697.0, 650.0, "none", "") for i in range(2)]
        + [_PartRect(f"sm_{i}", f"Small {i}", 691.0, 588.0, "none", "") for i in range(2)]
    )
    boards = _pack_group("mat", 18.0, rects, 2420.0, 1220.0, 2.0, 1)
    assert len(boards) == 2, f"Expected 2 boards, got {len(boards)}"
    counts = sorted(len(b.placements) for b in boards)
    assert counts == [3, 4], f"Expected [3,4] pieces per board, got {counts}"
