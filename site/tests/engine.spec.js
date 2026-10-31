// Take-apart lab 02: the single-cylinder four-stroke engine, inline in the labs section of the home page.
// desktop and mobile run everything; the @device tests also run on the other Chromium device projects.
import { test, expect } from '@playwright/test';
import { watchConsole, noOverflow } from './helpers.js';
import { gotoLab, lit, tab, seek, setRange, labelsClear } from './takeapart-helpers.js';

let errors;
test.beforeEach(async ({ page }) => { errors = watchConsole(page); await page.goto('./'); });
test.afterEach(async ({ page }) => { expect(errors, errors.join('\n')).toEqual([]); expect(await noOverflow(page)).toBe(true); });
const ID = 'engine';
const STROKE = /^(INTAKE|COMPRESSION|POWER|EXHAUST)$/;

test('engine plays inline on the labs section: renders, explodes, isolates and reassembles @device', async ({ page }, info) => {
  const lab = await gotoLab(page, ID);
  expect(await page.locator('#labs #lab-engine').count()).toBe(1);
  await expect(page.getByTestId('ta-engine-3d')).toHaveAttribute('data-webgl', 'on');
  await expect.poll(() => lit(page, ID), { timeout: 45_000 }).toBeGreaterThan(0.02);
  expect(Number(await lab.locator('[data-parts]').textContent())).toBeGreaterThan(16);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-engine-explode').click();
  await expect(lab).toHaveAttribute('data-exploded', 'true');
  await expect(page.getByTestId('ta-engine-status')).toHaveText('TEARDOWN');
  await expect.poll(() => lab.locator('.ta-label[data-on="1"]').count()).toBeGreaterThan(2);
  await expect.poll(async () => (await labelsClear(page, ID)).bad, { timeout: 5_000 }).toEqual([]);
  await tab(page, info, ID, 'subs');
  await expect(page.getByTestId('ta-engine-badge-valves')).toHaveText(/detached/i);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-engine-explode').click();
  await expect(lab).toHaveAttribute('data-exploded', 'false');
  for (const a of ['block', 'piston', 'crank', 'valves', 'ignition']) {
    await page.getByTestId(`ta-engine-asm-${a}`).click();
    await expect(lab).toHaveAttribute('data-assembly', a);
  }
  await page.getByTestId('ta-engine-asm-all').click();
  await expect(lab).toHaveAttribute('data-assembly', 'all');
});

