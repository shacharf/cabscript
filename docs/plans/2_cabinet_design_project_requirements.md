# Cabinet Design Application — Project Goal and Requirements

## 1. Project goal

Build a simple cabinet-design application that lets a user describe a cabinet with a compact, human-readable DSL, then automatically generates a resolved cabinet design, a 3D web preview, and manufacturing-oriented outputs such as a cut list.

The application should be useful for DIY cabinet design

The user should provide as little information as possible. Common woodworking assumptions, dimensions, construction rules, hinge rules, material defaults, and clearances should come from a standard library.

## 2. Core design principle

The application must distinguish clearly between:

1. **User DSL** — compact user-facing description of intent.
2. **Internal semantic representation** — the source of truth.
3. **Export formats** — rendering or interoperability outputs.

Formats such as **DXF, STL, STEP, GLB/glTF, SVG, CSV, and SketchUp-related outputs are export formats only**. They must not be used as the user-defined representation or as the internal source of truth.

The internal representation should be a semantic, JSON-compatible model containing cabinet structure, modules, parts, materials, dimensions, placement, hardware, warnings, and manufacturing metadata.

## 3. Target users

Primary user:

- DIY user designing a cabinet, closet, or built-in niche cabinet.
- Wants practical design guidance and a cut list.
- May not know all cabinet-making details.
- Wants a visual preview before building.

Secondary user:

- Technical user who wants a parametric DSL and a renderer.
- May later extend the system to CNC, SketchUp, OpenCutList, or optimization workflows.

## 4. Cabinet types

The DSL and internal model should support these cabinet categories:

- Cabinet built into a niche.
- Standing cabinet.
- Kitchen base cabinet.
- Kitchen wall cabinet.
- Wardrobe / closet.

The MVP should focus on **cabinet-in-a-niche** and **standing cabinet**.

## 5. Example use case: cabinet in a niche

The application should handle built-in niche constraints such as:

- Niche width, height, and depth.
- Cabinet dimensions derived from niche dimensions.
- Side, top, and back clearances.
- Fillers / scribe panels to close irregular gaps.
- Base / legs / plinth height.
- Maximum available board length.
- Automatic module splitting when the niche is taller than available board length.

Example real constraint:

- Niche height: 2650 mm.
- Maximum board length: 2420 mm.
- Therefore the app should support a main cabinet plus a top extension/module, rather than one impossible full-height carcass.

## 6. User DSL requirements

The DSL should be compact and readable. YAML is preferred because it is human-readable, widely supported, and easy to parse safely.

Example desired style:

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

The DSL should allow both compact and explicit forms. Compact forms should be normalized into an explicit schema before compilation.

## 7. Standard library requirements

The standard library should define reusable presets and defaults, including:

### 7.1 Cabinet standards

Examples:

- `euro_builtin_v1`
- `standing_frameless_v1`
- `kitchen_base_v1`

Each standard may define:

- Construction style.
- Carcass rules.
- Default clearances.
- Filler rules.
- Door gap rules.
- Default back panel method.
- Default base/plinth method.
- Default module split policy.

### 7.2 Materials

Examples:

- `plywood_18`
- `mdf_18`
- `melamine_18`

Each material should define:

- Body panel thickness.
- Shelf thickness.
- Door thickness.
- Back panel thickness.
- Maximum board length and width.
- Optional density.
- Optional default finish.

### 7.3 Door systems

Examples:

- Concealed full-overlay hinges.
- Concealed half-overlay hinges.
- Inset doors.

Door system defaults should include:

- Door gaps.
- Overlay/inset rules.
- Hinge type.
- Hinge cup diameter and depth.
- Hinge count rules by door height.
- Hinge position rules.

### 7.4 Door styles

Examples:

- Slab door.
- Frame-and-panel light door.
- Shaker-style door.

Frame-and-panel style should support parameters such as:

- Frame width.
- Frame thickness.
- Panel thickness.
- Groove depth.
- Middle rail rules for tall doors.

### 7.5 Shelf systems

Examples:

- Shelf pins with 32 mm system.
- Cleats.
- Fixed shelves with screws.

### 7.6 Base systems

Examples:

- Adjustable legs with recessed plinth.
- Plinth box.
- Side panels to floor.
- Wall-mounted cabinet.

## 8. Internal semantic representation

The internal representation is the source of truth. It should be JSON-compatible and typed with Python models.

It should contain:

- Project metadata.
- Units.
- Selected standard library presets.
- Space/niche information.
- Cabinet dimensions.
- Modules.
- Bays/layout regions.
- Parts.
- Doors.
- Shelves.
- Hardware.
- Operations/drilling metadata.
- Edge banding metadata.
- Materials.
- Warnings and validation messages.

The most important internal entity is a **Part**, not a mesh.

