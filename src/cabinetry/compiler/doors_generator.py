from .context import CompileContext
from ..model.cabinet import ResolvedModule
from ..model.parts import Part
from ..model.primitives import Vec3, PartAxes
from ..model.hardware import HardwareItem


MAX_SINGLE_DOOR_WIDTH = 600.0


def _hinge_count(door_height: float, rules: list) -> int:
    for rule in sorted(rules, key=lambda r: r.max_height):
        if door_height <= rule.max_height:
            return rule.count
    return rules[-1].count if rules else 2


def _generate_door_hardware(
    door_part: Part,
    door_system: object,
    hw_counter: list[int],
) -> list[HardwareItem]:
    items: list[HardwareItem] = []
    count = _hinge_count(door_part.length, door_system.hinge_count_rule)  # type: ignore[attr-defined]
    door_h = door_part.length
    positions_y = []
    if count == 1:
        positions_y = [door_part.origin.y + door_h / 2]
    else:
        positions_y = [door_part.origin.y + 100]
        if count > 2:
            span = door_h - 200
            step = span / (count - 1)
            for i in range(1, count - 1):
                positions_y.append(door_part.origin.y + 100 + step * i)
        positions_y.append(door_part.origin.y + door_h - 100)

    for y in positions_y:
        hw_counter[0] += 1
        items.append(
            HardwareItem(
                id=f"hinge_{hw_counter[0]:03d}",
                kind="hinge",
                name="Concealed Hinge",
                position=Vec3(
                    x=door_part.origin.x,
                    y=y,
                    z=door_part.origin.z,
                ),
                params={
                    "cup_diameter": 35,
                    "cup_depth": 12,
                },
            )
        )
    return items


def generate_doors(
    ctx: CompileContext,
    modules: list[ResolvedModule],
) -> tuple[list[Part], list[HardwareItem]]:
    doors_dsl = ctx.normalized_dsl.get("doors", {})
    if not doors_dsl:
        return [], []

    door_t = ctx.material.door_thickness
    gap = ctx.door_system.gap
    mat = ctx.material.name
    parts: list[Part] = []
    hardware: list[HardwareItem] = []
    counter = [0]
    hw_counter = [0]

    def _make_doors_for_module(mod: ResolvedModule, section_key: str) -> None:
        section = doors_dsl.get(section_key, "none")
        if section == "none":
            return

        # Full-width doors for this module
        opening_w = mod.width
        opening_h = mod.height
        door_h = opening_h - gap * 2

        if door_h <= 0:
            return

        if opening_w <= MAX_SINGLE_DOOR_WIDTH:
            door_w = opening_w - gap * 2
            _add_door(mod, door_w, door_h, mod.x + gap, mod.y + gap)
        else:
            half = opening_w / 2
            door_w = half - gap * 1.5
            _add_door(mod, door_w, door_h, mod.x + gap, mod.y + gap)
            _add_door(mod, door_w, door_h, mod.x + half + gap * 0.5, mod.y + gap)

    def _add_door(
        mod: ResolvedModule,
        door_w: float,
        door_h: float,
        x: float,
        y: float,
    ) -> None:
        counter[0] += 1
        door_part = Part(
            id=f"door_{counter[0]:03d}",
            name=f"Door {counter[0]}",
            kind="door",
            module_id=mod.id,
            material=mat,
            length=door_h,
            width=door_w,
            thickness=door_t,
            origin=Vec3(x=x, y=y, z=-door_t),
            axes=PartAxes(length_axis="y", width_axis="x", thickness_axis="z"),
            grain_direction="length",
            edge_banding=["front", "back", "left", "right"],
        )
        parts.append(door_part)

        if door_h > 2300:
            ctx.warn("DOOR_TOO_TALL", f"Door {counter[0]} height {door_h}mm is very tall.")
        if ctx.door_style.type == "slab" and door_h > 1800:
            ctx.warn(
                "SLAB_DOOR_WARP_RISK",
                f"Slab door {counter[0]} height {door_h}mm may be at risk of warping.",
            )

        hinges = _generate_door_hardware(door_part, ctx.door_system, hw_counter)
        hardware.extend(hinges)

    # Match each module to its door spec by id, with legacy fallback for mod_main/mod_top.
    _LEGACY = {"mod_main": "main", "mod_top": "top"}
    for mod in modules:
        section_key = mod.id if mod.id in doors_dsl else _LEGACY.get(mod.id)
        if section_key:
            _make_doors_for_module(mod, section_key)

    return parts, hardware
