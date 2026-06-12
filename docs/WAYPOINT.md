# Waypoint

Current implementation status. `docs/NORTH_STAR.md` remains the long-term vision; this file tracks current reality and near-term direction.

## Current State

Project is in the planning phase. No source code exists yet. The detailed implementation plan lives in `docs/plans/3_cabinet_design_coding_agent_plan.md`.

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
```

## Active Direction

Build the `cabinetry` Python package in phases as specified in the plan (§23). Phase 1 targets a working skeleton: package structure, FastAPI app, static frontend placeholder, and a passing `/api/health` endpoint.

The core rule driving all decisions: **DXF, STL, STEP, GLB, SVG, and CSV are export formats only — never the DSL or internal source of truth.**

## Decisions

- Internal source of truth is a typed Pydantic v2 semantic model (`ResolvedProject`).
- Coordinate system: X = width, Y = height, Z = depth; cabinet origin at back-left-bottom.
- Module split: `main_plus_top` mode — split when body height exceeds max board length.
- Cut list dimensions come from `Part.length / width / thickness` manufacturing fields, never from mesh bounding boxes.
- Technology stack: Python 3.12+, FastAPI, Pydantic v2, PyYAML, trimesh, NumPy, Three.js; uv for virtual-env and dependency management.
- Linting: black + flake8 (no ruff).
- Storage root is read from the `CABSCRIPT_ROOT` env var (loaded via `python-dotenv`); default is `<repo root>/data`. Backend storage integration deferred.

## Current Constraints

- No source code exists yet — all phases remain to be implemented.
- MVP supports only one `*` column per row and one `*` row per module in the layout solver.
- Door generation is slab-only for MVP; frame-and-panel is a future extension.
- Hardware is represented semantically; approximate rendering only for MVP.
- SVG views are optional (post-GLB).

## Open Questions

- None currently.

## Next

1. Scaffold the `cabinetry/` repo structure from §3 of the plan (directories, `pyproject.toml`, empty `__init__.py` files).
2. Implement the FastAPI skeleton (`app/main.py`, `app/routes.py`) with `/api/health`.
3. Add static frontend placeholder (`app/static/index.html`).
4. Configure pytest and verify tests run.
5. Move to Phase 2: DSL parser, dimension parser, shorthand normalizer, stdlib YAML files.
