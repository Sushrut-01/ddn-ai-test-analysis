# 🚀 Run Your First Guruttava Test - Step by Step

**Status**: ✅ Guruttava job is now visible in Jenkins!
**Next**: Run the first test build and verify end-to-end flow

---

## 🎯 Step 1: Access the Guruttava Job

### Option A: From Jenkins Dashboard
```
1. Open: http://localhost:8081/
2. Look for: "Guruttava-E2E-Tests" in the job list
3. Click on it
```

### Option B: Direct URL
```
http://localhost:8081/job/Guruttava-E2E-Tests/
```

---

## 🎯 Step 2: Trigger First Build

### On the Job Page:

1. Click **"Build with Parameters"** (left sidebar)

2. You'll see these parameters:

   **PLATFORM**: Select **Android** (start with one platform)

   **TEST_TYPE**: Select **Smoke** (quick test)

   **SEND_NOTIFICATIONS**: ✓ (keep checked)

3. Click **"Build"** button

---

## 🎯 Step 3: Monitor the Build

### Watch Real-Time Execution:

1. You'll see **"Build #1"** appear under "Build History"
2. Click on **#1**
3. Click **"Console Output"** (left sidebar)
4. Watch the live log

### Expected Console Output:

```bash
=========================================
Guruttava E2E Tests (Robot Framework)
Build: 1
Job: Guruttava-E2E-Tests
Platform: Android
Test Type: Smoke
=========================================
Project ID: 2 | Slug: guruttava           ← CRITICAL: Verify this!
Checking out code from https://github.com/Sushrut-01/gurutattva-e2e-automation (branch: Sushrut-laptop)...
Git Branch: Sushrut-laptop | Commit: <hash>
Installing Robot Framework and dependencies...
Running Android tests from: tests/mobile/android/
Test Type: Smoke
Executing Robot Framework tests...
Parsing test results and uploading to platform...
Triggering AI analysis for failures...
=========================================
Guruttava Tests completed!
Platform: Android
Results uploaded to project_id: 2      ← CRITICAL: Verify this!
=========================================
```

### Key Things to Check in Console:

