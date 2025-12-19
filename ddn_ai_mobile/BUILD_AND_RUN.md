# DDN AI Mobile - Build and Run Guide

## Prerequisites

Before building the application, ensure you have the following installed:

### Required Tools

1. **Flutter SDK** (version 3.16.0 or higher)
   ```bash
   flutter --version
   ```
   If not installed, follow: https://docs.flutter.dev/get-started/install

2. **Android Studio** (for Android development)
   - Android SDK
   - Android SDK Command-line Tools
   - Android SDK Build-Tools
   - Android Emulator (optional)

3. **Java Development Kit (JDK)** (version 17 or higher)
   ```bash
   java -version
   ```

4. **Git**
   ```bash
   git --version
   ```

### Verify Flutter Installation

```bash
flutter doctor -v
```

Ensure all checks pass (✓). Common issues:
- Android licenses: Run `flutter doctor --android-licenses`
- Android Studio not detected: Set `ANDROID_HOME` environment variable

---

## Project Setup

### Step 1: Navigate to Project Directory

```bash
cd C:\DDN-AI-Project-Documentation\ddn_ai_mobile
```

### Step 2: Install Flutter Dependencies

```bash
flutter pub get
```

This will download all packages defined in `pubspec.yaml`.

### Step 3: Run Code Generation

The project uses **Freezed**, **json_serializable**, and **Retrofit** for code generation.

#### Generate All Code

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**What this does:**
- Generates Freezed models (`.freezed.dart` files)
- Generates JSON serialization code (`.g.dart` files)
- Generates Retrofit API services (`_api_service.g.dart` files)
- `--delete-conflicting-outputs` removes old generated files before creating new ones

#### Watch Mode (for development)

If you want code to regenerate automatically on file changes:

```bash
flutter pub run build_runner watch --delete-conflicting-outputs
```

**Note:** This will run in the background. Press `Ctrl+C` to stop.

---

## Backend API Setup

The mobile app connects to the backend API. **Ensure the backend is running** before launching the app.

### Start Backend Services

#### Option 1: Using Docker Compose (Recommended)

```bash
cd C:\DDN-AI-Project-Documentation
docker-compose -f docker-compose-unified.yml up -d dashboard-api
```

#### Option 2: Run Manually

```bash
cd C:\DDN-AI-Project-Documentation\implementation
python dashboard_api_full.py
```

### Verify Backend is Running

Open browser and navigate to:
- Dashboard API: `http://localhost:5006/api/system/status`
- Should return JSON with system status

**API Endpoints Used by Mobile App:**
- Dashboard API: `http://localhost:5006/api`
  - GET `/system/status`
  - GET `/stats`
  - GET `/activity`
  - GET `/failures`
  - GET `/failures/{id}`
  - POST `/trigger/manual`
  - POST `/feedback/submit`
  - POST `/chat`

---

## Running the Application

### Step 1: List Available Devices

```bash
flutter devices
```

You should see:
- **Android Emulator** (if running)
- **Physical Android device** (if connected via USB with USB debugging enabled)
- **Chrome** (for web development)

### Step 2: Start Android Emulator (if not running)

#### From Android Studio:
1. Open Android Studio
2. Click **Tools** → **AVD Manager**
3. Click **▶ (Play)** button next to an emulator
4. Wait for emulator to boot (~30 seconds)

#### From Command Line:
```bash
emulator -list-avds
emulator -avd <avd_name>
```

### Step 3: Run the Application

#### Run on Android Emulator/Device

```bash
flutter run
```

This will:
1. Build the app in debug mode
2. Install on the connected device/emulator
3. Launch the app
4. Enable hot reload (press `r` in terminal)

#### Run with Specific Device

```bash
flutter run -d <device_id>
```

Example:
```bash
flutter run -d emulator-5554
```

#### Run in Release Mode (for performance testing)

```bash
flutter run --release
```

**Note:** Release mode disables debugging tools but provides better performance.

---

## Hot Reload (Development)

While the app is running in debug mode:

- **Press `r`** in terminal → Hot reload (apply code changes without restarting)
- **Press `R`** in terminal → Hot restart (restart app completely)
- **Press `q`** in terminal → Quit

---

## Building APK for Testing

### Debug APK

```bash
flutter build apk --debug
```

Output: `build/app/outputs/flutter-apk/app-debug.apk`

### Release APK

```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### Install APK on Device

```bash
flutter install
```

Or manually:
```bash
adb install build/app/outputs/flutter-apk/app-release.apk
```

---

## Troubleshooting

### Issue: Code Generation Fails

**Error:** `pub finished with exit code 1`

**Solution:**
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Issue: "Waiting for another flutter command to release the startup lock"

**Solution:**
```bash
taskkill /F /IM dart.exe
```

Then retry the command.

### Issue: App Can't Connect to Backend

**Error:** `NetworkException` or `Connection refused`

**Solution:**
1. Verify backend is running: `http://localhost:5006/api/system/status`
2. **For Android Emulator:** Use `10.0.2.2` instead of `localhost`:
   - Update `lib/core/constants/api_endpoints.dart`:
     ```dart
     static const String baseUrl = 'http://10.0.2.2:5006';
     ```
