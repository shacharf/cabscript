import { useRef, useEffect, useCallback } from 'react';
import { useStore } from '../../store/useStore';
import type { ResolvedProject, Part } from '../../types/cabinet';

const BG = '#050a18';

const BAY_FILL: Record<string, string> = {
  shelves: 'rgba(80,140,220,0.18)',
  hanging: 'rgba(220,130,60,0.18)',
  shoes: 'rgba(60,180,110,0.18)',
  storage: 'rgba(120,130,160,0.15)',
  drawers: 'rgba(150,90,200,0.18)',
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
  hitRegions: HitRegion[],
) {
  const container = canvas.parentElement!;
  canvas.width = container.clientWidth || canvas.offsetWidth;
  canvas.height = container.clientHeight || canvas.offsetHeight;

  const ctx = canvas.getContext('2d')!;
  hitRegions.length = 0;

  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const PAD_LEFT = 60, PAD_RIGHT = 30, PAD_TOP = 30, PAD_BOTTOM = 50;
  const drawW = canvas.width - PAD_LEFT - PAD_RIGHT;
  const drawH = canvas.height - PAD_TOP - PAD_BOTTOM;

  const scale = Math.min(drawW / project.width, drawH / project.height);
  const offX = PAD_LEFT + (drawW - project.width * scale) / 2;
  const offY = PAD_TOP + (drawH - project.height * scale) / 2;

  const cx = (x: number) => offX + x * scale;
  const cy = (y: number) => offY + (project.height - y) * scale;
  const cs = (v: number) => v * scale;

  // Cabinet interior
  ctx.fillStyle = '#0d1525';
  ctx.fillRect(cx(0), cy(project.height), cs(project.width), cs(project.height));

  // Bay zones
  for (const bay of project.bays) {
    const bx = cx(bay.x), by = cy(bay.y + bay.height), bw = cs(bay.width), bh = cs(bay.height);
    ctx.fillStyle = BAY_FILL[bay.function.kind] ?? 'rgba(150,160,180,0.12)';
    ctx.fillRect(bx, by, bw, bh);
    hitRegions.push({ kind: 'bay', id: bay.id, x: bx, y: by, w: bw, h: bh });
  }

  // Structural panels
  for (const part of project.parts) {
    if (part.kind === 'back_panel' || part.kind === 'door' || part.kind === 'shelf') continue;
    const { x, y, w, h } = partXY(part);
    if (w < 0.5 || h < 0.5) continue;
    if (['side_panel', 'top_panel', 'bottom_panel'].includes(part.kind)) {
      const px = cx(x), py = cy(y + h), pw = cs(w), ph = cs(h);
      ctx.fillStyle = '#7a6a50';
      ctx.fillRect(px, py, pw, ph);
      ctx.strokeStyle = '#a08060';
      ctx.lineWidth = 0.5;
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

  // Dimensions
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
  const selectBay = useStore((s) => s.selectBay);
  const selectPart = useStore((s) => s.selectPart);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const hitRegionsRef = useRef<HitRegion[]>([]);

  const redraw = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (project) {
      drawProject(canvas, project, doorsVisible, hitRegionsRef.current);
    } else {
      drawEmpty(canvas);
    }
  }, [project, doorsVisible]);

  useEffect(() => {
    redraw();
  }, [redraw]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;
    const observer = new ResizeObserver(() => requestAnimationFrame(redraw));
    observer.observe(container);
    return () => observer.disconnect();
  }, [redraw]);

  function handleClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    // Iterate in reverse (topmost drawn item wins)
    for (let i = hitRegionsRef.current.length - 1; i >= 0; i--) {
      const r = hitRegionsRef.current[i]!;
      if (mx >= r.x && mx <= r.x + r.w && my >= r.y && my <= r.y + r.h) {
        if (r.kind === 'bay') {
          selectBay(r.id);
        } else {
          selectPart(r.id);
        }
        return;
      }
    }
    // Clicked empty space — deselect
    selectBay(null);
  }

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <canvas
        ref={canvasRef}
        onClick={handleClick}
        style={{ width: '100%', height: '100%', display: 'block', cursor: 'crosshair' }}
      />
    </div>
  );
}
