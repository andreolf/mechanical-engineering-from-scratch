import 'katex/dist/katex.min.css';
import '../styles/base.css';
import '../styles/learn.css';
import { renderNav, renderFooter, refreshXp } from '../chrome.js';
import { load, save, setLessonDone, recordQuiz, recordTest, streak, level, doneCount, today, PASS_MARK, XP } from '../store.js';
import { renderQuiz } from './quiz.js';
import { mountWidgets } from './widgets.js';
import { certCode, drawCertificate, canvasToPdf } from './cert.js';
import { renderPhaseMap } from '../phase-map.js';

const app = document.getElementById('app');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
window.__mefs = window.__mefs || {};
renderFooter('learn');

let curriculum, index;
const phaseCache = {};
const ready = Promise.all([
  fetch('./curriculum.json').then((r) => r.json()),
  fetch('./lessons/index.json').then((r) => r.json()).catch(() => ({ written: [], phases: {} })),
]).then(([c, i]) => { curriculum = c; index = i; });
async function phaseData(ph) {
  if (!index.phases[ph]) return null;
  return (phaseCache[ph] ||= fetch(`./lessons/${ph}.json`).then((r) => r.json()));
}
const allLessons = () => curriculum.phases.flatMap((p) => p.lessons.map((l) => ({ ...l, phase: p })));
const written = () => new Set(index.written);
const dateLabel = (iso) => new Intl.DateTimeFormat('en-GB', { day: 'numeric', month: 'long', year: 'numeric' }).format(new Date(iso + 'T12:00:00'));
function setTitle(t) { document.title = `${t} | Mechanical Engineering from Scratch`; }

