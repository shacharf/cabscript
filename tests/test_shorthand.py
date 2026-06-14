from cabinetry.dsl.shorthand import normalize_shorthand, parse_bay_function
from cabinetry.model.layout import BayFunction


def test_use_string():
    result = normalize_shorthand({"use": "euro_builtin_v1"})
    assert result["use"] == {"standard": "euro_builtin_v1"}


def test_material_shorthand():
    result = normalize_shorthand({"material": "plywood_18"})
    assert "material" not in result
    assert result["use"]["material"] == "plywood_18"


def test_space_niche():
    result = normalize_shorthand({"space": "niche 1200 x 2650 x 600"})
    assert result["space"]["kind"] == "niche"
    assert result["space"]["niche"]["width"] == 1200.0
    assert result["space"]["niche"]["height"] == 2650.0
    assert result["space"]["niche"]["depth"] == 600.0


def test_parse_bay_shelves_adjustable():
    fn = parse_bay_function("shelves 5 adjustable")
    assert fn.kind == "shelves"
    assert fn.params["count"] == 5
    assert fn.params["adjustable"] is True


def test_parse_bay_hanging_rod():
    fn = parse_bay_function("hanging rod 1700")
    assert fn.kind == "hanging"
    assert fn.params["rod_height"] == 1700.0


def test_parse_bay_shoes():
    fn = parse_bay_function("shoes 4")
    assert fn.kind == "shoes"
    assert fn.params["rows"] == 4


def test_parse_bay_storage():
    fn = parse_bay_function("storage")
    assert fn.kind == "storage"


def test_parse_bay_empty():
    fn = parse_bay_function("empty")
    assert fn.kind == "empty"
