# Robot Framework Setup Guide for Jenkins

**Date:** 2025-10-24

---

## Overview

This guide explains how to configure Jenkins to run **Robot Framework** tests from your GitHub repository and automatically send failures to MongoDB.

---

## Current Problem

Your Jenkins jobs are configured for **Node.js tests** (npm), but you need **Robot Framework Python tests**:

```
❌ Current: npm ci → npm run test:basic
✅ Needed:  pip install robotframework → robot tests/
```

---

## Solution: Robot Framework Jenkins Job

### 1. Jenkins Job Configuration

Created: `jenkins/jobs/ddn-robot-tests.xml`

This job will:
1. Clone your GitHub repository
2. Install Robot Framework and dependencies
3. Run .robot test files
4. Send failures to MongoDB automatically
5. Generate Robot Framework reports

### 2. Robot Framework MongoDB Listener

Created: `implementation/mongodb_robot_listener.py`

This listener:
- Hooks into Robot Framework test execution
- Captures test failures in real-time
- Sends them to MongoDB Atlas
- Includes test metadata (suite, tags, duration)

---

## Installation Steps

### Step 1: Install Jenkins Plugins

You need the **Robot Framework Plugin** for Jenkins:

1. Open Jenkins: `http://localhost:8081`
2. Go to **Manage Jenkins** → **Manage Plugins**
3. Click **Available** tab
4. Search for: **"Robot Framework"**
5. Install: **Robot Framework Plugin**
6. Restart Jenkins

### Step 2: Install Python Dependencies

On your Jenkins server (Windows machine), install Robot Framework:

```batch
REM Install Robot Framework
pip install robotframework

REM Install common Robot Framework libraries
pip install robotframework-requests
pip install robotframework-seleniumlibrary
pip install robotframework-databaselibrary
pip install robotframework-sshlibrary

REM Install MongoDB support
pip install pymongo
pip install python-dotenv
```

### Step 3: Import Jenkins Job

1. Copy `mongodb_robot_listener.py` to your GitHub repo
2. Open Jenkins: `http://localhost:8081`
3. Click **New Item**
4. Name: `DDN-Robot-Tests`
5. Select: **Pipeline** or **Freestyle Project**
6. Click **OK**
7. Paste the configuration from `ddn-robot-tests.xml`

Or use Jenkins CLI:
```batch
java -jar jenkins-cli.jar -s http://localhost:8081/ create-job DDN-Robot-Tests < jenkins\jobs\ddn-robot-tests.xml
```

---

## Robot Framework Test Structure

### Example Test File: `tests/ddn_basic_tests.robot`

```robotframework
*** Settings ***
Documentation    DDN Storage Basic Tests
Library          RequestsLibrary
Library          Collections
Library          String

*** Variables ***
${DDN_URL}       http://localhost:8080
${TIMEOUT}       30s

*** Test Cases ***
Test DDN Storage Connection
    [Documentation]    Verify DDN storage is reachable
    [Tags]             smoke    connection
    Create Session     ddn    ${DDN_URL}
    ${response}=       GET On Session    ddn    /api/health
    Should Be Equal As Numbers    ${response.status_code}    200

Test Domain Creation
    [Documentation]    Test creating a new domain
    [Tags]             domain    critical
    Create Session     ddn    ${DDN_URL}
    ${body}=    Create Dictionary    name=test-domain    tenantId=tenant1
    ${response}=    POST On Session    ddn    /api/domains    json=${body}
    Should Be Equal As Numbers    ${response.status_code}    201
    Dictionary Should Contain Key    ${response.json()}    domainId

Test Invalid Configuration
    [Documentation]    Test error handling for invalid config
    [Tags]             negative    error-handling
    Create Session     ddn    ${DDN_URL}
    ${body}=    Create Dictionary    name=    tenantId=
    Run Keyword And Expect Error    *400*    POST On Session    ddn    /api/domains    json=${body}

*** Keywords ***
Cleanup Test Data
    [Documentation]    Clean up test data after tests
    Delete All Sessions
```

### Directory Structure

```
your-github-repo/
├── tests/
│   ├── ddn_basic_tests.robot
│   ├── ddn_advanced_tests.robot
│   ├── domain_tests.robot
│   └── storage_tests.robot
├── resources/
│   ├── keywords.robot       # Reusable keywords
│   └── variables.robot      # Global variables
├── mongodb_robot_listener.py  # MongoDB listener
├── requirements.txt         # Python dependencies
└── README.md
```

