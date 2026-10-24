// Phase list rendered from curriculum.json and lessons/index.json, with lesson search.
import { load, doneCount } from './store.js';
import './styles/phase-map.css';
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function renderPhaseMap(host, data, written, { linkBase = 'learn.html' } = {}) {
  const s = load();
  const w = new Set(written.written || []);
  const totalDone = doneCount(s, data.phases.flatMap((p) => p.lessons.map((l) => l.id)));
  host.innerHTML = `
    <div class="map-tools">
      <label class="search"><span class="sr-only">Search lessons</span>
        <input id="lesson-search" type="search" name="lesson-search" autocomplete="off" spellcheck="false" placeholder="Search lessons, for example Bernoulli…" /></label>
      <p class="map-stats small muted num" id="progress-stats"><span data-k="done">${totalDone}</span> of ${data.lessonCount} lessons done</p>
    </div>
    <p id="search-count" class="small muted" aria-live="polite"></p>
    <ol class="phases">${data.phases.map((p) => {
      const ids = p.lessons.map((l) => l.id);
      const nW = ids.filter((id) => w.has(id)).length, nD = doneCount(s, ids);
      const status = nW === ids.length ? 'Full lessons' : nW ? `${nW} of ${ids.length} written` : 'Outline';
      return `<li class="phase" id="phase-${p.id}" data-phase="${p.id}">
        <button type="button" class="phase-head" aria-expanded="false" aria-controls="phase-body-${p.id}">
          <span class="phase-num num">${p.id}</span>
          <span class="phase-title"><strong>${esc(p.title)}</strong><span class="phase-sub">${esc(p.de)}</span></span>
          <span class="phase-meta"><span class="pill ${nW === ids.length ? 'pill-on' : nW ? 'pill-part' : ''}">${status}</span><span class="phase-count num">${nD ? `${nD}/${ids.length} done` : `${ids.length} lessons`}</span></span>
          <span class="chev" aria-hidden="true"></span>
        </button>
        <div class="phase-body" id="phase-body-${p.id}" hidden>
          <p class="phase-summary">${esc(p.summary)}</p>
          <p class="phase-eth small muted">Mirrors: ${esc(p.eth)}${p.ethNamed ? '' : ' (generic description)'}. Anchors: ${esc(p.anchor)}.</p>
          <ol class="lesson-list">${p.lessons.map((l) => `
            <li class="lesson-item" data-id="${l.id}" data-text="${esc((l.id + ' ' + l.title + ' ' + l.goal + ' ' + l.tool + ' ' + l.lab + ' ' + l.math).toLowerCase())}">
              <a href="${linkBase}#/${l.id}"><span class="lid num">${l.id}</span><span class="lt">${esc(l.title)}</span>
              <span class="ls">${s.lessons[l.id]?.done ? '<span class="dot dot-done" title="Done"></span><span class="sr-only">Done</span>' : w.has(l.id) ? '<span class="tag-full">Full lesson</span>' : '<span class="tag-outline">Outline</span>'}</span></a>
            </li>`).join('')}
          </ol>
          ${nW ? `<p class="phase-actions"><a class="btn-small" href="${linkBase}#/test/${p.id}">Phase ${p.id} test</a></p>` : ''}
        </div>
      </li>`; }).join('')}
    </ol>`;
  const setOpen = (li, open) => {
    li.classList.toggle('open', open);
    li.querySelector('.phase-head').setAttribute('aria-expanded', String(open));
    li.querySelector('.phase-body').hidden = !open;
  };
  host.addEventListener('click', (e) => {
    const head = e.target.closest('.phase-head');
    if (head) { const li = head.closest('.phase'); setOpen(li, !li.classList.contains('open')); }
  });
  const search = host.querySelector('#lesson-search'), count = host.querySelector('#search-count');
  let tmr;
  search.addEventListener('input', () => {
    clearTimeout(tmr);
    tmr = setTimeout(() => {
      const q = search.value.trim().toLowerCase();
      let hits = 0;
      host.querySelectorAll('.phase').forEach((li) => {
        let n = 0;
        li.querySelectorAll('.lesson-item').forEach((it) => { const m = !q || it.dataset.text.includes(q); it.hidden = !m; if (m) n++; });
        hits += q ? n : 0;
        li.hidden = !!q && n === 0;
        setOpen(li, !!q && n > 0);
      });
      count.textContent = q ? `${hits} ${hits === 1 ? 'lesson matches' : 'lessons match'} “${search.value.trim()}”` : '';
    }, 120);
  });
}
