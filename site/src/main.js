import './styles/base.css';
import './styles/home.css';
import { initHero } from './hero-beam.js';
import { initTruss } from './lab-truss.js';
import { initGyro } from './lab-gyro.js';
import { initPipe } from './lab-pipe.js';
import { renderPhaseMap } from './phase-map.js';
import { renderNav, renderFooter } from './chrome.js';
import { whenNear } from './stage.js';

window.__mefs = window.__mefs || {};
renderNav('home');
renderFooter('home');
const safe = (name, fn) => { try { return fn(); } catch (e) { console.warn(`[${name}] failed to start`, e); } };

safe('hero', () => initHero(document.querySelector('#hero')));
// Labs start only when they come near the viewport, which saves battery on phones.
[['#lab-truss', initTruss], ['#lab-flywheel', initGyro], ['#lab-pipe', initPipe]].forEach(([sel, init]) => {
  const el = document.querySelector(sel);
  whenNear(el, () => safe(sel, () => init(el)));
});

// Take-apart labs: three.js and the models load only when the slot comes near the viewport,
// or at once when the address asks for one (#lab-gearbox, #lab-engine).
const TA = { gearbox: () => import('./lab-gearbox.js').then((m) => m.initGearbox), engine: () => import('./lab-engine.js').then((m) => m.initEngine) };
const taStarted = {};
function startTA(id) {
  const el = document.querySelector(`#ta-${id}-slot`);
  if (!el) return Promise.resolve(null);
  return (taStarted[id] ||= TA[id]().then((init) => safe(id, () => init(el))).catch((e) => console.warn(`[${id}] failed to load`, e)));
}
function taDeepLink() {
  const m = location.hash.match(/^#lab-(\w+)$/);
  if (!m || !TA[m[1]]) return;
  // labs above the target load as it scrolls past them and grow, so keep the target pinned until the page settles
  // (about 4 s) or the reader scrolls on their own
  startTA(m[1]).then(() => {
    const go = () => document.querySelector(location.hash)?.scrollIntoView({ block: 'start' });
    requestAnimationFrame(go);
    const ro = new ResizeObserver(() => requestAnimationFrame(go));
    document.querySelectorAll('.ta-slot, .ta-band').forEach((s) => ro.observe(s));
    const evs = ['wheel', 'touchstart', 'keydown', 'pointerdown'];
    const stop = () => { ro.disconnect(); evs.forEach((e) => removeEventListener(e, stop)); };
    evs.forEach((e) => addEventListener(e, stop, { passive: true }));
    setTimeout(stop, 4000);
  });
}
Object.keys(TA).forEach((id) => { const el = document.querySelector(`#ta-${id}-slot`); if (el) whenNear(el, () => startTA(id)); });
taDeepLink();
window.addEventListener('hashchange', taDeepLink);

document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const text = document.querySelector(btn.dataset.copy).textContent.trim();
    try { await navigator.clipboard.writeText(text); btn.textContent = 'Copied'; } catch { btn.textContent = 'Select and copy'; }
    setTimeout(() => (btn.textContent = 'Copy'), 1500);
  });
});

Promise.all([fetch('./curriculum.json').then((r) => r.json()), fetch('./lessons/index.json').then((r) => r.json()).catch(() => ({ written: [] }))])
  .then(([data, written]) => {
    document.querySelectorAll('[data-count=phases]').forEach((e) => (e.textContent = data.phaseCount));
    document.querySelectorAll('[data-count=lessons]').forEach((e) => (e.textContent = data.lessonCount));
    document.querySelectorAll('[data-count=written]').forEach((e) => (e.textContent = written.written.length));
    renderPhaseMap(document.querySelector('#phase-map'), data, written);
    window.__mefs.curriculumReady = true;
    if (location.hash.startsWith('#phase-')) document.querySelector(location.hash)?.scrollIntoView();
  })
  .catch((e) => {
    document.querySelector('#phase-map').innerHTML = '<p class="muted">The course list couldn’t load. If you opened index.html straight from disk, run <code>npm run dev</code> and open the local address instead.</p>';
    console.warn(e);
  });
