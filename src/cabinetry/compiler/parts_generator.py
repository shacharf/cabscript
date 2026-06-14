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

    for mod in modules:
        # Left side panel
        parts.append(
            Part(
                id=_part_id("side", counter),
                name=f"{mod.name} Left Side",
                kind="side_panel",
                module_id=mod.id,
                material=mat,
                length=mod.height,
                width=mod.depth,
                thickness=t,
                origin=Vec3(x=mod.x, y=mod.y, z=mod.z),
                axes=PartAxes(length_axis="y", width_axis="z", thickness_axis="x"),
                grain_direction="length",
                edge_banding=["front"],
            )
        )
        # Right side panel
        parts.append(
            Part(
                id=_part_id("side", counter),
                name=f"{mod.name} Right Side",
                kind="side_panel",
                module_id=mod.id,
                material=mat,
                length=mod.height,
                width=mod.depth,
                thickness=t,
                origin=Vec3(x=mod.x + mod.width - t, y=mod.y, z=mod.z),
                axes=PartAxes(length_axis="y", width_axis="z", thickness_axis="x"),
                grain_direction="length",
                edge_banding=["front"],
            )
        )
        # Bottom panel (between sides)
        inner_w = mod.width - 2 * t
        parts.append(
            Part(
                id=_part_id("bottom", counter),
                name=f"{mod.name} Bottom",
                kind="bottom_panel",
                module_id=mod.id,
                material=mat,
                length=inner_w,
                width=mod.depth,
                thickness=t,
                origin=Vec3(x=mod.x + t, y=mod.y, z=mod.z),
                axes=PartAxes(length_axis="x", width_axis="z", thickness_axis="y"),
                grain_direction="length",
                edge_banding=["front"],
            )
        )
        # Top panel (between sides)
        parts.append(
            Part(
                id=_part_id("top", counter),
                name=f"{mod.name} Top",
                kind="top_panel",
                module_id=mod.id,
                material=mat,
                length=inner_w,
                width=mod.depth,
                thickness=t,
                origin=Vec3(x=mod.x + t, y=mod.y + mod.height - t, z=mod.z),
                axes=PartAxes(length_axis="x", width_axis="z", thickness_axis="y"),
                grain_direction="length",
                edge_banding=["front"],
            )
        )
        # Back panel (surface-applied)
        parts.append(
            Part(
                id=_part_id("back", counter),
                name=f"{mod.name} Back",
                kind="back_panel",
                module_id=mod.id,
                material=mat,
                length=mod.height,
                width=mod.width,
                thickness=bt,
                origin=Vec3(x=mod.x, y=mod.y, z=mod.z + mod.depth - bt),
                axes=PartAxes(length_axis="y", width_axis="x", thickness_axis="z"),
                grain_direction="none",
            )
        )

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

    for bay in bays:
        fn = bay.function
        if fn.kind in ("shelves", "shoes"):
            count = fn.params.get("count", fn.params.get("rows", 3))
            shelf_clearance = 2.0
            shelf_length = bay.width - shelf_clearance
            shelf_width = bay.depth - 50  # some front/rear clearance

            if count > 0:
                spacing = bay.height / (count + 1)
                for i in range(int(count)):
                    y_pos = bay.y + spacing * (i + 1)
                    counter[0] += 1
                    pid = f"shelf_{counter[0]:03d}"
                    parts.append(
                        Part(
                            id=pid,
                            name=f"Shelf {counter[0]}",
                            kind="shelf",
                            module_id=bay.module_id,
                            material=mat,
                            length=shelf_length,
                            width=shelf_width,
                            thickness=shelf_t,
                            origin=Vec3(
                                x=bay.x + shelf_clearance / 2,
                                y=y_pos,
                                z=bay.z + 25,
                            ),
                            axes=PartAxes(
                                length_axis="x", width_axis="z", thickness_axis="y"
                            ),
                            grain_direction="length",
                            edge_banding=["front"],
                        )
                    )

        elif fn.kind == "hanging":
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

    return parts, hardware
