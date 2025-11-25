const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== RECHECKING AFTER AGING SERVICE TRIGGER ===\n");
  
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  const table = page.locator("table").nth(3);
  const rows = await table.locator("tbody tr").all();
  
  console.log(`Checking ${rows.length} failures for AI analysis updates\n`);
  
  let hasAnalysis = 0;
  let hasZero = 0;
  
  for (let i = 0; i < Math.min(rows.length, 10); i++) {
    const cells = await rows[i].locator("td").allTextContents();
    const aiStatus = cells[4];
    
    console.log(`${i+1}. ${cells[1].substring(0, 40)}...`);
    console.log(`   AI Status: "${aiStatus}"`);
    
    if (aiStatus.includes("0%")) {
      hasZero++;
    } else if (aiStatus.match(/\d+%/) && !aiStatus.includes("0%")) {
      hasAnalysis++;
      console.log(`    Has confidence score`);
    }
  }
  
  console.log(`\nResults: ${hasAnalysis} with analysis, ${hasZero} at 0%`);
  
  if (hasAnalysis > 0) {
    console.log("\n BUG #2 FIXED! AI analysis now working!");
  } else {
    console.log("\n Still showing 0% - aging service may need more time or check logs");
  }
  
  await page.screenshot({ path: "after-aging-trigger.png", fullPage: true });
  await browser.close();
})();
