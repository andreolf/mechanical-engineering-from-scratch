import * as THREE from 'three';
import { createStage, utilColor, fmt, makeGrid } from './stage.js';
import { cantilever, BEAM_MATERIALS } from './physics.js';

// Physical beam: 2 m cantilever, rectangular 40 x 80 mm section. Drawn at 2 units per metre.
const L = 2.0, b = 0.04, h = 0.08, I = (b * h ** 3) / 12, c = h / 2;
const S = 2.0;           // world units per metre
const SEC = 2.0;         // section drawn x2 for visibility

export function initHero(root) {
  const host = root.querySelector('.hero-canvas');
  const out = root.querySelector('#hero-readout');
  const sliderP = root.querySelector('#hero-load');
  const selMat = root.querySelector('#hero-material');
  const state = { P: 2500, a: L, mat: 'steel', demo: true, tip: 0, sigma: 0, util: 0, k: 1, interactions: 0 };
  window.__mefs = window.__mefs || {};
  window.__mefs.hero = { state };

  const compute = () => {
    const m = BEAM_MATERIALS[state.mat];
    const EI = m.E * I;
    state.tip = cantilever(state.P, state.a, L, EI).w;
    state.sigma = (state.P * state.a * c) / I;
    state.util = state.sigma / m.sy;
    state.k = state.tip > 0 ? Math.min(5, (0.25 * L) / state.tip) : 5;
    const warn = state.util >= 1 ? '<b class="bad">Yield exceeded: linear-elastic model no longer valid</b>'
      : state.tip / L > 0.05 ? '<b class="warn">Large deflection: small-deflection theory becomes inaccurate</b>'
      : `Safety factor vs yield: <b>${fmt(1 / Math.max(state.util, 1e-9), 2)}</b>`;
    out.innerHTML = `<span>Load <b data-k="P">${fmt(state.P / 1000, 2)} kN</b> at <b data-k="a">${fmt(state.a, 2)} m</b></span>
      <span>Tip deflection <b data-k="tip">${fmt(state.tip * 1000, 1)} mm</b></span>
      <span>Max bending stress <b data-k="sigma">${fmt(state.sigma / 1e6, 0)} MPa</b></span>
      <span>${warn}</span>
      <span class="fine">${m.name}, 40×80 mm section, 2 m span. Euler-Bernoulli, educational model. Deflection drawn ×${fmt(state.k, 1)}, section ×${SEC}.</span>`;
  };
  sliderP.addEventListener('input', () => { state.P = +sliderP.value; state.demo = false; state.interactions++; compute(); });
  selMat.addEventListener('change', () => { state.mat = selMat.value; state.interactions++; compute(); });
  compute();

  const stage = createStage(host, { fov: 38, camPos: [2.6, 1.5, 5.4], target: [1.9, -0.25, 0] });
  if (!stage.ok) return state;
  stage.canvas.setAttribute('aria-label', 'Interactive 3D cantilever beam: drag to move the load');
  stage.canvas.dataset.testid = 'hero-canvas';
  const { scene, camera } = stage;
  scene.add(makeGrid(24, 48).translateY(-1.6));

  // Wall
  const wall = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2.6, 1.4), new THREE.MeshStandardMaterial({ color: 0x1b1f17, roughness: 0.9 }));
  wall.position.set(-0.15, -0.3, 0);
  scene.add(wall);
  const wallEdges = new THREE.LineSegments(new THREE.EdgesGeometry(wall.geometry), new THREE.LineBasicMaterial({ color: 0xeeff41, transparent: true, opacity: 0.35 }));
  wallEdges.position.copy(wall.position);
  scene.add(wallEdges);

  // Beam
  const LU = L * S, HU = h * S * SEC, BU = b * S * SEC;
  const geo = new THREE.BoxGeometry(LU, HU, BU, 160, 8, 4);
  geo.translate(LU / 2, 0, 0);
  const pos = geo.attributes.position;
  const base = Float32Array.from(pos.array);
  const colors = new Float32Array(pos.count * 3);
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const beam = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.45, metalness: 0.15 }));
  scene.add(beam);
  const ghost = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(LU, HU, BU).translate(LU / 2, 0, 0)), new THREE.LineBasicMaterial({ color: 0x55602a, transparent: true, opacity: 0.5 }));
  scene.add(ghost);

  // Bending-moment diagram drawn on the floor-side plane
  const NM = 80;
  const mGeo = new THREE.BufferGeometry();
  mGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array((NM + 1) * 2 * 3), 3));
  const mIdx = [];
  for (let i = 0; i < NM; i++) { const a0 = 2 * i; mIdx.push(a0, a0 + 1, a0 + 2, a0 + 1, a0 + 3, a0 + 2); }
  mGeo.setIndex(mIdx);
  const mMesh = new THREE.Mesh(mGeo, new THREE.MeshBasicMaterial({ color: 0xeeff41, transparent: true, opacity: 0.08, side: THREE.DoubleSide, depthWrite: false }));
  scene.add(mMesh);

  // Load arrow
  const arrow = new THREE.Group();
  const arrowMat = new THREE.MeshStandardMaterial({ color: 0xeeff41, emissive: 0x556010, roughness: 0.4 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1, 12), arrowMat);
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.2, 18), arrowMat);
  head.rotation.x = Math.PI;
  const knob = new THREE.Mesh(new THREE.SphereGeometry(0.09, 20, 14), arrowMat);
  arrow.add(shaft, head, knob);
  scene.add(arrow);

  // Interaction: drag horizontally to move the load; mouse vertical drag also scales the load.
  const ray = new THREE.Raycaster();
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  let dragging = false, lastY = 0;
  const setFromEvent = (ev) => {
    ray.setFromCamera(stage.ndc(ev), camera);
    const hit = new THREE.Vector3();
    if (ray.ray.intersectPlane(plane, hit)) state.a = Math.min(L, Math.max(0.1, hit.x / S));
  };
  stage.canvas.addEventListener('pointerdown', (ev) => {
    dragging = true; state.demo = false; state.interactions++; lastY = ev.clientY;
    stage.canvas.setPointerCapture?.(ev.pointerId);
    setFromEvent(ev); compute();
  });
  stage.canvas.addEventListener('pointermove', (ev) => {
    if (!dragging) return;
    setFromEvent(ev);
    if (ev.pointerType === 'mouse') {
      state.P = Math.min(8000, Math.max(0, state.P + (ev.clientY - lastY) * 25));
      sliderP.value = state.P;
    }
    lastY = ev.clientY;
    compute();
  });
  const end = () => { dragging = false; };
  stage.canvas.addEventListener('pointerup', end);
  stage.canvas.addEventListener('pointercancel', end);

  const col = new THREE.Color();
  stage.onFrame({
    update(dt, t) {
      if (state.demo) {
        state.a = 1.15 + 0.85 * Math.sin(t * 0.6);
        state.P = 2600 + 1800 * Math.sin(t * 0.37 + 1);
        sliderP.value = state.P;
        if (Math.round(t * 10) % 3 === 0) compute();
      }
      const m = BEAM_MATERIALS[state.mat];
      const EI = m.E * I;
      const k = state.k;
      for (let i = 0; i < pos.count; i++) {
        const xu = base[3 * i], yu = base[3 * i + 1], zu = base[3 * i + 2];
        const x = xu / S;
        const r = cantilever(state.P, state.a, x, EI);
        // slope for plane-section rotation
        const dx = 1e-3, r2 = cantilever(state.P, state.a, Math.min(L, x + dx), EI);
        const slope = (r2.w - r.w) / dx;
        pos.array[3 * i] = xu + yu * slope * k;
        pos.array[3 * i + 1] = yu - r.w * S * k;
        pos.array[3 * i + 2] = zu;
        const yPhys = (yu / HU) * h;
        const sigma = (r.M * yPhys) / I;
        utilColor(Math.abs(sigma) / m.sy, col);
        colors[3 * i] = col.r; colors[3 * i + 1] = col.g; colors[3 * i + 2] = col.b;
      }
      pos.needsUpdate = true; geo.attributes.color.needsUpdate = true;
      geo.computeVertexNormals();
      // moment diagram below beam
      const mp = mGeo.attributes.position.array;
      const Mmax = 8000 * L;
      for (let i = 0; i <= NM; i++) {
        const x = (i / NM) * L, M = cantilever(state.P, state.a, x, EI).M;
        const y0 = -0.75, y1 = y0 - (M / Mmax) * 0.8;
        mp.set([x * S, y0, -0.25, x * S, y1, -0.25], i * 6);
      }
      mGeo.attributes.position.needsUpdate = true;
      mGeo.computeBoundingSphere();
      // arrow
      const len = 0.35 + 0.9 * (state.P / 8000);
      const xa = state.a * S, ya = HU / 2 - cantilever(state.P, state.a, state.a, EI).w * S * k;
      shaft.scale.y = len; shaft.position.y = 0.2 + len / 2; head.position.y = 0.1; knob.position.y = 0.2 + len;
      arrow.position.set(xa, ya, 0);
      // camera: gentle sway; pull back on narrow screens
      const wide = window.innerWidth > 900;
      stage.target.set(1.9, wide ? -0.75 : -0.3, 0);
      const dist = wide ? 10.5 : stage.fitDistance(5.0, 2.4, 1.05);
      const ang = Math.sin(t * 0.15) * 0.25 + 0.2;
      camera.position.set(stage.target.x + Math.sin(ang) * dist, stage.target.y + 0.28 * dist, Math.cos(ang) * dist);
      // on wide screens shift the image right so the beam sits beside the headline, not under it
      const W = stage.canvas.width, H = stage.canvas.height;
      if (wide && W) { if (!camera.view || camera.view.offsetX !== -0.16 * W) camera.setViewOffset(W, H, -0.16 * W, 0, W, H); }
      else if (camera.view && camera.view.enabled) camera.clearViewOffset();
      camera.lookAt(stage.target);
    },
  });
  window.__mefs.hero.stage = stage;
  window.__mefs.hero.compute = compute;
  return state;
}