async function route() {
  await ready;
  const h = decodeURIComponent(location.hash.replace(/^#\/?/, '')) || 'course';
  const [a, b] = h.split('/');
  let page = 'course';
  try {
    if (/^\d\d\.\d\d$/.test(a)) { page = 'lesson'; await viewLesson(a); }
    else if (a === 'progress') { page = 'progress'; viewProgress(); }
    else if (a === 'test' && /^\d\d$/.test(b)) { page = 'progress'; await viewTest(b); }
    else if (a === 'cert') { page = 'progress'; await viewCert(b || 'course'); }
    else if (a === 'verify') { page = 'progress'; viewVerify(); }
    else viewCourse();
  } catch (e) {
    console.warn(e);
    app.innerHTML = `<div class="wrap page"><h1>This page couldn’t load</h1><p>Check your connection and reload. If it keeps failing, <a href="https://github.com/andreolf/mechanical-engineering-from-scratch/issues">report it on GitHub</a>.</p></div>`;
  }
  renderNav(page);
  document.body.classList.toggle('in-lesson', page === 'lesson');
  window.scrollTo(0, 0);
  app.focus({ preventScroll: true });
  window.__mefs.route = h;
}
window.addEventListener('hashchange', route);
route();

/* ---------- Course overview ---------- */
function viewCourse() {
  setTitle('Course');
  app.innerHTML = `<div class="wrap page"><h1>All phases and lessons</h1>
    <p class="lede">${curriculum.phaseCount} phases and ${curriculum.lessonCount} lessons. ${index.written.length === curriculum.lessonCount ? 'Every one is a full lesson' : `${index.written.length} are full lessons`} with derivations, code, exercises and a quiz.</p>
    <div id="phase-map"></div></div>`;
  renderPhaseMap(app.querySelector('#phase-map'), curriculum, index, { linkBase: 'learn.html' });
  window.__mefs.curriculumReady = true;
}

/* ---------- Lesson ---------- */
async function viewLesson(id) {
  const list = allLessons();
  const i = list.findIndex((l) => l.id === id);
  if (i < 0) { app.innerHTML = `<div class="wrap page"><h1>Lesson ${esc(id)} doesn’t exist</h1><p><a href="#/course">See all lessons</a></p></div>`; return; }
  const meta = list[i], phase = meta.phase, prev = list[i - 1], next = list[i + 1];
  const data = await phaseData(phase.id);
  const full = data?.lessons[id];
  const s = load();
  setTitle(`${id} ${meta.title}`);
  const W = written();
  const side = phase.lessons.map((l) => `<li><a href="#/${l.id}" ${l.id === id ? 'aria-current="page"' : ''}><span class="num">${l.id}</span><span>${esc(l.title)}</span>${s.lessons[l.id]?.done ? '<i class="dot-done" aria-label="done"></i>' : W.has(l.id) ? '' : '<em>outline</em>'}</a></li>`).join('');
  const navBtn = (l, dir) => l ? `<a class="pn pn-${dir}" href="#/${l.id}"><span class="small muted">${dir === 'prev' ? 'Previous' : 'Next'}</span><span class="pn-t"><span class="num">${l.id}</span> ${esc(l.title)}</span></a>` : '<span></span>';
  app.innerHTML = `
  <div class="lesson-bar" id="lesson-bar">
    <div class="wrap lesson-bar-in">
      <button type="button" class="btn-small" id="toc-btn" aria-expanded="false" aria-controls="lesson-side">Phase ${phase.id} lessons</button>
      <span class="lb-title num">${id}</span>
      <a class="btn-small" href="${next ? `#/${next.id}` : '#/course'}" aria-label="Next lesson">Next</a>
    </div>
    <div class="read-progress" aria-hidden="true"><i></i></div>
  </div>
  <div class="wrap lesson-layout">
    <aside class="lesson-side" id="lesson-side" aria-label="Lessons in phase ${phase.id}">
      <p class="side-phase"><a href="#/course">Phase ${phase.id}</a><span>${esc(phase.title)}</span></p>
      <ol>${side}</ol>
    </aside>
    <article class="lesson ${full ? 'is-full' : 'is-outline'}" aria-labelledby="lesson-title">
      <header class="lesson-head">
        <p class="crumb small"><a href="#/course">Phase ${phase.id}: ${esc(phase.title)}</a></p>
        <h1 id="lesson-title"><span class="lesson-id num">${id}</span> ${esc(meta.title)}</h1>
        <p class="lesson-goal">${esc(meta.goal)}</p>
        <dl class="lesson-meta small">
          ${full ? `<div><dt>Reading time</dt><dd class="num">${full.minutes} min</dd></div>` : '<div><dt>Status</dt><dd>Outline</dd></div>'}
          <div><dt>ETH course</dt><dd>${esc(meta.eth)}</dd></div>
          <div><dt>Pro tool</dt><dd>${esc(meta.tool)}</dd></div>
        </dl>
      </header>
      ${full ? `<div class="prose">${full.html}</div>
        <section class="quiz-wrap" id="check-yourself" aria-label="Quiz"></section>
        <section class="complete" id="complete"></section>`
      : `<div class="coming">
          <p class="coming-title">Lesson outline</p>
          <p>The full text of this lesson didn’t load. Here is its outline; reload the page to try again.</p>
          <dl class="outline">
            <dt>Derive by hand</dt><dd>${esc(meta.math)}</dd>
            <dt>Code from scratch</dt><dd>${esc(meta.code)}</dd>
            <dt>Interactive lab</dt><dd>${esc(meta.lab)}${(meta.labLinks || []).map((k) => ` <a href="${k.url.startsWith('#') ? 'index.html' + k.url : k.url}">${esc(k.title)}</a>`).join('')}</dd>
            <dt>Test that proves it</dt><dd>${esc(meta.test)}</dd>
          </dl>
          ${firstWrittenAfter(list, i) ? `<p><a class="btn" href="#/${firstWrittenAfter(list, i).id}">Go to the next full lesson</a></p>` : `<p><a class="btn" href="#/00.01">Start from lesson 00.01</a></p>`}
        </div>`}
      <nav class="prevnext" aria-label="Lesson navigation">${navBtn(prev, 'prev')}${navBtn(next, 'next')}</nav>
    </article>
    ${full && full.sections.length ? `<nav class="lesson-toc" aria-label="On this page"><p class="small muted">On this page</p><ol>${full.sections.map((x) => `<li><a href="#/${id}" data-scroll="${x.id}">${esc(x.title)}</a></li>`).join('')}<li><a href="#/${id}" data-scroll="check-yourself">Check yourself</a></li></ol></nav>` : ''}
  </div>`;
  // mobile lesson drawer
  const tocBtn = app.querySelector('#toc-btn'), sideEl = app.querySelector('#lesson-side');
  tocBtn.addEventListener('click', () => { const open = !sideEl.classList.contains('open'); sideEl.classList.toggle('open', open); tocBtn.setAttribute('aria-expanded', String(open)); });
  sideEl.addEventListener('click', (e) => { if (e.target.closest('a')) sideEl.classList.remove('open'); });
  app.querySelectorAll('[data-scroll]').forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); document.getElementById(a.dataset.scroll)?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }); }));
  // reading progress
  const bar = app.querySelector('.read-progress i'), art = app.querySelector('article');
  const onScroll = () => { const r = art.getBoundingClientRect(); const p = Math.min(1, Math.max(0, -r.top / Math.max(1, r.height - innerHeight))); bar.style.transform = `scaleX(${p})`; };
  window.removeEventListener('scroll', window.__mefsScroll || (() => {}));
  window.__mefsScroll = onScroll; window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (!full) return;
  mountWidgets(app);
  app.querySelectorAll('[data-copy-code]').forEach((b) => b.addEventListener('click', async () => {
    const code = b.closest('figure').querySelector('code').innerText;
    try { await navigator.clipboard.writeText(code); b.textContent = 'Copied'; } catch { b.textContent = 'Select and copy'; }
    setTimeout(() => (b.textContent = 'Copy'), 1500);
  }));
  const quizHost = app.querySelector('#check-yourself');
  renderQuiz(quizHost, full.quiz, {
    title: 'Check yourself',
    onGraded: (c, t) => { const st = load(); recordQuiz(st, id, c, t); refreshXp(); renderComplete(); },
  });
  window.__mefs.lessonQuiz = full.quiz;
  const renderComplete = () => {
    const st = load(), rec = st.lessons[id] || {};
    app.querySelector('#complete').innerHTML = rec.done
      ? `<p class="done-line"><span class="dot-done" aria-hidden="true"></span> Lesson done${rec.at ? ` on ${dateLabel(rec.at)}` : ''}. ${rec.quizBest != null ? `Best quiz score ${rec.quizBest} of ${rec.quizTotal}.` : ''}</p>
         <div class="complete-actions">${next ? `<a class="btn btn-primary" href="#/${next.id}">Next: ${esc(next.title)}</a>` : ''}<button type="button" class="btn" data-undo>Mark as not done</button></div>`
      : `<p>Finished the derivation, ran the code and tried the exercises? Mark the lesson done to earn ${XP.lesson} XP and keep your streak.</p>
         <div class="complete-actions"><button type="button" class="btn btn-primary" data-done>Mark lesson as done</button></div>`;
    app.querySelector('[data-done]')?.addEventListener('click', () => { setLessonDone(load(), id, true); refreshXp(); renderComplete(); toast(`+${XP.lesson} XP. Lesson ${id} done.`); });
    app.querySelector('[data-undo]')?.addEventListener('click', () => { setLessonDone(load(), id, false); refreshXp(); renderComplete(); });
  };
  renderComplete();
}
function firstWrittenAfter(list, i) { const W = written(); return list.slice(i + 1).find((l) => W.has(l.id)) || list.find((l) => W.has(l.id)); }

function toast(msg) {
  let t = document.getElementById('toast');
  if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; t.setAttribute('role', 'status'); t.setAttribute('aria-live', 'polite'); document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), 2600);
}

/* ---------- Progress dashboard ---------- */
function viewProgress() {
  setTitle('Your progress');
  const s = load(), st = streak(s), lv = level(s.xp), W = written();
  const totalWritten = index.written.length;
  const doneWritten = index.written.filter((id) => s.lessons[id]?.done).length;
  const days = new Set(s.days);
  const cells = []; const d = new Date(); d.setDate(d.getDate() - 83);
  for (let k = 0; k < 84; k++) { const iso = today(d); cells.push(`<i class="${days.has(iso) ? 'on' : ''}" title="${iso}"></i>`); d.setDate(d.getDate() + 1); }
  const rows = curriculum.phases.map((p) => {
    const ids = p.lessons.map((l) => l.id), nW = ids.filter((x) => W.has(x)).length, nD = doneCount(s, ids);
    const t = s.tests[p.id];
    const testCell = !nW ? '<span class="muted">Not available yet</span>'
      : t?.passedAt ? `<span class="pass">Passed ${Math.round(t.best * 100)}%</span> <a class="btn-small" href="#/cert/${p.id}">Certificate</a>`
      : `${t ? `<span class="muted num">Best ${Math.round(t.best * 100)}%</span> ` : ''}<a class="btn-small" href="#/test/${p.id}">Take test</a>`;
    return `<li class="prow"><span class="pnum num">${p.id}</span><span class="ptitle">${esc(p.title)}<span class="bar"><i style="width:${(100 * nD) / ids.length}%"></i></span><span class="small muted num">${nD} of ${ids.length} done${nW && nW < ids.length ? `, ${nW} written` : !nW ? ', not written yet' : ''}</span></span><span class="ptest">${testCell}</span></li>`;
  }).join('');
  const passed = curriculum.phases.filter((p) => s.tests[p.id]?.passedAt).length;
  app.innerHTML = `<div class="wrap page">
    <h1>Your progress</h1>
    <p class="lede">Everything here is stored in this browser only. Clearing site data or switching device starts you from zero.</p>
    <div class="stats-grid">
      <div class="stat"><span class="stat-v num" data-stat="xp">${s.xp}</span><span class="stat-l">XP, level ${lv.level}</span><span class="bar"><i style="width:${(100 * lv.into) / lv.span}%"></i></span><span class="small muted num">${lv.span - lv.into} XP to level ${lv.level + 1}</span></div>
      <div class="stat"><span class="stat-v num" data-stat="streak">${st.current}</span><span class="stat-l">day streak</span><span class="small muted num">Longest: ${st.best} ${st.best === 1 ? 'day' : 'days'}</span></div>
      <div class="stat"><span class="stat-v num" data-stat="done">${doneWritten}</span><span class="stat-l">of ${totalWritten} full lessons done</span></div>
      <div class="stat"><span class="stat-v num">${passed}</span><span class="stat-l">of ${curriculum.phaseCount} phase tests passed</span></div>
    </div>
    <section class="activity" aria-label="Activity in the last 12 weeks"><h2>Last 12 weeks</h2><div class="heat">${cells.join('')}</div>
      <p class="small muted">Each square is a day. A day counts when you finish a lesson, a quiz or a test.</p></section>
    <section><h2>Phases</h2><ol class="prows">${rows}</ol></section>
    <section class="cert-course"><h2>Full-course certificate</h2>
      <p>${passed === curriculum.phaseCount ? 'You passed every phase test. Generate your certificate.' : `Pass all ${curriculum.phaseCount} phase tests to unlock it. You have passed ${passed}.`}</p>
      <a class="btn ${passed === curriculum.phaseCount ? 'btn-primary' : ''}" href="#/cert/course">${passed === curriculum.phaseCount ? 'Create course certificate' : 'See what’s required'}</a>
      <p class="small muted">How XP works: ${XP.lesson} per lesson marked done, ${XP.quizCorrect} per quiz question answered correctly (improvements only), ${XP.test} for passing a phase test.</p></section>
    <section class="danger-zone"><h2>Reset</h2><p class="small muted">Deletes all progress, XP and streaks in this browser. This can’t be undone.</p><button type="button" class="btn btn-danger" id="reset">Delete my progress</button></section>
  </div>`;
  app.querySelector('#reset').addEventListener('click', () => {
    if (confirm('Delete all progress, XP and streaks stored in this browser?')) { localStorage.removeItem('mefs.v2'); localStorage.removeItem('mefs.progress.v1'); route(); }
  });
}

/* ---------- Phase test ---------- */
async function viewTest(ph) {
  const phase = curriculum.phases.find((p) => p.id === ph);
  const data = await phaseData(ph);
  setTitle(`Phase ${ph} test`);
  if (!data) { app.innerHTML = `<div class="wrap page"><h1>Phase ${ph} test</h1><p>This phase has no full lessons yet, so its test isn’t available. <a href="#/progress">Back to your progress</a></p></div>`; return; }
  const W = written(), allWritten = phase.lessons.every((l) => W.has(l.id));
  const pool = [...Object.values(data.lessons).flatMap((l) => l.quiz), ...data.tests];
  const n = Math.min(12, pool.length);
  const seed = Date.now() % 2147483647; let x = seed || 1;
  const rnd = () => ((x = (x * 16807) % 2147483647) / 2147483647);
  const qs = pool.map((q) => [rnd(), q]).sort((a, b) => a[0] - b[0]).slice(0, n).map((p) => p[1]);
  window.__mefs.currentTest = qs;
  const t = load().tests[ph];
  app.innerHTML = `<div class="wrap page narrow">
    <p class="crumb small"><a href="#/progress">Your progress</a></p>
    <h1>Phase ${ph} test: ${esc(phase.title)}</h1>
    <p class="lede">${n} questions drawn from a bank of ${pool.length}. Score ${Math.round(PASS_MARK * 100)}% or more to pass and unlock the phase certificate. Each attempt draws a new set.</p>
    ${allWritten ? '' : `<p class="note-inline">Only ${phase.lessons.filter((l) => W.has(l.id)).length} of ${phase.lessons.length} lessons in this phase are written, so the test covers those. You can still pass it now.</p>`}
    ${t?.passedAt ? `<p class="pass">You passed this test on ${dateLabel(t.passedAt)} with ${Math.round(t.best * 100)}%. <a href="#/cert/${ph}">Open your certificate</a></p>` : ''}
    <div id="test-quiz"></div><div id="test-result" aria-live="polite"></div></div>`;
  renderQuiz(app.querySelector('#test-quiz'), qs, {
    submitLabel: 'Submit test',
    onGraded: (c, total) => {
      const first = recordTest(load(), ph, c, total);
      refreshXp();
      const ok = c / total >= PASS_MARK;
      app.querySelector('#test-result').innerHTML = `<div class="result ${ok ? 'ok' : 'no'}"><p class="result-score num">${Math.round((100 * c) / total)}%</p><p>${ok ? `Passed. ${first ? `+${XP.test} XP. ` : ''}Your phase certificate is ready.` : `You need ${Math.ceil(PASS_MARK * total)} of ${total} to pass. Review the explanations above, then try a new set.`}</p>
        <div class="complete-actions">${ok ? `<a class="btn btn-primary" href="#/cert/${ph}">Create certificate</a>` : `<button type="button" class="btn btn-primary" data-new>Try a new set</button>`}<a class="btn" href="#/progress">Back to progress</a></div></div>`;
      app.querySelector('[data-new]')?.addEventListener('click', () => viewTest(ph).then(() => window.scrollTo(0, 0)));
      app.querySelector('#test-result').scrollIntoView({ block: 'nearest' });
    },
  });
}

/* ---------- Certificate ---------- */
async function viewCert(scope) {
  const s = load();
  const isCourse = scope === 'course';
  const phase = isCourse ? null : curriculum.phases.find((p) => p.id === scope);
  if (!isCourse && !phase) { location.hash = '#/progress'; return; }
  const passed = curriculum.phases.filter((p) => s.tests[p.id]?.passedAt).map((p) => p.id);
  const eligible = isCourse ? passed.length === curriculum.phaseCount : passed.includes(scope);
  setTitle(isCourse ? 'Course certificate' : `Phase ${scope} certificate`);
  if (!eligible) {
    app.innerHTML = `<div class="wrap page narrow"><p class="crumb small"><a href="#/progress">Your progress</a></p><h1>${isCourse ? 'Full-course certificate' : `Phase ${scope} certificate`}</h1>
      <p class="lede">${isCourse ? `This certificate needs all ${curriculum.phaseCount} phase tests passed. You have passed ${passed.length}.` : `Pass the phase ${scope} test with ${Math.round(PASS_MARK * 100)}% or more to create this certificate.`}</p>
      ${isCourse ? '' : `<a class="btn btn-primary" href="#/test/${scope}">Take the phase ${scope} test</a>`}</div>`;
    return;
  }
  const rec = isCourse ? null : s.tests[scope];
  const date = isCourse ? passed.map((p) => s.tests[p].passedAt).sort().pop() : rec.passedAt;
  const phases = isCourse ? passed : [scope];
  app.innerHTML = `<div class="wrap page">
    <p class="crumb small"><a href="#/progress">Your progress</a></p>
    <h1>${isCourse ? 'Full-course certificate' : `Phase ${scope} certificate`}</h1>
    <p class="lede">Type your name as you want it to appear. The certificate is drawn in your browser; nothing is uploaded.</p>
    <form class="cert-form" id="cert-form" autocomplete="on">
      <label for="cert-name">Name on the certificate</label>
      <div class="cert-row"><input id="cert-name" name="name" type="text" autocomplete="name" maxlength="60" required value="${esc(s.name)}" placeholder="Ada Lovelace…" /><button type="submit" class="btn btn-primary">Create certificate</button></div>
      <p class="field-error small" id="cert-err" aria-live="polite"></p>
    </form>
    <div class="cert-out" id="cert-out" hidden>
      <canvas id="cert-canvas" class="cert-canvas" role="img" aria-label="Certificate preview"></canvas>
      <dl class="cert-details small"><div><dt>Verification code</dt><dd class="num" id="cert-code"></dd></div><div><dt>Date</dt><dd>${dateLabel(date)}</dd></div><div><dt>Scope</dt><dd>${isCourse ? 'Full course' : `Phase ${scope}`}</dd></div></dl>
      <div class="complete-actions"><a class="btn btn-primary" id="dl-png" download>Download PNG</a><a class="btn" id="dl-pdf" download>Download PDF</a></div>
    </div>
    <p class="small muted cert-honesty">This is a free certificate of completion, not an accredited qualification. It isn’t affiliated with or endorsed by ETH Zurich. The verification code is a SHA-256 hash of the name, date, scope and phases, so anyone can check the details weren’t edited on the <a href="#/verify">verify page</a>. It can’t prove who took the tests.</p>
  </div>`;
  const form = app.querySelector('#cert-form');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = form.name.value.trim().replace(/\s+/g, ' ');
    const err = app.querySelector('#cert-err');
    if (name.length < 2) { err.textContent = 'Enter at least 2 characters for your name.'; form.name.focus(); return; }
    err.textContent = '';
    const st = load(); st.name = name; save(st);
    const details = { scope: isCourse ? 'course' : `phase-${scope}`, name, date, phases };
    const code = await certCode(details);
    try { await Promise.all(["400 38px 'Source Serif 4 Variable'", "800 100px 'Archivo Variable'", "500 26px 'Archivo Variable'"].map((f) => document.fonts.load(f))); } catch { /* fall back to system fonts */ }
    const canvas = app.querySelector('#cert-canvas');
    const statement = isCourse
      ? `has completed Mechanical Engineering from Scratch, passing all ${phases.length} phase tests with a score of at least ${Math.round(PASS_MARK * 100)}%.`
      : `has completed Phase ${scope}, ${phase.title}, of Mechanical Engineering from Scratch, passing the phase test with ${Math.round(rec.best * 100)}%.`;
    drawCertificate(canvas, { name, statement, dateLabel: dateLabel(date), scopeLabel: isCourse ? 'Full course' : `Phase ${scope}`, phases, code });
    app.querySelector('#cert-code').textContent = code;
    const base = `certificate-${isCourse ? 'course' : `phase-${scope}`}-${name.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`;
    const png = app.querySelector('#dl-png'); png.href = canvas.toDataURL('image/png'); png.download = `${base}.png`;
    const pdf = app.querySelector('#dl-pdf'); URL.revokeObjectURL(pdf.href); pdf.href = URL.createObjectURL(canvasToPdf(canvas)); pdf.download = `${base}.pdf`;
    app.querySelector('#cert-out').hidden = false;
    st.certs[details.scope] = { code, name, date }; save(st);
    window.__mefs.cert = { code, details };
  });
  if (s.name) form.requestSubmit();
}

/* ---------- Verify ---------- */
function viewVerify() {
  setTitle('Verify a certificate');
  const opts = curriculum.phases.map((p) => `<option value="phase-${p.id}">Phase ${p.id}: ${esc(p.title)}</option>`).join('');
  app.innerHTML = `<div class="wrap page narrow">
    <h1>Verify a certificate</h1>
    <p class="lede">Enter the details printed on the certificate. If they produce the same code, the certificate hasn’t been edited.</p>
    <form class="verify-form" id="verify" autocomplete="off">
      <label>Name <input name="name" type="text" required spellcheck="false" /></label>
      <label>Date <input name="date" type="date" required /></label>
      <label>Scope <select name="scope"><option value="course">Full course (all 20 phases)</option>${opts}</select></label>
      <label>Verification code <input name="code" type="text" required spellcheck="false" placeholder="ABCD-1234-EF56…" autocapitalize="characters" /></label>
      <button type="submit" class="btn btn-primary">Check code</button>
    </form>
    <div id="verify-out" aria-live="polite"></div>
    <p class="small muted">This check runs in your browser. It confirms the details match the code. It can’t confirm who took the tests, because there are no accounts and no server.</p>
  </div>`;
  app.querySelector('#verify').addEventListener('submit', async (e) => {
    e.preventDefault();
    const f = e.target;
    const scope = f.scope.value;
    const phases = scope === 'course' ? curriculum.phases.map((p) => p.id) : [scope.slice(6)];
    const code = await certCode({ scope, name: f.name.value, date: f.date.value, phases });
    const ok = code === f.code.value.trim().toUpperCase();
    app.querySelector('#verify-out').innerHTML = ok ? `<p class="result ok">Match. The code ${code} belongs to these details.</p>` : `<p class="result no">No match. Check the spelling of the name, the date and the scope exactly as printed.</p>`;
  });
}
