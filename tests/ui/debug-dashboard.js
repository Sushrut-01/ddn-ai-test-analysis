const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  const buttons = await page.locator("button").all();
  console.log(`Found ${buttons.length} buttons`);
  for (let i = 0; i < buttons.length; i++) {
    const text = await buttons[i].textContent();
    const visible = await buttons[i].isVisible();
    console.log(`${i+1}. "${text}" (visible: ${visible})`);
  }
  await page.screenshot({ path: "dashboard-debug.png", fullPage: true });
  await page.waitForTimeout(3000);
  await browser.close();
})();
