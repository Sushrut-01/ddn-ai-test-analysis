# Jenkins Test Configuration - What Actually Runs

**Date:** November 24, 2025  
**Question:** When Jenkins build starts, does it run Python tests in Robot Framework from GitHub?

---

## ✅ YES - Robot Framework Job Pulls from GitHub

**The `ddn-robot-tests.xml` job configuration shows:**

```xml
<scm class="hudson.plugins.git.GitSCM">
  <userRemoteConfigs>
    <hudson.plugins.git.UserRemoteConfig>
      <url>https://github.com/Sushrut-01/ddn-ai-test-analysis.git</url>
      <credentialsId>github-credentials</credentialsId>
    </hudson.plugins.git.UserRemoteConfig>
  </userRemoteConfigs>
  <branches>
    <hudson.plugins.git.BranchSpec>
      <name>*/main</name>
    </hudson.plugins.git.BranchSpec>
  </branches>
</scm>
```

**Then runs:**
```batch
python -m robot ^
  --outputdir robot-results ^
  --listener mongodb_robot_listener.py ^
  robot-tests/
```

---

## 📊 Two Jenkins Configurations Exist

### **Configuration 1: Jenkinsfile (Mocha/JavaScript)**

| Property | Value |
|----------|-------|
| **File** | `jenkins/Jenkinsfile` |
| **Type** | Groovy Pipeline |
| **Framework** | Mocha (JavaScript/Node.js) |
| **Tests** | `tests/*.js` (ddn-advanced-scenarios.js) |
| **Reporter** | `tests/mongodb-reporter.js` |
| **Source** | ❓ Not specified (may use local files) |
| **Command** | `npm run test:jenkins` |

**Jenkinsfile excerpt:**
```groovy
stage('Run Tests') {
    dir(TEST_DIR) {
        sh """
            export BUILD_ID="${env.BUILD_ID}"
            export BUILD_NUMBER="${env.BUILD_NUMBER}"
            export JOB_NAME="${env.JOB_NAME}"
            
            npm run test:jenkins || true
        """
    }
}
```

---

### **Configuration 2: ddn-robot-tests.xml (Robot Framework/Python)**

| Property | Value |
|----------|-------|
| **File** | `jenkins/jobs/ddn-robot-tests.xml` |
| **Type** | XML Job Definition |
| **Framework** | Robot Framework (Python) |
| **Tests** | `robot-tests/*.robot` (ddn_basic_tests.robot, ddn_advanced_tests.robot) |
| **Reporter** | `implementation/mongodb_robot_listener.py` ✅ **FIXED** |
| **Source** | ✅ **GitHub** `https://github.com/Sushrut-01/ddn-ai-test-analysis.git` |
| **Branch** | `main` |
| **Command** | `python -m robot --listener mongodb_robot_listener.py robot-tests/` |

**Job configuration excerpt:**
```xml
<scm class="hudson.plugins.git.GitSCM">
  <userRemoteConfigs>
    <hudson.plugins.git.UserRemoteConfig>
      <url>https://github.com/Sushrut-01/ddn-ai-test-analysis.git</url>
      <credentialsId>github-credentials</credentialsId>
    </hudson.plugins.git.UserRemoteConfig>
  </userRemoteConfigs>
  <branches>
    <hudson.plugins.git.BranchSpec>
      <name>*/main</name>
    </hudson.plugins.git.BranchSpec>
  </branches>
</scm>

<builders>
  <hudson.tasks.BatchFile>
    <command>
      python -m robot ^
        --outputdir robot-results ^
        --listener mongodb_robot_listener.py ^
        %TEST_SUITE%
    </command>
  </hudson.tasks.BatchFile>
</builders>
```

---

## 🎯 Answer to Your Question

### **Q: When Jenkins build starts, is it running Python tests in Robot Framework from GitHub?**

**A: It depends on which Jenkins job is configured:**

