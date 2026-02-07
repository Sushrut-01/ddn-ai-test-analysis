# 🔧 Jenkins Python Installation Fix

**Issue**: Guruttava build failed with "python3: command not found"
**Cause**: Jenkins container doesn't have Python installed by default
**Solution**: Installing Python 3, pip, and git in Jenkins container
**Status**: ⏳ Installation in progress...

---

## 🚨 The Problem

### Build Failure Details:

**Build**: #1
**Result**: FAILURE
**Duration**: 63 seconds
**Exit Code**: 127 (command not found)

### Console Output Errors:

```bash
/tmp/jenkins9920208797907742296.sh: line 33: python3: command not found
/tmp/jenkins9920208797907742296.sh: line 34: python3: command not found
/tmp/jenkins9920208797907742296.sh: line 66: python3: command not found
Robot Framework exit code: 127
```

### What Worked:

✅ Git clone from Sushrut-laptop branch succeeded
✅ PROJECT_ID=2 and PROJECT_SLUG=guruttava set correctly
✅ Job configuration is correct
✅ Repository access works

### What Failed:

❌ Python 3 not found in Jenkins container
❌ Unable to install Robot Framework
❌ Unable to run tests
❌ Unable to run parser script

---

## ✅ The Solution

### Installing Python in Jenkins Container:

```bash
# Run as root to install packages
docker exec -u root ddn-jenkins bash -c "apt-get update && apt-get install -y python3 python3-pip git"
```

### What's Being Installed:

1. **Python 3.13** - Latest Python version
2. **pip** - Python package manager
3. **git** - Already present, but ensuring it's available
4. **Build tools** - Compilers and development libraries
5. **Dependencies** - All required libraries for Python development

### Installation Progress:

```
Get:1 http://deb.debian.org/debian trixie InRelease [140 kB]
Get:2 http://deb.debian.org/debian trixie-updates InRelease [47.3 kB]
...
Reading package lists...
Building dependency tree...
The following NEW packages will be installed:
  python3 python3-pip python3-minimal python3-dev python3.13
  build-essential gcc g++ make binutils
  (+ 70 more packages)
```

**Total Download**: ~99 MB
**Disk Space Required**: ~364 MB
**Estimated Time**: 2-5 minutes

---

## 🔄 After Installation Completes

### Step 1: Verify Python Installation

```bash
# Check Python is available
docker exec ddn-jenkins bash -c "python3 --version"
# Expected: Python 3.13.5

# Check pip is available
docker exec ddn-jenkins bash -c "pip3 --version"
# Expected: pip 24.x from /usr/lib/python3.13/...

# Check git is available
docker exec ddn-jenkins bash -c "git --version"
# Expected: git version 2.x.x
```

### Step 2: Rebuild Guruttava Job

**Option A: From Jenkins UI**
```
1. Go to: http://localhost:8081/job/Guruttava-E2E-Tests/
2. Click: "Build with Parameters"
3. Select:
   - PLATFORM: Android
   - TEST_TYPE: Smoke
   - SEND_NOTIFICATIONS: ✓
4. Click: "Build"
```

**Option B: Using curl**
```bash
curl -X POST "http://localhost:8081/job/Guruttava-E2E-Tests/buildWithParameters?PLATFORM=Android&TEST_TYPE=Smoke&SEND_NOTIFICATIONS=true"
```

### Step 3: Monitor New Build

This time you should see:

```bash
=========================================
Guruttava E2E Tests (Robot Framework)
Build: 2
...
=========================================
Project ID: 2 | Slug: guruttava
Checking out code from https://github.com/Sushrut-01/gurutattva-e2e-automation (branch: Sushrut-laptop)...
Git Branch: Sushrut-laptop | Commit: 2d288d7...
Installing Robot Framework and dependencies...
Collecting robotframework                         ← SUCCESS!
  Downloading robotframework-7.x.x.tar.gz
Successfully installed robotframework-7.x.x       ← SUCCESS!
Running Android tests from: tests/mobile/android/
Executing Robot Framework tests...
==============================================================================
Guruttava Android Tests                           ← TESTS RUNNING!
==============================================================================
Test 1 ... PASS/FAIL
Test 2 ... PASS/FAIL
...
Parsing test results and uploading to platform...
Triggering AI analysis for failures...
=========================================
Guruttava Tests completed!
Platform: Android
Results uploaded to project_id: 2
=========================================
```

---

## 🎯 Why Did This Happen?

### DDN Jobs vs Guruttava Job

