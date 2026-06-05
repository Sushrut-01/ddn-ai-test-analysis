const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== REAL-TIME JENKINS BUILD MONITORING ===\n");
  console.log("Monitoring: Jenkins  MongoDB  Dashboard  AI Analysis\n");
  console.log("Press Ctrl+C to stop monitoring\n");
  console.log("=".repeat(70) + "\n");
  
  // Get baseline
  console.log(" BASELINE (Before Build)");
  console.log("-".repeat(70));
  
  const baselineResponse = await fetch("http://localhost:5006/api/failures?limit=1");
  const baselineData = await baselineResponse.json();
  const baselineTotal = baselineData.data.total;
  const baselineTimestamp = new Date().toISOString();
  
  console.log(`Total failures in MongoDB: ${baselineTotal}`);
  console.log(`Baseline timestamp: ${baselineTimestamp}`);
  console.log("");
  
  // Monitor loop
  let lastCount = baselineTotal;
  let newFailures = [];
  let checkCount = 0;
  const maxChecks = 60; // Monitor for ~5 minutes
  
  console.log(" MONITORING STARTED - Checking every 5 seconds...\n");
  
  while (checkCount < maxChecks) {
    await new Promise(resolve => setTimeout(resolve, 5000));
    checkCount++;
    
    try {
      // Check MongoDB
      const response = await fetch("http://localhost:5006/api/failures?limit=10");
      const data = await response.json();
      const currentTotal = data.data.total;
      const failures = data.data.failures;
      
      // Detect new failures
      if (currentTotal > lastCount) {
        const newCount = currentTotal - lastCount;
        console.log(`\n🆕 NEW FAILURES DETECTED! +${newCount} failures`);
        console.log("=".repeat(70));
        
        // Show new failures details
        const recentFailures = failures.slice(0, newCount);
        recentFailures.forEach((f, i) => {
          console.log(`\n${i + 1}. ${f.test_name || "Unknown Test"}`);
          console.log(`   Build ID: ${f.build_id || "N/A"}`);
          console.log(`   Job: ${f.job_name || "N/A"}`);
          console.log(`   Suite: ${f.suite_name || " MISSING"}`);
          console.log(`   Pass Count: ${f.pass_count !== undefined ? f.pass_count : " MISSING"}`);
          console.log(`   Fail Count: ${f.fail_count !== undefined ? f.fail_count : " MISSING"}`);
          console.log(`   Total Count: ${f.total_count !== undefined ? f.total_count : " MISSING"}`);
          console.log(`   Status: ${f.status || "N/A"}`);
          console.log(`   Timestamp: ${f.timestamp || "N/A"}`);
          
          // Check metadata completeness
          const hasMetadata = f.suite_name && f.pass_count !== undefined;
          if (hasMetadata) {
            console.log(`    BUG #1 FIX VERIFIED: Suite metadata present!`);
          } else {
            console.log(`     Still missing suite metadata`);
          }
          
          // Check build ID format
          const standardFormat = /^[\w-]+-\d+$/;
          if (standardFormat.test(f.build_id)) {
            console.log(`    BUG #3 FIX VERIFIED: Standardized build ID format!`);
          }
          
          newFailures.push(f);
        });
        
        console.log("\n" + "=".repeat(70));
        lastCount = currentTotal;
        
        // Update Dashboard and screenshot
        await page.goto("http://localhost:5173");
        await page.waitForLoadState("networkidle");
        await page.waitForTimeout(2000);
        await page.screenshot({ 
          path: `monitoring-${Date.now()}.png`, 
          fullPage: true 
        });
        console.log(` Dashboard screenshot saved`);
      }
      
      // Progress indicator
      if (checkCount % 6 === 0) {
        console.log(`  [${new Date().toLocaleTimeString()}] Still monitoring... (${checkCount}/${maxChecks} checks)`);
      }
      
    } catch (error) {
      console.log(`  Error during monitoring: ${error.message}`);
    }
  }
  
  // Final summary
  console.log("\n" + "=".repeat(70));
  console.log(" MONITORING SUMMARY");
  console.log("=".repeat(70));
  console.log(`Baseline: ${baselineTotal} failures`);
  console.log(`Final: ${lastCount} failures`);
  console.log(`New failures detected: ${lastCount - baselineTotal}`);
  console.log(`Monitoring duration: ~${(checkCount * 5) / 60} minutes`);
  
  if (newFailures.length > 0) {
    console.log(`\n DETECTED ${newFailures.length} NEW FAILURES`);
    console.log("\nVerification Results:");
    
    const withMetadata = newFailures.filter(f => f.suite_name && f.pass_count !== undefined).length;
    const withStandardId = newFailures.filter(f => /^[\w-]+-\d+$/.test(f.build_id)).length;
    
    console.log(`  Bug #1 (Suite Metadata): ${withMetadata}/${newFailures.length} fixed`);
    console.log(`  Bug #3 (Build ID Format): ${withStandardId}/${newFailures.length} fixed`);
    
    if (withMetadata === newFailures.length && withStandardId === newFailures.length) {
      console.log("\n ALL FIXES VERIFIED! Jenkins integration working perfectly!");
    }
  } else {
    console.log("\n  No new failures detected. Possible reasons:");
    console.log("  - Jenkins build hasn''t started yet");
    console.log("  - All tests passed");
    console.log("  - Jenkins webhook not configured");
  }
  
  await browser.close();
})();
