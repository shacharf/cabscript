# Cabinet Design Application — Detailed Coding Agent Plan

## 1. Implementation objective

Build a Python 3.12+ application that compiles a compact cabinet DSL into a semantic cabinet model, generates a parts list and cut list, exports a GLB model for web-based 3D rendering, and serves an interactive browser viewer.

The key architectural rule is:

> DXF, STL, STEP, GLB/glTF, SVG, CSV, and SketchUp-related outputs are export formats only. They must not be used as the user DSL or as the internal source of truth.

The source of truth is a typed internal semantic model.

## 2. Technology requirements

Use:

- Python 3.12+
- Clean reusable code
- Modular architecture
- Type hints throughout
- Pydantic v2 for data models
- FastAPI for the backend API
- PyYAML for DSL parsing
- trimesh for GLB/glTF export
- NumPy as needed for geometry
- Three.js for web rendering
- pytest for tests
- black, flake8 for formatting/linting. Do not use ruff
- mypy if practical

Recommended packages:

Use **uv** for virtual-environment and dependency management (`uv sync`, `uv run`).

```toml
[project]
requires-python = ">=3.12"
dependencies = [
  "fastapi",
  "uvicorn[standard]",
  "pydantic>=2",
  "pyyaml",
  "trimesh",
  "numpy",
  "jinja2",
  "python-multipart",
  "python-dotenv",
]

[project.optional-dependencies]
dev = [
  "pytest",
  "pytest-cov",
  "mypy",
  "httpx",
]
future_dxf = ["ezdxf"]
future_nesting = ["rectpack"]
```

## 2.5 Environment configuration

Use `python-dotenv` to load environment variables from a `.env` file at startup.

Create a `.env` file at the repo root (committed with safe defaults; real overrides go in `.env.local` which is gitignored):

```dotenv
# Root directory for runtime data (generated files, future backend storage).
# Defaults to <repo root>/data if unset.
CABSCRIPT_ROOT=
```

In `app/main.py` (or a dedicated `config.py`), resolve the storage root:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[3]  # adjust depth to match package layout
CABSCRIPT_ROOT = Path(os.environ.get("CABSCRIPT_ROOT") or REPO_ROOT / "data")
CABSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)
```

Backend storage integration (database, object store, etc.) is deferred. For now all generated artefacts are either returned in-memory over HTTP or written under `CABSCRIPT_ROOT`.

## 3. Repository structure

Create this structure:

```text
cabinetry/
  pyproject.toml
  README.md
  .env               safe defaults (committed)
  .env.local         local overrides (gitignored)
  data/              default CABSCRIPT_ROOT output directory (gitignored)

  src/
    cabinetry/
      __init__.py

      app/
        __init__.py
        main.py
        routes.py
        static/
          index.html
          viewer.js
          styles.css

      dsl/
        __init__.py
        parser.py
        shorthand.py
        dimensions.py
        errors.py

      stdlib/
        __init__.py
        loader.py
        standards.yaml
        materials.yaml
        door_systems.yaml
        door_styles.yaml
        shelf_systems.yaml
        base_systems.yaml
        colors.yaml

      model/
        __init__.py
        primitives.py
        materials.py
        space.py
        cabinet.py
        layout.py
        parts.py
        doors.py
        hardware.py
        project.py
        validation.py

      compiler/
        __init__.py
        context.py
        defaults.py
        normalize.py
        resolve_dimensions.py
        modules.py
        layout_solver.py
        parts_generator.py
        shelves_generator.py
        doors_generator.py
        hardware_generator.py
        warnings.py
        compile.py

      geometry/
        __init__.py
        coordinates.py
        mesh.py
        materials.py
        scene.py
        export.py

      outputs/
        __init__.py
        cutlist.py
        bom.py
        svg_views.py

      examples/
        niche_closet.yaml
        standing_cabinet.yaml
        kitchen_base.yaml

  tests/
    test_dsl_parser.py
    test_dimensions.py
    test_shorthand.py
    test_stdlib_loader.py
    test_defaults_merge.py
    test_module_split.py
    test_layout_solver.py
    test_parts_generator.py
    test_doors_generator.py
    test_cutlist.py
    test_geometry_export.py
    test_api.py
```

## 4. Conceptual pipeline

Implement this pipeline:

```text
DSL text
  ↓
Parse YAML
  ↓
Raw DSL dictionary
  ↓
Normalize shorthand
  ↓
Merge with standard library defaults
  ↓
Validate request
  ↓
Resolve dimensions
  ↓
Resolve modules
  ↓
Resolve layout rows/columns/bays
  ↓
Generate semantic parts
  ↓
Generate doors and hardware
  ↓
Validate resolved model
  ↓
