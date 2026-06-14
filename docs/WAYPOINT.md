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
- 54 passing tests

### Frontend
- React 19 + TypeScript (Vite), lives in `frontend/`
- Monaco DSL editor with context-aware YAML autocomplete (values from `/api/stdlib`, line-based context detection)
- 2D front elevation viewer: pan (drag), zoom (wheel), double-click to reset; drawer bay divisions; per-bay dimension toggle; click-to-select; vertical dividers enforced to minimum 3 px with a distinct stroke
- 3D viewer (Three.js + OrbitControls, GLB loaded via `/api/render.glb`); camera starts in front of the cabinet (negative-Z side)
- Right panel: standard/material/type dropdowns, finish color palette (swatches), selected element inspector with drawer count editing
- Bottom panel: compile messages + cut list table
- Start screen: New Project / Open `.yaml` file / Save `.yaml` file
- Resizable editor/viewer/properties columns with widths persisted to localStorage

## Active Direction

V4 UI features shipped. Recent rendering fixes applied (see Decisions). Next areas to tackle:

1. **SVG export** — front elevation SVG from `outputs/svg_views.py` (stub exists, not implemented)
2. **More cabinet types** — `kitchen_base`, `kitchen_wall`, `wardrobe` compiler support beyond `built_in`
3. **Drawer box geometry** — add drawer sides/bottom/back parts to the 3D GLB (currently only drawer_front exists)
4. **Bay function editing** — extend SelectedProperties to change bay function type (not just drawer count)

## Decisions

- Internal source of truth is a typed Pydantic v2 semantic model (`ResolvedProject`).
- Coordinate system: X = width, Y = height, Z = depth. Origin is at the **front**-left-bottom of the cabinet interior (x=0, y=0, z=0 = front-left-bottom corner). Z increases toward the back; doors and drawer fronts are at z < 0 (in front of the opening). The 3D camera is positioned at negative Z to look at the cabinet from the front.
- Module split: `main_plus_top` auto mode — split when body height exceeds max board length. Named modules (`cabinet.modules`) take priority and support arbitrary module ids.
- Cut list dimensions come from `Part.length / width / thickness` manufacturing fields, never from mesh bounding boxes.
- Shelves in a multi-column row are generated as a single full-width part spanning all columns (sits on top of vertical dividers), not per-bay pieces.
- Technology stack: Python 3.12+, FastAPI, Pydantic v2, PyYAML, trimesh, NumPy, React 19, TypeScript, Vite, Three.js, Zustand, Monaco Editor; uv for Python env.
- Linting: black + flake8 (no ruff).
- Storage root is read from the `CABSCRIPT_ROOT` env var (loaded via `python-dotenv`); default is `<repo root>/data`. Backend storage integration deferred.
- DSL write-back from UI uses targeted regex line-replace on top-level keys (not full YAML round-trip) to preserve user formatting and shorthand.

## Current Constraints

- MVP supports only one `*` column per row and one `*` row per module in the layout solver.
- Door generation is slab-only for MVP; frame-and-panel is a future extension.
- Hardware is represented semantically; approximate rendering only for MVP.
- SVG views are not yet implemented (`outputs/svg_views.py` is a stub).
- Bay function type changing from the UI is not yet implemented; only drawer count is editable.
- Drawer box geometry (sides, bottom, back) is not modeled; only the front face exists in the 3D GLB.

## Open Questions

- None currently.

## Next

1. Implement `outputs/svg_views.py` front elevation SVG and wire a `/api/svg` endpoint.
2. Add drawer box geometry to the compiler and GLB export for a fuller 3D representation.
3. Extend bay function editing beyond drawer count — allow changing function type via a dropdown in `SelectedProperties`.
