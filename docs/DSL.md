# Cabinet DSL Reference

The cabinet DSL is a compact YAML format that describes a cabinet design. It is the sole source of truth — all outputs (3D model, cut list, BOM) are derived from it.

Shorthand forms are normalized to their explicit equivalents before compilation. Both forms are valid input.

---

## Canonical example

```yaml
# Select a construction standard and material.
use: euro_builtin_v1        # shorthand for `use: { standard: euro_builtin_v1 }`
material: plywood_18        # shorthand for `use: { material: plywood_18 }`

# Describe the installation space.
space: niche 1200 x 2650 x 600   # shorthand: "niche W x H x D" (mm)

# Cabinet configuration.
cabinet:
  type: built_in            # built_in | standing | kitchen_base | kitchen_wall | wardrobe
  split: auto               # auto | none | [list of explicit heights in mm]
  base: legs 80             # shorthand: "legs <height>" | "plinth <height>"

# Interior layout — one or more named regions mapped to a row/column grid.
layout:
  top: storage 380          # shorthand: single-bay region with function and fixed height (mm)
  main:
    columns:
      400: shelves 5 adjustable   # fixed width (mm): bay function
      500: hanging rod 1700
      "*": shoes 4                # "*" = take remaining width

# Door configuration.
doors:
  top: auto                 # auto | none
  main: auto
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

| Field      | Type   | Default            | Description                              |
|------------|--------|--------------------|------------------------------------------|
| `standard` | string | —                  | Standard library key, e.g. `euro_builtin_v1` |
| `material` | string | —                  | Material library key, e.g. `plywood_18`  |

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

Describes the installation envelope.

| Field  | Type                  | Description                                 |
|--------|-----------------------|---------------------------------------------|
| `kind` | `niche` \| `free`     | `niche` = fixed opening; `free` = standalone |
| `niche.width`  | mm            | Opening width                               |
| `niche.height` | mm            | Opening height                              |
| `niche.depth`  | mm            | Opening depth                               |

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

Controls cabinet type, module splitting, and base.

| Field   | Type                                       | Default  | Description                                         |
|---------|--------------------------------------------|----------|-----------------------------------------------------|
| `type`  | `built_in` \| `standing` \| `kitchen_base` \| `kitchen_wall` \| `wardrobe` | — | Cabinet category |
| `split` | `auto` \| `none` \| list of mm             | `auto`   | Module split strategy (see §Module splitting below) |
| `base`  | string \| null                             | null     | Base system shorthand or null                       |

**`base` shorthand forms**

```yaml
base: legs 80       # adjustable legs, 80 mm height
base: plinth 100    # plinth box, 100 mm height
```

**Module splitting**

`auto` applies the standard's `module_split` rules:
- If body height ≤ max board length − margin → one module.
- Otherwise → main module (up to `default_main_height`) + top module (remainder).

`none` forces a single module regardless of height.

A list of mm values sets explicit split heights from the bottom, e.g. `[2250]` → main at 0–2250, top at 2250–body_height.

---

### `layout`

Maps named regions to a row/column grid of bays. Region names (`main`, `top`) correspond to modules produced by the module splitter.

**Region shorthand (single-bay)**

```yaml
layout:
  top: storage 380
# expands to:
layout:
  top:
    rows:
      - height: 380
        columns:
          - width: "*"
            function: { kind: storage }
```

**Multi-column region**

```yaml
layout:
  main:
    columns:
      400: shelves 5 adjustable
      500: hanging rod 1700
      "*": shoes 4
```

Columns are resolved left to right. `"*"` takes the remaining inner width after fixed columns. Only one `"*"` column per row is supported.

**Row/column grid (explicit)**

```yaml
layout:
  main:
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

---

### `doors`

Controls door generation per region.

| Field    | Type                     | Default | Description                                   |
|----------|--------------------------|---------|-----------------------------------------------|
| `top`    | `auto` \| `none`         | `none`  | Door coverage for the top module region        |
| `main`   | `auto` \| `none`         | `auto`  | Door coverage for the main module region       |
| `style`  | string                   | standard default | Door style key, e.g. `slab`, `frame_panel_light` |
| `hinges` | `concealed`              | standard default | Hinge system (only `concealed` for MVP)       |

`auto` generates one door per column per row. If an opening exceeds the maximum single-door width, it is split into two doors.

---

### `finish`

Maps part roles to finish names. Finish names are resolved via `stdlib/colors.yaml` to RGBA values for GLB rendering.

| Field     | Type   | Default       | Description                         |
|-----------|--------|---------------|-------------------------------------|
| `body`    | string | —             | Carcass panels and shelves           |
| `doors`   | string | —             | Door faces                          |
| `shelves` | string | same as `body` | Shelf panels (optional override)    |
| `back`    | string | same as `body` | Back panel (optional override)      |

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

| Category       | Key                      | File                  |
|----------------|--------------------------|-----------------------|
| Standard        | `euro_builtin_v1`        | `standards.yaml`      |
| Material        | `plywood_18`             | `materials.yaml`      |
| Material        | `mdf_18`                 | `materials.yaml`      |
| Door system     | `concealed_full_overlay` | `door_systems.yaml`   |
| Door style      | `slab`                   | `door_styles.yaml`    |
| Door style      | `frame_panel_light`      | `door_styles.yaml`    |
| Shelf system    | `shelf_pins_32`          | `shelf_systems.yaml`  |
| Shelf system    | `cleats_basic`           | `shelf_systems.yaml`  |
| Base system     | `adjustable_legs_80`     | `base_systems.yaml`   |
| Finish colour   | `warm_white`             | `colors.yaml`         |
| Finish colour   | `oak`                    | `colors.yaml`         |
| Finish colour   | `white`                  | `colors.yaml`         |
| Finish colour   | `anthracite`             | `colors.yaml`         |
