// Take-apart lab: a two-stage spur reducer. The input stage is the 18 : 45 module-2 pair worked in lesson 15.08; the
// output stage has the same tooth counts at module 3, because it carries 2.5 times the torque (15.09: bigger teeth are
// stronger). Speeds and torques follow from the tooth counts. No lesson gives a mesh efficiency, so the train is ideal.
import * as THREE from 'three';
import { takeApart } from './takeapart/engine.js';
import { gearGeometry } from './takeapart/gear.js';
import { mesh, grp, ringGeo, cylZ, bearing, bolt } from './takeapart/kit.js';
import { findThePart } from './takeapart/quiz.js';

const LIME = '#eeff41', CORAL = '#ff6b81', AMBER = '#ffb547', CYAN = '#5cc8ff';
const L = (id, t) => [id, t];
const LES = {
  fits: L('15.03', 'Tolerances and fits'), shaft: L('15.04', 'Shaft design'), keys: L('15.05', 'Keys, splines and press fits'),
  roll: L('15.06', 'Rolling bearings'), lube: L('15.07', 'Plain bearings and lubrication'), geom: L('15.08', 'Gear geometry'),
  str: L('15.09', 'Gear strength'), trains: L('15.10', 'Gear trains and planetary gears'), bolts: L('15.12', 'Bolted joints'), gas: L('10.02', 'The ideal gas'),
};
const Z1 = 18, Z2 = 45, Z3 = 18, Z4 = 45; // tooth counts
const M1 = 0.02, M2 = 0.03; // modules in model units (1 unit = 100 mm): 2 mm and 3 mm
const R1 = Z2 / Z1, R2 = Z4 / Z3, RT = R1 * R2; // 2.5, 2.5, 6.25
const RP1 = (2 * Z1) / 2 / 1000, RP3 = (3 * Z3) / 2 / 1000; // pinion pitch radii in m: 18 mm and 27 mm
const RPM0 = 1500, TQ0 = 19.1; // the 15.09 example: 3 kW into an 18-tooth pinion at 1500 rpm is 19.1 N·m
const INFO = {
  base: { name: 'Housing, lower half', kicker: 'Housing', what: 'Holds the six bearings in line and carries the oil the gears run in. It splits on the shaft line so the shafts drop straight in. The front wall is cut away here so you can watch the mesh.', spec: ['Bearing seats machined to 25 H7/k6: from 15 μm interference to 19 μm clearance, so the ring is located but still removable (15.03)'], lessons: [LES.fits] },
  cover: { name: 'Housing, upper half', kicker: 'Housing', what: 'The other half of the split housing, with an inspection window over the mesh. Its bearing bores are machined together with the lower half’s so the shafts line up.', spec: [], lessons: [LES.fits] },
  win: { name: 'Inspection window', kicker: 'Housing', what: 'A cover over the mesh so you can check the teeth without opening the box.', spec: [], lessons: [LES.geom] },
  shaftIn: { name: 'Input shaft', kicker: 'Shafts & bearings', what: 'Brings the motor torque in and carries the 18-tooth input pinion.', spec: ['The 15.09 example: 3 kW into an 18-tooth pinion at 1500 rpm is 19.1 N·m', 'Torque on a solid shaft gives τ = 16T / πd³ (06.14)'], lessons: [LES.shaft, L('06.14', 'Torsion of circular shafts')] },
  shaftMid: { name: 'Countershaft', kicker: 'Shafts & bearings', what: 'Carries the 45-tooth input-stage gear and the output-stage pinion. It turns 2.5 times slower than the input and carries 2.5 times the torque.', spec: ['15.04 sizes a gearbox countershaft for 150 N·m in 1045 steel at a safety factor of 2: d = 31.84 mm', 'Shoulders raise the stress: K_f = 1.7 in bending, 1.5 in torsion (15.04)'], lessons: [LES.shaft] },
  shaftOut: { name: 'Output shaft', kicker: 'Shafts & bearings', what: 'Turns 6.25 times slower than the input and, with no losses, carries 6.25 times the torque.', spec: ['3 kW at 1500 rpm in: 240 rpm and 119.4 N·m out, ideal'], lessons: [LES.shaft, LES.trains] },
  p1: { name: 'Input pinion · 18 teeth', kicker: 'Input stage', what: 'Drives the 45-tooth gear. The smaller gear of a pair does more turns, so its teeth see more load cycles and usually fail first.', spec: ['Module 2 mm, 20°: pitch radius 18 mm, 63 mm between centres (15.08)', 'Contact ratio 1.633: one to two tooth pairs carry the load at all times (15.08)', 'At 1500 rpm and 3 kW with a 20 mm face: 125.6 MPa bending, 825 MPa contact (15.09)'], lessons: [LES.geom, LES.str] },
  g2: { name: 'Input gear · 45 teeth', kicker: 'Input stage', what: 'Takes the drive from the pinion and turns at 18/45 of its speed.', spec: ['Pitch radius 45 mm, base radius 42.2862 mm (15.08)', 'Ratio 45 / 18 = 2.5 : 1'], lessons: [LES.geom] },
  p3: { name: 'Output pinion · 18 teeth', kicker: 'Output stage', what: 'Same tooth count as the input pinion, bigger teeth: this stage carries 2.5 times the torque.', spec: ['Module 3 mm, so 94.5 mm between centres', 'In 15.09 the same 18-tooth pinion drops from 125.6 to 64.7 MPa bending going from module 2 to 3', 'Face widths are usually kept between 8 and 16 modules (15.09)'], lessons: [LES.str, LES.geom] },
  g4: { name: 'Output gear · 45 teeth', kicker: 'Output stage', what: 'The last gear in the train. Its shaft turns at 1/6.25 of the input speed.', spec: ['Overall ratio (45/18) × (45/18) = 6.25 : 1', 'Ratio of a simple train: the product of driven over driver teeth'], lessons: [LES.geom, LES.trains] },
  brg: { name: 'Deep-groove ball bearing', kicker: 'Shafts & bearings', qty: 6, what: 'Locates each shaft and carries the gear forces into the housing.', spec: ['A 6202 has C = 8060 N. At 1500 N equivalent load, L10 = 155.1 million revolutions (15.06)', 'Life goes as (C/P)³: double the load and it drops eightfold', 'At 95 % reliability the life is 0.619 L10'], lessons: [LES.roll, LES.fits] },
  seal: { name: 'Lip seal', kicker: 'Seals & fasteners', qty: 2, what: 'Keeps the oil in and the dirt out where a shaft leaves the housing. Only the input and output shafts need one.', spec: ['15.06: in wet, sandy service bearings fail from contamination long before fatigue, so seals matter more than the rating C'], lessons: [LES.roll] },
  key: { name: 'Parallel key', kicker: 'Seals & fasteners', qty: 3, what: 'Locks a hub to its shaft so the torque can cross. It is sized to shear before the shaft does.', spec: ['A 6 × 6 mm key, 25 mm long, on a 20 mm shaft at 100 N·m: 66.7 MPa shear, 133.3 MPa crushing (15.05)', 'A press fit on the same shaft can carry 216.8 N·m (15.05)'], lessons: [LES.keys] },
  bolt: { name: 'Cover bolt', kicker: 'Seals & fasteners', qty: 6, what: 'Clamps the two halves so the joint never opens under load.', spec: ['An M10 class 8.8 bolt: preload 26.10 kN from about 52.2 N·m of torque (15.12)', 'Under a 15 kN separating load the bolt gains only 2.859 kN; the plates take the rest'], lessons: [LES.bolts] },
  breather: { name: 'Breather', kicker: 'Seals & fasteners', what: 'A vent on top of the cover. As the oil and air warm up, it lets air out, so pressure never pushes oil past the seals.', spec: ['Sealed air at fixed volume follows p₂ / p₁ = T₂ / T₁ (10.02)'], lessons: [LES.gas, LES.roll] },
  plug: { name: 'Oil drain plug', kicker: 'Seals & fasteners', what: 'Sits at the lowest point of the housing so the old oil, and the wear particles in it, can be drained.', spec: ['The gears dip into the oil and fling it over the teeth and bearings'], lessons: [LES.lube] },
  oil: { name: 'Oil bath', kicker: 'Housing', what: 'The big gears dip into it and fling oil over the teeth and bearings.', spec: [], lessons: [LES.lube] },
};

