from .context import CompileContext


def resolve_cabinet_dimensions(ctx: CompileContext) -> tuple[float, float, float]:
    ndsl = ctx.normalized_dsl
    clearances = ctx.standard.clearances
    cabinet_spec = ndsl.get("cabinet", {})
    cabinet_type = cabinet_spec.get("type", "built_in")

    if cabinet_type == "built_in":
        space = ndsl.get("space", {})
        niche = space.get("niche")
        if niche is None:
            raise ValueError("built_in cabinet requires a niche space specification.")
        niche_w = float(niche["width"])
        niche_h = float(niche["height"])
        niche_d = float(niche["depth"])

        width = niche_w - 2 * clearances.side_each
        height = niche_h - clearances.top
        depth = niche_d - clearances.back

        if width <= 0:
            ctx.error("INVALID_WIDTH", "Cabinet width is not positive after applying clearances.")
        if height <= 0:
            ctx.error("INVALID_HEIGHT", "Cabinet height is not positive after applying clearances.")
        if depth <= 0:
            ctx.error("INVALID_DEPTH", "Cabinet depth is not positive after applying clearances.")

        if clearances.side_each < 5:
            ctx.warn(
                "INSUFFICIENT_CLEARANCE",
                f"Side clearance {clearances.side_each}mm is very small.",
                path="space.niche",
            )

        return width, height, depth

    else:
        # For standing/free cabinets, use explicit dimensions or defaults
        w = cabinet_spec.get("width", "auto")
        h = cabinet_spec.get("height", "auto")
        d = cabinet_spec.get("depth", "auto")

        width = float(w) if w != "auto" else 600.0
        height = float(h) if h != "auto" else 2000.0
        depth = float(d) if d != "auto" else float(ctx.standard.cabinet.default_depth)

        return width, height, depth
