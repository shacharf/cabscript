# UI
- pan / zoom the 2d view: wheel to zoom around cursor, left-drag to pan, double-click to reset
- resize sections: editor, properties, view — drag handles between columns; widths saved to localStorage

# DSL editor
- context aware autocomplete
  Monaco CompletionItemProvider registered via beforeMount. Stdlib fetched from /api/stdlib (cached
  in useStore.stdlib); provider reads it via a ref so it's always current. Line-based context:
  current line `key: ` pattern + upward scan for unindented parent key. Suggestions:
    - at column 0: top-level keys (use, material, space, cabinet, layout, doors, finish)
    - use: → stdlib.standards
    - material: → stdlib.materials
    - finish.*: → stdlib.colors keys
    - layout.*: → drawers N, shelves N, hanging rod N, storage N, shoes N, open
    - doors.*: → none, auto, single, pair, folding; style → slab, frame_panel_light; hinges → concealed
    - cabinet.type: → built_in, standing, kitchen_base, kitchen_wall, wardrobe
    - cabinet.base: → legs 80, legs 100, plinth 100

# Visualization
- display drawers: horizontal divider lines + handle indicators within drawer bays in 2D view,
  driven by bay.function.params.count — no backend changes needed
- toggle dimensions (button in viewer toolbar): show/hide per-bay height labels on right edge of
  cabinet; for drawer bays shows per-drawer height (heightMM × count)

# Cabinet definition / Properties panel
- Bay function editing: when a drawer bay is selected the Properties panel shows an editable count
  field; changes rewrite `  moduleId: drawers N` in the DSL layout section via regex (same pattern
  as GlobalProperties niche editing). Other bay types and parts remain read-only.
