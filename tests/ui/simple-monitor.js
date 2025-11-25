const fetch = require("node-fetch");

console.log("=== JENKINS BUILD MONITORING ===\n");
console.log("Watching for new failures from Jenkins builds...\n");

let lastCount = 833;
let checkNum = 0;

async function check() {
  checkNum++;
  
  try {
    const response = await fetch("http://localhost:5006/api/failures?limit=5");
    const data = await response.json();
    const currentCount = data.data.total;
    const failures = data.data.failures;
    
    if (currentCount > lastCount) {
      const newCount = currentCount - lastCount;
      console.log(`\n [${new Date().toLocaleTimeString()}] NEW FAILURES: +${newCount}`);
      console.log("=".repeat(60));
      
      const recentFailures = failures.slice(0, Math.min(newCount, 5));
      recentFailures.forEach((f, i) => {
        console.log(`\n${i+1}. ${f.test_name?.substring(0, 50)}...`);
        console.log(`   Build: ${f.build_id}`);
        console.log(`   Job: ${f.job_name}`);
        console.log(`   Suite: ${f.suite_name || " MISSING"}`);
        console.log(`   Pass/Fail: ${f.pass_count}/${f.fail_count} of ${f.total_count || ""}`);
        
        const hasMetadata = f.suite_name && f.pass_count !== undefined;
        const standardBuildId = /^[\w-]+-\d+$/.test(f.build_id);
        
        if (hasMetadata) console.log("    Suite metadata present!");
        if (standardBuildId) console.log("    Standard build ID format!");
      });
      
      console.log("\n" + "=".repeat(60));
      lastCount = currentCount;
    } else if (checkNum % 12 === 0) {
      console.log(`[${new Date().toLocaleTimeString()}] Monitoring... (${currentCount} total failures)`);
    }
    
  } catch (err) {
    console.log(`Error: ${err.message}`);
  }
  
  setTimeout(check, 5000);
}

check();
