# 🚀 Create Guruttava E2E Job - Step by Step

**Existing DDN Jobs**: ✅ Keep them! They're working fine.
**New Job Needed**: Guruttava-E2E-All-Suites (for all E2E test suites)

---

## ✅ Existing DDN Jobs (Keep These!)

You already have these working DDN jobs:
- ✅ **DDN-Basic-Tests** - Running basic test suite
- ✅ **DDN-Advanced-Tests** - Running advanced test suite
- ✅ **DDN-Nightly-Tests** - Running nightly comprehensive tests
- ✅ **DDN-Tests** - General DDN tests

**Status**: All integrated with database, Jira, and dashboard
**Action**: **Keep them as-is!** No changes needed.

---

## 🆕 Create NEW Job: Guruttava-E2E-All-Suites

### Why Create This Job?
- Run **ALL Guruttava E2E test suites** in sequence
- Support Android, iOS, and Web platforms
- Complete isolation (PROJECT_ID=2, GURU Jira project)
- Separate from DDN data

---

## 📋 Step-by-Step Creation

### Step 1: Open Jenkins
Go to: http://localhost:8081/

### Step 2: Create New Item
1. Click **"New Item"** (top left)
2. Enter name: `Guruttava-E2E-All-Suites`
3. Select **"Pipeline"** (NOT FreeStyle like DDN jobs)
4. Click **"OK"**

### Step 3: Add Description
In the **Description** field:
```
Guruttava E2E Automation - Run ALL Test Suites Sequentially
Platforms: Android, iOS, Web
Multi-Project: PROJECT_ID=2, Jira: GURU
Repo: https://github.com/Sushrut-01/gurutattva-e2e-automation
```

### Step 4: Configure Parameters
Check ☑ **"This project is parameterized"**

Click **"Add Parameter"** and add these 4 parameters:

#### Parameter 1: Choice Parameter
- **Name**: `PLATFORM`
- **Choices** (one per line):
  ```
  All
  Android
  iOS
  Web
  ```
- **Description**: `Select platform (All = runs EVERY suite sequentially)`

#### Parameter 2: Choice Parameter
- **Name**: `TEST_TYPE`
- **Choices** (one per line):
  ```
  All
  Smoke
  Regression
  Sanity
  ```
- **Description**: `Select test type`

#### Parameter 3: String Parameter
- **Name**: `DEVICE_NAME`
- **Default Value**: `emulator-5554`
- **Description**: `Android device name or iOS simulator`

#### Parameter 4: String Parameter
- **Name**: `APP_PATH`
- **Default Value**: `apps/guruttava.apk`
- **Description**: `Path to mobile app (APK/APP file)`

### Step 5: Configure Pipeline
Scroll down to **"Pipeline"** section:

1. **Definition**: Select `Pipeline script from SCM`

2. **SCM**: Select `Git`

3. **Repository URL**:
   ```
   https://github.com/Sushrut-01/gurutattva-e2e-automation
   ```

4. **Credentials**: (leave as "- none -" if public repo)

5. **Branches to build**:
   - Branch Specifier: `*/main`

6. **Script Path**:
   ```
   Jenkinsfile
   ```

7. ☑ Check **"Lightweight checkout"**

### Step 6: Build Triggers (Optional but Recommended)
Scroll to **"Build Triggers"**:
- ☑ Check **"Poll SCM"**
- **Schedule**: `H/15 * * * *`
  - This checks GitHub every 15 minutes for changes

### Step 7: Advanced Options (Optional)
Under **"Pipeline"** section, you can also:
- ☑ Check **"Do not allow concurrent builds"** (recommended)

### Step 8: Save
Click **"Save"** button at the bottom

---

## ⚠️ BEFORE First Build - Copy Jenkinsfile to GitHub!

The job will fail without the Jenkinsfile in your repository!

### Copy Jenkinsfile to Guruttava Repo:
```bash
# Navigate to your local Guruttava repo
cd /path/to/gurutattva-e2e-automation

# Copy the Jenkinsfile
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/Guruttava-Jenkinsfile ./Jenkinsfile

# Check it was copied
ls -la Jenkinsfile

# Commit and push
git add Jenkinsfile
git commit -m "feat: add Jenkins pipeline to run all E2E suites sequentially (PROJECT_ID=2)"
git push origin main
```

### Verify on GitHub:
Go to: https://github.com/Sushrut-01/gurutattva-e2e-automation
- You should see `Jenkinsfile` in the root directory

---

## 🚀 Test Your New Job

### Step 1: Navigate to Job
Go to: http://localhost:8081/job/Guruttava-E2E-All-Suites/

### Step 2: Build with Parameters
1. Click **"Build with Parameters"** (left sidebar)
2. You'll see 4 parameters:
   - **PLATFORM**: Select `All` ← **This runs EVERY test suite!**
   - **TEST_TYPE**: Select `All` or `Smoke` for first test
   - **DEVICE_NAME**: Leave as `emulator-5554`
   - **APP_PATH**: Leave as `apps/guruttava.apk`
3. Click **"Build"** button

### Step 3: Monitor Build
1. You'll see a new build number appear (e.g., #1)
2. Click on the build number
3. Click **"Console Output"** to see live logs

