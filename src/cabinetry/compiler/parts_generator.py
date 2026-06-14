from .context import CompileContext
from ..model.cabinet import ResolvedModule
from ..model.layout import ResolvedBay
from ..model.parts import Part
from ..model.primitives import Vec3, PartAxes
from ..model.hardware import HardwareItem


def _part_id(prefix: str, counter: list[int]) -> str:
    counter[0] += 1
    return f"{prefix}_{counter[0]:03d}"


def generate_carcass_parts(
    ctx: CompileContext, modules: list[ResolvedModule]
) -> list[Part]:
    parts: list[Part] = []
    t = ctx.material.body_thickness
    bt = ctx.material.back_thickness
    counter = [0]
    mat = ctx.material.name

    # Group modules into vertical stacks sharing the same x/width/z/depth column.
    stacks: dict[tuple, list[ResolvedModule]] = {}
    for mod in modules:
        key = (round(mod.x), round(mod.width), round(mod.z), round(mod.depth))
        stacks.setdefault(key, []).append(mod)

    for stack in stacks.values():
        stack.sort(key=lambda m: m.y)
        first = stack[0]
        gx, gw, gz, gd = first.x, first.width, first.z, first.depth
        gy = first.y
        gh = sum(m.height for m in stack)
        inner_w = gw - 2 * t

        # Left side — full stack height
        parts.append(Part(
            id=_part_id("side", counter), name="Left Side", kind="side_panel",
            module_id=first.id, material=mat,
            length=gh, width=gd, thickness=t,
            origin=Vec3(x=gx, y=gy, z=gz),
            axes=PartAxes(length_axis="y", width_axis="z", thickness_axis="x"),
            grain_direction="length", edge_banding=["front"],
        ))
        # Right side — full stack height
        parts.append(Part(
            id=_part_id("side", counter), name="Right Side", kind="side_panel",
            module_id=first.id, material=mat,
            length=gh, width=gd, thickness=t,
            origin=Vec3(x=gx + gw - t, y=gy, z=gz),
            axes=PartAxes(length_axis="y", width_axis="z", thickness_axis="x"),
            grain_direction="length", edge_banding=["front"],
        ))
        # Bottom panel
        parts.append(Part(
            id=_part_id("bottom", counter), name="Bottom", kind="bottom_panel",
            module_id=first.id, material=mat,
            length=inner_w, width=gd, thickness=t,
            origin=Vec3(x=gx + t, y=gy, z=gz),
            axes=PartAxes(length_axis="x", width_axis="z", thickness_axis="y"),
            grain_direction="length", edge_banding=["front"],
        ))
        # Top panel
        parts.append(Part(
            id=_part_id("top", counter), name="Top", kind="top_panel",
            module_id=first.id, material=mat,
            length=inner_w, width=gd, thickness=t,
            origin=Vec3(x=gx + t, y=gy + gh - t, z=gz),
            axes=PartAxes(length_axis="x", width_axis="z", thickness_axis="y"),
            grain_direction="length", edge_banding=["front"],
        ))
        # Back panel — full stack
        parts.append(Part(
            id=_part_id("back", counter), name="Back", kind="back_panel",
            module_id=first.id, material=mat,
            length=gh, width=gw, thickness=bt,
            origin=Vec3(x=gx, y=gy, z=gz + gd - bt),
            axes=PartAxes(length_axis="y", width_axis="x", thickness_axis="z"),
            grain_direction="none",
        ))
        # Horizontal dividers at module boundaries (N-1 for N stacked modules)
        for i in range(len(stack) - 1):
            div_y = stack[i].y + stack[i].height
            parts.append(Part(
                id=_part_id("div_h", counter), name="Horizontal Divider", kind="divider",
                module_id=stack[i].id, material=mat,
                length=inner_w, width=gd, thickness=t,
                origin=Vec3(x=gx + t, y=div_y, z=gz),
                axes=PartAxes(length_axis="x", width_axis="z", thickness_axis="y"),
                grain_direction="length", edge_banding=["front"],
            ))

    return parts


