# Waypoint

Current implementation status. `docs/NORTH_STAR.md` remains the long-term vision; this file tracks current reality and near-term direction.

## Current State

A fully working V1 is implemented end-to-end:

```text
DSL text (YAML)
        |
        v
parse → normalize shorthand → merge stdlib defaults
        |
        v
resolve dimensions → split modules → solve layout
        |
        v
generate parts (carcass, shelves, doors, hardware)
        |
        v
ResolvedProject (source of truth)
        |
        ├── GLB export → Three.js browser viewer
        ├── cut list (JSON / CSV)
        └── FastAPI REST API
                |
                └── React + TypeScript SPA (frontend/)
```

### Backend
- Complete YAML DSL compiler pipeline (parse → normalize → compile → geometry)
- FastAPI REST API (`/api/compile`, `/api/render.glb`, `/api/cutlist`, `/api/stdlib`)
- Pydantic v2 domain model (`ResolvedProject`)
- trimesh GLB export
- Cut list generation (JSON + CSV)
- 51 passing tests

### Frontend
- React 19 + TypeScript (Vite), lives in `frontend/`
- Monaco DSL editor (YAML syntax, auto-compiles 600ms after keystroke)
- 2D front elevation viewer with bay coloring, dimension labels, and click-to-select
- 3D viewer (Three.js + OrbitControls, GLB loaded via `/api/render.glb`)
- Right panel: standard/material/type dropdowns, finish color palette (swatches), selected element inspector
- Bottom panel: compile messages + cut list table
- Start screen: New Project / Open `.yaml` file / Save `.yaml` file

## Active Direction

UI Phase 1 is complete. Next areas to tackle (not yet started):

1. **Project definition form** — GUI to set space dimensions (width/height/depth) without manually editing the DSL `space:` line
2. **Bay editing** — click a bay in the 2D view to change its function via the properties panel (write-back to DSL layout section)
3. **SVG export** — front elevation SVG from `outputs/svg_views.py` (stub exists, not implemented)
4. **More cabinet types** — `kitchen_base`, `kitchen_wall`, `wardrobe` compiler support beyond `built_in`

## Decisions

- Internal source of truth is a typed Pydantic v2 semantic model (`ResolvedProject`).
- Coordinate system: X = width, Y = height, Z = depth; cabinet origin at back-left-bottom.
- Module split: `main_plus_top` mode — split when body height exceeds max board length.
- Cut list dimensions come from `Part.length / width / thickness` manufacturing fields, never from mesh bounding boxes.
- Technology stack: Python 3.12+, FastAPI, Pydantic v2, PyYAML, trimesh, NumPy, React 19, TypeScript, Vite, Three.js, Zustand, Monaco Editor; uv for Python env.
- Linting: black + flake8 (no ruff).
- Storage root is read from the `CABSCRIPT_ROOT` env var (loaded via `python-dotenv`); default is `<repo root>/data`. Backend storage integration deferred.
- DSL write-back from UI uses targeted regex line-replace on top-level keys (not full YAML round-trip) to preserve user formatting and shorthand.

## Current Constraints

- MVP supports only one `*` column per row and one `*` row per module in the layout solver.
- Door generation is slab-only for MVP; frame-and-panel is a future extension.
- Hardware is represented semantically; approximate rendering only for MVP.
- SVG views are not yet implemented (`outputs/svg_views.py` is a stub).
- GlobalProperties panel does not yet expose space dimensions as editable fields (only standard, material, cabinet type).
- Bay function write-back from the UI is not yet implemented (read-only inspector in V1).

## Open Questions

- None currently.

## Next

1. Extend `GlobalProperties` panel to expose space dimensions (width/height/depth) as numeric inputs with DSL write-back.
2. Add bay function editing — clicking a bay in the 2D view should allow changing its function via a dropdown in `SelectedProperties`.
3. Implement `outputs/svg_views.py` front elevation SVG and wire a `/api/svg` endpoint.
