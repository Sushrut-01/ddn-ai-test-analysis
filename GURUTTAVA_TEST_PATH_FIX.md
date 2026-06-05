# 🔧 Guruttava Test Path Fix Required

**Issue Found**: Test directory path is incorrect in job configuration
**Cause**: Repository structure is different than assumed
**Solution**: Update test paths in Jenkins job

---

## 🔍 Problem Analysis

### Build #3 Error:

```bash
[ ERROR ] Parsing '/var/jenkins_home/workspace/Guruttava-E2E-Tests/tests/mobile/android' failed:
File or directory to execute does not exist.
```

### What Job Configuration Says:

```bash
TEST_SUITE="tests/mobile/android/"  ← WRONG! This doesn't exist
```

### Actual Repository Structure:

```
gurutattva-e2e-automation/
├── pages/              # Page Object Models
├── resources/          # Shared keywords
├── tests/              # All test files here (no subdirectories!)
│   ├── CleanUpDummyE2EData.robot
│   ├── E2EAudio.robot
│   ├── E2EDhyankendra.robot
│   ├── E2EEvents.robot
│   ├── E2EHindi.robot
│   ├── E2ENamkaran.robot
│   └── ... more .robot files
├── results/
├── requirements.txt
└── README.md
```

**Reality**: It's a web/CRM testing project, not mobile with Android/iOS subdirectories!

---

## ✅ Solution: Update Jenkins Job

### Current Configuration (WRONG):

```bash
# Determine which test suites to run based on PLATFORM parameter
TEST_SUITE=""
if [ "$PLATFORM" = "Android" ]; then
    TEST_SUITE="tests/mobile/android/"  ← DOESN'T EXIST!
elif [ "$PLATFORM" = "iOS" ]; then
    TEST_SUITE="tests/mobile/ios/"  ← DOESN'T EXIST!
elif [ "$PLATFORM" = "Web" ]; then
    TEST_SUITE="tests/web/"  ← DOESN'T EXIST!
elif [ "$PLATFORM" = "All" ]; then
    TEST_SUITE="tests/"
else
    TEST_SUITE="tests/mobile/android/"
fi
```

### Fixed Configuration (CORRECT):

```bash
# Determine which test suites to run based on TEST_TYPE parameter
TEST_SUITE="tests/"  # Run all tests from tests/ directory

# Optional: Filter by test type using Robot Framework tags
if [ "$TEST_TYPE" != "All" ]; then
    TEST_TAG="--include ${TEST_TYPE}"
else
    TEST_TAG=""
fi
```

### Or Run Specific Test Files:

```bash
# Run specific test based on selection
case "$PLATFORM" in
    "Audio")
        TEST_SUITE="tests/E2EAudio.robot"
        ;;
    "Events")
        TEST_SUITE="tests/E2EEvents.robot"
        ;;
    "Dhyankendra")
        TEST_SUITE="tests/E2EDhyankendra.robot"
        ;;
    *)
        TEST_SUITE="tests/"  # Run all tests
        ;;
esac
```

---

## 🔧 Quick Fix Options

### Option 1: Simple Fix (Run All Tests)

**Easiest**: Just change the test path to `tests/`

**Pros**:
- Works immediately
- Tests all features
- Simple configuration

**Cons**:
- Runs ALL tests (might take longer)
- No platform filtering

### Option 2: Update Parameters (Better)

**Change PLATFORM parameter to test module**:
- Audio Tests
- Events Tests
- Dhyankendra Tests
- All Tests

**Pros**:
- More accurate to actual tests
- Selective test execution
- Better control

**Cons**:
- Need to update job configuration

---

## 🚀 Immediate Action: Manual Override

For now, let's just run ALL tests to verify the pipeline works:

### Update Job Configuration:

1. **Go to Jenkins**: http://localhost:8081/job/Guruttava-E2E-Tests/configure

2. **Find the Execute Shell section**

3. **Find this block** (around line 50-70):

```bash
# Determine which test suites to run based on PLATFORM parameter
TEST_SUITE=""
if [ "$PLATFORM" = "Android" ]; then
    TEST_SUITE="tests/mobile/android/"
...
```

4. **Replace with**:

```bash
# Determine which test suites to run
TEST_SUITE="tests/"  # Run all Robot Framework tests
echo "Running all tests from: $TEST_SUITE"
```

5. **Click Save**

6. **Trigger Build #4**

---

## 💡 Better Solution: Proper Configuration

### Updated Shell Script:

