// Learner state, saved only in this browser (localStorage). No accounts, no network.
const KEY = 'mefs.v2';
const OLD = 'mefs.progress.v1';
export const XP = { lesson: 50, quizCorrect: 10, test: 200 };
export const PASS_MARK = 0.8;

const today = (d = new Date()) => {
  const z = new Date(d.getTime() - d.getTimezoneOffset() * 60000);
  return z.toISOString().slice(0, 10);
};

function blank() { return { v: 2, lessons: {}, tests: {}, xp: 0, days: [], name: '', certs: {} }; }

export function load() {
  let s;
  try { s = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch { s = null; }
  if (!s || s.v !== 2) {
    s = blank();
    try { // migrate v1 checkbox progress
      const old = JSON.parse(localStorage.getItem(OLD) || '[]');
      for (const id of old) s.lessons[id] = { done: true, at: today() };
    } catch { /* ignore */ }
  }
  return s;
}
export function save(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch { /* storage blocked: progress lives for this tab only */ } }

function touchDay(s) { const d = today(); if (!s.days.includes(d)) s.days.push(d); }

export function setLessonDone(s, id, done = true) {
  const rec = (s.lessons[id] ||= {});
  if (done && !rec.done) { rec.done = true; rec.at = today(); s.xp += XP.lesson; touchDay(s); }
  if (!done && rec.done) { rec.done = false; s.xp = Math.max(0, s.xp - XP.lesson); }
  save(s);
}
export function recordQuiz(s, id, correct, total) {
  const rec = (s.lessons[id] ||= {});
  const prevBest = rec.quizBest || 0;
  rec.quizBest = Math.max(prevBest, correct);
  rec.quizTotal = total;
  rec.quizAttempts = (rec.quizAttempts || 0) + 1;
  s.xp += XP.quizCorrect * Math.max(0, correct - prevBest); // XP only for improvement, so retries can't farm points
  touchDay(s);
  save(s);
}
export function recordTest(s, phase, score, total) {
  const rec = (s.tests[phase] ||= { best: 0, attempts: 0 });
  rec.attempts++;
  const frac = score / total;
  const firstPass = frac >= PASS_MARK && !rec.passedAt;
  rec.best = Math.max(rec.best, frac);
  if (firstPass) { rec.passedAt = today(); s.xp += XP.test; }
  touchDay(s);
  save(s);
  return firstPass;
}
export function streak(s) {
  const set = new Set(s.days);
  let cur = 0;
  const d = new Date();
  if (!set.has(today(d))) d.setDate(d.getDate() - 1); // a streak survives until the end of today
  while (set.has(today(d))) { cur++; d.setDate(d.getDate() - 1); }
  let best = 0, run = 0, prev = null;
  for (const day of [...set].sort()) {
    const t = new Date(day + 'T12:00:00');
    run = prev && (t - prev) / 86400000 < 1.5 ? run + 1 : 1;
    best = Math.max(best, run); prev = t;
  }
  return { current: cur, best };
}
export function level(xp) {
  // level n needs 250 * n * (n + 1) / 2 XP: 250, 750, 1500, ...
  let n = 0;
  while (250 * (n + 1) * (n + 2) / 2 <= xp) n++;
  const lo = 250 * n * (n + 1) / 2, hi = 250 * (n + 1) * (n + 2) / 2;
  return { level: n + 1, into: xp - lo, span: hi - lo };
}
export function doneCount(s, ids) { return ids.filter((id) => s.lessons[id]?.done).length; }
export function resetAll() { try { localStorage.removeItem(KEY); localStorage.removeItem(OLD); } catch { /* ignore */ } }
export { today };
