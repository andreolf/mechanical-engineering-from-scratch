import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import { watchConsole, noOverflow, shot, isTouch, smallTargets } from './helpers.js';

const clear = async (page) => { await page.goto('./learn.html#/course'); await page.evaluate(() => localStorage.clear()); };

async function answerAll(page, scope, questions, wrongIndex = -1) {
  const qs = page.locator(`${scope} .qq`);
  for (let i = 0; i < questions.length; i++) {
    const q = questions[i], el = qs.nth(i);
    if (q.type === 'mc') {
      const pick = i === wrongIndex ? (q.answer + 1) % q.options.length : q.answer;
      await el.locator('.opt').nth(pick).click();
    } else {
      await el.locator('input').fill(String(i === wrongIndex ? q.answer * 3 + 1 : q.answer));
    }
  }
}

test.describe('Lessons, quizzes, progress and certificates', () => {
  test('a full lesson renders math, code, figures and solutions, without overflow @device', async ({ page }, info) => {
    const errors = watchConsole(page);
    await clear(page);
    await page.goto('./learn.html#/01.08');
    await expect(page.locator('h1')).toContainText('Small-angle physics');
    expect(await page.locator('.prose .katex').count()).toBeGreaterThan(10);
    await expect(page.locator('.math-display').first()).toBeVisible();
    await expect(page.locator('.katex-error')).toHaveCount(0);
    await expect(page.locator('figure.code a[download]')).toHaveAttribute('href', /code\/01-08-pendulum\.py$/);
    const code = await page.request.get(await page.locator('figure.code a[download]').getAttribute('href'));
    expect(code.ok()).toBeTruthy();
    expect(await code.text()).toContain('def period_ratio');
    await expect(page.locator('.widget[data-ready="1"]')).toHaveCount(1);
    const sol = page.locator('details.solution').first();
    await expect(sol).not.toHaveAttribute('open', '');
    await sol.locator('summary').click();
    await expect(sol).toHaveAttribute('open', '');
    // long equations scroll inside their own box, the page never scrolls sideways
    expect(await noOverflow(page)).toBe(true);
    const wide = await page.evaluate(() => [...document.querySelectorAll('.math-display, .code pre')].every((el) => getComputedStyle(el).overflowX === 'auto'));
    expect(wide).toBe(true);
    if (isTouch(info)) {
      const bar = await page.locator('#lesson-bar').boundingBox();
      expect(bar.height).toBeLessThanOrEqual(64);                  // compact sticky bar
      await page.locator('#toc-btn').click();
      await expect(page.locator('#lesson-side')).toBeVisible();
      await page.locator('#lesson-side a[href="#/01.09"]').click();
      await expect(page.locator('h1')).toContainText('Riemann');
      await page.goBack();
      const small = await smallTargets(page, 'main');
      expect(small, small.join('\n')).toEqual([]);
    }
    await page.goto('./learn.html#/01.08');
    await page.waitForTimeout(300);
    await page.screenshot({ path: shot(info, 'lesson') });
    await page.locator('.widget').scrollIntoViewIfNeeded();
    await page.screenshot({ path: shot(info, 'lesson-widget') });
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('quiz grades multiple-choice and numeric answers with tolerance @device', async ({ page }, info) => {
    const errors = watchConsole(page);
    await clear(page);
    await page.goto('./learn.html#/00.02');
    await page.waitForFunction(() => window.__mefs?.lessonQuiz);
    const quiz = await page.evaluate(() => window.__mefs.lessonQuiz);
    const iNum = quiz.findIndex((q) => q.type === 'num');
    // first attempt: one wrong answer
    await answerAll(page, '#check-yourself', quiz, iNum);
    await page.getByRole('button', { name: 'Check answers' }).click();
    await expect(page.locator('#check-yourself .score')).toHaveText(`${quiz.length - 1} of ${quiz.length} correct`);
    await expect(page.locator('#check-yourself .qq').nth(iNum)).toHaveClass(/is-incorrect/);
    await expect(page.locator('#check-yourself .qq').nth(iNum).locator('.fb')).toContainText(/Not quite|Incorrect|correct answer/i);
    const xp1 = await page.evaluate(() => JSON.parse(localStorage.getItem('mefs.v2')).xp);
    expect(xp1).toBe(10 * (quiz.length - 1));
    // a value inside the tolerance (but not exact) is accepted
    const q = quiz[iNum];
    await page.locator('#check-yourself .qq').nth(iNum).locator('input').fill(String(q.answer * (1 + q.tol / 2)));
    await page.getByRole('button', { name: 'Check answers' }).click();
    await expect(page.locator('#check-yourself .score')).toHaveText(`${quiz.length} of ${quiz.length} correct`);
    await expect(page.locator('#site-nav [data-xp]')).toHaveText(String(10 * quiz.length));
    // outside the tolerance is rejected
    await page.locator('#check-yourself .qq').nth(iNum).locator('input').fill(String(q.answer * (1 + q.tol * 3)));
    await page.getByRole('button', { name: 'Check answers' }).click();
    await expect(page.locator('#check-yourself .qq').nth(iNum)).toHaveClass(/is-incorrect/);
    await page.locator('#check-yourself .qq').nth(iNum).scrollIntoViewIfNeeded();
    await page.screenshot({ path: shot(info, 'quiz') });
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('lesson progress, XP and streak persist across reloads @device', async ({ page }, info) => {
    await clear(page);
    await page.goto('./learn.html#/00.01');
    await page.getByRole('button', { name: 'Mark lesson as done' }).click();
    await expect(page.locator('.done-line')).toContainText('Lesson done');
    await page.reload();
    await expect(page.locator('.done-line')).toContainText('Lesson done');
    await page.goto('./learn.html#/progress');
    await expect(page.locator('[data-stat=done]')).toHaveText('1');
    await expect(page.locator('[data-stat=xp]')).toHaveText('50');
    await expect(page.locator('[data-stat=streak]')).toHaveText('1');
    await page.goto('./learn.html#/course');
    await expect(page.locator('[data-k=done]')).toHaveText('1');
    // every lesson is written: the last capstone renders in full, with no outline fallback
    await page.goto('./learn.html#/19.10');
    await expect(page.locator('h1')).toContainText('Publish');
    await expect(page.locator('.widget[data-ready="1"]')).toHaveCount(1);
    await expect(page.locator('.coming')).toHaveCount(0);
    await page.goto('./learn.html#/progress');
    expect(await noOverflow(page)).toBe(true);
    await page.screenshot({ path: shot(info, 'progress'), fullPage: false });
  });

  test('phase test: pass at 80% unlocks a downloadable, verifiable certificate @device', async ({ page }, info) => {
    const errors = watchConsole(page);
    await clear(page);
    await page.goto('./learn.html#/test/00');
    await page.waitForFunction(() => window.__mefs?.currentTest?.length >= 10);
    const qs = await page.evaluate(() => window.__mefs.currentTest);
    await answerAll(page, '#test-quiz', qs, 0);                     // one wrong: 11/12 = 92%
    await page.getByRole('button', { name: 'Submit test' }).click();
    await expect(page.locator('#test-result')).toContainText('Passed');
    await page.getByRole('link', { name: 'Create certificate' }).click();
    await page.locator('#cert-name').fill('Ada Lovelace');
    await page.getByRole('button', { name: 'Create certificate' }).click();
    await expect(page.locator('#cert-code')).toHaveText(/^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}$/);
    const code = await page.locator('#cert-code').textContent();
    await expect(page.locator('.cert-honesty')).toContainText(/isn’t affiliated with or endorsed by ETH Zurich/);
    const [png] = await Promise.all([page.waitForEvent('download'), page.locator('#dl-png').click()]);
    expect(png.suggestedFilename()).toMatch(/certificate-phase-00-ada-lovelace\.png/);
    const pngBytes = fs.readFileSync(await png.path());
    expect(pngBytes.subarray(1, 4).toString()).toBe('PNG');
    const [pdf] = await Promise.all([page.waitForEvent('download'), page.locator('#dl-pdf').click()]);
    const pdfBytes = fs.readFileSync(await pdf.path());
    expect(pdfBytes.subarray(0, 5).toString()).toBe('%PDF-');
    expect(pdfBytes.subarray(-6).toString()).toContain('%%EOF');
    await page.locator('#cert-canvas').scrollIntoViewIfNeeded();
    expect(await noOverflow(page)).toBe(true);
    // nav chip with 3-digit XP must stay inside the viewport
    const chip = await page.locator('.xp-chip').first().boundingBox();
    expect(chip.x + chip.width).toBeLessThanOrEqual(page.viewportSize().width - 4);
    await page.screenshot({ path: shot(info, 'certificate') });
    if (info.project.name === 'desktop') fs.writeFileSync(shot(info, 'certificate-image'), pngBytes);
    // verify page recomputes the same code from the printed details
    const date = await page.evaluate(() => JSON.parse(localStorage.getItem('mefs.v2')).tests['00'].passedAt);
    await page.goto('./learn.html#/verify');
    await page.locator('[name=name]').fill('Ada Lovelace');
    await page.locator('[name=date]').fill(date);
    await page.locator('[name=scope]').selectOption('phase-00');
    await page.locator('[name=code]').fill(code);
    await page.getByRole('button', { name: 'Check code' }).click();
    await expect(page.locator('#verify-out')).toContainText('Match');
    await page.locator('[name=name]').fill('Ada Lovelace2');
    await page.getByRole('button', { name: 'Check code' }).click();
    await expect(page.locator('#verify-out')).toContainText('No match');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('full course: passing all 20 phase tests earns a course certificate that verifies @device', async ({ page }, info) => {
    test.setTimeout(300_000);
    const errors = watchConsole(page);
    await clear(page);
    const phases = Array.from({ length: 20 }, (_, i) => String(i).padStart(2, '0'));
    for (const ph of phases) {
      await page.goto(`./learn.html#/test/${ph}`);
      await page.waitForFunction((p) => window.__mefs?.route === `test/${p}` && window.__mefs?.currentTest?.length >= 10, ph);
      const qs = await page.evaluate(() => window.__mefs.currentTest);
      await answerAll(page, '#test-quiz', qs);
      await page.getByRole('button', { name: 'Submit test' }).click();
      await expect(page.locator('#test-result')).toContainText('Passed');
      await page.evaluate(() => { window.__mefs.currentTest = null; });
    }
    await page.goto('./learn.html#/progress');
    await expect(page.getByRole('link', { name: 'Create course certificate' })).toBeVisible();
    await page.getByRole('link', { name: 'Create course certificate' }).click();
    await expect(page.locator('h1')).toHaveText('Full-course certificate');
    await page.locator('#cert-name').fill('Ada Lovelace');
    await page.getByRole('button', { name: 'Create certificate' }).click();
    await expect(page.locator('#cert-code')).toHaveText(/^[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}$/);
    const code = await page.locator('#cert-code').textContent();
    const cert = await page.evaluate(() => window.__mefs.cert.details);
    expect(cert.scope).toBe('course');
    expect(cert.phases).toEqual(phases);
    const [png] = await Promise.all([page.waitForEvent('download'), page.locator('#dl-png').click()]);
    expect(png.suggestedFilename()).toMatch(/certificate-course-ada-lovelace\.png/);
    const [pdf] = await Promise.all([page.waitForEvent('download'), page.locator('#dl-pdf').click()]);
    expect(fs.readFileSync(await pdf.path()).subarray(0, 5).toString()).toBe('%PDF-');
    await page.locator('#cert-canvas').scrollIntoViewIfNeeded();
    expect(await noOverflow(page)).toBe(true);
    await page.screenshot({ path: shot(info, 'course-certificate') });
    // the verify page recomputes the code from the printed details
    const date = await page.evaluate(() => { const t = JSON.parse(localStorage.getItem('mefs.v2')).tests; return Object.values(t).map((x) => x.passedAt).sort().pop(); });
    expect(date).toBe(cert.date);
    await page.goto('./learn.html#/verify');
    await page.locator('[name=name]').fill('Ada Lovelace');
    await page.locator('[name=date]').fill(date);
    await page.locator('[name=scope]').selectOption('course');
    await page.locator('[name=code]').fill(code);
    await page.getByRole('button', { name: 'Check code' }).click();
    await expect(page.locator('#verify-out')).toContainText('Match');
    await page.locator('[name=scope]').selectOption('phase-19');
    await page.getByRole('button', { name: 'Check code' }).click();
    await expect(page.locator('#verify-out')).toContainText('No match');
    expect(errors, errors.join('\n')).toEqual([]);
  });

  test('failing a phase test keeps the certificate locked', async ({ page }) => {
    await clear(page);
    await page.goto('./learn.html#/test/01');
    await page.waitForFunction(() => window.__mefs?.currentTest?.length >= 10);
    await page.getByRole('button', { name: 'Submit test' }).click();      // blank answers
    await expect(page.locator('#test-result')).toContainText('You need');
    await page.goto('./learn.html#/cert/01');
    await expect(page.locator('main')).toContainText('Pass the phase 01 test');
    await page.goto('./learn.html#/cert/course');
    await expect(page.locator('main')).toContainText('all 20 phase tests');
  });
});
