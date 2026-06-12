# Architecture

This document describes the current codebase shape, major responsibilities, data/control flow, storage, extension points, and implementation constraints. `docs/NORTH_STAR.md` defines the long-term destination; `docs/WAYPOINT.md` tracks current project state.

## System Map

```text
DSL text (YAML)
        |
        v
dsl/parser.py         — yaml.safe_load, reject invalid docs
        |
        v
dsl/shorthand.py      — normalize compact syntax to explicit dict
        |
        v
compiler/defaults.py  — deep-merge with stdlib presets
        |
        v
compiler/context.py   — CompileContext (mutable working state)
        |
        v
compiler/resolve_dimensions.py  — niche/clearance → w/h/d
compiler/modules.py             — body height → ResolvedModule list
compiler/layout_solver.py       — row/column grid → ResolvedBay list
compiler/parts_generator.py     — carcass + shelf Part objects
compiler/doors_generator.py     — slab door Part objects
compiler/hardware_generator.py  — hinges, rods, legs
        |
        v
model/project.py      — ResolvedProject  (source of truth)
        |
        ├── geometry/export.py   → GLB bytes (trimesh)
        ├── outputs/cutlist.py   → JSON / CSV cut list
        ├── outputs/svg_views.py → SVG elevation/section (future)
        └── app/routes.py        → FastAPI REST responses
```

## Package Responsibilities

```text
src/cabinetry/
  app/
    main.py          FastAPI app creation and startup
    routes.py        All HTTP route handlers
    static/          index.html, viewer.js, styles.css

  dsl/
    parser.py        YAML → raw dict (DslSyntaxError on bad input)
    shorthand.py     Compact DSL keys → explicit nested dict
    dimensions.py    "1200 x 2650 x 600" → (float, float, float)
    errors.py        DslSyntaxError and related exceptions

  stdlib/
    loader.py        StdLib class — lazy-loads YAML files, typed getters
    specs.py         Pydantic spec models for all stdlib YAML schemas
    standards.yaml   Construction standards (e.g. euro_builtin_v1)
    materials.yaml   Sheet goods specs
    door_systems.yaml Hinge/overlay specs
    door_styles.yaml  Slab / frame-panel specs
    shelf_systems.yaml Pin / cleat specs
    base_systems.yaml Leg / plinth specs
    colors.yaml       Finish name → RGBA

  model/
    primitives.py    Mm, Vec3, Size3, PartAxes
    materials.py     MaterialSpec, SheetSize
    space.py         NicheSpec, SpaceSpec
    cabinet.py       CabinetRequest, ResolvedModule
    layout.py        BayFunction, ColumnSpec, RowSpec, ResolvedBay
    parts.py         Part, PartKind, Operation, EdgeName
    doors.py         (door-specific helpers, if needed)
    hardware.py      HardwareItem
    validation.py    Severity, ValidationMessage
    project.py       ResolvedProject

  compiler/
    context.py       CompileContext dataclass (mutable pipeline state)
    defaults.py      deep_merge(base, override) — stdlib < standard < user
    normalize.py     High-level normalization orchestration
    resolve_dimensions.py  Niche/clearance → cabinet w/h/d
    modules.py       Module splitting logic (main_plus_top)
    layout_solver.py Row/column grid → ResolvedBay list
    parts_generator.py    Carcass panels + shelf parts
    shelves_generator.py  Shelf distribution within a bay
    doors_generator.py    Slab door parts + hinge metadata
    hardware_generator.py Legs, rods, hinges
    warnings.py      Warning/error validation checks
    compile.py       compile_dsl(text) → (normalized_dict, ResolvedProject)

  geometry/
    coordinates.py   part_box_size(part) → (x_size, y_size, z_size)
    mesh.py          box_mesh_for_part(part, color) → trimesh.Trimesh
    materials.py     Finish/role → RGBA colour lookup
    scene.py         build_scene(project) → trimesh.Scene
    export.py        export_glb(project) → bytes

  outputs/
    cutlist.py       CutListItem, generate_cutlist() → JSON + CSV
    bom.py           Bill of materials (future)
    svg_views.py     Front elevation + side section SVG (future)

  examples/
    niche_closet.yaml
    standing_cabinet.yaml
    kitchen_base.yaml
```

### `dsl`

Owns all text-to-dict translation. Produces a plain Python dict — no model objects. The shorthand normalizer expands compact keys (`use: euro_builtin_v1`, `space: niche 1200 x 2650 x 600`, column shorthand) into the explicit nested form the compiler expects. Nothing outside `dsl/` touches raw YAML text.

