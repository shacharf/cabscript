from cabinetry.compiler.compile import compile_dsl


TALL_DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 1200 x 2650 x 600
cabinet:
  type: built_in
  split: auto
  base: legs 80
layout:
  main:
    columns:
      "*": shelves 3
"""

SHORT_DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 1200 x 1800 x 600
cabinet:
  type: built_in
  split: auto
  base: legs 80
layout:
  main:
    columns:
      "*": shelves 3
"""


def test_tall_cabinet_splits():
    _, project = compile_dsl(TALL_DSL)
    assert len(project.modules) == 2
    module_ids = {m.id for m in project.modules}
    assert "mod_main" in module_ids
    assert "mod_top" in module_ids


def test_short_cabinet_no_split():
    _, project = compile_dsl(SHORT_DSL)
    assert len(project.modules) == 1
    assert project.modules[0].id == "mod_main"


def test_split_heights_sum():
    _, project = compile_dsl(TALL_DSL)
    base_h = 80
    total_body = sum(m.height for m in project.modules)
    # Body height = cabinet height - base
    expected_cabinet_h = 2650 - 10  # minus top clearance
    expected_body = expected_cabinet_h - base_h
    assert abs(total_body - expected_body) < 1
