from cabinetry.compiler.compile import compile_dsl

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


def test_parts_have_dimensions():
    _, project = compile_dsl(SIMPLE_DSL)
    for part in project.parts:
        assert part.length > 0, f"{part.id} has zero length"
        assert part.width > 0, f"{part.id} has zero width"
        assert part.thickness > 0, f"{part.id} has zero thickness"
