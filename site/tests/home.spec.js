import { test, expect } from '@playwright/test';
import { watchConsole, noOverflow, canvasHasContent, shot, isTouch, smallTargets } from './helpers.js';

test.describe('Home page', () => {
  test('hero: clean layout, title below the nav, no overlap, no overflow, no console errors @device', async ({ page }, info) => {
    const errors = watchConsole(page);
    await page.goto('./');
    const h1 = page.locator('h1.hero-title');
    await expect(h1).toHaveText('Mechanical Engineering from Scratch');
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    const nav = await page.locator('#site-nav').boundingBox();
    const t = await h1.boundingBox();
    expect(t.y).toBeGreaterThanOrEqual(nav.y + nav.height - 1);       // not clipped under the sticky nav
    expect(t.x).toBeGreaterThanOrEqual(0);
    expect(t.x + t.width).toBeLessThanOrEqual(page.viewportSize().width + 1);
    const sheet = await page.locator('figure.sheet').boundingBox();
    const overlap = !(t.x + t.width <= sheet.x || sheet.x + sheet.width <= t.x || t.y + t.height <= sheet.y || sheet.y + sheet.height <= t.y);
    expect(overlap, 'headline overlaps the 3D sheet').toBe(false);
    // the primary call to action is visible in the first screen on phones too
    const cta = await page.getByRole('link', { name: 'Start lesson 00.01' }).boundingBox();
    expect(cta.y + cta.height).toBeLessThanOrEqual(page.viewportSize().height + 1);
    const webgl = await page.evaluate(() => !document.querySelector('#hero .webgl-fallback'));
    if (webgl) {
      await page.locator('figure.sheet').scrollIntoViewIfNeeded();
      await page.waitForFunction(() => window.__mefs?.hero?.stage?.frames > 10);
      const r = await canvasHasContent(page, 'hero-canvas');
      expect(r.ok, JSON.stringify(r)).toBeTruthy();
    }
    expect(await noOverflow(page)).toBe(true);
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.waitForTimeout(400);
    await page.screenshot({ path: shot(info, 'hero') });
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('hero beam reacts to dragging, sliders and material', async ({ page }, info) => {
    await page.goto('./');
    await page.waitForFunction(() => window.__mefs?.hero?.stage?.frames > 5);
    const before = await page.evaluate(() => ({ ...window.__mefs.hero.state }));
    if (isTouch(info)) {
      await page.locator('#hero-load').fill('6000');
      await page.locator('#hero-load').dispatchEvent('input');
    } else {
      const box = await page.locator('canvas[data-testid=hero-canvas]').boundingBox();
      await page.mouse.move(box.x + box.width * 0.55, box.y + box.height * 0.5);
      await page.mouse.down();
      await page.mouse.move(box.x + box.width * 0.3, box.y + box.height * 0.5, { steps: 8 });
      await page.mouse.up();
    }
    const after = await page.evaluate(() => ({ ...window.__mefs.hero.state }));
    expect(after.demo).toBe(false);
    expect(after.interactions).toBeGreaterThan(before.interactions);
    const tipSteel = after.tip;
    await page.selectOption('#hero-material', 'bamboo');
    const tipBamboo = await page.evaluate(() => window.__mefs.hero.state.tip);
    expect(tipBamboo / tipSteel).toBeGreaterThan(10);
    await expect(page.locator('[data-k=mat]')).toContainText('Bamboo');
  });

  test('3D canvas lets the page scroll until rotate mode is switched on @device', async ({ page }) => {
    await page.goto('./');
    test.skip(await page.locator('#hero .webgl-fallback').count() > 0, 'no WebGL in this browser');
    await page.locator('figure.sheet').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.hero?.stage?.frames > 2);
    const canvas = page.locator('canvas[data-testid=hero-canvas]');
    await expect(canvas).toHaveCSS('touch-action', 'pan-y');
    const btn = page.locator('#hero .orbit-toggle');
    await expect(btn).toHaveAttribute('aria-pressed', 'false');
    const bb = await btn.boundingBox();
    expect(bb.height).toBeGreaterThanOrEqual(44);
    await btn.click();
    await expect(btn).toHaveAttribute('aria-pressed', 'true');
    await expect(canvas).toHaveCSS('touch-action', 'none');
    await btn.click();
    await expect(canvas).toHaveCSS('touch-action', 'pan-y');
  });

  test('truss lab: deleting members redistributes load, then collapses', async ({ page }, info) => {
    const errors = watchConsole(page);
    await page.goto('./');
    await page.locator('#lab-truss').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.truss?.stage?.frames > 10);
    expect((await canvasHasContent(page, 'truss-canvas')).ok).toBeTruthy();
    await page.locator('#lab-truss .lab-canvas').scrollIntoViewIfNeeded();
    const util0 = await page.evaluate(() => window.__mefs.truss.state.maxUtil);
    const alive = () => page.evaluate(() => window.__mefs.truss.members().filter((m) => m.alive).length);
    const n0 = await alive();
    const s = await page.evaluate(() => window.__mefs.truss.memberScreen(17));
    if (isTouch(info)) await page.touchscreen.tap(s.x, s.y); else await page.mouse.click(s.x, s.y);
    await expect.poll(alive).toBeLessThan(n0);
    const st1 = await page.evaluate(() => ({ ...window.__mefs.truss.state }));
    expect(st1.mechanism).toBe(false);
    expect(st1.maxUtil).not.toBeCloseTo(util0, 5);
    await expect(page.locator('#lab-truss .lab-banner')).toContainText(/Still standing|overloaded/);
    await page.locator('[name=truss-pos]').fill('0.2');
    await page.locator('[name=truss-pos]').dispatchEvent('input');
    expect(await page.evaluate(() => window.__mefs.truss.state.maxUtil)).not.toBeCloseTo(st1.maxUtil, 5);
    await page.evaluate(() => window.__mefs.truss.removeMember(15));
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Mechanism');
    await page.waitForTimeout(1000);
    await page.locator('#lab-truss').screenshot({ path: shot(info, 'lab-truss') });
    await page.locator('[data-action=truss-reset]').click();
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Tap or click');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('flywheel lab: spin precesses, stopping the spin makes it fall', async ({ page }) => {
    await page.goto('./');
    await page.locator('#lab-flywheel').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.gyro?.state?.steps > 1000);
    await page.waitForTimeout(2500);
    const fast = await page.evaluate(() => ({ ...window.__mefs.gyro.state, s: null }));
    expect(Math.abs(fast.tilt)).toBeLessThan(15);
    expect(Math.abs(fast.phiRate)).toBeGreaterThan(0.2);
    // Wait on simulated time, not wall-clock time: under load the browser renders fewer frames, so the fall takes longer in real seconds.
    // A frame-by-frame watcher records the lowest tilt, so a fast swing cannot slip between two polls.
    await page.locator('[data-action=gyro-stop]').click();
    await page.evaluate(() => {
      const st = window.__mefs.gyro.state;
      window.__gyroWatch = { t0: st.t, minTilt: st.tilt };
      const tick = () => { const w = window.__gyroWatch; w.minTilt = Math.min(w.minTilt, st.tilt); if (st.t - w.t0 < 3) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    });
    await page.waitForFunction(() => window.__mefs.gyro.state.t - window.__gyroWatch.t0 >= 3 || window.__gyroWatch.minTilt < -45, null, { timeout: 60000 });
    expect(await page.evaluate(() => window.__gyroWatch.minTilt)).toBeLessThan(-45);
    await expect(page.locator('#lab-flywheel .lab-banner')).toContainText('falls');
  });

  test('pipe lab: throat squeeze raises speed, extreme flow cavitates', async ({ page }) => {
    await page.goto('./');
    await page.locator('#lab-pipe').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.pipe?.state?.res);
    const u0 = await page.evaluate(() => window.__mefs.pipe.state.res.Ut);
    await page.locator('[name=pipe-d]').fill('35');
    await page.locator('[name=pipe-d]').dispatchEvent('input');
    expect(await page.evaluate(() => window.__mefs.pipe.state.res.Ut)).toBeGreaterThan(u0 * 2);
    await page.locator('[name=pipe-q]').fill('40');
    await page.locator('[name=pipe-q]').dispatchEvent('input');
    await expect(page.locator('#lab-pipe .lab-banner')).toContainText('Cavitation');
  });

  test('phase map: expands, searches and links to lessons', async ({ page }, info) => {
    await page.goto('./#curriculum');
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    await expect(page.locator('.phase')).toHaveCount(20);
    const head = page.locator('#phase-00 .phase-head');
    await head.click();
    await expect(head).toHaveAttribute('aria-expanded', 'true');
    await expect(page.locator('#phase-00 .lesson-item').first()).toBeVisible();
    await expect(page.locator('#phase-00')).toContainText('Full lesson');
    await page.locator('#lesson-search').fill('bernoulli');
    await expect(page.locator('#search-count')).toContainText('match');
    await page.locator('#lesson-search').fill('');
    await expect(page.locator('.phase:not([hidden])')).toHaveCount(20);
    if ((await head.getAttribute('aria-expanded')) !== 'true') await head.click();
    await page.locator('#phase-00 a[href$="#/00.03"]').first().click();
    await expect(page).toHaveURL(/learn\.html#\/00\.03/);
    await expect(page.locator('h1')).toContainText('Buckingham Pi');
  });

  test('works without WebGL', async ({ page }) => {
    const errors = watchConsole(page);
    await page.goto('./?nowebgl');
    await expect(page.locator('.webgl-fallback').first()).toBeVisible();
    await page.locator('#lab-truss').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => window.__mefs?.truss?.removeMember);
    await page.locator('#lab-pipe').scrollIntoViewIfNeeded();
    await page.locator('[name=pipe-d]').fill('30');
    await page.locator('[name=pipe-d]').dispatchEvent('input');
    await page.evaluate(() => window.__mefs.truss.removeMember(15));
    await expect(page.locator('#lab-truss .lab-banner')).toContainText('Mechanism');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('footer and touch targets @device', async ({ page }, info) => {
    await page.goto('./');
    await page.waitForFunction(() => window.__mefs?.curriculumReady);
    const footer = page.locator('#site-footer');
    await footer.scrollIntoViewIfNeeded();
    await expect(footer).toContainText('not affiliated with or endorsed by ETH Zurich');
    await expect(footer.getByRole('link', { name: /GitHub/ }).first()).toHaveAttribute('href', /github\.com\/andreolf/);
    await expect(footer.locator('.foot-h')).toHaveText(['This course', 'More from Scratch', 'About']);
    const sib = footer.getByTestId('sibling-courses');
    for (const [name, url] of [['Security from Scratch', 'https://andreolf.github.io/security-from-scratch/'], ['AI Safety from Scratch', 'https://andreolf.github.io/ai-safety-from-scratch/'], ['Mechatronics from Scratch', 'https://andreolf.github.io/mechatronics-from-scratch/']])
      await expect(sib.getByRole('link', { name })).toHaveAttribute('href', url);
    await expect(sib.getByRole('link', { name: /Mechanical Engineering from Scratch/ })).toHaveCount(0);
    const links = await footer.locator('.foot-list a').evaluateAll((as) => as.map((a) => ({ h: a.getBoundingClientRect().height, d: getComputedStyle(a).textDecorationLine, t: getComputedStyle(a.querySelector('.foot-link-t') || a).textDecorationLine })));
    expect(links.length).toBe(9);
    for (const l of links) { expect(l.h).toBeGreaterThanOrEqual(44); expect(l.d).toBe('none'); expect(l.t).toBe('none'); }
    await expect(footer).toContainText("Certificates are free certificates of completion, not accredited qualifications. This project is not affiliated with or endorsed by ETH Zurich; ETH course names are given for orientation only.");
    await expect(page.locator('main')).not.toContainText(/Sister course|Sibling courses/);
    if (isTouch(info)) {
      const small = await smallTargets(page, '#site-footer');
      expect(small, small.join('\n')).toEqual([]);
      const navSmall = await smallTargets(page, '#site-nav');
      expect(navSmall, navSmall.join('\n')).toEqual([]);
    }
    expect(await noOverflow(page)).toBe(true);
    await footer.screenshot({ path: shot(info, 'footer') });
  });
});
