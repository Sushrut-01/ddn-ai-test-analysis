# Claude Agents - Quick Reference

## Available Agents in Dropdown

You should now see **4 specialized agents** in your Claude agent dropdown:

### 1. 🤖 playwright-test-generator
**Purpose**: Automatically generates Playwright test scripts

**When to use**: 
- "Generate a test for the Dashboard analyze button"
- "Create a test that validates the failure list"
- "Write a test for the service status page"

**What it does**:
- Analyzes Dashboard UI at http://localhost:5173
- Generates Playwright test code
- Uses flexible selectors (text, role, CSS)
- Saves to `tests/ui/generated/`

---

### 2. 🔧 playwright-test-healer
**Purpose**: Repairs failing tests automatically

**When to use**:
- "Fix the failing test in manual_analyze.spec.ts"
- "Heal tests that can't find the button"
- "Update selectors for the changed UI"

**What it does**:
- Analyzes failed selectors
- Tries CSS, XPath, text, and role-based alternatives
- Updates test files with working selectors
- Retries up to 3 times
- Documents all fixes

---

### 3. 📋 playwright-test-planner
**Purpose**: Creates test plans from requirements

**When to use**:
- "Create a test plan for the analysis workflow"
- "Plan E2E tests for the Dashboard"
- "Generate test scenarios for error handling"

**What it does**:
- Creates Gherkin format test plans (Given/When/Then)
- Breaks down into scenarios (happy path, edge cases, errors)
- Includes accessibility checks
- Saves to `tests/ui/plans/`
- Estimates execution time and priority

---

### 4. 🎯 qa-dashboard-tester
**Purpose**: Specialized Dashboard E2E testing

**When to use**:
- "Test the entire Dashboard workflow"
- "Verify all Dashboard features work"
- "Run E2E tests on the analysis flow"

**What it does**:
- Tests Dashboard features (Trigger Analysis, failures, analytics)
- Verifies API endpoints (port 5006)
- Checks UI responsiveness
- Validates data display
- Tests error handling

**Knows about**:
- Dashboard URL: http://localhost:5173
- API URL: http://localhost:5006
- Button text: "Trigger Analysis"
- All service endpoints

---

## How to Add Agents to Dropdown

1. **Click the Agent dropdown** (Ctrl+Shift+I or click "Agent" in chat)
2. **Click "Configure Custom Agents..."** at the bottom
3. **Add each agent** by clicking the "+" button
4. **Copy-paste the agent configurations** from below

### Agent 1: playwright-test-generator
```json
{
  "name": "playwright-test-generator",
  "description": "Generates Playwright test scripts from user interactions",
  "prompt": "You are a Playwright Test Generator. Create E2E tests for the DDN Dashboard (http://localhost:5173). Generate Playwright test code with flexible selectors (text-based, role-based), include assertions and waits, save to tests/ui/generated/. Dashboard API: http://localhost:5006, Main button: 'Trigger Analysis'."
}
```

### Agent 2: playwright-test-healer
```json
{
  "name": "playwright-test-healer",
  "description": "Repairs failing Playwright tests automatically",
  "prompt": "You are a Playwright Test Healer. Fix failing tests by analyzing errors and trying alternative selectors: CSS fallback, XPath, text-based (/Trigger Analysis/i), role-based (getByRole). Update test files, document fixes, retry to confirm. Max 3 attempts."
}
```

### Agent 3: playwright-test-planner
```json
{
  "name": "playwright-test-planner",
  "description": "Creates test plans in Gherkin format",
  "prompt": "You are a Playwright Test Planner. Create comprehensive test plans in Gherkin format (Given/When/Then). Include happy path, edge cases, error handling, and accessibility scenarios. Map to Playwright structure and save to tests/ui/plans/. Add priority and time estimates."
}
```

### Agent 4: qa-dashboard-tester
```json
{
  "name": "qa-dashboard-tester",
  "description": "Specialized Dashboard E2E tester",
  "prompt": "You are a QA Dashboard Tester for DDN AI Test Failure Analysis Dashboard. Test: Manual Analysis (button: 'Trigger Analysis' at http://localhost:5173), Failure list, Service status, Analytics, API health (http://localhost:5006/api/health). Verify UI loads, test interactions, validate API responses, check error handling, report with screenshots."
}
```

## How to Use

1. **Select an agent** from the dropdown
2. **Type your request**

### Example Prompts

**Test Generator**:
```
Generate a Playwright test that:
1. Opens the Dashboard
2. Clicks "Trigger Analysis"
3. Waits for analysis to complete
4. Verifies results appear
```

**Test Healer**:
```
Fix the test in manual_analyze.spec.ts that's failing because it can't find the analyze button
```

**Test Planner**:
```
Create a comprehensive test plan for the Dashboard manual analysis feature
```

**Dashboard Tester**:
```
Run full E2E tests on the Dashboard and report any issues
```

---

## Configuration

File: `.claude/settings.local.json`

The agents use the **MCP Playwright server** which provides browser automation tools.

### MCP Server
- **Package**: `@ejazullah/mcp-playwright@latest`
- **Command**: `npx -y @ejazullah/mcp-playwright@latest`
- **Tools**: Navigation, interaction, inspection, waiting, extraction, CDP

---

## Troubleshooting

**Agent not in dropdown?**
- Restart VS Code/Cursor/Claude Desktop
- Check `.claude/settings.local.json` exists
- Verify MCP server installed: `npm list @ejazullah/mcp-playwright`

**Agent not working?**
- Ensure Dashboard is running on port 5173
- Ensure API is running on port 5006
- Check Playwright browsers installed: `npx playwright install`

**Selector issues?**
- Use the **Test Healer agent** to auto-fix
- Or manually try: text-based `/Trigger Analysis/i`, role-based `getByRole('button')`

---

## Next Steps

1. ✅ Agents are installed and configured
2. ⏳ **Try the agents**: Select from dropdown and give a command
3. ⏳ **Generate tests**: Ask Test Generator to create Dashboard tests
4. ⏳ **Heal failing tests**: Ask Test Healer to fix selector issues
5. ⏳ **Plan test suites**: Ask Test Planner for comprehensive coverage

---

**Last Updated**: November 23, 2025
