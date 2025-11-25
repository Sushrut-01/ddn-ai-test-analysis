const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto("http://localhost:5173");
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(3000);
  
  console.log("=== SEARCHING FOR TRIGGER/ANALYZE ELEMENTS ===\n");
  
  // Check all clickable elements with analyze/trigger text
  const triggers = await page.locator("*:has-text('Trigger'), *:has-text('Analyze'), *:has-text('Manual')").all();
  console.log(`Found ${triggers.length} elements with trigger/analyze text\n`);
  
  for (let i = 0; i < triggers.length; i++) {
    const el = triggers[i];
    const tag = await el.evaluate(e => e.tagName);
    const text = await el.textContent();
    const visible = await el.isVisible();
    const clickable = await el.evaluate(e => {
      return e.tagName === "BUTTON" || e.tagName === "A" || e.onclick !== null || e.getAttribute("role") === "button";
    });
    
    console.log(`${i+1}. <${tag}> "${text.trim().substring(0, 60)}"`);
    console.log(`   Visible: ${visible}, Clickable: ${clickable}`);
    
    if (clickable && visible && tag === "BUTTON") {
      const classes = await el.evaluate(e => e.className);
      console.log(`   Classes: "${classes}"`);
      console.log(`    THIS IS A BUTTON!`);
    }
    console.log("");
  }
  
  await page.waitForTimeout(2000);
  await browser.close();
})();
