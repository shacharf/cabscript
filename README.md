# CabScript — Cabinet Design DSL

A cabinet design tool that compiles a compact YAML DSL into a 3D model, cut list, and parts list. Includes a browser-based 3D viewer.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — install with `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Local development

```bash
# Install dependencies
uv sync

# Run the dev server (auto-reloads on file changes)
uv run uvicorn cabinetry.app.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

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

Paste a DSL document into the left panel, then:

- **Compile** — validates the DSL and shows warnings/errors
- **Render 3D** — compiles, renders a 3D model, and displays the cut list

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
src/cabinetry/
  app/          FastAPI app, routes, static frontend
  dsl/          YAML parser, dimension parser, shorthand normalizer
  stdlib/       Standard library YAML files (standards, materials, door systems, …)
  model/        Pydantic data models (source of truth)
  compiler/     Pipeline: dimension resolution → module split → layout → parts → doors
  geometry/     Trimesh mesh generation and GLB export
  outputs/      Cut list (JSON + CSV), BOM, SVG views

tests/          pytest test suite (51 tests)
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
