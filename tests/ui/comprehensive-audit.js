const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log("=== COMPREHENSIVE DASHBOARD PAGES AUDIT ===\n");
  console.log("Testing all pages for completeness, functionality, and data issues\n");
  
  const issues = [];
  const baseUrl = "http://localhost:5173";
  
  // ========================================
  // PAGE 1: Main Dashboard (/)
  // ========================================
  console.log("1. MAIN DASHBOARD (/)\n" + "=".repeat(50));
  await page.goto(baseUrl);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  // Check hero section
  const heroHeading = await page.locator("h1, h2").first().textContent();
  console.log(` Hero heading: "${heroHeading}"`);
  
  // Check statistics cards
  const statCards = await page.locator("[class*='card'], [class*='Card']").count();
  console.log(` Found ${statCards} cards/sections`);
  
  // Check failures table
  const mainTable = await page.locator("table").nth(3);
  const mainRows = await mainTable.locator("tbody tr").count();
  console.log(` Failures table: ${mainRows} rows`);
  
  if (mainRows === 0) {
    issues.push("Main Dashboard: No failures displayed in table");
  }
  
  // Check for action buttons in table
  const viewButtons = await mainTable.locator("button:has-text('View')").count();
  console.log(` View buttons: ${viewButtons}`);
  
  if (viewButtons === 0) {
    issues.push("Main Dashboard: No View buttons in failures table");
  }
  
  // Check for "View All" link
  const viewAllLink = await page.locator("text=/view all|see all/i").count();
  console.log(` View All link: ${viewAllLink > 0 ? "Present" : "Missing"}`);
  
  if (viewAllLink === 0) {
    issues.push("Main Dashboard: Missing View All Failures link");
  }
  
  await page.screenshot({ path: "audit-01-dashboard.png", fullPage: true });
  console.log(" Screenshot saved\n");
  
  // ========================================
  // PAGE 2: Failures List (/failures)
  // ========================================
  console.log("\n2. FAILURES PAGE (/failures)\n" + "=".repeat(50));
  await page.goto(`${baseUrl}/failures`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  // Check page heading
  const failuresHeading = await page.locator("h1, h2, h3, h4").first().textContent();
  console.log(` Page heading: "${failuresHeading}"`);
  
  // Check search functionality
  const searchBox = await page.locator("input[type='text'], input[placeholder*='search' i]").count();
  console.log(` Search box: ${searchBox > 0 ? "Present" : "Missing"}`);
  
  if (searchBox === 0) {
    issues.push("Failures Page: Missing search functionality");
  }
  
  // Check filters
  const filterDropdowns = await page.locator("select, [role='combobox']").count();
  console.log(` Filter dropdowns: ${filterDropdowns}`);
  
  // Check pagination
  const pagination = await page.locator("button:has-text('Next'), button:has-text('Previous'), [class*='pagination']").count();
  console.log(` Pagination controls: ${pagination > 0 ? "Present" : "Missing"}`);
  
  if (pagination === 0) {
    issues.push("Failures Page: Missing pagination controls");
  }
  
  // Check failures list/table
  const failuresTable = await page.locator("table, [class*='list']").count();
  const failuresRows = await page.locator("table tbody tr, [class*='list'] > *").count();
  console.log(` Failures displayed: ${failuresRows} items`);
  
  if (failuresRows === 0) {
    issues.push("Failures Page: No failures displayed");
  }
  
  await page.screenshot({ path: "audit-02-failures.png", fullPage: true });
  console.log(" Screenshot saved\n");
  
  // ========================================
  // PAGE 3: Failure Details (/failures/:id)
  // ========================================
  console.log("\n3. FAILURE DETAILS PAGE\n" + "=".repeat(50));
  
  // Try to click first View button to go to details
  try {
    await page.goto(`${baseUrl}/failures`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(1000);
    
    const firstViewBtn = page.locator("button:has-text('View')").first();
    if (await firstViewBtn.count() > 0) {
      await firstViewBtn.click();
      await page.waitForLoadState("networkidle");
      await page.waitForTimeout(2000);
      
      const detailsUrl = page.url();
      console.log(` Navigated to: ${detailsUrl}`);
      
      // Check page content
      const detailsHeading = await page.locator("h1, h2, h3, h4").first().textContent();
      console.log(` Page heading: "${detailsHeading}"`);
      
      // Check for error message
      const errorMsg = await page.locator("text=/error message|error:|stack trace/i").count();
      console.log(` Error message section: ${errorMsg > 0 ? "Present" : "Missing"}`);
      
      if (errorMsg === 0) {
        issues.push("Failure Details: Missing error message display");
      }
      
      // Check for AI analysis section
      const aiAnalysis = await page.locator("text=/ai analysis|recommendation|root cause/i").count();
      console.log(` AI analysis section: ${aiAnalysis > 0 ? "Present" : "Missing"}`);
      
      // Check for tabs (stack trace, raw data, etc)
      const tabs = await page.locator("[role='tab'], button[class*='tab']").count();
      console.log(` Tabs: ${tabs}`);
      
      // Check for back button
      const backBtn = await page.locator("button:has-text('Back'), a:has-text('Back')").count();
      console.log(` Back button: ${backBtn > 0 ? "Present" : "Missing"}`);
      
      if (backBtn === 0) {
        issues.push("Failure Details: Missing back button");
      }
      
      // Check for feedback/actions
      const feedbackBtn = await page.locator("button:has-text('Feedback'), button:has-text('Accept'), button:has-text('Reject')").count();
      console.log(` Feedback buttons: ${feedbackBtn}`);
      
      await page.screenshot({ path: "audit-03-failure-details.png", fullPage: true });
      console.log(" Screenshot saved\n");
    } else {
      console.log(" Could not navigate to details - no View button found\n");
      issues.push("Failures Page: Cannot navigate to Failure Details (no View button)");
    }
  } catch (e) {
    console.log(` Error accessing Failure Details: ${e.message}\n`);
    issues.push(`Failure Details: Error loading page - ${e.message}`);
  }
  
  // ========================================
  // PAGE 4: Analytics (/analytics)
  // ========================================
  console.log("\n4. ANALYTICS PAGE (/analytics)\n" + "=".repeat(50));
  await page.goto(`${baseUrl}/analytics`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const analyticsHeading = await page.locator("h1, h2, h3, h4").first().textContent();
  console.log(` Page heading: "${analyticsHeading}"`);
  
  // Check for charts/graphs
  const charts = await page.locator("canvas, svg[class*='chart'], [class*='Chart']").count();
  console.log(` Charts/graphs: ${charts}`);
  
  if (charts === 0) {
    issues.push("Analytics: No charts/visualizations found");
  }
  
  // Check for metrics cards
  const metricsCards = await page.locator("[class*='metric'], [class*='stat']").count();
  console.log(` Metrics cards: ${metricsCards}`);
  
  // Check for time range selector
  const timeRange = await page.locator("select, button:has-text('7d'), button:has-text('30d')").count();
  console.log(` Time range selector: ${timeRange > 0 ? "Present" : "Missing"}`);
  
  // Check for data tables
  const analyticsTables = await page.locator("table").count();
  console.log(` Data tables: ${analyticsTables}`);
  
  await page.screenshot({ path: "audit-04-analytics.png", fullPage: true });
  console.log(" Screenshot saved\n");
  
  // ========================================
  // PAGE 5: Manual Trigger (/manual-trigger)
  // ========================================
  console.log("\n5. MANUAL TRIGGER PAGE (/manual-trigger)\n" + "=".repeat(50));
  
  try {
    await page.goto(`${baseUrl}/manual-trigger`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    
    const manualHeading = await page.locator("h1, h2, h3, h4").first().textContent();
    console.log(` Page heading: "${manualHeading}"`);
    
    // Check for form fields
    const buildIdInput = await page.locator("input[name*='build' i], input[placeholder*='build' i]").count();
    console.log(` Build ID input: ${buildIdInput > 0 ? "Present" : "Missing"}`);
    
    const jobNameInput = await page.locator("input[name*='job' i], input[placeholder*='job' i]").count();
    console.log(` Job Name input: ${jobNameInput > 0 ? "Present" : "Missing"}`);
    
    // Check for trigger button
    const triggerBtn = await page.locator("button:has-text('Trigger'), button:has-text('Submit'), button:has-text('Analyze')").count();
    console.log(` Trigger button: ${triggerBtn > 0 ? "Present" : "Missing"}`);
    
    if (triggerBtn === 0) {
      issues.push("Manual Trigger: Missing trigger/submit button");
    }
    
    // Check for history/results section
    const historySection = await page.locator("text=/history|recent|previous/i").count();
    console.log(` History section: ${historySection > 0 ? "Present" : "Missing"}`);
    
    await page.screenshot({ path: "audit-05-manual-trigger.png", fullPage: true });
    console.log(" Screenshot saved\n");
  } catch (e) {
    console.log(` Error accessing Manual Trigger: ${e.message}\n`);
    issues.push(`Manual Trigger: Error loading page - ${e.message}`);
  }
  
  // ========================================
  // PAGE 6: Trigger Analysis (/trigger-analysis)
  // ========================================
  console.log("\n6. TRIGGER ANALYSIS PAGE (/trigger-analysis)\n" + "=".repeat(50));
  await page.goto(`${baseUrl}/trigger-analysis`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const triggerAnalysisHeading = await page.locator("h1, h2, h3, h4").first().textContent();
  console.log(` Page heading: "${triggerAnalysisHeading}"`);
  
  // Check for failures list with checkboxes
  const checkboxes = await page.locator("input[type='checkbox']").count();
  console.log(` Checkboxes: ${checkboxes}`);
  
  if (checkboxes === 0) {
    issues.push("Trigger Analysis: No checkboxes for selecting failures");
  }
  
  // Check for bulk action buttons
  const selectAllBtn = await page.locator("button:has-text('Select All')").count();
  const deselectBtn = await page.locator("button:has-text('Deselect')").count();
  const analyzeBtn = await page.locator("button:has-text('Analyze')").count();
  
  console.log(` Select All: ${selectAllBtn > 0 ? "Present" : "Missing"}`);
  console.log(` Deselect All: ${deselectBtn > 0 ? "Present" : "Missing"}`);
  console.log(` Analyze button: ${analyzeBtn > 0 ? "Present" : "Missing"}`);
  
  // Check if failures list is populated
  const failureItems = await page.locator("table tbody tr, [class*='list'] > [class*='item']").count();
  console.log(` Failures displayed: ${failureItems}`);
  
  if (failureItems === 0) {
    issues.push("Trigger Analysis: No failures displayed for selection");
  }
  
  await page.screenshot({ path: "audit-06-trigger-analysis.png", fullPage: true });
  console.log(" Screenshot saved\n");
  
  // ========================================
  // PAGE 7: Knowledge Management (/knowledge)
  // ========================================
  console.log("\n7. KNOWLEDGE MANAGEMENT PAGE (/knowledge)\n" + "=".repeat(50));
  
  try {
    await page.goto(`${baseUrl}/knowledge`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);
    
    const knowledgeHeading = await page.locator("h1, h2, h3, h4").first().textContent();
    console.log(` Page heading: "${knowledgeHeading}"`);
    
    // Check for document list/grid
    const documents = await page.locator("table tbody tr, [class*='document'], [class*='card']").count();
    console.log(` Documents/items: ${documents}`);
    
    // Check for upload functionality
    const uploadBtn = await page.locator("button:has-text('Upload'), input[type='file']").count();
    console.log(` Upload button: ${uploadBtn > 0 ? "Present" : "Missing"}`);
    
    // Check for search
    const knowledgeSearch = await page.locator("input[type='text'], input[placeholder*='search' i]").count();
    console.log(` Search box: ${knowledgeSearch > 0 ? "Present" : "Missing"}`);
    
    await page.screenshot({ path: "audit-07-knowledge.png", fullPage: true });
    console.log(" Screenshot saved\n");
  } catch (e) {
    console.log(` Error accessing Knowledge page: ${e.message}\n`);
    issues.push(`Knowledge Management: Error loading page - ${e.message}`);
  }
  
  // ========================================
  // CROSS-PAGE CHECKS
  // ========================================
  console.log("\n8. CROSS-PAGE FEATURES\n" + "=".repeat(50));
  
  // Check navigation menu
  await page.goto(baseUrl);
  await page.waitForTimeout(1000);
  
  const navItems = await page.locator("nav a, nav button").count();
  console.log(` Navigation menu items: ${navItems}`);
  
  const expectedPages = ["Dashboard", "Failures", "Analytics", "Manual Trigger", "Trigger Analysis", "Knowledge"];
  console.log("\nChecking navigation for all pages:");
  for (const pageName of expectedPages) {
    const exists = await page.locator(`text="${pageName}"`).count() > 0;
    console.log(`  ${exists ? "" : ""} ${pageName}`);
    if (!exists) {
      issues.push(`Navigation: Missing link to ${pageName} page`);
    }
  }
  
  // Check for user profile/settings
  const userMenu = await page.locator("[class*='user'], [class*='profile'], [class*='avatar']").count();
  console.log(`\n User menu/profile: ${userMenu > 0 ? "Present" : "Missing"}`);
  
  // Check for notifications
  const notifications = await page.locator("[class*='notification'], [class*='alert'], [class*='badge']").count();
  console.log(` Notifications: ${notifications > 0 ? "Present" : "Missing"}`);
  
  // ========================================
  // FINAL SUMMARY
  // ========================================
  console.log("\n" + "=".repeat(70));
  console.log("AUDIT SUMMARY");
  console.log("=".repeat(70) + "\n");
  
  console.log(`Pages tested: 7`);
  console.log(`Screenshots captured: 7`);
  console.log(`Issues found: ${issues.length}\n`);
  
  if (issues.length > 0) {
    console.log("ISSUES FOUND:\n");
    issues.forEach((issue, i) => {
      console.log(`${i + 1}. ${issue}`);
    });
  } else {
    console.log(" No major issues found! All pages have basic functionality.\n");
  }
  
  console.log("\nScreenshots saved:");
  console.log("  - audit-01-dashboard.png");
  console.log("  - audit-02-failures.png");
  console.log("  - audit-03-failure-details.png");
  console.log("  - audit-04-analytics.png");
  console.log("  - audit-05-manual-trigger.png");
  console.log("  - audit-06-trigger-analysis.png");
  console.log("  - audit-07-knowledge.png");
  
  await page.waitForTimeout(2000);
  await browser.close();
})();
