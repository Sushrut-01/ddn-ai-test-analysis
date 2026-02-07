# Quick Fix Guide for Test Team

**Estimated Time:** 10 minutes
**File to Edit:** `resources/libraries.robot`
**Repository:** https://github.com/Sushrut-01/gurutattva-e2e-automation
**Branch:** Sushrut-laptop

---

## The Problem

Jenkins builds are failing because the `Web Open Browser` keyword doesn't pass Docker-required Chrome options to SeleniumLibrary.

**Error in builds:** Chrome crashes or sessions fail to start

---

## The Solution (8 Lines)

### Find this code (around line 210 in resources/libraries.robot):

```robot
Web Open Browser
    [Arguments]    ${url}    ${browser}=chrome    ${alias}=${EMPTY}    ${remote_url}=${EMPTY}    &{kwargs}
    Web.Open Browser    ${url}    ${browser}    ${alias}    ${remote_url}    &{kwargs}
```

### Replace with this code:

```robot
Web Open Browser
    [Arguments]    ${url}    ${browser}=chrome    ${alias}=${EMPTY}    ${remote_url}=${EMPTY}    &{kwargs}

    # Docker Chrome options for Jenkins CI/CD
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    Call Method    ${chrome_options}    add_argument    --no-sandbox
    Call Method    ${chrome_options}    add_argument    --disable-dev-shm-usage
    Call Method    ${chrome_options}    add_argument    --disable-gpu
    Call Method    ${chrome_options}    add_argument    --remote-debugging-port=9222
    Call Method    ${chrome_options}    add_argument    --user-data-dir=/tmp/chrome-user-data
    Call Method    ${chrome_options}    add_argument    --single-process
    Call Method    ${chrome_options}    add_argument    --headless

    Web.Open Browser    ${url}    ${browser}    ${alias}    ${remote_url}    options=${chrome_options}    &{kwargs}
```

---

## Step-by-Step Instructions

### 1. Clone the repository (if not already cloned):
```bash
git clone -b Sushrut-laptop https://github.com/Sushrut-01/gurutattva-e2e-automation
cd gurutattva-e2e-automation
```

### 2. Open the file:
```bash
# Use your preferred editor
notepad resources/libraries.robot
# OR
code resources/libraries.robot
# OR
vim resources/libraries.robot
```

### 3. Find the `Web Open Browser` keyword:
- Press Ctrl+F (or `/` in vim)
- Search for: `Web Open Browser`
- Find the one with `[Arguments]` on the next line (around line 210)

### 4. Replace the code:
- Delete the current implementation (3 lines)
- Paste the new implementation (14 lines) from above

### 5. Save the file:
- Ctrl+S (or `:wq` in vim)

### 6. Commit and push:
```bash
git add resources/libraries.robot
git commit -m "fix: add Docker Chrome options to Web Open Browser for Jenkins CI/CD"
git push origin Sushrut-laptop
```

### 7. Trigger Jenkins build:
- Go to: http://localhost:8080/job/Guruttava-E2E-Tests/
- Click "Build with Parameters"
- Select your desired platform and test type
- Click "Build"

---

## What This Fix Does

**Before:** SeleniumLibrary opens Chrome without any special options → Chrome crashes in Docker

**After:** SeleniumLibrary opens Chrome with Docker-required options → Chrome works perfectly

---

## Example from Same File

If you want to see a similar pattern, look at the `Web Open Browser With Custom Download Path` keyword in the same file. It already uses this pattern:

```robot
${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
# ... adds options ...
Web.Open Browser    ${url}    ${browser}    options=${chrome_options}
```

We're just applying the same pattern to `Web Open Browser`.

---

## Verification

After triggering the Jenkins build, check the console output. You should see:

```
🌐 Opening web browser: chrome
🔗 Navigating to: https://gurutattvacmsnewdev.rysun.in:9090/
✅ Web browser opened successfully
```

Instead of:

```
❌ SessionNotCreatedException: Chrome instance exited
❌ Chrome failed to start: crashed
```

---

## Troubleshooting

### If build still fails after fix:

**1. Check if git pulled your changes:**
```bash
# In Jenkins console output, look for:
# Git Branch: Sushrut-laptop | Commit: <your-commit-hash>
```

**2. Verify the fix is in the workspace:**
```bash
docker exec ddn-jenkins cat /var/jenkins_home/workspace/Guruttava-E2E-Tests/resources/libraries.robot | grep -A 15 "Web Open Browser"
```

**3. Check if there are multiple `Web Open Browser` keywords:**
- Make sure you edited the right one (the one WITHOUT "Custom Download Path" in the name)

**4. Check for syntax errors:**
- Robot Framework is indentation-sensitive
- Use 4 spaces (not tabs)
- Make sure arguments line up correctly

---

## Why Is This Needed?

Jenkins runs tests in a Docker container. Docker containers have security restrictions that require Chrome to run with specific flags:

- `--no-sandbox`: Disable Chrome's sandbox (required in containers)
- `--disable-dev-shm-usage`: Don't use /dev/shm (limited in containers)
- `--remote-debugging-port=9222`: Enable remote debugging (required in Docker)
- `--user-data-dir=/tmp/chrome-user-data`: Explicit temp directory
- `--single-process`: Run Chrome in single process mode (container optimization)

Without these flags, Chrome crashes immediately.

**Jenkins infrastructure already has these configured**, but they need to be **passed to SeleniumLibrary** through the `options=` parameter. That's what this fix does.

---

## Need Help?

See the comprehensive documentation in: `JENKINS_INFRASTRUCTURE_COMPLETE_HANDOFF.md`

---

**Created:** 2026-01-18
**Status:** Jenkins infrastructure ready, awaiting test code fix
**Estimated Impact:** Fixes all Chrome-related build failures
