import pytest
from cabinetry.dsl.parser import parse_dsl
from cabinetry.dsl.errors import DslSyntaxError


def test_valid_yaml():
    result = parse_dsl("key: value\nother: 123")
    assert result == {"key": "value", "other": 123}


def test_empty_document():
    with pytest.raises(DslSyntaxError, match="empty"):
        parse_dsl("")


def test_none_document():
    with pytest.raises(DslSyntaxError):
        parse_dsl("~")


def test_non_mapping():
    with pytest.raises(DslSyntaxError, match="mapping"):
        parse_dsl("- item1\n- item2")


def test_invalid_yaml():
    with pytest.raises(DslSyntaxError):
        parse_dsl("key: [unclosed")