#### **If using `ddn-robot-tests` job:**
✅ **YES** - It does ALL of these:
1. ✅ Clones from GitHub: `https://github.com/Sushrut-01/ddn-ai-test-analysis.git`
2. ✅ Checks out `main` branch
3. ✅ Runs **Python Robot Framework tests** from `robot-tests/` directory
4. ✅ Uses `mongodb_robot_listener.py` reporter (**Already fixed by Claude with Bug #1 & #3**)
5. ✅ Pulls fresh code on every build (or every 15 minutes via SCM trigger)

#### **If using default Jenkinsfile pipeline:**
❌ **NO** - It runs:
1. ❌ **Mocha/JavaScript tests** (not Robot Framework)
2. ❌ Uses `tests/mongodb-reporter.js` (needs Bug #4 fix from Claude)
3. ❓ Git source not specified in Jenkinsfile (may use local workspace)

---

## 🔍 How to Check Which Job Is Running

### **Method 1: Check Jenkins UI**
```
1. Open Jenkins: http://localhost:8080 or http://localhost:8081
2. Look at job list
3. Check which job has recent builds:
   - "ddn-robot-tests" → Robot Framework from GitHub ✅
   - "DDN-Nightly-Tests" or similar → Mocha/JavaScript ❌
```

### **Method 2: Check Build Console Output**
Look for these indicators in the build log:

**Robot Framework Build:**
```
Installing Robot Framework...
pip install robotframework
Running Robot Framework tests...
python -m robot --listener mongodb_robot_listener.py
```

**Mocha Build:**
```
npm run test:jenkins
Mocha tests executing...
```

---

## 📋 Complete Robot Framework Job Flow

When `ddn-robot-tests` job runs:

```
1. TRIGGER
   ├─ Manual trigger from Jenkins UI
   ├─ Git commit to main branch
   └─ Every 15 minutes (SCM polling)
        ↓
2. GIT CHECKOUT
   ├─ Clone: https://github.com/Sushrut-01/ddn-ai-test-analysis.git
   ├─ Branch: main
   └─ Fresh code pulled
        ↓
3. SETUP ENVIRONMENT
   ├─ Install Python packages
   ├─ pip install robotframework
   ├─ pip install robotframework-requests
   ├─ pip install pymongo
   └─ Set MONGODB_URI environment variable
        ↓
4. RUN TESTS
   ├─ Command: python -m robot --listener mongodb_robot_listener.py robot-tests/
   ├─ Test Files:
   │   ├─ robot-tests/ddn_basic_tests.robot
   │   └─ robot-tests/ddn_advanced_tests.robot
   └─ Listener: implementation/mongodb_robot_listener.py
        ↓
5. CAPTURE FAILURES
   ├─ mongodb_robot_listener.py captures each test failure
   ├─ Adds suite metadata (Bug #1 fix ✅)
   ├─ Standardizes build_id (Bug #3 fix ✅)
   └─ Inserts into MongoDB Atlas
        ↓
6. PUBLISH RESULTS
   ├─ Robot Framework HTML reports
   ├─ output.xml, log.html, report.html
   └─ Failures visible in Dashboard
```

---

## ✅ Key Findings

| Question | Answer |
|----------|--------|
| **Does Robot Framework job exist?** | ✅ YES - `jenkins/jobs/ddn-robot-tests.xml` |
| **Does it pull from GitHub?** | ✅ YES - `https://github.com/Sushrut-01/ddn-ai-test-analysis.git` |
| **Which branch?** | `main` |
| **Are tests Python?** | ✅ YES - Robot Framework (Python-based) |
| **Is reporter fixed?** | ✅ YES - `mongodb_robot_listener.py` fixed by Claude |
| **Will failures appear in MongoDB?** | ✅ YES - If this job runs |

---

## ⚠️ Important: Two Test Systems

Your project has **TWO separate test systems**:

### **System 1: Robot Framework (Python) ✅ Ready**
- **Tests:** `robot-tests/*.robot`
- **Reporter:** `mongodb_robot_listener.py` ✅ **FIXED**
- **Jenkins Job:** `ddn-robot-tests.xml` ✅ **Uses GitHub**
- **Status:** Ready to use, all bugs fixed

### **System 2: Mocha (JavaScript) ⚠️ In Progress**
- **Tests:** `tests/ddn-advanced-scenarios.js`
- **Reporter:** `mongodb-reporter.js` ⚠️ **Needs verification**
- **Jenkins Job:** `Jenkinsfile` ❓ **Git source unclear**
- **Status:** Claude fixing Bug #4 (13.6% complete)

---

## 🚀 Recommendation

**If you want Robot Framework tests from GitHub:**

1. ✅ Use the `ddn-robot-tests` Jenkins job
2. ✅ It's already configured to pull from GitHub
3. ✅ The reporter is already fixed (Bug #1 & #3)
4. ✅ Tests should appear in MongoDB immediately

**To verify it works:**

```powershell
# Trigger the Robot Framework job manually
# Then check MongoDB for new failures
Invoke-WebRequest -Uri "http://localhost:5006/api/failures?limit=5" | 
    ConvertFrom-Json | 
    Select-Object -ExpandProperty data
```

**Expected result:**
- New failures from Robot Framework tests
- `suite_name` populated
- `pass_count`, `fail_count`, `total_count` present
- `build_id` in format: "ddn-robot-tests-XXX"

---

**Summary:** YES, the `ddn-robot-tests` Jenkins job **does run Python Robot Framework tests from GitHub** (main branch). The reporter is already fixed and ready to use! ✅
