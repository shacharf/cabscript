# Cabinet DSL Reference

The cabinet DSL is a compact YAML format that describes a cabinet design. It is the sole source of truth — all outputs (3D model, cut list, BOM) are derived from it.

Shorthand forms are normalized to their explicit equivalents before compilation. Both forms are valid input.

---

## Canonical example

```yaml
# Select a construction standard and material.
use: euro_builtin_v1        # shorthand for `use: { standard: euro_builtin_v1 }`
material: plywood_18        # shorthand for `use: { material: plywood_18 }`

# Describe the installation space (built_in cabinet — niche defines dimensions).
space: niche 1200 x 2650 x 600   # shorthand: "niche W x H x D" (mm)

# Cabinet configuration with explicit named modules.
cabinet:
  type: built_in
  base: legs 80             # shorthand: "legs <height>" | "plinth <height>"
  modules:
    - id: lower
      height: 1000
    - id: upper
      height: "*"           # takes remaining body height

# Interior layout — each key matches a module id.
layout:
  lower:
    columns:
      400: shelves 4        # fixed width (mm): bay function shorthand
      "*": hanging rod 900  # "*" = take remaining width
  upper: shelves 2 adjustable   # shorthand: single full-width bay

# Door configuration — each key matches a module id or is a style option.
doors:
  lower: auto               # auto | none
  upper: auto
  style: slab               # slab | frame_panel_light
  hinges: concealed         # concealed (only supported value for MVP)

# Finish colours (mapped via stdlib/colors.yaml to RGBA for GLB rendering).
finish:
  body: warm_white
  doors: oak
  shelves: warm_white       # optional; falls back to body if omitted
  back: warm_white          # optional; falls back to body if omitted
```

---

## Block reference

### `use`

Selects the construction standard and/or material from the standard library.

| Field      | Type   | Default | Description                                      |
|------------|--------|---------|--------------------------------------------------|
| `standard` | string | —       | Standard library key, e.g. `euro_builtin_v1`     |
| `material` | string | —       | Material library key, e.g. `plywood_18`          |

**Shorthand forms**

```yaml
use: euro_builtin_v1
# expands to:
use:
  standard: euro_builtin_v1
```

```yaml
material: plywood_18
# expands to:
use:
  material: plywood_18
```

---

### `space`

Describes the installation envelope. Required for `built_in` cabinets; omitted for standalone types (use `cabinet.width/height/depth` instead).

| Field          | Type              | Description        |
|----------------|-------------------|--------------------|
| `kind`         | `niche` \| `free` | `niche` = fixed opening; `free` = standalone |
| `niche.width`  | mm                | Opening width      |
| `niche.height` | mm                | Opening height     |
| `niche.depth`  | mm                | Opening depth      |

Cabinet body dimensions are derived from the niche by subtracting construction clearances defined in the selected standard.

**Shorthand form**

```yaml
space: niche 1200 x 2650 x 600
# expands to:
space:
  kind: niche
  niche:
    width: 1200
    height: 2650
    depth: 600
```

Dimension string formats accepted: `1200 x 2650 x 600`, `1200x2650x600`, `1200 X 2650 X 600`.

---

### `cabinet`

Controls cabinet type, dimensions, module definition, and base.

| Field     | Type                                                      | Default  | Description                          |
|-----------|-----------------------------------------------------------|----------|--------------------------------------|
| `type`    | `built_in` \| `standing` \| `kitchen_base` \| `kitchen_wall` \| `wardrobe` | — | Cabinet category |
| `width`   | mm                                                        | 600      | Explicit width — used when `type` is not `built_in` |
| `height`  | mm                                                        | 2000     | Explicit height — used when `type` is not `built_in` |
| `depth`   | mm                                                        | standard default | Explicit depth — used when `type` is not `built_in` |
| `split`   | `auto` \| `none` \| list of mm                            | `auto`   | Module split strategy (ignored when `modules` is present) |
| `base`    | string \| null                                            | null     | Base system shorthand or null        |
| `modules` | list of `{id, height}` objects                            | —        | Named module list (takes priority over `split`) |

**`base` shorthand forms**

```yaml
base: legs 80       # adjustable legs, 80 mm height
base: plinth 100    # plinth box, 100 mm height
```

**Standalone cabinet dimensions**

For cabinet types other than `built_in`, specify explicit dimensions instead of a `space` niche:

```yaml
cabinet:
  type: standing
  width: 800
  height: 1800
  depth: 400
```

Omitted dimensions fall back to defaults: `width=600`, `height=2000`, `depth` from standard.

**Named modules**

The recommended way to define modules. Each entry has a unique `id` (used as the key in `layout` and `doors`) and a `height` in mm. Exactly one module may use `"*"` to take the remaining body height.

```yaml
cabinet:
  modules:
    - id: lower
      height: 900
    - id: upper
      height: "*"
```

Modules stack bottom-to-top in the order listed.

**Auto-split (legacy)**

When `modules` is absent, `split: auto` applies the standard's `module_split` rules:
- If body height ≤ max board length − margin → one module (`id: mod_main`).
- Otherwise → main module (`id: mod_main`, up to `default_main_height`) + top module (`id: mod_top`, remainder).

`split: none` forces a single `mod_main` module regardless of height.

A list of mm values sets explicit split heights, e.g. `split: [2250]` → `mod_0` at 0–2250, `mod_1` at 2250–body_height.

