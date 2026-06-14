import re
from .errors import DslSyntaxError


def parse_3d_dimensions(text: str) -> tuple[float, float, float]:
    """Parse '1200 x 2650 x 600' into width, height, depth."""
    pattern = r"^\s*(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)\s*$"
    m = re.match(pattern, text)
    if not m:
        raise DslSyntaxError(
            f"Invalid 3D dimension string: {text!r}. Expected format: '1200 x 2650 x 600'."
        )
    return float(m.group(1)), float(m.group(2)), float(m.group(3))