3. **For Physical Device:** Use computer's IP address:
   - Find IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
   - Example: `http://192.168.1.100:5006`

### Issue: Android Licenses Not Accepted

**Error:** `Android license status unknown`

**Solution:**
```bash
flutter doctor --android-licenses
```

Press `y` to accept all licenses.

### Issue: Gradle Build Fails

**Error:** `Gradle build failed`

**Solution:**
1. Clear Gradle cache:
   ```bash
   cd android
   .\gradlew clean
   cd ..
   ```
2. Rebuild:
   ```bash
   flutter clean
   flutter pub get
   flutter run
   ```

### Issue: "Failed to install .apk"

**Solution:**
1. Enable USB debugging on Android device
2. Allow installation from unknown sources
3. Uninstall previous version:
   ```bash
   adb uninstall com.ddn.ai.ddn_ai_mobile
   ```
4. Reinstall:
   ```bash
   flutter install
   ```

---

## Development Workflow

### Recommended Workflow

1. **Start Backend API:**
   ```bash
   docker-compose -f docker-compose-unified.yml up -d dashboard-api
   ```

2. **Start Flutter in Watch Mode:**
   ```bash
   flutter pub run build_runner watch
   ```
   (Keep this running in a separate terminal)

3. **Run App:**
   ```bash
   flutter run
   ```

4. **Make Code Changes** → Press `r` in terminal to hot reload

5. **Stop:**
   - Press `q` to quit app
   - `Ctrl+C` to stop build_runner watch
   - `docker-compose down` to stop backend

---

## Testing

### Run Unit Tests

```bash
flutter test
```

### Run Widget Tests

```bash
flutter test test/features/
```

### Run Integration Tests

```bash
flutter test integration_test/
```

### Run Tests with Coverage

```bash
flutter test --coverage
```

View coverage report:
```bash
genhtml coverage/lcov.info -o coverage/html
```

---

## Configuration

### API Endpoints

Update in `lib/core/constants/api_endpoints.dart`:

```dart
class ApiEndpoints {
  // Change this for production
  static const String baseUrl = 'http://localhost:5006';

  // For Android emulator
  // static const String baseUrl = 'http://10.0.2.2:5006';

  // For physical device (use your computer's IP)
  // static const String baseUrl = 'http://192.168.1.100:5006';
}
```

### App Name and Package

Update in `android/app/build.gradle`:

```gradle
defaultConfig {
    applicationId "com.ddn.ai.ddn_ai_mobile"
    ...
}
```

### App Icon

Replace files in:
- `android/app/src/main/res/mipmap-*dpi/ic_launcher.png`

Or use `flutter_launcher_icons` package.

---

## Production Build

### Build App Bundle (for Google Play Store)

```bash
flutter build appbundle --release
```

Output: `build/app/outputs/bundle/release/app-release.aab`

### Build APK (for direct distribution)

```bash
flutter build apk --release --split-per-abi
```

This creates 3 optimized APKs:
- `app-armeabi-v7a-release.apk` (32-bit ARM)
- `app-arm64-v8a-release.apk` (64-bit ARM - most common)
- `app-x86_64-release.apk` (64-bit x86)

---

## Environment Setup Summary

### Minimum Requirements

- **Flutter:** 3.16.0+
- **Dart:** 3.2.0+
- **Android SDK:** API 33 (Android 13)
- **Minimum Android Version:** API 21 (Android 5.0)
- **JDK:** 17+

### Quick Start Script (Windows PowerShell)

```powershell
# Navigate to project
cd C:\DDN-AI-Project-Documentation\ddn_ai_mobile

# Install dependencies
flutter pub get

# Generate code
flutter pub run build_runner build --delete-conflicting-outputs

# Start backend (in separate terminal)
# docker-compose -f ../docker-compose-unified.yml up -d dashboard-api

# Run app
flutter run
```

---

## Project Structure

```
ddn_ai_mobile/
├── lib/
│   ├── core/              # Core utilities and DI
│   ├── features/          # Feature modules
│   │   ├── auth/          # Authentication ✓
│   │   ├── dashboard/     # Dashboard ✓
│   │   ├── failures/      # Failures management ✓
│   │   ├── chat/          # AI Chatbot ✓
│   │   ├── analytics/     # Analytics (placeholder)
│   │   └── settings/      # Settings ✓
│   ├── routes/            # Navigation
│   ├── shared/            # Reusable widgets
│   └── main.dart          # App entry point
├── android/               # Android native code
├── ios/                   # iOS native code (future)
├── test/                  # Unit tests
├── integration_test/      # Integration tests
└── pubspec.yaml           # Dependencies
```

---

## Next Steps

1. **Run Code Generation**: `flutter pub run build_runner build`
2. **Start Backend API**: `docker-compose up dashboard-api`
3. **Launch App**: `flutter run`
4. **Test Features**:
   - Login with any email/password (mock auth)
   - View Dashboard with real data
   - Browse test failures
   - Chat with AI assistant
   - Submit feedback

---

## Support

For issues:
1. Check logs: `flutter logs`
2. Clear cache: `flutter clean && flutter pub get`
3. Rebuild: `flutter run --debug`
4. Check backend: `http://localhost:5006/api/system/status`

Happy coding! 🚀
