"""Generate a front-view SVG of a resolved cabinet project with dimensions."""

from __future__ import annotations

from html import escape

from ..model.project import ResolvedProject

# mm to px conversion — larger than cut_svg.py for better readability
SCALE = 0.35
PAD_LEFT = 55
PAD_RIGHT = 70  # room for per-bay dim labels
PAD_TOP = 30
PAD_BOTTOM = 55

_BAY_FILL = {
    "shelves":         "#4a7fc420",
    "hanging":         "#d47a3020",
    "shoes":           "#3ab46020",
    "storage":         "#78808820",
    "drawers":         "#8040b020",
    "drawers_no_front": "#8040b014",
    "hooks":           "#c0a83020",
    "empty":           "#ffffff08",
}
_BAY_STROKE = {
    "shelves":         "#4a7fc440",
    "hanging":         "#d47a3040",
    "shoes":           "#3ab46040",
    "storage":         "#78808840",
    "drawers":         "#8040b040",
    "drawers_no_front": "#8040b030",
    "hooks":           "#c0a83040",
    "empty":           "#ffffff18",
}
_WOOD = "#7a6a50"
_WOOD_STROKE = "#a08060"
_SHELF_FILL = "#8a7855"
_SHELF_STROKE = "#b09a70"
_DIM_COLOR = "#90b4e0"


def _part_xy(part):
    """Replicate frontend partXY: derive x, y, w, h from origin + axes."""
    sz: dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}
    sz[part.axes.length_axis] += part.length
    sz[part.axes.width_axis] += part.width
    sz[part.axes.thickness_axis] += part.thickness
    return part.origin.x, part.origin.y, sz["x"], sz["y"]


