# 📱 How to Install and Run DDN AI Mobile App on Your Android Device

This guide will help you install and run the Flutter app on your physical Android device.

---

## Prerequisites

Before you begin, ensure you have:
- ✅ Flutter SDK installed on your computer
- ✅ Android device (Android 5.0 / API 21 or higher)
- ✅ USB cable to connect device to computer
- ✅ Backend services running (Dashboard API on port 5006, Manual Trigger API on port 5004)

---

## Method 1: Run Directly from Computer (USB Debugging)

This is the fastest method for development and testing.

### Step 1: Enable Developer Options on Android Device

1. Open **Settings** on your Android device
2. Scroll down to **About Phone** (or **About Device**)
3. Find **Build Number** (usually at the bottom)
4. **Tap Build Number 7 times** rapidly
5. You'll see a message: "You are now a developer!"

### Step 2: Enable USB Debugging

1. Go back to **Settings**
2. Open **Developer Options** (usually under System > Advanced)
3. Enable **USB Debugging**
4. Enable **Install via USB** (if available)

### Step 3: Connect Device to Computer

1. Connect your Android device to your computer using a USB cable
2. On your device, you'll see a popup: **"Allow USB debugging?"**
3. Check **"Always allow from this computer"**
4. Tap **OK**

### Step 4: Verify Device is Connected

Open a terminal/command prompt and run:

```bash
flutter devices
```

You should see output like:

```
Found 2 devices:
  SM G960F (mobile) • 1234567890ABCDEF • android-arm64 • Android 12 (API 31)
  Chrome (web)      • chrome           • web-javascript • Google Chrome 120.0
```

If your device is listed, you're ready to go!

### Step 5: Update API Endpoint Configuration

**IMPORTANT:** Your device cannot access `localhost` on your computer. You need to use your computer's IP address.

#### Find Your Computer's IP Address:

**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" under your active network adapter (e.g., `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig
```
Look for "inet" under your active network interface (e.g., `192.168.1.100`)

#### Update API Endpoints:

Edit `lib/core/constants/api_endpoints.dart`:

```dart
class ApiEndpoints {
  // Replace 'localhost' with your computer's IP address
  static const String baseUrl = 'http://192.168.1.100:5006'; // Replace with YOUR IP
  static const String dashboardApiUrl = 'http://192.168.1.100:5006/api';
  static const String manualTriggerApiUrl = 'http://192.168.1.100:5004/api';

  // Rest of the file remains the same...
}
```

**Important Notes:**
- Use your actual computer's IP address (e.g., `192.168.1.100`)
- Ensure your Android device and computer are on the **same WiFi network**
- If you have a firewall, allow incoming connections on ports 5006 and 5004

### Step 6: Run Code Generation

```bash
cd ddn_ai_mobile
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

This generates all Freezed models and Retrofit API services.

### Step 7: Run the App

```bash
flutter run
```

Flutter will automatically detect your connected device and install the app. You'll see:

```
Launching lib/main.dart on SM G960F in debug mode...
Running Gradle task 'assembleDebug'...
✓ Built build/app/outputs/flutter-apk/app-debug.apk.
Installing build/app/outputs/flutter-apk/app-debug.apk...
Syncing files to device SM G960F...
Flutter run key commands.
r Hot reload.
R Hot restart.
h List all available interactive commands.
d Detach (terminate "flutter run" but leave application running).
c Clear the screen
q Quit (terminate the application on the device).
```

The app will launch on your device!

---

## Method 2: Build APK and Install Manually

This method creates an installable APK file.

### Step 1: Update API Endpoints

Follow **Step 5** from Method 1 to update API endpoints with your computer's IP address.

### Step 2: Build APK

```bash
cd ddn_ai_mobile
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
flutter build apk --release
```

This creates an APK at: `build/app/outputs/flutter-apk/app-release.apk`

### Step 3: Transfer APK to Device

**Option A: USB Transfer**
1. Connect device via USB
2. Copy `app-release.apk` to your device's Download folder
3. On your device, open **Files** app
4. Navigate to **Downloads**
5. Tap `app-release.apk`
6. Tap **Install**

**Option B: Email/Cloud**
1. Email the APK to yourself
2. Open email on your device
3. Download and install the APK

**Option C: ADB Install**
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Step 4: Allow Unknown Sources (if needed)

If you see "Install blocked", you need to allow app installation from unknown sources:

1. Tap **Settings** in the popup
2. Enable **Allow from this source**
3. Go back and tap **Install** again

---

## Method 3: Build App Bundle for Google Play (Production)

For production deployment to Google Play Store:

```bash
flutter build appbundle --release
```

This creates: `build/app/outputs/bundle/release/app-release.aab`

Upload this to Google Play Console.

---

## Testing the App

### Step 1: Login

When you launch the app, you'll see the login screen.

**Current Authentication:** Mock (accepts any credentials)
- Email: `admin@ddn.ai` (or any email)
- Password: `admin123` (or any password)

Tap **Login** to proceed.

### Step 2: Verify Backend Connection

On the Dashboard screen, you should see:

✅ **System Status Cards** (MongoDB, PostgreSQL, Pinecone, AI Service)
✅ **Stats Grid** (Total Failures, Success Rate, etc.)
✅ **Recent Activity** timeline

