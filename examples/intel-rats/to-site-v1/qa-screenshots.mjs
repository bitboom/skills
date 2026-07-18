import fs from 'node:fs';
import path from 'node:path';
import { chromium, devices } from 'playwright';

const baseUrl = process.argv[2] || 'http://127.0.0.1:4173';
const outputDir = process.argv[3] || 'verification/screenshots';
fs.mkdirSync(outputDir, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_PATH || undefined,
});
const cases = [
  { name: 'site-desktop', url: '/', viewport: { width: 1440, height: 1050 }, dpr: 1 },
  { name: 'site-mechanism', url: '/mechanism/', viewport: { width: 1440, height: 1050 }, dpr: 1 },
  { name: 'site-mobile', url: '/', viewport: devices['iPhone 13'].viewport, dpr: 1, isMobile: true, hasTouch: true },
];
const results = [];
try {
  for (const item of cases) {
    const context = await browser.newContext({
      viewport: item.viewport,
      deviceScaleFactor: item.dpr,
      isMobile: item.isMobile ?? false,
      hasTouch: item.hasTouch ?? false,
      userAgent: item.isMobile ? devices['iPhone 13'].userAgent : undefined,
    });
    const page = await context.newPage();
    const failures = [];
    page.on('console', (message) => { if (message.type() === 'error') failures.push(`console: ${message.text()}`); });
    page.on('pageerror', (error) => failures.push(`pageerror: ${error.message}`));
    await page.goto(`${baseUrl}${item.url}`, { waitUntil: 'networkidle' });
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
    if (overflow) failures.push('horizontal overflow');
    if (!await page.locator('main').isVisible()) failures.push('main is not visible');
    if (!await page.locator('h1').isVisible()) failures.push('h1 is not visible');
    const screenshot = path.join(outputDir, `${item.name}.png`);
    await page.screenshot({ path: screenshot, fullPage: true });
    results.push({ name: item.name, url: item.url, viewport: item.viewport, screenshot, failures });
    await context.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(outputDir, 'screenshot-gate.json'), JSON.stringify({ passed: results.every((item) => item.failures.length === 0), results }, null, 2) + '\n');
if (!results.every((item) => item.failures.length === 0)) process.exitCode = 2;
