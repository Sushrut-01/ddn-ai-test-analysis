# 🔧 Jenkins Fix & End-to-End Testing Guide

**Date**: January 17, 2026
**Purpose**: Fix Jenkins job configurations and perform complete E2E testing

---

## 🚨 Issues Found

### Issue 1: DDN Jenkinsfile Missing from GitHub
- **Status**: ❌ Jenkinsfile NOT in https://github.com/Sushrut-01/ddn-jenkins-testing/main
- **Impact**: DDN-Tests job cannot execute
- **Fix Required**: Push Jenkinsfile to repository

### Issue 2: Guruttava Job Points to Wrong Branch
- **Current Config**: Points to `*/main` branch
- **Actual Location**: Jenkinsfile is in `*/Sushrut-laptop` branch
- **Status**: ✅ FIXED - Updated to use Sushrut-laptop branch
- **Action**: Jenkins restarted to apply changes

---

## ✅ Step 1: Fix DDN Jenkinsfile (REQUIRED)

### Option A: Push Jenkinsfile to GitHub (Recommended)

```bash
# Navigate to your DDN testing repository
cd /path/to/ddn-jenkins-testing

# Copy Jenkinsfile from this documentation repo
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/DDN-Jenkinsfile ./Jenkinsfile

# Verify the file
ls -la Jenkinsfile

# Add and commit
git add Jenkinsfile
git commit -m "feat: add multi-project Jenkins pipeline (PROJECT_ID=1)"

# Push to GitHub
git push origin main
```

### Option B: Update Jenkins Job to Use Different Repo/Branch
If you prefer not to modify the main repo, create a new branch:

```bash
cd /path/to/ddn-jenkins-testing
git checkout -b jenkins-pipeline
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/DDN-Jenkinsfile ./Jenkinsfile
git add Jenkinsfile
git commit -m "feat: add Jenkins pipeline"
git push origin jenkins-pipeline
```

Then update Jenkins job to use `*/jenkins-pipeline` branch.

---

## ✅ Step 2: Verify Guruttava Job Fix

The Guruttava job has been updated to use the correct branch. Verify it works:

1. **Open Jenkins**: http://localhost:8081/
2. **Navigate to**: Guruttava-E2E-Tests job
3. **Click**: "Configure"
4. **Verify**:
   - Repository URL: `https://github.com/Sushrut-01/gurutattva-e2e-automation`
   - Branch: `*/Sushrut-laptop` ✅
   - Script Path: `Jenkinsfile` ✅

---

## 🧪 Step 3: End-to-End Testing Plan

### Test 1: Guruttava Job Execution

#### 3.1 Trigger Guruttava Job
```
1. Go to: http://localhost:8081/job/Guruttava-E2E-Tests/
2. Click: "Build with Parameters"
3. Select:
   - PLATFORM: Android (start with one platform)
   - TEST_TYPE: Smoke
   - DEVICE_NAME: emulator-5554
   - APP_PATH: apps/guruttava.apk
4. Click: "Build"
```

#### 3.2 Monitor Execution
```
1. Click on build number (e.g., #1)
2. Click "Console Output"
3. Watch for:
   ✓ Git checkout from Sushrut-laptop branch
   ✓ Python setup
   ✓ Robot Framework installation
   ✓ Appium connection check
   ✓ Test execution
   ✓ Results upload to platform
```

#### 3.3 Verify Data Flow

**A. Check MongoDB**
```bash
# Use MongoDB Compass or mongosh
mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests

# Check collection: guruttava_test_failures
# Should see new entries with project_id: 2
```

**B. Check PostgreSQL**
```bash
# Connect to PostgreSQL
docker exec -it ddn-postgres psql -U ddn_user -d ddn_db

# Query failures for Guruttava
SELECT id, test_name, project_id, error_category, created_at
FROM failure_analysis
WHERE project_id = 2
ORDER BY created_at DESC
LIMIT 10;
```

**C. Check Dashboard**
```
1. Open: http://localhost:5173/
2. Select: "Guruttava" project from dropdown
3. Navigate to: Failures page
4. Verify: New failures appear
5. Check: AI analysis is available
6. Confirm: No DDN data is mixed in
```

**D. Check Jira**
```
1. Open your Jira instance
2. Go to: GURU project
3. Verify: New tickets created from failures
4. Check: Ticket details match test failures
```

---

### Test 2: DDN Job Execution (After Fixing Jenkinsfile)

#### 3.4 Trigger DDN Job
```
1. Go to: http://localhost:8081/job/DDN-Tests/
2. Click: "Build with Parameters"
3. Select:
   - TEST_TYPE: Smoke
   - TEST_SUITE: Basic
   - SEND_NOTIFICATIONS: true
   - RUN_PERFORMANCE_TESTS: false
4. Click: "Build"
```

