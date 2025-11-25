# Jenkins Setup Instructions - Complete Real-Time Flow

## 🚀 Quick Setup (3 Minutes)

### Step 1: Copy the Unified Build Script
```powershell
# Open the file
notepad C:\DDN-AI-Project-Documentation\JENKINS-UNIFIED-BUILD-SCRIPT.bat

# Select All (Ctrl+A) and Copy (Ctrl+C)
```

### Step 2: Configure Jenkins Job
1. Open Jenkins: **http://localhost:8081**
2. Click on **"DDN-Nightly-Tests"** job
3. Click **"Configure"** (left sidebar)
4. Scroll to **"Build Steps"** section
5. **DELETE** existing build step (old Mocha-only script)
6. Click **"Add build step"** → **"Execute Windows batch command"**
7. **Paste** the unified script (Ctrl+V)
8. Click **"Save"** (bottom of page)

### Step 3: Trigger Build #27
1. Click **"Build Now"** (left sidebar)
2. Watch build progress
3. Click on **#27** to see console output

---

## ✅ What This Unified Script Does

### BOTH Test Frameworks Run:

**1. Robot Framework Tests** (Basic/Functional)
- ✅ Runs from `robot-tests/` folder
- ✅ Uses `mongodb_robot_listener.py`
- ✅ Reports failures to MongoDB with suite metadata
- ✅ Generates HTML reports in `robot-results/`

**2. Mocha/JavaScript Tests** (Advanced/Integration)
- ✅ Runs from `tests/ddn-advanced-scenarios.js`
- ✅ Uses `mongodb-reporter.js`
- ✅ All 25 reportFailure() calls have suite metadata
- ✅ Reports failures to MongoDB

---

## 📊 Real-Time Flow After Build #27 Runs

```
Jenkins Build #27 Triggered
         ↓
┌────────────────────────────────┐
│  STEP 1: Set Environment       │
│  - MONGODB_URI                 │
│  - JOB_NAME, BUILD_NUMBER      │
│  - GIT_COMMIT, GIT_BRANCH      │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  STEP 2: Install Python Deps   │
│  - robotframework              │
│  - pymongo                     │
│  - python-dotenv               │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  STEP 3: Install Node.js Deps  │
│  - cd tests                    │
│  - npm install                 │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  STEP 4: Run Robot Framework   │
│  robot --listener              │
│  mongodb_robot_listener.py     │
└────────────────────────────────┘
         ↓
    Test Failures?
         ↓
┌────────────────────────────────┐
│  mongodb_robot_listener.py     │
│  Captures failure and sends:   │
│  - suite_name (from .robot)    │
│  - pass_count, fail_count      │
│  - total_count                 │
│  - job_name, build_id          │
└────────────────────────────────┘
         ↓
    MongoDB Atlas
    test_failures collection
         ↓
┌────────────────────────────────┐
│  STEP 5: Run Mocha Tests       │
│  cd tests                      │
│  npm test                      │
└────────────────────────────────┘
         ↓
    Test Failures?
         ↓
┌────────────────────────────────┐
│  reportFailure() called        │
│  mongodb-reporter.js sends:    │
│  - suite_name (hardcoded)      │
│  - pass_count: 0               │
│  - fail_count: 1               │
│  - total_count: 1              │
└────────────────────────────────┘
         ↓
    MongoDB Atlas
    test_failures collection
         ↓
┌────────────────────────────────┐
│  Dashboard API queries MongoDB │
│  http://localhost:5006         │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  Dashboard UI shows failures   │
│  http://localhost:5173         │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  Aging Service detects         │
│  failures > 3 days old         │
│  http://localhost:5007         │
└────────────────────────────────┘
         ↓
┌────────────────────────────────┐
│  AI Analysis Service           │
│  analyzes failures             │
│  http://localhost:5000         │
└────────────────────────────────┘
         ↓
    Results stored in PostgreSQL
    failure_analysis table
         ↓
    Dashboard shows AI insights!
```

---

## 🔍 Expected Build #27 Console Output

