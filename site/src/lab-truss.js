import * as THREE from 'three';
import { createStage, fmt, paintRange, REDUCED_MOTION } from './stage.js';
import { solveTruss } from './physics.js';

// 12 m steel truss bridge, 6 panels x 2 m, 2 m deep, cross-braced inner panels (4 redundant members).
const E = 210e9, A = 1.0e-3, I = 5.0e-7, SY = 235e6;
const NY = SY * A; // axial yield force
function buildBridge() {
  const nodes = [];
  for (let i = 0; i <= 6; i++) nodes.push({ x: 2 * i, y: 0, fx: i === 0, fy: i === 0 || i === 6 });
  for (let i = 1; i <= 5; i++) nodes.push({ x: 2 * i, y: 2, fx: false, fy: false });
  const top = (i) => 6 + i; // top node above bottom i (1..5)
  const M = [];
  const add = (a, b, kind) => M.push({ a, b, kind, EA: E * A, alive: true, failed: false });
  for (let i = 0; i < 6; i++) add(i, i + 1, 'bottom chord');
  for (let i = 1; i < 5; i++) add(top(i), top(i + 1), 'top chord');
  for (let i = 1; i <= 5; i++) add(i, top(i), 'vertical');
  add(0, top(1), 'end diagonal'); add(6, top(5), 'end diagonal');
  for (let i = 1; i < 5; i++) { add(i, top(i + 1), 'diagonal'); add(i + 1, top(i), 'diagonal'); }
  return { nodes, members: M };
}