---

### `layout`

Maps module ids to a row/column grid of bays. Each key must match a module id from `cabinet.modules` (or `mod_main` / `mod_top` for auto-split).

**Single-bay shorthand**

```yaml
layout:
  upper: shelves 2 adjustable
# expands to a single full-width, full-height bay with that function
```

**Multi-column shorthand**

```yaml
layout:
  lower:
    columns:
      400: shelves 5 adjustable   # fixed width (mm): bay function
      500: hanging rod 1700
      "*": shoes 4                # "*" = take remaining width
```

Columns are resolved left to right. Only one `"*"` column per row is supported.

**Row/column grid (explicit)**

```yaml
layout:
  lower:
    rows:
      - height: "*"
        columns:
          - width: 400
            function: { kind: shelves, params: { count: 5, adjustable: true } }
          - width: 500
            function: { kind: hanging, params: { rod_height: 1700 } }
          - width: "*"
            function: { kind: shoes, params: { rows: 4 } }
```

**Shelf merging across columns**

When multiple adjacent columns in the same row both have `shelves` or `shoes` functions **with the same count**, shelves are generated as a single full-width part spanning all columns. The vertical divider between the columns acts as a shelf support. For rows where only one column has shelves, the shelf spans that column only.

Columns with *different* shelf counts are not merged — each count group generates its own shelf set spanning only the columns that share that count.

**Bay functions**

| Shorthand                  | Kind       | Params                                      |
|----------------------------|------------|---------------------------------------------|
| `shelves 5`                | `shelves`  | `count: 5`                                  |
| `shelves 5 adjustable`     | `shelves`  | `count: 5, adjustable: true`                |
| `hanging`                  | `hanging`  | —                                           |
| `hanging rod 1700`         | `hanging`  | `rod_height: 1700`                          |
| `shoes 4`                  | `shoes`    | `rows: 4`                                   |
| `storage`                  | `storage`  | —                                           |
| `empty`                    | `empty`    | —                                           |
| `hooks`                    | `hooks`    | —                                           |
| `drawers`                  | `drawers`  | —                                           |
| `drawers 4`                | `drawers`  | `count: 4`                                  |
| `drawers no_front`         | `drawers_no_front` | —                                   |
| `drawers 4 no_front`       | `drawers_no_front` | `count: 4`                          |

---

### `doors`

Controls door generation per module region, plus global style options.

| Field     | Type                     | Default | Description                                        |
|-----------|--------------------------|---------|----------------------------------------------------|
| `<mod-id>`| `auto` \| `none`         | `none`  | Door coverage for that module                      |
| `style`   | string                   | standard default | Door style key, e.g. `slab`, `frame_panel_light` |
| `hinges`  | `concealed`              | standard default | Hinge system (only `concealed` for MVP)          |

`auto` generates one door covering the full module width. If the opening exceeds the maximum single-door width, it is split into two doors side by side.

```yaml
doors:
  lower: auto
  upper: none
  style: slab
```

**Spanning a single door across multiple modules**

Use `span` with a list of module IDs to generate one door (or pair) covering their combined height:

```yaml
doors:
  span: [drawers_unit_bottom, drawers_unit_top, hanging]
  style: slab
  hinges: concealed
```

Modules listed in `span` are excluded from per-module door generation. For multiple independent span groups, use a list of lists:

```yaml
doors:
  span:
    - [lower_left, upper_left]
    - [lower_right, upper_right]
  style: slab
```

---

### `finish`

Maps part roles to finish names. Finish names are resolved via `stdlib/colors.yaml` to RGBA values for GLB rendering.

| Field     | Type   | Default        | Description                          |
|-----------|--------|----------------|--------------------------------------|
| `body`    | string | —              | Carcass panels and shelves           |
| `doors`   | string | —              | Door faces                           |
| `shelves` | string | same as `body` | Shelf panels (optional override)     |
| `back`    | string | same as `body` | Back panel (optional override)       |

---

## Dimension strings

Anywhere a 3D dimension is expected as a string, the format is:

```
W x H x D
```

- Values are in millimetres (integers or decimals).
- The separator is `x` or `X`, optionally surrounded by spaces.

---

## Standard library keys

Standard library entries are defined in `src/cabinetry/stdlib/`. The keys below are available out of the box.

| Category      | Key                      | File                  |
|---------------|--------------------------|-----------------------|
| Standard       | `euro_builtin_v1`        | `standards.yaml`      |
| Material       | `plywood_18`             | `materials.yaml`      |
| Material       | `mdf_18`                 | `materials.yaml`      |
| Door system    | `concealed_full_overlay` | `door_systems.yaml`   |
| Door style     | `slab`                   | `door_styles.yaml`    |
| Door style     | `frame_panel_light`      | `door_styles.yaml`    |
| Shelf system   | `shelf_pins_32`          | `shelf_systems.yaml`  |
| Shelf system   | `cleats_basic`           | `shelf_systems.yaml`  |
| Base system    | `adjustable_legs_80`     | `base_systems.yaml`   |
| Finish colour  | `warm_white`             | `colors.yaml`         |
| Finish colour  | `oak`                    | `colors.yaml`         |
| Finish colour  | `white`                  | `colors.yaml`         |
| Finish colour  | `anthracite`             | `colors.yaml`         |
