// Take-apart lab: a single-cylinder four-stroke engine, cut away so the piston shows. The piston follows the exact
// slider-crank of lesson 05.04 (r = 50 mm, l = 200 mm); the valves open in step with it from a camshaft at half crank
// speed. Pressure is the air-standard Otto cycle of lesson 10.12 (r = 10, k = 1.3997, 1200 kJ/kg, from 300 K and 100 kPa).
// Real engines have valve overlap, spark advance and losses; this model has none of them, and it says so on screen.
import * as THREE from 'three';
import { takeApart } from './takeapart/engine.js';
import { gearGeometry } from './takeapart/gear.js';
import { mesh, grp, ringGeo, cylZ } from './takeapart/kit.js';
import { findThePart } from './takeapart/quiz.js';

const LIME = '#eeff41', CORAL = '#ff6b81', AMBER = '#ffb547', CYAN = '#5cc8ff';
const L = (id, t) => [id, t];
const LES = {
  kin: L('05.04', 'Rigid body kinematics'), otto: L('10.12', 'Otto and Diesel cycles'), first: L('10.04', 'The first law for closed systems'), comb: L('10.18', 'Combustion and flame temperature'),
  fly: L('07.17', 'Flywheel energy storage'), bal: L('07.11', 'Rotating machinery and balancing'), fins: L('13.04', 'Fins'), plain: L('15.07', 'Plain bearings'),
  chain: L('15.11', 'Belts and chains'), spring: L('15.14', 'Helical springs'), buck: L('06.19', 'Buckling of columns'), fat: L('09.13', 'Fatigue'), cast: L('09.24', 'Casting and solidification'), bolts: L('15.12', 'Bolted joints'),
};
// Otto cycle, lesson 10.12
const CV = 0.718, RG = 0.287, K = 1.3997, RC = 10, T1 = 300, P1 = 100, QIN = 1200;
const V1 = (RG * T1) / P1, V2 = V1 / RC, T2 = T1 * RC ** (K - 1), P2 = P1 * RC ** K, T3 = T2 + QIN / CV, P3 = (P2 * T3) / T2;
const ETA = 1 - RC ** (1 - K);
// slider-crank, lesson 05.04: crank r = 50 mm, rod l = 200 mm. Drawn at 1 unit = 100 mm.
const RMM = 50, LMM = 200;
const R = RMM / 100, LR = LMM / 100, Y0 = 0.9;
const xMm = (th) => RMM * Math.cos(th) + Math.sqrt(LMM * LMM - RMM * RMM * Math.sin(th) ** 2); // piston from crank centre
// dx/dt = -r ω sinθ - r² ω sinθ cosθ / sqrt(l² - r² sin²θ), in m/s for ω in rad/s
const vMs = (th, w) => (-RMM * w * Math.sin(th) - (RMM * RMM * w * Math.sin(th) * Math.cos(th)) / Math.sqrt(LMM * LMM - RMM * RMM * Math.sin(th) ** 2)) / 1000;
const pinY = (th) => Y0 + xMm(th) / 100;
const STROKES = [['INTAKE', 'Inlet open · piston going down'], ['COMPRESSION', 'Valves shut · piston going up'], ['POWER', 'Fired · gas drives the piston down'], ['EXHAUST', 'Exhaust open · piston going up']];
const W955 = 955; // rpm, about 100 rad/s: the speed of the lesson 05.04 example
// ideal valve timing, no overlap: inlet open 0-180° of crank, exhaust 540-720°, a half-sine lift profile
const wrap = (th) => ((th % (4 * Math.PI)) + 4 * Math.PI) % (4 * Math.PI);
const liftIn = (th) => { const a = wrap(th); return a < Math.PI ? Math.sin(a) : 0; };
const liftEx = (th) => { const a = wrap(th) - 3 * Math.PI; return a > 0 ? Math.sin(a) : 0; };
const strokeOf = (th) => Math.min(3, Math.floor(wrap(th) / Math.PI));