#### 3.5 Monitor Execution
```
1. Click on build number
2. Click "Console Output"
3. Watch for:
   ✓ Git checkout from main branch
   ✓ Selenium Hub connection
   ✓ Test execution
   ✓ Results processing
   ✓ Upload to platform with PROJECT_ID=1
```

#### 3.6 Verify Data Flow

**A. Check MongoDB**
```
# Collection: ddn_test_failures
# Should see entries with project_id: 1
```

**B. Check PostgreSQL**
```sql
-- Query failures for DDN
SELECT id, test_name, project_id, error_category, created_at
FROM failure_analysis
WHERE project_id = 1
ORDER BY created_at DESC
LIMIT 10;
```

**C. Check Dashboard**
```
1. Open: http://localhost:5173/
2. Select: "DDN Project" from dropdown
3. Navigate to: Failures page
4. Verify: New failures appear
5. Check: AI analysis is available
6. Confirm: No Guruttava data is mixed in
```

**D. Check Jira**
```
1. Go to: DDN project in Jira
2. Verify: New tickets created
3. Check: Correct project association
```

---

## 🔍 Test 3: Multi-Project Isolation Verification

### 3.7 Verify Data Isolation

**PostgreSQL Isolation Check**
```sql
-- Count failures by project
SELECT project_id, COUNT(*) as failure_count
FROM failure_analysis
GROUP BY project_id;

-- Should see:
-- project_id | failure_count
-- 1          | X (DDN)
-- 2          | Y (Guruttava)

-- Verify no cross-contamination
SELECT * FROM failure_analysis
WHERE project_id NOT IN (1, 2);
-- Should return 0 rows
```

**MongoDB Isolation Check**
```javascript
// Check DDN collection
db.ddn_test_failures.find({}).forEach(doc => {
  if (doc.project_id !== 1) {
    print("ERROR: Wrong project_id in DDN collection");
  }
});

// Check Guruttava collection
db.guruttava_test_failures.find({}).forEach(doc => {
  if (doc.project_id !== 2) {
    print("ERROR: Wrong project_id in Guruttava collection");
  }
});
```

**Dashboard Isolation Check**
```
1. Select "DDN Project"
2. Note the failure IDs displayed
3. Switch to "Guruttava"
4. Verify: Completely different set of failures
5. Switch back to "DDN Project"
6. Verify: Same failures as step 2 (no mixing)
```

---

## 🧪 Test 4: AI Service Integration

### 3.8 Trigger AI Analysis

**Manual Trigger API**
```bash
# Test AI analysis for a specific failure
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 2,
    "project_slug": "guruttava"
  }'
```

**Check LangGraph Service**
```bash
# Verify LangGraph is running
curl http://localhost:5000/health

# Should return: {"status": "healthy"}
```

**Verify AI Results in Dashboard**
```
1. Open failure details in dashboard
2. Check "AI Analysis" section
3. Verify:
   ✓ Error category (CODE_ERROR, CONFIG_ERROR, etc.)
   ✓ Root cause analysis
   ✓ Recommended fixes
   ✓ Similar errors
   ✓ Confidence score
```

---

## 🧪 Test 5: GitHub PR Workflow

### 3.9 Test PR Creation

```bash
# Create a test PR using the API
curl -X POST http://localhost:5006/api/github/create-pr \
  -H "Content-Type: application/json" \
  -d '{
    "failure_id": 123,
    "project_id": 1
  }'
```

**Verify in GitHub**
```
1. Go to: https://github.com/Sushrut-01/ddn-test-data/pulls
2. Check: New PR created
3. Verify: PR contains fix recommendation
4. Check: PR references failure ID
```

---

## 🧪 Test 6: Complete End-to-End Flow

### 3.10 Full Flow Test (DDN)

```
Jenkins DDN-Tests Build
  ↓
Robot Framework Tests Execute
  ↓
output.xml Generated
  ↓
robot_framework_parser.py (--project-id 1)
  ↓
MongoDB: ddn_test_failures (project_id: 1)
  ↓
POST /api/trigger-analysis (project_id: 1, project_slug: "ddn")
  ↓
LangGraph AI Classifier (analyzes error)
  ↓
POST /api/analysis/store (project_id: 1)
  ↓
PostgreSQL: failure_analysis (project_id: 1)
  ↓
Jira Ticket Created (DDN project)
  ↓
Dashboard: GET /api/failures?project_id=1
  ↓
Frontend Display (DDN project view)
```

### 3.11 Full Flow Test (Guruttava)

