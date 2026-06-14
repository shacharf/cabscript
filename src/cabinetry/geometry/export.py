from ..model.project import ResolvedProject
from .scene import build_scene


def export_glb(project: ResolvedProject, finish: dict[str, str] | None = None) -> bytes:
    scene = build_scene(project)
    result = scene.export(file_type="glb")
    if isinstance(result, bytes):
        return result
    raise TypeError(f"Expected bytes from GLB export, got {type(result)}")
