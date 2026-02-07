# 🔧 Fix Jenkins Job Configuration - Step by Step

**Issue**: Robot Framework exit code 252 = Directory doesn't exist
**Cause**: Job looks for `tests/mobile/android/` but it doesn't exist
**Solution**: Change test path to `tests/` (5-minute fix)

---

## 📋 Step-by-Step Fix Instructions

### Step 1: Open Job Configuration

**Click this URL**:
```
http://localhost:8081/job/Guruttava-E2E-Tests/configure
```

**Or navigate manually**:
1. Go to: http://localhost:8081/
2. Click: "Guruttava-E2E-Tests"
3. Click: "Configure" (left sidebar)

---

### Step 2: Scroll Down to "Build" Section

Scroll down until you see:
```
Build
  Execute shell
  [Large text box with bash script]
```

---

### Step 3: Find the Problem Code

In the large text box, **scroll down** and find these lines (around line 50-70):

```bash
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
```

---

### Step 4: Replace with Fixed Code

**DELETE the entire block above** (from `TEST_SUITE=""` to the last `fi`)

**REPLACE with this simple code**:

```bash
# Run all Robot Framework tests
TEST_SUITE="tests/"
echo "Running all tests from: $TEST_SUITE"
```

**That's it!** Just these 3 lines!

---

### Step 5: Verify the Change

After the change, the script should look like:

```bash
# Create output directory
mkdir -p robot-results

# Run all Robot Framework tests
TEST_SUITE="tests/"
echo "Running all tests from: $TEST_SUITE"

echo "Running $PLATFORM tests from: $TEST_SUITE"  # ← This line might say "Android" but it's OK
echo "Test Type: $TEST_TYPE"

# Run Robot Framework tests
echo "Executing Robot Framework tests..."
python3 -m robot \
    --outputdir robot-results \
    --xunit robot-results/xunit.xml \
    ...
```

---

### Step 6: Save Configuration

**Scroll to the bottom** of the page

**Click**: "Save" button

**Wait**: For "Configuration saved" message

---

### Step 7: Trigger Build #4

1. You'll be redirected to the job page
2. Click: **"Build with Parameters"** (left sidebar)
3. Select:
   - PLATFORM: **Android** (doesn't matter now, we ignore it)
   - TEST_TYPE: **Smoke**
   - SEND_NOTIFICATIONS: ✓
4. Click: **"Build"**

---

### Step 8: Watch Build #4 Execute

1. Build #4 appears under "Build History"
2. Click on **#4**
3. Click: **"Console Output"**
4. Watch for:

**Expected Output**:
```bash
Running all tests from: tests/
Executing Robot Framework tests...
==============================================================================
E2EAudio :: Audio E2E Tests
==============================================================================
Test Case 1                                                           | PASS/FAIL
Test Case 2                                                           | PASS/FAIL
...
==============================================================================
E2EAudio :: Audio E2E Tests                                | X passed, Y failed
==============================================================================
```

**Success Indicators**:
- ✅ Tests actually execute (you see test names)
- ✅ Robot Framework exit code: 0 (or non-zero if tests fail)
- ✅ "Results uploaded to project_id: 2"
- ✅ Build result: SUCCESS or UNSTABLE (both are good!)

---

## 🎯 Visual Guide

### What to Delete:

```diff
- # Determine which test suites to run based on PLATFORM parameter
- TEST_SUITE=""
- if [ "$PLATFORM" = "Android" ]; then
-     TEST_SUITE="tests/mobile/android/"
- elif [ "$PLATFORM" = "iOS" ]; then
-     TEST_SUITE="tests/mobile/ios/"
- elif [ "$PLATFORM" = "Web" ]; then
-     TEST_SUITE="tests/web/"
- elif [ "$PLATFORM" = "All" ]; then
-     TEST_SUITE="tests/"
- else
-     # Default to Android if not specified
-     TEST_SUITE="tests/mobile/android/"
- fi
```

### What to Add:

```diff
+ # Run all Robot Framework tests
+ TEST_SUITE="tests/"
+ echo "Running all tests from: $TEST_SUITE"
```

---

## ⚠️ Important Notes

### Don't Worry About:

- The line that says "Running $PLATFORM tests from: tests/"
- The PLATFORM parameter (we'll fix it properly later)
- The echo statements mentioning "Android"

### What Matters:

- ✅ `TEST_SUITE="tests/"` is set correctly
- ✅ Robot Framework will run `.robot` files from `tests/` directory
- ✅ Tests will execute!

---

## 🐛 If You Have Trouble Finding the Code

### Search for this text in the shell script box:

Press `Ctrl+F` (Find) and search for:
```
tests/mobile/android
```

This will jump you right to the section that needs fixing.

---

## 📊 Expected Results

### Build #4 Should:

1. ✅ **Clone repository** successfully (already works)
2. ✅ **Install Python packages** (already works)
3. ✅ **Find test directory** (will work after fix!)
4. ✅ **Execute Robot Framework tests** (will work!)
5. ✅ **Generate results** (output.xml, log.html, report.html)
6. ✅ **Upload to MongoDB** (project_id=2)
7. ✅ **Trigger AI analysis**
8. ✅ **Build result**: SUCCESS or UNSTABLE

### After Build Completes:

- ✅ Console shows test execution
- ✅ Tests pass or fail (both are fine - we just need them to RUN)
- ✅ Data flows to MongoDB and PostgreSQL
- ✅ Dashboard shows Guruttava failures
- ✅ **END-TO-END FLOW COMPLETE!** 🎉

---

## 🚀 Quick Summary

**What you're changing**:
- **From**: `TEST_SUITE="tests/mobile/android/"` (doesn't exist)
- **To**: `TEST_SUITE="tests/"` (exists!)

**Where**: Jenkins job configuration → Build → Execute shell

**Time**: 2 minutes to change, 5-10 minutes for build to run

**Result**: Tests will execute successfully!

---

## 💡 After This Works

Once Build #4 succeeds, we can:

1. ✅ Verify MongoDB data
2. ✅ Check PostgreSQL entries
3. ✅ View failures in Dashboard
4. ✅ Confirm multi-project isolation
5. ✅ **CELEBRATE SUCCESS!** 🎉

Then optionally:
- Update PLATFORM parameter to match actual test modules
- Create custom test selection
- Set up scheduled builds

---

**Go ahead and make this change now!**

**URL**: http://localhost:8081/job/Guruttava-E2E-Tests/configure

Just change those ~13 lines to 3 lines, save, and rebuild! 🎯
