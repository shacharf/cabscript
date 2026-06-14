import pytest
from cabinetry.dsl.dimensions import parse_3d_dimensions
from cabinetry.dsl.errors import DslSyntaxError


def test_spaced():
    assert parse_3d_dimensions("1200 x 2650 x 600") == (1200.0, 2650.0, 600.0)


def test_nospaces():
    assert parse_3d_dimensions("1200x2650x600") == (1200.0, 2650.0, 600.0)


def test_uppercase_x():
    assert parse_3d_dimensions("1200 X 2650 X 600") == (1200.0, 2650.0, 600.0)


def test_invalid():
    with pytest.raises(DslSyntaxError):
        parse_3d_dimensions("1200 x 2650")


def test_invalid_text():
    with pytest.raises(DslSyntaxError):
        parse_3d_dimensions("wide x tall x deep")
