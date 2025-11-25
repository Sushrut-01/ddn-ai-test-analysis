import { test } from '@playwright/nextjs-utils';
import { expect } from '@playwright/nextjs-utils';
import { getServerSideProps } from '../../src/pages/manual-analyze';

test('manual-analyze', async ({ page }) => {
  const response = await getServerSideProps({});

  const { data } = response;

  const { title, description } = data;

  await page.goto(`http://localhost:3000/manual-analyze`);

  await page.getByRole('heading', { name: title }).toBeVisible();

  await page.getByRole('heading', { name: description }).toBeVisible();

  // Click the Analyze Now button
  const analyzeButton = page.getByRole('button', { name: /Analyze Now|Analyze|Trigger Analysis/i });
  await expect(analyzeButton).toBeVisible({ timeout: 10000 });
  await analyzeButton.click();
});