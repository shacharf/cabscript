import { create } from 'zustand';
import type {
  ResolvedProject,
  ValidationMessage,
  CutlistItem,
  StdLibData,
} from '../types/cabinet';
import { apiCompile, apiRenderGlb, apiCutlist, apiStdlib, ApiError } from '../api/client';

export const DEFAULT_DSL = `use: euro_builtin_v1
material: plywood_18

space: niche 1200 x 2650 x 600

cabinet:
  type: built_in
  base: legs 80
  modules:
    - id: drawers_unit
      height: 800
    - id: hanging
      height: 1000
    - id: top_shelf
      height: "*"

layout:
  drawers_unit: drawers 3
  hanging: hanging rod 900
  top_shelf: shelves 1 adjustable

doors:
  drawers_unit: none
  hanging: auto
  top_shelf: auto
  style: slab
  hinges: concealed

finish:
  body: warm_white
  doors: oak
`;

interface CabinetStore {
  fileName: string | null;
  dslText: string;
  isDirty: boolean;

  project: ResolvedProject | null;
  warnings: ValidationMessage[];
  cutlist: CutlistItem[];
  compileStatus: 'idle' | 'compiling' | 'ok' | 'error';
  compileError: string | null;

  activeView: '2d' | '3d';
  doorsVisible: boolean;
  glbBlobUrl: string | null;

  selectedBayId: string | null;
  selectedPartId: string | null;

  stdlib: StdLibData | null;

  setDslText: (text: string) => void;
  setActiveView: (v: '2d' | '3d') => void;
  toggleDoors: () => void;
  selectBay: (id: string | null) => void;
  selectPart: (id: string | null) => void;
  loadFile: (name: string, text: string) => void;
  newProject: () => void;

  compile: () => Promise<void>;
  render3d: () => Promise<void>;
  loadStdlib: () => Promise<void>;
}

export const useStore = create<CabinetStore>((set, get) => ({
  fileName: null,
  dslText: DEFAULT_DSL,
  isDirty: false,

  project: null,
  warnings: [],
  cutlist: [],
  compileStatus: 'idle',
  compileError: null,

  activeView: '2d',
  doorsVisible: true,
  glbBlobUrl: null,

  selectedBayId: null,
  selectedPartId: null,

  stdlib: null,

  setDslText: (text) => set({ dslText: text, isDirty: true }),

  setActiveView: (v) => set({ activeView: v }),

  toggleDoors: () => set((s) => ({ doorsVisible: !s.doorsVisible })),

  selectBay: (id) => set({ selectedBayId: id, selectedPartId: null }),

  selectPart: (id) => set({ selectedPartId: id, selectedBayId: null }),

  loadFile: (name, text) =>
    set({
      fileName: name,
      dslText: text,
      isDirty: false,
      project: null,
      warnings: [],
      cutlist: [],
      compileStatus: 'idle',
      compileError: null,
      selectedBayId: null,
      selectedPartId: null,
    }),

  newProject: () =>
    set({
      fileName: 'untitled.yaml',
      dslText: DEFAULT_DSL,
      isDirty: false,
      project: null,
      warnings: [],
      cutlist: [],
      compileStatus: 'idle',
      compileError: null,
      selectedBayId: null,
      selectedPartId: null,
    }),

  compile: async () => {
    set({ compileStatus: 'compiling', compileError: null });
    try {
      const data = await apiCompile(get().dslText);
      set({
        project: data.project,
        warnings: data.warnings,
        compileStatus: 'ok',
        compileError: null,
      });
      // Also fetch cut list non-blocking
      apiCutlist(get().dslText)
        .then((r) => set({ cutlist: r.items }))
        .catch(() => undefined);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : String(e);
      set({
        compileStatus: 'error',
        compileError: msg,
        warnings: [{ severity: 'error', code: 'COMPILE_ERROR', message: msg, path: null }],
      });
    }
  },

  render3d: async () => {
    try {
      const buf = await apiRenderGlb(get().dslText);
      const prev = get().glbBlobUrl;
      if (prev) URL.revokeObjectURL(prev);
      const url = URL.createObjectURL(new Blob([buf], { type: 'model/gltf-binary' }));
      set({ glbBlobUrl: url });
    } catch (_) {
      // Non-fatal; 3D viewer will show previous or empty state
    }
  },

  loadStdlib: async () => {
    try {
      const data = await apiStdlib();
      set({ stdlib: data });
    } catch (_) {
      // Non-fatal fallback
      set({
        stdlib: {
          standards: ['euro_builtin_v1'],
          materials: ['plywood_18', 'mdf_18'],
          colors: {},
        },
      });
    }
  },
}));