If you see "No internet connection" or loading spinners that never finish:
- Check that backend services are running
- Verify you used the correct IP address in api_endpoints.dart
- Ensure device and computer are on the same WiFi network

### Step 3: Test Features

Navigate through the bottom navigation bar:

1. **Dashboard** - System status and stats
2. **Failures** - List of test failures with filters
3. **Chat** - AI chatbot
4. **Analytics** - Charts and analytics dashboard
5. **More** - Settings, RAG Approval Queue, Profile

### Step 4: Test Offline Mode

1. Turn off WiFi on your device
2. Pull to refresh on any screen
3. You should see cached data (last fetched data)
4. Try triggering a manual analysis - it will be queued
5. Turn WiFi back on
6. Pull to refresh - queued actions will sync

---

## Troubleshooting

### Issue 1: Device Not Detected

**Solution:**
```bash
# Check ADB devices
adb devices

# If empty, try:
adb kill-server
adb start-server
adb devices
```

If still not detected:
- Try a different USB cable (some cables are charge-only)
- Try a different USB port
- Reinstall USB drivers (Windows)
- Check USB debugging is enabled

### Issue 2: "No devices found"

**Solution:**
- Ensure USB debugging is enabled
- Accept the "Allow USB debugging" popup on your device
- Run `adb devices` and verify device is listed

### Issue 3: "Gradle build failed"

**Solution:**
```bash
cd android
./gradlew clean
cd ..
flutter clean
flutter pub get
flutter run
```

### Issue 4: "Error connecting to the service protocol"

**Solution:**
- Restart the app
- Disconnect and reconnect USB cable
- Run `flutter doctor` to check for issues

### Issue 5: Cannot Connect to Backend

**Symptoms:**
- Loading spinners never finish
- "Network error" messages
- Empty data screens

**Solution:**

1. **Verify Backend is Running:**
   ```bash
   # Check Dashboard API
   curl http://localhost:5006/api/system/status

   # Check Manual Trigger API
   curl http://localhost:5004/api/health
   ```

2. **Verify IP Address:**
   - Ensure you updated `api_endpoints.dart` with your computer's IP
   - Test from device browser: `http://192.168.1.100:5006/api/system/status`
   - If it doesn't load, there's a network issue

3. **Check Firewall:**
   - Windows: Allow ports 5006 and 5004 in Windows Firewall
   - Mac: System Preferences > Security & Privacy > Firewall Options
   - Linux: `sudo ufw allow 5006` and `sudo ufw allow 5004`

4. **Check Same WiFi Network:**
   - Ensure device and computer are on the same WiFi network
   - Corporate networks may block device-to-device communication

### Issue 6: "Install blocked" when installing APK

**Solution:**
1. Go to Settings > Security
2. Enable "Unknown sources" or "Install unknown apps"
3. Allow installation from the source (Files app, Chrome, etc.)

### Issue 7: App Crashes on Startup

**Solution:**
1. Check logs:
   ```bash
   adb logcat | grep flutter
   ```
2. Common causes:
   - Missing code generation (run `flutter pub run build_runner build`)
   - Network issues (check API endpoints)
   - Missing dependencies (run `flutter pub get`)

---

## Hot Reload During Development

While the app is running on your device (Method 1):

- **Press `r`** in the terminal - Hot reload (preserves app state)
- **Press `R`** in the terminal - Hot restart (resets app state)
- **Press `q`** in the terminal - Quit and stop the app

You can make changes to the code, press `r`, and see changes instantly on your device!

---

## Network Configuration Summary

**For Development (USB Debugging):**
```
Computer IP: 192.168.1.100 (example - use YOUR IP)
Device WiFi: Same network as computer
API Endpoints: http://192.168.1.100:5006 and :5004
```

**Important:**
- ❌ Don't use `localhost` - device can't access it
- ❌ Don't use `127.0.0.1` - device can't access it
- ✅ Use your computer's IP address (e.g., `192.168.1.100`)
- ✅ Ensure same WiFi network
- ✅ Allow firewall access to ports 5006 and 5004

---

## Next Steps

1. **Test all features** - Navigate through Dashboard, Failures, Chat, Analytics, RAG Approval
2. **Test offline mode** - Turn off WiFi and verify cached data works
3. **Test dark mode** - Go to More > Settings > Toggle Dark Mode
4. **Provide feedback** - Submit feedback on failures to test the feedback workflow
5. **Test manual trigger** - Trigger analysis for a build ID

---

## Development Workflow

**Recommended workflow for development:**

1. Connect device via USB
2. Run `flutter run` (Method 1)
3. Make code changes
4. Press `r` for hot reload
5. Test changes on device
6. Repeat

**For testing releases:**

1. Build APK: `flutter build apk --release`
2. Install APK on device
3. Test production build
4. Distribute to testers

---

## Additional Resources

- **Flutter Docs**: https://docs.flutter.dev/get-started/install
- **Android Developer**: https://developer.android.com/studio/debug/dev-options
- **ADB Guide**: https://developer.android.com/studio/command-line/adb

---

**Congratulations!** Your DDN AI mobile app is now running on your Android device! 🎉

For questions or issues, refer to the troubleshooting section or check the Flutter documentation.
