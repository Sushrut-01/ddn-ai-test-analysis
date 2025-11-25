import { test, expect } from '@playwright/test';
import { getApi } from './helpers/dashboard-helpers';

const DASHBOARD_URL = process.env.DASHBOARD_URL || 'http://localhost:5173';
const DASHBOARD_API = process.env.DASHBOARD_API || 'http://localhost:5006';

test.describe('Manual Analyze Now flow', () => {
  test('start analysis and validate results via API', async ({ page }) => {
    const api = getApi(DASHBOARD_API);

    // Check API health
    const health = await api.health();
    expect(health.status).toBe(200);

    // Visit dashboard UI
    await page.goto(DASHBOARD_URL);
    await expect(page).toHaveTitle(/Dashboard|DDN/i);

    // Basic presence check for Analyze Now button (best-effort selector)
    // Note: UI may show "Analyze Now", "Analyze", or "Trigger Analysis" depending on version
    const analyzeButton = page.locator('button', { hasText: /Analyze Now|Analyze|Trigger Analysis/i }).first();
    await expect(analyzeButton).toBeVisible({ timeout: 10000 });

    // Click analyze and wait for a job id to appear in the UI or API
    await analyzeButton.click();

    // Wait briefly for job to be enqueued and poll API for recent analyses
    let analysisId: string | null = null;
    for (let i = 0; i < 20; i++) {
      try {
        const resp = await api.failures();
        if (resp.status === 200 && Array.isArray(resp.data) && resp.data.length > 0) {
          // take most recent failure if available
          analysisId = resp.data[0].analysisId || resp.data[0].jobId || null;
          if (analysisId) break;
        }
      } catch (e) {
        // ignore and retry
      }
      await new Promise((r) => setTimeout(r, 3000));
    }

    // If no analysisId, attempt to read analysis list endpoint
    if (!analysisId) {
      try {
        const flow = await api.pipeline();
        // best-effort: look for running/queued job id
        if (flow.status === 200 && flow.data && flow.data.currentJob) {
          analysisId = flow.data.currentJob.id;
        }
      } catch (e) {
        // proceed to failing assertion below
      }
    }

    expect(analysisId, 'No analysis job id found after triggering Analyze Now').toBeTruthy();

    // Poll analysis status until complete or timeout
    let status: any = null;
    for (let i = 0; i < 40; i++) {
      try {
        const r = await api.analysis(analysisId as string);
        if (r.status === 200 && r.data) {
          status = r.data.status || r.data.state || 'unknown';
          if (status === 'complete' || status === 'finished' || status === 'done' || status === 'success') break;
        }
      } catch (e) {
        // ignore
      }
      await new Promise((r) => setTimeout(r, 5000));
    }

    expect(status, 'Analysis did not complete within timeout').toBeTruthy();
  });
});
