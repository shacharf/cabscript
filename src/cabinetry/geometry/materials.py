from ..stdlib.loader import StdLib

_stdlib = StdLib()

_DEFAULT_COLORS: dict[str, tuple[int, int, int, int]] = {
    "body": (245, 240, 235, 255),
    "doors": (180, 140, 90, 255),
    "shelves": (245, 240, 235, 255),
    "back": (220, 215, 210, 255),
    "default": (200, 200, 200, 255),
}

_ROLE_KINDS = {
    "body": {"side_panel", "top_panel", "bottom_panel", "rail", "cleat", "filler", "plinth"},
    "doors": {"door", "drawer_front"},
    "shelves": {"shelf", "divider"},
    "back": {"back_panel"},
}


def resolve_part_color(
    part_kind: str, finish: dict[str, str]
) -> tuple[int, int, int, int]:
    # Determine role
    role = "default"
    for r, kinds in _ROLE_KINDS.items():
        if part_kind in kinds:
            role = r
            break

    finish_name = finish.get(role)
    if finish_name:
        try:
            color_spec = _stdlib.get_color(finish_name)
            return color_spec.rgba
        except Exception:
            pass

    return _DEFAULT_COLORS.get(role, _DEFAULT_COLORS["default"])