export function initTruss(root) {
  const host = root.querySelector('.lab-canvas');
  const out = root.querySelector('.lab-readout');
  const banner = root.querySelector('.lab-banner');
  const sLoad = root.querySelector('[name=truss-load]');
  const sPos = root.querySelector('[name=truss-pos]');
  const bReset = root.querySelector('[data-action=truss-reset]');
  const bAuto = root.querySelector('[data-action=truss-autofail]');
  let { nodes, members } = buildBridge();
  const st = { load: +sLoad.value * 1000, pos: +sPos.value, res: null, removed: 0, failedCount: 0, mechanism: false, autoFail: true, collapse: 0, maxUtil: 0, solves: 0 };
  root.querySelectorAll('input[type=range]').forEach(paintRange);
  window.__mefs = window.__mefs || {};
  const api = (window.__mefs.truss = { state: st, members: () => members.map((m, i) => ({ i, alive: m.alive, kind: m.kind })) });

  const util = (m, N) => {
    const Lm = Math.hypot(nodes[m.b].x - nodes[m.a].x, nodes[m.b].y - nodes[m.a].y);
    const Pcr = (Math.PI ** 2 * E * I) / (Lm * Lm);
    return N >= 0 ? N / NY : -N / Math.min(NY, Pcr);
  };
  let failTimer = null;
  const solve = () => {
    const alive = members.filter((m) => m.alive);
    const loads = new Float64Array(nodes.length * 2);
    // truck load split linearly between the two nearest deck nodes
    const xp = st.pos * 12, i0 = Math.min(5, Math.floor(xp / 2)), t = xp / 2 - i0;
    loads[2 * i0 + 1] -= st.load * (1 - t);
    loads[2 * (i0 + 1) + 1] -= st.load * t;
    const r = solveTruss(nodes, alive, loads);
    st.solves++;
    st.mechanism = r.mechanism;
    st.res = { u: r.u, N: new Map(alive.map((m, k) => [m, r.forces[k]])) };
    let maxU = 0, worst = null;
    for (const [m, N] of st.res.N) { const uu = util(m, N); if (uu > maxU) { maxU = uu; worst = m; } }
    st.maxUtil = r.mechanism ? Infinity : maxU;
    const midDefl = -r.u[2 * 3 + 1];
    if (r.mechanism) {
      banner.className = 'lab-banner bad';
      banner.textContent = 'Mechanism: no load path left. The bridge folds (collapse mode shown is illustrative).';
    } else if (maxU > 1) {
      banner.className = 'lab-banner bad';
      banner.textContent = `Member overloaded (${worst.kind}, ${fmt(maxU * 100, 0)}% of capacity)${st.autoFail ? ': it fails, load redistributes…' : ''}`;
    } else {
      banner.className = 'lab-banner ok';
      banner.textContent = st.removed ? `Still standing. Load found another path through ${alive.length} members.` : 'Tap or click a member to delete it.';
    }
    out.innerHTML = `<span>Members <b data-k="alive">${alive.length}</b>/25 · removed <b data-k="removed">${st.removed}</b> · failed <b>${st.failedCount}</b></span>
      <span>Max utilisation <b data-k="util">${r.mechanism ? '∞' : fmt(maxU * 100, 0) + '%'}</b> · midspan deflection <b>${r.mechanism ? '—' : fmt(midDefl * 1000, 1) + ' mm'}</b></span>
      <span class="fine">Pin-jointed steel bars (A = 10 cm², yield 235 MPa, Euler buckling for compression), direct stiffness method, linear-elastic. Educational model; real bridges have rigid joints, dynamics and codes.</span>`;
    clearTimeout(failTimer);
    if (!r.mechanism && maxU > 1 && st.autoFail && worst) {
      failTimer = setTimeout(() => { worst.alive = false; worst.failed = true; st.failedCount++; solve(); }, 650);
    }
    if (r.mechanism) st.collapse = Math.max(st.collapse, 0.0001); else st.collapse = 0;
  };
  api.removeMember = (i) => { if (members[i].alive) { members[i].alive = false; st.removed++; solve(); } };
  sLoad.addEventListener('input', () => { st.load = +sLoad.value * 1000; solve(); });
  sPos.addEventListener('input', () => { st.pos = +sPos.value; solve(); });
  bAuto.addEventListener('click', () => { st.autoFail = !st.autoFail; bAuto.setAttribute('aria-pressed', st.autoFail); bAuto.textContent = st.autoFail ? 'Progressive failure: on' : 'Progressive failure: off'; solve(); });
  bReset.addEventListener('click', () => { ({ nodes, members } = buildBridge()); st.removed = 0; st.failedCount = 0; st.collapse = 0; rebuildMeshes?.(); solve(); });
  solve();

  const stage = createStage(host, { fov: 36, camPos: [6, 3.2, 15], target: [6, 0.8, 0] });
  let rebuildMeshes = null;
  if (!stage.ok) return;
  stage.canvas.dataset.testid = 'truss-canvas';
  stage.canvas.setAttribute('aria-label', '3D truss bridge: click members to delete them');
  const { scene, camera } = stage;
  stage.addFloor(-2.2, 44, 0.5);
  stage.key.position.set(8, 14, 9); stage.key.target.position.set(6, 0, 0);
  { const sc = stage.key.shadow.camera; sc.left = -12; sc.right = 12; sc.top = 12; sc.bottom = -12; sc.far = 60; sc.updateProjectionMatrix(); }
  // abutments
  for (const x of [-0.6, 12.6]) {
    const ab = new THREE.Mesh(new THREE.BoxGeometry(1.2, 2.2, 3), new THREE.MeshStandardMaterial({ color: 0x23261f, roughness: 1 }));
    ab.position.set(x, -1.1 - 0.05, 0); ab.castShadow = ab.receiveShadow = true; scene.add(ab);
  }
  // river
  const water = new THREE.Mesh(new THREE.PlaneGeometry(11.4, 6), new THREE.MeshStandardMaterial({ color: 0x0a2a33, roughness: 0.2, metalness: 0.3, transparent: true, opacity: 0.85 }));
  water.rotation.x = -Math.PI / 2; water.position.set(6, -2.0, 0); scene.add(water);
  const deck = new THREE.Mesh(new THREE.BoxGeometry(12, 0.06, 1.6), new THREE.MeshStandardMaterial({ color: 0x2b2f26, transparent: true, opacity: 0.7 }));
  scene.add(deck);
  const truck = new THREE.Group();
  const tb = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.7, 0.9), new THREE.MeshStandardMaterial({ color: 0xeeff41, roughness: 0.5 }));
  tb.position.y = 0.45; tb.castShadow = true; truck.add(tb);
  const cab = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.5, 0.9), new THREE.MeshStandardMaterial({ color: 0xc8d636 }));
  cab.position.set(0.95, 0.35, 0); truck.add(cab);
  scene.add(truck);

  const unit = new THREE.CylinderGeometry(1, 1, 1, 10, 1);
  unit.translate(0, 0.5, 0);
  const sph = new THREE.SphereGeometry(0.11, 14, 10);
  let memberMeshes = [], nodeMeshes = [], planeMeshes = [];
  const nodeMat = new THREE.MeshStandardMaterial({ color: 0xd9d9d9, roughness: 0.4 });
  rebuildMeshes = () => {
    [...memberMeshes, ...nodeMeshes].forEach((m) => m.parent && m.parent.remove(m));
    memberMeshes = []; nodeMeshes = []; planeMeshes = [];
    for (const z of [-0.75, 0.75]) {
      members.forEach((m, i) => {
        const mesh = new THREE.Mesh(unit, new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.38, metalness: 0.45 }));
        mesh.userData = { i, z }; mesh.castShadow = true; scene.add(mesh); memberMeshes.push(mesh);
      });
      nodes.forEach((n, i) => { const s = new THREE.Mesh(sph, nodeMat); s.userData = { i, z }; scene.add(s); nodeMeshes.push(s); });
    }
    // cross ties between the two truss planes (visual only)
  };
  rebuildMeshes();
  const tension = new THREE.Color(0x41d9ff), comp = new THREE.Color(0xff6a2a), idle = new THREE.Color(0x777777), tmp = new THREE.Color();
  const P = (i, z, mag, t) => {
    const n = nodes[i];
    let x = n.x, y = n.y;
    if (st.res) {
      x += st.res.u[2 * i] * mag; y += st.res.u[2 * i + 1] * mag;
    }
    return new THREE.Vector3(x, y, z);
  };
  const up = new THREE.Vector3(0, 1, 0);
  api.memberScreen = (i) => {
    const m = members[i];
    const mid = P(m.a, 0.75, 1, 0).add(P(m.b, 0.75, 1, 0)).multiplyScalar(0.5);
    return stage.toScreen(mid);
  };
  api.stage = stage;
  // picking
  const ray = new THREE.Raycaster();
  let downAt = null;
  stage.canvas.addEventListener('pointerdown', (ev) => { downAt = { x: ev.clientX, y: ev.clientY }; });
  stage.canvas.addEventListener('pointerup', (ev) => {
    if (!downAt || Math.hypot(ev.clientX - downAt.x, ev.clientY - downAt.y) > 12) return;
    ray.setFromCamera(stage.ndc(ev), camera);
    const hits = ray.intersectObjects(memberMeshes.filter((m) => m.visible), false);
    let pick = hits[0]?.object.userData.i;
    if (pick === undefined) {
      // forgiving touch target: nearest member midpoint within 28 px
      let best = 28;
      members.forEach((m, i) => { if (!m.alive) return; const s = api.memberScreen(i); const d = Math.hypot(s.x - ev.clientX, s.y - ev.clientY); if (d < best) { best = d; pick = i; } });
    }
    if (pick !== undefined) api.removeMember(pick);
  });
  let hover = -1;
  stage.canvas.addEventListener('pointermove', (ev) => {
    if (ev.pointerType !== 'mouse') return;
    ray.setFromCamera(stage.ndc(ev), camera);
    const hits = ray.intersectObjects(memberMeshes.filter((m) => m.visible), false);
    hover = hits[0]?.object.userData.i ?? -1;
    stage.canvas.style.cursor = hover >= 0 ? 'pointer' : 'default';
  });

  stage.onFrame((dt, t) => {
    const mag = st.mechanism ? 0 : 60; // displacement magnification for display
    if (st.mechanism) st.collapse = Math.min(1, st.collapse + dt * 0.8);
    // collapse: move nodes along the normalised mechanism mode
    let modeScale = 0;
    if (st.mechanism && st.res) {
      let mx = 0; for (let k = 0; k < st.res.u.length; k++) mx = Math.max(mx, Math.abs(st.res.u[k]));
      modeScale = mx > 0 ? (1.6 * (1 - Math.cos(st.collapse * Math.PI)) / 2) / mx : 0;
    }
    const pos = (i, z) => P(i, z, st.mechanism ? modeScale : mag, t);
    memberMeshes.forEach((mesh) => {
      const { i, z } = mesh.userData, m = members[i];
      mesh.visible = m.alive;
      if (!m.alive) return;
      const a = pos(m.a, z), b = pos(m.b, z), d = b.clone().sub(a), len = d.length();
      mesh.position.copy(a);
      mesh.quaternion.setFromUnitVectors(up, d.normalize());
      const N = st.res?.N.get(m) ?? 0, uu = st.mechanism ? 1 : Math.min(1.2, util(m, N));
      mesh.scale.set(0.06, len, 0.06);
      tmp.copy(idle).lerp(N >= 0 ? tension : comp, Math.min(1, uu * 1.4 + 0.15));
      if (st.mechanism) tmp.setRGB(1, 0.15 + 0.1 * Math.sin(t * 10), 0.1);
      if (uu > 1) tmp.setRGB(1, 0.1, 0.1).multiplyScalar(0.7 + 0.3 * Math.sin(t * 20));
      if (i === hover) tmp.set(0xffffff);
      mesh.material.color.copy(tmp);
      mesh.material.emissive?.copy(tmp).multiplyScalar(0.18);
    });
    nodeMeshes.forEach((s) => s.position.copy(pos(s.userData.i, s.userData.z)));
    const xp = st.pos * 12;
    const i0 = Math.min(5, Math.floor(xp / 2)), tt = xp / 2 - i0;
    const ya = pos(i0, 0).y * (1 - tt) + pos(i0 + 1, 0).y * tt;
    truck.position.set(xp - 0.5, ya + 0.03, 0);
    deck.position.set(6, (pos(3, 0).y + 0) / 2 - 0.03, 0);
    const dist = stage.fitDistance(15, 6, 1.05);
    const ang = REDUCED_MOTION ? 0.15 : Math.sin(t * 0.12) * 0.3;
    if (!stage.orbiting) { camera.position.set(6 + Math.sin(ang) * dist, 0.8 + 0.22 * dist, Math.cos(ang) * dist); camera.lookAt(stage.target); }
  });
}
