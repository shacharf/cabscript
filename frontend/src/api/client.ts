import type { CompileResponse, CutlistItem, StdLibData } from '../types/cabinet';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const resp = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new ApiError(resp.status, (err as { detail?: string }).detail ?? JSON.stringify(err));
  }
  return resp.json() as Promise<T>;
}

export async function apiCompile(dsl: string): Promise<CompileResponse> {
  return post<CompileResponse>('/api/compile', { dsl });
}

export async function apiRenderGlb(dsl: string): Promise<ArrayBuffer> {
  const resp = await fetch('/api/render.glb', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dsl }),
  });
  if (!resp.ok) {
    throw new ApiError(resp.status, 'GLB render failed');
  }
  return resp.arrayBuffer();
}

export async function apiCutlist(dsl: string): Promise<{ items: CutlistItem[] }> {
  return post<{ items: CutlistItem[] }>('/api/cutlist', { dsl });
}

export async function apiExportZip(
  dsl: string,
  settings: { ignore_grain: boolean } = { ignore_grain: false },
): Promise<Blob> {
  const resp = await fetch('/api/export.zip', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dsl, settings }),
  });
  if (!resp.ok) {
    throw new ApiError(resp.status, 'Export failed');
  }
  return resp.blob();
}

export async function apiExportHtml(
  dsl: string,
  settings: { ignore_grain: boolean } = { ignore_grain: false },
): Promise<string> {
  const resp = await fetch('/api/export.html', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ dsl, settings }),
  });
  if (!resp.ok) {
    throw new ApiError(resp.status, 'Preview failed');
  }
  return resp.text();
}

export async function apiStdlib(): Promise<StdLibData> {
  const resp = await fetch('/api/stdlib');
  if (!resp.ok) throw new ApiError(resp.status, 'Failed to load stdlib');
  return resp.json() as Promise<StdLibData>;
}

export async function apiVersion(): Promise<string> {
  const resp = await fetch('/api/version');
  if (!resp.ok) return '';
  const data = (await resp.json()) as { version: string };
  return data.version;
}