const INFO = {
  block: { name: 'Cylinder block', kicker: 'Block & head', what: 'The cylinder the piston runs in, and the crankcase under it. Cut open at the front here so you can see inside.', spec: ['Engine blocks are cast. Metal shrinks 3 to 7 % by volume as it freezes, so a riser feeds the last part to solidify (09.24)'], lessons: [LES.cast] },
  fins: { name: 'Cooling fins', kicker: 'Block & head', what: 'An air-cooled cylinder sheds its heat through fins: far more surface for the same metal.', spec: ['13.04: a short pin fin runs at 92.36 % efficiency and carries 38 times what its base area would alone'], lessons: [LES.fins] },
  sump: { name: 'Sump', kicker: 'Block & head', what: 'Holds the oil the crank and rod bearings run on.', spec: [], lessons: [LES.plain] },
  head: { name: 'Cylinder head', kicker: 'Block & head', what: 'Closes the top of the cylinder and holds the valves, the spark plug and the camshaft.', spec: ['Clamped down hard enough that combustion pressure never lifts it (15.12)'], lessons: [LES.bolts, LES.cast] },
  headbolt: { name: 'Head bolt', kicker: 'Block & head', qty: 4, what: 'Clamps the head to the block through the gasket.', spec: ['The preload has to stay above the peak gas force on the head, or the joint opens (15.12)'], lessons: [LES.bolts] },
  cover: { name: 'Cam cover', kicker: 'Block & head', what: 'Keeps the oil in around the camshaft and valve springs.', spec: [], lessons: [] },
  piston: { name: 'Piston', kicker: 'Piston & rod', what: 'Turns gas pressure into force on the rod. Its height follows the slider-crank exactly.', spec: ['05.04: r = 50 mm, l = 200 mm. At 60° the piston sits 220.3 mm from the crank centre', 'At 60° and 100 rad/s it moves at 4.885 m/s towards the crank (05.04)', 'The gas does work p dV on its crown (10.04)'], lessons: [LES.kin, LES.first] },
  rings: { name: 'Piston rings', kicker: 'Piston & rod', qty: 3, what: 'Two compression rings seal the gas; the bottom ring scrapes oil off the bore.', spec: [], lessons: [LES.plain] },
  pin: { name: 'Wrist pin', kicker: 'Piston & rod', what: 'Also called the gudgeon pin. It joins piston and rod: the slider end of the slider-crank.', spec: [], lessons: [LES.kin] },
  rod: { name: 'Connecting rod', kicker: 'Piston & rod', what: 'Pushes and pulls between piston and crank. Compression makes it a column; the endless cycling makes it a fatigue part.', spec: ['l = 200 mm centre to centre (05.04)', 'Check it as a column: a slender strut buckles long before it crushes (06.19)'], lessons: [LES.buck, LES.fat, LES.kin] },
  crank: { name: 'Crankshaft', kicker: 'Crank & flywheel', what: 'Turns the rod’s push into rotation. The counterweights balance the crankpin and the rod’s big end.', spec: ['Crank radius 50 mm, so the stroke is 100 mm (05.04)', 'Balancing: 07.11 corrects a rotor in two planes so the force and the moment both vanish'], lessons: [LES.kin, LES.bal] },
  mainbrg: { name: 'Main bearing', kicker: 'Crank & flywheel', qty: 2, what: 'A plain bearing: the journal rides on a wedge of oil and never touches the shell.', spec: ['15.07: a 20 μm wedge at 10 m/s carries 300.45 kN per metre of width; double the film and the load falls by 4'], lessons: [LES.plain] },
  fly: { name: 'Flywheel', kicker: 'Crank & flywheel', what: 'Stores energy from the power stroke and carries the engine through the other three.', spec: ['07.17: high-strength steel at 800 MPa can spin its rim at up to 319.2 m/s'], lessons: [LES.fly, LES.bal] },
  cam: { name: 'Camshaft', kicker: 'Valvetrain', what: 'Opens each valve once every two turns of the crank, so it turns at half crank speed.', spec: ['One lobe per valve, set 90° of cam apart here: inlet open over 0–180° of crank, exhaust over 540–720°'], lessons: [LES.chain] },
  chain: { name: 'Timing chain', kicker: 'Valvetrain', what: 'Drives the camshaft from the crank at exactly 2 : 1, without slipping.', spec: ['Sprockets 18 and 36 teeth', '15.11: a chain’s speed pulses by 1 − cos(π/z); on the 18-tooth sprocket that is 1.52 %'], lessons: [LES.chain] },
  valveIn: { name: 'Inlet valve', kicker: 'Valvetrain', what: 'Lets the fresh charge in on the intake stroke.', spec: ['Open over 0–180° of crank here. Real engines open it early and shut it late (valve overlap); this model leaves that out'], lessons: [LES.otto] },
  valveEx: { name: 'Exhaust valve', kicker: 'Valvetrain', what: 'Lets the burnt gas out on the exhaust stroke. It runs hotter than the inlet valve.', spec: ['Open over 540–720° of crank here, with no overlap'], lessons: [LES.otto] },
  spring: { name: 'Valve spring', kicker: 'Valvetrain', qty: 2, what: 'Shuts the valve again and keeps it following the cam.', spec: ['Rate k = G d⁴ / 8 D³ n: it goes as the wire diameter to the fourth power, and twice the coils give half the rate (15.14)'], lessons: [LES.spring] },
  plug: { name: 'Spark plug', kicker: 'Ignition', what: 'Fires at the top of the compression stroke and starts the power stroke.', spec: ['In the ideal Otto cycle all the heat goes in at constant volume, right at the top (10.12)'], lessons: [LES.otto, LES.comb] },
  coil: { name: 'Ignition coil', kicker: 'Ignition', what: 'Turns the low battery voltage into the high-voltage pulse that jumps the plug gap, timed to the top of compression.', spec: [], lessons: [LES.otto] },
  lead: { name: 'HT lead', kicker: 'Ignition', what: 'The insulated lead that carries the pulse from the coil to the plug.', spec: [], lessons: [] },
};

const SEQ = { duration: 32, events: [
  { t: 0, status: 'IDLE', text: 'Idle · piston at top dead centre' },
  { t: 2, status: 'CRANKING', text: 'Starter on · cranking slowly' },
  { t: 5, status: 'RUNNING', text: 'Fires · running at the set speed' },
  { t: 14, status: 'STOPPING', text: 'Ignition off · coasting to a stop' },
  { t: 16, status: 'TEARDOWN', text: 'Teardown · head off, parts out' },
  { t: 23, status: 'REASSEMBLE', text: 'Reassemble · head bolted back' },
  { t: 28, status: 'IDLE', text: 'Idle · ready to start' },
] };
const CRANK_RPM = 200;
const rpmAt = (t, set) => (t < 2 ? 0 : t < 5 ? CRANK_RPM : t < 14 ? set : t < 15.5 ? set * (1 - (t - 14) / 1.5) : 0);
const explodedAt = (t) => t >= 16 && t < 23;
const statusAt = (t) => [...SEQ.events].reverse().find((e) => e.t <= t + 1e-6)?.status || 'IDLE';

