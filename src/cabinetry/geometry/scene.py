import trimesh
from ..model.project import ResolvedProject
from .mesh import box_mesh_for_part
from .materials import resolve_part_color


def build_scene(project: ResolvedProject) -> trimesh.Scene:
    scene = trimesh.Scene()
    finish = {}

    # Will be populated from normalized DSL if available; geometry module
    # doesn't have ctx, so we use simple defaults based on part kind.

    for part in project.parts:
        color = resolve_part_color(part.kind, finish)
        mesh = box_mesh_for_part(part, color)
        scene.add_geometry(mesh, node_name=part.id)

    return scene
