const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  console.log("=== DASHBOARD CONTENT ANALYSIS ===\n");
  
  // Check for builds/test results sections
  const headings = await page.locator("h1, h2, h3, h4").all();
  console.log(`Found ${headings.length} headings:`);
  for (let h of headings) {
    const text = await h.textContent();
    console.log(`  - "${text}"`);
  }
  
  console.log("\n=== TABLES (Test Results/Builds) ===");
  const tables = await page.locator("table").all();
  console.log(`Found ${tables.length} tables`);
  for (let i = 0; i < tables.length; i++) {
    const rows = await tables[i].locator("tr").all();
    console.log(`\nTable ${i+1}: ${rows.length} rows`);
    if (rows.length > 0) {
      const firstRow = await rows[0].textContent();
      console.log(`  Header: "${firstRow}"`);
      if (rows.length > 1) {
        const secondRow = await rows[1].textContent();
        console.log(`  Sample: "${secondRow}"`);
      }
    }
  }
  
  console.log("\n=== LISTS/CARDS (Failed Tests) ===");
  const lists = await page.locator("ul, ol, [class*=card], [class*=list]").all();
  console.log(`Found ${lists.length} list/card elements`);
  
  console.log("\n=== TEXT CONTAINING 'fail', 'pass', 'build', 'test' ===");
  const keywords = await page.locator("text=/fail|pass|build|test|suite|jenkins/i").all();
  console.log(`Found ${keywords.length} elements with keywords`);
  for (let i = 0; i < Math.min(keywords.length, 15); i++) {
    const text = await keywords[i].textContent();
    const visible = await keywords[i].isVisible();
    if (visible && text.trim().length > 0) {
      console.log(`  ${i+1}. "${text.trim().substring(0, 80)}"`);
    }
  }
  
  await page.screenshot({ path: "dashboard-full-content.png", fullPage: true });
  console.log("\n Screenshot saved: dashboard-full-content.png");
  
  await page.waitForTimeout(3000);
  await browser.close();
})();
