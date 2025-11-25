const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== JENKINS BUILD DATA VALIDATION ===\n");
  
  // 1. Check API health and data source
  console.log("1. Checking API health...");
  const apiResponse = await fetch("http://localhost:5006/api/health");
  const apiHealth = await apiResponse.json();
  console.log(`   API Status: ${apiHealth.status}`);
  
  // 2. Fetch test failures from API
  console.log("\n2. Fetching test failures from API...");
  const failuresResponse = await fetch("http://localhost:5006/api/test-failures");
  const apiFailures = await failuresResponse.json();
  console.log(`   API returned ${apiFailures.length} failures`);
  
  // 3. Load Dashboard
  console.log("\n3. Loading Dashboard UI...");
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  // 4. Validate test failures table
  console.log("\n4. Validating Test Failures Table...");
  const table = page.locator("table").nth(3);
  const rows = await table.locator("tbody tr").all();
  console.log(`   Dashboard shows ${rows.length} failures`);
  
  if (apiFailures.length !== rows.length) {
    console.log(`     MISMATCH: API has ${apiFailures.length} but Dashboard shows ${rows.length}`);
  } else {
    console.log(`    Count matches`);
  }
  
  // 5. Check each row for required fields
  console.log("\n5. Checking data completeness for each failure...\n");
  const issues = [];
  
  for (let i = 0; i < rows.length; i++) {
    const cells = await rows[i].locator("td").allTextContents();
    const row = {
      buildId: cells[0],
      testName: cells[1],
      jobName: cells[2],
      agingDays: cells[3],
      aiStatus: cells[4],
      aiRecommendation: cells[5],
      timestamp: cells[6]
    };
    
    console.log(`Row ${i+1}: ${row.testName.substring(0, 50)}...`);
    
    // Validate Build ID
    if (!row.buildId || row.buildId.length < 5) {
      issues.push(`Row ${i+1}: Missing or invalid Build ID`);
      console.log(`    Build ID missing or invalid`);
    } else {
      console.log(`    Build ID: ${row.buildId}`);
    }
    
    // Validate Test Name
    if (!row.testName || row.testName.trim().length === 0) {
      issues.push(`Row ${i+1}: Missing Test Name`);
      console.log(`    Test Name missing`);
    }
    
    // Validate Job Name
    if (!row.jobName || row.jobName.trim().length === 0) {
      issues.push(`Row ${i+1}: Missing Job Name`);
      console.log(`    Job Name missing`);
    }
    
    // Check AI Analysis Status
    if (row.aiStatus.includes("0%") || row.aiStatus.includes("N/A")) {
      console.log(`     AI Analysis: ${row.aiStatus} (Not analyzed or failed)`);
    }
    
    // Check AI Recommendation
    if (row.aiRecommendation.includes("N/A") || row.aiRecommendation.includes("No recommendation")) {
      console.log(`     No AI Recommendation available`);
    }
    
    console.log("");
  }
  
  // 6. Check for complete test suite info
  console.log("\n6. Checking for Test Suite Information...");
  const apiFailure = apiFailures[0];
  console.log(`   Sample API failure keys: ${Object.keys(apiFailure).join(", ")}`);
  
  const requiredFields = ["build_id", "test_name", "job_name", "timestamp", "suite_name", "pass_count", "fail_count", "total_count"];
  const missingFields = requiredFields.filter(field => !(field in apiFailure));
  
  if (missingFields.length > 0) {
    console.log(`    Missing fields in API: ${missingFields.join(", ")}`);
  } else {
    console.log(`    All required fields present`);
  }
  
  // 7. Summary
  console.log("\n=== DATA VALIDATION SUMMARY ===\n");
  console.log(`Total Failures: ${rows.length}`);
  console.log(`Issues Found: ${issues.length}`);
  
  if (issues.length > 0) {
    console.log("\nIssues:");
    issues.forEach(issue => console.log(`  - ${issue}`));
  }
  
  // Check for pass/fail counts
  console.log("\nTest Suite Completeness:");
  console.log(`  Pass Count: ${apiFailure.pass_count || "MISSING"}`);
  console.log(`  Fail Count: ${apiFailure.fail_count || "MISSING"}`);
  console.log(`  Total Count: ${apiFailure.total_count || "MISSING"}`);
  console.log(`  Suite Name: ${apiFailure.suite_name || "MISSING"}`);
  
  await page.screenshot({ path: "data-validation.png", fullPage: true });
  console.log("\n Screenshot saved: data-validation.png");
  
  await page.waitForTimeout(3000);
  await browser.close();
})();