✅ **Project ID: 2** (NOT 1 - that's DDN)
✅ **Project Slug: guruttava** (NOT ddn)
✅ **Branch: Sushrut-laptop** (where the tests are)
✅ **MongoDB upload successful**
✅ **AI analysis triggered**

---

## 🎯 Step 4: Verify End-to-End Data Flow

### A. Check MongoDB (Guruttava Collection)

**Open MongoDB Compass or mongosh:**

Connection String:
```
mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests
```

**Query Guruttava Test Failures:**

```javascript
// Database: ddn_tests
// Collection: guruttava_test_failures

// Find recent Guruttava failures
db.guruttava_test_failures.find({
  project_id: 2
}).sort({
  timestamp: -1
}).limit(5)

// Expected: New documents from the Jenkins build
// Each should have:
// - project_id: 2
// - project_slug: "guruttava"
// - test_name: (from Robot Framework)
// - error_message: (if tests failed)
// - timestamp: (recent)
```

**Verify No Data Mixing:**

```javascript
// Check DDN collection - should have NO new data
db.ddn_test_failures.find({
  project_id: 1
}).sort({
  timestamp: -1
}).limit(5)

// These should be OLDER than the Guruttava build
```

---

### B. Check PostgreSQL (Failure Analysis)

**Connect to PostgreSQL:**

```bash
docker exec -it ddn-postgres psql -U ddn_user -d ddn_db
```

**Query Guruttava Failures:**

```sql
-- Find Guruttava failures (project_id = 2)
SELECT
    id,
    test_name,
    project_id,
    error_category,
    severity,
    created_at
FROM failure_analysis
WHERE project_id = 2
ORDER BY created_at DESC
LIMIT 10;

-- Expected: New entries with project_id = 2
```

**Check Project Counts:**

```sql
-- Count failures by project
SELECT
    project_id,
    COUNT(*) as failure_count,
    MAX(created_at) as latest_failure
FROM failure_analysis
GROUP BY project_id;

-- Expected output:
-- project_id | failure_count | latest_failure
-- 1          | X             | <older timestamp> (DDN)
-- 2          | Y             | <recent timestamp> (Guruttava - just now!)
```

**Verify No Cross-Contamination:**

```sql
-- This should return 0 rows
SELECT * FROM failure_analysis
WHERE project_id NOT IN (1, 2);
```

---

### C. Check Dashboard (Frontend)

**Open Dashboard:**

```
http://localhost:5173/
```

**Test Steps:**

1. **Look for Project Selector** (usually top-right corner)
   - You should see dropdown with: "DDN Project" and "Guruttava"

2. **Select "Guruttava"**
   - Dashboard should refresh

3. **Navigate to "Failures" page**
   - You should see new test failures from the Jenkins build
   - Check the timestamps - should be very recent

4. **Click on a failure** to view details
   - Check "AI Analysis" tab
   - Should show:
     - Error Category (CODE_ERROR, CONFIG_ERROR, etc.)
     - Root Cause Analysis
     - Recommended Fixes
     - Similar Errors
     - Confidence Score

5. **Switch to "DDN Project"**
   - Failures should be DIFFERENT (older DDN failures)
   - NO Guruttava failures should appear here

6. **Switch back to "Guruttava"**
   - Same failures as step 3 (confirms proper filtering)

---

### D. Check Jira Integration (If Configured)

**Check Jira GURU Project:**

1. Open your Jira instance
2. Go to **GURU** project (Guruttava's Jira project)
3. Look for new issues created in the last few minutes
4. Verify:
   - Issues created from test failures
   - Correct project assignment (GURU, not DDN)
   - Issue description contains:
     - Test name
     - Error message
     - AI-generated fix recommendations
     - Link to Jenkins build

**Check Jira DDN Project:**

1. Go to **DDN** project
2. Verify: NO new issues from the Guruttava build
3. Confirm: Only older DDN-related issues

---

## 🎯 Step 5: Verify Multi-Project Isolation

### Isolation Checklist:

```
✓ MongoDB:
  - guruttava_test_failures has project_id=2 data
  - ddn_test_failures has NO new data
  - Collections are separate

✓ PostgreSQL:
  - failure_analysis table has entries with project_id=2
  - No project_id=1 entries from Guruttava build
  - Proper WHERE filtering by project_id

✓ Dashboard:
  - Project selector switches between DDN and Guruttava
  - Each project shows ONLY its own failures
  - No data mixing when switching

✓ Jira:
  - GURU project has Guruttava tickets
  - DDN project has NO Guruttava tickets
  - Proper project key assignment
```

---

## 🎯 Step 6: Check AI Analysis

### Manual Trigger (Optional):

If AI analysis didn't run automatically during build:

```bash
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 2,
    "project_slug": "guruttava"
  }'
```

### Check LangGraph Service:

```bash
# View AI service logs
docker logs ddn-langgraph --tail 50

# Look for:
# - Guruttava failures being processed
# - Classifier categorizing errors
# - Root cause analysis generated
```

### Verify in Dashboard:

1. Refresh the failures page
2. Click on a failure
3. Go to "AI Analysis" tab
4. Should show:
   - Error category
   - Root cause
   - Recommended fixes
   - Similar errors
   - Prevention strategies

---

## 📊 Success Criteria - All Must Pass

### Build Execution:
- [ ] Build completed (success/unstable/failure - any is fine for first run)
- [ ] Console shows PROJECT_ID=2
- [ ] Console shows PROJECT_SLUG=guruttava
- [ ] Git clone from Sushrut-laptop branch succeeded
- [ ] Robot Framework tests executed

### Data Storage:
- [ ] MongoDB guruttava_test_failures has new documents
- [ ] MongoDB ddn_test_failures has NO new documents
- [ ] PostgreSQL has failures with project_id=2
- [ ] PostgreSQL has NO failures with project_id=1 from this build

### Dashboard:
- [ ] Guruttava project shows new failures
- [ ] DDN project shows NO new failures
- [ ] Project switching works correctly
- [ ] No data mixing observed

### AI Analysis:
- [ ] AI analysis completed (check logs or dashboard)
- [ ] Error categories assigned
- [ ] Fix recommendations generated

### Integration:
- [ ] Jira tickets in GURU project (if configured)
- [ ] No Jenkins errors in console
- [ ] All services healthy (docker ps)

---

## 🐛 Troubleshooting

### Build Fails with "Git clone failed"

**Check:**
```bash
# Test Git access
git clone -b Sushrut-laptop https://github.com/Sushrut-01/gurutattva-e2e-automation /tmp/test

# Verify branch exists
curl -I https://raw.githubusercontent.com/Sushrut-01/gurutattva-e2e-automation/Sushrut-laptop/README.md
```

### No Data in MongoDB

**Cause**: Parser might not have executed or MongoDB connection failed

**Check Console Output For:**
- "Parsing test results and uploading to platform..."
- Any MongoDB connection errors
- robot_framework_parser.py execution

**Verify Parser Exists:**
```bash
# Check if parser is in the repo
curl -s https://raw.githubusercontent.com/Sushrut-01/gurutattva-e2e-automation/Sushrut-laptop/implementation/robot_framework_parser.py | head -20
```

### Dashboard Shows No Failures

**Possible Causes:**
1. Frontend not filtering by project_id correctly
2. localStorage has wrong project selected
3. API not returning data

**Check in Browser Console:**
```javascript
// Check selected project
console.log(localStorage.getItem('selected_project_id'));
// Should be "2" for Guruttava

// Fix if needed
localStorage.setItem('selected_project_id', '2');
location.reload();
```

### Wrong PROJECT_ID in Console

**If console shows PROJECT_ID=1 instead of 2:**

This is a critical issue! The shell script has PROJECT_ID hardcoded.

**Fix:**
1. Go to job configuration
2. Find the "Execute shell" section
3. Verify line says: `export PROJECT_ID="2"`
4. If it says "1", change to "2"
5. Save and rebuild

---

## 🎉 Next Steps After Successful Build

### 1. Test Other Platforms

Run builds with:
- **iOS** platform (if you have iOS tests)
- **Web** platform (if you have web tests)
- **All** platform (runs all test suites)

### 2. Test Different Test Types

Run builds with:
- **Regression** tests
- **Sanity** tests
- **All** tests

### 3. Run Parallel Builds

**Test isolation by running both projects simultaneously:**

1. Trigger DDN-Basic-Tests
2. Immediately trigger Guruttava-E2E-Tests
3. Verify both complete without interference
4. Check data isolation after both finish

### 4. Set Up Scheduled Builds

Configure automatic builds:
- Nightly regression: `0 2 * * *`
- Every 6 hours: `H */6 * * *`
- Hourly smoke tests: `H * * * *`

### 5. Configure Notifications

Set up:
- Slack/Teams notifications on failures
- Email alerts for critical errors
- Build status badges

---

## 📚 Documentation

After successful E2E testing, document:
- Build numbers and results
- Any issues encountered
- Performance metrics (build duration)
- Test coverage statistics
- Data isolation verification results

---

## ✅ Quick Reference

**Jenkins Job**: http://localhost:8081/job/Guruttava-E2E-Tests/

**Build URL**: http://localhost:8081/job/Guruttava-E2E-Tests/build?delay=0sec

**Dashboard**: http://localhost:5173/

**MongoDB**: mongodb+srv://sushrutnistane097_db_user:...

**PostgreSQL**: docker exec -it ddn-postgres psql -U ddn_user -d ddn_db

---

**Ready to run the first test!** 🚀

Just click "Build with Parameters" and watch the magic happen!
