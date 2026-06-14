import { useRef, useEffect } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { useStore } from '../../store/useStore';

export default function View3d() {
  const glbBlobUrl = useStore((s) => s.glbBlobUrl);
  const doorsVisible = useStore((s) => s.doorsVisible);
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Stable refs for Three.js objects
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const currentModelRef = useRef<THREE.Object3D | null>(null);
  const rafRef = useRef<number>(0);

  // Init Three.js once
  useEffect(() => {
    const canvas = canvasRef.current!;
    const container = containerRef.current!;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    rendererRef.current = renderer;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050a18);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100);
    camera.position.set(2, 2, 3);
    cameraRef.current = camera;

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controlsRef.current = controls;

    scene.add(new THREE.HemisphereLight(0xfff4e0, 0x334455, 0.7));
    const key = new THREE.DirectionalLight(0xffffff, 1.2);
    key.position.set(4, 6, 3);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0xc8d8ff, 0.5);
    fill.position.set(-4, 2, 1);
    scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffffff, 0.3);
    rim.position.set(-2, 3, -4);
    scene.add(rim);
    scene.add(new THREE.GridHelper(6, 24, 0x2a2a2a, 0x2a2a2a));

    function resize() {
      const w = container.clientWidth;
      const h = container.clientHeight;
      renderer.setSize(w, h);
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
    }
    const observer = new ResizeObserver(resize);
    observer.observe(container);
    resize();

    function animate() {
      rafRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();

    return () => {
      cancelAnimationFrame(rafRef.current);
      observer.disconnect();
      controls.dispose();
      renderer.dispose();
    };
  }, []);

  // Load GLB when URL changes
  useEffect(() => {
    const scene = sceneRef.current;
    const camera = cameraRef.current;
    const controls = controlsRef.current;
    if (!scene || !camera || !controls || !glbBlobUrl) return;

    if (currentModelRef.current) {
      scene.remove(currentModelRef.current);
      currentModelRef.current = null;
    }

    new GLTFLoader().load(
      glbBlobUrl,
      (gltf) => {
        const model = gltf.scene;
        model.scale.setScalar(0.001); // mm → m
        scene.add(model);
        currentModelRef.current = model;

        // Apply door visibility
        applyDoorVis(model, doorsVisible);

        // Frame camera
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const dist = (maxDim / (2 * Math.tan((camera.fov * Math.PI) / 360))) * 1.5;
        camera.position.set(
          center.x + dist * 0.6,
          center.y + dist * 0.5,
          center.z + dist * 0.9,
        );
        controls.target.copy(center);
        controls.update();
      },
      undefined,
      (err) => console.error('GLB load error', err),
    );
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [glbBlobUrl]);

  // Toggle door visibility
  useEffect(() => {
    if (currentModelRef.current) {
      applyDoorVis(currentModelRef.current, doorsVisible);
    }
  }, [doorsVisible]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <canvas ref={canvasRef} style={{ width: '100%', height: '100%', display: 'block' }} />
      {!glbBlobUrl && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#2a3a5a',
            fontSize: 14,
            pointerEvents: 'none',
          }}
        >
          Switch to 3D tab after compiling to render the model.
        </div>
      )}
    </div>
  );
}

function applyDoorVis(model: THREE.Object3D, visible: boolean) {
  model.traverse((node) => {
    if (node.name?.startsWith('door_')) {
      node.visible = visible;
    }
  });
}
