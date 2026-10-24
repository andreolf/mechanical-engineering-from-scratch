// Phase map rendered from curriculum.json, with search and browser-only progress.
const KEY = 'mefs.progress.v1';
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

export function loadProgress() {
  try { return new Set(JSON.parse(localStorage.getItem(KEY) || '[]')); } catch { return new Set(); }
}
function saveProgress(set) { try { localStorage.setItem(KEY, JSON.stringify([...set])); } catch { /* storage blocked */ } }

export function initPhaseMap(root, data) {
  const grid = root.querySelector('#phase-grid');
  const search = root.querySelector('#lesson-search');
  const count = root.querySelector('#search-count');
  const stats = root.querySelector('#progress-stats');
  const reset = root.querySelector('#progress-reset');
  const done = loadProgress();

  grid.innerHTML = data.phases.map((p) => `
    <article class="phase" id="phase-${p.id}" data-phase="${p.id}">
      <button class="phase-head" aria-expanded="false" aria-controls="phase-body-${p.id}">
        <span class="phase-num">${p.id}</span>
        <span class="phase-title"><strong>${esc(p.title)}</strong><em>${esc(p.de)}</em></span>
        <span class="phase-meta"><span class="phase-count">${p.lessons.length} lessons</span><span class="bar"><i style="width:0%"></i></span></span>
      </button>
      <div class="phase-body" id="phase-body-${p.id}" hidden>
        <p class="phase-summary">${esc(p.summary)}</p>
        <p class="phase-eth"><span>ETH reference</span> ${esc(p.eth)}${p.ethNamed ? '' : ' <small>(generic)</small>'} · <span>Anchors</span> ${esc(p.anchor)}</p>
        <ol class="lessons">
          ${p.lessons.map((l) => `
          <li class="lesson" data-id="${l.id}" data-text="${esc((l.title + ' ' + l.goal + ' ' + l.tool + ' ' + l.lab + ' ' + l.math + ' ' + l.code).toLowerCase())}">
            <div class="lesson-row">
              <label class="check"><input type="checkbox" data-lesson="${l.id}" aria-label="Mark ${esc(l.id)} ${esc(l.title)} done"><span></span></label>
              <button class="lesson-toggle" aria-expanded="false"><span class="lid">${l.id}</span> ${esc(l.title)}</button>
            </div>
            <dl class="lesson-detail" hidden>
              <dt>Goal</dt><dd>${esc(l.goal)}</dd>
              <dt>Derive</dt><dd>${esc(l.math)}</dd>
              <dt>Code</dt><dd>${esc(l.code)}</dd>
              <dt>Lab</dt><dd>${esc(l.lab)}${l.labLinks.map((k) => ` <a href="${esc(k.url)}" ${k.url.startsWith('http') ? 'target="_blank" rel="noopener"' : ''}>${esc(k.title)} ↗</a>`).join('')}</dd>
              <dt>Test</dt><dd>${esc(l.test)}</dd>
              <dt>Pro tool</dt><dd>${esc(l.tool)}</dd>
              <dt>ETH</dt><dd>${esc(l.eth)}</dd>
            </dl>
          </li>`).join('')}
        </ol>
      </div>
    </article>`).join('');

  const setOpen = (art, open) => {
    art.classList.toggle('open', open);
    art.querySelector('.phase-head').setAttribute('aria-expanded', open);
    art.querySelector('.phase-body').hidden = !open;
  };
  grid.addEventListener('click', (e) => {
    const head = e.target.closest('.phase-head');
    if (head) { const art = head.closest('.phase'); setOpen(art, !art.classList.contains('open')); return; }
    const tog = e.target.closest('.lesson-toggle');
    if (tog) {
      const dl = tog.closest('.lesson').querySelector('.lesson-detail');
      dl.hidden = !dl.hidden; tog.setAttribute('aria-expanded', !dl.hidden);
    }
  });
  const refresh = () => {
    let total = 0, complete = 0;
    for (const p of data.phases) {
      const n = p.lessons.filter((l) => done.has(l.id)).length;
      total += n;
      if (n === p.lessons.length) complete++;
      const art = grid.querySelector(`#phase-${p.id}`);
      art.querySelector('.bar i').style.width = `${(100 * n) / p.lessons.length}%`;
      art.querySelector('.phase-count').textContent = n ? `${n}/${p.lessons.length} done` : `${p.lessons.length} lessons`;
      art.classList.toggle('complete', n === p.lessons.length);
    }
    stats.innerHTML = `<span><b data-k="done">${total}</b> / ${data.lessonCount} lessons</span><span><b>${complete}</b> / ${data.phaseCount} phases</span>`;
  };
  grid.querySelectorAll('input[data-lesson]').forEach((cb) => { cb.checked = done.has(cb.dataset.lesson); });
  grid.addEventListener('change', (e) => {
    const cb = e.target.closest('input[data-lesson]');
    if (!cb) return;
    cb.checked ? done.add(cb.dataset.lesson) : done.delete(cb.dataset.lesson);
    saveProgress(done); refresh();
  });
  reset.addEventListener('click', () => {
    done.clear(); saveProgress(done);
    grid.querySelectorAll('input[data-lesson]').forEach((cb) => (cb.checked = false));
    refresh();
  });
  let tmr;
  search.addEventListener('input', () => {
    clearTimeout(tmr);
    tmr = setTimeout(() => {
      const q = search.value.trim().toLowerCase();
      let hits = 0;
      grid.querySelectorAll('.phase').forEach((art) => {
        let n = 0;
        art.querySelectorAll('.lesson').forEach((li) => {
          const m = !q || li.dataset.text.includes(q);
          li.hidden = !m; if (m) n++;
        });
        hits += q ? n : 0;
        art.hidden = !!q && n === 0;
        setOpen(art, !!q && n > 0);
      });
      count.textContent = q ? `${hits} lesson${hits === 1 ? '' : 's'} match “${search.value.trim()}”` : '';
    }, 120);
  });
  refresh();
}
