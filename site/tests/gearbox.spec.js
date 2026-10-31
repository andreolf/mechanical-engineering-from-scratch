// Take-apart lab 01: the two-stage spur reducer, inline in the labs section of the home page.
// desktop and mobile run everything; the @device tests also run on the other Chromium device projects.
import { test, expect } from '@playwright/test';
import { watchConsole, noOverflow } from './helpers.js';
import { gotoLab, lit, tab, seek, setRange, labelsClear } from './takeapart-helpers.js';

let errors;
test.beforeEach(async ({ page }) => { errors = watchConsole(page); await page.goto('./'); });
test.afterEach(async ({ page }) => { expect(errors, errors.join('\n')).toEqual([]); expect(await noOverflow(page)).toBe(true); });
const ID = 'gearbox';

test('gearbox plays inline on the labs section: renders, explodes, isolates and reassembles @device', async ({ page }, info) => {
  const lab = await gotoLab(page, ID);
  expect(await page.locator('#labs #lab-gearbox').count()).toBe(1);
  await expect(page.getByTestId('ta-gearbox-3d')).toHaveAttribute('data-webgl', 'on');
  await expect.poll(() => lit(page, ID), { timeout: 45_000 }).toBeGreaterThan(0.02);
  expect(Number(await lab.locator('[data-parts]').textContent())).toBeGreaterThan(14);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-gearbox-explode').click();
  await expect(lab).toHaveAttribute('data-exploded', 'true');
  await expect(page.getByTestId('ta-gearbox-status')).toHaveText('TEARDOWN');
  await expect.poll(() => lab.locator('.ta-label[data-on="1"]').count()).toBeGreaterThan(2);
  await expect.poll(async () => (await labelsClear(page, ID)).bad, { timeout: 5_000 }).toEqual([]);
  await tab(page, info, ID, 'subs');
  await expect(page.getByTestId('ta-gearbox-badge-input')).toHaveText(/detached/i);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-gearbox-explode').click();
  await expect(lab).toHaveAttribute('data-exploded', 'false');
  for (const a of ['housing', 'input', 'output', 'shafts', 'fasteners']) {
    await page.getByTestId(`ta-gearbox-asm-${a}`).click();
    await expect(lab).toHaveAttribute('data-assembly', a);
  }
  await page.getByTestId('ta-gearbox-asm-all').click();
  await expect(lab).toHaveAttribute('data-assembly', 'all');
});