### What Will Happen:
```
Stage 1: Checkout gurutattva-e2e-automation repo
  ↓
Stage 2: Setup Python + Robot Framework + Appium
  ↓
Stage 3: Verify Appium Server
  ↓
Stage 4: Run ALL Android Test Suites (in sequence)
  - Every .robot file in tests/mobile/android/
  ↓
Stage 5: Run ALL iOS Test Suites (in sequence)
  - Every .robot file in tests/mobile/ios/
  ↓
Stage 6: Run ALL Web Test Suites (in sequence)
  - Every .robot file in tests/web/
  ↓
Stage 7: Parse Results
  ↓
Stage 8: Upload to Platform (PROJECT_ID=2)
  ↓
Stage 9: Publish Robot Reports
  ↓
Stage 10: Trigger AI Analysis (if failures)
  - Creates Jira tickets in GURU project
  - Stores in PostgreSQL with project_id=2
  - Visible in dashboard under Guruttava project
```

---

## 📊 Comparison: DDN Jobs vs Guruttava Job

| Aspect | Existing DDN Jobs | New Guruttava Job |
|--------|------------------|-------------------|
| **Type** | FreeStyle Project | Pipeline (modern) |
| **PROJECT_ID** | 1 (DDN) | 2 (Guruttava) |
| **GitHub Repo** | ddn-jenkins-testing | gurutattva-e2e-automation |
| **Test Types** | Basic, Advanced, Nightly | Android, iOS, Web (ALL suites) |
| **Jira Project** | DDN | GURU |
| **MongoDB Collections** | ddn_* | guruttava_* |
| **Dashboard** | DDN Project view | Guruttava Project view |
| **Keep or Create?** | **KEEP** (working) | **CREATE** (new) |

---

## ✅ Verification Checklist

After creating the Guruttava job:
- [ ] Job appears in Jenkins dashboard: http://localhost:8081/
- [ ] Jenkinsfile copied to gurutattva-e2e-automation repo
- [ ] Jenkinsfile visible on GitHub
- [ ] First build triggered (Build with Parameters)
- [ ] Build runs without errors (check Console Output)
- [ ] Robot Framework reports published
- [ ] Failures uploaded to platform with PROJECT_ID=2
- [ ] Data visible in dashboard under "Guruttava" project
- [ ] Jira tickets created in GURU project (if failures)

---

## 🎯 What Makes This Job Special?

### When You Select PLATFORM=All:
1. **Runs EVERY test suite** in your repository
2. **Sequential execution**: Android → iOS → Web
3. **Within each platform**, runs all test files:
   - `tests/mobile/android/*.robot`
   - `tests/mobile/ios/*.robot`
   - `tests/web/*.robot`
4. **Consolidates results** from all suites
5. **Single report** with all test results

### Benefits:
- ✅ **One-click execution** of entire test suite
- ✅ **Complete coverage** - nothing is missed
- ✅ **Automatic AI analysis** of all failures
- ✅ **Jira tickets** for all issues found
- ✅ **Complete isolation** from DDN project data

---

## 🔧 Optional: Update Existing DDN Jobs (Later)

Your existing DDN jobs work fine, but for better multi-project support, you can add:

### Add PROJECT_ID Environment Variable
Edit each DDN job (DDN-Basic-Tests, DDN-Advanced-Tests, DDN-Nightly-Tests):
1. Click job → Configure
2. Scroll to "Build Environment" section
3. Check "Inject environment variables"
4. Add:
   ```
   PROJECT_ID=1
   PROJECT_SLUG=ddn
   ```
5. Save

**This ensures proper multi-project isolation**, but your jobs work without it too (they default to project_id=1).

---

## 🎉 You're Done!

After creating this job, you'll have:

### DDN (Existing - Keep)
- ✅ DDN-Basic-Tests
- ✅ DDN-Advanced-Tests
- ✅ DDN-Nightly-Tests
- ✅ DDN-Tests

### Guruttava (NEW - Just Created)
- ✅ Guruttava-E2E-All-Suites ← **Runs ALL suites sequentially!**

**Total CI/CD Setup**: 5 jobs, 2 projects, complete isolation! 🚀

---

## 🐛 Troubleshooting

### Job Shows "Jenkinsfile not found"
**Solution**: Jenkinsfile not in GitHub repo
```bash
cd /path/to/gurutattva-e2e-automation
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/Guruttava-Jenkinsfile ./Jenkinsfile
git add . && git commit -m "add Jenkinsfile" && git push
```

### Appium Not Accessible
**Solution**: Start Appium container
```bash
docker start guruttava-appium
curl http://localhost:4723/wd/hub/status  # Should return OK
```

### Tests Pass But No Data in Dashboard
**Solution**: Check PROJECT_ID in console output
- Search console for "PROJECT_ID"
- Should show: `PROJECT_ID=2`, `PROJECT_SLUG=guruttava`

---

**Ready to create the Guruttava job? Follow the steps above!** 🚀

**Time Required**: 5 minutes to create + 5 minutes to copy Jenkinsfile = **10 minutes total**
