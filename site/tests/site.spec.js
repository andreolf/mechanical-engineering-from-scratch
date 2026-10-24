import { test, expect } from '@playwright/test';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const SHOTS = process.env.SHOTS_DIR || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../screenshots');

function watchConsole(page) {
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push(String(e)));
  return errors;
}
// Non-blank canvas check: sample pixels and require colour variety.
async function canvasHasContent(page, testid) {
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
async function tapOrClick(page, x, y, isMobile) {
  if (isMobile) await page.touchscreen.tap(x, y); else await page.mouse.click(x, y);
}

test.describe('Mechanical Engineering from Scratch', () => {
  test('loads with no console errors and renders the hero 3D scene', async ({ page }, info) => {
    const errors = watchConsole(page);
    await page.goto('./');
    await expect(page.locator('h1')).toContainText('Mechanical Engineering');
    await page.waitForFunction(() => window.__mefs?.hero?.stage?.frames > 10);
    const r = await canvasHasContent(page, 'hero-canvas');
    expect(r.ok, JSON.stringify(r)).toBeTruthy();
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    await expect(page.locator('[data-count=lessons]').first()).not.toHaveText('');
    await page.waitForTimeout(500);
    await page.screenshot({ path: `${SHOTS}/hero-${info.project.name}.png` });
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('hero beam reacts to dragging and the load slider', async ({ page }, info) => {
    await page.goto('./');
    await page.waitForFunction(() => window.__mefs?.hero?.stage?.frames > 5);
    const box = await page.locator('canvas[data-testid=hero-canvas]').boundingBox();
    // project two beam points to the screen and drag between them
    const before = await page.evaluate(() => ({ ...window.__mefs.hero.state }));
    if (info.project.name === 'mobile') {
      // touch: tap near the left part of the beam area to move the load there
      await page.locator('#hero-load').fill('6000');
      await page.locator('#hero-load').dispatchEvent('input');
    } else {
      await page.mouse.move(box.x + box.width * 0.55, box.y + box.height * 0.5);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width * 0.25, box.y + box.height * 0.5, { steps: 8 });
      await page.mouse.up();
    }
    const after = await page.evaluate(() => ({ ...window.__mefs.hero.state }));
    expect(after.demo).toBe(false);
    expect(after.interactions).toBeGreaterThan(before.interactions);
    if (info.project.name !== 'mobile') expect(Math.abs(after.a - before.a)).toBeGreaterThan(0.05);
    // material switch changes deflection (steel -> bamboo is ~14x softer)
    const tipSteel = after.tip;
    await page.selectOption('#hero-material', 'bamboo');
    const tipBamboo = await page.evaluate(() => window.__mefs.hero.state.tip);
    expect(tipBamboo / tipSteel).toBeGreaterThan(10);
    await expect(page.locator('#hero-readout')).toContainText('Bamboo');
  });

  test('truss lab: deleting members redistributes load, then collapses', async ({ page }, info) => {
    const errors = watchConsole(page);
    await page.goto('./');
    await page.locator('#lab-truss').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.truss?.stage?.frames > 10);
    expect((await canvasHasContent(page, 'truss-canvas')).ok).toBeTruthy();
    const util0 = await page.evaluate(() => window.__mefs.truss.state.maxUtil);
    // pause the camera sway effect by reading position right before the tap
    const tapMember = async (i) => {
      const s = await page.evaluate((k) => window.__mefs.truss.memberScreen(k), i);
      await tapOrClick(page, s.x, s.y, info.project.name === 'mobile');
    };
    // member 17 is an inner diagonal (redundant): bridge should survive
    const membersBefore = await page.evaluate(() => window.__mefs.truss.members().filter((m) => m.alive).length);
    await tapMember(17);
    await expect.poll(() => page.evaluate(() => window.__mefs.truss.members().filter((m) => m.alive).length)).toBeLessThan(membersBefore);
    const st1 = await page.evaluate(() => ({ ...window.__mefs.truss.state }));
    expect(st1.mechanism).toBe(false);
    expect(st1.maxUtil).not.toBeCloseTo(util0, 5);
    await expect(page.locator('#lab-truss .lab-banner')).toContainText(/Still standing|overloaded/);
    await page.waitForTimeout(300);
    await page.locator('#lab-truss').screenshot({ path: `${SHOTS}/lab-truss-standing-${info.project.name}.png` });
    // slider moves the truck and changes forces
    await page.locator('[name=truss-pos]').fill('0.2');
    await page.locator('[name=truss-pos]').dispatchEvent('input');
    const st2 = await page.evaluate(() => window.__mefs.truss.state.maxUtil);
    expect(st2).not.toBeCloseTo(st1.maxUtil, 5);
    // the end diagonal is not redundant: removing it leaves a mechanism
    await page.evaluate(() => window.__mefs.truss.removeMember(15));
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Mechanism');
    await page.waitForTimeout(1200);
    await page.locator('#lab-truss').screenshot({ path: `${SHOTS}/lab-truss-collapse-${info.project.name}.png` });
    await page.locator('[data-action=truss-reset]').click();
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Tap or click');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('gyroscope lab: spin precesses, stopping the spin makes it fall', async ({ page }, info) => {
    await page.goto('./');
    await page.locator('#lab-flywheel').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.gyro?.state?.steps > 1000);
    if (await page.locator('canvas[data-testid=gyro-canvas]').count()) expect((await canvasHasContent(page, 'gyro-canvas')).ok).toBeTruthy();
    await page.waitForTimeout(2500);
    const fast = await page.evaluate(() => ({ ...window.__mefs.gyro.state, s: null }));
    expect(Math.abs(fast.tilt)).toBeLessThan(15); // stays near horizontal
    expect(Math.abs(fast.phiRate)).toBeGreaterThan(0.2); // precessing
    await page.locator('#lab-flywheel').screenshot({ path: `${SHOTS}/lab-gyro-${info.project.name}.png` });
    await page.locator('[data-action=gyro-stop]').click();
    await expect.poll(() => page.evaluate(() => window.__mefs.gyro.state.tilt), { timeout: 8000 }).toBeLessThan(-45);
    await expect(page.locator('#lab-flywheel .lab-banner')).toContainText('falls');
  });

  test('pipe lab: throat squeeze raises speed, extreme flow cavitates', async ({ page }, info) => {
    await page.goto('./');
    await page.locator('#lab-pipe').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.pipe?.state?.res);
    if (await page.locator('canvas[data-testid=pipe-canvas]').count()) {
      await page.waitForTimeout(500);
      expect((await canvasHasContent(page, 'pipe-canvas')).ok).toBeTruthy();
    }
    const u0 = await page.evaluate(() => window.__mefs.pipe.state.res.Ut);
    await page.locator('[name=pipe-d]').fill('35');
    await page.locator('[name=pipe-d]').dispatchEvent('input');
    const u1 = await page.evaluate(() => window.__mefs.pipe.state.res.Ut);
    expect(u1).toBeGreaterThan(u0 * 2);
    await page.locator('[name=pipe-q]').fill('40');
    await page.locator('[name=pipe-q]').dispatchEvent('input');
    await expect(page.locator('#lab-pipe .lab-banner')).toContainText('Cavitation');
    await page.waitForTimeout(600);
    await page.locator('#lab-pipe').screenshot({ path: `${SHOTS}/lab-pipe-${info.project.name}.png` });
  });

  test('phase map expands, search filters, progress persists across reloads', async ({ page }, info) => {
    await page.goto('./#curriculum');
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    const phases = page.locator('.phase');
    await expect(phases).toHaveCount(20);
    const head = page.locator('#phase-06 .phase-head');
    await head.click();
    await expect(head).toHaveAttribute('aria-expanded', 'true');
    await expect(page.locator('#phase-06 .lesson').first()).toBeVisible();
    await page.locator('#phase-06 .lesson-toggle').first().click();
    await expect(page.locator('#phase-06 .lesson-detail').first()).toBeVisible();
    await expect(page.locator('#phase-06 .lesson-detail').first()).toContainText('Pro tool');
    // progress
    await page.locator('#phase-06 input[data-lesson="06.01"]').check();
    await page.locator('#phase-06 input[data-lesson="06.02"]').check();
    await expect(page.locator('[data-k=done]')).toHaveText('2');
    await page.locator('#phase-06').screenshot({ path: `${SHOTS}/phase-map-open-${info.project.name}.png` });
    await page.reload();
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    await expect(page.locator('[data-k=done]')).toHaveText('2');
    await expect(page.locator('input[data-lesson="06.02"]')).toBeChecked();
    // search
    await page.locator('#lesson-search').fill('bernoulli');
    await expect(page.locator('#search-count')).toContainText('match');
    const visible = await page.locator('.lesson:not([hidden])').count();
    expect(visible).toBeGreaterThan(0);
    expect(visible).toBeLessThan(20);
    await expect(page.locator('.phase:not([hidden])').first()).toHaveClass(/open/);
    await page.locator('#lesson-search').fill('zzzz-no-match');
    await expect(page.locator('#search-count')).toContainText('0 lessons');
    await page.locator('#lesson-search').fill('');
    await expect(page.locator('.phase:not([hidden])')).toHaveCount(20);
    await page.locator('#curriculum').screenshot({ path: `${SHOTS}/phase-map-${info.project.name}.png` });
    await page.locator('#progress-reset').click();
    await expect(page.locator('[data-k=done]')).toHaveText('0');
  });

  test('graceful fallback without WebGL', async ({ page }) => {
    const errors = watchConsole(page);
    await page.goto('./?nowebgl');
    await expect(page.locator('.webgl-fallback')).toHaveCount(4);
    // physics still answers controls
    await page.locator('[name=pipe-d]').fill('30');
    await page.locator('[name=pipe-d]').dispatchEvent('input');
    await expect(page.locator('#lab-pipe [data-k=ut]')).not.toHaveText('');
    await page.evaluate(() => window.__mefs.truss.removeMember(15));
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Mechanism');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('no horizontal overflow at the device width', async ({ page }) => {
    await page.goto('./');
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    const vw = page.viewportSize().width;
    const m = await page.evaluate(() => ({ iw: window.innerWidth, sw: document.documentElement.scrollWidth }));
    expect(m.iw).toBe(vw);
    expect(m.sw).toBeLessThanOrEqual(vw + 1);
  });
});
