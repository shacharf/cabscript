import re
from ..dsl.parser import parse_dsl
from ..dsl.shorthand import normalize_shorthand
from ..dsl.errors import StdLibLookupError
from ..stdlib.loader import StdLib
from ..model.project import ResolvedProject
from .context import CompileContext
from .resolve_dimensions import resolve_cabinet_dimensions
from .modules import resolve_modules
from .layout_solver import resolve_layout
from .parts_generator import generate_carcass_parts, generate_bay_parts
from .doors_generator import generate_doors
from .hardware_generator import generate_base_hardware
from .warnings import check_parts

_stdlib = StdLib()


def _parse_base_system(ctx: CompileContext) -> None:
    cabinet_spec = ctx.normalized_dsl.get("cabinet", {})
    base_spec = cabinet_spec.get("base")
    if base_spec is None:
        return
    base_str = str(base_spec).strip()
    # "legs 80" is inline — not a stdlib lookup
    if re.match(r"^legs\s+\d+", base_str):
        return
    # Otherwise try stdlib
    try:
        ctx.base_system = ctx.stdlib.get_base_system(base_str)
    except StdLibLookupError as e:
        ctx.error("UNKNOWN_PRESET", str(e), path="cabinet.base")


def compile_dsl(text: str) -> tuple[dict, ResolvedProject]:
    raw = parse_dsl(text)
    normalized = normalize_shorthand(raw)

    use = normalized.get("use", {})
    standard_name = use.get("standard", "euro_builtin_v1")
    material_name = use.get("material", "plywood_18")

    standard = _stdlib.get_standard(standard_name)
    material = _stdlib.get_material(material_name)
    door_system = _stdlib.get_door_system(standard.doors.default_system)
    door_style = _stdlib.get_door_style(standard.doors.default_style)
    shelf_system = _stdlib.get_shelf_system(standard.shelf.default_support)

    # Allow DSL overrides for door system/style
    doors_dsl = normalized.get("doors", {})
    if "style" in doors_dsl:
        try:
            door_style = _stdlib.get_door_style(doors_dsl["style"])
        except StdLibLookupError:
            pass  # keep default

    ctx = CompileContext(
        raw_dsl=raw,
        normalized_dsl=normalized,
        stdlib=_stdlib,
        standard=standard,
        material=material,
        door_system=door_system,
        door_style=door_style,
        shelf_system=shelf_system,
        base_system=None,
    )

    _parse_base_system(ctx)

    width, height, depth = resolve_cabinet_dimensions(ctx)

    if ctx.has_errors:
        raise ValueError(
            "Compilation errors: " + "; ".join(e.message for e in ctx.errors)
        )

    modules = resolve_modules(ctx, width, height, depth)
    bays = resolve_layout(ctx, modules)
    carcass_parts = generate_carcass_parts(ctx, modules)
    bay_parts, bay_hardware = generate_bay_parts(ctx, bays)
    door_parts, door_hardware = generate_doors(ctx, modules)
    base_hardware = generate_base_hardware(ctx, width, depth)

    all_parts = carcass_parts + bay_parts + door_parts
    all_hardware = bay_hardware + door_hardware + base_hardware

    check_parts(ctx, all_parts)

    all_warnings = ctx.warnings + ctx.errors

    project = ResolvedProject(
        standard=standard_name,
        material=material_name,
        width=width,
        height=height,
        depth=depth,
        modules=modules,
        bays=bays,
        parts=all_parts,
        hardware=all_hardware,
        warnings=all_warnings,
    )

    return normalized, project