Generate outputs:
    - internal JSON model
    - GLB for web rendering
    - CSV/JSON cut list
    - SVG views, later
    - DXF/STEP/OpenCutList bridge, later
```

Keep parsing, compilation, geometry, outputs, and web API separate.

## 5. Coordinate system

Use this global coordinate system:

```text
X = width, left to right
Y = height, bottom to top
Z = depth, front to back
```

Cabinet origin:

```text
(0, 0, 0) = back-left-bottom of installed cabinet envelope
```

If there is a base/legs/plinth, the carcass begins above the base:

```text
carcass_origin_z = base_height
```

## 6. Internal model design

The internal semantic model is the source of truth.

### 6.1 Primitive models

File: `model/primitives.py`

```python
from typing import Literal
from pydantic import BaseModel

Mm = float

class Vec3(BaseModel):
    x: Mm
    y: Mm
    z: Mm

class Size3(BaseModel):
    width: Mm
    depth: Mm
    height: Mm

AxisName = Literal["x", "y", "z"]

class PartAxes(BaseModel):
    length_axis: AxisName
    width_axis: AxisName
    thickness_axis: AxisName
```

### 6.2 Material models

File: `model/materials.py`

```python
from pydantic import BaseModel
from .primitives import Mm

class SheetSize(BaseModel):
    length: Mm
    width: Mm

class MaterialSpec(BaseModel):
    name: str
    body_thickness: Mm
    shelf_thickness: Mm
    door_thickness: Mm
    back_thickness: Mm
    max_board: SheetSize
    density_kg_m3: float | None = None
    default_finish: str | None = None
```

### 6.3 Space model

File: `model/space.py`

```python
from typing import Literal
from pydantic import BaseModel
from .primitives import Mm

class NicheSpec(BaseModel):
    width: Mm
    height: Mm
    depth: Mm

class SpaceSpec(BaseModel):
    kind: Literal["niche", "free"]
    niche: NicheSpec | None = None
```

### 6.4 Cabinet request model

File: `model/cabinet.py`

```python
from typing import Literal
from pydantic import BaseModel
from .primitives import Mm

class CabinetRequest(BaseModel):
    type: Literal["built_in", "standing", "kitchen_base", "kitchen_wall", "wardrobe"]
    width: Mm | Literal["auto"] = "auto"
    height: Mm | Literal["auto"] = "auto"
    depth: Mm | Literal["auto"] = "auto"
    split: Literal["auto", "none"] | list[Mm] = "auto"
    base: str | None = None

class ResolvedModule(BaseModel):
    id: str
    name: str
    x: Mm
    y: Mm
    z: Mm
    width: Mm
    depth: Mm
    height: Mm
```

### 6.5 Layout model

File: `model/layout.py`

```python
from typing import Literal, Any
from pydantic import BaseModel, Field
from .primitives import Mm

class BayFunction(BaseModel):
    kind: Literal["shelves", "hanging", "drawers", "shoes", "storage", "hooks", "empty"]
    params: dict[str, Any] = Field(default_factory=dict)

class ColumnSpec(BaseModel):
    width: Mm | Literal["*"]
    function: BayFunction

class RowSpec(BaseModel):
    height: Mm | Literal["*"]
    columns: list[ColumnSpec]

class LayoutSpec(BaseModel):
    rows: list[RowSpec]

class ResolvedBay(BaseModel):
    id: str
    module_id: str
    row_index: int
    col_index: int
    x: Mm
    y: Mm
    z: Mm
    width: Mm
    depth: Mm
    height: Mm
    function: BayFunction
```

### 6.6 Part model

File: `model/parts.py`

```python
from typing import Literal
from pydantic import BaseModel, Field
from .primitives import Mm, Vec3, PartAxes

PartKind = Literal[
    "side_panel",
    "top_panel",
    "bottom_panel",
    "shelf",
    "divider",
    "back_panel",
    "door",
    "drawer_front",
    "filler",
    "plinth",
    "rail",
    "cleat",
]

EdgeName = Literal["front", "back", "left", "right", "top", "bottom"]

class Operation(BaseModel):
    kind: str
    params: dict = Field(default_factory=dict)

class Part(BaseModel):
    id: str
    name: str
    kind: PartKind
    module_id: str | None = None
    material: str

    # Manufacturing dimensions.
    length: Mm
    width: Mm
    thickness: Mm

    # 3D placement.
    origin: Vec3
    axes: PartAxes

    grain_direction: Literal["length", "width", "none"] = "none"
    edge_banding: list[EdgeName] = Field(default_factory=list)
    operations: list[Operation] = Field(default_factory=list)
```

Important: `length`, `width`, and `thickness` are manufacturing dimensions. Do not derive the cut list from arbitrary mesh bounding boxes.

### 6.7 Hardware model

File: `model/hardware.py`

```python
from typing import Literal
from pydantic import BaseModel, Field
from .primitives import Mm, Vec3

