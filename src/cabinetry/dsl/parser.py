import yaml
from .errors import DslSyntaxError


def parse_dsl(text: str) -> dict:
    if not text or not text.strip():
        raise DslSyntaxError("DSL document is empty.")
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise DslSyntaxError(f"YAML parse error: {e}") from e
    if doc is None:
        raise DslSyntaxError("DSL document is empty.")
    if not isinstance(doc, dict):
        raise DslSyntaxError(
            f"DSL document must be a YAML mapping (dict), got {type(doc).__name__}."
        )
    return doc
