# 🚀 Create Guruttava Pipeline Job - Manual Steps (5 Minutes)

**Current Issue**: The existing job is FreeStyle, we need Pipeline type!

---

## ✅ Simple Steps to Fix:

### Step 1: Delete Old Job
1. Go to: http://localhost:8081/
2. Find "Guruttava-E2E-All-Suites"
3. Click on it
4. Left sidebar → Click **"Delete Project"**
5. Confirm deletion

---

### Step 2: Create New Pipeline Job

1. Go back to: http://localhost:8081/
2. Click **"New Item"** (top left)
3. Enter name: `Guruttava-E2E-All-Suites`
4. Select **"Pipeline"** (NOT FreeStyle!)
5. Click **"OK"**

---

### Step 3: Configure Job

#### A. Description (Optional)
```
Guruttava E2E Automation - Run ALL Test Suites Sequentially
Platforms: Android, iOS, Web
Multi-Project: PROJECT_ID=2, Jira: GURU
```

#### B. This project is parameterized
☑ Check **"This project is parameterized"**

Click **"Add Parameter"** 4 times and add these:

**Parameter 1: Choice Parameter**
- Name: `PLATFORM`
- Choices (one per line):
  ```
  All
  Android
  iOS
  Web
  ```
- Description: `Select platform (All = runs ALL suites)`

**Parameter 2: Choice Parameter**
- Name: `TEST_TYPE`
- Choices:
  ```
  All
  Smoke
  Regression
  Sanity
  ```
- Description: `Select test type`

**Parameter 3: String Parameter**
- Name: `DEVICE_NAME`
- Default: `emulator-5554`
- Description: `Android device or iOS simulator`

**Parameter 4: String Parameter**
- Name: `APP_PATH`
- Default: `apps/guruttava.apk`
- Description: `Path to mobile app`

#### C. Pipeline Section (MOST IMPORTANT!)

Scroll down to **"Pipeline"** section:

1. **Definition**: Select `Pipeline script from SCM`

2. **SCM**: Select `Git`

3. **Repository URL**:
   ```
   https://github.com/Sushrut-01/gurutattva-e2e-automation
   ```

4. **Credentials**: Leave as `- none -`

5. **Branch Specifier**:
   ```
   */master
   ```

6. **Script Path**:
   ```
   Jenkinsfile
   ```

7. ☑ Check **"Lightweight checkout"**

#### D. Build Triggers (Optional)

☑ Check **"Poll SCM"**
- Schedule: `H/15 * * * *`

---

### Step 4: Save
Click **"Save"** at the bottom!

---

## 🎯 Key Configuration Summary:

| Setting | Value |
|---------|-------|
| **Job Name** | Guruttava-E2E-All-Suites |
| **Job Type** | Pipeline (NOT FreeStyle!) |
| **Repository** | https://github.com/Sushrut-01/gurutattva-e2e-automation |
| **Branch** | */master |
| **Script** | Jenkinsfile |
| **Parameters** | 4 (PLATFORM, TEST_TYPE, DEVICE_NAME, APP_PATH) |

---

## 🚀 After Saving - Test It!

1. Go to: http://localhost:8081/job/Guruttava-E2E-All-Suites/
2. Click **"Build with Parameters"**
3. Select:
   - **PLATFORM**: `All` ← Runs ALL suites!
   - **TEST_TYPE**: `All`
4. Click **"Build"**
5. Click on build #1
6. Click **"Console Output"** to watch it run!

---

## ✅ What Will Happen:

```
1. Jenkins pulls from GitHub (origin/master)
2. Finds Jenkinsfile in repo root
3. Executes Jenkinsfile
4. Runs ALL Android → iOS → Web test suites
5. Uploads results (PROJECT_ID=2)
6. Creates Jira tickets in GURU project
7. Shows in dashboard under Guruttava project
```

---

## 🎉 Success Indicators:

After first build, you should see:
- ✅ Build #1 appears
- ✅ Console shows: "Checking out from GitHub"
- ✅ Console shows: "PROJECT_ID=2", "PROJECT_SLUG=guruttava"
- ✅ All test suites execute in sequence
- ✅ Results uploaded to platform
- ✅ Jira tickets created (if failures)
- ✅ Data visible in dashboard (Guruttava project)

---

**Time Required**: 5 minutes to create + 2 minutes to test = 7 minutes total!

**Ready? Start with Step 1 above!** 🚀