```
Jenkins Guruttava-E2E-Tests Build
  ↓
Robot Framework Tests Execute (Android/iOS/Web)
  ↓
output.xml Generated
  ↓
robot_framework_parser.py (--project-id 2)
  ↓
MongoDB: guruttava_test_failures (project_id: 2)
  ↓
POST /api/trigger-analysis (project_id: 2, project_slug: "guruttava")
  ↓
LangGraph AI Classifier
  ↓
POST /api/analysis/store (project_id: 2)
  ↓
PostgreSQL: failure_analysis (project_id: 2)
  ↓
Jira Ticket Created (GURU project)
  ↓
Dashboard: GET /api/failures?project_id=2
  ↓
Frontend Display (Guruttava project view)
```

---

## 📊 Success Criteria

### ✅ All Tests Must Pass:

- [ ] Guruttava job executes successfully
- [ ] DDN job executes successfully (after Jenkinsfile push)
- [ ] MongoDB has correct project-specific data
- [ ] PostgreSQL has correct project_id filtering
- [ ] Dashboard shows project-specific failures only
- [ ] Jira tickets created in correct projects (DDN vs GURU)
- [ ] AI analysis generated for failures
- [ ] GitHub PR workflow works
- [ ] No cross-project data contamination
- [ ] Manual trigger API works for both projects

---

## 🐛 Troubleshooting

### Jenkins Job Fails with "Jenkinsfile not found"
**Cause**: Jenkinsfile not in GitHub repository
**Fix**: Follow Step 1 to push Jenkinsfile

### Guruttava Job Uses Wrong Branch
**Cause**: Job configured for main branch instead of Sushrut-laptop
**Fix**: Already applied - restart Jenkins if needed

### No Data in Dashboard
**Cause**: PROJECT_ID not set correctly in Jenkins
**Fix**: Check Jenkins console output for PROJECT_ID value

### Jira Tickets in Wrong Project
**Cause**: project_id not passed correctly
**Fix**: Verify Jira configuration in project_configurations table

### AI Analysis Not Generated
**Cause**: LangGraph service not accessible or MongoDB data missing
**Fix**:
```bash
# Check LangGraph
docker logs ddn-langgraph

# Check manual trigger service
docker logs ddn-manual-trigger
```

---

## 📝 Testing Checklist

Copy this checklist and mark off items as you complete testing:

```
SETUP
[ ] Jenkins is accessible (http://localhost:8081/)
[ ] All Docker containers running (docker ps)
[ ] DDN Jenkinsfile pushed to GitHub
[ ] Guruttava job branch config verified

GURUTTAVA TESTING
[ ] Guruttava job executed successfully
[ ] Console output shows correct PROJECT_ID=2
[ ] MongoDB guruttava_test_failures has new data
[ ] PostgreSQL has failures with project_id=2
[ ] Dashboard shows Guruttava failures
[ ] Jira tickets created in GURU project
[ ] AI analysis generated

DDN TESTING
[ ] DDN job executed successfully
[ ] Console output shows correct PROJECT_ID=1
[ ] MongoDB ddn_test_failures has new data
[ ] PostgreSQL has failures with project_id=1
[ ] Dashboard shows DDN failures
[ ] Jira tickets created in DDN project
[ ] AI analysis generated

ISOLATION TESTING
[ ] No DDN data has project_id=2
[ ] No Guruttava data has project_id=1
[ ] Dashboard switch between projects shows different data
[ ] Jira tickets in correct projects
[ ] MongoDB collections have correct project_id

INTEGRATION TESTING
[ ] Manual trigger API works for both projects
[ ] GitHub PR workflow tested
[ ] AI service generates analysis
[ ] All containers healthy

DOCUMENTATION
[ ] Test results documented
[ ] Issues logged (if any)
[ ] Success metrics recorded
```

---

## 🎯 Next Steps After Testing

1. **If all tests pass**:
   - Document final configuration
   - Create user guide for running jobs
   - Set up scheduled builds

2. **If tests fail**:
   - Review console output
   - Check service logs
   - Verify configurations
   - Retry with fixes

3. **Performance tuning**:
   - Optimize database queries
   - Tune AI service parameters
   - Configure caching if needed

---

## 📚 Reference Documentation

- **PROMPT.md**: Complete project architecture
- **SKILL.md**: Troubleshooting procedures
- **JENKINS_READY.md**: Jenkins setup guide
- **FINAL_STATUS.md**: Current system status

---

**Status**: Ready to execute testing plan
**Prerequisites**: DDN Jenkinsfile must be pushed to GitHub first
**Estimated Testing Time**: 1-2 hours for complete E2E testing
**Expected Outcome**: All systems working with proper data isolation

---
