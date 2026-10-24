// Shared three.js stage: renderer, resize, render-only-when-visible loop, and WebGL fallback.
import * as THREE from 'three';

const params = new URLSearchParams(location.search);
export const FORCE_NO_WEBGL = params.has('nowebgl');

export function hasWebGL() {
  if (FORCE_NO_WEBGL) return false;
  try {
    const c = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (c.getContext('webgl2') || c.getContext('webgl')));
  } catch { return false; }
}

const stages = new Set();
let rafId = null;
let last = performance.now();
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  for (const s of stages) if (s.visible && !document.hidden) s.tick(dt, now / 1000);
  rafId = requestAnimationFrame(loop);
}
function ensureLoop() { if (rafId === null) rafId = requestAnimationFrame(loop); }

export function fallback(container, message) {
  container.classList.add('no-webgl');
  const div = document.createElement('div');
  div.className = 'webgl-fallback';
  div.setAttribute('role', 'note');
  div.innerHTML = `<strong>3D view unavailable</strong><span>${message || 'Your browser has WebGL turned off or unsupported. The physics still runs: numbers and controls below keep working.'}</span>`;
  container.appendChild(div);
  return { ok: false };
}

export function createStage(container, { fov = 40, camPos = [0, 2, 8], target = [0, 0, 0], background = 0x000000 } = {}) {
  if (!hasWebGL()) return fallback(container);
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  } catch (e) {
    return fallback(container);
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(background, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const canvas = renderer.domElement;
  canvas.setAttribute('role', 'img');
  container.appendChild(canvas);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(fov, 1, 0.05, 200);
  camera.position.set(...camPos);
  const tgt = new THREE.Vector3(...target);
  camera.lookAt(tgt);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x1a1a1a, 1.4));
  const dir = new THREE.DirectionalLight(0xffffff, 1.6);
  dir.position.set(4, 8, 6);
  scene.add(dir);

  const stage = { ok: true, renderer, scene, camera, canvas, target: tgt, visible: true, frames: 0, updaters: [], container };
  stage.onFrame = (fn) => stage.updaters.push(fn);
  stage.resize = () => {
    const w = container.clientWidth || 300, h = container.clientHeight || 200;
    renderer.setSize(w, h, false);
    canvas.style.width = '100%'; canvas.style.height = '100%';
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    stage.aspect = w / h;
    stage.updaters.forEach((f) => f.resize && f.resize(w, h));
  };
  stage.tick = (dt, t) => {
    for (const f of stage.updaters) (f.update || f)(dt, t);
    renderer.render(scene, camera);
    stage.frames++;
  };
  // Pointer helper: normalised device coords.
  stage.ndc = (ev) => {
    const r = canvas.getBoundingClientRect();
    return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  };
  // Distance at which a box of world width w and height h fits the view (with margin).
  stage.fitDistance = (w, h, margin = 1.1) => {
    const v = (camera.fov * Math.PI) / 360, a = stage.aspect || 1;
    const hf = Math.atan(Math.tan(v) * a);
    return margin * Math.max(h / 2 / Math.tan(v), w / 2 / Math.tan(hf));
  };
  stage.toScreen = (v3) => {
    const p = v3.clone().project(camera);
    const r = canvas.getBoundingClientRect();
    return { x: r.left + (p.x + 1) / 2 * r.width, y: r.top + (1 - p.y) / 2 * r.height };
  };
  new ResizeObserver(() => stage.resize()).observe(container);
  new IntersectionObserver((entries) => { for (const e of entries) stage.visible = e.isIntersecting; }, { rootMargin: '100px' }).observe(container);
  canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); stage.visible = false; });
  stage.resize();
  stages.add(stage);
  ensureLoop();
  return stage;
}

// Utilisation colour map: 0 -> dim grey-green, 0.5 -> lime, 0.8 -> amber, >=1 -> red.
const STOPS = [[0, [0.16, 0.2, 0.16]], [0.45, [0.93, 1.0, 0.25]], [0.8, [1.0, 0.62, 0.1]], [1.0, [1.0, 0.13, 0.1]]];
export function utilColor(u, out = new THREE.Color()) {
  u = Math.max(0, Math.min(1, u));
  for (let i = 1; i < STOPS.length; i++) {
    if (u <= STOPS[i][0]) {
      const [u0, c0] = STOPS[i - 1], [u1, c1] = STOPS[i];
      const t = (u - u0) / (u1 - u0);
      return out.setRGB(c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, c0[2] + (c1[2] - c0[2]) * t);
    }
  }
  return out.setRGB(1, 0.13, 0.1);
}

export function fmt(x, d = 1) {
  if (!isFinite(x)) return '—';
  return Number(x).toLocaleString('en-US', { maximumFractionDigits: d, minimumFractionDigits: d });
}

export function makeGrid(size = 20, div = 40) {
  const g = new THREE.GridHelper(size, div, 0x2a3a10, 0x151a10);
  g.material.transparent = true; g.material.opacity = 0.7;
  return g;
}