class HardwareItem(BaseModel):
    id: str
    kind: Literal["hinge", "shelf_pin", "rod", "leg", "handle", "drawer_slide", "screw"]
    name: str
    position: Vec3 | None = None
    params: dict = Field(default_factory=dict)
```

### 6.8 Validation model

File: `model/validation.py`

```python
from enum import Enum
from pydantic import BaseModel

class Severity(str, Enum):
    info = "info"
    warning = "warning"
    error = "error"

class ValidationMessage(BaseModel):
    severity: Severity
    code: str
    message: str
    path: str | None = None
```

### 6.9 Resolved project model

File: `model/project.py`

```python
from pydantic import BaseModel, Field
from .cabinet import ResolvedModule
from .layout import ResolvedBay
from .parts import Part
from .hardware import HardwareItem
from .validation import ValidationMessage

class ResolvedProject(BaseModel):
    units: str = "mm"
    standard: str
    material: str
    width: float
    height: float
    depth: float
    modules: list[ResolvedModule] = Field(default_factory=list)
    bays: list[ResolvedBay] = Field(default_factory=list)
    parts: list[Part] = Field(default_factory=list)
    hardware: list[HardwareItem] = Field(default_factory=list)
    warnings: list[ValidationMessage] = Field(default_factory=list)
```

## 7. DSL parsing and normalization

### 7.1 YAML parser

File: `dsl/parser.py`

Implement:

```python
def parse_dsl(text: str) -> dict:
    ...
```

Requirements:

- Use `yaml.safe_load`.
- Reject empty documents.
- Reject non-mapping top-level documents.
- Raise custom `DslSyntaxError` with useful messages.

### 7.2 Dimension parser

File: `dsl/dimensions.py`

Implement:

```python
def parse_3d_dimensions(text: str) -> tuple[float, float, float]:
    """Parse '1200 x 2650 x 600' into width, height, depth."""
```

Support:

```text
1200 x 2650 x 600
1200x2650x600
1200 X 2650 X 600
```

Reject invalid forms.

### 7.3 Shorthand normalization

File: `dsl/shorthand.py`

Implement:

```python
def normalize_shorthand(raw: dict) -> dict:
    ...
```

Normalize:

```yaml
use: euro_builtin_v1
```

into:

```yaml
use:
  standard: euro_builtin_v1
```

Normalize:

```yaml
material: plywood_18
```

into:

```yaml
use:
  material: plywood_18
```

Normalize:

```yaml
space: niche 1200 x 2650 x 600
```

into:

```yaml
space:
  kind: niche
  niche:
    width: 1200
    height: 2650
    depth: 600
```

Normalize layout shorthand:

```yaml
layout:
  main:
    columns:
      400: shelves 5 adjustable
      500: hanging rod 1700
      "*": shoes 4
```

into explicit rows and columns.

### 7.4 Bay function parsing

Implement:

```python
def parse_bay_function(text: str) -> BayFunction:
    ...
```

Support MVP patterns:

```text
shelves 5
shelves 5 adjustable
hanging
hanging rod 1700
shoes 4
storage
empty
```

Parsed examples:

```text
shelves 5 adjustable
→ kind=shelves, params={count: 5, adjustable: true}

hanging rod 1700
→ kind=hanging, params={rod_height: 1700}

shoes 4
→ kind=shoes, params={rows: 4}
```

## 8. Standard library implementation

File: `stdlib/loader.py`

Implement:

```python
class StdLib:
    def get_standard(self, name: str) -> StandardSpec: ...
    def get_material(self, name: str) -> MaterialSpec: ...
    def get_door_system(self, name: str) -> DoorSystemSpec: ...
    def get_door_style(self, name: str) -> DoorStyleSpec: ...
    def get_shelf_system(self, name: str) -> ShelfSystemSpec: ...
    def get_base_system(self, name: str) -> BaseSystemSpec: ...
    def get_color(self, name: str) -> ColorSpec: ...
```

Each getter loads the corresponding YAML file on first access (or at construction), finds the named entry, and deserializes it with `Model(**data)`. Unknown names should raise a `StdLibLookupError` with the available keys listed.

Load YAML files from package resources.

### 8.0 Stdlib Pydantic spec models

File: `stdlib/specs.py`

These models mirror the structure of the stdlib YAML files. `MaterialSpec` is imported from `model/materials.py` (already defined in §6.2); all others live here.

```python
from __future__ import annotations
from pydantic import BaseModel
from .model.primitives import Mm


# --- Standard spec ---

class CabinetDefaults(BaseModel):
    default_depth: Mm

class ClearancesSpec(BaseModel):
    side_each: Mm
    top: Mm
    back: Mm
    door_gap: Mm

