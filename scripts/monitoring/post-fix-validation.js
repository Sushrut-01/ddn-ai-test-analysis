const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== POST-FIX VALIDATION TESTING ===\n");
  console.log("Verifying Claude''s bug fixes and checking for remaining issues\n");
  
  const results = {
    fixed: [],
    stillBroken: [],
    newIssues: []
  };
  
  // ========================================
  // TEST 1: Suite Metadata (Bug #1)
  // ========================================
  console.log("TEST 1: Suite Metadata\n" + "=".repeat(50));
  
  const response = await fetch("http://localhost:5006/api/failures?limit=5");
  const apiData = await response.json();
  const failures = apiData.data.failures;
  
  console.log(`Fetched ${failures.length} failures from API\n`);
  
  let hasMetadata = 0;
  failures.forEach((f, i) => {
    console.log(`Failure ${i+1}: ${f.test_name?.substring(0, 50)}...`);
    console.log(`  Suite Name: ${f.suite_name || "MISSING"}`);
    console.log(`  Pass Count: ${f.pass_count !== undefined ? f.pass_count : "MISSING"}`);
    console.log(`  Fail Count: ${f.fail_count !== undefined ? f.fail_count : "MISSING"}`);
    console.log(`  Total Count: ${f.total_count !== undefined ? f.total_count : "MISSING"}`);
    
    if (f.suite_name && f.pass_count !== undefined && f.fail_count !== undefined) {
      hasMetadata++;
      console.log(`   Has complete metadata`);
    } else {
      console.log(`   Metadata incomplete`);
    }
    console.log("");
  });
  
  if (hasMetadata === failures.length) {
    results.fixed.push("Bug #1: Suite metadata now present in ALL failures");
    console.log(` BUG #1 FIXED: ${hasMetadata}/${failures.length} failures have complete metadata\n`);
  } else if (hasMetadata > 0) {
    results.stillBroken.push(`Bug #1: Partial fix - only ${hasMetadata}/${failures.length} have metadata (need to re-run Robot tests)`);
    console.log(`  BUG #1 PARTIAL: ${hasMetadata}/${failures.length} have metadata (old data still exists)\n`);
  } else {
    results.stillBroken.push("Bug #1: Suite metadata still missing from all failures");
    console.log(` BUG #1 NOT FIXED: No failures have suite metadata\n`);
  }
  
  // ========================================
  // TEST 2: AI Analysis (Bug #2)
  // ========================================
  console.log("\nTEST 2: AI Analysis Confidence\n" + "=".repeat(50));
  
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  const failuresTable = page.locator("table").nth(3);
  const rows = await failuresTable.locator("tbody tr").all();
  
  console.log(`Checking ${rows.length} failures on Dashboard\n`);
  
  let hasAnalysis = 0;
  let hasZeroPercent = 0;
  
  for (let i = 0; i < Math.min(rows.length, 10); i++) {
    const cells = await rows[i].locator("td").allTextContents();
    const aiStatus = cells[4]; // AI Analysis Status column
    
    console.log(`Row ${i+1}: ${cells[1].substring(0, 40)}...`);
    console.log(`  AI Status: "${aiStatus}"`);
    
    if (aiStatus.includes("0%")) {
      hasZeroPercent++;
      console.log(`   Still showing 0%`);
    } else if (aiStatus.match(/\d+%/) && !aiStatus.includes("0%")) {
      hasAnalysis++;
      console.log(`   Has non-zero confidence`);
    } else {
      console.log(`  ? Status: ${aiStatus}`);
    }
  }
  
  console.log("");
  
  if (hasAnalysis > 5) {
    results.fixed.push(`Bug #2: AI analysis working - ${hasAnalysis}/10 have non-zero confidence`);
    console.log(` BUG #2 FIXED: ${hasAnalysis}/10 failures have AI analysis\n`);
  } else if (hasZeroPercent === rows.length) {
    results.stillBroken.push("Bug #2: All failures still show 0% confidence");
    console.log(` BUG #2 NOT FIXED: All ${rows.length} still show 0%\n`);
  } else {
    results.newIssues.push(`AI Analysis: Mixed results - ${hasAnalysis} working, ${hasZeroPercent} at 0%`);
    console.log(`  BUG #2 PARTIAL: Need to trigger aging service\n`);
  }
  
  // ========================================
  // TEST 3: Build ID Consistency (Bug #3)
  // ========================================
  console.log("\nTEST 3: Build ID Format\n" + "=".repeat(50));
  
  const buildIds = failures.map(f => f.build_id);
  console.log("Build IDs from API:");
  buildIds.forEach((id, i) => console.log(`  ${i+1}. ${id}`));
  
  const standardFormat = /^[\w-]+-\d+$/; // job-name-123 format
  const standardized = buildIds.filter(id => standardFormat.test(id));
  
  console.log(`\nStandardized format: ${standardized.length}/${buildIds.length}`);
  
  if (standardized.length === buildIds.length) {
    results.fixed.push("Bug #3: All build IDs now use standardized format");
    console.log(` BUG #3 FIXED: All build IDs standardized\n`);
  } else if (standardized.length > 0) {
    results.fixed.push(`Bug #3: Partial - ${standardized.length}/${buildIds.length} use new format (old data remains)`);
    console.log(`  BUG #3 PARTIAL: New failures use standard format, old data unchanged\n`);
  } else {
    results.stillBroken.push("Bug #3: Build IDs still inconsistent");
    console.log(` BUG #3 NOT FIXED\n`);
  }
  
  // ========================================
  // TEST 4: Trigger Analysis Page (Bug #4)
  // ========================================
  console.log("\nTEST 4: Trigger Analysis Page\n" + "=".repeat(50));
  
  await page.goto("http://localhost:5173/trigger-analysis");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const checkboxes = await page.locator("input[type=''checkbox'']").count();
  const analyzeBtn = await page.locator("button:has-text(''Analyze'')").first();
  const failureCount = await page.locator("table tbody tr, [class*=''list''] > *").count();
  
  console.log(`Checkboxes: ${checkboxes}`);
  console.log(`Analyze button: ${await analyzeBtn.count() > 0 ? "Present" : "Missing"}`);
  console.log(`Failures displayed: ${failureCount}`);
  
  if (checkboxes > 0 && await analyzeBtn.count() > 0) {
    results.fixed.push("Bug #4: Trigger Analysis page fully functional");
    console.log(` BUG #4: Confirmed working (not a bug)\n`);
  } else {
    results.newIssues.push("Bug #4: Page still incomplete");
    console.log(` BUG #4: Still has issues\n`);
  }
  
  await page.screenshot({ path: "post-fix-validation.png", fullPage: true });
  
  // ========================================
  // TEST 5: Recheck Additional Bugs
  // ========================================
  console.log("\nTEST 5: Rechecking Additional Bugs\n" + "=".repeat(50));
  
  // Bug #6: View buttons on Failures page
  await page.goto("http://localhost:5173/failures");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const viewButtons = await page.locator("button:has-text(''View'')").count();
  console.log(`\nBug #6 (View Buttons): ${viewButtons} found`);
  
  if (viewButtons > 0) {
    results.fixed.push("Bug #6: View buttons now present on Failures page");
  } else {
    results.stillBroken.push("Bug #6: View buttons still missing");
  }
  
  // Bug #7: Pagination
  const pagination = await page.locator("button:has-text(''Next''), button:has-text(''Previous''), [class*=''pagination'']").count();
  console.log(`Bug #7 (Pagination): ${pagination > 0 ? "Present" : "Missing"}`);
  
  if (pagination === 0) {
    results.stillBroken.push("Bug #7: Pagination still missing");
  }
  
  // Bug #9: Manual Trigger inputs
  await page.goto("http://localhost:5173/manual-trigger");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const inputs = await page.locator("input[type=''text''], input[name*=''build''], input[name*=''job'']").count();
  console.log(`Bug #9 (Manual Trigger Inputs): ${inputs} input fields`);
  
  if (inputs === 0) {
    results.stillBroken.push("Bug #9: Manual Trigger still missing input fields");
  }
  
  await browser.close();
  
  // ========================================
  // FINAL SUMMARY
  // ========================================
  console.log("\n" + "=".repeat(70));
  console.log("VALIDATION RESULTS");
  console.log("=".repeat(70) + "\n");
  
  console.log(` FIXED (${results.fixed.length}):`);
  results.fixed.forEach(item => console.log(`   ${item}`));
  
  console.log(`\n STILL BROKEN (${results.stillBroken.length}):`);
  results.stillBroken.forEach(item => console.log(`   ${item}`));
  
  console.log(`\n  NEW ISSUES (${results.newIssues.length}):`);
  results.newIssues.forEach(item => console.log(`   ${item}`));
  
  console.log("\n" + "=".repeat(70));
  
  if (results.stillBroken.length === 0) {
    console.log(" ALL CRITICAL BUGS FIXED! Ready for E2E testing!");
  } else {
    console.log("  Some issues remain - review needed before E2E testing");
  }
  
  console.log("\nScreenshot: post-fix-validation.png");
})();