test('gearbox: a tapped part opens its card, and the card links to the exact lesson @device', async ({ page, isMobile }, info) => {
  await gotoLab(page, ID);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-gearbox-play').click();
  await page.getByTestId('ta-gearbox-turntable').click();
  await page.getByTestId('ta-gearbox-3d').scrollIntoViewIfNeeded();
  await page.waitForTimeout(800);
  const pt = await page.evaluate(() => window.__mefs.gearbox.screenOf('g4-0'));
  if (isMobile) await page.touchscreen.tap(pt.x, pt.y); else await page.mouse.click(pt.x, pt.y);
  const card = page.getByTestId('ta-gearbox-card');
  await expect(card).toBeVisible();
  await expect(card.locator('h5')).not.toBeEmpty(); // the ray takes whatever is in front of the gear's centre
  await expect(card.locator('a[href^="learn.html#/"]').first()).toBeVisible();
  await page.getByTestId('ta-gearbox-card-close').click();
  await expect(card).toBeHidden();
  await page.evaluate(() => window.__mefs.gearbox.openCard('p1-0'));
  await expect(card).toContainText('1.633');
  await expect(card).toContainText('125.6 MPa');
  await expect.poll(async () => (await labelsClear(page, ID)).bad, { timeout: 5_000 }).toEqual([]);
  await card.locator('a[href="learn.html#/15.08"]').click();
  await expect(page).toHaveURL(/learn\.html#\/15\.08$/);
  await expect(page.locator('h1')).toContainText('Gear geometry');
});

test('gearbox: every gear turns at the speed its tooth counts give, and only when the mesh is assembled', async ({ page }, info) => {
  const lab = await gotoLab(page, ID);
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-gearbox-play').click();
  await setRange(page, 'ta-gearbox-rpm', 2000);
  await setRange(page, 'ta-gearbox-torque', 20);
  await expect.poll(async () => Number(await lab.getAttribute('data-rpm')), { timeout: 20_000 }).toBeGreaterThan(1999);
  await expect.poll(async () => Number(await lab.getAttribute('data-tq-in')), { timeout: 20_000 }).toBeGreaterThan(19.99);
  await expect(page.getByTestId('ta-gearbox-status')).toHaveText('UNDER LOAD');
  expect(Number(await lab.getAttribute('data-rpm-mid'))).toBeCloseTo(800, 0);
  expect(Number(await lab.getAttribute('data-rpm-out'))).toBeCloseTo(320, 0);
  expect(Number(await lab.getAttribute('data-tq-out'))).toBeCloseTo(125, 1);
  await page.waitForTimeout(600);
  const a = await page.evaluate(() => window.__mefs.gearbox.angles());
  expect(a.p1).toBeGreaterThan(0.05);
  expect(a.g2 / a.p1).toBeCloseTo(-18 / 45, 6);
  expect(a.p3).toBeCloseTo(a.g2, 6);
  expect(a.g4 / a.p3).toBeCloseTo(-18 / 45, 6);
  expect(a.g4 / a.p1).toBeCloseTo(1 / 6.25, 6);
  await tab(page, info, ID, 'tele');
  const tel = page.getByTestId('ta-gearbox-telemetry');
  await expect(tel).toContainText('6.25 : 1');
  await expect(tel).toContainText('125.0'); // 20 N·m × 6.25
  await expect(tel).toContainText('4.19'); // 20 N·m at 2000 rpm is 4.19 kW
  await tab(page, info, ID, 'parts');
  await page.getByTestId('ta-gearbox-explode').click();
  await expect(page.getByTestId('ta-gearbox-status')).toHaveText('TEARDOWN');
  const th1 = Number(await lab.getAttribute('data-theta'));
  await page.waitForTimeout(800);
  expect(Number(await lab.getAttribute('data-theta'))).toBeCloseTo(th1, 4);
});

test('gearbox: the scripted loop runs idle, spin-up, load, hold, teardown and reassembly', async ({ page }) => {
  const lab = await gotoLab(page, ID);
  const status = page.getByTestId('ta-gearbox-status');
  for (const [t, word, ex] of [[1, 'IDLE', 'false'], [4, 'SPIN-UP', 'false'], [8, 'LOADING', 'false'], [12, 'HOLD', 'false'], [20, 'TEARDOWN', 'true'], [25, 'REASSEMBLE', 'false'], [30, 'IDLE', 'false']]) {
    await seek(page, ID, t);
    await expect(status).toHaveText(word);
    await expect(lab).toHaveAttribute('data-exploded', ex);
  }
  await seek(page, ID, 12);
  await expect.poll(async () => Number(await lab.getAttribute('data-tq-out')), { timeout: 10_000 }).toBeCloseTo(19.1 * 6.25, 1);
  await page.getByTestId('ta-gearbox-scrub').dispatchEvent('change');
  await expect(page.getByTestId('ta-gearbox-log')).toContainText('Scrubbed to 00:12');
});

test('gearbox: find-the-part quiz @device', async ({ page }, info) => {
  await gotoLab(page, ID);
  await tab(page, info, ID, 'parts');
  const quiz = page.getByTestId('ta-gearbox-quiz');
  await expect(quiz).toContainText('0 / 3');
  const pick = (pid) => page.evaluate((pid) => window.__mefs.gearbox.openCard(pid), pid);
  await pick('p1-0');
  await expect(quiz).toContainText('Try again');
  await pick('g4-0'); await expect(quiz).toContainText('1 / 3');
  await pick('key-1'); await expect(quiz).toContainText('2 / 3');
  await pick('breather-0'); await expect(quiz).toContainText('3 / 3');
  await expect(quiz).toContainText('All found');
  expect(await page.locator('#lab-gearbox').innerText()).not.toMatch(/\bXP\b/);
});

test('gearbox: the #lab-gearbox address opens the lab straight away', async ({ page }) => {
  await page.goto('./#lab-gearbox');
  const lab = page.locator('#lab-gearbox');
  await expect(lab).toBeVisible({ timeout: 45_000 });
  await expect.poll(() => lab.evaluate((e) => Math.abs(e.getBoundingClientRect().top) < 200), { timeout: 15_000 }).toBe(true);
});
