const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== COMPLETE JENKINS BUILD DATA VALIDATION ===\n");
  console.log("Checking: Build completeness, test suite data, pass/fail counts\n");
  
  // 1. Fetch from API first
  console.log("1. Fetching test failures from API...");
  const response = await fetch("http://localhost:5006/api/failures?limit=50");
  const apiData = await response.json();
  const apiFailures = apiData.data.failures;
  console.log(`    API returned ${apiFailures.length} failures\n`);
  
  // 2. Validate API data structure
  console.log("2. Validating API data completeness...\n");
  const requiredFields = [
    "build_id", "test_name", "job_name", "timestamp",
    "error_message", "stack_trace"
  ];
  
  const desiredFields = [
    "suite_name", "pass_count", "fail_count", "total_count",
    "build_url", "jenkins_job_url"
  ];
  
  let issues = [];
  let missingCounts = 0;
  
  apiFailures.slice(0, 5).forEach((failure, i) => {
    console.log(`Sample ${i+1}: ${failure.test_name.substring(0, 50)}...`);
    console.log(`  Build ID: ${failure.build_id || "MISSING"}`);
    console.log(`  Job Name: ${failure.job_name || "MISSING"}`);
    console.log(`  Suite Name: ${failure.suite_name || "NOT PROVIDED"}`);
    console.log(`  Pass Count: ${failure.pass_count !== undefined ? failure.pass_count : "NOT PROVIDED"}`);
    console.log(`  Fail Count: ${failure.fail_count !== undefined ? failure.fail_count : "NOT PROVIDED"}`);
    console.log(`  Total Count: ${failure.total_count !== undefined ? failure.total_count : "NOT PROVIDED"}`);
    console.log(`  AI Analysis: ${failure.ai_analysis ? " Available" : " Not analyzed"}`);
    
    if (failure.pass_count === undefined || failure.fail_count === undefined) {
      missingCounts++;
    }
    console.log("");
  });
  
  // 3. Load Dashboard UI
  console.log("\n3. Loading Dashboard UI...");
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  console.log("    Dashboard loaded\n");
  
  // 4. Check test failures table
  console.log("4. Validating Dashboard table display...");
  const table = page.locator("table").nth(3);
  const rows = await table.locator("tbody tr").all();
  console.log(`   Dashboard shows ${rows.length} rows\n`);
  
  // 5. Validate each row
  console.log("5. Checking each row for completeness...\n");
  
  for (let i = 0; i < Math.min(rows.length, 10); i++) {
    const cells = await rows[i].locator("td").allTextContents();
    console.log(`Row ${i+1}:`);
    console.log(`  Build ID: ${cells[0]}`);
    console.log(`  Test: ${cells[1].substring(0, 60)}...`);
    console.log(`  Job: ${cells[2]}`);
    console.log(`  Aging: ${cells[3]}`);
    console.log(`  AI Status: ${cells[4]}`);
    console.log(`  Recommendation: ${cells[5].substring(0, 40)}...`);
    
    // Validate critical fields
    if (!cells[0] || cells[0].length < 5) {
      issues.push(`Row ${i+1}: Missing Build ID`);
    }
    if (!cells[1] || cells[1].trim().length === 0) {
      issues.push(`Row ${i+1}: Missing Test Name`);
    }
    if (!cells[2] || cells[2].trim().length === 0) {
      issues.push(`Row ${i+1}: Missing Job Name`);
    }
    console.log("");
  }
  
  // 6. Check for test suite summary
  console.log("\n6. Checking for Test Suite Summary Info...");
  const suiteInfo = await page.locator("text=/suite|pass|fail|total/i").all();
  console.log(`   Found ${suiteInfo.length} elements mentioning suite/pass/fail info`);
  
  if (suiteInfo.length === 0) {
    issues.push("Dashboard does not display test suite pass/fail counts");
  }
  
  // 7. Final Summary
  console.log("\n=== VALIDATION SUMMARY ===\n");
  console.log(`Total Failures in API: ${apiFailures.length}`);
  console.log(`Failures shown in Dashboard: ${rows.length}`);
  console.log(`Failures missing pass/fail counts: ${missingCounts}/${apiFailures.length}`);
  console.log(`Critical Issues Found: ${issues.length}\n`);
  
  if (issues.length > 0) {
    console.log("Issues:");
    issues.forEach(issue => console.log(`   ${issue}`));
  } else {
    console.log(" All validations passed!");
  }
  
  // 8. Data Flow Check
  console.log("\n=== DATA FLOW VERIFICATION ===\n");
  console.log("Expected Flow:");
  console.log("1. Jenkins runs test suites");
  console.log("2. Failed tests reported to MongoDB with:");
  console.log("   - Build ID, Test Name, Job Name ");
  console.log("   - Error Message, Stack Trace ");
  console.log("   - Suite Name, Pass/Fail/Total counts", missingCounts === 0 ? "" : " MISSING");
  console.log("3. Dashboard fetches from MongoDB ");
  console.log("4. AI analysis runs and stores in PostgreSQL");
  console.log("5. Dashboard shows combined data \n");
  
  if (missingCounts > 0) {
    console.log("  WARNING: Test suite pass/fail counts not being captured from Jenkins");
    console.log("   This data should be included in Jenkins webhook payload");
    console.log("   Check: implementation/jenkins_integration_service.py");
  }
  
  await page.screenshot({ path: "complete-validation.png", fullPage: true });
  console.log("\n Screenshot saved: complete-validation.png");
  
  await page.waitForTimeout(3000);
  await browser.close();
})();