class FillersSpec(BaseModel):
    side: str   # "auto" | "none" | float
    top: str

class CarcassSpec(BaseModel):
    top_panel: bool
    bottom_panel: bool
    back_panel: bool
    back_panel_method: str  # "surface_applied" | "rabbeted"

class ModuleSplitSpec(BaseModel):
    mode: str  # "main_plus_top" | "equal" | "none"
    default_main_height: Mm
    min_top_module_height: Mm
    max_single_module_height_margin: Mm

class ShelfDefaultsSpec(BaseModel):
    default_support: str
    adjustable_shelf_clearance: Mm

class DoorDefaultsSpec(BaseModel):
    default_system: str
    default_style: str

class StandardSpec(BaseModel):
    construction: str  # "frameless" | "face_frame"
    cabinet: CabinetDefaults
    clearances: ClearancesSpec
    fillers: FillersSpec
    carcass: CarcassSpec
    module_split: ModuleSplitSpec
    shelf: ShelfDefaultsSpec
    doors: DoorDefaultsSpec


# --- Door system spec ---

class HingeCountRule(BaseModel):
    max_height: Mm
    count: int

class DoorSystemSpec(BaseModel):
    hinge_type: str
    overlay: str  # "full" | "half" | "inset"
    gap: Mm
    cup_diameter: Mm
    cup_depth: Mm
    default_cup_distance_from_edge: Mm
    hinge_count_rule: list[HingeCountRule]


# --- Door style spec ---

class MiddleRailSpec(BaseModel):
    min_height: Mm
    count: int

class DoorStyleSpec(BaseModel):
    type: str  # "slab" | "frame_panel"
    frame_width: Mm | None = None
    frame_thickness: Mm | None = None
    panel_thickness: Mm | None = None
    groove_depth: Mm | None = None
    middle_rail: MiddleRailSpec | None = None


# --- Shelf system spec ---

class ShelfSystemSpec(BaseModel):
    type: str  # "shelf_pins" | "cleats" | "fixed"
    pin_diameter: Mm | None = None
    hole_spacing: Mm | None = None
    front_offset: Mm | None = None
    back_offset: Mm | None = None
    hole_depth: Mm | None = None
    cleat_height: Mm | None = None
    cleat_thickness: Mm | None = None


# --- Base system spec ---

class BaseSystemSpec(BaseModel):
    type: str  # "adjustable_legs" | "plinth_box" | "wall_mounted"
    height: Mm
    plinth: str | None = None   # "recessed" | "flush"
    front_setback: Mm | None = None


# --- Color spec ---

class ColorSpec(BaseModel):
    rgba: tuple[int, int, int, int]
    description: str | None = None
```

### 8.1 `standards.yaml`

Create:

```yaml
euro_builtin_v1:
  construction: frameless
  cabinet:
    default_depth: 580
  clearances:
    side_each: 8
    top: 10
    back: 0
    door_gap: 3
  fillers:
    side: auto
    top: auto
  carcass:
    top_panel: true
    bottom_panel: true
    back_panel: true
    back_panel_method: surface_applied
  module_split:
    mode: main_plus_top
    default_main_height: 2250
    min_top_module_height: 250
    max_single_module_height_margin: 30
  shelf:
    default_support: shelf_pins_32
    adjustable_shelf_clearance: 2
  doors:
    default_system: concealed_full_overlay
    default_style: slab
```

### 8.2 `materials.yaml`

Create:

```yaml
plywood_18:
  body_thickness: 18
  shelf_thickness: 18
  door_thickness: 18
  back_thickness: 6
  max_board:
    length: 2420
    width: 1220
  density_kg_m3: 650

mdf_18:
  body_thickness: 18
  shelf_thickness: 18
  door_thickness: 18
  back_thickness: 3
  max_board:
    length: 2440
    width: 1220
  density_kg_m3: 750
```

### 8.3 `door_systems.yaml`

Create:

```yaml
concealed_full_overlay:
  hinge_type: concealed_35mm
  overlay: full
  gap: 3
  cup_diameter: 35
  cup_depth: 12
  default_cup_distance_from_edge: 22
  hinge_count_rule:
    - max_height: 900
      count: 2
    - max_height: 1600
      count: 3
    - max_height: 2300
      count: 4
    - max_height: 2600
      count: 5
```

### 8.4 `door_styles.yaml`

Create:

```yaml
slab:
  type: slab

frame_panel_light:
  type: frame_panel
  frame_width: 60
  frame_thickness: 25
  panel_thickness: 4
  groove_depth: 8
  middle_rail:
    min_height: 1500
    count: 1
