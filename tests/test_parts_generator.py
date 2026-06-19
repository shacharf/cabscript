from cabinetry.compiler.compile import compile_dsl

MULTI_SHELF_COUNT_DSL = """
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
      "500": shelves 3
      "*": shelves 5
"""

DRAWERS_NO_FRONT_DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 600 x 2000 x 580
cabinet:
  type: built_in
  split: none
  base: legs 80
layout:
  main:
    columns:
      "*": drawers 4 no_front
"""

SIMPLE_DSL = """
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


def test_side_panels_generated():
    _, project = compile_dsl(SIMPLE_DSL)
    sides = [p for p in project.parts if p.kind == "side_panel"]
    assert len(sides) == 2  # left and right for one module


def test_top_bottom_panels():
    _, project = compile_dsl(SIMPLE_DSL)
    tops = [p for p in project.parts if p.kind == "top_panel"]
    bottoms = [p for p in project.parts if p.kind == "bottom_panel"]
    assert len(tops) >= 1
    assert len(bottoms) >= 1


def test_back_panel():
    _, project = compile_dsl(SIMPLE_DSL)
    backs = [p for p in project.parts if p.kind == "back_panel"]
    assert len(backs) >= 1


def test_shelves_generated():
    _, project = compile_dsl(SIMPLE_DSL)
    shelves = [p for p in project.parts if p.kind == "shelf"]
    assert len(shelves) == 3


def test_different_shelf_counts_per_column():
    _, project = compile_dsl(MULTI_SHELF_COUNT_DSL)
    shelves = [p for p in project.parts if p.kind == "shelf"]
    assert len(shelves) == 8, f"Expected 8 shelves (3+5), got {len(shelves)}"


def test_drawers_no_front_generates_no_drawer_fronts():
    _, project = compile_dsl(DRAWERS_NO_FRONT_DSL)
    fronts = [p for p in project.parts if p.kind == "drawer_front"]
    assert len(fronts) == 0, f"Expected 0 drawer fronts for no_front drawers, got {len(fronts)}"


def test_parts_have_dimensions():
    _, project = compile_dsl(SIMPLE_DSL)
    for part in project.parts:
        assert part.length > 0, f"{part.id} has zero length"
        assert part.width > 0, f"{part.id} has zero width"
        assert part.thickness > 0, f"{part.id} has zero thickness"