// the scripted loop: idle, spin up, load, hold, teardown, reassemble
const SEQ = { duration: 32, events: [
  { t: 0, status: 'IDLE', text: 'Idle · shafts at rest' },
  { t: 2, status: 'SPIN-UP', text: 'Motor on · spinning up, no load' },
  { t: 6, status: 'LOADING', text: 'Load on · torque ramps up' },
  { t: 10, status: 'HOLD', text: 'Holding at full load' },
  { t: 15, status: 'STOPPING', text: 'Load off · motor stops' },
  { t: 17, status: 'TEARDOWN', text: 'Teardown · cover off, parts out' },
  { t: 24, status: 'REASSEMBLE', text: 'Reassemble · cover bolted back' },
  { t: 28, status: 'IDLE', text: 'Idle · ready to run' },
] };
const ramp = (t, a, b) => Math.max(0, Math.min(1, (t - a) / (b - a)));
const rpmK = (t) => (t < 2 ? 0 : t < 6 ? ramp(t, 2, 6) : t < 15 ? 1 : t < 16.5 ? 1 - ramp(t, 15, 16.5) : 0);
const tqK = (t) => (t < 6 ? 0 : t < 10 ? ramp(t, 6, 10) : t < 15 ? 1 : t < 15.6 ? 1 - ramp(t, 15, 15.6) : 0);
const explodedAt = (t) => t >= 17 && t < 24;
const statusAt = (t) => [...SEQ.events].reverse().find((e) => e.t <= t + 1e-6)?.status || 'IDLE';

