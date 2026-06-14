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
