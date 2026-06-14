export type Mm = number;
export type AxisName = 'x' | 'y' | 'z';

export interface Vec3 {
  x: Mm;
  y: Mm;
  z: Mm;
}

export interface PartAxes {
  length_axis: AxisName;
  width_axis: AxisName;
  thickness_axis: AxisName;
}

export type BayFunctionKind =
  | 'shelves'
  | 'hanging'
  | 'drawers'
  | 'shoes'
  | 'storage'
  | 'hooks'
  | 'empty';

export interface BayFunction {
  kind: BayFunctionKind;
  params: Record<string, unknown>;
}

export interface ResolvedModule {
  id: string;
  name: string;
  x: Mm;
  y: Mm;
  z: Mm;
  width: Mm;
  depth: Mm;
  height: Mm;
}

export interface ResolvedBay {
  id: string;
  module_id: string;
  row_index: number;
  col_index: number;
  x: Mm;
  y: Mm;
  z: Mm;
  width: Mm;
  depth: Mm;
  height: Mm;
  function: BayFunction;
}

export type PartKind =
  | 'side_panel'
  | 'top_panel'
  | 'bottom_panel'
  | 'shelf'
  | 'divider'
  | 'back_panel'
  | 'door'
  | 'drawer_front'
  | 'filler'
  | 'plinth'
  | 'rail'
  | 'cleat';

export interface Part {
  id: string;
  name: string;
  kind: PartKind;
  module_id: string | null;
  material: string;
  length: Mm;
  width: Mm;
  thickness: Mm;
  origin: Vec3;
  axes: PartAxes;
  grain_direction: 'length' | 'width' | 'none';
  edge_banding: string[];
  operations: unknown[];
}

export interface HardwareItem {
  id: string;
  kind: string;
  name: string;
  position: Vec3 | null;
  params: Record<string, unknown>;
}

export type Severity = 'info' | 'warning' | 'error';

export interface ValidationMessage {
  severity: Severity;
  code: string;
  message: string;
  path: string | null;
}

export interface ResolvedProject {
  units: string;
  standard: string;
  material: string;
  width: Mm;
  height: Mm;
  depth: Mm;
  modules: ResolvedModule[];
  bays: ResolvedBay[];
  parts: Part[];
  hardware: HardwareItem[];
  warnings: ValidationMessage[];
}

export interface CompileResponse {
  normalized: Record<string, unknown>;
  project: ResolvedProject;
  warnings: ValidationMessage[];
}

export interface CutlistItem {
  part_ids: string[];
  name: string;
  kind: string;
  material: string;
  length: Mm;
  width: Mm;
  thickness: Mm;
  quantity: number;
  grain_direction: string;
  edge_banding: string[];
}

export interface ColorEntry {
  rgba: [number, number, number, number];
  description: string;
}

export interface StdLibData {
  standards: string[];
  materials: string[];
  colors: Record<string, ColorEntry>;
}
