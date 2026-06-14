from ..model.parts import Part


def part_box_size(part: Part) -> tuple[float, float, float]:
    """Return rendered box size in global X/Y/Z from part axes."""
    size = {"x": 0.0, "y": 0.0, "z": 0.0}
    size[part.axes.length_axis] = part.length
    size[part.axes.width_axis] = part.width
    size[part.axes.thickness_axis] = part.thickness
    return size["x"], size["y"], size["z"]
