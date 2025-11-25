const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== POST-FIX VALIDATION TESTING ===\n");
  
  const results = { fixed: [], stillBroken: [], newIssues: [] };
  
  // TEST 1: Suite Metadata
  console.log("TEST 1: Suite Metadata (Bug #1)\n" + "=".repeat(50));
  
  const response = await fetch("http://localhost:5006/api/failures?limit=5");
  const apiData = await response.json();
  const failures = apiData.data.failures;
  
  console.log(`Fetched ${failures.length} failures\n`);
  
  let hasMetadata = 0;
  failures.forEach((f, i) => {
    console.log(`${i+1}. ${f.test_name?.substring(0, 40)}...`);
    const has = f.suite_name && f.pass_count !== undefined;
    console.log(`   Suite: ${f.suite_name || "MISSING"}, Pass: ${f.pass_count !== undefined ? f.pass_count : "MISSING"}`);
    if (has) hasMetadata++;
  });
  
  console.log(`\nResult: ${hasMetadata}/${failures.length} have metadata`);
  if (hasMetadata === 0) {
    results.stillBroken.push("Bug #1: Suite metadata missing (need to run Robot tests with new listener)");
    console.log(" NOT FIXED - Old data has no metadata\n");
  } else if (hasMetadata === failures.length) {
    results.fixed.push("Bug #1: All failures have suite metadata");
    console.log(" FIXED\n");
  } else {
    results.newIssues.push(`Bug #1: Partial - ${hasMetadata}/${failures.length}`);
    console.log("  PARTIAL\n");
  }
  
  // TEST 2: AI Analysis
  console.log("TEST 2: AI Analysis (Bug #2)\n" + "=".repeat(50));
  
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  const table = page.locator("table").nth(3);
  const rows = await table.locator("tbody tr").count();
  console.log(`Dashboard table rows: ${rows}\n`);
  
  if (rows > 0) {
    const cells = await table.locator("tbody tr").first().locator("td").allTextContents();
    console.log(`First row AI status: "${cells[4]}"`);
    
    if (cells[4].includes("0%")) {
      results.stillBroken.push("Bug #2: AI still showing 0% (need to trigger aging service)");
      console.log(" NOT FIXED - Need to run: curl -X POST http://localhost:5007/trigger-now\n");
    } else {
      results.fixed.push("Bug #2: AI analysis showing confidence scores");
      console.log(" FIXED\n");
    }
  } else {
    results.newIssues.push("Dashboard table empty - cannot verify AI analysis");
    console.log("  Cannot verify - table empty\n");
  }
  
  // TEST 3: Build IDs
  console.log("TEST 3: Build ID Format (Bug #3)\n" + "=".repeat(50));
  
  const buildIds = failures.map(f => f.build_id);
  console.log("Build IDs:", buildIds.join(", "));
  
  const standardFormat = /^[\w-]+-\d+$/;
  const standardized = buildIds.filter(id => standardFormat.test(id)).length;
  
  console.log(`Standardized: ${standardized}/${buildIds.length}`);
  if (standardized === 0) {
    results.stillBroken.push("Bug #3: Old data still has old format (expected - only affects new failures)");
    console.log("  Expected - old data unchanged\n");
  } else {
    results.fixed.push(`Bug #3: ${standardized}/${buildIds.length} use new format`);
    console.log(" Working for new data\n");
  }
  
  // TEST 4: Additional Bugs
  console.log("TEST 4: Additional Issues\n" + "=".repeat(50));
  
  await page.goto("http://localhost:5173/failures");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const viewBtns = await page.locator("button:has-text(\"View\")").count();
  console.log(`View buttons: ${viewBtns}`);
  results.stillBroken.push(`Bug #6: View buttons still missing (${viewBtns} found)`);
  
  const pagination = await page.locator("[class*=\"pagination\"]").count();
  console.log(`Pagination: ${pagination > 0 ? "Present" : "Missing"}`);
  if (pagination === 0) results.stillBroken.push("Bug #7: Pagination missing");
  
  await page.screenshot({ path: "post-fix-validation.png", fullPage: true });
  await browser.close();
  
  // SUMMARY
  console.log("\n" + "=".repeat(70));
  console.log("SUMMARY");
  console.log("=".repeat(70));
  console.log(`\n Fixed: ${results.fixed.length}`);
  results.fixed.forEach(r => console.log(`   - ${r}`));
  console.log(`\n Still Broken: ${results.stillBroken.length}`);
  results.stillBroken.forEach(r => console.log(`   - ${r}`));
  console.log(`\n  New Issues: ${results.newIssues.length}`);
  results.newIssues.forEach(r => console.log(`   - ${r}`));
  
  console.log("\n NEXT STEPS:");
  console.log("1. Run Robot tests with new listener to generate metadata");
  console.log("2. Trigger aging service: curl -X POST http://localhost:5007/trigger-now");
  console.log("3. Share ADDITIONAL-BUGS-FOUND.md with Claude for remaining fixes");
})();