def generate_bay_parts(
    ctx: CompileContext, bays: list[ResolvedBay]
) -> tuple[list[Part], list[HardwareItem]]:
    parts: list[Part] = []
    hardware: list[HardwareItem] = []
    shelf_t = ctx.material.shelf_thickness
    mat = ctx.material.name
    counter = [0]
    hw_counter = [0]

    # Group shelf/shoe bays by row so that adjacent shelf columns produce a
    # single full-width shelf instead of separate per-bay pieces.
    shelf_clearance = 2.0
    shelf_row_groups: dict[tuple, list[ResolvedBay]] = {}
    for bay in bays:
        if bay.function.kind in ("shelves", "shoes"):
            key = (bay.module_id, bay.row_index)
            shelf_row_groups.setdefault(key, []).append(bay)

    for row_bays in shelf_row_groups.values():
        row_bays.sort(key=lambda b: b.col_index)
        left_bay = row_bays[0]
        right_bay = row_bays[-1]
        fn = left_bay.function
        count = fn.params.get("count", fn.params.get("rows", 3))
        # Merged shelf spans from leftmost bay's left edge to rightmost bay's right edge
        shelf_x = left_bay.x + shelf_clearance / 2
        shelf_length = (right_bay.x + right_bay.width) - left_bay.x - shelf_clearance
        shelf_width = left_bay.depth - 50  # front/rear clearance

        if count > 0:
            spacing = left_bay.height / (count + 1)
            for i in range(int(count)):
                y_pos = left_bay.y + spacing * (i + 1)
                counter[0] += 1
                pid = f"shelf_{counter[0]:03d}"
                parts.append(
                    Part(
                        id=pid,
                        name=f"Shelf {counter[0]}",
                        kind="shelf",
                        module_id=left_bay.module_id,
                        material=mat,
                        length=shelf_length,
                        width=shelf_width,
                        thickness=shelf_t,
                        origin=Vec3(
                            x=shelf_x,
                            y=y_pos,
                            z=left_bay.z + 25,
                        ),
                        axes=PartAxes(
                            length_axis="x", width_axis="z", thickness_axis="y"
                        ),
                        grain_direction="length",
                        edge_banding=["front"],
                    )
                )

    for bay in bays:
        fn = bay.function

        if fn.kind == "hanging":
            rod_height = fn.params.get("rod_height", bay.height - 100)
            hw_counter[0] += 1
            hardware.append(
                HardwareItem(
                    id=f"rod_{hw_counter[0]:03d}",
                    kind="rod",
                    name="Hanging Rod",
                    position=Vec3(
                        x=bay.x + bay.width / 2,
                        y=bay.y + rod_height,
                        z=bay.z + bay.depth / 2,
                    ),
                    params={"length": bay.width - 20, "diameter": 25},
                )
            )

        elif fn.kind == "drawers":
            count = int(fn.params.get("count", 3))
            if count < 1:
                continue
            drawer_h = bay.height / count
            front_length = bay.width - 4  # 2mm gap each side
            for i in range(count):
                y_pos = bay.y + i * drawer_h + 2  # 2mm gap below
                front_h = drawer_h - 4            # 2mm gap top + bottom
                counter[0] += 1
                parts.append(
                    Part(
                        id=f"drawer_front_{counter[0]:03d}",
                        name=f"Drawer Front {counter[0]}",
                        kind="drawer_front",
                        module_id=bay.module_id,
                        material=mat,
                        length=front_h,
                        width=front_length,
                        thickness=shelf_t,
                        origin=Vec3(x=bay.x + 2, y=y_pos, z=-shelf_t),
                        axes=PartAxes(
                            length_axis="y", width_axis="x", thickness_axis="z"
                        ),
                        grain_direction="length",
                        edge_banding=["front", "back", "left", "right"],
                    )
                )

    # Vertical dividers between adjacent columns in the same module row
    row_groups: dict[tuple, list[ResolvedBay]] = {}
    for bay in bays:
        key = (bay.module_id, bay.row_index)
        row_groups.setdefault(key, []).append(bay)

    div_t = ctx.material.body_thickness
    for row_bays in row_groups.values():
        if len(row_bays) < 2:
            continue
        row_bays.sort(key=lambda b: b.col_index)
        for i in range(len(row_bays) - 1):
            left = row_bays[i]
            counter[0] += 1
            parts.append(Part(
                id=f"div_v_{counter[0]:03d}",
                name="Vertical Divider",
                kind="divider",
                module_id=left.module_id,
                material=mat,
                length=left.height,
                width=left.depth,
                thickness=div_t,
                origin=Vec3(x=left.x + left.width, y=left.y, z=left.z),
                axes=PartAxes(length_axis="y", width_axis="z", thickness_axis="x"),
                grain_direction="length",
                edge_banding=["front"],
            ))

    return parts, hardware
