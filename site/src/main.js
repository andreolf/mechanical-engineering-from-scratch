import './style.css';
import { initHero } from './hero-beam.js';
import { initTruss } from './lab-truss.js';
import { initGyro } from './lab-gyro.js';
import { initPipe } from './lab-pipe.js';
import { initPhaseMap } from './phase-map.js';

window.__mefs = window.__mefs || {};
const safe = (name, fn) => { try { return fn(); } catch (e) { console.warn(`[${name}] failed to start`, e); } };

safe('hero', () => initHero(document.querySelector('#hero')));
safe('truss', () => initTruss(document.querySelector('#lab-truss')));
safe('gyro', () => initGyro(document.querySelector('#lab-flywheel')));
safe('pipe', () => initPipe(document.querySelector('#lab-pipe')));

document.querySelectorAll('[data-copy]').forEach((btn) => {
  btn.addEventListener('click', async () => {
    const text = document.querySelector(btn.dataset.copy).textContent.trim();
    try { await navigator.clipboard.writeText(text); btn.textContent = 'copied'; } catch { btn.textContent = 'select & copy'; }
    setTimeout(() => (btn.textContent = 'copy'), 1500);
  });
});

fetch('./curriculum.json')
  .then((r) => r.json())
  .then((data) => {
    document.querySelectorAll('[data-count=phases]').forEach((e) => (e.textContent = data.phaseCount));
    document.querySelectorAll('[data-count=lessons]').forEach((e) => (e.textContent = data.lessonCount));
    initPhaseMap(document.querySelector('#curriculum'), data);
    window.__mefs.curriculumReady = true;
    if (location.hash.startsWith('#phase-')) document.querySelector(location.hash)?.scrollIntoView();
  })
  .catch((e) => {
    document.querySelector('#phase-grid').innerHTML = '<p class="fine">Could not load curriculum.json. If you opened index.html from disk, run <code>npm run dev</code> instead.</p>';
    console.warn(e);
  });