export function initGearbox(root) {
  let setRpm = RPM0, setTq = TQ0, rpm = 0, tq = 0, theta = 0, manual = false; const model = {};
  const spec = {
    id: 'gearbox', numLabel: 'Take-apart lab · 01', cls: 'ta-lab', code: 'SR-2 · 6.25 : 1', kicker: 'Two-stage spur reducer · take-apart',
    title: 'Take a gearbox apart',
    blurb: 'A two-stage spur reducer, cut tooth by tooth from the involute in lesson 15.08. Watch the mesh run through the open front, isolate a stage, explode the box, and tap any part to see what it does and which lesson works out its numbers.',
    theme: { accent: LIME, danger: CORAL, warn: AMBER, panel: 0xb9bdb2, grid: 0x262a1c, grid2: 0x121409 },
    lessonHref: (lid) => `learn.html#/${lid}`,
    lessons: [LES.geom, LES.str, LES.trains, LES.shaft, LES.roll, LES.bolts],
    camera: { pos: [1.6, 2.2, 4.7], target: [0, 0.85, 0], dist: 5.2, fov: 34, minDist: 1.5, maxDist: 16, floor: 9, shadow: 3, aspectRef: 1.45 },
    assemblies: [
      { id: 'housing', label: 'Housing', focus: () => [0, 1.1, 0], dist: 6.2 },
      { id: 'input', label: 'Input stage', focus: () => model.at((model.XA + model.XB) / 2, -0.2, 0.5), dist: 3.4 },
      { id: 'output', label: 'Output stage', focus: () => model.at((model.XB + model.XC) / 2, 0.15, 0.5), dist: 4.0 },
      { id: 'shafts', label: 'Shafts & bearings', focus: () => [0, 1.6, 0], dist: 5.2 },
      { id: 'fasteners', label: 'Seals & fasteners', focus: () => [0, 1.4, 0], dist: 5.6 },
    ],
    subsystems: [
      { id: 'housing', name: 'Housing', sub: 'Split casting · oil bath', assembly: 'housing' },
      { id: 'input', name: 'Input stage', sub: 'm 2 · 18 : 45', assembly: 'input' },
      { id: 'output', name: 'Output stage', sub: 'm 3 · 18 : 45', assembly: 'output' },
      { id: 'shafts', name: 'Shafts & bearings', sub: '6 ball bearings', assembly: 'shafts' },
      { id: 'fasteners', name: 'Seals & fasteners', sub: 'Seals · keys · bolts', assembly: 'fasteners' },
    ],
    graph: { title: 'Shaft speed · rpm', range: [0, 3000], series: [{ label: 'Input', color: LIME }, { label: 'Counter', color: CYAN }, { label: 'Output', color: AMBER }] },
    sequence: SEQ, telemetryTitle: 'Drive', labelTop: 44,
    build: (ctx) => build(ctx, model),
    onEvent(e, api) { manual = false; api.setExploded(explodedAt(e.t)); },
    onSeek(t, e, api) { manual = false; api.setExploded(explodedAt(t)); rpm = rpmK(t) * setRpm; tq = tqK(t) * setTq; },
    onTick(dt, api) { tick(dt, api); },
    // pull the camera back for the exploded view so the lifted cover and bolts stay in frame
    onExplode(v, api) { if (!api.state.assembly) api.focus(() => (v ? [0, 1.75, 0] : spec.camera.target), (v ? 7.6 : spec.camera.dist) * (api.camera ? Math.min(1.9, Math.max(1, 1.45 / Math.max(0.45, api.camera.aspect)) ** 0.8) : 1)); },
    onPick(p) { quiz.pick(p); },
  };

  function tick(dt, api) {
    const S = api.state;
    const meshed = !S.exploded && (!S.assembly || S.assembly === 'input' || S.assembly === 'output');
    const tRpm = S.playing ? rpmK(S.t) * setRpm : manual ? setRpm : rpm;
    const tTq = S.playing ? tqK(S.t) * setTq : manual ? setTq : tq;
    const k = Math.min(1, dt * 4); rpm += (tRpm - rpm) * k; tq += (tTq - tq) * k;
    const n1 = meshed ? rpm : 0, T1 = meshed && n1 > 1 ? tq : 0;
    // drawn at 1/60 of the real speed so the teeth stay readable
    theta += ((n1 / 60) * 2 * Math.PI * dt) / 60; model.theta = theta;
    // the loop's own word while it plays or is scrubbed; once the operator drives, the word follows the shafts
    const st = statusAt(S.t);
    let word;
    if (S.exploded) word = 'TEARDOWN';
    else if (S.assembly && !meshed) word = 'INSPECT';
    else if (!manual && st !== 'TEARDOWN') word = st;
    else word = n1 < 1 ? 'IDLE' : T1 > 0.2 ? 'UNDER LOAD' : 'NO LOAD';
    api.setStatus(word, '', `Input ${Math.round(n1)} rpm · ${T1.toFixed(1)} N·m · drawn at 1/60 speed`);
    tele(api, n1, T1, dt);
  }

  function tele(api, n, T, dt) {
    tele.acc = (tele.acc || 0) + dt; if (tele.acc < 0.08) return; tele.acc = 0;
    const n2 = n / R1, n3 = n2 / R2, w = (n * 2 * Math.PI) / 60;
    const T2 = T * R1, T3 = T2 * R2, P = T * w;
    if (!tele.k) {
      api.telemetry.innerHTML = `<div class="ta-big"><span class="ta-micro">Output torque</span><b data-k="big">0<small>N·m</small></b></div>
        <dl class="ta-kv">
          <div><dt>Input · rpm</dt><dd data-k="n1"></dd></div><div><dt>Input torque · N·m</dt><dd data-k="t1"></dd></div>
          <div><dt>Input stage</dt><dd>2.50 : 1</dd></div><div><dt>Output stage</dt><dd>2.50 : 1</dd></div>
          <div><dt>Total ratio</dt><dd>6.25 : 1</dd></div><div><dt>Power · kW</dt><dd data-k="pw"></dd></div>
          <div><dt>Countershaft · rpm</dt><dd data-k="n2"></dd></div><div><dt>Output · rpm</dt><dd data-k="n3"></dd></div>
          <div><dt>Tooth force 1 · N</dt><dd data-k="w1"></dd></div><div><dt>Tooth force 2 · N</dt><dd data-k="w2"></dd></div>
        </dl>
        <p class="ta-note">Ideal train, 45/18 × 45/18 = 6.25. No lesson gives a mesh efficiency, so no losses come off. Starts at the 15.09 case: 19.1 N·m at 1500 rpm, 3 kW.</p>`;
      tele.k = Object.fromEntries([...api.telemetry.querySelectorAll('[data-k]')].map((e) => [e.dataset.k, e]));
    }
    const f0 = (v) => Math.round(v).toLocaleString('en-US'), f1 = (v) => v.toFixed(1), f2 = (v) => v.toFixed(2);
    const on = n > 1;
    tele.k.big.innerHTML = `${on ? f1(T3) : '0.0'}<small>N·m</small>`;
    Object.entries({ n1: f0(n), t1: f1(T), pw: f2(P / 1000), n2: f0(n2), n3: f1(n3), w1: f0(T / RP1), w2: f0(T2 / RP3) }).forEach(([key, v]) => { tele.k[key].textContent = v; });
    api.graphPush([n, n2, n3]);
    const S = api.state, ex = S.exploded, iso = S.assembly;
    const stage = (id) => (ex ? ['Detached', 'detached'] : iso && iso !== id && iso !== 'input' && iso !== 'output' ? ['Idle', 'idle'] : on ? [T > 0.2 ? 'Loaded' : 'Meshing', ''] : ['Idle', 'idle']);
    api.badge('housing', ex ? 'Open' : 'Sealed', ex ? 'detached' : '');
    api.badge('input', ...stage('input'));
    api.badge('output', ...stage('output'));
    api.badge('shafts', ex ? 'Detached' : on ? `${f0(n3)} rpm out` : 'At rest', ex ? 'detached' : on ? '' : 'idle');
    api.badge('fasteners', ex ? 'Detached' : 'Tight', ex ? 'detached' : '');
    Object.assign(api.sec.dataset, { rpm: n.toFixed(2), rpmMid: n2.toFixed(3), rpmOut: n3.toFixed(3), tqIn: T.toFixed(3), tqOut: T3.toFixed(3), theta: theta.toFixed(5) });
  }

  const api = takeApart(root, spec);
  // drive controls: input speed and torque
  const range = (label, key, min, max, step, value, fmt, fn) => {
    const lab = document.createElement('label'); lab.className = 'ta-range';
    lab.innerHTML = `<span>${label}</span><output>${fmt(value)}</output><input type="range" min="${min}" max="${max}" step="${step}" value="${value}" aria-label="${label}" data-testid="ta-gearbox-${key}">`;
    const out = lab.querySelector('output');
    lab.querySelector('input').addEventListener('input', (e) => { const v = +e.target.value; out.textContent = fmt(v); fn(v); if (api.state.playing) api.setPlaying(false, 'Operator took over'); manual = true; });
    return lab;
  };
  const head = document.createElement('h4'); head.className = 'ta-ph'; head.innerHTML = '<span>Drive</span><small>Input shaft</small>';
  const rRpm = range('Input speed', 'rpm', 300, 3000, 50, RPM0, (v) => `${v} rpm`, (v) => { setRpm = v; });
  const rTq = range('Input torque', 'torque', 0, 40, 0.1, TQ0, (v) => `${v.toFixed(1)} N·m`, (v) => { setTq = v; });
  const quiz = findThePart(api, [
    ['Which gear turns 6.25 times slower than the motor?', 'g4'],
    ['Which part is sized to shear before the shaft does?', 'key'],
    ['Which part lets warm air out so the oil isn’t pushed past the seals?', 'breather'],
  ]);
  api.extra.append(head, rRpm, rTq, quiz.el);
  api.angles = () => model.angles?.();
  window.__mefs = window.__mefs || {}; window.__mefs.gearbox = api;
  return api;
}

