import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import { watchConsole, noOverflow } from './helpers.js';

// Every written lesson must render cleanly: no console errors, no KaTeX errors, widgets drawn, no sideways overflow.
const index = JSON.parse(fs.readFileSync(process.env.LESSON_INDEX || new URL('../public/lessons/index.json', import.meta.url)));
const ids = index.written;

test.describe('All written lessons', () => {
  test.describe.configure({ mode: 'parallel' });
  const chunks = [];
  for (let i = 0; i < ids.length; i += 8) chunks.push(ids.slice(i, i + 8));
  for (const chunk of chunks) {
    test(`lessons ${chunk[0]} to ${chunk[chunk.length - 1]} render cleanly @sweep`, async ({ page }) => {
      test.setTimeout(30_000 + chunk.length * 8_000);
      const errors = watchConsole(page);
      for (const id of chunk) {
        await page.goto(`./learn.html#/${id}`);
        await expect(page.locator('.lb-title')).toContainText(id);
        await expect(page.locator('#check-yourself .qq').first()).toBeAttached();
        await expect(page.locator('.coming')).toHaveCount(0);
        expect(await page.locator('.katex-error').count(), `${id} KaTeX errors`).toBe(0);
        const widgets = page.locator('.widget[data-widget]');
        const nw = await widgets.count();
        for (let i = 0; i < nw; i++) {
          await widgets.nth(i).scrollIntoViewIfNeeded();
          await expect(widgets.nth(i), `${id} widget ${i}`).toHaveAttribute('data-ready', '1');
          await expect(widgets.nth(i).locator('.w-out')).not.toHaveText('');
          await expect(widgets.nth(i).locator('.muted')).toHaveCount(0);
        }
        expect(await page.locator('#check-yourself .qq').count(), `${id} quiz`).toBeGreaterThanOrEqual(3);
        expect(await noOverflow(page), `${id} overflow`).toBe(true);
      }
      expect(errors, errors.join('\n')).toEqual([]);
    });
  }
});
