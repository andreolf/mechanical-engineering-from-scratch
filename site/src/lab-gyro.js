import * as THREE from 'three';
import { createStage, fmt, paintRange, REDUCED_MOTION } from './stage.js';
import { gyroStep } from './physics.js';

// Heavy symmetric gyroscope: 2 kg disc, r = 0.15 m, centre 0.20 m from a frictionless pivot.
const p = { m: 2, g: 9.81, l: 0.2, r: 0.15, c: 0.0 };
p.I3 = 0.5 * p.m * p.r * p.r;
p.I1 = 0.25 * p.m * p.r * p.r + p.m * p.l * p.l;

export function initGyro(root) {
  const host = root.querySelector('.lab-canvas');
  const out = root.querySelector('.lab-readout');
  const banner = root.querySelector('.lab-banner');
  const sSpin = root.querySelector('[name=gyro-spin]');
  const bRelease = root.querySelector('[data-action=gyro-release]');
  const bStop = root.querySelector('[data-action=gyro-stop]');
  const st = { spin: +sSpin.value, s: null, psi: 0, phiRate: 0, tilt: 0, t: 0, prevPhi: null, steps: 0 };
  root.querySelectorAll('input[type=range]').forEach(paintRange);
  window.__mefs = window.__mefs || {};
  window.__mefs.gyro = { state: st, params: p };

  const release = () => {
    st.s = { n: [1, 0, 0], L: [p.I3 * st.spin, 0, 0] }; // axle horizontal, no initial precession -> nutation appears
    st.prevPhi = null; st.t = 0;
  };
  const setSpin = (w) => {
    st.spin = w;
    if (!st.s) return release();
    const n = st.s.n, L = st.s.L, Ln = L[0] * n[0] + L[1] * n[1] + L[2] * n[2];
    st.s.L = L.map((v, i) => v + (p.I3 * w - Ln) * n[i]); // change spin about the axle only
  };
  sSpin.addEventListener('input', () => setSpin(+sSpin.value));
  bRelease.addEventListener('click', () => { st.spin = +sSpin.value; release(); });
  bStop.addEventListener('click', () => { sSpin.value = 0; setSpin(0); });
  release();

  const physicsStep = (dt) => {
    const h = 0.0005; let n = Math.ceil(dt / h);
    for (let k = 0; k < n; k++) st.s = gyroStep(st.s, p, dt / n);
    st.steps += n; st.t += dt;
    const [x, y, z] = st.s.n;
    st.tilt = Math.asin(Math.max(-1, Math.min(1, z))) * 180 / Math.PI; // + above horizontal
    const phi = Math.atan2(y, x);
    if (st.prevPhi !== null && Math.hypot(x, y) > 0.2) {
      let d = phi - st.prevPhi; if (d > Math.PI) d -= 2 * Math.PI; if (d < -Math.PI) d += 2 * Math.PI;
      st.phiRate = st.phiRate * 0.97 + (d / dt) * 0.03;
    }
    st.prevPhi = phi;
    const Ln = st.s.L[0] * x + st.s.L[1] * y + st.s.L[2] * z;
    st.psi += (Ln / p.I3) * dt;
  };
  let lastText = 0;
  const report = (force) => {
    if (!force && performance.now() - lastText < 120) return;
    lastText = performance.now();
    const w3 = st.spin, pred = w3 > 1 ? (p.m * p.g * p.l) / (p.I3 * w3) : NaN;
    const E = 0.5 * p.I3 * w3 * w3;
    out.innerHTML = `<span>Spin <b data-k="spin">${fmt(w3 * 60 / (2 * Math.PI), 0)} rpm</b> · stored energy <b>${fmt(E, 0)} J</b></span>
      <span>Precession measured <b data-k="prec">${fmt(Math.abs(st.phiRate), 2)} rad/s</b> · fast-top formula mgl/(I₃ω) <b>${isNaN(pred) ? '—' : fmt(pred, 2) + ' rad/s'}</b></span>
      <span>Axle tilt <b data-k="tilt">${fmt(st.tilt, 1)}°</b> from horizontal</span>
      <span class="fine">Rigid symmetric top, frictionless pivot, RK4 on dL/dt = τ. Educational model: no bearing friction or air drag.</span>`;
    if (w3 < 20) { banner.className = 'lab-banner bad'; banner.textContent = 'Spin too low: angular momentum cannot resist gravity\'s torque. It falls and swings.'; }
    else if (w3 < 80) { banner.className = 'lab-banner warn'; banner.textContent = 'Slow spin: big nodding (nutation) and fast precession.'; }
    else { banner.className = 'lab-banner ok'; banner.textContent = 'Fast spin: torque turns L sideways instead of tipping it. It precesses.'; }
  };
  window.__mefs.gyro.report = report;

  const stage = createStage(host, { fov: 40, camPos: [0.9, 1.3, 1.25], target: [0.05, 0.92, 0] });
  if (!stage.ok) {
    // still run physics so the numbers respond without WebGL
    setInterval(() => { physicsStep(1 / 30); report(); }, 33);
    return;
  }
  stage.canvas.dataset.testid = 'gyro-canvas';
  stage.canvas.setAttribute('aria-label', '3D gyroscope precessing on a pivot');
  const { scene, camera } = stage;
  stage.addFloor(0, 8, 0.6);
  const sc = stage.key.shadow.camera; sc.left = -1.5; sc.right = 1.5; sc.top = 1.5; sc.bottom = -1.5; sc.updateProjectionMatrix();
  const steel = new THREE.MeshPhysicalMaterial({ color: 0x9aa0a6, metalness: 0.9, roughness: 0.28 });
  const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.05, 1.0, 16), steel);
  tower.position.y = 0.5; scene.add(tower);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.25, 0.04, 32), new THREE.MeshStandardMaterial({ color: 0x1a1d16 }));
  base.position.y = 0.02; scene.add(base);
  const pivot = new THREE.Group(); pivot.position.y = 1.0; scene.add(pivot);
  const body = new THREE.Group(); pivot.add(body); // body local +X is the axle
  const axle = new THREE.Mesh(new THREE.CylinderGeometry(0.008, 0.008, p.l + 0.05, 10), steel);
  axle.rotation.z = -Math.PI / 2; axle.position.x = (p.l + 0.05) / 2; body.add(axle);
  const wheel = new THREE.Group(); wheel.position.x = p.l; body.add(wheel);
  const disc = new THREE.Mesh(new THREE.CylinderGeometry(p.r, p.r, 0.03, 48), new THREE.MeshPhysicalMaterial({ color: 0x5b6066, metalness: 0.9, roughness: 0.25, clearcoat: 0.4 }));
  disc.rotation.z = -Math.PI / 2; wheel.add(disc);
  const rim = new THREE.Mesh(new THREE.TorusGeometry(p.r, 0.012, 10, 64), new THREE.MeshStandardMaterial({ color: 0xeeff41, emissive: 0x334000 }));
  rim.rotation.y = Math.PI / 2; wheel.add(rim);
  for (let k = 0; k < 3; k++) { // spokes so spin is visible
    const sp = new THREE.Mesh(new THREE.BoxGeometry(0.035, 2 * p.r * 0.95, 0.012), new THREE.MeshStandardMaterial({ color: 0xeeff41 }));
    sp.rotation.x = (k * Math.PI) / 3; wheel.add(sp);
  }
  scene.traverse((o) => { if (o.isMesh) { o.castShadow = true; } });
  const Larrow = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 0.4, 0xeeff41, 0.06, 0.04);
  const Tarrow = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, 0, 0), 0.2, 0xff5a3c, 0.05, 0.035);
  pivot.add(Larrow, Tarrow);
  const trailN = 400, trailPos = new Float32Array(trailN * 3), trailGeo = new THREE.BufferGeometry();
  trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPos, 3));
  const trail = new THREE.Line(trailGeo, new THREE.LineBasicMaterial({ color: 0xeeff41, transparent: true, opacity: 0.45 }));
  pivot.add(trail); let trailI = 0;

  // world z-up physics -> three y-up: (x, y, z)_phys -> (x, z, -y)_three
  const toThree = (v) => new THREE.Vector3(v[0], v[2], -v[1]);
  const q = new THREE.Quaternion(), qs = new THREE.Quaternion(), X = new THREE.Vector3(1, 0, 0);
  stage.onFrame((dt, t) => {
    physicsStep(dt);
    report();
    const n3 = toThree(st.s.n).normalize();
    q.setFromUnitVectors(X, n3);
    body.quaternion.copy(q);
    qs.setFromAxisAngle(X, st.psi % (2 * Math.PI));
    wheel.quaternion.copy(qs);
    const L3 = toThree(st.s.L), Lm = L3.length();
    Larrow.visible = Lm > 1e-3;
    if (Larrow.visible) { Larrow.setDirection(L3.clone().normalize()); Larrow.setLength(0.12 + Math.min(0.5, Lm * 0.06), 0.06, 0.04); }
    const tau = new THREE.Vector3(0, 1, 0).cross(n3); // l n x (-m g Y) points along Y x n
    Tarrow.setDirection(tau.clone().normalize()); Tarrow.position.copy(n3.clone().multiplyScalar(p.l));
    const tip = n3.clone().multiplyScalar(p.l + 0.02);
    trailPos.set([tip.x, tip.y, tip.z], (trailI % trailN) * 3); trailI++;
    trailGeo.setDrawRange(0, Math.min(trailI, trailN)); trailGeo.attributes.position.needsUpdate = true;
    const dist = stage.fitDistance(0.85, 0.8, 1.1);
    const a = REDUCED_MOTION ? 0 : t * 0.1;
    if (!stage.orbiting) { camera.position.set(Math.sin(a + 0.6) * dist, 0.92 + 0.35 * dist, Math.cos(a + 0.6) * dist); camera.lookAt(stage.target); }
  });
}