test('engine: a tapped part opens its card, and the card links to the exact lesson @device', async ({ page, isMobile }, info) => {
  await gotoLab(page, ID);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-engine-play').click();
  await page.getByTestId('ta-engine-turntable').click();
  await page.getByTestId('ta-engine-3d').scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  const pt = await page.evaluate(() => window.__mefs.engine.screenOf('fly-0'));
  if (isMobile) await page.touchscreen.tap(pt.x, pt.y); else await page.mouse.click(pt.x, pt.y);
  const card = page.getByTestId('ta-engine-card');
  await expect(card).toBeVisible();
  await expect(card.locator('h5')).not.toBeEmpty();
  await expect(card.locator('a[href^="learn.html#/"]').first()).toBeVisible();
  await page.getByTestId('ta-engine-card-close').click();
  await expect(card).toBeHidden();
  await page.evaluate(() => window.__mefs.engine.openCard('rod-0'));
  await expect(card).toContainText('200 mm');
  await expect.poll(async () => (await labelsClear(page, ID)).bad, { timeout: 5_000 }).toEqual([]);
  await card.locator('a[href="learn.html#/06.19"]').click();
  await expect(page).toHaveURL(/learn\.html#\/06\.19$/);
  await expect(page.locator('h1')).toContainText('Buckling');
});

test('engine: the piston follows the 05.04 slider-crank and the valves open on their strokes', async ({ page }, info) => {
  const lab = await gotoLab(page, ID);
  // the lesson's own numbers: r = 50 mm, l = 200 mm, crank at 60° turning at 100 rad/s
  const ex = await page.evaluate(() => { const a = window.__mefs.engine; return { x: a.xMm(Math.PI / 3), v: a.vMs(Math.PI / 3, 100) }; });
  expect(ex.x).toBeCloseTo(220.26, 2);
  expect(ex.v).toBeCloseTo(-4.885, 3);
  for (const [deg, stroke, li, le] of [[90, 'intake', 1, 0], [270, 'compression', 0, 0], [450, 'power', 0, 0], [630, 'exhaust', 0, 1]]) {
    await page.evaluate((d) => window.__mefs.engine.setCrank(d), deg);
    await expect(lab).toHaveAttribute('data-stroke', stroke);
    await expect.poll(async () => Number(await lab.getAttribute('data-lift-in'))).toBeCloseTo(li, 3);
    expect(Number(await lab.getAttribute('data-lift-ex'))).toBeCloseTo(le, 3);
  }
  await page.evaluate(() => window.__mefs.engine.setCrank(60));
  await expect.poll(async () => Number(await lab.getAttribute('data-pin-mm'))).toBeCloseTo(220.26, 2);
  await tab(page, info, ID, 'tele');
  await expect(page.getByTestId('ta-engine-telemetry')).toContainText('220.3');
  await expect(page.getByTestId('ta-engine-telemetry')).toContainText('60° / 720');
  // running: position and speed are the slider-crank of the angle on screen, at the set speed
  await tab(page, info, ID, 'parts');
  await setRange(page, 'ta-engine-rpm', 1000);
  await expect.poll(async () => Number(await lab.getAttribute('data-rpm')), { timeout: 20_000 }).toBeCloseTo(1000, 1);
  const s = await lab.evaluate((e) => ({ th: +e.dataset.theta, x: +e.dataset.pinMm, v: +e.dataset.vel }));
  const w = (1000 * 2 * Math.PI) / 60;
  expect(s.x).toBeCloseTo(50 * Math.cos(s.th) + Math.sqrt(200 ** 2 - 50 ** 2 * Math.sin(s.th) ** 2), 2);
  expect(s.v).toBeCloseTo((-50 * w * Math.sin(s.th) - (2500 * w * Math.sin(s.th) * Math.cos(s.th)) / Math.sqrt(40000 - 2500 * Math.sin(s.th) ** 2)) / 1000, 3);
  const seen = new Set();
  await expect.poll(async () => { const t = await page.getByTestId('ta-engine-status').textContent(); if (STROKE.test(t)) seen.add(t); return seen.size; }, { timeout: 30_000, intervals: [100] }).toBe(4);
  await tab(page, info, ID, 'tele');
  await expect(page.getByTestId('ta-engine-telemetry')).toContainText('500'); // the cam turns at half crank speed
});

test('engine: ideal Otto pressure from lesson 10.12, and the scripted loop', async ({ page }) => {
  const lab = await gotoLab(page, ID);
  const c = await page.evaluate(() => { const a = window.__mefs.engine; return [a.cycle(1e-6).p, a.cycle(2 * Math.PI - 1e-6).p, a.cycle(2 * Math.PI + 1e-6).p]; });
  expect(c[0]).toBeCloseTo(100, 3);
  expect(Math.round(c[1])).toBe(2510); // end of compression, r = 10
  expect(Math.round(c[2])).toBe(8081); // just after the spark, 1200 kJ/kg
  const status = page.getByTestId('ta-engine-status');
  await seek(page, ID, 1); await expect(status).toHaveText('IDLE');
  await seek(page, ID, 8); await expect(status).toHaveText(STROKE);
  await seek(page, ID, 19); await expect(status).toHaveText('TEARDOWN'); await expect(lab).toHaveAttribute('data-exploded', 'true');
  await seek(page, ID, 25); await expect(lab).toHaveAttribute('data-exploded', 'false'); await expect(status).toHaveText('REASSEMBLE');
  await seek(page, ID, 30); await expect(status).toHaveText('IDLE');
});

test('engine: find-the-part quiz @device', async ({ page }, info) => {
  await gotoLab(page, ID);
  await tab(page, info, ID, 'parts');
  const quiz = page.getByTestId('ta-engine-quiz');
  await expect(quiz).toContainText('0 / 3');
  const pick = (pid) => page.evaluate((pid) => window.__mefs.engine.openCard(pid), pid);
  await pick('crank-0'); await expect(quiz).toContainText('Try again');
  await pick('cam-0'); await expect(quiz).toContainText('1 / 3');
  await pick('fly-0'); await expect(quiz).toContainText('2 / 3');
  await pick('piston-0'); await expect(quiz).toContainText('3 / 3');
  await expect(quiz).toContainText('All found');
  expect(await page.locator('#lab-engine').innerText()).not.toMatch(/\bXP\b/);
});

test('engine: the #lab-engine address opens the lab straight away', async ({ page }) => {
  await page.goto('./#lab-engine');
  const lab = page.locator('#lab-engine');
  await expect(lab).toBeVisible({ timeout: 45_000 });
  await expect.poll(() => lab.evaluate((e) => Math.abs(e.getBoundingClientRect().top) < 200), { timeout: 15_000 }).toBe(true);
});
