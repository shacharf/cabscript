// ── State ────────────────────────────────────────────────────────────────────

let lastProject = null;   // most recent compiled ResolvedProject
let doorsVisible = true;  // door toggle state
let currentView = '3d';   // '3d' | '2d'

// ── API ───────────────────────────────────────────────────────────────────────

async function apiPost(path, body) {
  return fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

// ── UI helpers ────────────────────────────────────────────────────────────────

function setStatus(text) {
  const el = document.getElementById('status');
  if (el) el.textContent = text;
}

function showMessages(warnings) {
  const el = document.getElementById('messages');
  if (!el) return;
  el.innerHTML = '';
  if (!warnings || warnings.length === 0) {
    el.innerHTML = '<span style="color:#4a4">&#10003; OK</span>';
    return;
  }
  for (const w of warnings) {
    const div = document.createElement('div');
    div.className = `msg-${w.severity}`;
    div.textContent = `[${w.code}] ${w.message}`;
    el.appendChild(div);
  }
}

function showCutlist(items) {
  const tbody = document.getElementById('cutlist-body');
  if (!tbody) return;
  tbody.innerHTML = '';
  for (const item of items) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.quantity}</td>
      <td>${item.name}</td>
      <td>${Math.round(item.length)}&times;${Math.round(item.width)}&times;${Math.round(item.thickness)}</td>
      <td>${item.material}</td>`;
    tbody.appendChild(tr);
  }
}

// ── Compile ───────────────────────────────────────────────────────────────────

async function compile() {
  const dsl = document.getElementById('dsl-input').value;
  setStatus('Compiling…');
  showMessages([]);
  try {
    const resp = await apiPost('/api/compile', { dsl });
    const data = await resp.json();
    if (!resp.ok) {
      showMessages([{ severity: 'error', code: 'COMPILE_ERROR', message: data.detail || JSON.stringify(data) }]);
      setStatus('Compile failed.');
      return;
    }
    lastProject = data.project;
    showMessages(data.warnings);
    setStatus(`Compiled — ${data.project.parts.length} parts.`);
  } catch (e) {
    showMessages([{ severity: 'error', code: 'NETWORK_ERROR', message: e.message }]);
    setStatus('Error.');
  }
}

// ── Render ────────────────────────────────────────────────────────────────────

async function render() {
  const dsl = document.getElementById('dsl-input').value;
  setStatus('Compiling…');
  showMessages([]);

  try {
    const compResp = await apiPost('/api/compile', { dsl });
    if (!compResp.ok) {
      const err = await compResp.json();
      showMessages([{ severity: 'error', code: 'COMPILE_ERROR', message: err.detail || JSON.stringify(err) }]);
      setStatus('Compile failed.');
      return;
    }
    const compData = await compResp.json();
    lastProject = compData.project;
    showMessages(compData.warnings);
    setStatus(`Compiled — ${compData.project.parts.length} parts. Fetching…`);
  } catch (e) {
    showMessages([{ severity: 'error', code: 'NETWORK_ERROR', message: e.message }]);
    setStatus('Error.');
    return;
  }

  try {
    const clResp = await apiPost('/api/cutlist', { dsl });
    if (clResp.ok) showCutlist((await clResp.json()).items);
  } catch (_) { /* non-fatal */ }

  // Render whichever view is active
  if (currentView === '2d') {
    draw2dFront(lastProject);
    setStatus('Front view rendered.');
    return;
  }

  setStatus('Rendering 3D…');
  try {
    const glbResp = await apiPost('/api/render.glb', { dsl });
    if (!glbResp.ok) { setStatus('GLB render failed.'); return; }
    await loadGlb(await glbResp.arrayBuffer());
    setStatus('Rendered.');
  } catch (e) {
    setStatus('3D error: ' + e.message);
  }
}

// ── Three.js (lazy) ───────────────────────────────────────────────────────────

let _three = null;

async function initThree() {
  if (_three) return _three;

  const THREE = await import('three');
  const { OrbitControls } = await import('three/addons/controls/OrbitControls.js');
  const { GLTFLoader } = await import('three/addons/loaders/GLTFLoader.js');

  const canvas = document.getElementById('viewer');
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x050a18);

  const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100);
  camera.position.set(2, 2, 3);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;

  // Hemisphere light: warm sky, cool ground
  scene.add(new THREE.HemisphereLight(0xfff4e0, 0x334455, 0.7));

  // Key light — top-right-front
  const key = new THREE.DirectionalLight(0xffffff, 1.2);
  key.position.set(4, 6, 3);
  scene.add(key);

  // Fill light — left side, softer
  const fill = new THREE.DirectionalLight(0xc8d8ff, 0.5);
  fill.position.set(-4, 2, 1);
  scene.add(fill);

  // Rim light — back-left, highlights rear edges
  const rim = new THREE.DirectionalLight(0xffffff, 0.3);
  rim.position.set(-2, 3, -4);
  scene.add(rim);

  scene.add(new THREE.GridHelper(6, 24, 0x2a2a2a, 0x2a2a2a));

  function resize() {
    const p = canvas.parentElement;
    renderer.setSize(p.clientWidth, p.clientHeight);
    camera.aspect = p.clientWidth / p.clientHeight;
    camera.updateProjectionMatrix();
  }
  window.addEventListener('resize', resize);
  resize();

  (function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  })();

  _three = { THREE, scene, camera, controls, GLTFLoader };
  return _three;
}

let _currentModel = null;

async function loadGlb(arrayBuffer) {
  const { THREE, scene, camera, controls, GLTFLoader } = await initThree();

  if (_currentModel) { scene.remove(_currentModel); _currentModel = null; }

  const url = URL.createObjectURL(new Blob([arrayBuffer], { type: 'model/gltf-binary' }));

  await new Promise((resolve, reject) => {
    new GLTFLoader().load(url, (gltf) => {
      _currentModel = gltf.scene;
      _currentModel.scale.setScalar(0.001); // mm → m
      scene.add(_currentModel);

      // Apply current door visibility
      applyDoorVisibility();

      // Frame camera
      const box = new THREE.Box3().setFromObject(_currentModel);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z);
      const dist = (maxDim / (2 * Math.tan((camera.fov * Math.PI) / 360))) * 1.5;
      camera.position.set(center.x + dist * 0.6, center.y + dist * 0.5, center.z + dist * 0.9);
      controls.target.copy(center);
      controls.update();

      URL.revokeObjectURL(url);
      resolve();
    }, undefined, (err) => { URL.revokeObjectURL(url); reject(err); });
  });
}

// ── Door toggle ───────────────────────────────────────────────────────────────

function applyDoorVisibility() {
  if (!_currentModel) return;
  _currentModel.traverse((node) => {
    if (node.name && node.name.startsWith('door_')) {
      node.visible = doorsVisible;
    }
  });
}

function toggleDoors() {
  doorsVisible = !doorsVisible;
  const btn = document.getElementById('btn-toggle-doors');
  btn.textContent = doorsVisible ? 'Hide Doors' : 'Show Doors';
  btn.classList.toggle('doors-hidden', !doorsVisible);
  applyDoorVisibility();
  if (currentView === '2d' && lastProject) draw2dFront(lastProject);
}

// ── 2D front view ─────────────────────────────────────────────────────────────

const BG = '#050a18';

function drawEmpty2d() {
  const canvas = document.getElementById('canvas-2d');
  const container = canvas.parentElement;
  canvas.width = container.clientWidth || canvas.offsetWidth;
  canvas.height = container.clientHeight || canvas.offsetHeight;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#2a3a5a';
  ctx.font = '14px system-ui';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('Click Render 3D to compile and draw the front view.', canvas.width / 2, canvas.height / 2);
}

function draw2dFront(project) {
  const canvas = document.getElementById('canvas-2d');
  const container = canvas.parentElement;
  canvas.width = container.clientWidth || canvas.offsetWidth;
  canvas.height = container.clientHeight || canvas.offsetHeight;

  const ctx = canvas.getContext('2d');
  // Dark blue background
  ctx.fillStyle = BG;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const PAD_LEFT = 60, PAD_RIGHT = 30, PAD_TOP = 30, PAD_BOTTOM = 50;
  const drawW = canvas.width - PAD_LEFT - PAD_RIGHT;
  const drawH = canvas.height - PAD_TOP - PAD_BOTTOM;

  const scale = Math.min(drawW / project.width, drawH / project.height);
  const offX = PAD_LEFT + (drawW - project.width * scale) / 2;
  const offY = PAD_TOP + (drawH - project.height * scale) / 2;

  // Model → canvas: x left→right, y bottom→top (inverted for canvas)
  function cx(x) { return offX + x * scale; }
  function cy(y) { return offY + (project.height - y) * scale; }
  function cs(v) { return v * scale; }

  // Given a part, return its {x, y, w, h} in model XY (ignoring Z depth)
  function partXY(part) {
    const sz = { x: 0, y: 0, z: 0 };
    sz[part.axes.length_axis]    += part.length;
    sz[part.axes.width_axis]     += part.width;
    sz[part.axes.thickness_axis] += part.thickness;
    return { x: part.origin.x, y: part.origin.y, w: sz.x, h: sz.y };
  }

  // ── Cabinet interior background ──
  ctx.fillStyle = '#0d1525';
  ctx.fillRect(cx(0), cy(project.height), cs(project.width), cs(project.height));

  // ── Bay zones (color by function) ──
  const BAY_FILL = {
    shelves:  'rgba(80,140,220,0.18)',
    hanging:  'rgba(220,130,60,0.18)',
    shoes:    'rgba(60,180,110,0.18)',
    storage:  'rgba(120,130,160,0.15)',
    drawers:  'rgba(150,90,200,0.18)',
    hooks:    'rgba(200,170,60,0.18)',
    empty:    'rgba(255,255,255,0.04)',
  };
  for (const bay of project.bays) {
    ctx.fillStyle = BAY_FILL[bay.function.kind] || 'rgba(150,160,180,0.12)';
    ctx.fillRect(cx(bay.x), cy(bay.y + bay.height), cs(bay.width), cs(bay.height));
  }

  // ── Structural panels (sides, top, bottom) ──
  for (const part of project.parts) {
    if (part.kind === 'back_panel' || part.kind === 'door' || part.kind === 'shelf') continue;
    const { x, y, w, h } = partXY(part);
    if (w < 0.5 || h < 0.5) continue;

    if (['side_panel', 'top_panel', 'bottom_panel'].includes(part.kind)) {
      ctx.fillStyle = '#7a6a50';
      ctx.fillRect(cx(x), cy(y + h), cs(w), cs(h));
      ctx.strokeStyle = '#a08060';
      ctx.lineWidth = 0.5;
      ctx.strokeRect(cx(x), cy(y + h), cs(w), cs(h));
    }
  }

  // ── Shelves ──
  for (const part of project.parts) {
    if (part.kind !== 'shelf') continue;
    const { x, y, w, h } = partXY(part);
    const thickness = Math.max(2, cs(part.thickness));
    ctx.fillStyle = '#8a7855';
    ctx.fillRect(cx(x), cy(y + h) - thickness / 2, cs(w), thickness);
    ctx.strokeStyle = '#b09a70';
    ctx.lineWidth = 0.5;
    ctx.strokeRect(cx(x), cy(y + h) - thickness / 2, cs(w), thickness);
  }

  // ── Hanging rods ──
  for (const hw of project.hardware) {
    if (hw.kind !== 'rod' || !hw.position) continue;
    const halfLen = ((hw.params?.length) || 200) / 2;
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

  // ── Doors (semi-transparent overlay) ──
  if (doorsVisible) {
    for (const part of project.parts) {
      if (part.kind !== 'door') continue;
      const { x, y, w, h } = partXY(part);
      ctx.fillStyle = 'rgba(100,160,230,0.18)';
      ctx.fillRect(cx(x), cy(y + h), cs(w), cs(h));
      ctx.strokeStyle = 'rgba(100,170,255,0.6)';
      ctx.lineWidth = 1.5;
      ctx.strokeRect(cx(x), cy(y + h), cs(w), cs(h));
    }
  }

  // ── Bay labels ──
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
      ctx.fillText(`${Math.round(bay.width)}`, cx(bay.x + bay.width / 2), cy(bay.y + bay.height) - 8);
    }
  }

  // ── Overall dimensions ──
  ctx.strokeStyle = 'rgba(140,160,200,0.6)';
  ctx.fillStyle = 'rgba(160,180,220,0.8)';
  ctx.lineWidth = 1;
  ctx.textAlign = 'center';
  ctx.font = '12px system-ui';

  // Width (below)
  const dimLineY = cy(0) + 30;
  ctx.beginPath();
  ctx.moveTo(cx(0), cy(0) + 6);   ctx.lineTo(cx(0), dimLineY + 4);
  ctx.moveTo(cx(project.width), cy(0) + 6); ctx.lineTo(cx(project.width), dimLineY + 4);
  ctx.moveTo(cx(0), dimLineY);    ctx.lineTo(cx(project.width), dimLineY);
  ctx.stroke();
  ctx.fillText(`${Math.round(project.width)} mm`, cx(project.width / 2), dimLineY + 14);

  // Height (left)
  const dimLineX = cx(0) - 30;
  ctx.beginPath();
  ctx.moveTo(cx(0) - 6, cy(0));            ctx.lineTo(dimLineX - 4, cy(0));
  ctx.moveTo(cx(0) - 6, cy(project.height)); ctx.lineTo(dimLineX - 4, cy(project.height));
  ctx.moveTo(dimLineX, cy(0));             ctx.lineTo(dimLineX, cy(project.height));
  ctx.stroke();
  ctx.save();
  ctx.translate(dimLineX - 14, cy(project.height / 2));
  ctx.rotate(-Math.PI / 2);
  ctx.fillText(`${Math.round(project.height)} mm`, 0, 0);
  ctx.restore();

  // Module split lines
  for (const mod of project.modules) {
    if (mod.y === 0) continue;
    ctx.setLineDash([6, 4]);
    ctx.strokeStyle = 'rgba(180,200,255,0.25)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(cx(0), cy(mod.y));
    ctx.lineTo(cx(project.width), cy(mod.y));
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

// ── Tab switching ─────────────────────────────────────────────────────────────

function switchView(view) {
  currentView = view;
  document.getElementById('view-3d').style.display = view === '3d' ? '' : 'none';
  document.getElementById('view-2d').style.display = view === '2d' ? '' : 'none';
  document.getElementById('tab-3d').classList.toggle('active', view === '3d');
  document.getElementById('tab-2d').classList.toggle('active', view === '2d');

  if (view === '2d') {
    // Defer one frame so the browser lays out the now-visible div before we measure it
    requestAnimationFrame(() => {
      if (lastProject) draw2dFront(lastProject);
      else drawEmpty2d();
    });
  }
}

// ── Boot ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-compile').addEventListener('click', compile);
  document.getElementById('btn-render').addEventListener('click', render);
  document.getElementById('btn-toggle-doors').addEventListener('click', toggleDoors);
  document.getElementById('tab-3d').addEventListener('click', () => switchView('3d'));
  document.getElementById('tab-2d').addEventListener('click', () => switchView('2d'));
  window.addEventListener('resize', () => {
    if (currentView === '2d') requestAnimationFrame(() => lastProject ? draw2dFront(lastProject) : drawEmpty2d());
  });
});
