# ✅ Guruttava Jenkins Job - Updated with Real Device Configuration

**Date**: 2026-01-16
**Status**: ✅ Configuration updated from repository settings

---

## 🔍 Configuration Source

All configuration pulled from: **https://github.com/Sushrut-01/gurutattva-e2e-automation**

### Files Analyzed:
1. `resources/variables.robot` - Main device configuration
2. `appium_inspector_config.json` - Appium device settings

---

## 📱 Real Device Configuration

### Updated Jenkins Parameters:

| Parameter | Old Value (Wrong) | New Value (Correct) | Source |
|-----------|------------------|---------------------|---------|
| **DEVICE_NAME** | `emulator-5554` | `RZCT40WL69K` | variables.robot:73 |
| **APP_PACKAGE** | `apps/guruttava.apk` | `com.org.gurutattva.app` | variables.robot:74 |
| **APP_ACTIVITY** | N/A | `com.example.gurutattva_flutter_app.MainActivity` | variables.robot:75 |

### Device Details from Repository:

```robot
# From resources/variables.robot (lines 71-77)
${PLATFORM_NAME}     Android
${DEVICE_NAME}       RZCT40WL69K          # ← Real device, NOT emulator
${APP_PACKAGE}       com.org.gurutattva.app
${APP_ACTIVITY}      com.example.gurutattva_flutter_app.MainActivity
${AUTOMATION_NAME}   UiAutomator2
```

### Appium Configuration:

```json
{
  "appium:deviceName": "RZCT40WL69K",
  "appium:appPackage": "com.org.gurutattva.app",
  "appium:appActivity": "com.example.gurutattva_flutter_app.MainActivity",
  "appium:noReset": true,               # ← App already installed
  "appium:systemPort": 8210
}
```

---

## 🎯 Jenkins Job Parameters (After Update)

### Parameter 1: PLATFORM
- **Type**: Choice
- **Choices**: All, Android, iOS, Web
- **Default**: All
- **Description**: Select platform to test (All = runs ALL suites sequentially)

### Parameter 2: TEST_TYPE
- **Type**: Choice
- **Choices**: All, Smoke, Regression, Sanity
- **Default**: All
- **Description**: Select test type

### Parameter 3: DEVICE_NAME
- **Type**: String
- **Default**: `RZCT40WL69K` ✅ (Updated from emulator-5554)
- **Description**: Real Android device connected via USB (RZCT40WL69K)

### Parameter 4: APP_PACKAGE
- **Type**: String
- **Default**: `com.org.gurutattva.app` ✅ (Updated from apps/guruttava.apk)
- **Description**: App package name (app already installed with noReset=true)

---

## 📋 Key Configuration Notes

### 1. **Real Device Connection**
- Device: **RZCT40WL69K** (physical Android device)
- Connection: USB
- ADB should recognize: `adb devices` should show `RZCT40WL69K`

### 2. **App Installation**
- **noReset: true** means app is already installed
- No need to install APK during test execution
- App data persists between test runs
- Package: `com.org.gurutattva.app`

### 3. **System Port**
- Default: `8210` (from appium_inspector_config.json)
- Alternative: `8202` (from variables.robot)
- Should be unique per device if running parallel tests

### 4. **Critical Stability Settings** (from variables.robot:79-96)
```robot
${NO_RESET}                         true        # Don't uninstall app
${AUTO_RESET_ENABLED}               ${False}    # Don't reset app state
${SKIP_SERVER_INSTALLATION}         ${True}     # Don't reinstall UIAutomator2
${AUTO_GRANT_PERMISSIONS}           ${True}     # Auto-grant app permissions
${DONT_STOP_APP_ON_RESET}           ${True}     # Keep app running
${NEW_COMMAND_TIMEOUT}              600000      # 10 minutes
${SYSTEM_PORT}                      8202
${CONNECT_HARDWARE_KEYBOARD}        ${True}
```

---

## 🚀 Testing the Updated Job

### Step 1: Verify Device Connection
```bash
# Check if device is connected
adb devices

# Expected output:
# RZCT40WL69K    device
```

### Step 2: Verify App Installation
```bash
# Check if Guruttava app is installed
adb -s RZCT40WL69K shell pm list packages | grep gurutattva

# Expected output:
# package:com.org.gurutattva.app
```

### Step 3: Run Jenkins Job

1. Go to: http://localhost:8081/job/Guruttava-E2E-All-Suites/

2. Click **"Build with Parameters"**

3. Parameters will show:
   - **PLATFORM**: `All` (default)
   - **TEST_TYPE**: `All` (default)
   - **DEVICE_NAME**: `RZCT40WL69K` ✅ (updated!)
   - **APP_PACKAGE**: `com.org.gurutattva.app` ✅ (updated!)

4. Click **"Build"**

5. Watch Console Output for:
   ```
   ✅ Connecting to device RZCT40WL69K
   ✅ Starting session with com.org.gurutattva.app
   ✅ Running tests with PROJECT_ID=2
   ```

---

## 🔧 Troubleshooting

### If Device Not Found:
```bash
# 1. Check USB connection
adb devices

# 2. Restart ADB
adb kill-server
adb start-server

# 3. Enable USB debugging on device
# Settings → Developer Options → USB Debugging
```

### If App Not Found:
```bash
# Verify app package name
adb -s RZCT40WL69K shell pm list packages -f | grep gurutattva

# Should show:
# package:/data/app/.../com.org.gurutattva.app
```

### If Appium Connection Fails:
```bash
# Check Appium server is running
docker ps | grep appium

# Or verify Appium status
curl http://localhost:4723/status
```

---

## ✅ Configuration Update Summary

### Changes Made:
1. ✅ Updated `DEVICE_NAME` parameter: `emulator-5554` → `RZCT40WL69K`
2. ✅ Updated `APP_PATH` parameter → `APP_PACKAGE`: `com.org.gurutattva.app`
3. ✅ Updated parameter descriptions to reflect real device usage
4. ✅ Configuration matches actual repository settings

### Files Updated:
- `jenkins-jobs/Guruttava-Pipeline-Final.xml` (local)
- `/var/jenkins_home/jobs/Guruttava-E2E-All-Suites/config.xml` (Jenkins container)

### Jenkins Status:
- ✅ Job updated and restarted
- ✅ Configuration loaded from repository
- ✅ Ready to run with real device

---

## 📊 Multi-Project Architecture (Unchanged)

| Setting | Value |
|---------|-------|
| **Project ID** | 2 |
| **Project Slug** | guruttava |
| **Jira Project** | GURU |
| **MongoDB Collections** | guruttava_* |
| **Pinecone Namespace** | guruttava |
| **PostgreSQL Filter** | project_id=2 |

---

**Status**: ✅ Ready to test with real device RZCT40WL69K!
**Next Step**: Build with Parameters and run your first test!
