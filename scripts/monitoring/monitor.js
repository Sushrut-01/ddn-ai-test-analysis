const { chromium } = require("playwright");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  
  console.log("=== JENKINS BUILD MONITORING ACTIVE ===");
  console.log("Baseline: 833 failures");
  console.log("Watching for new failures every 5 seconds...");
  console.log("Press Ctrl+C to stop\n");
  
  let lastCount = 833;
  let checkNum = 0;
  
  const check = async () => {
    checkNum++;
    
    try {
      const response = await context.request.get("http://localhost:5006/api/failures?limit=5");
      const data = await response.json();
      const currentCount = data.data.total;
      const failures = data.data.failures;
      
      if (currentCount > lastCount) {
        const newCount = currentCount - lastCount;
        console.log(`\n [${new Date().toLocaleTimeString()}] NEW FAILURES DETECTED: +${newCount}`);
        console.log("=".repeat(70));
        
        for (let i = 0; i < Math.min(newCount, 5); i++) {
          const f = failures[i];
          console.log(`\n${i+1}. Test: ${f.test_name?.substring(0, 50)}...`);
          console.log(`   Build ID: ${f.build_id}`);
          console.log(`   Job: ${f.job_name}`);
          console.log(`   Suite: ${f.suite_name || " MISSING"}`);
          console.log(`   Pass: ${f.pass_count ?? ""} | Fail: ${f.fail_count ?? ""} | Total: ${f.total_count ?? ""}`);
          
          const hasMetadata = f.suite_name && f.pass_count !== undefined;
          const standardBuildId = /^[\w-]+-\d+$/.test(f.build_id);
          
          if (hasMetadata) {
            console.log(`    BUG #1 FIXED: Suite metadata present!`);
          } else {
            console.log(`     Missing suite metadata (old listener?)`);
          }
          
          if (standardBuildId) {
            console.log(`    BUG #3 FIXED: Standard build ID!`);
          }
        }
        
        console.log("\n" + "=".repeat(70));
        lastCount = currentCount;
      } else if (checkNum % 12 === 0) {
        console.log(`  [${new Date().toLocaleTimeString()}] Still monitoring... (Total: ${currentCount} failures)`);
      }
      
    } catch (err) {
      console.log(`  Error: ${err.message}`);
    }
    
    setTimeout(check, 5000);
  };
  
  await check();
})();