---

## How It Works

### 1. Jenkins Triggers Test Run

```batch
robot --outputdir robot-results ^
      --listener mongodb_robot_listener.py ^
      tests/
```

### 2. Robot Framework Executes Tests

```
Starting test suite: DDN Basic Tests
  Test: Test DDN Storage Connection ... PASS
  Test: Test Domain Creation ... PASS
  Test: Test Invalid Configuration ... FAIL
    Error: getaddrinfo ENOTFOUND emf.ddn.local
```

### 3. MongoDB Listener Captures Failure

```python
{
  "timestamp": "2025-10-24T18:00:00.000Z",
  "test_name": "Test Invalid Configuration",
  "test_suite": "DDN Basic Tests",
  "error_message": "Error: getaddrinfo ENOTFOUND emf.ddn.local",
  "stack_trace": "...",
  "build_number": 5,
  "job_name": "DDN-Robot-Tests",
  "test_type": "robot_framework",
  "tags": ["negative", "error-handling"],
  "status": "failed"
}
```

### 4. AI Analysis Service Processes Failure

```python
# AI analyzes the failure from MongoDB
{
  "classification": "ENVIRONMENT",
  "root_cause": "DNS hostname not resolvable",
  "severity": "HIGH",
  "solution": "Add DNS entry to /etc/hosts",
  "confidence": 0.95,
  "ai_status": "SUCCESS"
}
```

### 5. Dashboard Displays Results

```
✅ Test 1: Storage Connection - PASSED
✅ Test 2: Domain Creation - PASSED
❌ Test 3: Invalid Configuration - FAILED

   AI Analysis:
   - Classification: ENVIRONMENT - DNS
   - Root Cause: DNS hostname not resolvable
   - Solution: Add DNS entry to /etc/hosts
   - Similar Cases: 12 (92% success rate with this fix)

   Robot Framework Script:
   File: tests/ddn_basic_tests.robot
   Line: 25-30
   [Show on GitHub]
```

---

## Environment Variables

The Jenkins job needs these environment variables:

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://sushrutnistane097_db_user:Sharu@051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority
MONGODB_DB=ddn_tests

# Jenkins (set automatically)
BUILD_NUMBER=5
JOB_NAME=DDN-Robot-Tests
WORKSPACE=C:\jenkins\workspace\DDN-Robot-Tests
```

---

## Jenkins Job Features

### Triggers:
- **SCM Polling**: Every 15 minutes (`H/15 * * * *`)
- **Manual**: Click "Build Now"
- **GitHub Webhook**: On push/PR (configure in GitHub)

### Parameters:
- `TEST_SUITE`: Which tests to run (default: all)
- `SEND_NOTIFICATIONS`: Send Teams/Slack notifications

### Outputs:
- **Robot Framework Report**: HTML report with test details
- **MongoDB**: Test failures stored automatically
- **Jenkins Artifacts**: All logs and reports archived

---

## Testing the Setup

### Local Test (Before Jenkins):

```batch
cd your-github-repo

REM Set environment variables
set MONGODB_URI=mongodb+srv://...
set MONGODB_DB=ddn_tests

REM Run Robot Framework with MongoDB listener
python -m robot ^
  --outputdir results ^
  --listener mongodb_robot_listener.py ^
  tests/ddn_basic_tests.robot

REM Check results
start results\report.html
```

### Jenkins Test:

1. Go to: `http://localhost:8081/job/DDN-Robot-Tests/`
2. Click: **Build with Parameters**
3. Set `TEST_SUITE=tests/`
4. Click: **Build**
5. Watch: Console Output
6. Check: MongoDB for new failures

---

## Dashboard Integration

### What Dashboard Will Show:

#### For Each Failure:
1. **Test Details:**
   - Test name from Robot Framework
   - Suite name
   - Tags
   - Timestamp

2. **AI Analysis:**
   - Classification (ENVIRONMENT, CODE, CONFIG, etc.)
   - Root cause
   - Recommended solution
   - Confidence score

3. **Robot Framework Script:**
   - GitHub file link
   - Line numbers
   - Code snippet (BEFORE/AFTER if available)
   - Test keywords used

