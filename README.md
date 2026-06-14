# CabScript — Cabinet Design DSL

A cabinet design tool that compiles a compact YAML DSL into a 3D model, cut list, and parts list. Includes a React-based browser UI.

## Requirements

- Python 3.12+
- Node.js 18+ and npm
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Local development

There are two ways to run locally depending on whether you're working on the frontend.

### Option A — Frontend dev mode (hot reload for UI changes)

Run the FastAPI backend and the Vite dev server separately:

```bash
# Terminal 1 — Python backend (API only)
uv sync
uv run uvicorn cabinetry.app.main:app --reload

# Terminal 2 — React frontend (hot reload)
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The Vite dev server proxies all `/api` requests to the FastAPI backend at `:8000`, so no CORS configuration is needed.

### Option B — Backend-only (no Node.js required)

Build the React frontend once, then run only the Python server:

```bash
# Build the frontend (outputs to src/cabinetry/app/static/)
cd frontend
npm install
npm run build
cd ..

# Run the backend — it serves the built React app as static files
uv sync
uv run uvicorn cabinetry.app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000). Use this mode when you only need to work on the backend.

### Run tests

```bash
uv run pytest
```

### Environment variables

Copy `.env` to `.env.local` for local overrides (`.env.local` is gitignored):

```bash
cp .env .env.local
```

| Variable | Default | Description |
|---|---|---|
| `CABSCRIPT_ROOT` | `./data` | Directory for generated output files |

## Usage

Click **New Project** to start with the default closet template, or **Open Project** to load a `.yaml` file.

In the main editor:
- **DSL editor (left)** — edit the YAML design; the app auto-compiles 600 ms after you stop typing
- **Front view / 3D (center)** — click the tab to switch views; click a bay in the front view to inspect it
- **Properties (right)** — change material, standard, and finish colors; selected element details appear here
- **Messages / Cut List (bottom)** — compile warnings and the full cut list

### Example DSL

```yaml
use: euro_builtin_v1
material: plywood_18

space: niche 1200 x 2650 x 600

cabinet:
  type: built_in
  split: auto
  base: legs 80

layout:
  top: storage 380
  main:
    columns:
      400: shelves 5 adjustable
      500: hanging rod 1700
      "*": shoes 4

doors:
  top: auto
  main: auto
  style: slab
  hinges: concealed

finish:
  body: warm_white
  doors: oak
```

More examples are in `src/cabinetry/examples/`.

## API

The backend exposes a JSON API at `/api`:

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/parse` | POST | Parse and normalize DSL, return raw + normalized dict |
| `/api/compile` | POST | Compile DSL, return resolved project model + warnings |
| `/api/render.glb` | POST | Compile and return a GLB binary for 3D rendering |
| `/api/cutlist` | POST | Compile and return cut list as JSON + CSV |
| `/api/stdlib` | GET | List available standards and materials |

All POST endpoints accept `{"dsl": "<yaml string>"}`.

## Deployment

### Docker (recommended)

```bash
# Build image
docker build -t cabscript .

# Run
docker run -p 8000:8000 cabscript
```

Create a `Dockerfile` at the repo root:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev
COPY src/ src/
COPY .env .env
CMD ["uv", "run", "uvicorn", "cabinetry.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Fly.io

```bash
fly launch --name cabscript
fly deploy
```

### Railway / Render

Set the start command to:

```
uvicorn cabinetry.app.main:app --host 0.0.0.0 --port $PORT
```

And set the build command to:

```
uv sync --frozen
```

### Manual (any Linux server)

```bash
uv sync --frozen
uv run uvicorn cabinetry.app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

For production, put Nginx in front as a reverse proxy.

## Project structure

```
frontend/                React + TypeScript UI (Vite)
  src/
    components/          UI components (editor, viewer, properties panel, inspector)
    store/               Zustand state (DSL text, compiled project, selection)
    api/                 Typed fetch wrappers for /api/*
    types/               TypeScript mirrors of the Python domain models

src/cabinetry/
  app/          FastAPI app, routes, static frontend (built React output)
  dsl/          YAML parser, dimension parser, shorthand normalizer
  stdlib/       Standard library YAML files (standards, materials, door systems, …)
  model/        Pydantic data models (source of truth)
  compiler/     Pipeline: dimension resolution → module split → layout → parts → doors
  geometry/     Trimesh mesh generation and GLB export
  outputs/      Cut list (JSON + CSV), BOM, SVG views

tests/          pytest test suite
```

## Standard library

Built-in presets (see `src/cabinetry/stdlib/`):

| Type | Available |
|---|---|
| Standards | `euro_builtin_v1` |
| Materials | `plywood_18`, `mdf_18` |
| Door systems | `concealed_full_overlay` |
| Door styles | `slab`, `frame_panel_light` |
| Shelf systems | `shelf_pins_32`, `cleats_basic` |
| Base systems | `adjustable_legs_80` |
