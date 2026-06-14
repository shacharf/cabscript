from cabinetry.compiler.compile import compile_dsl
from cabinetry.geometry.export import export_glb

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
      "*": shelves 2
"""


def test_glb_bytes():
    _, project = compile_dsl(DSL)
    glb = export_glb(project)
    assert isinstance(glb, bytes)
    assert len(glb) > 0
    # GLB magic bytes
    assert glb[:4] == b"glTF"


def test_glb_has_parts():
    _, project = compile_dsl(DSL)
    assert len(project.parts) > 0