export function initEngine(root) {
  let rpm = 0, setRpm = W955, theta = 0, manual = false, hold = false; const model = {};
  const spec = {
    id: 'engine', numLabel: 'Take-apart lab · 02', cls: 'ta-lab', code: '1C-4T · r = 10', kicker: 'Single cylinder · four-stroke · take-apart',
    title: 'Take an engine apart',
    blurb: 'One cylinder, four strokes, cut open so you can watch. The piston follows the slider-crank from lesson 05.04 and the valves open in step from a camshaft at half speed. Isolate the valvetrain, explode the lot, and tap a part for the lesson behind it.',
    theme: { accent: LIME, danger: CORAL, warn: AMBER, panel: 0xb9bdb2, grid: 0x262a1c, grid2: 0x121409 },
    lessonHref: (lid) => `learn.html#/${lid}`,
    lessons: [LES.kin, LES.otto, LES.fly, LES.plain, LES.chain],
    camera: { pos: [4.0, 3.8, 7.2], target: [0, 2.75, 0], dist: 9.6, fov: 34, minDist: 3, maxDist: 26, floor: 12, shadow: 4, aspectRef: 1.45 },
    labelTop: 44,
    assemblies: [
      { id: 'block', label: 'Block & head', focus: () => [0, 2.4, 0], dist: 10 },
      { id: 'piston', label: 'Piston & rod', focus: () => [0, 2.6, 1.3], dist: 7.5 },
      { id: 'crank', label: 'Crank & flywheel', focus: () => [0, 1.0, 0.6], dist: 7 },
      { id: 'valves', label: 'Valvetrain', focus: () => [0, 4.4, 0.6], dist: 8 },
      { id: 'ignition', label: 'Ignition', focus: () => [0.8, 5.0, 0.8], dist: 6 },
    ],
    subsystems: [
      { id: 'block', name: 'Block & head', sub: 'Finned · cut open', assembly: 'block' },
      { id: 'piston', name: 'Piston & rod', sub: 'l = 200 mm', assembly: 'piston' },
      { id: 'crank', name: 'Crank & flywheel', sub: 'r = 50 mm', assembly: 'crank' },
      { id: 'valves', name: 'Valvetrain', sub: 'Cam at ½ speed', assembly: 'valves' },
      { id: 'ignition', name: 'Ignition', sub: 'Plug · coil', assembly: 'ignition' },
    ],
    graph: { title: 'Valve lift and piston height · %', range: [0, 100], series: [{ label: 'Inlet', color: LIME }, { label: 'Exhaust', color: AMBER }, { label: 'Piston', color: CYAN }] },
    sequence: SEQ, telemetryTitle: 'Cycle',
    build: (ctx) => build(ctx, model),
    onEvent(e, api) { manual = false; api.setExploded(explodedAt(e.t)); },
    onSeek(t, e, api) { manual = false; api.setExploded(explodedAt(t)); rpm = rpmAt(t, setRpm); },
    onExplode(v, api) { if (!api.state.assembly && api.camera) api.focus(() => (v ? [0.1, 3.2, 0] : spec.camera.target), (v ? 13.5 : spec.camera.dist) * Math.min(1.9, Math.max(1, 1.45 / Math.max(0.45, api.camera.aspect)) ** 0.8)); },
    onTick(dt, api) { tick(dt, api); },
    onPick(p) { quiz.pick(p); },
  };

  function tick(dt, api) {
    const S = api.state;
    if (S.playing) hold = false;
    const tgt = hold ? 0 : S.playing ? rpmAt(S.t, setRpm) : manual ? setRpm : rpm;
    rpm += (tgt - rpm) * Math.min(1, dt * 3);
    if (Math.abs(tgt - rpm) < 0.5) rpm = tgt; // settle exactly, so readouts don't hover a digit off
    const n = S.exploded ? 0 : rpm;
    theta = wrap(theta + ((n / 60) * 2 * Math.PI * dt) / 40); // drawn at 1/40 of the real speed
    model.theta = theta; model.firing = !S.playing || (S.t >= 5 && S.t < 14);
    const st = strokeOf(theta), loop = statusAt(S.t);
    let word, sub;
    if (S.exploded) { word = 'TEARDOWN'; sub = 'Exploded view · crank stopped'; }
    else if (n > 1) { word = STROKES[st][0]; sub = `${st === 2 && !model.firing ? 'No spark yet · cranking' : STROKES[st][1]} · 1/40 speed`; }
    else { word = !manual && (loop === 'REASSEMBLE' || loop === 'IDLE') ? loop : 'IDLE'; sub = `Crank stopped at ${Math.round((theta * 180) / Math.PI)}°`; }
    api.setStatus(word, '', sub);
    api.sec.dataset.stroke = STROKES[st][0].toLowerCase();
    tele(api, n, dt);
  }
  // pressure: volume from the slider-crank between V2 at TDC and V1 at BDC; pressure from the Otto states on each stroke
  // with no spark (cranking) the charge is simply compressed and let back out along the same curve
  function cycle(th, fired = true) {
    const a = wrap(th), x = xMm(a), v = V2 + (V1 - V2) * ((RMM + LMM - x) / (2 * RMM)), st = strokeOf(a);
    let p = P1;
    if (st === 1 || (st === 2 && !fired)) p = P1 * (V1 / v) ** K;
    else if (st === 2) p = P3 * (V2 / v) ** K;
    return { v, p, st };
  }
  function tele(api, n, dt) {
    tele.acc = (tele.acc || 0) + dt; if (tele.acc < 0.06) return; tele.acc = 0;
    const c = cycle(theta, model.firing), w = (n * 2 * Math.PI) / 60, x = xMm(theta), v = vMs(theta, w), li = liftIn(theta), le = liftEx(theta);
    if (!tele.k) {
      api.telemetry.innerHTML = `<div class="ta-big"><span class="ta-micro">Crank angle</span><b data-k="deg">0<small>° / 720</small></b></div>
        <dl class="ta-kv">
          <div><dt>Stroke</dt><dd data-k="s"></dd></div><div><dt>Crank · rpm</dt><dd data-k="n"></dd></div>
          <div><dt>Piston · mm</dt><dd data-k="x"></dd></div><div><dt>Piston · m/s</dt><dd data-k="v"></dd></div>
          <div><dt>Inlet lift</dt><dd data-k="li"></dd></div><div><dt>Exhaust lift</dt><dd data-k="le"></dd></div>
          <div><dt>Cylinder · kPa</dt><dd data-k="p"></dd></div><div><dt>Cam · rpm</dt><dd data-k="c"></dd></div>
        </dl>
        <p class="ta-note">x = r cos θ + √(l² − r² sin² θ) from the crank centre, r = 50, l = 200 mm (05.04); speed is dx/dt, + up. Pressure: ideal Otto at r = 10 (10.12), ${(ETA * 100).toFixed(1)} % efficient. Ideal timing too: no valve overlap, no spark advance.</p>`;
      tele.k = Object.fromEntries([...api.telemetry.querySelectorAll('[data-k]')].map((e) => [e.dataset.k, e]));
    }
    const deg = (wrap(theta) * 180) / Math.PI;
    tele.k.deg.innerHTML = `${Math.floor(deg + 1e-6) % 720}<small>° / 720</small>`;
    Object.entries({ s: STROKES[c.st][0].toLowerCase(), n: Math.round(n).toLocaleString('en-US'), x: x.toFixed(1), v: (v >= 0 ? '+' : '−') + Math.abs(v).toFixed(2), li: `${Math.round(li * 100)} %`, le: `${Math.round(le * 100)} %`, p: Math.round(c.p).toLocaleString('en-US'), c: Math.round(n / 2).toLocaleString('en-US') }).forEach(([k, val]) => { tele.k[k].textContent = val; });
    api.graphPush([li * 100, le * 100, ((x - (LMM - RMM)) / (2 * RMM)) * 100]);
    const S = api.state, ex = S.exploded, live = n > 1;
    const b = (id, on, off = 'Idle') => api.badge(id, ex ? 'Detached' : live ? on : off, ex ? 'detached' : live ? '' : 'idle');
    b('block', c.st === 2 ? 'Hot' : 'Running');
    b('piston', v >= 0 ? 'Rising' : 'Falling', 'At rest');
    b('crank', `${Math.round(n)} rpm`, 'At rest');
    b('valves', li > 0 ? 'Inlet open' : le > 0 ? 'Exhaust open' : 'Both shut');
    if (live && c.st === 2 && model.firing) api.badge('ignition', 'Fired', 'warn'); else b('ignition', 'Armed');
    Object.assign(api.sec.dataset, { theta: wrap(theta).toFixed(5), deg: deg.toFixed(2), pinMm: x.toFixed(3), vel: v.toFixed(4), liftIn: li.toFixed(4), liftEx: le.toFixed(4), rpm: n.toFixed(2) });
  }

  const api = takeApart(root, spec);
  const range = document.createElement('label'); range.className = 'ta-range';
  range.innerHTML = `<span>Engine speed</span><output>${W955} rpm</output><input type="range" min="200" max="3000" step="5" value="${W955}" aria-label="Engine speed" data-testid="ta-engine-rpm">`;
  range.querySelector('input').addEventListener('input', (e) => { setRpm = +e.target.value; range.querySelector('output').textContent = `${setRpm} rpm`; if (api.state.playing) api.setPlaying(false, 'Operator took over'); manual = true; hold = false; });
  const head = document.createElement('h4'); head.className = 'ta-ph'; head.innerHTML = '<span>Drive</span><small>Crank</small>';
  const quiz = findThePart(api, [
    ['Which part turns at half crank speed?', 'cam'],
    ['Which part carries the engine through the three strokes that make no power?', 'fly'],
    ['Which part is the slider in the slider-crank?', 'piston'],
  ]);
  api.extra.append(head, range, quiz.el);
  api.cycle = cycle; api.xMm = xMm; api.vMs = vMs; api.liftIn = liftIn; api.liftEx = liftEx;
  // jump the crank to an angle (degrees, 0-720) and stop there, for the tests and for anyone who wants to step through
  api.setCrank = (deg) => { api.setPlaying(false); manual = true; hold = true; rpm = 0; theta = wrap((deg * Math.PI) / 180); model.theta = theta; };
  window.__mefs = window.__mefs || {}; window.__mefs.engine = api;
  return api;
}

