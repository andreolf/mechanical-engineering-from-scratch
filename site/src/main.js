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
