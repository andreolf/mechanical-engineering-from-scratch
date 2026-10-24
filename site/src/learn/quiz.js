// Quiz rendering and grading: multiple choice and numeric answers with a relative tolerance.
export function parseNumber(raw) {
  if (raw == null) return NaN;
  let t = String(raw).trim().replace(/\s+/g, '').replace(/[−–]/g, '-');
  t = t.replace(/[x×·*]10\^?\(?(-?\d+)\)?/i, 'e$1');      // 2.2×10^-16 -> 2.2e-16
  if (/^-?\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)) t = t.replace(/,/g, ''); // 1,234.5
  else if (/^-?\d+,\d+$/.test(t)) t = t.replace(',', '.');             // 3,14 -> 3.14
  if (!/^[-+]?(\d+\.?\d*|\.\d+)(e[-+]?\d+)?$/i.test(t)) return NaN;
  return parseFloat(t);
}
export function gradeNumeric(value, answer, tol) {
  if (!isFinite(value)) return false;
  return answer === 0 ? Math.abs(value) <= tol : Math.abs(value - answer) <= tol * Math.abs(answer);
}

let uid = 0;
/** Renders questions into host. onGraded(correct, total) is called after each check. */
export function renderQuiz(host, questions, { onGraded, submitLabel = 'Check answers', title } = {}) {
  const id = `q${++uid}`;
  host.innerHTML = `${title ? `<h2 id="${id}-h">${title}</h2>` : ''}
  <form class="quiz" novalidate ${title ? `aria-labelledby="${id}-h"` : 'aria-label="Test questions"'}>
    ${questions.map((q, i) => `<fieldset class="qq" data-i="${i}">
      <legend><span class="qn num">${i + 1}</span><span class="qt">${q.q}</span></legend>
      ${q.type === 'mc' ? `<div class="opts">${q.options.map((o, j) => `<label class="opt"><input type="radio" name="${id}-${i}" value="${j}" /><span>${o}</span></label>`).join('')}</div>`
        : `<div class="numrow"><label class="sr-only" for="${id}-${i}">Your answer</label><input id="${id}-${i}" type="text" inputmode="decimal" autocomplete="off" spellcheck="false" placeholder="Your answer…" />${q.unit ? `<span class="unit">${q.unit}</span>` : ''}</div>
          <p class="hint small muted">Accepted within ±${+(q.tol * 100).toFixed(2)}%. You can type 2.2e-16 for scientific notation.</p>`}
      <div class="fb" aria-live="polite"></div>
    </fieldset>`).join('')}
    <div class="quiz-bar"><button type="submit" class="btn btn-primary">${submitLabel}</button><button type="button" class="btn" data-retry hidden>Try again</button><p class="score num" aria-live="polite"></p></div>
  </form>`;
  const form = host.querySelector('form');
  const result = { correct: 0, total: questions.length, graded: false };
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let correct = 0;
    questions.forEach((q, i) => {
      const fs = form.querySelector(`fieldset[data-i="${i}"]`);
      const fb = fs.querySelector('.fb');
      let ok = false, given = '';
      if (q.type === 'mc') {
        const sel = fs.querySelector('input:checked');
        ok = !!sel && +sel.value === q.answer;
        given = sel ? '' : 'No option chosen. ';
        fs.querySelectorAll('.opt').forEach((lab, j) => { lab.classList.toggle('is-right', j === q.answer); lab.classList.toggle('is-wrong', !!sel && +sel.value === j && j !== q.answer); });
      } else {
        const inp = fs.querySelector('input');
        const v = parseNumber(inp.value);
        ok = gradeNumeric(v, q.answer, q.tol);
        if (!isFinite(v)) given = inp.value.trim() ? 'That isn’t a number this quiz can read. ' : 'No answer entered. ';
        inp.setAttribute('aria-invalid', String(!ok));
      }
      if (ok) correct++;
      fs.classList.toggle('is-correct', ok); fs.classList.toggle('is-incorrect', !ok);
      const ans = q.type === 'num' ? ` The answer is ${fmtAns(q.answer)}${q.unit ? ' ' + q.unit : ''}.` : '';
      fb.innerHTML = `<p class="fb-${ok ? 'ok' : 'no'}"><strong>${ok ? 'Correct.' : 'Not quite.'}</strong> ${ok ? '' : given}${ok ? '' : ans}</p>${q.explain ? `<p class="fb-explain">${q.explain}</p>` : ''}`;
    });
    Object.assign(result, { correct, graded: true });
    form.querySelector('.score').textContent = `${correct} of ${questions.length} correct`;
    form.querySelector('[data-retry]').hidden = false;
    onGraded?.(correct, questions.length);
  });
  form.querySelector('[data-retry]').addEventListener('click', () => {
    form.reset();
    form.querySelectorAll('.fb').forEach((f) => (f.innerHTML = ''));
    form.querySelectorAll('fieldset').forEach((f) => f.classList.remove('is-correct', 'is-incorrect'));
    form.querySelectorAll('.opt').forEach((l) => l.classList.remove('is-right', 'is-wrong'));
    form.querySelector('.score').textContent = '';
    form.querySelector('[data-retry]').hidden = true;
    form.querySelector('fieldset input')?.focus();
  });
  return result;
}
const nf = new Intl.NumberFormat('en-US', { maximumSignificantDigits: 6 });
function fmtAns(x) { return Math.abs(x) !== 0 && (Math.abs(x) < 1e-3 || Math.abs(x) >= 1e7) ? x.toExponential(3) : nf.format(x); }
