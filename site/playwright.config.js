import { defineConfig, devices } from '@playwright/test';
// desktop and mobile run every test; the device projects run the @device subset
// (layout, touch, lesson, quiz, progress, certificate) on real device profiles.
const dev = { grep: /@device/ };
export default defineConfig({
  testDir: './tests',
  timeout: 90_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  workers: 3,
  reporter: [['list']],
  use: { baseURL: process.env.BASE_URL || 'http://127.0.0.1:4183/', acceptDownloads: true, launchOptions: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] } },
  webServer: process.env.BASE_URL ? undefined : { command: 'npm run build && npx vite preview --port 4183 --strictPort --host 127.0.0.1', url: 'http://127.0.0.1:4183', reuseExistingServer: true, timeout: 180_000 },
  projects: [
    { name: 'desktop', use: { browserName: 'chromium', viewport: { width: 1280, height: 800 } } },
    { name: 'mobile', use: { browserName: 'chromium', viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true } },
    { name: 'pixel7', ...dev, use: { ...devices['Pixel 7'] } },
    { name: 'iphone13', ...dev, use: { ...devices['iPhone 13'], launchOptions: {} } },
    { name: 'iphone14', ...dev, use: { ...devices['iPhone 14'], launchOptions: {} } },
    { name: 'android360', grep: /@device|@sweep/, use: { browserName: 'chromium', viewport: { width: 360, height: 740 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true, userAgent: devices['Galaxy S9+'].userAgent } },
    { name: 'iphone13-landscape', ...dev, use: { ...devices['iPhone 13 landscape'], launchOptions: {} } },
    { name: 'pixel7-landscape', ...dev, use: { ...devices['Pixel 7 landscape'] } },
  ],
});