```

### 8.5 `shelf_systems.yaml`

Create:

```yaml
shelf_pins_32:
  type: shelf_pins
  pin_diameter: 5
  hole_spacing: 32
  front_offset: 37
  back_offset: 37
  hole_depth: 12

cleats_basic:
  type: cleats
  cleat_height: 30
  cleat_thickness: 18
```

### 8.6 `base_systems.yaml`

Create:

```yaml
adjustable_legs_80:
  type: adjustable_legs
  height: 80
  plinth: recessed
  front_setback: 50
```

### 8.7 `colors.yaml`

TODO: Create an initial version of this file mapping finish names to RGB values used for GLB material colours.

Each entry should map a finish name (as used in the DSL `finish:` block) to an RGBA tuple. At minimum cover the defaults referenced in example DSLs.

Example structure:

```yaml
warm_white:
  rgba: [245, 240, 235, 255]
  description: Off-white body finish

oak:
  rgba: [180, 140, 90, 255]
  description: Natural oak door finish

white:
  rgba: [255, 255, 255, 255]

anthracite:
  rgba: [55, 55, 60, 255]
```

The `geometry/scene.py` builder should look up part finish via the role (`body`, `doors`, `shelves`, `back`) from the resolved project, resolve the finish name, and load the colour from `colors.yaml`.

## 9. Defaults merge

File: `compiler/defaults.py`

Implement deep merge with precedence:

```text
stdlib base defaults < selected standard < selected systems/materials < user DSL
```

User values must always win.

Implement:

```python
def deep_merge(base: dict, override: dict) -> dict:
    ...
```

## 9.5 Compile context

File: `compiler/context.py`

`CompileContext` is the working state object threaded through the entire compiler pipeline. It carries the raw and normalized DSL, all resolved stdlib presets, accumulated warnings and errors, and shared helper methods.

Use `@dataclass` rather than Pydantic — this is mutable internal state, not a DTO.

Note: `get_standard`, `get_material`, and related stdlib loader methods must return typed `*Spec` Pydantic models (not bare `dict`) so that context fields are fully type-safe.

```python
from dataclasses import dataclass, field
from .model.materials import MaterialSpec
from .model.validation import ValidationMessage, Severity
from .stdlib.specs import StandardSpec, DoorSystemSpec, DoorStyleSpec, ShelfSystemSpec, BaseSystemSpec
from .stdlib.loader import StdLib


@dataclass
class CompileContext:
    raw_dsl: dict
    normalized_dsl: dict
    stdlib: StdLib
    standard: StandardSpec
    material: MaterialSpec
    door_system: DoorSystemSpec
    door_style: DoorStyleSpec
    shelf_system: ShelfSystemSpec
    base_system: BaseSystemSpec | None

    warnings: list[ValidationMessage] = field(default_factory=list)
    errors: list[ValidationMessage] = field(default_factory=list)

    def warn(self, code: str, message: str, path: str | None = None) -> None:
        self.warnings.append(
            ValidationMessage(severity=Severity.warning, code=code, message=message, path=path)
        )

    def error(self, code: str, message: str, path: str | None = None) -> None:
        self.errors.append(
            ValidationMessage(severity=Severity.error, code=code, message=message, path=path)
        )

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
```

Compiler functions receive `ctx` as their first argument and call `ctx.warn()` / `ctx.error()` in place of raising for non-fatal issues. Fatal errors (impossible geometry, unknown preset) should still raise immediately.

Example usage:

```python
def resolve_dimensions(ctx: CompileContext) -> ResolvedDimensions:
    clearances = ctx.standard.clearances
    niche = ctx.normalized_dsl["space"]["niche"]

    cabinet_width = niche["width"] - 2 * clearances.side_each

    if cabinet_width <= 0:
        ctx.error("INVALID_WIDTH", "Cabinet width is not positive after applying clearances.")

    return ResolvedDimensions(width=cabinet_width, ...)
```

## 10. Dimension resolution

File: `compiler/resolve_dimensions.py`

Implement:

```python
def resolve_cabinet_dimensions(ctx: CompileContext) -> tuple[float, float, float]:
    ...
```

For built-in niche:

```text
cabinet_width  = niche_width  - 2 * side_clearance
cabinet_height = niche_height - top_clearance
cabinet_depth  = niche_depth  - back_clearance
```

For standing cabinet:

- Require explicit dimensions unless standard provides defaults.

Conventions:

```text
cabinet.height includes base/legs/plinth.
body_height = cabinet.height - base_height.
```

## 11. Module splitting

File: `compiler/modules.py`

Implement:

```python
def resolve_modules(ctx: CompileContext, width: float, height: float, depth: float) -> list[ResolvedModule]:
    ...
```

MVP auto split rule:

```text
available_body_height = cabinet_height - base_height

if split == none:
    create one module with height = available_body_height