```
=========================================
DDN UNIFIED TEST SUITE
Build Number: 27
Job Name: DDN-Nightly-Tests
Git Branch: feature/qa-agent
Git Commit: a1b2c3d4...
=========================================

[STEP 1/5] Setting environment variables...
   MongoDB: ddn-cluster.wudcfln.mongodb.net
   Database: ddn_tests
   Collection: test_failures
   Build ID: DDN-Nightly-Tests-27

[STEP 2/5] Installing Python dependencies...
   Python dependencies installed successfully

[STEP 3/5] Installing Node.js dependencies...
   Node.js dependencies installed successfully

[STEP 4/5] Running Robot Framework Tests...
=========================================
Running: robot --outputdir robot-results --listener implementation\mongodb_robot_listener.py robot-tests\
==============================================================================
Basic DDN Tests :: Basic functionality tests for DDN Storage
==============================================================================
Test Basic Functionality                                             | PASS |
------------------------------------------------------------------------------
Test Domain Creation                                                 | FAIL |
Error message here...
------------------------------------------------------------------------------
Basic DDN Tests :: Basic functionality tests for DDN Storage | FAIL |
2 tests, 1 passed, 1 failed
==============================================================================

✓ MongoDB Reporter: Connected to database
✓ Failure saved to MongoDB (ID: 674...)

Robot Framework Tests Status:
   Result: SOME TESTS FAILED (Exit Code: 1)
   Failures have been reported to MongoDB

[STEP 5/5] Running Mocha/JavaScript Tests...
=========================================
Running: npm test

  Domain-Based Isolation and Management Tests
    ✓ should create separate domains for different tenants
    ✗ should enforce domain isolation - prevent cross-domain access
      Error: Expected 403/401, got: 500
      ✓ Failure saved to MongoDB (ID: 674...)

  2 passing (2s)
  1 failing

Mocha Tests Status:
   Result: SOME TESTS FAILED (Exit Code: 1)
   Failures have been reported to MongoDB

=========================================
BUILD SUMMARY - Build #27
=========================================

Test Results:
   Robot Framework: 1 (0 = pass)
   Mocha Tests: 1 (0 = pass)

MongoDB Reporting:
   URI: mongodb+srv://ddn-cluster.wudcfln.mongodb.net
   Database: ddn_tests
   Collection: test_failures
   Build ID: DDN-Nightly-Tests-27

Next Steps:
   1. Check Dashboard: http://localhost:5173/failures
   2. Filter by Build ID: DDN-Nightly-Tests-27
   3. View AI Analysis: http://localhost:5173/analytics

Overall Result: BUILD FAILED (Robot Framework failures)
```

---

## 🧪 Verify Build #27 Worked

### 1. Check MongoDB Has Failures
```powershell
# Run this to check MongoDB
python check_mongodb.py
```

**Expected output:**
```
Checking MongoDB for Build #27 failures...
Found 2 failures:
  1. Robot Framework: Test Domain Creation
     Suite: Basic DDN Tests
     Build ID: DDN-Nightly-Tests-27
  2. Mocha: should enforce domain isolation
     Suite: Domain-Based Isolation and Management Tests
     Build ID: DDN-Nightly-Tests-27

✓ All failures have suite_name
✓ All failures have pass_count, fail_count, total_count
```

### 2. Check Dashboard
```
http://localhost:5173/failures
```

**You should see:**
- 2 new failures from Build #27
- Both have suite metadata
- Can click "View Details" on each

### 3. Verify Suite Metadata
Each failure should have:
```javascript
{
  suite_name: "Basic DDN Tests" OR "Domain-Based Isolation...",
  pass_count: 1,     // Or 0
  fail_count: 1,
  total_count: 2,    // Or 1
  job_name: "DDN-Nightly-Tests",
  build_id: "DDN-Nightly-Tests-27",
  build_url: "http://localhost:8081/job/DDN-Nightly-Tests/27/"
}
```

---

## ✅ Success Criteria

Build #27 is successful if:

- ✅ Jenkins runs both Robot Framework AND Mocha tests
- ✅ Console shows "Running Robot Framework Tests..."
- ✅ Console shows "Running Mocha/JavaScript Tests..."
- ✅ Failures appear in MongoDB `test_failures` collection
- ✅ All failures have `suite_name` field
- ✅ All failures have `pass_count`, `fail_count`, `total_count`
- ✅ Dashboard shows failures from both frameworks
- ✅ Build ID format: `DDN-Nightly-Tests-27`

---

## 🐛 Troubleshooting

### Issue: "npm: command not found"
**Solution:** Node.js not installed on Jenkins server
```powershell
# Install Node.js on Jenkins machine
# Or comment out Mocha test section in script
```

### Issue: "No module named 'robotframework'"
**Solution:** Python dependencies not installing
```batch
# Check Python is in PATH
python --version

# Manually install
pip install robotframework pymongo python-dotenv
```

### Issue: "MongoDB connection failed"
**Solution:** Check MONGODB_URI is correct
```batch
# Test connection
python -c "from pymongo import MongoClient; MongoClient('mongodb+srv://...').server_info(); print('Connected!')"
```

### Issue: No failures in MongoDB
**Solution:** Check environment variables are set
```batch
# In Jenkins script, verify these are set:
echo MONGODB_URI: %MONGODB_URI%
echo JOB_NAME: %JOB_NAME%
echo BUILD_NUMBER: %BUILD_NUMBER%
```

---

## 📚 Additional Files

- **JENKINS-UNIFIED-BUILD-SCRIPT.bat** - The complete script
- **COPY-THIS-TO-JENKINS.bat** - Old Robot-only script (replaced)
- **WHY-TWO-TEST-FRAMEWORKS.md** - Architecture explanation
- **DASHBOARD-BUGS-FIXED.md** - Bug fixes applied
- **BUG4-COMPLETE-FIX-SUMMARY.md** - Suite metadata fix details

---

## 🎯 Next Steps After Build #27

1. ✅ Verify failures appear in Dashboard
2. ✅ Wait 3 days for aging service to trigger AI analysis
3. ✅ Or manually trigger: `curl -X POST http://localhost:5007/trigger-now`
4. ✅ Check AI analysis results in Dashboard
5. ✅ Start using system for real test failures!

---

**Status:** 🟢 **Ready to Run Build #27!**

Copy the script to Jenkins and click "Build Now"!