function build(ctx, model) {
  if (!ctx) return { partsList: Object.entries(INFO).map(([k, info]) => ({ id: `${k}-0`, name: info.name, assembly: 'block', info })) };
  const { scene, M, part, contact } = ctx;
  const mat = { panel: M.panel(), panelDark: M.panelDark(), metal: M.metal(), steel: M.steel(), dark: M.dark(), rubber: M.rubber(), brass: M.brass(), accent: M.accent(), copper: M.copper() };
  const P = (id, key, assembly, obj, o = {}) => part(Object.assign({ id, assembly, obj, info: INFO[key], name: INFO[key].name }, o));
  const W = new THREE.Group(); scene.add(W);
  // the teardown: block stays put; head and valvetrain lift, piston and rod come out to the left, crank and flywheel
  // to the right, the sump drops and the ignition parts step off to the right of the head
  const XL = -2.0, XR = 2.15;
  const VT = [0, 0.9, 0.9], IGN = [0.7, 0.7, 0.8]; // isolated valvetrain and ignition slide up and out, moving as one
  const box = (w, h, d, m, x, y, z) => mesh(new THREE.BoxGeometry(w, h, d), m, x, y, z);
  const BORE = 0.45, CY0 = 1.65, CY1 = 3.85; // bore radius, cylinder bottom and top
  // ---- block: half cylinder (open to the front) + crankcase without its front wall ----
  const halfCyl = (r, h, open = true) => new THREE.CylinderGeometry(r, r, h, 48, 1, open, Math.PI / 2, Math.PI); // back half (z < 0)
  const block = new THREE.Group();
  const barrel = mesh(halfCyl(BORE + 0.09, CY1 - CY0), mat.panel, 0, (CY0 + CY1) / 2, 0); barrel.material.side = THREE.DoubleSide; block.add(barrel);
  const liner = mesh(halfCyl(BORE + 0.005, CY1 - CY0), mat.steel, 0, (CY0 + CY1) / 2, 0); liner.material.side = THREE.BackSide; block.add(liner);
  // cut faces in lime so the section reads as a section
  [-1, 1].forEach((s) => { block.add(box(0.09, CY1 - CY0, 0.01, mat.panelDark, s * (BORE + 0.05), (CY0 + CY1) / 2, 0.004)); block.add(box(0.008, CY1 - CY0, 0.012, mat.accent, s * (BORE + 0.095), (CY0 + CY1) / 2, 0.006)); });
  const CW = 1.7, CD = 1.1;
  block.add(box(CW, 0.08, CD, mat.panel, 0, CY0, -CD / 2 + 0.55)); // deck
  block.add(box(CW, CY0 - 0.25, 0.08, mat.panel, 0, (CY0 + 0.25) / 2, -0.55)); // back wall
  [-1, 1].forEach((s) => block.add(box(0.08, CY0 - 0.25, CD, mat.panel, s * (CW / 2), (CY0 + 0.25) / 2, 0)));
  block.add(box(CW, 0.012, 0.012, mat.accent, 0, CY0 + 0.04, 0.55));
  W.add(block);
  P('block-0', 'block', 'block', block, { explode: [0, 0, 0], label: 1, labelAt: [-CW / 2, 1.2, 0.4] });
  const fins = new THREE.Group();
  const finS = new THREE.Shape(); finS.absarc(0, 0, BORE + 0.38, 0, Math.PI, false); finS.absarc(0, 0, BORE + 0.09, Math.PI, 0, true); finS.closePath();
  const finG = new THREE.ExtrudeGeometry(finS, { depth: 0.05, bevelEnabled: false, curveSegments: 24 }); finG.rotateX(-Math.PI / 2); // back half (z < 0), 5 mm thick
  for (let k = 0; k < 9; k++) fins.add(mesh(finG, mat.panelDark, 0, CY0 + 0.32 + k * 0.2, 0));
  W.add(fins);
  P('fins-0', 'fins', 'block', fins, { explode: [0, 0, 0], label: 2, labelAt: [-(BORE + 0.38), 3.2, 0] });
  const sump = grp(0, 0, 0, box(CW - 0.1, 0.22, CD, mat.panelDark, 0, 0.14, 0));
  W.add(sump);
  P('sump-0', 'sump', 'block', sump, { explode: [0, -0.7, 0], label: 2, labelAt: [CW / 2 - 0.05, 0.14, CD / 2] });
  // ---- crankshaft (rotates about z at Y0) ----
  const crankArm = new THREE.Group(); const crank = grp(0, Y0, 0, crankArm);
  crankArm.add(mesh(cylZ(0.13, 1.5, 32), mat.metal, 0, 0, -0.35)); // main journals through to the back
  const web = (z) => { const s = new THREE.Shape(); s.moveTo(-0.16, R); s.absarc(0, R, 0.16, Math.PI, 0, true); s.lineTo(0.16, 0); s.absarc(0, 0, 0.42, 0, Math.PI, true); s.lineTo(-0.16, R); const g = new THREE.ExtrudeGeometry(s, { depth: 0.12, bevelEnabled: false }); g.translate(0, 0, -0.06); g.rotateZ(Math.PI); const m = mesh(g, mat.steel, 0, 0, z); return m; };
  // counterweight lobes sit opposite the pin, so draw the pin end of the web up
  const w1 = web(-0.2), w2 = web(0.2); w1.rotation.z = Math.PI; w2.rotation.z = Math.PI; crankArm.add(w1, w2);
  crankArm.add(mesh(cylZ(0.11, 0.3, 24), mat.metal, 0, R, 0)); // crankpin
  crankArm.add(mesh(new THREE.TorusGeometry(0.43, 0.008, 6, 48, Math.PI), mat.accent, 0, 0, 0.27));
  W.add(crank);
  P('crank-0', 'crank', 'crank', crank, { explode: [XR, -0.15, 0.35], glide: [0, 0, 1.2], label: 1, labelAt: [0.42, -0.2, 0.3] });
  const mainBrgs = [-0.4, -0.75].map((z, i) => { const g = grp(0, Y0, z, mesh(ringGeo(0.13, 0.22, 0.12), mat.brass)); W.add(g); P(`mainbrg-${i}`, 'mainbrg', 'crank', g, { explode: [XR, -0.15, 1.05 + i * 0.4], glide: [0, 0, 1.2], label: i ? 0 : 2, labelAt: [0.2, 0, 0] }); return g; });
  void mainBrgs;
  const flyArm = new THREE.Group(); const fly = grp(0, Y0, -1.05, flyArm);
  flyArm.add(mesh(ringGeo(0.14, 0.82, 0.14, 64), mat.steel), mesh(ringGeo(0.66, 0.84, 0.22, 64), mat.metal));
  for (let k = 0; k < 5; k++) { const a = (k / 5) * Math.PI * 2; flyArm.add(mesh(cylZ(0.09, 0.16, 16), mat.dark, Math.cos(a) * 0.42, Math.sin(a) * 0.42, 0)); }
  flyArm.add(mesh(new THREE.TorusGeometry(0.84, 0.01, 6, 64), mat.accent, 0, 0, -0.115));
  W.add(fly);
  P('fly-0', 'fly', 'crank', fly, { explode: [XR, -0.15, -0.55], glide: [0, 0, 1.2], label: 1, labelAt: [-0.84, 0.3, 0] });
  // ---- piston, rings, pin, rod ----
  const PH = 0.55;
  const pistonIn = grp(0, 0, 0, mesh(new THREE.CylinderGeometry(BORE - 0.01, BORE - 0.01, PH, 40), mat.metal, 0, 0.12, 0), mesh(new THREE.CylinderGeometry(BORE - 0.012, BORE - 0.012, 0.012, 40), mat.accent, 0, 0.12 + PH / 2, 0));
  const piston = grp(0, 0, 0, pistonIn); W.add(piston);
  const pPiston = P('piston-0', 'piston', 'piston', piston, { explode: [XL, 0.35, 0.3], glide: [0, 0, 1.4], label: 1, labelAt: [0.3, 3, 0.25] });
  const ringsIn = new THREE.Group(); [0.33, 0.25, 0.17].forEach((y, i) => ringsIn.add(mesh(new THREE.TorusGeometry(BORE - 0.006, 0.012, 6, 48), i === 2 ? mat.dark : mat.steel, 0, y, 0))); ringsIn.children.forEach((c) => (c.rotation.x = Math.PI / 2));
  const rings = grp(0, 0, 0, ringsIn); W.add(rings);
  const pRings = P('rings-0', 'rings', 'piston', rings, { explode: [XL, 1.05, 0.3], glide: [0, 0, 1.4], label: 2, labelAt: [-BORE, 0.33, 0] });
  const pinIn = grp(0, 0, 0, mesh(cylZ(0.07, 0.7, 20), mat.steel)); const pin = grp(0, 0, 0, pinIn); W.add(pin);
  const pPin = P('pin-0', 'pin', 'piston', pin, { explode: [XL + 0.75, 0.35, 0.3], glide: [0, 0, 1.4], label: 2 });
  const rodIn = new THREE.Group();
  const shank = new THREE.Shape(); shank.moveTo(-0.07, 0); shank.lineTo(-0.11, -LR); shank.lineTo(0.11, -LR); shank.lineTo(0.07, 0); shank.closePath();
  const sg = new THREE.ExtrudeGeometry(shank, { depth: 0.12, bevelEnabled: false }); sg.translate(0, 0, -0.06);
  rodIn.add(mesh(sg, mat.steel), mesh(ringGeo(0.07, 0.14, 0.14), mat.steel), mesh(ringGeo(0.11, 0.21, 0.16), mat.steel, 0, -LR, 0), mesh(ringGeo(0.11, 0.125, 0.165), mat.brass, 0, -LR, 0));
  rodIn.add(box(0.012, LR - 0.4, 0.125, mat.accent, 0, -LR / 2, 0));
  const rod = grp(0, 0, 0, rodIn); W.add(rod);
  const pRod = P('rod-0', 'rod', 'piston', rod, { explode: [XL, -0.35, 0.3], glide: [0, 0, 1.4], label: 1, labelAt: [0.15, -1.0, 0] });
  // ---- head ----
  const HY0 = CY1, HY1 = CY1 + 0.5;
  const head = new THREE.Group();
  head.add(box(1.35, HY1 - HY0, 0.68, mat.panel, 0, (HY0 + HY1) / 2, -0.34 + 0.0)); // back half of the head (cut on z = 0)
  head.add(box(1.35, HY1 - HY0, 0.01, mat.panelDark, 0, (HY0 + HY1) / 2, 0.006), box(1.35, 0.008, 0.012, mat.accent, 0, HY1 - 0.004, 0.008));
  [-1, 1].forEach((s) => head.add(box(0.2, HY1 - HY0, 0.68, mat.panel, s * 0.575, (HY0 + HY1) / 2, 0.34)));
  W.add(head);
  P('head-0', 'head', 'block', head, { explode: [0, 0.9, 0], label: 1, labelAt: [0.67, HY1, -0.3] });
  const hb = []; [[-0.55, -0.5], [0.55, -0.5], [-0.55, 0.5], [0.55, 0.5]].forEach(([x, z], i) => { const b = grp(x, HY1 + 0.02, z, mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 6), mat.dark, 0, 0.03, 0), mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.7, 10), mat.metal, 0, -0.35, 0)); W.add(b); hb.push(b); P(`headbolt-${i}`, 'headbolt', 'block', b, { explode: [x * 0.25, 1.75, z * 0.25], label: i === 1 ? 2 : 0, labelAt: [0, 0.06, 0] }); });
  const plug = grp(0.32, HY1 - 0.05, 0.22, mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.3, 12), mat.metal, 0, 0.12, 0), mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.12, 6), mat.steel, 0, 0.32, 0), mesh(new THREE.CylinderGeometry(0.045, 0.06, 0.32, 16), new THREE.MeshPhysicalMaterial({ color: 0xf1efe8, roughness: 0.3, clearcoat: 0.8 }), 0, 0.54, 0), mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.06, 8), mat.copper, 0, -0.06, 0));
  plug.rotation.z = -0.35; W.add(plug);
  const spark = mesh(new THREE.SphereGeometry(0.06, 12, 8), new THREE.MeshBasicMaterial({ color: new THREE.Color(AMBER), transparent: true, opacity: 0 }), 0.05, HY0 + 0.03, 0.15); spark.userData.noShadow = true; W.add(spark);
  P('plug-0', 'plug', 'ignition', plug, { explode: [1.35, 1.6, 0.2], glide: IGN, label: 1, labelAt: [0, 0.7, 0] });
  // ignition coil on the side of the head, and the HT lead over to the plug's cap
  const coil = grp(1.0, HY0 - 0.05, 0.25, box(0.24, 0.42, 0.24, mat.dark, 0, 0.21, 0), mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.08, 12), mat.steel, 0, 0.46, 0), box(0.245, 0.012, 0.245, mat.accent, 0, 0.3, 0));
  W.add(coil);
  P('coil-0', 'coil', 'ignition', coil, { explode: [2.0, 0.55, 0], glide: IGN, label: 2, labelAt: [0.12, 0.25, 0] });
  const capW = new THREE.Vector3(0, 0.7, 0).applyAxisAngle(new THREE.Vector3(0, 0, 1), -0.35).add(new THREE.Vector3(0.32, HY1 - 0.05, 0.22));
  const leadCurve = new THREE.CatmullRomCurve3([new THREE.Vector3(1.0, HY0 + 0.45, 0.25), new THREE.Vector3(1.0, HY0 + 0.85, 0.25), new THREE.Vector3(0.82, capW.y + 0.22, 0.24), capW.clone().add(new THREE.Vector3(0.04, 0.05, 0))]);
  const lead = grp(0, 0, 0, mesh(new THREE.TubeGeometry(leadCurve, 40, 0.022, 8), new THREE.MeshStandardMaterial({ color: 0x1b1d19, roughness: 0.7, metalness: 0 })));
  W.add(lead);
  P('lead-0', 'lead', 'ignition', lead, { explode: [1.7, 1.05, 0.1], glide: IGN, label: 2, labelAt: [0.9, HY0 + 0.9, 0.25] });
  // ---- valvetrain: camshaft along z above the valves, half crank speed ----
  const CAMY = HY1 + 0.55, VZ = [-0.22, 0.2];
  const camArm = new THREE.Group(); const cam = grp(0, CAMY, 0, camArm);
  camArm.add(mesh(cylZ(0.07, 1.6, 20), mat.metal, 0, 0, -0.45));
  const lobe = () => { const s = new THREE.Shape(); s.absarc(0, 0, 0.14, Math.PI * 0.2, Math.PI * 0.8, true); s.lineTo(-0.06, -0.26); s.absarc(0, -0.26, 0.06, Math.PI, 0, false); s.closePath(); const g = new THREE.ExtrudeGeometry(s, { depth: 0.1, bevelEnabled: false, curveSegments: 10 }); g.translate(0, 0, -0.05); return g; };
  // lobe nose at -y (pointing down) when rotation = 0; inlet nose down at crank 90°, exhaust at crank 630°
  const LOBE = [Math.PI / 4, (7 * Math.PI) / 4];
  VZ.forEach((z, i) => { const m = mesh(lobe(), mat.steel, 0, 0, z); camArm.add(m); m.rotation.z = LOBE[i]; });
  W.add(cam);
  P('cam-0', 'cam', 'valves', cam, { explode: [0, 1.5, 0], glide: VT, label: 1, labelAt: [0, 0.1, 0.35] });
  // sprockets and chain at the back
  const SZ = -0.75, sMat = mat.dark;
  const sprC = grp(0, Y0, SZ, mesh(gearGeometry({ m: 0.03, z: 18, width: 0.06, bore: 0.05 }).geo, sMat));
  const sprM = grp(0, CAMY, SZ, mesh(gearGeometry({ m: 0.03, z: 36, width: 0.06, bore: 0.05 }).geo, sMat));
  const r1 = 0.27, r2 = 0.54, Lc = CAMY - Y0;
  const chainG = new THREE.Group();
  const a = Math.asin((r2 - r1) / Lc);
  [-1, 1].forEach((s) => { const x1 = s * r1 * Math.cos(a), y1 = Y0 - r1 * Math.sin(a) * -1, x2 = s * r2 * Math.cos(a), y2 = CAMY + r2 * Math.sin(a); const len = Math.hypot(x2 - x1, y2 - y1); const run = box(0.04, len, 0.05, mat.panelDark, (x1 + x2) / 2, (y1 + y2) / 2, SZ); run.rotation.z = -Math.atan2(x2 - x1, y2 - y1); chainG.add(run); });
  chainG.add(mesh(new THREE.TorusGeometry(r1 + 0.02, 0.022, 6, 32, Math.PI), mat.panelDark, 0, Y0, SZ), mesh(new THREE.TorusGeometry(r2 + 0.02, 0.022, 6, 48, Math.PI), mat.panelDark, 0, CAMY, SZ));
  chainG.children[2].rotation.z = Math.PI;
  const chain = grp(0, 0, 0, chainG, sprC, sprM); W.add(chain);
  P('chain-0', 'chain', 'valves', chain, { explode: [-1.75, 0.3, -0.2], glide: VT, label: 1, labelAt: [-0.3, (Y0 + CAMY) / 2, SZ] });
  // valves: head disc at the deck, stem up to the cam, spring round the stem
  const VLEN = CAMY - 0.26 - (HY0 + 0.02);
  const mkValve = (key, z, i) => {
    const vin = grp(0, 0, 0, mesh(new THREE.CylinderGeometry(0.03, 0.03, VLEN, 10), mat.metal, 0, VLEN / 2, 0), mesh(new THREE.CylinderGeometry(0.13, 0.04, 0.06, 24), mat.metal, 0, 0.03, 0), mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.03, 16), mat.steel, 0, VLEN - 0.02, 0));
    vin.children[1].material = i ? new THREE.MeshPhysicalMaterial({ color: 0x8a5a3a, roughness: 0.4, metalness: 0.9 }) : mat.metal;
    const v = grp(0, HY0 + 0.02, z, vin); W.add(v);
    const pv = P(`${key}-0`, key, 'valves', v, { explode: [0, 1.05, 0], glide: VT, label: 1, labelAt: [0, VLEN * 0.55, 0] });
    const pts = []; const turns = 7, sh = 0.42, sr = 0.075; for (let k = 0; k <= turns * 24; k++) { const u = k / 24; pts.push(new THREE.Vector3(Math.cos(u * Math.PI * 2) * sr, (u / turns) * sh, Math.sin(u * Math.PI * 2) * sr)); }
    const coil = mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), turns * 24, 0.012, 5), i ? mat.accent : mat.steel);
    const spIn = grp(0, 0, 0, coil); const sp = grp(0, HY1 + 0.02, z, spIn); W.add(sp);
    P(`spring-${i}`, 'spring', 'valves', sp, { explode: [0, 1.15, 0], glide: VT, label: i ? 0 : 2, labelAt: [0.08, 0.2, 0] });
    return { vin, spIn, coil, sh, pv };
  };
  const valves = [mkValve('valveIn', VZ[0], 0), mkValve('valveEx', VZ[1], 1)];
  const cover = grp(0, CAMY + 0.02, -0.35, box(1.0, 0.36, 0.9, mat.panelDark, 0, 0, 0));
  W.add(cover);
  P('cover-0', 'cover', 'block', cover, { explode: [0, 2.15, 0.35], label: 2, labelAt: [0.5, 0.18, 0] });
  contact.scale.set(4.5, 3.5, 1); contact.position.set(0, 0.003, -0.2); contact.material.opacity = 0.6;
  const LIFT = 0.1;
  model.update = () => {
    const th = model.theta || 0;
    crankArm.rotation.z = -th; flyArm.rotation.z = -th; sprC.rotation.z = -th; // crank pin at (R sinθ, R cosθ)
    const py = pinY(th), cx = R * Math.sin(th), cy = Y0 + R * Math.cos(th);
    pistonIn.position.y = py; ringsIn.position.y = py; pinIn.position.y = py;
    // labels ride on the moving parts
    pPiston.labelAt.set(0.3, py + 0.4, 0.25); pRings.labelAt.set(-BORE, py + 0.33, 0); pPin.labelAt.set(0, py, 0.35); pRod.labelAt.set((cx) / 2 + 0.1, (py + cy) / 2, 0.06);
    rodIn.position.set(0, py, 0); rodIn.rotation.z = Math.atan2(cx, py - cy);
    const camRot = -th / 2; camArm.rotation.z = camRot; sprM.rotation.z = camRot;
    // the lobe nose points down at its valve at the middle of the opening; lift follows the same half-sine as the telemetry
    [liftIn(th), liftEx(th)].forEach((k, i) => {
      const lift = LIFT * k;
      valves[i].vin.position.y = -lift; valves[i].pv.labelAt.y = VLEN * 0.55 - lift; valves[i].spIn.scale.y = (valves[i].sh - lift) / valves[i].sh;
    });
    const intoPower = wrap(th) - 2 * Math.PI;
    spark.material.opacity = model.firing && intoPower >= 0 && intoPower < 0.5 ? 0.9 * (1 - intoPower / 0.5) : 0;
  };
  model.update();
  return model;
}