def project_to_svg(project: ResolvedProject) -> str:
    """Return a front-view SVG string matching the View2d canvas rendering."""
    S = SCALE
    pw = project.width
    ph = project.height

    total_w = pw * S + PAD_LEFT + PAD_RIGHT
    total_h = ph * S + PAD_TOP + PAD_BOTTOM

    def sx(x: float) -> float:
        return PAD_LEFT + x * S

    def sy(y: float) -> float:
        # model y=0 is bottom; SVG y=0 is top
        return PAD_TOP + (ph - y) * S

    def ss(v: float) -> float:
        return v * S

    lines: list[str] = []

    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_w:.1f}" height="{total_h:.1f}" '
        f'viewBox="0 0 {total_w:.1f} {total_h:.1f}" '
        f'font-family="sans-serif">'
    )

    # Cabinet interior background
    lines.append(
        f'<rect x="{sx(0):.1f}" y="{sy(ph):.1f}" '
        f'width="{ss(pw):.1f}" height="{ss(ph):.1f}" fill="#0d1525"/>'
    )

    # Bay zones
    for bay in project.bays:
        bx, by = sx(bay.x), sy(bay.y + bay.height)
        bw, bh = ss(bay.width), ss(bay.height)
        fill = _BAY_FILL.get(bay.function.kind, "#96a0b420")
        stroke = _BAY_STROKE.get(bay.function.kind, "#96a0b440")
        lines.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="0.5"/>'
        )

        # Drawer divisions
        if bay.function.kind in ("drawers", "drawers_no_front"):
            no_front = bay.function.kind == "drawers_no_front"
            count = int(bay.function.params.get("count", 3))
            if count > 0:
                drawer_h = bh / count
                dash = 'stroke-dasharray="4 4"' if no_front else ""
                for i in range(1, count):
                    ly = by + i * drawer_h
                    lines.append(
                        f'<line x1="{bx + 2:.1f}" y1="{ly:.1f}" '
                        f'x2="{bx + bw - 2:.1f}" y2="{ly:.1f}" '
                        f'stroke="#b482f060" stroke-width="1" {dash}/>'
                    )
                if not no_front:
                    handle_w = min(40, bw * 0.35)
                    handle_h = max(2, drawer_h * 0.1)
                    for i in range(count):
                        center_y = by + (i + 0.5) * drawer_h
                        hx = bx + (bw - handle_w) / 2
                        hy = center_y - handle_h / 2
                        lines.append(
                            f'<rect x="{hx:.1f}" y="{hy:.1f}" '
                            f'width="{handle_w:.1f}" height="{handle_h:.1f}" '
                            f'fill="#b482f060"/>'
                        )

    # Structural panels (side, top, bottom, divider)
    STRUCTURAL = {"side_panel", "top_panel", "bottom_panel", "divider"}
    for part in project.parts:
        if part.kind not in STRUCTURAL:
            continue
        x, y, w, h = _part_xy(part)
        if w < 0.5 or h < 0.5:
            continue
        px, py = sx(x), sy(y + h)
        is_vertical_div = part.kind == "divider" and part.axes.thickness_axis == "x"
        is_horizontal_div = part.kind == "divider" and part.axes.thickness_axis == "y"
        if is_vertical_div:
            pw_s = ss(max(w, 2))   # w == thickness; ensure min visible width
            ph_s = ss(h)
        elif is_horizontal_div:
            pw_s = ss(w)           # w == full inner width
            ph_s = ss(max(h, 2))   # h == thickness; ensure min visible height
        else:
            pw_s = ss(w)
            ph_s = ss(h)
        stroke_w = 1 if part.kind == "divider" else 0.5
        stroke_c = "#c0a070" if part.kind == "divider" else _WOOD_STROKE
        lines.append(
            f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw_s:.1f}" height="{ph_s:.1f}" '
            f'fill="{_WOOD}" stroke="{stroke_c}" stroke-width="{stroke_w}"/>'
        )

    # Shelves
    for part in project.parts:
        if part.kind != "shelf":
            continue
        x, y, w, h = _part_xy(part)
        thickness = max(2, ss(part.thickness))
        lx, ly = sx(x), sy(y + h) - thickness / 2
        lw = ss(w)
        lines.append(
            f'<rect x="{lx:.1f}" y="{ly:.1f}" width="{lw:.1f}" height="{thickness:.1f}" '
            f'fill="{_SHELF_FILL}" stroke="{_SHELF_STROKE}" stroke-width="0.5"/>'
        )

    # Hanging rods
    for hw in project.hardware:
        if hw.kind != "rod" or hw.position is None:
            continue
        half_len = float(hw.params.get("length", 200)) / 2
        ry = sy(hw.position.y)
        rx1 = sx(hw.position.x - half_len)
        rx2 = sx(hw.position.x + half_len)
        lines.append(
            f'<line x1="{rx1:.1f}" y1="{ry:.1f}" x2="{rx2:.1f}" y2="{ry:.1f}" '
            f'stroke="#aabbcc" stroke-width="3" stroke-linecap="round"/>'
        )
        for ex in [rx1, rx2]:
            lines.append(
                f'<circle cx="{ex:.1f}" cy="{ry:.1f}" r="4" fill="#aabbcc"/>'
            )

    # Bay labels
    for bay in project.bays:
        cx_bay = sx(bay.x + bay.width / 2)
        cy_bay = sy(bay.y + bay.height / 2)
        label = bay.function.kind[0].upper() + bay.function.kind[1:]
        label = escape(label.replace("_", " ").title())
        font_size = min(13, max(9, ss(40)))
        lines.append(
            f'<text x="{cx_bay:.1f}" y="{cy_bay:.1f}" font-size="{font_size:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'fill="#b4c8f0b0">{label}</text>'
        )
        if ss(bay.width) > 40:
            label_y = sy(bay.y + bay.height) - 6
            lines.append(
                f'<text x="{cx_bay:.1f}" y="{label_y:.1f}" '
                f'font-size="{max(8, font_size - 2):.1f}" '
                f'text-anchor="middle" dominant-baseline="middle" '
                f'fill="#8ca0c896">{round(bay.width)}</text>'
            )

    # Per-bay height dimensions (right side)
    label_x = sx(project.width) + 8
    seen_keys: set[str] = set()
    unique_bays = []
    for bay in project.bays:
        key = f"{bay.y}:{bay.height}"
        if key not in seen_keys:
            seen_keys.add(key)
            unique_bays.append(bay)

    for bay in unique_bays:
        mid_y = sy(bay.y + bay.height / 2)
        top_y = sy(bay.y + bay.height)
        bot_y = sy(bay.y)
        tick_x = sx(project.width) + 2
        line_x = label_x + 4
        lines.append(
            f'<line x1="{tick_x:.1f}" y1="{top_y:.1f}" x2="{line_x + 24:.1f}" y2="{top_y:.1f}" '
            f'stroke="{_DIM_COLOR}40" stroke-width="0.5"/>'
        )
        lines.append(
            f'<line x1="{tick_x:.1f}" y1="{bot_y:.1f}" x2="{line_x + 24:.1f}" y2="{bot_y:.1f}" '
            f'stroke="{_DIM_COLOR}40" stroke-width="0.5"/>'
        )
        lines.append(
            f'<line x1="{line_x:.1f}" y1="{top_y:.1f}" x2="{line_x:.1f}" y2="{bot_y:.1f}" '
            f'stroke="{_DIM_COLOR}40" stroke-width="0.5"/>'
        )
        if bay.function.kind in ("drawers", "drawers_no_front"):
            count = int(bay.function.params.get("count", 3))
            dh = round(bay.height / count)
            dim_text = escape(f"{dh}×{count}")
        else:
            dim_text = str(round(bay.height))
        lines.append(
            f'<text x="{label_x + 8:.1f}" y="{mid_y:.1f}" font-size="9" '
            f'text-anchor="start" dominant-baseline="middle" '
            f'fill="{_DIM_COLOR}c0">{dim_text}</text>'
        )

    # Overall width dimension (bottom)
    dim_line_y = sy(0) + 32
    lines.append(
        f'<line x1="{sx(0):.1f}" y1="{sy(0) + 6:.1f}" '
        f'x2="{sx(0):.1f}" y2="{dim_line_y + 4:.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    lines.append(
        f'<line x1="{sx(pw):.1f}" y1="{sy(0) + 6:.1f}" '
        f'x2="{sx(pw):.1f}" y2="{dim_line_y + 4:.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    lines.append(
        f'<line x1="{sx(0):.1f}" y1="{dim_line_y:.1f}" '
        f'x2="{sx(pw):.1f}" y2="{dim_line_y:.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    lines.append(
        f'<text x="{sx(pw / 2):.1f}" y="{dim_line_y + 14:.1f}" font-size="12" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'fill="{_DIM_COLOR}">{round(pw)} mm</text>'
    )

    # Overall height dimension (left side)
    dim_line_x = sx(0) - 32
    lines.append(
        f'<line x1="{sx(0) - 6:.1f}" y1="{sy(0):.1f}" '
        f'x2="{dim_line_x - 4:.1f}" y2="{sy(0):.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    lines.append(
        f'<line x1="{sx(0) - 6:.1f}" y1="{sy(ph):.1f}" '
        f'x2="{dim_line_x - 4:.1f}" y2="{sy(ph):.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    lines.append(
        f'<line x1="{dim_line_x:.1f}" y1="{sy(0):.1f}" '
        f'x2="{dim_line_x:.1f}" y2="{sy(ph):.1f}" '
        f'stroke="{_DIM_COLOR}90" stroke-width="1"/>'
    )
    mid_h = (sy(0) + sy(ph)) / 2
    lines.append(
        f'<text x="{dim_line_x - 14:.1f}" y="{mid_h:.1f}" font-size="12" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'fill="{_DIM_COLOR}" '
        f'transform="rotate(-90 {dim_line_x - 14:.1f} {mid_h:.1f})">'
        f'{round(ph)} mm</text>'
    )

    # Module split lines
    for mod in project.modules:
        if mod.y == 0:
            continue
        my = sy(mod.y)
        lines.append(
            f'<line x1="{sx(0):.1f}" y1="{my:.1f}" '
            f'x2="{sx(pw):.1f}" y2="{my:.1f}" '
            f'stroke="#b4c8ff30" stroke-width="1" stroke-dasharray="6 4"/>'
        )

    lines.append("</svg>")
    return "\n".join(lines)
