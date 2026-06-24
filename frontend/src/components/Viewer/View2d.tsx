import { useRef, useEffect, useCallback } from 'react';
import { useStore } from '../../store/useStore';
import { useSettings } from '../../store/useSettings';
import type { ResolvedProject, Part } from '../../types/cabinet';

const BG = '#050a18';

const BAY_FILL: Record<string, string> = {
  shelves: 'rgba(80,140,220,0.18)',
  hanging: 'rgba(220,130,60,0.18)',
  shoes: 'rgba(60,180,110,0.18)',
  storage: 'rgba(120,130,160,0.15)',
  drawers: 'rgba(150,90,200,0.18)',
  drawers_no_front: 'rgba(150,90,200,0.10)',
  hooks: 'rgba(200,170,60,0.18)',
  empty: 'rgba(255,255,255,0.04)',
};

interface HitRegion {
  kind: 'bay' | 'part';
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

interface Transform {
  panX: number;
  panY: number;
  zoom: number;
}

function partXY(part: Part) {
  const sz: Record<string, number> = { x: 0, y: 0, z: 0 };
  sz[part.axes.length_axis] += part.length;
  sz[part.axes.width_axis] += part.width;
  sz[part.axes.thickness_axis] += part.thickness;
  return { x: part.origin.x, y: part.origin.y, w: sz.x ?? 0, h: sz.y ?? 0 };
}

function drawProject(
  canvas: HTMLCanvasElement,
  project: ResolvedProject,
  doorsVisible: boolean,
  showDimensions: boolean,
  dimsFromFloor: boolean,
  hitRegions: HitRegion[],
  transform: Transform,
) {
  const container = canvas.parentElement!;
  canvas.width = container.clientWidth || canvas.offsetWidth;
  canvas.height = container.clientHeight || canvas.offsetHeight;

  const ctx = canvas.getContext('2d')!;
  hitRegions.length = 0;

  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const PAD_LEFT = dimsFromFloor ? 90 : 60, PAD_RIGHT = showDimensions ? 60 : 30, PAD_TOP = 30, PAD_BOTTOM = 50;
  const drawW = canvas.width - PAD_LEFT - PAD_RIGHT;
  const drawH = canvas.height - PAD_TOP - PAD_BOTTOM;

  const scale = Math.min(drawW / project.width, drawH / project.height);
  const offX = PAD_LEFT + (drawW - project.width * scale) / 2;
  const offY = PAD_TOP + (drawH - project.height * scale) / 2;

  const cx = (x: number) => offX + x * scale;
  const cy = (y: number) => offY + (project.height - y) * scale;
  const cs = (v: number) => v * scale;

  ctx.save();
  ctx.translate(transform.panX, transform.panY);
  ctx.scale(transform.zoom, transform.zoom);

  // Cabinet interior
  ctx.fillStyle = '#0d1525';
  ctx.fillRect(cx(0), cy(project.height), cs(project.width), cs(project.height));

  // Bay zones
  for (const bay of project.bays) {
    const bx = cx(bay.x), by = cy(bay.y + bay.height), bw = cs(bay.width), bh = cs(bay.height);
    ctx.fillStyle = BAY_FILL[bay.function.kind] ?? 'rgba(150,160,180,0.12)';
    ctx.fillRect(bx, by, bw, bh);
    hitRegions.push({ kind: 'bay', id: bay.id, x: bx, y: by, w: bw, h: bh });

    // Drawer divisions
    if (bay.function.kind === 'drawers' || bay.function.kind === 'drawers_no_front') {
      const noFront = bay.function.kind === 'drawers_no_front';
      const count = (bay.function.params.count as number) ?? 3;
      const drawerH = bh / count;
      ctx.strokeStyle = 'rgba(180,130,240,0.5)';
      ctx.lineWidth = 1;
      if (noFront) ctx.setLineDash([4, 4]);
      for (let i = 1; i < count; i++) {
        const ly = by + i * drawerH;
        ctx.beginPath();
        ctx.moveTo(bx + 2, ly);
        ctx.lineTo(bx + bw - 2, ly);
        ctx.stroke();
      }
      ctx.setLineDash([]);
      if (!noFront) {
        // Handle indicators — omitted for no_front since door hides the drawer faces
        const handleW = Math.min(40, bw * 0.35);
        const handleH = Math.max(2, drawerH * 0.1);
        ctx.fillStyle = 'rgba(180,130,240,0.4)';
        for (let i = 0; i < count; i++) {
          const centerY = by + (i + 0.5) * drawerH;
          ctx.fillRect(bx + (bw - handleW) / 2, centerY - handleH / 2, handleW, handleH);
        }
      }
    }
  }

  // Structural panels
  for (const part of project.parts) {
    if (part.kind === 'back_panel' || part.kind === 'door' || part.kind === 'shelf') continue;
    const { x, y, w, h } = partXY(part);
    if (w < 0.5 || h < 0.5) continue;
    if (['side_panel', 'top_panel', 'bottom_panel', 'divider'].includes(part.kind)) {
      const pw = part.kind === 'divider' ? Math.max(3, cs(w)) : cs(w);
      const ph = cs(h);
      const px = cx(x), py = cy(y + h);
      ctx.fillStyle = '#7a6a50';
      ctx.fillRect(px, py, pw, ph);
      ctx.strokeStyle = part.kind === 'divider' ? '#c0a070' : '#a08060';
      ctx.lineWidth = part.kind === 'divider' ? 1 : 0.5;
      ctx.strokeRect(px, py, pw, ph);
      hitRegions.push({ kind: 'part', id: part.id, x: px, y: py, w: pw, h: ph });
    }
  }

  // Shelves
  for (const part of project.parts) {
    if (part.kind !== 'shelf') continue;
    const { x, y, w, h } = partXY(part);
    const thickness = Math.max(2, cs(part.thickness));
    const sx = cx(x), sy = cy(y + h) - thickness / 2, sw = cs(w);
    ctx.fillStyle = '#8a7855';
    ctx.fillRect(sx, sy, sw, thickness);
    ctx.strokeStyle = '#b09a70';
    ctx.lineWidth = 0.5;
    ctx.strokeRect(sx, sy, sw, thickness);
    hitRegions.push({ kind: 'part', id: part.id, x: sx, y: sy, w: sw, h: thickness });
  }

  // Hanging rods
  for (const hw of project.hardware) {
    if (hw.kind !== 'rod' || !hw.position) continue;
    const halfLen = ((hw.params?.length as number) || 200) / 2;
    const rodY = cy(hw.position.y);
    ctx.strokeStyle = '#aabbcc';
    ctx.lineWidth = Math.max(2, cs(5));
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(cx(hw.position.x - halfLen), rodY);
    ctx.lineTo(cx(hw.position.x + halfLen), rodY);
    ctx.stroke();
    for (const sx of [hw.position.x - halfLen, hw.position.x + halfLen]) {
      ctx.beginPath();
      ctx.arc(cx(sx), rodY, Math.max(3, cs(7)), 0, Math.PI * 2);
      ctx.fillStyle = '#aabbcc';
      ctx.fill();
    }
  }

  // Doors
  if (doorsVisible) {
    for (const part of project.parts) {
      if (part.kind !== 'door') continue;
      const { x, y, w, h } = partXY(part);
      const dx = cx(x), dy = cy(y + h), dw = cs(w), dh = cs(h);
      ctx.fillStyle = 'rgba(100,160,230,0.18)';
      ctx.fillRect(dx, dy, dw, dh);
      ctx.strokeStyle = 'rgba(100,170,255,0.6)';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(dx, dy, dw, dh);
    }
  }

  // Bay labels
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  for (const bay of project.bays) {
    const labelSize = Math.min(13, Math.max(9, cs(40)));
    ctx.font = `${labelSize}px system-ui`;
    ctx.fillStyle = 'rgba(180,200,240,0.7)';
    const label = bay.function.kind.charAt(0).toUpperCase() + bay.function.kind.slice(1);
    ctx.fillText(label, cx(bay.x + bay.width / 2), cy(bay.y + bay.height / 2));

    if (cs(bay.width) > 40) {
      ctx.font = `${Math.max(8, labelSize - 2)}px system-ui`;
      ctx.fillStyle = 'rgba(140,160,200,0.6)';
      ctx.fillText(
        `${Math.round(bay.width)}`,
        cx(bay.x + bay.width / 2),
        cy(bay.y + bay.height) - 8,
      );
    }
  }

  // Per-bay dimension labels (right side, outside cabinet)
  if (showDimensions) {
    const labelX = cx(project.width) + 8;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.font = '9px system-ui';
    ctx.fillStyle = 'rgba(100,180,255,0.75)';
    const _dimSeen = new Set<string>();
    const uniqueBays = project.bays.filter(bay => {
      const key = `${bay.y}:${bay.height}`;
      if (_dimSeen.has(key)) return false;
      _dimSeen.add(key);
      return true;
    });
    for (const bay of uniqueBays) {
      const midY = cy(bay.y + bay.height / 2);
      const topY = cy(bay.y + bay.height);
      const botY = cy(bay.y);
      ctx.strokeStyle = 'rgba(100,180,255,0.3)';
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(cx(project.width) + 2, topY);
      ctx.lineTo(labelX + 28, topY);
      ctx.moveTo(cx(project.width) + 2, botY);
      ctx.lineTo(labelX + 28, botY);
      ctx.moveTo(labelX + 4, topY);
      ctx.lineTo(labelX + 4, botY);
      ctx.stroke();

      if (bay.function.kind === 'drawers') {
        const count = (bay.function.params.count as number) ?? 3;
        const dh = Math.round(bay.height / count);
        ctx.fillText(`${dh}×${count}`, labelX + 8, midY);
      } else {
        ctx.fillText(`${Math.round(bay.height)}`, labelX + 8, midY);
      }
    }
  }

  // Overall dimensions
  ctx.strokeStyle = 'rgba(140,160,200,0.6)';
  ctx.fillStyle = 'rgba(160,180,220,0.8)';
  ctx.lineWidth = 1;
  ctx.textAlign = 'center';
  ctx.font = '12px system-ui';

  const dimLineY = cy(0) + 30;
  ctx.beginPath();
  ctx.moveTo(cx(0), cy(0) + 6); ctx.lineTo(cx(0), dimLineY + 4);
  ctx.moveTo(cx(project.width), cy(0) + 6); ctx.lineTo(cx(project.width), dimLineY + 4);
  ctx.moveTo(cx(0), dimLineY); ctx.lineTo(cx(project.width), dimLineY);
  ctx.stroke();
  ctx.fillText(`${Math.round(project.width)} mm`, cx(project.width / 2), dimLineY + 14);

  const dimLineX = cx(0) - 30;
  ctx.beginPath();
  ctx.moveTo(cx(0) - 6, cy(0)); ctx.lineTo(dimLineX - 4, cy(0));
  ctx.moveTo(cx(0) - 6, cy(project.height)); ctx.lineTo(dimLineX - 4, cy(project.height));
  ctx.moveTo(dimLineX, cy(0)); ctx.lineTo(dimLineX, cy(project.height));
  ctx.stroke();
  ctx.save();
  ctx.translate(dimLineX - 14, cy(project.height / 2));
  ctx.rotate(-Math.PI / 2);
  ctx.fillText(`${Math.round(project.height)} mm`, 0, 0);
  ctx.restore();

  // From-floor dimension ticks (left side)
  if (dimsFromFloor) {
    const boundaries = new Set<number>();
    for (const bay of project.bays) {
      boundaries.add(bay.y);
      boundaries.add(bay.y + bay.height);
    }
    const tickX = cx(0) - 8;
    const labelX = cx(0) - 12;
    ctx.strokeStyle = 'rgba(100,180,255,0.3)';
    ctx.fillStyle = 'rgba(100,180,255,0.75)';
    ctx.lineWidth = 0.5;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    ctx.font = '9px system-ui';
    for (const y of boundaries) {
      if (y === 0 || y === project.height) continue;
      const canvasY = cy(y);
      ctx.beginPath();
      ctx.moveTo(cx(0) - 2, canvasY);
      ctx.lineTo(tickX, canvasY);
      ctx.stroke();
      ctx.fillText(`${Math.round(y)}`, labelX, canvasY);
    }
  }

  // Module split lines
  ctx.setLineDash([6, 4]);
  ctx.strokeStyle = 'rgba(180,200,255,0.25)';
  ctx.lineWidth = 1;
  for (const mod of project.modules) {
    if (mod.y === 0) continue;
    ctx.beginPath();
    ctx.moveTo(cx(0), cy(mod.y));
    ctx.lineTo(cx(project.width), cy(mod.y));
    ctx.stroke();
  }
  ctx.setLineDash([]);

  ctx.restore(); // pop pan/zoom transform
}

function drawEmpty(canvas: HTMLCanvasElement) {
  const container = canvas.parentElement!;
  canvas.width = container.clientWidth || canvas.offsetWidth;
  canvas.height = container.clientHeight || canvas.offsetHeight;
  const ctx = canvas.getContext('2d')!;
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#2a3a5a';
  ctx.font = '14px system-ui';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('Compile a design to see the front view.', canvas.width / 2, canvas.height / 2);
}

export default function View2d() {
  const project = useStore((s) => s.project);
  const doorsVisible = useStore((s) => s.doorsVisible);
  const showDimensions = useStore((s) => s.showDimensions);
  const selectBay = useStore((s) => s.selectBay);
  const selectPart = useStore((s) => s.selectPart);
  const { settings } = useSettings();
  const dimsFromFloor = settings.dims_from_floor;

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const hitRegionsRef = useRef<HitRegion[]>([]);
  const transformRef = useRef<Transform>({ panX: 0, panY: 0, zoom: 1 });
  const redrawRef = useRef<() => void>(() => {});

  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (project) {
      drawProject(canvas, project, doorsVisible, showDimensions, dimsFromFloor, hitRegionsRef.current, transformRef.current);
    } else {
      drawEmpty(canvas);
    }
  }, [project, doorsVisible, showDimensions, dimsFromFloor]);

  // Keep ref in sync with latest closure
  useEffect(() => { redrawRef.current = redraw; }, [redraw]);

  // Redraw on dependency changes
  useEffect(() => { redraw(); }, [redraw]);

  // ResizeObserver — set up once
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(() => requestAnimationFrame(() => redrawRef.current()));
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  // Wheel zoom — set up once, reads from refs
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    function onWheel(e: WheelEvent) {
      e.preventDefault();
      const rect = canvas!.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const { panX, panY, zoom } = transformRef.current;
      const factor = e.deltaY > 0 ? 0.85 : 1 / 0.85;
      const newZoom = Math.max(0.15, Math.min(6, zoom * factor));
      transformRef.current = {
        panX: mx - (mx - panX) * (newZoom / zoom),
        panY: my - (my - panY) * (newZoom / zoom),
        zoom: newZoom,
      };
      redrawRef.current();
    }
    canvas.addEventListener('wheel', onWheel, { passive: false });
    return () => canvas.removeEventListener('wheel', onWheel);
  }, []);

  function handleClickAt(clientX: number, clientY: number) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = clientX - rect.left;
    const my = clientY - rect.top;
    const { panX, panY, zoom } = transformRef.current;
    const tx = (mx - panX) / zoom;
    const ty = (my - panY) / zoom;

    for (let i = hitRegionsRef.current.length - 1; i >= 0; i--) {
      const r = hitRegionsRef.current[i]!;
      if (tx >= r.x && tx <= r.x + r.w && ty >= r.y && ty <= r.y + r.h) {
        if (r.kind === 'bay') selectBay(r.id);
        else selectPart(r.id);
        return;
      }
    }
    selectBay(null);
  }

  function handleMouseDown(e: React.MouseEvent<HTMLCanvasElement>) {
    if (e.button !== 0) return;
    const startX = e.clientX;
    const startY = e.clientY;
    const { panX, panY } = transformRef.current;
    let moved = false;

    function onMove(ev: MouseEvent) {
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;
      if (!moved && Math.abs(dx) + Math.abs(dy) < 4) return;
      moved = true;
      if (canvasRef.current) canvasRef.current.style.cursor = 'grabbing';
      transformRef.current = { ...transformRef.current, panX: panX + dx, panY: panY + dy };
      redrawRef.current();
    }

    function onUp(ev: MouseEvent) {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
      if (canvasRef.current) canvasRef.current.style.cursor = 'crosshair';
      if (!moved) handleClickAt(ev.clientX, ev.clientY);
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  }

  function handleDoubleClick() {
    transformRef.current = { panX: 0, panY: 0, zoom: 1 };
    redrawRef.current();
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        style={{ width: '100%', height: '100%', display: 'block', cursor: 'crosshair' }}
      />
    </div>
  );
}
