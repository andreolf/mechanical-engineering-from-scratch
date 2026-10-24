import * as THREE from 'three';
import { createStage, fmt, utilColor, paintRange, REDUCED_MOTION } from './stage.js';
import { pipeState, venturiRadius, WATER } from './physics.js';

// Horizontal venturi: D = 100 mm pipe, 2 m long, variable throat. Drawn at 3 units per metre.
const D = 0.1, LEN = 2.0, S = 3.0, P1 = 200e3; // inlet absolute pressure 200 kPa
const RS = 2.5; // radii drawn x2.5 so the flow is visible

export function initPipe(root) {
  const host = root.querySelector('.lab-canvas');
  const out = root.querySelector('.lab-readout');
  const banner = root.querySelector('.lab-banner');
  const sQ = root.querySelector('[name=pipe-q]');
  const sD = root.querySelector('[name=pipe-d]');
  const cF = root.querySelector('[name=pipe-friction]');
  const st = { Q: +sQ.value / 1000, d: +sD.value / 1000, friction: cF.checked, res: null };
  root.querySelectorAll('input[type=range]').forEach(paintRange);
  window.__mefs = window.__mefs || {};
  window.__mefs.pipe = { state: st };
  let geomDirty = true;
  const compute = () => {
    st.res = pipeState({ Q: st.Q, D, d: st.d, p1: P1, friction: st.friction, len: LEN });
    const r = st.res;
    out.innerHTML = `<span>Inlet speed <b data-k="u1">${fmt(r.U1, 2)} m/s</b> · throat speed <b data-k="ut">${fmt(r.Ut, 2)} m/s</b></span>
      <span>Throat pressure <b data-k="pt">${fmt(r.pt / 1000, 1)} kPa abs</b>${r.pt < 0 ? ' <b class="bad">(negative: non-physical, model broken)</b>' : ''} · outlet <b>${fmt(r.p2 / 1000, 1)} kPa</b> · Re ≈ <b>${fmt(r.Re1, 0)}</b></span>
      <span class="fine">1D steady incompressible Bernoulli, water at 20 °C, inlet 200 kPa abs, diameters drawn ×2.5. Friction uses Darcy-Weisbach with an assumed f = 0.02 and ignores diffuser separation losses. Educational model.</span>`;
    if (r.cavitating) { banner.className = 'lab-banner bad'; banner.textContent = 'Cavitation: the model predicts pressure below water\'s vapour pressure (~2.3 kPa). Real water boils into bubbles here and Bernoulli stops being valid.'; }
    else if (r.pt < 40e3) { banner.className = 'lab-banner warn'; banner.textContent = 'Getting close: throat pressure is dropping toward vapour pressure.'; }
    else { banner.className = 'lab-banner ok'; banner.textContent = 'Same flow rate through a smaller area means faster water and lower pressure.'; }
  };
  sQ.addEventListener('input', () => { st.Q = +sQ.value / 1000; compute(); });
  sD.addEventListener('input', () => { st.d = +sD.value / 1000; geomDirty = true; compute(); });
  cF.addEventListener('change', () => { st.friction = cF.checked; compute(); });
  compute();

  const stage = createStage(host, { fov: 38, camPos: [3, 2.2, 5.6], target: [3, 0.9, 0], shadows: false });
  if (!stage.ok) return;
  stage.canvas.dataset.testid = 'pipe-canvas';
  stage.canvas.setAttribute('aria-label', '3D venturi pipe with flowing particles and pressure gauges');
  const { scene, camera } = stage;
  const LU = LEN * S;
  // pipe wall (lathe), rebuilt when the throat changes
  const wallMat = new THREE.MeshPhysicalMaterial({ color: 0x9fdcff, transparent: true, opacity: 0.16, roughness: 0.1, side: THREE.DoubleSide, depthWrite: false });
  const ringMat = new THREE.LineBasicMaterial({ color: 0xeeff41, transparent: true, opacity: 0.35 });
  let wall = null, rings = null;
  const buildWall = () => {
    if (wall) { scene.remove(wall); wall.geometry.dispose(); scene.remove(rings); rings.geometry.dispose(); }
    const pts = [];
    for (let i = 0; i <= 120; i++) { const x = (i / 120) * LEN; pts.push(new THREE.Vector2(venturiRadius(x, D / 2, st.d / 2, LEN) * S * RS, x * S)); }
    const g = new THREE.LatheGeometry(pts, 48);
    g.rotateZ(-Math.PI / 2); // lathe axis y -> x
    wall = new THREE.Mesh(g, wallMat); scene.add(wall);
    const rp = [];
    for (let i = 0; i <= 24; i++) {
      const x = (i / 24) * LEN, R = venturiRadius(x, D / 2, st.d / 2, LEN) * S * RS;
      for (let k = 0; k < 32; k++) {
        const a0 = (k / 32) * Math.PI * 2, a1 = ((k + 1) / 32) * Math.PI * 2;
        rp.push(x * S, Math.cos(a0) * R, Math.sin(a0) * R, x * S, Math.cos(a1) * R, Math.sin(a1) * R);
      }
    }
    const rg = new THREE.BufferGeometry(); rg.setAttribute('position', new THREE.Float32BufferAttribute(rp, 3));
    rings = new THREE.LineSegments(rg, ringMat); scene.add(rings);
    geomDirty = false;
  };
  // manometer tubes at inlet, throat, outlet (height = gauge pressure head, scaled)
  const tubeX = [0.15 * LEN, 0.5 * LEN, 0.92 * LEN];
  const tubes = tubeX.map((x) => {
    const g = new THREE.Group();
    const glass = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 2.2, 16, 1, true), new THREE.MeshPhysicalMaterial({ color: 0xffffff, transparent: true, opacity: 0.12, side: THREE.DoubleSide, depthWrite: false }));
    glass.position.y = 1.1; g.add(glass);
    const col = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 1, 16), new THREE.MeshStandardMaterial({ color: 0x41d9ff, emissive: 0x0a3040 }));
    col.geometry.translate(0, 0.5, 0); g.add(col);
    g.position.set(x * S, D / 2 * S * RS, 0); scene.add(g);
    return { g, col, x };
  });
  // particles keep fractional radius rho and angle; axial position advances with local mean speed
  const isMobile = matchMedia('(max-width: 600px)').matches;
  const NP = isMobile ? 700 : 1600;
  const pr = new Float32Array(NP), pa = new Float32Array(NP), px = new Float32Array(NP);
  for (let i = 0; i < NP; i++) { pr[i] = Math.sqrt(Math.random()) * 0.92; pa[i] = Math.random() * Math.PI * 2; px[i] = Math.random() * LEN; }
  const pGeo = new THREE.BufferGeometry();
  const pPos = new Float32Array(NP * 3), pCol = new Float32Array(NP * 3);
  pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
  pGeo.setAttribute('color', new THREE.BufferAttribute(pCol, 3));
  const pts = new THREE.Points(pGeo, new THREE.PointsMaterial({ size: isMobile ? 0.05 : 0.04, vertexColors: true, transparent: true, opacity: 0.95 }));
  scene.add(pts);
  // cavitation bubbles
  const NB = 160, bGeo = new THREE.BufferGeometry(), bPos = new Float32Array(NB * 3);
  bGeo.setAttribute('position', new THREE.BufferAttribute(bPos, 3));
  const bubbles = new THREE.Points(bGeo, new THREE.PointsMaterial({ size: 0.09, color: 0xffffff, transparent: true, opacity: 0.8 }));
  scene.add(bubbles);
  const col = new THREE.Color();
  stage.onFrame((dt, t) => {
    if (geomDirty) buildWall();
    const r = st.res, vis = 0.35; // visual time scale: particles move at 0.35x real speed
    const umax = Math.max(r.Ut, 0.1);
    for (let i = 0; i < NP; i++) {
      const R = venturiRadius(px[i], D / 2, st.d / 2, LEN);
      const u = st.Q / (Math.PI * R * R);
      px[i] += u * dt * vis;
      if (px[i] > LEN) { px[i] -= LEN; }
      const RR = venturiRadius(px[i], D / 2, st.d / 2, LEN) * S * RS * pr[i];
      pPos[3 * i] = px[i] * S; pPos[3 * i + 1] = Math.cos(pa[i]) * RR; pPos[3 * i + 2] = Math.sin(pa[i]) * RR;
      utilColor(0.2 + 0.8 * (u / umax), col);
      pCol[3 * i] = col.r; pCol[3 * i + 1] = col.g; pCol[3 * i + 2] = col.b;
    }
    pGeo.attributes.position.needsUpdate = true; pGeo.attributes.color.needsUpdate = true;
    bubbles.visible = r.cavitating;
    if (r.cavitating) {
      for (let i = 0; i < NB; i++) {
        const x = 0.45 * LEN + ((i * 0.618 + t * 0.6) % 1) * 0.35 * LEN;
        const R = venturiRadius(x, D / 2, st.d / 2, LEN) * S * RS * 0.8, a = i * 2.4 + t;
        bPos.set([x * S, Math.cos(a) * R * ((i % 7) / 7), Math.sin(a) * R * ((i % 5) / 5)], i * 3);
      }
      bGeo.attributes.position.needsUpdate = true;
    }
    tubes.forEach((tb) => {
      const idx = Math.round((tb.x / LEN) * (r.p.length - 1));
      const head = Math.max(0.001, (r.p[idx] - WATER.pv) / (WATER.rho * 9.81)); // absolute head above vapour pressure (m)
      tb.col.scale.y = Math.min(2.2, head * 0.1); // 1 unit = 10 m head
      tb.col.material.color.set(r.p[idx] < WATER.pv ? 0xff3b2f : 0x41d9ff);
    });
    const dist = stage.fitDistance(6.6, 3.2, 1.05);
    const a = REDUCED_MOTION ? 0 : Math.sin(t * 0.13) * 0.3;
    if (!stage.orbiting) { camera.position.set(3 + Math.sin(a) * dist, 0.6 + 0.3 * dist, Math.cos(a) * dist); camera.lookAt(stage.target); }
  });
}
