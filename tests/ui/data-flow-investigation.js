const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== DATA FLOW INVESTIGATION ===\n");
  
  // Enable request/response logging
  page.on("response", async (response) => {
    if (response.url().includes("/api/")) {
      console.log(`API: ${response.status()} ${response.url()}`);
      if (response.status() !== 200) {
        console.log(`    Non-200 response!`);
      }
    }
  });
  
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      console.log(`Browser Error: ${msg.text()}`);
    }
  });
  
  // Check Main Dashboard data loading
  console.log("1. Main Dashboard Data Loading\n" + "=".repeat(50));
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  // Check if test failures table exists
  const tables = await page.locator("table").all();
  console.log(`\n Found ${tables.length} tables on page`);
  
  for (let i = 0; i < tables.length; i++) {
    const headers = await tables[i].locator("th").allTextContents();
    const rows = await tables[i].locator("tbody tr").count();
    console.log(`\nTable ${i + 1}:`);
    console.log(`  Headers: ${headers.join(", ")}`);
    console.log(`  Rows: ${rows}`);
    
    if (headers.join("").includes("Build") || headers.join("").includes("Test")) {
      console.log(`   This appears to be the Test Failures table`);
      
      if (rows === 0) {
        console.log(`    EMPTY! No data loaded`);
        
        // Check for error messages or loading states
        const errorMsg = await page.locator("text=/error|failed|no data|loading/i").count();
        if (errorMsg > 0) {
          const msgs = await page.locator("text=/error|failed|no data|loading/i").allTextContents();
          console.log(`  Error/status messages: ${msgs.join(", ")}`);
        }
      }
    }
  }
  
  // Check Failures Page
  console.log("\n\n2. Failures Page Data Loading\n" + "=".repeat(50));
  await page.goto("http://localhost:5173/failures");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  const failuresList = await page.locator("table tbody tr, [class*='list'] > *").count();
  console.log(`\n Failures displayed: ${failuresList}`);
  
  if (failuresList > 0) {
    // Get first few items details
    console.log("\nSample failures:");
    const rows = await page.locator("table tbody tr").all();
    for (let i = 0; i < Math.min(3, rows.length); i++) {
      const text = await rows[i].textContent();
      console.log(`  ${i + 1}. ${text.substring(0, 100)}...`);
    }
    
    // Check for View buttons
    const viewBtns = await page.locator("button:has-text('View')").count();
    console.log(`\n View buttons found: ${viewBtns}`);
    
    if (viewBtns > 0) {
      console.log("\nTesting navigation to Failure Details...");
      const firstBtn = page.locator("button:has-text('View')").first();
      await firstBtn.click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(2000);
      
      const detailsUrl = page.url();
      console.log(` Navigated to: ${detailsUrl}`);
      
      // Check details page content
      const content = await page.locator("body").textContent();
      if (content.includes("error") || content.includes("Error")) {
        console.log("  Page shows error");
      } else {
        console.log(" Details page loaded successfully");
      }
    }
  }
  
  // Direct API test
  console.log("\n\n3. Direct API Testing\n" + "=".repeat(50));
  
  const apiTests = [
    { name: "Test Failures", url: "http://localhost:5006/api/failures?limit=10" },
    { name: "Analytics Summary", url: "http://localhost:5006/api/analytics/summary" },
    { name: "System Status", url: "http://localhost:5006/api/system/status" }
  ];
  
  for (const test of apiTests) {
    try {
      console.log(`\nTesting: ${test.name}`);
      const response = await fetch(test.url);
      console.log(`  Status: ${response.status}`);
      
      if (response.status === 200) {
        const data = await response.json();
        console.log(`  Data keys: ${Object.keys(data).join(", ")}`);
        
        if (test.name === "Test Failures" && data.data) {
          console.log(`  Failures count: ${data.data.failures?.length || 0}`);
          console.log(`  Total: ${data.data.total || 0}`);
        }
      } else {
        console.log(`    Failed to fetch`);
      }
    } catch (e) {
      console.log(`   Error: ${e.message}`);
    }
  }
  
  await page.waitForTimeout(2000);
  await browser.close();
  
  console.log("\n" + "=".repeat(70));
  console.log("INVESTIGATION COMPLETE");
  console.log("=".repeat(70));
})();
