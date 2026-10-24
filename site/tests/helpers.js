import path from 'node:path';
import { fileURLToPath } from 'node:url';
export const SHOTS = process.env.SHOTS_DIR || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../screenshots');
export const shot = (info, name) => `${SHOTS}/v2-${name}-${info.project.name}.png`;
export function watchConsole(page) {
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));
  return errors;
}
export async function noOverflow(page) {
  const m = await page.evaluate(() => ({ iw: window.innerWidth, sw: document.documentElement.scrollWidth, bw: document.body.scrollWidth }));
  return m.sw <= m.iw + 1 && m.bw <= m.iw + 1 ? true : m;
}
export async function canvasHasContent(page, testid) {
  return page.evaluate((id) => {
    const c = document.querySelector(`canvas[data-testid="${id}"]`);
    if (!c) return { ok: false, why: 'no canvas' };
    const tmp = document.createElement('canvas'); tmp.width = 64; tmp.height = 64;
    const g = tmp.getContext('2d'); g.drawImage(c, 0, 0, 64, 64);
    const d = g.getImageData(0, 0, 64, 64).data; const set = new Set(); let lit = 0;
    for (let i = 0; i < d.length; i += 4) { set.add((d[i] >> 4) + '-' + (d[i + 1] >> 4) + '-' + (d[i + 2] >> 4)); if (d[i] + d[i + 1] + d[i + 2] > 60) lit++; }
    return { ok: set.size > 8 && lit > 20, colours: set.size, lit };
  }, testid);
}
export const isTouch = (info) => !!info.project.use.hasTouch;
// Interactive elements smaller than 44 CSS px in either direction (visible ones only).
export async function smallTargets(page, scope = 'body', min = 44) {
  return page.evaluate(([sel, min]) => {
    const out = [];
    document.querySelectorAll(`${sel} a[href], ${sel} button, ${sel} select, ${sel} input:not([type=hidden]), ${sel} summary`).forEach((el) => {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height || getComputedStyle(el).visibility === 'hidden') return;
      if (el.closest('.prose p, .prose li, .prose td, .lede, .footer-legal, .crumb, .fb, .cert-honesty, .small')) return; // inline text links
      if (el.type === 'radio' || el.type === 'checkbox') { const l = el.closest('label'); if (l && l.getBoundingClientRect().height >= min) return; }
      if (el.type === 'range') { if (r.height >= 28 && r.width >= min) return; }
      if (r.height < min - 0.5) out.push(`${el.tagName.toLowerCase()}${el.className ? '.' + String(el.className).split(' ')[0] : ''} "${(el.textContent || el.value || '').trim().slice(0, 30)}" ${Math.round(r.width)}x${Math.round(r.height)}`);
    });
    return out;
  }, [scope, min]);
}