### `stdlib`

Owns the bundled YAML preset library. `StdLib` loads each file once and exposes typed getters (`get_standard`, `get_material`, etc.) that return Pydantic `*Spec` objects. Raises `StdLibLookupError` (lists available keys) on unknown names.

### `model`

Pure Pydantic v2 data models. No business logic. `ResolvedProject` is the compiler's output and the single source of truth consumed by geometry and output generators.

### `compiler`

Stateful pipeline. `CompileContext` (a `@dataclass`) is threaded through every stage and accumulates warnings/errors via `ctx.warn()` / `ctx.error()`. Fatal problems raise immediately; non-fatal ones append to `ctx.warnings`. Entry point is `compile.py::compile_dsl(text)`.

### `geometry`

Converts `ResolvedProject` parts into renderable meshes using `trimesh`. Reads manufacturing dimensions and `PartAxes` to place box meshes; never reverse-engineers dimensions from mesh geometry. Finish colours come from `colors.yaml` via the material role (`body`, `doors`, `shelves`, `back`).

### `outputs`

Generates human-readable deliverables (cut list CSV/JSON, later SVG). Cut list dimensions come exclusively from `Part.length / width / thickness` — not from mesh bounding boxes.

### `app`

FastAPI app exposing the compiler and geometry pipeline as REST endpoints. Serves the static Three.js viewer from `app/static/`.

## Primary Flow

1. User pastes DSL into the browser textarea and clicks **Compile** or **Render**.
2. Browser POSTs to `/api/compile` or `/api/render.glb` with `{"dsl": "..."}`.
3. `compile_dsl(text)` runs the full pipeline: parse → normalize → merge stdlib → resolve dimensions → split modules → solve layout → generate parts/doors/hardware.
4. For `/api/compile`, the `ResolvedProject` JSON is returned with warnings.
5. For `/api/render.glb`, the project is passed to `export_glb()` and the GLB bytes are returned (`model/gltf-binary`).
6. The browser loads the GLB with Three.js `GLTFLoader`, frames the camera, and displays the model.

## Public Interfaces

- **CLI**: none for MVP (server started with `uvicorn cabinetry.app.main:app`).
- **REST API**:
  - `GET  /` — serves `index.html`
  - `GET  /api/health` — `{"status": "ok"}`
  - `POST /api/parse` — raw dict from DSL text
  - `POST /api/compile` — `CompileResponse` (normalized dict + `ResolvedProject` + warnings)
  - `POST /api/render.glb` — GLB bytes
  - `POST /api/cutlist` — cut list JSON
  - `GET  /api/stdlib` — available preset names
- **Python entry point**: `cabinetry.compiler.compile.compile_dsl(text: str) -> tuple[dict, ResolvedProject]`
- **DSL format**: YAML (see `examples/` and §24 of the plan for the canonical example).
- **GLB schema**: standard glTF 2.0 binary; one mesh node per `Part`, named by `part.id`.

## Storage and Artifacts

- No persistent database. All state is in-memory per request.
- `src/cabinetry/stdlib/*.yaml` — bundled preset library (source of truth for standards/materials/systems).
- GLB, cut-list CSV/JSON — generated on demand, returned as HTTP responses (not persisted).
- `examples/*.yaml` — canonical example DSL files (not persisted on server).

## Extension Points

- **New stdlib presets**: add entries to the relevant `*.yaml` file; no code changes needed.
- **New bay functions**: extend `parse_bay_function()` in `dsl/shorthand.py` and add a generator branch in `compiler/parts_generator.py`.
- **New output formats**: add a module under `outputs/` consuming `ResolvedProject`; wire a new route in `app/routes.py`.
- **New door styles**: add to `door_styles.yaml` and extend `doors_generator.py`.
- **New export formats (DXF, STEP, SVG)**: add under `outputs/` or `geometry/`; must consume `ResolvedProject`, not meshes.

## Implementation Constraints

- Python 3.12+.
- Pydantic v2 for all DTOs and stdlib spec models.
- `CompileContext` is a `@dataclass` (mutable internal state, not a DTO).
- DXF, STL, STEP, GLB/glTF, SVG, CSV are **export formats only** — never used as DSL or internal source of truth.
- Cut list dimensions must come from `Part.length / width / thickness`, never from mesh bounding boxes.
- `PartAxes` drives all mesh placement; geometry must not infer orientation from part kind.
- black + flake8 for formatting/linting (no ruff).
- No backward compatibility required.
- Keep subsystem boundaries clear and update this file when they change.
