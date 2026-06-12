## Main screen

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ BoardScript       File  Edit  View  Insert  Standards  Export  Help                         │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ [Compile ✓] [Undo] [Redo] [2D Front] [2D Side] [3D] [Cut List] [Manufacturing] [Warnings: 2] │
├───────────────────────┬─────────────────────────────────────────────┬────────────────────────┤
│ NAVIGATOR             │ CANVAS                                      │ PROPERTIES             │
│                       │                                             │                        │
│ Project               │  Tabs: [Front] [Side] [Top] [3D]             │ Selected object         │
│ ├─ Space / niche       │                                             │                        │
│ ├─ Cabinet             │     front elevation                         │ ID: main.left.shelf_03  │
│ │  ├─ Main module      │                                             │ Kind: shelf             │
│ │  │  ├─ Left bay      │     ┌───────────────────────────────┐       │                        │
│ │  │  ├─ Hanging bay   │     │           top doors            │       │ Geometry               │
│ │  │  └─ Shoe bay      │     ├─────────┬──────────┬──────────┤       │ X: auto                │
│ │  └─ Top module       │     │         │          │          │       │ Z: 1420                │
│ ├─ Doors               │     │ shelves │ hanging  │ shoes    │       │ Width: auto            │
│ ├─ Materials           │     │         │          │          │       │ Depth: 560             │
│ └─ Warnings            │     │ ─────── │          │ ───────  │       │ Thickness: 18          │
│                       │     │ ─────── │   rod    │ ───────  │       │                        │
│ SCRIPT                │     │ ─────── │          │ ───────  │       │ Rules                  │
│ ┌───────────────────┐ │     └─────────┴──────────┴──────────┘       │ Support: shelf-pins    │
│ │ YAML editor        │ │                                             │ Adjustable: true       │
│ │ with line numbers  │ │     Dimensions overlay: [on/off]            │ Edge banding: front    │
│ │ and diagnostics    │ │     Snap/grid: 32 mm                        │                        │
│ └───────────────────┘ │                                             │ [Apply] [Reset]        │
├───────────────────────┴─────────────────────────────────────────────┴────────────────────────┤
│ INSPECTOR TABLES                                                                              │
│ [Warnings] [Cut List] [Door List] [Hardware] [Sheet Usage] [Operations]                       │
│                                                                                               │
│ Part             Material      L      W      T     Qty   Edges    Warning                    │
│ shelf_01         plywood_18    382    560    18    5     front    -                          │
│ left_side        plywood_18    2250   580    18    1     front    -                          │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```