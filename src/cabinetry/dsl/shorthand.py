import re
from typing import Any
from .dimensions import parse_3d_dimensions
from ..model.layout import BayFunction


def parse_bay_function(text: str) -> BayFunction:
    text = text.strip()

    if text == "storage":
        return BayFunction(kind="storage")
    if text == "empty":
        return BayFunction(kind="empty")
    if text == "hanging":
        return BayFunction(kind="hanging")
    if text == "hooks":
        return BayFunction(kind="hooks")

    # hanging rod <height>
    m = re.match(r"^hanging\s+rod\s+(\d+(?:\.\d+)?)$", text)
    if m:
        return BayFunction(kind="hanging", params={"rod_height": float(m.group(1))})

    # shelves <count> [adjustable]
    m = re.match(r"^shelves\s+(\d+)(?:\s+(adjustable))?$", text)
    if m:
        params: dict[str, Any] = {"count": int(m.group(1))}
        if m.group(2):
            params["adjustable"] = True
        return BayFunction(kind="shelves", params=params)

    # shoes <count>
    m = re.match(r"^shoes\s+(\d+)$", text)
    if m:
        return BayFunction(kind="shoes", params={"rows": int(m.group(1))})

    # storage <height> — top-level shorthand used in layout.top
    m = re.match(r"^storage\s+\d+", text)
    if m:
        return BayFunction(kind="storage")

    # drawers [count]
    m = re.match(r"^drawers(?:\s+(\d+))?$", text)
    if m:
        params: dict[str, Any] = {"count": int(m.group(1))} if m.group(1) else {}
        return BayFunction(kind="drawers", params=params)

    raise ValueError(f"Cannot parse bay function: {text!r}")


def _normalize_layout_columns(columns_raw: Any) -> list[dict]:
    """Convert shorthand columns dict into list of {width, function} dicts."""
    rows = []
    if isinstance(columns_raw, dict):
        cols = []
        for k, v in columns_raw.items():
            width = "*" if str(k) == "*" else float(k)
            fn = parse_bay_function(str(v)) if isinstance(v, str) else BayFunction(kind="storage")
            cols.append({"width": width, "function": fn.model_dump()})
        rows.append({"height": "*", "columns": cols})
    return rows


def _normalize_layout_section(section_raw: Any) -> dict:
    """Normalize a layout section (main or top) into {rows: [...]}."""
    if isinstance(section_raw, str):
        # e.g. "storage 380" — single full-width storage bay
        fn = parse_bay_function(section_raw)
        return {
            "rows": [
                {
                    "height": "*",
                    "columns": [{"width": "*", "function": fn.model_dump()}],
                }
            ]
        }
    if isinstance(section_raw, dict):
        if "columns" in section_raw:
            return {"rows": _normalize_layout_columns(section_raw["columns"])}
        if "rows" in section_raw:
            return section_raw
    return {"rows": []}


def normalize_shorthand(raw: dict) -> dict:
    result = dict(raw)

    # Normalize `use: euro_builtin_v1` → `use: {standard: euro_builtin_v1}`
    if "use" in result and isinstance(result["use"], str):
        result["use"] = {"standard": result["use"]}

    # Normalize `material: plywood_18` → move into `use`
    if "material" in result and isinstance(result["material"], str):
        use = result.setdefault("use", {})
        if isinstance(use, dict):
            use["material"] = result.pop("material")

    # Normalize `space: niche 1200 x 2650 x 600`
    if "space" in result and isinstance(result["space"], str):
        text = result["space"].strip()
        if text.startswith("niche "):
            dims_str = text[len("niche "):].strip()
            w, h, d = parse_3d_dimensions(dims_str)
            result["space"] = {
                "kind": "niche",
                "niche": {"width": w, "height": h, "depth": d},
            }

    # Normalize layout shorthands — accept any section name, not just "main"/"top"
    if "layout" in result and isinstance(result["layout"], dict):
        layout = result["layout"]
        normalized_layout: dict = {}
        for section_key in layout:
            normalized_layout[section_key] = _normalize_layout_section(layout[section_key])
        result["layout"] = normalized_layout

    return result
