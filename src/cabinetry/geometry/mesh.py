import numpy as np
import trimesh
from ..model.parts import Part
from .coordinates import part_box_size


def box_mesh_for_part(part: Part, color: tuple[int, int, int, int]) -> trimesh.Trimesh:
    sx, sy, sz = part_box_size(part)
    sx = max(sx, 0.1)
    sy = max(sy, 0.1)
    sz = max(sz, 0.1)

    mesh = trimesh.creation.box(extents=[sx, sy, sz])

    cx = part.origin.x + sx / 2
    cy = part.origin.y + sy / 2
    cz = part.origin.z + sz / 2
    mesh.apply_translation([cx, cy, cz])

    face_count = len(mesh.faces)
    mesh.visual = trimesh.visual.ColorVisuals(
        mesh=mesh,
        face_colors=np.tile(np.array(color, dtype=np.uint8), (face_count, 1)),
    )

    return mesh
