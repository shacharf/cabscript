from cabinetry.compiler.compile import compile_dsl

DSL_WITH_DOORS = """
use: euro_builtin_v1
material: plywood_18
space: niche 1200 x 2650 x 600
cabinet:
  type: built_in
  split: auto
  base: legs 80
layout:
  top: storage 380
  main:
    columns:
      "*": shelves 3
doors:
  top: auto
  main: auto
  style: slab
  hinges: concealed
"""


def test_doors_generated():
    _, project = compile_dsl(DSL_WITH_DOORS)
    doors = [p for p in project.parts if p.kind == "door"]
    assert len(doors) > 0


def test_hinges_generated():
    _, project = compile_dsl(DSL_WITH_DOORS)
    hinges = [h for h in project.hardware if h.kind == "hinge"]
    assert len(hinges) > 0


def test_door_in_front_of_cabinet():
    _, project = compile_dsl(DSL_WITH_DOORS)
    doors = [p for p in project.parts if p.kind == "door"]
    for door in doors:
        assert door.origin.z < 0, f"Door {door.id} should be in front (z<0)"