if split == auto:
    if available_body_height <= max_board_length - margin:
        create one module
    else:
        main_height = min(default_main_height, max_board_length - margin)
        top_height = available_body_height - main_height
        if top_height < min_top_module_height:
            adjust main_height or emit warning
        create main module and top module
```

Example:

```text
niche height = 2650
base height = 80
top clearance = 10
cabinet height = 2640
body height = 2560
max board length = 2420
default main = 2250

main module = 2250
top module = 310
```

Generated modules:

```text
base at z=0..80
main module at z=80..2330
top module at z=2330..2640
```

## 12. Layout solver

File: `compiler/layout_solver.py`

Implement:

```python
def resolve_layout(ctx: CompileContext, modules: list[ResolvedModule]) -> list[ResolvedBay]:
    ...
```

MVP behavior:

- If DSL has `layout.top`, apply it to the top module.
- If DSL has `layout.main`, apply it to the main module.
- If only one module exists, apply `layout.main` or whole layout to it.
- Support row/column grids.

Column resolution:

```text
inner_width = module.width - 2 * body_thickness
sum_fixed = sum(fixed column widths)
remaining = inner_width - sum_fixed
"*" column gets remaining
```

Row resolution:

```text
inner_height = module.height - top_panel_thickness - bottom_panel_thickness
sum_fixed = sum(fixed row heights)
remaining = inner_height - sum_fixed
"*" row gets remaining
```

For MVP, allow only one `*` column per row and one `*` row per module.

## 13. Parts generation

File: `compiler/parts_generator.py`

Generate rectangular board parts from modules and bays.

### 13.1 Carcass parts

Use frameless construction with top/bottom between side panels.

For each module:

```text
left side:
  length = module.height
  width = module.depth
  thickness = body_thickness
  axes = length:y, width:z, thickness:x

right side:
  same, origin.x = module.width - thickness

bottom:
  length = module.width - 2 * thickness
  width = module.depth
  thickness = body_thickness
  axes = length:x, width:z, thickness:y

top:
  same, origin.y = module.y + module.height - thickness
```

Back panel, surface-applied within nominal depth:

```text
length = module.height
width = module.width
thickness = back_thickness
axes = length:y, width:x, thickness:z
origin.z = module.depth - back_thickness
```

### 13.2 Shelf parts

For a bay with `shelves`:

- `count` from params.
- `adjustable` from params.
- Evenly distribute shelves in bay height for MVP.
- Shelf length = bay.width - clearance.
- Shelf width = bay.depth - optional rear/front clearances.
- Shelf thickness = shelf_thickness.

### 13.3 Shoe shelves

Treat `shoes 4` like horizontal shelves for MVP.

### 13.4 Hanging bays

For a bay with `hanging`:

- Generate a hanging rod hardware item.
- Optional shelf above later.

### 13.5 Storage bays

For a bay with `storage`, no internal parts required for MVP.

## 14. Door generation

File: `compiler/doors_generator.py`

Implement slab doors for MVP.

Input:

```yaml
doors:
  top: auto
  main: auto
  style: slab
  hinges: concealed
```

MVP behavior:

- Generate doors per module/row/column grid.
- For each opening, create one door if narrow enough.
- If opening width exceeds max single door width, split into two doors.
- Apply door gap from door system.
- Position doors slightly in front of cabinet body.

Door part:

```text
length = door_height
width = door_width
thickness = door_thickness
axes = length:z, width:x, thickness:y
origin.y = -door_thickness
```

Hinge metadata:

- Use hinge count rules from door system.
- First hinge 100 mm from top.
- Last hinge 100 mm from bottom.
- Remaining hinges evenly spaced.
- Store hinge hardware items and/or door operations.

## 15. Hardware generation

File: `compiler/hardware_generator.py`

Generate:

- Hinges for doors.
- Rods for hanging bays.
- Legs for adjustable base.
- Shelf pins later.

For MVP, hardware can be represented semantically and optionally rendered approximately.

## 16. Validation and warnings

File: `compiler/warnings.py`

Implement validations at request and resolved-model levels.

### 16.1 Fatal errors

Raise errors for:

- Invalid DSL syntax.
- Missing niche for built-in cabinet.
- Impossible negative dimensions.
- Layout fixed widths exceeding available width.
- Layout fixed heights exceeding available height.
- Unknown material/standard/system.

### 16.2 Warnings

Emit warnings for:

- Auto module split applied.
- Board length exceeds max board length.
- Door too tall.
- Slab door may warp.
- Shelf span may sag.
- Cabinet nearly equals niche with insufficient clearance.
- Cabinet depth exceeds niche depth.
- Full-height cabinet cannot be rotated upright.
- Drawer support incomplete.

Warning codes:

```text
AUTO_SPLIT_APPLIED
BOARD_TOO_LONG
DOOR_TOO_TALL
SLAB_DOOR_WARP_RISK
SHELF_SPAN_TOO_WIDE
CABINET_EXCEEDS_NICHE
INSUFFICIENT_CLEARANCE
LAYOUT_OVERFLOW
UNKNOWN_PRESET
```

## 17. Geometry and GLB export

The renderer consumes generated parts. It must not reverse-engineer parts from mesh geometry.

### 17.1 Convert part to box dimensions

File: `geometry/coordinates.py`

Implement:

```python
def part_box_size(part: Part) -> tuple[float, float, float]:
    """Return rendered box size in global X/Y/Z dimensions from part manufacturing dimensions and axes."""
