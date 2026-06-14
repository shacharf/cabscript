from ..model.project import ResolvedProject


def generate_front_elevation(project: ResolvedProject) -> str:
    """Generate a minimal SVG front elevation."""
    scale = 0.1  # mm to px
    w = project.width * scale
    h = project.height * scale
    pad = 20

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{w + 2 * pad}" height="{h + 2 * pad}" '
        f'viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}">',
        f'<rect x="0" y="0" width="{w}" height="{h}" '
        f'fill="none" stroke="#333" stroke-width="1"/>',
    ]

    for part in project.parts:
        if part.axes.thickness_axis == "z":  # front-facing parts
            px = part.origin.x * scale
            py = (project.height - part.origin.y - part.width) * scale
            pw = part.length * scale
            ph = part.width * scale
            lines.append(
                f'<rect x="{px:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" '
                f'fill="none" stroke="#666" stroke-width="0.5"/>'
            )

    lines.append("</svg>")
    return "\n".join(lines)
