from importlib.metadata import version as pkg_version
from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from ..model.project import ResolvedProject
from ..model.validation import ValidationMessage
from ..compiler.compile import compile_dsl
from ..geometry.export import export_glb
from ..outputs.cutlist import generate_cutlist, cutlist_to_json, cutlist_to_csv
from ..outputs.export_bundle import build_export_zip
from ..stdlib.loader import StdLib

router = APIRouter()
_stdlib = StdLib()


class DslRequest(BaseModel):
    dsl: str


class ExportSettings(BaseModel):
    ignore_grain: bool = False


class ExportRequest(BaseModel):
    dsl: str
    settings: ExportSettings = ExportSettings()


class CompileResponse(BaseModel):
    normalized: dict
    project: ResolvedProject
    warnings: list[ValidationMessage]


@router.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/api/version")
def version() -> dict:
    return {"version": pkg_version("cabinetry")}


@router.post("/api/parse")
def parse_endpoint(req: DslRequest) -> dict:
    from ..dsl.parser import parse_dsl as _parse
    from ..dsl.shorthand import normalize_shorthand
    raw = _parse(req.dsl)
    normalized = normalize_shorthand(raw)
    return {"raw": raw, "normalized": normalized}


@router.post("/api/compile", response_model=CompileResponse)
def compile_endpoint(req: DslRequest) -> CompileResponse:
    normalized, project = compile_dsl(req.dsl)
    return CompileResponse(
        normalized=normalized,
        project=project,
        warnings=project.warnings,
    )


@router.post("/api/render.glb")
def render_glb_endpoint(req: DslRequest) -> Response:
    _, project = compile_dsl(req.dsl)
    glb = export_glb(project)
    return Response(content=glb, media_type="model/gltf-binary")


@router.post("/api/cutlist")
def cutlist_endpoint(req: DslRequest) -> dict:
    _, project = compile_dsl(req.dsl)
    items = generate_cutlist(project)
    return {
        "json": cutlist_to_json(items),
        "csv": cutlist_to_csv(items),
        "items": [item.model_dump() for item in items],
    }


@router.post("/api/export.zip")
def export_zip_endpoint(req: ExportRequest) -> Response:
    _, project = compile_dsl(req.dsl)
    zip_bytes = build_export_zip(project, _stdlib, ignore_grain=req.settings.ignore_grain)
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": "attachment; filename=cabinet-export.zip"
        },
    )


@router.post("/api/export.html")
def export_html_endpoint(req: ExportRequest) -> Response:
    from ..outputs.cutlist import board_cutlist_to_csv
    from ..outputs.export_html import build_export_html
    from ..outputs.nesting import nest_parts
    import csv, io

    _, project = compile_dsl(req.dsl)
    items = generate_cutlist(project)
    boards = nest_parts(project, _stdlib, ignore_grain=req.settings.ignore_grain)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["board_index", "label", "part_id", "x", "y", "w", "h", "rotated", "formica_side"])
    for board in boards:
        for p in board.placements:
            writer.writerow([
                board.index, p.label, p.part_id,
                round(p.x, 1), round(p.y, 1), round(p.w, 1), round(p.h, 1),
                "yes" if p.rotated else "no", p.formica_side,
            ])
    cut_plan_csv = buf.getvalue()

    html = build_export_html(items, boards, cut_plan_csv, project)
    return Response(content=html, media_type="text/html")


@router.get("/api/stdlib")
def stdlib_endpoint() -> dict:
    return {
        "standards": _stdlib.all_standards(),
        "materials": _stdlib.all_materials(),
        "colors": _stdlib.all_colors(),
    }
