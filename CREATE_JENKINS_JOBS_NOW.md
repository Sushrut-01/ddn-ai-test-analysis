# 🚀 Create Jenkins Jobs - Step by Step

**Time Required**: 5 minutes
**Jenkins URL**: http://localhost:8081/

---

## ✅ Job 1: DDN-Tests-Pipeline

### Step 1: Open Jenkins
Open your browser and go to: http://localhost:8081/

### Step 2: Create New Item
1. Click **"New Item"** (top left corner)
2. Enter item name: `DDN-Tests-Pipeline`
3. Select **"Pipeline"**
4. Click **"OK"**

### Step 3: Configure General Settings
1. **Description** (optional):
   ```
   DDN Storage Test Automation - Web API, Selenium, and E2E Testing (Multi-Project: PROJECT_ID=1)
   ```

2. Check ☑ **"This project is parameterized"**

3. Add these parameters by clicking "Add Parameter":

   **Parameter 1: Choice Parameter**
   - Name: `TEST_TYPE`
   - Choices (one per line):
     ```
     All
     Smoke
     Regression
     Sanity
     Performance
     ```
   - Description: `Select test type to run`

   **Parameter 2: Choice Parameter**
   - Name: `TEST_SUITE`
   - Choices (one per line):
     ```
     All
     Basic
     Advanced
     API
     UI
     ```
   - Description: `Select test suite`

   **Parameter 3: Boolean Parameter**
   - Name: `SEND_NOTIFICATIONS`
   - Default: ☑ Checked
   - Description: `Send notifications on completion`

   **Parameter 4: Boolean Parameter**
   - Name: `RUN_PERFORMANCE_TESTS`
   - Default: ☐ Unchecked
   - Description: `Include performance benchmarks`

### Step 4: Configure Pipeline
Scroll down to the **"Pipeline"** section:

1. **Definition**: Select `Pipeline script from SCM`

2. **SCM**: Select `Git`

3. **Repository URL**:
   ```
   https://github.com/Sushrut-01/ddn-jenkins-testing.git
   ```

4. **Branch Specifier**:
   ```
   */main
   ```

5. **Script Path**:
   ```
   Jenkinsfile
   ```

6. ☑ Check **"Lightweight checkout"**

### Step 5: Build Triggers (Optional)
Scroll to **"Build Triggers"** section:
- ☑ Check **"Poll SCM"**
- Schedule: `H/15 * * * *` (checks every 15 minutes)

### Step 6: Save
Click **"Save"** at the bottom

---

## ✅ Job 2: Guruttava-E2E-All-Suites

### Step 1: Go Back to Dashboard
Click **"Jenkins"** logo (top left) or go to http://localhost:8081/

### Step 2: Create New Item
1. Click **"New Item"** (top left corner)
2. Enter item name: `Guruttava-E2E-All-Suites`
3. Select **"Pipeline"**
4. Click **"OK"**

### Step 3: Configure General Settings
1. **Description** (optional):
   ```
   Guruttava E2E Automation - Run ALL Test Suites Sequentially (Android/iOS/Web) (Multi-Project: PROJECT_ID=2)
   ```

2. Check ☑ **"This project is parameterized"**

3. Add these parameters by clicking "Add Parameter":

   **Parameter 1: Choice Parameter**
   - Name: `PLATFORM`
   - Choices (one per line):
     ```
     All
     Android
     iOS
     Web
     ```
   - Description: `Select platform to test (All = runs EVERY suite sequentially)`

   **Parameter 2: Choice Parameter**
   - Name: `TEST_TYPE`
   - Choices (one per line):
     ```
     All
     Smoke
     Regression
     Sanity
     ```
   - Description: `Select test type`

   **Parameter 3: String Parameter**
   - Name: `DEVICE_NAME`
   - Default Value: `emulator-5554`
   - Description: `Android device name or iOS simulator`

   **Parameter 4: String Parameter**
   - Name: `APP_PATH`
   - Default Value: `apps/guruttava.apk`
   - Description: `Path to mobile app (APK/APP file)`

### Step 4: Configure Pipeline
Scroll down to the **"Pipeline"** section:

1. **Definition**: Select `Pipeline script from SCM`

2. **SCM**: Select `Git`

3. **Repository URL**:
   ```
   https://github.com/Sushrut-01/gurutattva-e2e-automation
   ```

4. **Branch Specifier**:
   ```
   */main
   ```

5. **Script Path**:
   ```
   Jenkinsfile
   ```

6. ☑ Check **"Lightweight checkout"**

