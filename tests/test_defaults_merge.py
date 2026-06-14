from cabinetry.compiler.defaults import deep_merge


def test_basic_merge():
    base = {"a": 1, "b": 2}
    override = {"b": 99, "c": 3}
    result = deep_merge(base, override)
    assert result == {"a": 1, "b": 99, "c": 3}


def test_nested_merge():
    base = {"a": {"x": 1, "y": 2}}
    override = {"a": {"y": 99, "z": 3}}
    result = deep_merge(base, override)
    assert result["a"] == {"x": 1, "y": 99, "z": 3}


def test_override_wins():
    base = {"key": "base_value"}
    override = {"key": "user_value"}
    result = deep_merge(base, override)
    assert result["key"] == "user_value"


def test_base_unchanged():
    base = {"a": 1}
    override = {"b": 2}
    deep_merge(base, override)
    assert "b" not in base
