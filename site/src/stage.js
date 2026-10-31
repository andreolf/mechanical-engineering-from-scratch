// Shared three.js stage: studio lighting, soft shadows, render-only-when-visible loop,
// optional touch-friendly orbit mode, capped pixel ratio and a WebGL fallback.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

const params = new URLSearchParams(location.search);
export const FORCE_NO_WEBGL = params.has('nowebgl');
export const REDUCED_MOTION = matchMedia('(prefers-reduced-motion: reduce)').matches;
export const COARSE = matchMedia('(pointer: coarse)').matches;

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
  div.innerHTML = `<strong>3D view unavailable</strong><span>${message || 'WebGL is turned off or unsupported in this browser. The physics still runs, so the numbers and controls keep working.'}</span>`;
  container.appendChild(div);
  return { ok: false };
}

/** Run init() the first time the element comes within 400px of the viewport. */
export function whenNear(el, init) {
  if (!('IntersectionObserver' in window)) return init();
  const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); init(); } }, { rootMargin: '400px 0px' });
  io.observe(el);
}

export function createStage(container, { fov = 40, camPos = [0, 2, 8], target = [0, 0, 0], shadows = true, orbit = true } = {}) {
  if (!hasWebGL()) return fallback(container);
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  } catch { return fallback(container); }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, COARSE ? 1.75 : 2));
  renderer.setClearColor(0x000000, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  if (shadows) { renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFShadowMap; /* PCFSoft was removed in recent three.js and only warned */ }
  const canvas = renderer.domElement;
  canvas.setAttribute('role', 'img');
  container.appendChild(canvas);
  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;
  const camera = new THREE.PerspectiveCamera(fov, 1, 0.05, 200);
  camera.position.set(...camPos);
  const tgt = new THREE.Vector3(...target);
  camera.lookAt(tgt);
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  key.position.set(5, 9, 6);
  if (shadows) {
    key.castShadow = true;
    key.shadow.mapSize.set(COARSE ? 1024 : 2048, COARSE ? 1024 : 2048);
    key.shadow.radius = 4;
    key.shadow.bias = -0.0004;
    key.shadow.normalBias = 0.02;
  }
  scene.add(key, key.target);
  const rim = new THREE.DirectionalLight(0xdfe9ff, 0.9);
  rim.position.set(-6, 3, -5);
  scene.add(rim);

  const stage = { ok: true, renderer, scene, camera, canvas, key, target: tgt, visible: true, frames: 0, updaters: [], container, orbiting: false };
  stage.onFrame = (fn) => stage.updaters.push(fn);
  stage.resize = () => {
    const w = container.clientWidth || 300, h = container.clientHeight || 200;
    renderer.setSize(w, h, false);
    canvas.style.width = '100%'; canvas.style.height = '100%';
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    stage.aspect = w / h;
  };
  stage.tick = (dt, t) => {
    for (const f of stage.updaters) (f.update || f)(dt, t);
    if (stage.controls && stage.orbiting) stage.controls.update();
    renderer.render(scene, camera);
    stage.frames++;
  };
  stage.ndc = (ev) => {
    const r = canvas.getBoundingClientRect();
    return new THREE.Vector2(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  };
  stage.toScreen = (v3) => {
    const p = v3.clone().project(camera);
    const r = canvas.getBoundingClientRect();
    return { x: r.left + ((p.x + 1) / 2) * r.width, y: r.top + ((1 - p.y) / 2) * r.height };
  };
  stage.fitDistance = (w, h, margin = 1.1) => {
    const v = (camera.fov * Math.PI) / 360, a = stage.aspect || 1;
    const hf = Math.atan(Math.tan(v) * a);
    return margin * Math.max(h / 2 / Math.tan(v), w / 2 / Math.tan(hf));
  };
  /** Shadow-catching floor. */
  stage.addFloor = (y = 0, size = 30, opacity = 0.55) => {
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.ShadowMaterial({ opacity }));
    floor.rotation.x = -Math.PI / 2; floor.position.y = y; floor.receiveShadow = true;
    scene.add(floor);
    const grid = new THREE.GridHelper(size, size * 2, 0x23261c, 0x111309);
    grid.position.y = y + 0.001; grid.material.transparent = true; grid.material.opacity = 0.9;
    scene.add(grid);
    return floor;
  };
  // Orbit mode: off by default so the page scrolls normally on phones; a button switches it on.
  if (orbit) {
    const controls = new OrbitControls(camera, canvas);
    controls.enabled = false; controls.enableDamping = true; controls.enablePan = false;
    controls.minDistance = 0.5; controls.maxDistance = 60;
    stage.controls = controls;
    canvas.style.touchAction = 'pan-y'; // OrbitControls sets 'none'; restore scrolling until orbit mode is on
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'orbit-toggle';
    btn.setAttribute('aria-pressed', 'false');
    btn.textContent = 'Rotate and zoom';
    btn.addEventListener('click', () => {
      stage.orbiting = !stage.orbiting;
      controls.enabled = stage.orbiting;
      controls.target.copy(stage.target);
      container.classList.toggle('is-orbiting', stage.orbiting);
      canvas.style.touchAction = stage.orbiting ? 'none' : 'pan-y';
      btn.setAttribute('aria-pressed', String(stage.orbiting));
      btn.textContent = stage.orbiting ? 'Done' : 'Rotate and zoom';
    });
    container.appendChild(btn);
  }
  new ResizeObserver(() => stage.resize()).observe(container);
  new IntersectionObserver((entries) => { for (const e of entries) stage.visible = e.isIntersecting; }, { rootMargin: '80px' }).observe(container);
  canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault(); stage.visible = false; });
  stage.resize();
  stages.add(stage);
  ensureLoop();
  return stage;
}

// Utilisation colour map for stress: cool graphite -> lime -> amber -> red at yield.
const STOPS = [[0, [0.22, 0.25, 0.24]], [0.45, [0.85, 0.95, 0.2]], [0.8, [1.0, 0.6, 0.12]], [1.0, [1.0, 0.18, 0.1]]];
export function utilColor(u, out = new THREE.Color()) {
  u = Math.max(0, Math.min(1, u));
  for (let i = 1; i < STOPS.length; i++) {
    if (u <= STOPS[i][0]) {
      const [u0, c0] = STOPS[i - 1], [u1, c1] = STOPS[i];
      const t = (u - u0) / (u1 - u0);
      return out.setRGB(c0[0] + (c1[0] - c0[0]) * t, c0[1] + (c1[1] - c0[1]) * t, c0[2] + (c1[2] - c0[2]) * t, THREE.SRGBColorSpace);
    }
  }
  return out.setRGB(1, 0.18, 0.1, THREE.SRGBColorSpace);
}

const nf = new Map();
export function fmt(x, d = 1) {
  if (!isFinite(x)) return '–';
  if (!nf.has(d)) nf.set(d, new Intl.NumberFormat('en-US', { maximumFractionDigits: d, minimumFractionDigits: d }));
  return nf.get(d).format(x);
}

/** Paint a range input's filled part (CSS var) so the track shows its value. */
export function paintRange(input) {
  const f = () => input.style.setProperty('--fill', `${((input.value - input.min) / (input.max - input.min)) * 100}%`);
  input.addEventListener('input', f); f();
  return f;
}