### Step 5: Build Triggers (Optional)
Scroll to **"Build Triggers"** section:
- ☑ Check **"Poll SCM"**
- Schedule: `H/15 * * * *` (checks every 15 minutes)

### Step 6: Save
Click **"Save"** at the bottom

---

## ✅ Before First Build - Copy Jenkinsfiles to GitHub!

**IMPORTANT**: The jobs will fail until you copy the Jenkinsfiles to your repositories!

### For DDN:
```bash
cd /path/to/ddn-jenkins-testing

# Copy the Jenkinsfile
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/DDN-Jenkinsfile ./Jenkinsfile

# Commit and push
git add Jenkinsfile
git commit -m "feat: add multi-project Jenkins pipeline (PROJECT_ID=1)"
git push origin main
```

### For Guruttava:
```bash
cd /path/to/gurutattva-e2e-automation

# Copy the Jenkinsfile
cp C:/DDN-AI-Project-Documentation/jenkins-jobs/Guruttava-Jenkinsfile ./Jenkinsfile

# Commit and push
git add Jenkinsfile
git commit -m "feat: add Jenkins pipeline to run all E2E suites (PROJECT_ID=2)"
git push origin main
```

---

## 🎯 Test Your Jobs

### Test DDN Job:
1. Go to http://localhost:8081/job/DDN-Tests-Pipeline/
2. Click **"Build with Parameters"**
3. Select:
   - TEST_TYPE: `Smoke`
   - TEST_SUITE: `All`
   - SEND_NOTIFICATIONS: ☑
   - RUN_PERFORMANCE_TESTS: ☐
4. Click **"Build"**
5. Watch the console output

### Test Guruttava Job (All E2E Suites):
1. Go to http://localhost:8081/job/Guruttava-E2E-All-Suites/
2. Click **"Build with Parameters"**
3. Select:
   - PLATFORM: `All` ← **This runs EVERY test suite!**
   - TEST_TYPE: `All`
   - DEVICE_NAME: `emulator-5554`
   - APP_PATH: `apps/guruttava.apk`
4. Click **"Build"**
5. **This will run ALL Android → iOS → Web test suites sequentially!**

---

## 📊 What Happens When You Run

### DDN-Tests-Pipeline Flow:
```
1. Checkout ddn-jenkins-testing repo
2. Setup Python + Robot Framework
3. Run Selected Test Suite (Basic/Advanced/API/UI)
4. Parse results
5. Upload to platform (PROJECT_ID=1)
6. Store in PostgreSQL (project_id=1)
7. Create Jira tickets in DDN project
8. Display in dashboard (DDN project only)
```

### Guruttava-E2E-All-Suites Flow (PLATFORM=All):
```
1. Checkout gurutattva-e2e-automation repo
2. Setup Python + Robot Framework + Appium
3. Run ALL Android test suites (sequence)
   - Suite 1 → Suite 2 → Suite 3 → ... → Suite N
4. Run ALL iOS test suites (sequence)
   - Suite 1 → Suite 2 → Suite 3 → ... → Suite N
5. Run ALL Web test suites (sequence)
   - Suite 1 → Suite 2 → Suite 3 → ... → Suite N
6. Consolidate results
7. Upload to platform (PROJECT_ID=2)
8. Store in PostgreSQL (project_id=2)
9. Create Jira tickets in GURU project
10. Display in dashboard (Guruttava project only)
```

---

## ✅ Verification Checklist

After creating both jobs:
- [ ] DDN-Tests-Pipeline appears in Jenkins dashboard
- [ ] Guruttava-E2E-All-Suites appears in Jenkins dashboard
- [ ] Both show parameters when clicking "Build with Parameters"
- [ ] Jenkinsfiles copied to both GitHub repositories
- [ ] Test build of DDN-Tests-Pipeline runs successfully
- [ ] Test build of Guruttava-E2E-All-Suites runs successfully

---

## 🎉 You're Done!

Both Jenkins jobs are now configured for CI/CD:
- ✅ **DDN-Tests-Pipeline** - PROJECT_ID=1 (Web/API testing)
- ✅ **Guruttava-E2E-All-Suites** - PROJECT_ID=2 (Mobile/Web testing, ALL suites)

**Key Features**:
- ✅ Automatic builds on code push (SCM polling every 15 min)
- ✅ Parameterized builds (choose what to test)
- ✅ Complete data isolation (different project_id)
- ✅ Automatic AI analysis and Jira ticket creation
- ✅ Results visible in dashboard per project

**Run All Guruttava E2E Suites**: Just select PLATFORM=All! 🚀
