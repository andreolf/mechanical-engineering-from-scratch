import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import { createStage, utilColor, fmt, paintRange, REDUCED_MOTION } from './stage.js';
import { cantilever, BEAM_MATERIALS } from './physics.js';

// Physical beam: 2 m cantilever, rectangular 40 x 80 mm section. Drawn at 2 units per metre.
const L = 2.0, b = 0.04, h = 0.08, I = (b * h ** 3) / 12, c = h / 2;
const S = 2.0, SEC = 2.0; // world units per metre; section drawn x2 for visibility
const PMAX = 8000;

export function initHero(root) {
  const host = root.querySelector('.hero-canvas');
  const sliderP = root.querySelector('#hero-load');
  const sliderA = root.querySelector('#hero-pos');
  const selMat = root.querySelector('#hero-material');
  const cells = Object.fromEntries([...root.querySelectorAll('[data-k]')].map((e) => [e.dataset.k, e]));
  const note = root.querySelector('#hero-note');
  const state = { P: 2500, a: 1.7, mat: 'steel', demo: !REDUCED_MOTION, tip: 0, sigma: 0, util: 0, k: 1, interactions: 0 };
  window.__mefs = window.__mefs || {};
  window.__mefs.hero = { state };
  const fillP = paintRange(sliderP), fillA = paintRange(sliderA);

  const compute = () => {
    const m = BEAM_MATERIALS[state.mat];
    const EI = m.E * I;
    state.tip = cantilever(state.P, state.a, L, EI).w;
    state.sigma = (state.P * state.a * c) / I;
    state.util = state.sigma / m.sy;
    state.k = state.tip > 0 ? Math.min(5, (0.22 * L) / state.tip) : 5;
    cells.P.textContent = `${fmt(state.P / 1000, 2)} kN`;
    cells.a.textContent = `${fmt(state.a, 2)} m`;
    cells.tip.textContent = `${fmt(state.tip * 1000, 1)} mm`;
    cells.sigma.textContent = `${fmt(state.sigma / 1e6, 0)} MPa`;
    cells.sf.textContent = state.util >= 1 ? 'Yielded' : fmt(1 / Math.max(state.util, 1e-9), 2);
    cells.sf.dataset.state = state.util >= 1 ? 'bad' : state.util > 0.67 ? 'warn' : 'ok';
    cells.mat.textContent = m.name;
    note.textContent = state.util >= 1 ? 'The beam has yielded, so the linear-elastic model no longer applies.'
      : state.tip / L > 0.05 ? 'Deflection is over 5% of the span, so small-deflection theory loses accuracy.'
      : `Euler-Bernoulli beam, 40 × 80 mm section. Deflection drawn ×${fmt(state.k, 1)}.`;
  };
  const stopDemo = () => { if (state.demo) { state.demo = false; } state.interactions++; };
  sliderP.addEventListener('input', () => { state.P = +sliderP.value; stopDemo(); compute(); });
  sliderA.addEventListener('input', () => { state.a = +sliderA.value; stopDemo(); compute(); });
  selMat.addEventListener('change', () => { state.mat = selMat.value; stopDemo(); compute(); });
  compute();

  const stage = createStage(host, { fov: 30, camPos: [3.4, 1.6, 6], target: [2.0, -0.15, 0], orbit: true });
  if (!stage.ok) return state;
  stage.canvas.setAttribute('aria-label', '3D cantilever beam. Drag across it, or use the sliders, to move the load.');
  stage.canvas.dataset.testid = 'hero-canvas';
  const { scene, camera } = stage;
  stage.addFloor(-1.15, 24, 0.6);
  stage.key.position.set(3, 7, 4.5);
  stage.key.target.position.set(2, -0.5, 0);
  const sc = stage.key.shadow.camera; sc.left = -4; sc.right = 4; sc.top = 4; sc.bottom = -4; sc.updateProjectionMatrix();

  const steel = new THREE.MeshPhysicalMaterial({ color: 0x8d9297, metalness: 0.85, roughness: 0.32, clearcoat: 0.2 });
  const darkSteel = new THREE.MeshPhysicalMaterial({ color: 0x3a3d40, metalness: 0.8, roughness: 0.42 });
  // Clamp: base plate, upright, two jaws and bolt heads
  const plate = new THREE.Mesh(new RoundedBoxGeometry(1.1, 0.12, 1.3, 3, 0.03), darkSteel);
  plate.position.set(-0.3, -1.09, 0);
  const upright = new THREE.Mesh(new RoundedBoxGeometry(0.42, 1.0, 0.9, 3, 0.04), darkSteel);
  upright.position.set(-0.27, -0.55, 0);
  const jawGeo = new RoundedBoxGeometry(0.62, 0.2, 0.62, 3, 0.03);
  const jawTop = new THREE.Mesh(jawGeo, steel); jawTop.position.set(-0.08, 0.1 + 0.08 * SEC, 0);
  const jawBot = new THREE.Mesh(jawGeo, steel); jawBot.position.set(-0.08, -0.1 - 0.08 * SEC, 0);
  const clamp = new THREE.Group();
  clamp.add(plate, upright, jawTop, jawBot);
  const boltGeo = new THREE.CylinderGeometry(0.045, 0.045, 0.05, 6);
  for (const x of [-0.28, 0.12]) for (const z of [-0.2, 0.2]) {
    const bolt = new THREE.Mesh(boltGeo, darkSteel); bolt.position.set(x, jawTop.position.y + 0.12, z); clamp.add(bolt);
  }
  clamp.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
  scene.add(clamp);

  // Beam with per-vertex stress colours
  const LU = L * S, HU = h * S * SEC, BU = b * S * SEC;
  const geo = new THREE.BoxGeometry(LU, HU, BU, 160, 8, 4);
  geo.translate(LU / 2, 0, 0);
  const pos = geo.attributes.position;
  const base = Float32Array.from(pos.array);
  const colors = new Float32Array(pos.count * 3);
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const beam = new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({ vertexColors: true, metalness: 0.35, roughness: 0.3, clearcoat: 0.5, clearcoatRoughness: 0.25 }));
  beam.castShadow = true;
  scene.add(beam);
  // undeformed outline (dashed) for comparison
  const ghostPts = [new THREE.Vector3(0, HU / 2, BU / 2), new THREE.Vector3(LU, HU / 2, BU / 2), new THREE.Vector3(LU, -HU / 2, BU / 2), new THREE.Vector3(0, -HU / 2, BU / 2)];
  const ghost = new THREE.Line(new THREE.BufferGeometry().setFromPoints(ghostPts), new THREE.LineDashedMaterial({ color: 0x9a9d93, dashSize: 0.06, gapSize: 0.05, transparent: true, opacity: 0.6 }));
  ghost.computeLineDistances();
  scene.add(ghost);
  // deflection dimension line at the tip (lime), drawn in front of the beam
  const dimMat = new THREE.LineBasicMaterial({ color: 0xeeff41 });
  const dimGeo = new THREE.BufferGeometry();
  dimGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6 * 3), 3));
  const dim = new THREE.LineSegments(dimGeo, dimMat);
  scene.add(dim);

  // Load arrow
  const arrow = new THREE.Group();
  const arrowMat = new THREE.MeshStandardMaterial({ color: 0xeeff41, emissive: 0x6b7a00, emissiveIntensity: 0.35, roughness: 0.35 });
  const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 1, 16), arrowMat);
  const head = new THREE.Mesh(new THREE.ConeGeometry(0.065, 0.18, 24), arrowMat);
  head.rotation.x = Math.PI;
  const grip = new THREE.Mesh(new THREE.TorusGeometry(0.07, 0.018, 12, 32), arrowMat);
  arrow.add(shaft, head, grip);
  arrow.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  scene.add(arrow);

  // Drag across the canvas to move the load. Horizontal only, so vertical swipes still scroll the page on phones.
  const ray = new THREE.Raycaster();
  const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0);
  let dragging = false;
  const setFromEvent = (ev) => {
    ray.setFromCamera(stage.ndc(ev), camera);
    const hit = new THREE.Vector3();
    if (ray.ray.intersectPlane(plane, hit)) { state.a = Math.min(L, Math.max(0.1, hit.x / S)); sliderA.value = state.a; fillA(); }
  };
  stage.canvas.addEventListener('pointerdown', (ev) => { if (stage.orbiting) return; dragging = true; stopDemo(); setFromEvent(ev); compute(); });
  stage.canvas.addEventListener('pointermove', (ev) => { if (!dragging || stage.orbiting) return; setFromEvent(ev); compute(); });
  const end = () => { dragging = false; };
  ['pointerup', 'pointercancel', 'pointerleave'].forEach((t) => stage.canvas.addEventListener(t, end));

  const col = new THREE.Color();
  let lastText = 0;
  stage.onFrame({
    update(dt, t) {
      if (state.demo) {
        state.a = 1.2 + 0.75 * Math.sin(t * 0.55);
        state.P = 2800 + 1700 * Math.sin(t * 0.33 + 1);
        if (t - lastText > 0.12) { sliderP.value = state.P; sliderA.value = state.a; fillP(); fillA(); compute(); lastText = t; }
      }
      const m = BEAM_MATERIALS[state.mat];
      const EI = m.E * I, k = state.k;
      for (let i = 0; i < pos.count; i++) {
        const xu = base[3 * i], yu = base[3 * i + 1], zu = base[3 * i + 2];
        const x = xu / S;
        const r = cantilever(state.P, state.a, x, EI);
        const r2 = cantilever(state.P, state.a, Math.min(L, x + 1e-3), EI);
        const slope = (r2.w - r.w) / 1e-3;
        pos.array[3 * i] = xu + yu * slope * k;
        pos.array[3 * i + 1] = yu - r.w * S * k;
        pos.array[3 * i + 2] = zu;
        const sigma = (r.M * ((yu / HU) * h)) / I;
        utilColor(Math.abs(sigma) / m.sy, col);
        colors[3 * i] = col.r; colors[3 * i + 1] = col.g; colors[3 * i + 2] = col.b;
      }
      pos.needsUpdate = true; geo.attributes.color.needsUpdate = true;
      geo.computeVertexNormals();
      // dimension line: vertical between undeformed and deformed tip, with end ticks
      const tipY = HU / 2 - state.tip * S * k, x0 = LU + 0.18, z0 = BU / 2;
      dimGeo.attributes.position.array.set([x0, HU / 2, z0, x0, tipY, z0, x0 - 0.06, HU / 2, z0, x0 + 0.06, HU / 2, z0, x0 - 0.06, tipY, z0, x0 + 0.06, tipY, z0]);
      dimGeo.attributes.position.needsUpdate = true; dimGeo.computeBoundingSphere();
      // arrow sits on the deflected beam
      const len = 0.3 + 0.8 * (state.P / PMAX);
      const ya = HU / 2 - cantilever(state.P, state.a, state.a, EI).w * S * k;
      shaft.scale.y = len; shaft.position.y = 0.18 + len / 2; head.position.y = 0.09; grip.position.y = 0.2 + len;
      arrow.position.set(state.a * S, ya, 0);
      if (!stage.orbiting) {
        const dist = stage.fitDistance(5.6, 2.9, 1.0);
        const ang = (REDUCED_MOTION ? 0 : Math.sin(t * 0.12) * 0.18) + 0.38;
        stage.target.set(1.85, -0.25, 0);
        camera.position.set(stage.target.x + Math.sin(ang) * dist, stage.target.y + 0.32 * dist, Math.cos(ang) * dist);
        camera.lookAt(stage.target);
      }
    },
  });
  window.__mefs.hero.stage = stage;
  window.__mefs.hero.compute = compute;
  return state;
}
