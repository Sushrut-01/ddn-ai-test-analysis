# 🎯 Create Guruttava Job Manually - Simple Approach

**Problem**: Jenkins having issues after multiple restarts
**Solution**: Create the job manually through UI (same as DDN jobs were created)
**Time**: 5 minutes once Jenkins is stable

---

## 🛑 STOP Restarting Jenkins

**Current Issue**: Too many restarts causing initialization errors
**Action**: Let Jenkins run and stabilize for 10-15 minutes without touching it

```bash
# Just wait and check periodically
curl -I http://localhost:8081/

# When you get HTTP 200 or 403, it's stable
```

---

## ✅ Once Jenkins is Stable - Create Job Manually

### Step 1: Access Jenkins
```
http://localhost:8081/
```

### Step 2: Create New Job

1. Click **"New Item"** (top left)
2. Enter name: **Guruttava-E2E-Tests**
3. Select: **"Freestyle project"**
4. Click **"OK"**

### Step 3: Configure Job

#### A. General Settings
- **Description**: `Guruttava E2E Tests - Robot Framework tests for Android, iOS, and Web with MongoDB reporting`
- **Discard old builds**:
  - ✓ Check this
  - Days to keep: 30
  - Max # of builds: 50

#### B. This project is parameterized
Click **"This project is parameterized"**

Add these parameters:

**Parameter 1: Choice Parameter**
- Name: `PLATFORM`
- Choices (one per line):
  ```
  Android
  iOS
  Web
  All
  ```
- Description: `Select platform to test`

**Parameter 2: Choice Parameter**
- Name: `TEST_TYPE`
- Choices:
  ```
  Smoke
  Regression
  Sanity
  All
  ```
- Description: `Select test type`

**Parameter 3: Boolean Parameter**
- Name: `SEND_NOTIFICATIONS`
- Default: ✓ Checked
- Description: `Send notifications to Teams/Slack on failure`

#### C. Build Triggers
- ✓ **Build periodically**
- Schedule: `H */6 * * *` (every 6 hours)

#### D. Build Environment
(Leave empty for now)

#### E. Build - Execute Shell

Click **"Add build step" → "Execute shell"**

Paste this script:

```bash
#!/bin/bash
echo "========================================="
echo "Guruttava E2E Tests (Robot Framework)"
echo "Build: $BUILD_NUMBER"
echo "Job: $JOB_NAME"
echo "Platform: $PLATFORM"
echo "Test Type: $TEST_TYPE"
echo "========================================="

# Project Configuration (CRITICAL for multi-project isolation)
export PROJECT_ID="2"
export PROJECT_SLUG="guruttava"
echo "Project ID: $PROJECT_ID | Slug: $PROJECT_SLUG"

# Git checkout from Sushrut-laptop branch
REPO_URL="https://github.com/Sushrut-01/gurutattva-e2e-automation"
BRANCH="Sushrut-laptop"
echo "Checking out code from $REPO_URL (branch: $BRANCH)..."
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    rm -rf * .[^.]*
    git clone -b $BRANCH "$REPO_URL" .
fi
export GIT_COMMIT=$(git rev-parse HEAD)
export GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Git Branch: $GIT_BRANCH | Commit: $GIT_COMMIT"

# Install dependencies
echo "Installing Robot Framework and dependencies..."
python3 -m pip install --quiet --upgrade pip --break-system-packages 2>/dev/null || python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet --break-system-packages robotframework robotframework-appiumlibrary robotframework-seleniumlibrary pymongo python-dotenv boto3 requests 2>/dev/null || python3 -m pip install --quiet robotframework robotframework-appiumlibrary robotframework-seleniumlibrary pymongo python-dotenv boto3 requests

# MongoDB configuration (Guruttava collection)
export MONGODB_URI='mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
export MONGODB_COLLECTION="guruttava_test_failures"
export JOB_NAME="$JOB_NAME"
export BUILD_NUMBER="$BUILD_NUMBER"
export BUILD_URL="$BUILD_URL"

# Create output directory
mkdir -p robot-results

# Determine which test suites to run based on PLATFORM parameter
TEST_SUITE=""
if [ "$PLATFORM" = "Android" ]; then
    TEST_SUITE="tests/mobile/android/"
elif [ "$PLATFORM" = "iOS" ]; then
    TEST_SUITE="tests/mobile/ios/"
elif [ "$PLATFORM" = "Web" ]; then
    TEST_SUITE="tests/web/"
elif [ "$PLATFORM" = "All" ]; then
    TEST_SUITE="tests/"
else
    # Default to Android if not specified
    TEST_SUITE="tests/mobile/android/"
fi

echo "Running $PLATFORM tests from: $TEST_SUITE"
echo "Test Type: $TEST_TYPE"

# Run Robot Framework tests
echo "Executing Robot Framework tests..."
python3 -m robot \
    --outputdir robot-results \
    --xunit robot-results/xunit.xml \
    --variable PROJECT_ID:$PROJECT_ID \
    --variable PROJECT_SLUG:$PROJECT_SLUG \
    --variable TEST_TYPE:$TEST_TYPE \
    --name "Guruttava_${PLATFORM}_Tests" \
    $TEST_SUITE

# Capture Robot Framework exit code
ROBOT_EXIT_CODE=$?
echo "Robot Framework exit code: $ROBOT_EXIT_CODE"

# Parse Robot output.xml and upload to platform
echo "Parsing test results and uploading to platform..."
if [ -f "robot-results/output.xml" ]; then
    # Use the robot_framework_parser.py if it exists in the repo
    if [ -f "implementation/robot_framework_parser.py" ]; then
        python3 implementation/robot_framework_parser.py \
            --output-file robot-results/output.xml \
            --project-id $PROJECT_ID \
            --project-slug $PROJECT_SLUG \
            --build-number $BUILD_NUMBER \
            --job-name "$JOB_NAME"
    fi

    # Trigger AI analysis
    echo "Triggering AI analysis for failures..."
    curl -X POST http://host.docker.internal:5004/api/trigger-analysis \
        -H "Content-Type: application/json" \
        -d "{\"project_id\": $PROJECT_ID, \"project_slug\": \"$PROJECT_SLUG\"}" \
        2>/dev/null || echo "AI analysis trigger failed (non-critical)"
fi

echo "========================================="
echo "Guruttava Tests completed!"
echo "Platform: $PLATFORM"
echo "Results uploaded to project_id: $PROJECT_ID"
echo "========================================="

# Exit with the robot exit code to properly mark build as UNSTABLE/FAILURE
exit $ROBOT_EXIT_CODE
```

