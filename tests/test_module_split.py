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


NAMED_MODULES_DSL = """
use: euro_builtin_v1
material: plywood_18
space: niche 1200 x 2650 x 600
cabinet:
  type: built_in
  base: legs 80
  modules:
    - id: drawers_unit
      height: 800
    - id: hanging
      height: 1000
    - id: top_shelf
      height: "*"
layout:
  drawers_unit: drawers 3
  hanging: hanging rod 900
  top_shelf: shelves 1 adjustable
doors:
  drawers_unit: none
  hanging: auto
  top_shelf: auto
  style: slab
  hinges: concealed
finish:
  body: warm_white
  doors: oak
"""


def test_named_modules_ids():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    ids = [m.id for m in project.modules]
    assert ids == ["drawers_unit", "hanging", "top_shelf"]


def test_named_modules_heights_sum():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    total = sum(m.height for m in project.modules)
    # body height = niche_height - top_clearance - base
    # 2650 - 10 (top clearance) - 80 (legs) = 2560
    assert abs(total - 2560) < 1


def test_named_modules_star_height():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    top = next(m for m in project.modules if m.id == "top_shelf")
    # star = 2560 - 800 - 1000 = 760
    assert abs(top.height - 760) < 1


def test_named_modules_bays_map_to_modules():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    bay_modules = {b.module_id for b in project.bays}
    assert bay_modules == {"drawers_unit", "hanging", "top_shelf"}


def test_named_modules_drawers_parts():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    drawer_fronts = [p for p in project.parts if p.kind == "drawer_front"]
    assert len(drawer_fronts) == 3


def test_named_modules_no_doors_on_drawers():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    door_module_ids = {p.module_id for p in project.parts if p.kind == "door"}
    assert "drawers_unit" not in door_module_ids


def test_named_modules_doors_on_hanging_and_top():
    _, project = compile_dsl(NAMED_MODULES_DSL)
    door_module_ids = {p.module_id for p in project.parts if p.kind == "door"}
    assert "hanging" in door_module_ids
    assert "top_shelf" in door_module_ids
