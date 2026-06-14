from cabinetry.compiler.compile import compile_dsl
from cabinetry.outputs.cutlist import generate_cutlist, cutlist_to_csv

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


def test_cutlist_groups_identical():
    _, project = compile_dsl(DSL)
    items = generate_cutlist(project)
    # 3 shelves should be grouped into 1 line item with quantity 3
    shelf_items = [i for i in items if i.kind == "shelf"]
    assert len(shelf_items) == 1
    assert shelf_items[0].quantity == 3


def test_cutlist_dimensions_from_parts():
    _, project = compile_dsl(DSL)
    items = generate_cutlist(project)
    for item in items:
        assert item.length > 0
        assert item.width > 0
        assert item.thickness > 0


def test_cutlist_csv():
    _, project = compile_dsl(DSL)
    items = generate_cutlist(project)
    csv_str = cutlist_to_csv(items)
    lines = csv_str.strip().split("\n")
    assert lines[0].startswith("quantity")
    assert len(lines) > 1
