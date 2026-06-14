from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel
from ..model.project import ResolvedProject
from ..model.validation import ValidationMessage
from ..compiler.compile import compile_dsl
from ..geometry.export import export_glb
from ..outputs.cutlist import generate_cutlist, cutlist_to_json, cutlist_to_csv
from ..stdlib.loader import StdLib

router = APIRouter()
_stdlib = StdLib()


class DslRequest(BaseModel):
    dsl: str


class CompileResponse(BaseModel):
    normalized: dict
    project: ResolvedProject
    warnings: list[ValidationMessage]


@router.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


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


@router.get("/api/stdlib")
def stdlib_endpoint() -> dict:
    return {
        "standards": _stdlib.all_standards(),
        "materials": _stdlib.all_materials(),
    }