#### F. Post-build Actions

**Add: Archive the artifacts**
- Files to archive: `robot-results/**/*`
- ✓ Check "Do not fail build if archiving returns nothing"

**Add: Publish JUnit test result report**
- Test report XMLs: `robot-results/xunit.xml`
- ✓ Check "Allow empty results"

### Step 4: Save
Click **"Save"** at the bottom

---

## 🧪 Test the Job

### First Build:

1. Go to job page: http://localhost:8081/job/Guruttava-E2E-Tests/
2. Click **"Build with Parameters"**
3. Select:
   - PLATFORM: **Android**
   - TEST_TYPE: **Smoke**
   - SEND_NOTIFICATIONS: ✓
4. Click **"Build"**

### Monitor Execution:

1. Click on build **#1**
2. Click **"Console Output"**
3. Watch for:
   - ✓ Project ID: 2
   - ✓ Git clone from Sushrut-laptop
   - ✓ Tests execution
   - ✓ MongoDB upload
   - ✓ AI analysis trigger

---

## ✅ Verify End-to-End Flow

### Check MongoDB:
```javascript
// Connect: mongodb+srv://...
db.guruttava_test_failures.find({project_id: 2}).limit(5)
```

### Check PostgreSQL:
```sql
SELECT * FROM failure_analysis WHERE project_id = 2 LIMIT 5;
```

### Check Dashboard:
```
http://localhost:5173/
→ Select "Guruttava" project
→ View failures
```

---

## 🎯 Why Manual Creation?

| Approach | Status |
|----------|--------|
| XML config injection | ❌ Caused restart issues |
| Pipeline from SCM | ❌ Jenkinsfile branch confusion |
| **Manual UI creation** | ✅ **Same as working DDN jobs** |

**The DDN jobs that ARE working were likely created manually through the UI.**
**Let's follow the same proven approach!**

---

## ⏰ Timeline

- **Now**: Let Jenkins stabilize (10-15 minutes)
- **Then**: Create job manually (5 minutes)
- **Next**: Run first build (5-10 minutes)
- **Finally**: Verify E2E flow (5 minutes)

**Total**: ~30-35 minutes for stable, working setup

---

## 📋 Checklist

- [ ] Jenkins stable and accessible (HTTP 200)
- [ ] Created Guruttava-E2E-Tests job via UI
- [ ] Configured all parameters correctly
- [ ] Saved job configuration
- [ ] Ran first test build
- [ ] Build executed successfully
- [ ] MongoDB has guruttava_test_failures data
- [ ] PostgreSQL has project_id=2 entries
- [ ] Dashboard shows Guruttava failures
- [ ] Data isolation confirmed

---

**Simple, stable, proven approach. Let's wait for Jenkins to stabilize and create the job properly!** 🚀
