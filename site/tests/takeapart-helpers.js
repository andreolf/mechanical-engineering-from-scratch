// Shared helpers for the take-apart lab tests (gearbox.spec.js, engine.spec.js).
import { expect } from '@playwright/test';
export async function gotoLab(page, id) {
  await page.locator(`#ta-${id}-slot`).scrollIntoViewIfNeeded();
  const lab = page.locator(`#lab-${id}`);
  await expect(lab).toBeVisible({ timeout: 45_000 });
  await lab.scrollIntoViewIfNeeded();
  return lab;
}
// fraction of lit pixels in a screenshot of the 3D canvas (a WebGL canvas cannot be read back directly)
export async function lit(page, id) {
  const b64 = (await page.locator(`[data-testid="ta-${id}-3d"] canvas`).screenshot()).toString('base64');
  return page.evaluate(async (b64) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d'); g.drawImage(img, 0, 0);
    const d = g.getImageData(0, 0, c.width, c.height).data; let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] + d[i + 1] + d[i + 2] > 90) n++; return n / (d.length / 4);
  }, b64);
}
export const tab = async (page, info, id, name) => { if (info.project.use.isMobile) await page.getByTestId(`ta-${id}-tab-${name}`).click(); };
export const seek = (page, id, t) => page.evaluate(([id, t]) => { const s = document.querySelector(`[data-testid="ta-${id}-scrub"]`); s.value = t; s.dispatchEvent(new Event('input')); }, [id, t]);
export const setRange = (page, testid, v) => page.evaluate(([id, v]) => { const s = document.querySelector(`[data-testid="${id}"]`); s.value = v; s.dispatchEvent(new Event('input', { bubbles: true })); }, [testid, v]);
// labels that are shown must not overlap each other, and none may sit under an open part card
export async function labelsClear(page, id) {
  return page.evaluate((id) => {
    const view = document.querySelector(`[data-testid="ta-${id}-3d"]`); const v = view.getBoundingClientRect();
    const ls = [...view.querySelectorAll('.ta-label[data-on="1"]')].map((e) => e.getBoundingClientRect()).filter((r) => r.width);
    const card = view.querySelector('.ta-card:not([hidden])')?.getBoundingClientRect();
    const hit = (a, b) => a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1;
    const bad = [];
    ls.forEach((a, i) => { ls.slice(i + 1).forEach((b) => { if (hit(a, b)) bad.push('overlap'); }); if (card && Number(getComputedStyle(view.querySelector('.ta-labels')).opacity) > 0.05 && hit(a, card)) bad.push(`under card (labels opacity ${getComputedStyle(view.querySelector('.ta-labels')).opacity})`); if (a.left < v.left - 1 || a.right > v.right + 1) bad.push('clipped'); });
    return { n: ls.length, bad };
  }, id);
}
