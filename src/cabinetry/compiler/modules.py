import re
from .context import CompileContext
from ..model.cabinet import ResolvedModule


def _parse_base_height(base_spec: str | None) -> float:
    if base_spec is None:
        return 0.0
    m = re.match(r"^legs\s+(\d+(?:\.\d+)?)$", str(base_spec).strip())
    if m:
        return float(m.group(1))
    # Try stdlib base system name
    return 0.0


def _resolve_named_modules(
    ctx: CompileContext,
    module_specs: list[dict],
    width: float,
    depth: float,
    base_height: float,
    body_height: float,
) -> list[ResolvedModule]:
    star_count = sum(1 for s in module_specs if s.get("height") == "*")
    if star_count > 1:
        ctx.error("MODULE_OVERFLOW", "At most one module height may be '*'.")
        return []

    fixed_sum = sum(
        float(s["height"]) for s in module_specs if s.get("height") != "*"
    )
    if fixed_sum > body_height:
        ctx.error(
            "MODULE_OVERFLOW",
            f"Fixed module heights sum ({fixed_sum}mm) exceeds available body height "
            f"({body_height}mm).",
        )
        return []

    star_height = body_height - fixed_sum

    min_h = ctx.standard.module_split.min_top_module_height
    modules: list[ResolvedModule] = []
    y_pos = base_height
    for spec in module_specs:
        h = star_height if spec.get("height") == "*" else float(spec["height"])
        mod_id = str(spec["id"])
        if h < min_h:
            ctx.warn(
                "MIN_MODULE_HEIGHT",
                f"Module '{mod_id}' height {h}mm is below minimum {min_h}mm.",
            )
        modules.append(
            ResolvedModule(
                id=mod_id,
                name=mod_id.replace("_", " ").title(),
                x=0.0,
                y=y_pos,
                z=0.0,
                width=width,
                depth=depth,
                height=h,
            )
        )
        y_pos += h

    return modules


def resolve_modules(
    ctx: CompileContext, width: float, height: float, depth: float
) -> list[ResolvedModule]:
    cabinet_spec = ctx.normalized_dsl.get("cabinet", {})
    split = cabinet_spec.get("split", "auto")
    base_spec = cabinet_spec.get("base")

    base_height = _parse_base_height(base_spec)
    if ctx.base_system is not None:
        base_height = ctx.base_system.height

    body_height = height - base_height
    max_board = ctx.material.max_board.length
    split_spec = ctx.standard.module_split
    margin = split_spec.max_single_module_height_margin

    # Named modules take priority over split: auto/none/list
    named_specs = cabinet_spec.get("modules")
    if named_specs:
        return _resolve_named_modules(
            ctx, named_specs, width, depth, base_height, body_height
        )

    modules: list[ResolvedModule] = []

    if split == "none":
        modules.append(
            ResolvedModule(
                id="mod_main",
                name="Main",
                x=0.0,
                y=base_height,
                z=0.0,
                width=width,
                depth=depth,
                height=body_height,
            )
        )
    elif split == "auto":
        if body_height <= max_board - margin:
            modules.append(
                ResolvedModule(
                    id="mod_main",
                    name="Main",
                    x=0.0,
                    y=base_height,
                    z=0.0,
                    width=width,
                    depth=depth,
                    height=body_height,
                )
            )
        else:
            ctx.warn(
                "AUTO_SPLIT_APPLIED",
                f"Cabinet body height {body_height}mm exceeds max board length {max_board}mm. "
                "Splitting into main + top modules.",
            )
            main_height = min(split_spec.default_main_height, max_board - margin)
            top_height = body_height - main_height

            if top_height < split_spec.min_top_module_height:
                # Adjust main to ensure top meets minimum
                main_height = body_height - split_spec.min_top_module_height
                top_height = split_spec.min_top_module_height
                ctx.warn(
                    "AUTO_SPLIT_APPLIED",
                    f"Top module adjusted to minimum height {split_spec.min_top_module_height}mm.",
                )

            modules.append(
                ResolvedModule(
                    id="mod_main",
                    name="Main",
                    x=0.0,
                    y=base_height,
                    z=0.0,
                    width=width,
                    depth=depth,
                    height=main_height,
                )
            )
            modules.append(
                ResolvedModule(
                    id="mod_top",
                    name="Top",
                    x=0.0,
                    y=base_height + main_height,
                    z=0.0,
                    width=width,
                    depth=depth,
                    height=top_height,
                )
            )
    else:
        # Custom split list
        y_pos = base_height
        for i, mod_height in enumerate(split):
            modules.append(
                ResolvedModule(
                    id=f"mod_{i}",
                    name=f"Module {i + 1}",
                    x=0.0,
                    y=y_pos,
                    z=0.0,
                    width=width,
                    depth=depth,
                    height=float(mod_height),
                )
            )
            y_pos += float(mod_height)

    return modules
