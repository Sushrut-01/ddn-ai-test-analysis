import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './',
  timeout: 2 * 60 * 1000,
  expect: { timeout: 10000 },
  reporter: [['list'], ['junit', { outputFile: '../test-results/ui/playwright-junit.xml' }]],
  use: {
    headless: true,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 30000,
    navigationTimeout: 60000
  }
});
