import pytest
from cabinetry.stdlib.loader import StdLib
from cabinetry.dsl.errors import StdLibLookupError


def test_load_standard():
    stdlib = StdLib()
    spec = stdlib.get_standard("euro_builtin_v1")
    assert spec.construction == "frameless"
    assert spec.clearances.side_each == 8


def test_load_material():
    stdlib = StdLib()
    mat = stdlib.get_material("plywood_18")
    assert mat.body_thickness == 18
    assert mat.back_thickness == 6


def test_load_door_system():
    stdlib = StdLib()
    ds = stdlib.get_door_system("concealed_full_overlay")
    assert ds.overlay == "full"
    assert len(ds.hinge_count_rule) > 0


def test_load_shelf_system():
    stdlib = StdLib()
    ss = stdlib.get_shelf_system("shelf_pins_32")
    assert ss.type == "shelf_pins"
    assert ss.hole_spacing == 32


def test_unknown_standard():
    stdlib = StdLib()
    with pytest.raises(StdLibLookupError, match="Unknown standard"):
        stdlib.get_standard("nonexistent_v99")


def test_all_standards():
    stdlib = StdLib()
    standards = stdlib.all_standards()
    assert "euro_builtin_v1" in standards
