const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  console.log("=== TEST FAILURES TABLE ANALYSIS ===\n");
  
  // Find the test failures table
  const table = page.locator("table").nth(3); // 4th table (0-indexed)
  const headers = await table.locator("th").allTextContents();
  console.log("Table Headers:");
  headers.forEach((h, i) => console.log(`  ${i+1}. ${h}`));
  
  console.log("\n=== ALL TEST FAILURE ROWS ===");
  const rows = await table.locator("tbody tr").all();
  console.log(`Total rows: ${rows.length}\n`);
  
  for (let i = 0; i < rows.length; i++) {
    const cells = await rows[i].locator("td").allTextContents();
    console.log(`Row ${i+1}:`);
    console.log(`  Build ID: ${cells[0]}`);
    console.log(`  Test Name: ${cells[1]}`);
    console.log(`  Job Name: ${cells[2]}`);
    console.log(`  Aging Days: ${cells[3]}`);
    console.log(`  AI Status: ${cells[4]}`);
    console.log(`  AI Recommendation: ${cells[5]}`);
    console.log(`  Timestamp: ${cells[6]}`);
    console.log(`  Actions: ${cells[7]}`);
    console.log("");
  }
  
  console.log("=== CHECKING FOR ANALYZE/TRIGGER BUTTONS ===");
  const analyzeButtons = await page.locator("text=/analyze|trigger/i").all();
  console.log(`Found ${analyzeButtons.length} elements with analyze/trigger text`);
  for (let btn of analyzeButtons) {
    const text = await btn.textContent();
    const tag = await btn.evaluate(el => el.tagName);
    console.log(`  <${tag}>: "${text}"`);
  }
  
  console.log("\n=== VIEW BUTTONS IN TABLE ===");
  const viewButtons = await table.locator("button:has-text('View')").all();
  console.log(`Found ${viewButtons.length} View buttons`);
  
  console.log("\n=== WORKFLOW: Expected Flow ===");
  console.log("1. Jenkins builds run and fail");
  console.log("2. Failed tests appear in Dashboard table");
  console.log("3. User triggers AI analysis (WHERE IS THIS BUTTON?)");
  console.log("4. AI analyzes failures and provides recommendations");
  console.log("5. Results show in 'AI Analysis Status' and 'AI Recommendation' columns");
  
  await page.waitForTimeout(3000);
  await browser.close();
})();
