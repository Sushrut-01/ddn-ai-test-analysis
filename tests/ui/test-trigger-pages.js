const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  console.log("=== TRIGGER ANALYSIS PAGE TESTING ===\n");
  
  // 1. Click on Trigger Analysis in navigation
  console.log("1. Navigating to Trigger Analysis page...");
  await page.click("text='Trigger Analysis'");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  console.log(`   Current URL: ${page.url()}\n`);
  
  // 2. Check page content
  console.log("2. Checking page content...");
  const heading = await page.locator("h1, h2, h3").first().textContent();
  console.log(`   Page heading: "${heading}"\n`);
  
  // 3. Find all buttons
  console.log("3. Finding all buttons on page...");
  const buttons = await page.locator("button").all();
  console.log(`   Found ${buttons.length} buttons\n`);
  
  for (let i = 0; i < buttons.length; i++) {
    const text = await buttons[i].textContent();
    const visible = await buttons[i].isVisible();
    console.log(`   ${i+1}. "${text}" (visible: ${visible})`);
  }
  
  // 4. Find trigger button
  console.log("\n4. Looking for trigger/analyze button...");
  const triggerBtn = await page.locator("button:has-text('Trigger'), button:has-text('Analyze'), button:has-text('Start')").first();
  
  if (await triggerBtn.count() > 0) {
    const btnText = await triggerBtn.textContent();
    console.log(`    Found button: "${btnText}"`);
    console.log(`   Button is ${await triggerBtn.isVisible() ? "visible" : "hidden"}`);
    console.log(`   Button is ${await triggerBtn.isEnabled() ? "enabled" : "disabled"}`);
  } else {
    console.log(`    No trigger button found`);
  }
  
  // 5. Check for Manual Trigger page
  console.log("\n5. Checking Manual Trigger page...");
  await page.goto("http://localhost:5173/manual-trigger");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
  
  const manualHeading = await page.locator("h1, h2, h3").first().textContent();
  console.log(`   Page heading: "${manualHeading}"`);
  
  const manualButtons = await page.locator("button").all();
  console.log(`   Found ${manualButtons.length} buttons:`);
  for (let i = 0; i < Math.min(manualButtons.length, 10); i++) {
    const text = await manualButtons[i].textContent();
    const visible = await manualButtons[i].isVisible();
    console.log(`   ${i+1}. "${text}" (visible: ${visible})`);
  }
  
  await page.screenshot({ path: "trigger-analysis-pages.png", fullPage: true });
  console.log("\n Screenshot saved");
  
  await page.waitForTimeout(3000);
  await browser.close();
})();