4. **Similar Past Failures:**
   - From RAG/Pinecone search
   - What solutions worked
   - Success rate

#### Example Dashboard View:

```
╔═══════════════════════════════════════════════════════════════╗
║ Test Failure #146                                             ║
╠═══════════════════════════════════════════════════════════════╣
║ Test: Test Invalid Configuration                              ║
║ Suite: DDN Basic Tests                                        ║
║ Build: #5 (2025-10-24 18:00:00)                              ║
║ Tags: [negative, error-handling]                             ║
╠═══════════════════════════════════════════════════════════════╣
║ 🤖 AI ANALYSIS (Confidence: 95%)                             ║
║ Classification: ENVIRONMENT - DNS Configuration               ║
║ Root Cause: DNS hostname 'emf.ddn.local' not resolvable      ║
║ Severity: HIGH                                                ║
╠═══════════════════════════════════════════════════════════════╣
║ 💡 RECOMMENDED SOLUTION                                       ║
║ 1. Add DNS entry to /etc/hosts:                              ║
║    192.168.1.10 emf.ddn.local                                ║
║ 2. Or update DNS server configuration                        ║
║ 3. Verify with: ping emf.ddn.local                          ║
╠═══════════════════════════════════════════════════════════════╣
║ 📄 ROBOT FRAMEWORK TEST                                       ║
║ File: tests/ddn_basic_tests.robot (Line 25-30)              ║
║ [View on GitHub] [View Full Report]                          ║
╠═══════════════════════════════════════════════════════════════╣
║ 📊 SIMILAR PAST FAILURES (12 found)                          ║
║ ✅ 11 resolved with DNS fix (92% success rate)               ║
║ ⏱️  Average resolution time: 15 minutes                      ║
╚═══════════════════════════════════════════════════════════════╝
```

---

## Next Steps

### 1. Prepare Your GitHub Repository

Add to your repo:
```
your-repo/
├── tests/
│   └── *.robot files
├── mongodb_robot_listener.py  ← Copy from implementation/
├── requirements.txt
└── README.md
```

**requirements.txt:**
```
robotframework>=6.0
robotframework-requests>=0.9.4
robotframework-seleniumlibrary>=6.1.0
robotframework-databaselibrary>=1.2.4
pymongo>=4.5.0
python-dotenv>=1.0.0
```

### 2. Install Jenkins Plugin

- Robot Framework Plugin for Jenkins

### 3. Create Jenkins Job

- Import `ddn-robot-tests.xml`
- Configure GitHub credentials
- Set MongoDB environment variables

### 4. Test Locally First

```batch
python -m robot --listener mongodb_robot_listener.py tests/
```

### 5. Run Jenkins Build

- Trigger test build
- Check MongoDB for failures
- Verify AI analysis runs
- Check dashboard display

---

## Troubleshooting

### Robot Framework Not Found
```batch
pip install robotframework
python -m robot --version
```

### MongoDB Connection Error
- Check `MONGODB_URI` environment variable
- Test connection: `python tests/test-mongodb-connection.js` → Convert to Python

### Tests Not Running
- Check .robot file syntax
- Verify test path in Jenkins job
- Check Jenkins console output

### Listener Not Loading
```batch
REM Test listener directly
python mongodb_robot_listener.py
```

---

## Summary

✅ **Created:** Jenkins job for Robot Framework tests
✅ **Created:** MongoDB listener for automatic failure reporting
✅ **Ready:** AI analysis pipeline
✅ **Ready:** Dashboard integration

**Next:** Share your GitHub repo structure so I can customize the configuration!

---

## Questions for You:

1. **Where are your .robot test files in GitHub?**
   - Path: `tests/`, `robot-tests/`, `test-suites/`?

2. **What Robot Framework libraries do you use?**
   - SeleniumLibrary, RequestsLibrary, DatabaseLibrary, SSHLibrary?

3. **Do you have existing .robot files?**
   - Or should I create example templates?

4. **GitHub Repository Access:**
   - Is it public or private?
   - Do you have GitHub credentials in Jenkins?

Once you answer, I'll:
1. Customize the Jenkins job for your exact repo structure
2. Create example .robot test files if needed
3. Set up GitHub integration for dashboard to show test scripts
4. Implement MCP for intelligent GitHub queries
