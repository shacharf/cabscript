# Plan: React UI — Phase 1 (Implemented)

## Goal

Replace the vanilla JS frontend with a well-structured React + TypeScript SPA. Phase 1 delivers a complete interactive editing environment matching the layout spec below.

```
<MenuBar>
------------------------------------------------------------------
DSL editor | 2D front view / 3D viewer  | Global properties
(Monaco)   | [Front View] [3D] toggle   |-------------------------
           |                            | Color palette
           |                            |-------------------------
           |                            | Selected element
------------------------------------------------------------------
Messages / Cut List (bottom inspector)
```

## Tech Stack

| Concern | Choice |
|---|---|
| Framework | React 19 + TypeScript via Vite |
| DSL editor | `@monaco-editor/react` (YAML syntax, `automaticLayout`) |
| 3D viewer | Three.js + OrbitControls + GLTFLoader |
| State | Zustand (single flat store) |
| Styling | Custom CSS modules, dark theme (`#050a18` / `#1a1e26` / `#1e2230`) |
| UI library | None |

## File Layout

```
frontend/
  index.html
  vite.config.ts           # build → ../src/cabinetry/app/static, proxy /api → :8000
  tsconfig.json / tsconfig.app.json / tsconfig.node.json
  package.json
  src/
    main.tsx
    App.tsx                # StartScreen gate → AppShell
    vite-env.d.ts          # CSS module + asset type declarations
    types/cabinet.ts       # TypeScript mirrors of all Python Pydantic models
    store/useStore.ts      # Zustand store (see State Shape below)
    api/client.ts          # Typed fetch wrappers (apiCompile, apiRenderGlb, apiCutlist, apiStdlib)
    styles/global.css      # CSS reset + dark-theme variables
    components/
      StartScreen/         # Open file / New project modal
      AppShell/            # MenuBar + 3-column layout shell
      DslEditor/           # Monaco editor (auto-compiles 600ms after keystroke)
      Viewer/              # Tab switcher + View2d + View3d
      PropertiesPanel/     # Right rail: GlobalProperties + ColorPalette + SelectedProperties
      Inspector/           # Bottom: WarningsTable + CutlistTable
```

## State Shape (Zustand)

```ts
interface CabinetStore {
  fileName: string | null;          // null = show StartScreen
  dslText: string;                  // single source of truth for YAML
  isDirty: boolean;

  project: ResolvedProject | null;  // last successful compile
  warnings: ValidationMessage[];
  cutlist: CutlistItem[];
  compileStatus: 'idle' | 'compiling' | 'ok' | 'error';
  compileError: string | null;

  activeView: '2d' | '3d';
  doorsVisible: boolean;
  glbBlobUrl: string | null;        // revocable blob URL for GLTFLoader

  selectedBayId: string | null;
  selectedPartId: string | null;

  stdlib: StdLibData | null;        // loaded once on mount
}
```

## Key Component Decisions

### DslEditor
Monaco YAML editor, controlled via `store.dslText`. `onChange` debounced 600 ms → `store.compile()`.

### View2d
Port of `draw2dFront` from `viewer.js:240-380`. Canvas `useRef` + `useEffect` on `[project, doorsVisible]`. During draw, fills a `HitRegion[]` ref (`{kind, id, x, y, w, h}`). Canvas `onClick` iterates regions in reverse draw order to identify clicked bay or part. `ResizeObserver` on the container triggers redraws.

### View3d
Port of `initThree` + `loadGlb` from `viewer.js:1-222`. Three.js init in a one-shot `useEffect`. Separate effects watch `glbBlobUrl` (swap model) and `doorsVisible` (traverse mesh names). Both views are always mounted; only visibility toggles — this preserves the WebGL context across tab switches.

### GlobalProperties
Reads display values from `project` (never parses raw YAML). On change, applies a targeted regex line-replace on the top-level DSL key (`^use:`, `^material:`, `^\s+type:`, etc.) and writes back via `store.setDslText`. Handles missing keys by appending.

### ColorPalette
Same line-replace strategy targeting `finish.body:`, `finish.doors:`, `finish.shelves:`. Color names and RGBA values sourced from `stdlib.colors`.

### StartScreen / MenuBar
- **Open**: `<input type="file" accept=".yaml,.yml">` → `FileReader` → `store.loadFile`
- **New**: `store.newProject()` sets `dslText` to built-in `niche_closet.yaml` template
- **Save**: `new Blob([dslText])` → anchor `download` click (no server involvement)

## Backend Changes

| File | Change |
|---|---|
| `stdlib/loader.py` | Added `all_colors() → dict` (mirrors `all_materials` pattern) |
| `app/routes.py` | `/api/stdlib` response now includes `"colors"` key |
| `app/main.py` | Added `/assets` static mount (serves Vite's `assets/` chunk directory) |

## Build / Dev

**Dev (hot reload):**
```bash
# Terminal 1
uv run uvicorn cabinetry.app.main:app --reload

# Terminal 2
cd frontend && npm run dev   # → http://localhost:5173
```

**Production build:**
```bash
cd frontend && npm run build   # emits to src/cabinetry/app/static/
uv run uvicorn cabinetry.app.main:app   # serves SPA at http://localhost:8000
```

Vite config sets `build.outDir = '../src/cabinetry/app/static'` and proxies `/api → http://localhost:8000` in dev.