A part should represent a physical board or manufactured item with:

- ID.
- Name.
- Kind.
- Material.
- Manufacturing dimensions: length, width, thickness.
- 3D placement.
- Orientation axes.
- Grain direction.
- Edge banding.
- Operations such as holes, grooves, rabbets, dados, or hinge cups.

Rendered meshes should be generated from parts. Meshes are not the source of truth.

## 9. Export formats

Export formats are generated from the internal semantic model.

### 9.1 GLB / glTF

Use GLB/glTF for web-based 3D rendering.

Purpose:

- Browser rendering.
- Interactive inspection.
- Part highlighting.
- Sharing a visual model.

GLB/glTF should not be the internal model.

### 9.2 CSV / JSON cut list

Use CSV and JSON for cut lists.

Purpose:

- Saw-shop cutting.
- Spreadsheet review.
- Debugging.
- Material estimates.

### 9.3 SVG

Use SVG for simple 2D outputs.

Purpose:

- Front elevation.
- Side section.
- Browser-native diagrams.
- Printable drawings.

### 9.4 DXF

Use DXF later for CAD/CNC workflows.

Purpose:

- Part outlines.
- Drilling maps.
- CNC profiles.
- Sheet layouts.

DXF should not be the internal model.

### 9.5 STEP

STEP may be added later for CAD interoperability.

Purpose:

- Import into CAD tools.
- Solid model exchange.

Not required for MVP.

### 9.6 STL

STL should generally be avoided for this project.

Reason:

- STL is triangle mesh only.
- It loses woodworking semantics such as material, part identity, grain, edge banding, and hardware.

### 9.7 SketchUp / OpenCutList bridge

OpenCutList works inside SketchUp and analyzes SketchUp components. It is not primarily an external DXF/STL/STEP consumer.

A future bridge could export a SketchUp Ruby script that creates a SketchUp model with one component per board. OpenCutList could then analyze those components.

This is optional and should not be part of the MVP core.

## 10. Rendering requirements

Rendering should be web-based.

Recommended rendering path:

- Backend generates GLB from the semantic parts model.
- Frontend uses an off-the-shelf web renderer, preferably Three.js.
- The 3D viewer loads GLB using GLTFLoader.
- User can orbit, pan, zoom, and inspect the model.

The renderer should support:

- Different colors/materials for body, shelves, doors, and back panel.
- Named parts, allowing future part selection/highlighting.
- Basic lighting and camera controls.
- Re-rendering after DSL changes.

## 11. Outputs required for MVP

The MVP should produce:

1. Normalized DSL / explicit project model.
2. Resolved semantic cabinet model.
3. Validation warnings/errors.
4. Web-based 3D preview.
5. Cut list.
6. Basic hardware list.
7. Door list.
8. Basic front elevation or SVG view, if time permits.

## 12. Validation requirements

The application should produce helpful warnings and errors.

Examples:

- Board exceeds maximum board length.
- Cabinet too large for niche.
- Cabinet height requires module split.
- Door is too tall and may warp.
- Slab door exceeds recommended height.
- Shelf span may sag.
- Drawer definition incomplete.
- Cabinet depth exceeds niche depth.
- No valid remaining width for `*` column.
- Layout rows or columns exceed available space.
- Full-height cabinet cannot be rotated upright in available room height.

Warnings should be non-fatal when possible. Fatal errors should be reserved for impossible geometry or invalid DSL.

## 13. MVP scope

The MVP should support:

- YAML DSL input.
- Standard library defaults.
- Built-in niche cabinet.
- Standing cabinet.
- Frameless Euro-style carcass.
- Auto module splitting.
- Main module plus top module.
- Shelves.
- Hanging bays.
- Shoe shelves.
- Basic storage bays.
- Slab doors.
- Concealed hinge metadata.
- Adjustable legs / base height.
- Back panel.
- GLB rendering.
- Cut list.
- Basic validation.

## 14. Out of scope for MVP

Do not implement in the first version:

- Full drag-and-drop UI.
- CNC toolpaths.
- Real nesting optimization.
- STEP export.
- Direct SKP export.
- Photorealistic rendering.
- Advanced joinery.
- Drawer box engineering.
- Parametric curved/angled geometry.
- Full OpenCutList integration.
- Cost estimation.
- Structural engineering-grade sag calculation.

## 15. Long-term extensions

Possible future features:

- Interactive layout editor.
- DXF export.
- SVG/PDF assembly drawings.
- Drilling maps.
- Shelf-pin hole maps.
- Hinge drilling maps.
- Drawer slide systems.
- Frame-and-panel door generator.
- Sheet nesting optimization.
- Cost estimation.
- Weight estimation.
- OpenCutList bridge via SketchUp Ruby script.
- STEP export.
- AR preview.
- Design recommendation engine.
