// "Find the part": a short hunt where each question names a job and you tap the part that does it.
// Purely local, nothing is scored or saved. questions: [[text, partKind]], partKind is the part id before the dash.
export function findThePart(api, Q) {
  let k = 0, solved = 0;
  const el = document.createElement('div'); el.className = 'ta-quiz';
  el.setAttribute('data-testid', `${api.sec.id.replace('lab-', 'ta-')}-quiz`);
  const render = (msg = '', ok = null) => {
    const done = k >= Q.length;
    el.innerHTML = `<h4 class="ta-ph"><span>Find the part</span><small>${solved} / ${Q.length}</small></h4>
      ${done ? '<p class="ta-q">All found.</p><p class="ta-qhint">Each card’s lesson link shows where its numbers come from.</p>' : `<p class="ta-q">${Q[k][0]}</p><p class="ta-qhint">Tap it in the model or its label.</p>`}
      <p class="ta-qmsg" data-ok="${ok}" role="status">${msg}</p>`;
  };
  render();
  return {
    el,
    pick(p) {
      if (k >= Q.length || !p?.id) return;
      const kind = p.id.split('-')[0];
      if (kind === Q[k][1]) { solved++; k++; render(`Right: the ${p.info.name.replace(/ ·.*/, '').toLowerCase()}.`, true); }
      else render(`That’s the ${p.info.name.replace(/ ·.*/, '').toLowerCase()}. Try again.`, false);
    },
  };
}
