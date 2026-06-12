# North Star

## Vision

A semantic cabinet design tool that lets anyone describe a cabinet in plain YAML and receive a complete, manufacturable design — resolved dimensions, 3D preview, cut list, and hardware list — without needing to know cabinet-making conventions in advance. The system encodes woodworking knowledge in a standard library so the user provides intent, not engineering.

Long-term, this becomes a parametric design platform where a short human-readable spec compiles to a fully resolved parts model that can feed any downstream workflow: a saw shop, a CNC machine, a SketchUp model, or a material optimizer.

## Target Users

**Primary — DIY builder:** Designing a built-in niche cabinet, closet, or kitchen cabinet. Wants to see what it will look like and get a cut list before buying materials. Does not know hinge rules, clearances, or module-split constraints. Success means a correct cut list and a 3D preview they trust.

**Secondary — Technical user:** Wants a parametric DSL and exportable semantic model they can pipe into CNC, OpenCutList, or custom tooling. Success means a clean, typed internal model with no information loss between DSL and export.

## Principles

- **DSL describes intent; the system resolves details.** Users should never have to specify things the standard library already knows (hinge count, clearances, module splits, grain direction).
- **Three layers, no blurring.** User DSL → internal semantic model → export formats. Exports are never the source of truth.
- **Parts, not meshes.** The fundamental unit is a physical board with manufacturing metadata. Geometry is derived from parts, not the other way around.
- **Warn, don't block.** Validation errors should be non-fatal when possible. The system should tell the user what is wrong and why, not silently produce a bad design.
- **Standard library is the product.** The quality of defaults, presets, and woodworking rules determines whether the tool is useful. A correct standard library beats a richer UI.
- **Compact input, explicit internals.** Shorthand DSL forms are normalized to a full explicit schema before any computation. No ambiguity survives past the normalization step.

## Long-Term Capabilities

### Semantic Cabinet Compiler

A compiler that takes a YAML DSL, resolves all defaults from a versioned standard library, and produces a fully typed internal model: every part with dimensions, placement, grain, edge banding, and operations; every door with hinge positions; every shelf with support method; every module boundary with split rationale. The model is the authoritative artifact — all other outputs derive from it.

### Rich Export Ecosystem

From the semantic model, generate any downstream format without loss: cut list (CSV/JSON), 3D viewer (GLB/Three.js), front elevation (SVG), drilling maps, DXF part outlines for CNC, and a SketchUp Ruby bridge for OpenCutList integration. Each export is a view of the same model, not a separate design.

### Interactive Design Environment

A web UI where the YAML DSL and the 3D preview are live-linked. Editing the spec re-renders the model in real time. Parts can be selected and inspected. Validation warnings appear inline. Long-term: a visual layout editor that writes back to the DSL, and an AR preview for in-situ visualization.

## Non-Goals

- This project does not optimize for photorealistic rendering. Accuracy of geometry and part metadata matters; visual fidelity does not.
- This project does not perform structural engineering. Sag warnings are heuristic, not load-calculated.
- This project does not manage purchasing, cost estimation, or supplier integration.
- This project does not target professional cabinet shops or frame-construction workflows. The focus is frameless Euro-style construction for DIY builders.
- This project does not replace a general-purpose CAD tool. It is purpose-built for cabinets and should stay narrow.
