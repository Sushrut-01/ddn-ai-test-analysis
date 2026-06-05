# 📦 How to Build APK for DDN AI Mobile App

This guide will help you build an installable APK file for your Android device.

---

## Prerequisites

### 1. Install Flutter

**If you don't have Flutter installed:**

**Windows:**
```bash
# Download Flutter SDK
# Go to: https://docs.flutter.dev/get-started/install/windows
# Download flutter_windows_3.16.0-stable.zip (or latest)

# Extract to C:\flutter

# Add to PATH:
# Control Panel → System → Advanced → Environment Variables
# Edit PATH variable, add: C:\flutter\bin

# Verify installation:
flutter doctor
```

**Mac:**
```bash
# Download Flutter SDK
# Go to: https://docs.flutter.dev/get-started/install/macos

# Extract and add to PATH:
export PATH="$PATH:`pwd`/flutter/bin"

# Verify:
flutter doctor
```

**Linux:**
```bash
# Download Flutter SDK
# Go to: https://docs.flutter.dev/get-started/install/linux

# Extract and add to PATH:
export PATH="$PATH:/path/to/flutter/bin"

# Verify:
flutter doctor
```

### 2. Install Android SDK

Flutter will prompt you to install Android SDK if not already installed:

```bash
flutter doctor
```

Follow the instructions to install:
- Android SDK
- Android SDK Command-line Tools
- Android SDK Platform-Tools
- Android licenses (run `flutter doctor --android-licenses`)

---

## Build APK - Automated Method

### Windows

I've created a build script for you. Simply double-click:

```
build_apk.bat
```

This will:
1. ✅ Check Flutter installation
2. ✅ Get dependencies
3. ✅ Run code generation
4. ✅ Build release APK
5. ✅ Show APK location

**APK will be at:** `build\app\outputs\flutter-apk\app-release.apk`

### Mac/Linux

Run the following commands:

```bash
cd ddn_ai_mobile

# Get dependencies
flutter pub get

# Generate code (Freezed, Retrofit, etc.)
flutter pub run build_runner build --delete-conflicting-outputs

# Build APK
flutter build apk --release
```

**APK will be at:** `build/app/outputs/flutter-apk/app-release.apk`

---

## Build APK - Manual Steps

### Step 1: Install Dependencies

```bash
cd C:\DDN-AI-Project-Documentation\ddn_ai_mobile
flutter pub get
```

### Step 2: Run Code Generation

This generates all the required code for Freezed models, Retrofit APIs, etc.

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**Expected output:**
```
[INFO] Generating build script completed, took 412ms
[INFO] Reading cached asset graph completed, took 156ms
[INFO] Checking for updates since last build completed, took 845ms
[INFO] Running build completed, took 12.4s
[INFO] Caching finalized dependency graph completed, took 89ms
[INFO] Succeeded after 13.9s with 234 outputs
```

### Step 3: Build Release APK

```bash
flutter build apk --release
```

**This will take 5-10 minutes on first build.**

**Expected output:**
```
Running Gradle task 'assembleRelease'...
✓ Built build\app\outputs\flutter-apk\app-release.apk (18.5MB)
```

### Step 4: Locate APK

Your APK is at:
```
build\app\outputs\flutter-apk\app-release.apk
```

File size: ~15-20 MB

---

## Install APK on Your Phone

### Method 1: USB Transfer

1. Connect phone to computer via USB
2. Copy `app-release.apk` to phone's Download folder
3. On phone, open **Files** app → **Downloads**
4. Tap `app-release.apk`
5. Tap **Install**
6. If prompted, enable "Install from unknown sources"

### Method 2: Email/Cloud

1. Email the APK to yourself (some email providers block APKs)
2. Or upload to Google Drive/Dropbox
3. Download on your phone
4. Install from Downloads

### Method 3: ADB Install

If you have ADB installed:

```bash
adb install build\app\outputs\flutter-apk\app-release.apk
```

---

## Troubleshooting

### Error: "Flutter command not found"

**Solution:**
- Install Flutter SDK
- Add Flutter to PATH environment variable
- Restart terminal/command prompt
- Run `flutter doctor`

### Error: "Android SDK not found"

**Solution:**
```bash
flutter doctor --android-licenses
```

Accept all licenses with `y`.

### Error: "Gradle build failed"

**Solution:**
```bash
cd android
gradlew clean
cd ..
flutter clean
flutter pub get
flutter build apk --release
```

### Error: "Build runner failed"

**Solution:**
```bash
flutter pub get
flutter clean
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

### Error: "Out of memory"

**Solution:**

Edit `android/gradle.properties`, add:
```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=1024m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
```

Then rebuild.

### Build Takes Too Long

**Normal build times:**
- First build: 5-10 minutes
- Subsequent builds: 2-3 minutes

**Tips to speed up:**
- Close other applications
- Use SSD (not HDD)
- Increase RAM allocation in gradle.properties

---

## APK Variants

### Release APK (Default)
```bash
flutter build apk --release
```
- Optimized for production
- Smaller size (~15-20 MB)
- No debugging info
- **Use this for distribution**

### Debug APK
```bash
flutter build apk --debug
```
- Larger size (~40-50 MB)
- Includes debugging info
- Slower performance
- Only use for testing

### Split APKs (by ABI)
```bash
flutter build apk --split-per-abi
```
- Creates 3 APKs: arm64-v8a, armeabi-v7a, x86_64
- Smaller individual file sizes (~10 MB each)
- Install the correct one for your device

---

## App Bundle (For Google Play)

If you want to publish to Google Play Store:

```bash
flutter build appbundle --release
```

Creates: `build/app/outputs/bundle/release/app-release.aab`

Upload this `.aab` file to Google Play Console.

---

## Verify Build

After building, check the APK:

```bash
# Check APK size
dir build\app\outputs\flutter-apk\app-release.apk

# Analyze APK contents (requires Android SDK)
bundletool build-apks --bundle=build\app\outputs\bundle\release\app-release.aab --output=build\app.apks
```

---

## Next Steps After Building APK

1. **Transfer APK** to your phone
2. **Install** the APK
3. **Ensure backend is running:**
   ```bash
   # Dashboard API should be running on port 5006
   curl http://192.168.1.7:5006/api/system/status

   # Manual Trigger API on port 5004
   curl http://192.168.1.7:5004/api/health
   ```
4. **Connect to same WiFi** - Phone and computer must be on same network
5. **Allow firewall access** to ports 5006, 5004
6. **Open app** and login (any email/password works - mock auth)
7. **Test features:**
   - Dashboard - System status and stats
   - Failures - List of failures
   - Chat - AI chatbot
   - Analytics - Charts dashboard
   - More - RAG approval, Settings

---

## Build Configuration

Your app is configured to connect to:

- **Computer IP:** `192.168.1.7` (automatically configured)
- **Dashboard API:** `http://192.168.1.7:5006/api`
- **Manual Trigger API:** `http://192.168.1.7:5004/api`

If your computer's IP changes, update `lib/core/constants/api_endpoints.dart`:

```dart
static const String _computerIp = '192.168.1.7'; // Change this
```

Then rebuild the APK.

---

## Summary

**Quick build command:**
```bash
flutter pub get && flutter pub run build_runner build --delete-conflicting-outputs && flutter build apk --release
```

**APK location:**
```
build\app\outputs\flutter-apk\app-release.apk
```

**Install on phone:**
1. Copy APK to phone
2. Open and install
3. Enable "Unknown sources" if needed

**Ready to test!** 🚀

---

For detailed installation instructions, see: `INSTALL_ON_DEVICE.md`
