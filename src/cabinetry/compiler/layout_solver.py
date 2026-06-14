from .context import CompileContext
from ..model.cabinet import ResolvedModule
from ..model.layout import ResolvedBay, BayFunction


def resolve_layout(
    ctx: CompileContext, modules: list[ResolvedModule]
) -> list[ResolvedBay]:
    layout_dsl = ctx.normalized_dsl.get("layout", {})
    t = ctx.material.body_thickness
    bays: list[ResolvedBay] = []

    module_map = {m.id: m for m in modules}

    def _resolve_for_module(mod: ResolvedModule, section: dict, bay_id_prefix: str) -> None:
        rows_spec = section.get("rows", [])
        inner_height = mod.height - 2 * t  # top + bottom panel
        inner_width = mod.width - 2 * t    # left + right side

        # Resolve heights
        fixed_heights = [r["height"] for r in rows_spec if r["height"] != "*"]
        star_rows = [r for r in rows_spec if r["height"] == "*"]
        sum_fixed = sum(fixed_heights)
        remaining_h = inner_height - sum_fixed
        if len(star_rows) > 1:
            raise ValueError("Only one '*' row per module is supported in MVP.")
        star_height = remaining_h if star_rows else 0.0

        if sum_fixed > inner_height:
            ctx.error(
                "LAYOUT_OVERFLOW",
                f"Fixed row heights ({sum_fixed}mm) exceed available inner height ({inner_height}mm) "
                f"in module {mod.id}.",
            )

        row_y = mod.y + t  # bottom panel top edge
        for row_i, row_spec in enumerate(rows_spec):
            rh = star_height if row_spec["height"] == "*" else float(row_spec["height"])
            cols_spec = row_spec.get("columns", [])

            # Resolve widths
            fixed_widths = [c["width"] for c in cols_spec if c["width"] != "*"]
            star_cols = [c for c in cols_spec if c["width"] == "*"]
            sum_fixed_w = sum(fixed_widths)
            remaining_w = inner_width - sum_fixed_w
            if len(star_cols) > 1:
                raise ValueError("Only one '*' column per row is supported in MVP.")
            star_width = remaining_w if star_cols else 0.0

            if sum_fixed_w > inner_width:
                ctx.error(
                    "LAYOUT_OVERFLOW",
                    f"Fixed column widths ({sum_fixed_w}mm) exceed inner width ({inner_width}mm) "
                    f"in row {row_i} of module {mod.id}.",
                )

            col_x = mod.x + t
            for col_i, col_spec in enumerate(cols_spec):
                cw = star_width if col_spec["width"] == "*" else float(col_spec["width"])
                fn_data = col_spec["function"]
                fn = BayFunction(**fn_data) if isinstance(fn_data, dict) else fn_data

                bay = ResolvedBay(
                    id=f"{bay_id_prefix}_r{row_i}_c{col_i}",
                    module_id=mod.id,
                    row_index=row_i,
                    col_index=col_i,
                    x=col_x,
                    y=row_y,
                    z=mod.z,
                    width=cw,
                    depth=mod.depth,
                    height=rh,
                    function=fn,
                )
                bays.append(bay)
                col_x += cw

            row_y += rh

    # Apply layout to modules
    has_main = "mod_main" in module_map
    has_top = "mod_top" in module_map

    if has_main and "main" in layout_dsl:
        _resolve_for_module(module_map["mod_main"], layout_dsl["main"], "bay_main")
    elif has_main and layout_dsl:
        # Use first section as main
        first_key = next(iter(layout_dsl))
        _resolve_for_module(module_map["mod_main"], layout_dsl[first_key], "bay_main")
    elif has_main:
        # Default: single storage bay
        mod = module_map["mod_main"]
        bays.append(
            ResolvedBay(
                id="bay_main_r0_c0",
                module_id=mod.id,
                row_index=0,
                col_index=0,
                x=mod.x + t,
                y=mod.y + t,
                z=mod.z,
                width=mod.width - 2 * t,
                depth=mod.depth,
                height=mod.height - 2 * t,
                function=BayFunction(kind="storage"),
            )
        )

    if has_top and "top" in layout_dsl:
        _resolve_for_module(module_map["mod_top"], layout_dsl["top"], "bay_top")
    elif has_top:
        mod = module_map["mod_top"]
        bays.append(
            ResolvedBay(
                id="bay_top_r0_c0",
                module_id=mod.id,
                row_index=0,
                col_index=0,
                x=mod.x + t,
                y=mod.y + t,
                z=mod.z,
                width=mod.width - 2 * t,
                depth=mod.depth,
                height=mod.height - 2 * t,
                function=BayFunction(kind="storage"),
            )
        )

    # Handle modules with no layout key
    for mod in modules:
        if mod.id not in ("mod_main", "mod_top"):
            bays.append(
                ResolvedBay(
                    id=f"bay_{mod.id}_r0_c0",
                    module_id=mod.id,
                    row_index=0,
                    col_index=0,
                    x=mod.x + t,
                    y=mod.y + t,
                    z=mod.z,
                    width=mod.width - 2 * t,
                    depth=mod.depth,
                    height=mod.height - 2 * t,
                    function=BayFunction(kind="storage"),
                )
            )

    return bays