```

Use `PartAxes`:

- Place `length`, `width`, `thickness` along the specified axes.

### 17.2 Mesh generation

File: `geometry/mesh.py`

Use `trimesh.creation.box`.

Implement:

```python
def box_mesh_for_part(part: Part, color: tuple[int, int, int, int]) -> trimesh.Trimesh:
    ...
```

Important:

- Mesh box should be centered at `origin + size / 2`.
- Mesh node name should use `part.id`.
- Mesh color should come from material role or finish.

### 17.3 Scene generation

File: `geometry/scene.py`

Implement:

```python
def build_scene(project: ResolvedProject) -> trimesh.Scene:
    ...
```

Generate a scene with one named mesh per part.

### 17.4 GLB export

File: `geometry/export.py`

Implement:

```python
def export_glb(project: ResolvedProject) -> bytes:
    scene = build_scene(project)
    return scene.export(file_type="glb")
```

## 18. Cut list generation

File: `outputs/cutlist.py`

Do not derive cut list from mesh. Use `Part.length`, `Part.width`, and `Part.thickness`.

Implement:

```python
class CutListItem(BaseModel):
    part_ids: list[str]
    name: str
    kind: str
    material: str
    length: float
    width: float
    thickness: float
    quantity: int
    grain_direction: str
    edge_banding: list[str]
```

Group identical parts by:

```text
kind
material
length
width
thickness
grain_direction
edge_banding
```

Output:

- JSON.
- CSV.

CSV columns:

```text
quantity,name,kind,material,length,width,thickness,grain_direction,edge_banding,part_ids
```

## 19. SVG views

Optional but recommended after GLB.

File: `outputs/svg_views.py`

Generate simple:

- Front elevation.
- Side section.

SVG is useful because it is easy to show in browser and print.

Do not use SVG as internal representation.

## 20. FastAPI backend

File: `app/main.py`

Create app and include routes.

Routes:

```text
GET  /
GET  /api/health
POST /api/parse
POST /api/compile
POST /api/render.glb
POST /api/cutlist
GET  /api/stdlib
```

### 20.1 Request/response models

```python
class DslRequest(BaseModel):
    dsl: str

class CompileResponse(BaseModel):
    normalized: dict
    project: ResolvedProject
    warnings: list[ValidationMessage]
```

### 20.2 Compile endpoint

```python
@app.post("/api/compile", response_model=CompileResponse)
def compile_endpoint(req: DslRequest) -> CompileResponse:
    normalized, project = compile_dsl(req.dsl)
    return CompileResponse(
        normalized=normalized,
        project=project,
        warnings=project.warnings,
    )
```

### 20.3 GLB endpoint

```python
@app.post("/api/render.glb")
def render_glb_endpoint(req: DslRequest):
    _, project = compile_dsl(req.dsl)
    glb = export_glb(project)
    return Response(content=glb, media_type="model/gltf-binary")
```

### 20.4 Cut list endpoint

```python
@app.post("/api/cutlist")
def cutlist_endpoint(req: DslRequest):
    _, project = compile_dsl(req.dsl)
    return generate_cutlist(project)
