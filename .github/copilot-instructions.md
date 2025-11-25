# GitHub Copilot - Playwright Agents Instructions

Use these prompt prefixes in Copilot Chat to invoke specialized testing agents:

## @workspace /playwright-test-generator
Generate Playwright test scripts from user interactions.

**Instructions:**
- Create E2E tests for the DDN Dashboard (http://localhost:5173)
- Generate Playwright test code with flexible selectors (text-based, role-based)
- Include assertions and proper waits
- Save to tests/ui/generated/
- Dashboard API: http://localhost:5006
- Main button text: 'Trigger Analysis'

**Usage:** `@workspace /playwright-test-generator Generate a test for the Trigger Analysis button`

---

## @workspace /playwright-test-healer
Repair failing Playwright tests by fixing selector issues.

**Instructions:**
- Analyze test errors and failed selectors
- Try alternatives: CSS fallback, XPath, text-based (/Trigger Analysis/i), role-based (getByRole)
- Update test files with working selectors
- Document all fixes
- Max 3 retry attempts

**Usage:** `@workspace /playwright-test-healer Fix the failing test in manual_analyze.spec.ts`

---

## @workspace /playwright-test-planner
Create test plans in Gherkin format.

**Instructions:**
- Analyze Dashboard UI structure
- Create Gherkin plans (Given/When/Then)
- Include: happy path, edge cases, error handling, accessibility
- Save to tests/ui/plans/
- Add priority and time estimates

**Usage:** `@workspace /playwright-test-planner Create a test plan for manual analysis feature`

---

## @workspace /qa-dashboard-tester
Run specialized Dashboard E2E tests.

**Instructions:**
- Test Dashboard features: Manual Analysis button, Failure list, Service status, Analytics
- Verify API health: http://localhost:5006/api/health
- Check UI responsiveness and error handling
- Use Playwright headed mode
- Report issues with screenshots

**Usage:** `@workspace /qa-dashboard-tester Test the Trigger Analysis workflow end-to-end`

---

## Quick Commands for Copilot Chat

Copy and paste these into Copilot Chat:

```
@workspace I need to generate a Playwright test for the Dashboard. Act as a test generator: analyze the UI at http://localhost:5173, create test code with flexible selectors, include assertions and waits, save to tests/ui/generated/. The main button is 'Trigger Analysis'.
```

```
@workspace I need to fix a failing Playwright test. Act as a test healer: analyze the error, try CSS/XPath/text/role-based selector alternatives, update the test file, document the fix. Max 3 attempts.
```

```
@workspace I need a test plan. Act as a test planner: create a Gherkin format plan with happy path, edge cases, error handling, and accessibility scenarios. Save to tests/ui/plans/.
```

```
@workspace I need to test the Dashboard. Act as a QA tester: test Manual Analysis (button: 'Trigger Analysis'), Failure list, Service status, Analytics. Verify API at http://localhost:5006/api/health. Use Playwright headed mode.
```
