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
        section = "auto" if section_key == "span" else doors_dsl.get(section_key, "none")
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

    # Handle span groups: one door covering the combined height of multiple modules.
    span_raw = doors_dsl.get("span")
    spanned_module_ids: set[str] = set()
    if span_raw:
        # Normalise: flat list → one group; list-of-lists → multiple groups.
        if span_raw and not isinstance(span_raw[0], list):
            span_groups = [span_raw]
        else:
            span_groups = span_raw

        mod_by_id = {m.id: m for m in modules}
        for group in span_groups:
            group_mods = [mod_by_id[mid] for mid in group if mid in mod_by_id]
            if not group_mods:
                continue
            spanned_module_ids.update(m.id for m in group_mods)
            # Bounding box of the group
            span_x = group_mods[0].x
            span_w = group_mods[0].width
            span_y = min(m.y for m in group_mods)
            span_top = max(m.y + m.height for m in group_mods)
            span_h = span_top - span_y
            # Use a proxy ResolvedModule so _make_doors_for_module works unchanged.
            proxy = group_mods[0].model_copy(
                update={"y": span_y, "height": span_h, "width": span_w, "x": span_x}
            )
            _make_doors_for_module(proxy, "span")

    # Per-module doors — skip any module already covered by a span group.
    _LEGACY = {"mod_main": "main", "mod_top": "top"}
    for mod in modules:
        if mod.id in spanned_module_ids:
            continue
        section_key = mod.id if mod.id in doors_dsl else _LEGACY.get(mod.id)
        if section_key:
            _make_doors_for_module(mod, section_key)

    return parts, hardware
