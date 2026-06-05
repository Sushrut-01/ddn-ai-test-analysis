# Build Instructions - DDN AI Mobile

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Flutter SDK** (3.0+)
   ```bash
   flutter --version
   ```

2. **Android Studio** or **VS Code** with Flutter extensions

3. **Android SDK** (API level 21+)

4. **Git** for version control

## Initial Setup

### 1. Install Flutter Dependencies

```bash
cd ddn_ai_mobile
flutter pub get
```

### 2. Run Code Generation

Generate Freezed models, JSON serialization, Retrofit services, and Injectable DI:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

For continuous code generation during development:

```bash
flutter pub run build_runner watch
```

### 3. Verify Installation

Check for any issues:

```bash
flutter doctor
```

Fix any issues reported by the doctor command.

## Backend Configuration

### Update API Base URLs

Edit `lib/core/constants/api_endpoints.dart` to point to your backend:

```dart
// For local development
static const String baseUrl = 'http://10.0.2.2:5006'; // Android emulator
// OR
static const String baseUrl = 'http://localhost:5006'; // iOS simulator

// For production
static const String baseUrl = 'https://your-production-api.com';
```

**Android Emulator:** Use `10.0.2.2` to access host machine's localhost
**iOS Simulator:** Use `localhost` directly
**Physical Device:** Use your machine's IP address (e.g., `http://192.168.1.100:5006`)

## Firebase Setup (for Push Notifications)

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project: "DDN AI Mobile"
3. Enable Firebase Cloud Messaging

### 2. Add Android App

1. Register Android app with package name: `com.ddn.ai.ddn_ai_mobile`
2. Download `google-services.json`
3. Place it in `android/app/`

### 3. Add iOS App (Optional - Future)

1. Register iOS app with bundle ID: `com.ddn.ai.ddnAiMobile`
2. Download `GoogleService-Info.plist`
3. Place it in `ios/Runner/`

### 4. Generate firebase_options.dart

```bash
flutterfire configure
```

## Running the App

### Development Mode

```bash
# Run on connected device/emulator
flutter run

# Run with specific device
flutter devices
flutter run -d <device-id>

# Run with hot reload
flutter run --hot
```

### Debug Build

```bash
# Android APK
flutter build apk --debug

# Install on connected device
flutter install
```

### Release Build

```bash
# Android APK
flutter build apk --release

# Android App Bundle (for Play Store)
flutter build appbundle --release
```

## Code Generation Commands

### After Creating Models

When you create a new model with `@freezed` or `@JsonSerializable`:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### After Creating API Services

When you create a new Retrofit API service:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### After Adding Injectable Dependencies

When you add `@injectable` or `@lazySingleton` annotations:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## Testing

### Run All Tests

```bash
flutter test
```

### Run Tests with Coverage

```bash
flutter test --coverage
```

View coverage report:

```bash
# On macOS/Linux
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html

# On Windows
genhtml coverage/lcov.info -o coverage/html
start coverage/html/index.html
```

### Run Integration Tests

```bash
flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/app_test.dart
```

## Troubleshooting

### Issue: "Null safety" errors

**Solution:** Ensure all dependencies support null safety. Run:
```bash
flutter pub outdated
flutter pub upgrade
```

### Issue: Code generation not working

**Solution:** Clean and rebuild:
```bash
flutter clean
flutter pub get
flutter pub run build_runner clean
flutter pub run build_runner build --delete-conflicting-outputs
```

### Issue: Android build fails

**Solution:** Check Android SDK:
```bash
cd android
./gradlew clean
./gradlew build
```

### Issue: Cannot connect to backend on Android emulator

**Solution:** Use `10.0.2.2` instead of `localhost` in API endpoints

### Issue: Hive database errors

**Solution:** Clear app data and reinstall:
```bash
flutter clean
flutter pub get
flutter run
```

## Environment-Specific Builds

### Development

```bash
flutter run --dart-define=ENV=dev
```

### Staging

```bash
flutter build apk --dart-define=ENV=staging --release
```

### Production

```bash
flutter build appbundle --dart-define=ENV=prod --release
```

Access environment variable in code:
```dart
const env = String.fromEnvironment('ENV', defaultValue: 'dev');
```

## Performance Profiling

### Check App Size

```bash
flutter build apk --analyze-size
```

### Profile Performance

```bash
flutter run --profile
```

Then use DevTools:
```bash
flutter pub global activate devtools
flutter pub global run devtools
```

## CI/CD Integration

### GitHub Actions (Example)

Create `.github/workflows/flutter.yml`:

```yaml
name: Flutter CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.16.0'

    - name: Install dependencies
      run: flutter pub get

    - name: Run code generation
      run: flutter pub run build_runner build --delete-conflicting-outputs

    - name: Analyze code
      run: flutter analyze

    - name: Run tests
      run: flutter test --coverage

    - name: Build APK
      run: flutter build apk --release

    - name: Upload APK
      uses: actions/upload-artifact@v3
      with:
        name: app-release.apk
        path: build/app/outputs/flutter-apk/app-release.apk
```

## Next Steps

After successful build:

1. **Run the app** on emulator/device
2. **Implement authentication module** (Phase 2)
3. **Setup GoRouter navigation** (Phase 2)
4. **Build dashboard UI** (Phase 2)

See `README.md` for full implementation roadmap.

---

**Need Help?**
- Flutter Docs: https://flutter.dev/docs
- Riverpod Docs: https://riverpod.dev/
- Dio Docs: https://pub.dev/packages/dio