```bash
#!/bin/bash
echo "========================================="
echo "Guruttava E2E Tests (Robot Framework)"
echo "Build: $BUILD_NUMBER"
echo "Job: $JOB_NAME"
echo "Platform: $PLATFORM"
echo "Test Type: $TEST_TYPE"
echo "========================================="

# Project Configuration
export PROJECT_ID="2"
export PROJECT_SLUG="guruttava"
echo "Project ID: $PROJECT_ID | Slug: $PROJECT_SLUG"

# Git checkout
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

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
python3 -m pip install --quiet --upgrade pip --break-system-packages 2>/dev/null || python3 -m pip install --quiet --upgrade pip
if [ -f "requirements.txt" ]; then
    python3 -m pip install --quiet --break-system-packages -r requirements.txt 2>/dev/null || python3 -m pip install --quiet -r requirements.txt
else
    # Fallback to manual installation
    python3 -m pip install --quiet --break-system-packages robotframework robotframework-appiumlibrary robotframework-seleniumlibrary Appium-Python-Client selenium pymongo python-dotenv boto3 requests
fi

# MongoDB configuration
export MONGODB_URI='mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority'
export MONGODB_COLLECTION="guruttava_test_failures"
export JOB_NAME="$JOB_NAME"
export BUILD_NUMBER="$BUILD_NUMBER"
export BUILD_URL="$BUILD_URL"

# Create output directory
mkdir -p robot-results

# Select test based on PLATFORM parameter
case "$PLATFORM" in
    "Audio")
        TEST_SUITE="tests/E2EAudio.robot"
        ;;
    "Events")
        TEST_SUITE="tests/E2EEvents.robot"
        ;;
    "Dhyankendra")
        TEST_SUITE="tests/E2EDhyankendra.robot"
        ;;
    "Hindi")
        TEST_SUITE="tests/E2EHindi.robot"
        ;;
    "All"|*)
        TEST_SUITE="tests/"
        ;;
esac

echo "Running tests from: $TEST_SUITE"
echo "Test Type: $TEST_TYPE"

# Build Robot options
ROBOT_OPTS="--outputdir robot-results --xunit robot-results/xunit.xml"

# Add test type filtering if needed
if [ "$TEST_TYPE" != "All" ] && [ "$TEST_TYPE" != "Smoke" ]; then
    # Robot Framework doesn't have built-in test types, so we run all
    echo "Note: Running all tests (test type filtering not configured)"
fi

# Run Robot Framework tests
echo "Executing Robot Framework tests..."
python3 -m robot \
    $ROBOT_OPTS \
    --variable PROJECT_ID:$PROJECT_ID \
    --variable PROJECT_SLUG:$PROJECT_SLUG \
    --name "Guruttava_E2E_Tests" \
    $TEST_SUITE

# Capture exit code
ROBOT_EXIT_CODE=$?
echo "Robot Framework exit code: $ROBOT_EXIT_CODE"

# Parse and upload results (if parser exists)
echo "Parsing test results and uploading to platform..."
if [ -f "robot-results/output.xml" ]; then
    # Try to find and run parser
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
echo "Test Suite: $TEST_SUITE"
echo "Results uploaded to project_id: $PROJECT_ID"
echo "========================================="

# Exit with robot exit code
exit $ROBOT_EXIT_CODE
```

---

## 📝 Parameter Changes Needed

### Current Parameters:

- **PLATFORM**: Android, iOS, Web, All

### Better Parameters:

- **TEST_MODULE**: Audio, Events, Dhyankendra, Hindi, All
- **TEST_TYPE**: Smoke, Regression, Sanity, All
- **SEND_NOTIFICATIONS**: true/false

---

## 🎯 Quick Action Plan

### Simplest Path (5 minutes):

1. Go to: http://localhost:8081/job/Guruttava-E2E-Tests/configure
2. Find "Execute shell" section
3. Change `TEST_SUITE="tests/mobile/android/"` to `TEST_SUITE="tests/"`
4. Save
5. Build with Parameters
6. SUCCESS!

### Better Path (10 minutes):

1. Copy the updated shell script above
2. Go to job configuration
3. Replace entire "Execute shell" content
4. Update PLATFORM parameter choices:
   - Change to: Audio, Events, Dhyankendra, Hindi, All
5. Save
6. Build with Parameters (select "All")
7. SUCCESS with proper test selection!

---

**Which approach do you prefer?**
- **Quick**: Just change test path to `tests/`
- **Proper**: Update entire script with test module selection

Let me know and I'll guide you through it!