```

## 21. Web frontend

Use a simple static frontend.

### 21.1 UI requirements

Left panel:

- Textarea for DSL.
- Compile button.
- Render button.
- Warnings/errors panel.
- Cut list table.

Right panel:

- Three.js viewer.
- Orbit controls.
- Basic lighting.
- Grid helper.

### 21.2 `viewer.js`

Responsibilities:

- Read DSL from textarea.
- POST to `/api/compile`.
- Display warnings.
- POST to `/api/render.glb`.
- Convert returned bytes to Blob URL.
- Load GLB with Three.js GLTFLoader.
- Clear previous model.
- Add new model.
- Frame camera to model bounds.

### 21.3 Initial example DSL in UI

Use this as default text:

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

## 22. Testing plan

### 22.1 Parser tests

Test:

- Valid YAML.
- Invalid YAML.
- Empty document.
- Non-object top-level document.

### 22.2 Dimension tests

Test:

- `1200 x 2650 x 600`.
- `1200x2650x600`.
- Invalid dimensions.

### 22.3 Shorthand tests

Test:

- `use: euro_builtin_v1`.
- `material: plywood_18`.
- `space: niche 1200 x 2650 x 600`.
- `shelves 5 adjustable`.
- `hanging rod 1700`.
- `shoes 4`.

### 22.4 Stdlib tests

Test:

- Load all stdlib YAMLs.
- Selected presets exist.
- Unknown preset raises useful error.

### 22.5 Module split tests

Test:

- Cabinet shorter than board length creates one module.
- Cabinet taller than board length creates main + top module.
- 2650 niche / 2420 board / 80 base produces valid modules.

### 22.6 Layout tests

Test:

- Fixed + `*` columns resolve correctly.
- Overflow fixed columns raises error.
- Multiple `*` columns rejected in MVP.

### 22.7 Parts tests

Test:

- Left/right side panels have correct dimensions and axes.
- Top/bottom panels fit between sides.
- Back panel is generated.
- Shelves are generated and positioned.

### 22.8 Doors tests

Test:

- Main doors generated.
- Top doors generated.
- Door dimensions include gaps.
- Hinge count follows rules.

### 22.9 Cut list tests

Test:

- Identical shelves grouped.
- Cut dimensions come from part manufacturing dimensions.
- Edge banding included.

### 22.10 Geometry tests

Test:

- GLB bytes are produced.
- Each part produces one mesh.
- No mesh has zero or negative size.

### 22.11 API tests

Test:

- `/api/health`.
- `/api/compile`.
- `/api/render.glb`.
- `/api/cutlist`.

## 23. Implementation phases

### Phase 1 — Project skeleton

Deliver:

- Package structure.
- FastAPI app.
- Static frontend placeholder.
- pytest setup.
- Example DSL.

Acceptance:

- Server starts.
- `/api/health` returns OK.
- Tests run.

### Phase 2 — DSL and stdlib

Deliver:

- YAML parser.
- Dimension parser.
- Shorthand normalizer.
- Standard library loader.
- Defaults merge.

Acceptance:

- Example DSL normalizes into explicit dictionary.
- Unknown preset errors are clear.

### Phase 3 — Semantic compilation

Deliver:

- Pydantic models.
- Compile context.
- Dimension resolver.
- Module splitter.
- Basic validation.

Acceptance:

- Example DSL compiles to `ResolvedProject`.
- Auto split works.
- Warnings are generated.

### Phase 4 — Layout and parts

Deliver:

- Layout solver.
- Bay generation.
- Carcass parts.
- Shelf parts.
- Hanging rod hardware.

Acceptance:

- Parts list contains side/top/bottom/back/shelves.
- All parts have manufacturing dimensions and 3D placement.

### Phase 5 — Doors and hardware

Deliver:

- Slab door generation.
- Top/main door rows.
- Concealed hinge metadata.
- Basic leg hardware.

Acceptance:

- Door parts render in front of cabinet.
- Hinge count rules apply.

### Phase 6 — GLB rendering

Deliver:

- Part-to-box mesh conversion.
- GLB export.
- Three.js viewer.

Acceptance:

- User can paste DSL and render cabinet in browser.
- Orbit/zoom works.
- Body and doors have different colors.

### Phase 7 — Cut list

Deliver:

- Cut list JSON.
- Cut list CSV.
- Frontend cut list table.

Acceptance:

- Identical shelves are grouped.
- Cut dimensions are correct.

### Phase 8 — Polish and validation

Deliver:

- More warnings.
- Better error display.
- Better example projects.
- README instructions.

Acceptance:

- App is usable for a simple niche cabinet design.

## 24. Example end-to-end expected behavior

Input DSL:

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

Expected compilation:

- Standard: `euro_builtin_v1`.
- Material: `plywood_18`.
- Cabinet dimensions derived from niche and clearances.
- Base height: 80 mm.
- Body split into main and top modules because body height exceeds board length.
- Main module around 2250 mm high.
- Top module uses remaining height.
- Main layout has three columns.
- Left bay has adjustable shelves.
- Middle bay has hanging rod.
- Right bay has shoe shelves.
- Top module is storage.
- Slab doors are generated for main and top regions.
- Concealed hinge metadata is generated.
- GLB renders in browser.
- Cut list is generated from semantic parts.

## 25. Future extensions

After MVP, add:

- Drawer box generation.
- Drawer slide systems.
- Frame-and-panel door parts.
- Shelf-pin drilling maps.
- Hinge-cup drilling maps.
- SVG front elevation and side section.
- DXF export.
- Sheet nesting optimization.
- Cost and weight estimates.
- STEP export.
- SketchUp Ruby exporter for OpenCutList bridge.
- Interactive layout editor.