**Question**: "Why did DDN jobs work but Guruttava doesn't?"

**Possible Reasons**:

1. **DDN jobs created earlier**: Python might have been installed manually before
2. **Different job configuration**: DDN jobs might use a different approach
3. **Jenkins image changed**: Jenkins container was rebuilt without Python

### Checking DDN Job Execution:

```bash
# Trigger a DDN job and check console
curl -X POST "http://localhost:8081/job/DDN-Basic-Tests/build?delay=0sec"

# Wait 30 seconds, then check console
curl -s "http://localhost:8081/job/DDN-Basic-Tests/lastBuild/consoleText" | grep python3
```

---

## 📋 Permanent Fix Options

### Option 1: Custom Jenkins Image (Recommended)

Create a Dockerfile with Python pre-installed:

**File**: `jenkins/Dockerfile`

```dockerfile
FROM jenkins/jenkins:lts

USER root

# Install Python, pip, git
RUN apt-get update && \
    apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install common Python packages for testing
RUN pip3 install --no-cache-dir \
    robotframework \
    robotframework-appiumlibrary \
    robotframework-seleniumlibrary \
    pymongo \
    python-dotenv \
    boto3 \
    requests

USER jenkins
```

**Build and use custom image:**

```bash
# Build custom Jenkins image
docker build -t jenkins-with-python:lts ./jenkins/

# Update docker-compose-unified.yml
# Change: image: jenkins/jenkins:lts
# To:     image: jenkins-with-python:lts

# Restart Jenkins
docker-compose up -d jenkins
```

### Option 2: Initialization Script

Create a Jenkins init script:

**File**: `jenkins-init.groovy`

```groovy
import jenkins.model.*

def instance = Jenkins.getInstance()

// Run Python installation on startup
def installPython = """
apt-get update
apt-get install -y python3 python3-pip git
pip3 install robotframework pymongo python-dotenv boto3 requests
""".execute()

installPython.waitFor()
println "Python installation completed"
```

### Option 3: Manual Installation (Current Approach)

**Pros**:
- Quick fix
- No configuration changes needed
- Works immediately

**Cons**:
- Lost if Jenkins container is recreated
- Must be repeated after updates
- Not automated

---

## 🔍 Verification Steps

After installation completes and rebuild succeeds:

### 1. Check Build Status

```bash
# Get latest build info
curl -s "http://localhost:8081/job/Guruttava-E2E-Tests/lastBuild/api/json" | \
  python3 -c "import sys, json; b = json.load(sys.stdin); \
  print(f'Build: #{b[\"number\"]}\nResult: {b.get(\"result\")}')"

# Expected: Build: #2, Result: SUCCESS (or UNSTABLE if tests failed)
```

### 2. Check MongoDB Data

```javascript
// Connect to MongoDB
mongodb+srv://sushrutnistane097_db_user:...

// Query Guruttava failures
db.guruttava_test_failures.find({project_id: 2}).count()
// Should show > 0 if tests ran
```

### 3. Check PostgreSQL Data

```sql
SELECT COUNT(*) FROM failure_analysis WHERE project_id = 2;
-- Should show > 0 if AI analysis completed
```

### 4. Check Dashboard

```
http://localhost:5173/
→ Select "Guruttava"
→ Should see failures (if any tests failed)
```

---

## 📝 Installation Status

**Command Running**:
```bash
docker exec -u root ddn-jenkins bash -c "apt-get update && apt-get install -y python3 python3-pip git"
```

**Current Progress**:
- ✅ Package lists updated
- ✅ Dependencies resolved
- ⏳ Downloading packages (99 MB)
- ⏳ Installing Python 3.13
- ⏳ Installing pip
- ⏳ Installing build tools
- ⏳ Configuring packages

**Completion ETA**: 2-5 minutes (depending on network speed)

---

## ⚠️ Important Notes

1. **Don't restart Jenkins** during installation - let it complete
2. **Wait for installation** before rebuilding job
3. **Installation is persistent** until container is removed/rebuilt
4. **Consider custom image** for long-term solution

---

## 🎯 Next Steps

1. ✅ Wait for Python installation to complete (in progress)
2. ⏳ Verify Python is available in Jenkins
3. ⏳ Rebuild Guruttava job (Build #2)
4. ⏳ Monitor successful execution
5. ⏳ Verify end-to-end data flow
6. ⏳ Test multi-project isolation
7. ⏳ Document permanent fix (custom Jenkins image)

---

**Installation will complete shortly, then we can rebuild and test successfully!** ⏰