function build(ctx, model) {
  if (!ctx) return { partsList: Object.entries(INFO).map(([k, info]) => ({ id: `${k}-0`, name: info.name, assembly: 'housing', info })) };
  const { scene, M, part, contact } = ctx;
  const mat = { panel: M.panel(), panelDark: M.panelDark(), metal: M.metal(), steel: M.steel(), dark: M.dark(), rubber: M.rubber(), brass: M.brass(), accent: M.accent() };
  const gearMat = new THREE.MeshPhysicalMaterial({ color: 0x9a9e96, roughness: 0.3, metalness: 1.0, clearcoat: 0.2 });
  const gearMatD = new THREE.MeshPhysicalMaterial({ color: 0x5d6158, roughness: 0.36, metalness: 1.0 });
  const P = (id, key, assembly, obj, o = {}) => part(Object.assign({ id, assembly, obj, info: INFO[key], name: INFO[key].name }, o));
  const Y0 = 0.95; // shaft line above the floor
  const XA = -1.04, XB = XA + (M1 * (Z1 + Z2)) / 2, XC = XB + (M2 * (Z3 + Z4)) / 2; // 63 and 94.5 mm centres
  const S1 = -0.2, S2 = 0.15, W1 = 0.2, W2 = 0.3; // stage planes and face widths (20 and 30 mm)
  Object.assign(model, { XA, XB, XC, at: (x, z, dy = 0) => [x, Y0 + dy, z] });
  const world = new THREE.Group(); scene.add(world);
  const LIFT = [0, 0.5, 0.15]; // how a stage rises out of the box when isolated, shafts and all
  // ---- gears ----
  const mk = (m, z, w, bore, mt) => new THREE.Mesh(gearGeometry({ m, z, width: w, bore }).geo, mt);
  const hubRing = (a, b, w, mt) => mesh(ringGeo(a, b, w), mt);
  const gp1 = grp(XA, Y0, S1, mk(M1, Z1, W1, 0.1, gearMat));
  const gg2 = grp(XB, Y0, S1, mk(M1, Z2, W1, 0.16, gearMatD), hubRing(0.16, 0.26, W1 * 1.25, mat.steel));
  for (let k = 0; k < 6; k++) { const a = (k / 6) * Math.PI * 2; gg2.add(mesh(cylZ(0.045, W1 * 1.02, 18), mat.dark, Math.cos(a) * 0.34, Math.sin(a) * 0.34, 0)); }
  const gp3 = grp(XB, Y0, S2, mk(M2, Z3, W2, 0.16, gearMat));
  const gg4 = grp(XC, Y0, S2, mk(M2, Z4, W2, 0.2, gearMatD), hubRing(0.2, 0.34, W2 * 1.15, mat.steel));
  for (let k = 0; k < 6; k++) { const a = (k / 6) * Math.PI * 2; gg4.add(mesh(cylZ(0.07, W2 * 1.02, 18), mat.dark, Math.cos(a) * 0.5, Math.sin(a) * 0.5, 0)); }
  world.add(gp1, gg2, gp3, gg4);
  // a thin lime ring on the pitch circle of each pinion face: the circle the ratio is measured on
  const pitchRing = (g, r, z) => g.add(mesh(new THREE.TorusGeometry(r, 0.005, 6, 72), mat.accent, 0, 0, z));
  pitchRing(gp1, (M1 * Z1) / 2, W1 / 2 + 0.007); pitchRing(gp3, (M2 * Z3) / 2, W2 / 2 + 0.007);
  P('p1-0', 'p1', 'input', gp1, { explode: [-0.35, 0.75, -1.1], glide: LIFT, label: 1, labelAt: [0, 0.2, 0] });
  P('g2-0', 'g2', 'input', gg2, { explode: [0, 1.0, -1.25], glide: LIFT, label: 1, labelAt: [0.3, 0.38, 0] });
  P('p3-0', 'p3', 'output', gp3, { explode: [-0.2, 1.05, 1.0], glide: LIFT, label: 1, labelAt: [0, 0.28, 0] });
  P('g4-0', 'g4', 'output', gg4, { explode: [0.35, 0.75, 1.3], glide: LIFT, label: 1, labelAt: [0.45, 0.5, 0] });
  // ---- shafts ----
  const shaft = (x, r, z0, z1, steps = []) => { const g = grp(x, Y0, 0, mesh(cylZ(r, z1 - z0, 32), mat.metal, 0, 0, (z0 + z1) / 2)); steps.forEach(([zz, rr, ll]) => g.add(mesh(cylZ(rr, ll, 32), mat.steel, 0, 0, zz))); return g; };
  const sIn = shaft(XA, 0.1, -1.15, 0.52, [[-0.03, 0.118, 0.06]]);
  const sMid = shaft(XB, 0.16, -0.5, 0.5, [[-0.03, 0.185, 0.06]]);
  const sOut = shaft(XC, 0.2, -0.5, 1.2, [[-0.03, 0.225, 0.06]]);
  world.add(sIn, sMid, sOut);
  P('shaftIn-0', 'shaftIn', 'shafts', sIn, { explode: [0, 0.6, -1.3], glide: { shafts: [0, 0.75, 0], input: LIFT }, label: 2, labelAt: [0, 0, -1.0] });
  P('shaftMid-0', 'shaftMid', 'shafts', sMid, { explode: [0, 1.4, 0], glide: { shafts: [0, 1.05, 0], input: LIFT, output: LIFT }, label: 2, labelAt: [0, 0.16, 0.42] });
  P('shaftOut-0', 'shaftOut', 'shafts', sOut, { explode: [0.15, 0.5, 1.6], glide: { shafts: [0, 0.75, 0], output: LIFT }, label: 2, labelAt: [0, 0, 1.05] });
  // ---- keys ----
  const keyGeo = (len) => new THREE.BoxGeometry(0.06, 0.06, len);
  const kIn = grp(XA, Y0 + 0.1, -0.95, mesh(keyGeo(0.25), mat.dark));
  const kMid = grp(XB, Y0 + 0.16, S1, mesh(keyGeo(0.2), mat.dark));
  const kOut = grp(XC, Y0 + 0.2, 1.0, mesh(keyGeo(0.3), mat.dark));
  world.add(kIn, kMid, kOut);
  P('key-0', 'key', 'fasteners', kIn, { explode: [0, 1.0, -1.7], glide: [0, 0.4, -0.2], label: 2, labelAt: [0, 0.03, 0] });
  P('key-1', 'key', 'fasteners', kMid, { explode: [0, 2.3, -0.3], glide: [0, 1.0, 0] });
  P('key-2', 'key', 'fasteners', kOut, { explode: [0.15, 0.95, 2.0], glide: [0, 0.4, 0.2] });
  // ---- bearings ----
  const brgs = [];
  [[XA, 0.1], [XB, 0.16], [XC, 0.2]].forEach(([x, a], i) => [-0.42, 0.42].forEach((z) => {
    const b = bearing(mat, a, 0.1); b.position.set(x, Y0, z); world.add(b); brgs.push(b);
    const k = brgs.length - 1;
    P(`brg-${k}`, 'brg', 'shafts', b, { explode: [0, 0.35 + i * 0.12, z < 0 ? -0.75 - i * 0.1 : 0.75 + i * 0.1], glide: [0, [0.75, 1.05, 0.75][i], z < 0 ? -0.2 : 0.2], label: k === 5 ? 1 : k === 0 ? 2 : 0, labelAt: [0, b.userData.outer, 0] });
  }));
  // ---- seals ----
  const seal = (x, a, z) => { const g = grp(x, Y0, z, mesh(ringGeo(a, a + 0.07, 0.05), mat.rubber), mesh(new THREE.TorusGeometry(a + 0.035, 0.008, 6, 40), mat.accent, 0, 0, z < 0 ? -0.026 : 0.026)); world.add(g); return g; };
  const seIn = seal(XA, 0.1, -0.555), seOut = seal(XC, 0.2, 0.555);
  P('seal-0', 'seal', 'fasteners', seIn, { explode: [0, 0.2, -1.35], glide: [0, 0.4, -0.45], label: 2, labelAt: [0, 0.17, 0] });
  P('seal-1', 'seal', 'fasteners', seOut, { explode: [0.1, 0.2, 1.35], glide: [0, 0.4, 0.45] });
  // ---- housing: split on the shaft line ----
  const X0 = XA - 0.34, X1 = XC + 0.84, ZW = 0.52, H0 = 0.15, H1 = Y0 + 0.82, T = 0.05;
  const cx = (X0 + X1) / 2, wx = X1 - X0;
  const box = (w, hh, d, m, x, y, z) => mesh(new THREE.BoxGeometry(w, hh, d), m, x, y, z);
  const base = new THREE.Group();
  base.add(box(wx, T, ZW * 2, mat.panel, cx, H0 + T / 2, 0));
  base.add(box(wx, Y0 - H0, T, mat.panel, cx, (Y0 + H0) / 2, -ZW + T / 2)); // back wall; the front is cut away so the gears show
  base.add(box(0.012, Y0 - H0, 0.012, mat.accent, X0 + 0.006, (Y0 + H0) / 2, ZW), box(0.012, Y0 - H0, 0.012, mat.accent, X1 - 0.006, (Y0 + H0) / 2, ZW)); // section lines
  base.add(box(T, Y0 - H0, ZW * 2, mat.panel, X0 + T / 2, (Y0 + H0) / 2, 0), box(T, Y0 - H0, ZW * 2, mat.panel, X1 - T / 2, (Y0 + H0) / 2, 0));
  base.add(box(wx + 0.16, 0.04, ZW * 2 + 0.16, mat.panelDark, cx, Y0 - 0.02, 0)); // flange
  base.add(box(wx + 0.3, 0.08, ZW * 2 - 0.1, mat.panelDark, cx, 0.04, 0), box(0.25, H0, ZW * 2 - 0.1, mat.panelDark, X0 + 0.15, H0 / 2, 0), box(0.25, H0, ZW * 2 - 0.1, mat.panelDark, X1 - 0.15, H0 / 2, 0)); // feet
  const half = (r, len) => { const g = new THREE.CylinderGeometry(r, r, len, 40, 1, true, Math.PI / 2, Math.PI); g.rotateX(Math.PI / 2); return g; };
  const bossR = [0.31, 0.43, 0.5];
  [XA, XB, XC].forEach((x, i) => [-1, 1].forEach((s) => { const b1 = mesh(half(bossR[i] * 0.62, 0.1), mat.panel, x, Y0, s * (ZW + 0.03)); b1.rotation.z = Math.PI; base.add(b1); }));
  const oil = mesh(new THREE.BoxGeometry(wx - 0.12, 0.22, ZW * 2 - 0.12), new THREE.MeshPhysicalMaterial({ color: 0x5a4a12, roughness: 0.15, metalness: 0, transparent: true, opacity: 0.5, depthWrite: false }), cx, H0 + 0.16, 0);
  oil.userData.noShadow = true;
  world.add(base, oil);
  P('base-0', 'base', 'housing', base, { explode: [0, -0.15, 0], glide: [0, -0.25, 0], label: 1, labelAt: [X1, Y0 - 0.35, ZW] });
  P('oil-0', 'oil', 'housing', oil, { explode: [0, -0.15, 0], glide: [0, -0.25, 0], pickable: false });
  const cover = new THREE.Group();
  const CH = H1 - Y0;
  cover.add(box(wx + 0.16, 0.04, ZW * 2 + 0.16, mat.panelDark, cx, Y0 + 0.02, 0));
  cover.add(box(wx, CH, T, mat.panel, cx, Y0 + CH / 2, -ZW + T / 2));
  cover.add(box(0.012, CH, 0.012, mat.accent, X0 + 0.006, Y0 + CH / 2, ZW), box(0.012, CH, 0.012, mat.accent, X1 - 0.006, Y0 + CH / 2, ZW), box(wx, 0.012, 0.012, mat.accent, cx, H1, ZW));
  cover.add(box(T, CH, ZW * 2, mat.panel, X0 + T / 2, Y0 + CH / 2, 0), box(T, CH, ZW * 2, mat.panel, X1 - T / 2, Y0 + CH / 2, 0));
  const WX0 = XA - 0.15, WX1 = XC + 0.35; // the inspection window: a frame of four plates
  cover.add(box(WX0 - X0, T, ZW * 2, mat.panel, (X0 + WX0) / 2, H1 - T / 2, 0), box(X1 - WX1, T, ZW * 2, mat.panel, (WX1 + X1) / 2, H1 - T / 2, 0));
  cover.add(box(WX1 - WX0, T, 0.18, mat.panel, (WX0 + WX1) / 2, H1 - T / 2, -ZW + 0.09), box(WX1 - WX0, T, 0.18, mat.panel, (WX0 + WX1) / 2, H1 - T / 2, ZW - 0.09));
  [XA, XB, XC].forEach((x, i) => [-1, 1].forEach((s) => { cover.add(mesh(half(bossR[i] * 0.62, 0.1), mat.panel, x, Y0, s * (ZW + 0.03))); }));
  world.add(cover);
  P('cover-0', 'cover', 'housing', cover, { explode: [0, 1.9, -0.5], glide: [0, 1.2, 0], label: 1, labelAt: [X0, H1, -ZW] });
  const win = mesh(new THREE.BoxGeometry(WX1 - WX0, 0.01, ZW * 2 - 0.36), new THREE.MeshPhysicalMaterial({ color: 0x0b1215, roughness: 0.05, metalness: 0, transparent: true, opacity: 0.18, depthWrite: false }), (WX0 + WX1) / 2, H1 - 0.01, 0);
  win.userData.noShadow = true; world.add(win);
  P('win-0', 'win', 'housing', win, { explode: [0, 1.9, -0.5], glide: [0, 1.2, 0], pickable: false });
  // ---- bolts, breather, drain plug ----
  const bx = [X0 + 0.12, cx, X1 - 0.12];
  let bi = 0; for (const x of bx) for (const s of [-1, 1]) { const b = bolt(mat, 0.035, 0.18); b.position.set(x, Y0 + 0.04, s * (ZW + 0.05)); world.add(b); P(`bolt-${bi}`, 'bolt', 'fasteners', b, { explode: [0, 2.45, s * 0.35 - 0.25], glide: [0, 1.4, 0], label: bi === 1 ? 2 : 0, labelAt: [0, 0.05, 0] }); bi++; }
  const brX = (WX1 + X1) / 2;
  const breather = grp(brX, H1, 0,
    mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.06, 6), mat.steel, 0, 0.03, 0),
    mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.06, 16), mat.metal, 0, 0.09, 0),
    mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.05, 24), mat.dark, 0, 0.145, 0),
    mesh(new THREE.TorusGeometry(0.066, 0.006, 6, 32), mat.accent, 0, 0.12, 0));
  breather.children[3].rotation.x = Math.PI / 2;
  world.add(breather);
  P('breather-0', 'breather', 'fasteners', breather, { explode: [0.35, 2.75, -0.5], glide: [0, 0.9, 0], label: 2, labelAt: [0, 0.17, 0] });
  const plug = grp(X1, H0 + 0.11, 0.2,
    mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.04, 6), mat.steel, 0.02, 0, 0),
    mesh(new THREE.CylinderGeometry(0.065, 0.065, 0.012, 24), mat.brass, 0.002, 0, 0));
  plug.children.forEach((c) => { c.rotation.z = Math.PI / 2; });
  world.add(plug);
  P('plug-0', 'plug', 'fasteners', plug, { explode: [0.8, -0.05, 0.2], glide: [0.45, 0, 0.2], label: 2, labelAt: [0.04, 0, 0] });
  contact.scale.set(wx * 1.5, ZW * 3, 1); contact.position.set(cx, 0.003, 0); contact.material.opacity = 0.55;

  // ---- the mesh ----
  // input θ; the countershaft turns −θ/2.5, the output +θ/6.25. Each gear is phased so a tooth sits in its partner's gap.
  const ph2 = Math.PI - Math.PI / Z2, ph4 = Math.PI - Math.PI / Z4;
  model.update = () => {
    const th = model.theta || 0;
    gp1.rotation.z = th; sIn.rotation.z = th;
    gg2.rotation.z = ph2 - th / R1; gp3.rotation.z = -th / R1; sMid.rotation.z = -th / R1;
    gg4.rotation.z = ph4 + th / RT; sOut.rotation.z = th / RT;
    brgs.forEach((b, i) => { b.children[1].rotation.z = i < 2 ? th : i < 4 ? -th / R1 : th / RT; });
  };
  // gear angles turned since start (phases removed), for the tests
  model.angles = () => ({ p1: gp1.rotation.z, g2: gg2.rotation.z - ph2, p3: gp3.rotation.z, g4: gg4.rotation.z - ph4 });
  return model;
}
