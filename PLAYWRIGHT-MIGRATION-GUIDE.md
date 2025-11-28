# Playwright Tests Migration Guide

**Date:** November 25, 2025  
**Status:** Migration Required

## Summary

Playwright tests were mistakenly created in the main project repo (`ddn-ai-test-analysis`). They have been partially cleaned up and need to be consolidated into the dedicated Playwright repo (`ddn-playwright-automation`).

## What Was Removed from Main Repo

✅ **Removed (causing CI failures):**
- `e2e/` folder - Example/scaffold tests pointing to playwright.dev
- Root `playwright.config.ts` - Configuration pointing to e2e
- `.github/workflows/playwright.yml` - GitHub Actions workflow

✅ **Relocated:**
- `tests/ui/*.js` monitoring scripts → `scripts/monitoring/`

## What Remains in Main Repo (Needs Migration)

The following files in `tests/ui/` should be moved to `ddn-playwright-automation`:

### 1. Test Files
- `tests/ui/manual_analyze.spec.ts` - Dashboard "Analyze Now" test
- `tests/ui/tests/manual-analyze.spec.ts` - Next.js variant test

### 2. Configuration & Helpers
- `tests/ui/playwright.config.ts` - Working Playwright config
- `tests/ui/helpers/dashboard-helpers.ts` - API utility functions
- `tests/ui/package.json` - Dependencies
- `tests/ui/package-lock.json` - Lock file

### 3. Documentation
- `tests/ui/MCP-PLAYWRIGHT-AGENTS.md` - MCP Playwright agents guide
- `tests/ui/README.md` - Basic documentation

### 4. Artifacts (Optional)
- `tests/ui/*.png` - Test screenshots
- `tests/ui/test-results/` - Test run artifacts

## Migration Steps

### Step 1: Copy to ddn-playwright-automation Repo

```powershell
# Navigate to ddn-playwright-automation repo
cd path\to\ddn-playwright-automation

# Copy test files
Copy-Item C:\DDN-AI-Project-Documentation\tests\ui\manual_analyze.spec.ts tests\
Copy-Item C:\DDN-AI-Project-Documentation\tests\ui\tests\manual-analyze.spec.ts tests\

# Copy helpers
New-Item -ItemType Directory -Path helpers -Force
Copy-Item C:\DDN-AI-Project-Documentation\tests\ui\helpers\*.ts helpers\

# Copy documentation
Copy-Item C:\DDN-AI-Project-Documentation\tests\ui\MCP-PLAYWRIGHT-AGENTS.md docs\
Copy-Item C:\DDN-AI-Project-Documentation\tests\ui\README.md docs\ui-tests-README.md

# Merge configurations if needed
# Review tests/ui/playwright.config.ts and merge settings into your config
```

### Step 2: Update Imports in Migrated Tests

After copying, update import paths in test files:

```typescript
// Old (main repo)
import { getApi } from './helpers/dashboard-helpers';

// New (playwright repo - adjust as needed)
import { getApi } from '../helpers/dashboard-helpers';
```

### Step 3: Install Dependencies in Playwright Repo

```powershell
cd ddn-playwright-automation
npm install
npx playwright install
```

### Step 4: Test in Playwright Repo

```powershell
# Run the migrated test
npx playwright test manual_analyze.spec.ts

# Ensure Dashboard is running
# Dashboard UI: http://localhost:5173
# Dashboard API: http://localhost:5006
```

### Step 5: Clean Up Main Repo

After successful migration and testing:

```powershell
# Back in main repo
cd C:\DDN-AI-Project-Documentation

# Remove the entire tests/ui folder (except node_modules if you want to keep)
Remove-Item -Path "tests\ui" -Recurse -Force -Exclude node_modules
```

## Monitoring Scripts

Operational monitoring scripts have been moved to `scripts/monitoring/`:
- `monitor.js` - Dashboard monitoring
- `monitor-jenkins.js` - Jenkins integration monitoring
- `debug-*.js` - Various debugging utilities
- `data-flow-investigation.js` - Analysis tools
- `complete-validation.js`, `comprehensive-audit.js` - Validation scripts

These are NOT tests, they are runtime utilities and should remain in the main repo.

## Verification

After migration:
1. ✅ Main repo has no Playwright test failures in CI
2. ✅ `ddn-playwright-automation` repo runs all tests successfully
3. ✅ Monitoring scripts still work from `scripts/monitoring/`
4. ✅ No duplicate code between repos

## Next Steps

1. Complete the migration following steps above
2. Update `ddn-playwright-automation` README with new test locations
3. Add CI workflow in Playwright repo if not already present
4. Archive old `tests/ui/` in main repo once verified

---

**Note:** This cleanup was performed to stop failing CI builds caused by example Playwright tests running against external sites. Real Dashboard tests are preserved and should be moved to the dedicated testing repo.

---

**Note:** This is a test repo. Please do NOT use this repo for production or any other purpose.
