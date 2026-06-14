from cabinetry.compiler.compile import compile_dsl


MULTI_COL_DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 1200 x 2200 x 600
cabinet:
  type: built_in
  split: none
  base: legs 80
layout:
  main:
    columns:
      400: shelves 3
      "*": hanging
"""


def test_column_widths():
    _, project = compile_dsl(MULTI_COL_DSL)
    bays = project.bays
    assert len(bays) == 2
    widths = sorted(b.width for b in bays)
    assert widths[0] == 400.0
    # Star column gets the rest
    # inner_width = (1200 - 2*8 - 2*18) = 1148
    expected_star = 1200 - 2 * 8 - 2 * 18 - 400
    assert abs(widths[1] - expected_star) < 1


def test_bay_functions():
    _, project = compile_dsl(MULTI_COL_DSL)
    kinds = {b.function.kind for b in project.bays}
    assert "shelves" in kinds
    assert "hanging" in kinds
