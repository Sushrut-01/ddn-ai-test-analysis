@echo off
echo ========================================
echo DDN AI Mobile - APK Builder
echo ========================================
echo.

REM Check if Flutter is installed
where flutter >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Flutter is not installed or not in PATH
    echo.
    echo Please install Flutter first:
    echo 1. Download from: https://docs.flutter.dev/get-started/install/windows
    echo 2. Extract to C:\flutter
    echo 3. Add C:\flutter\bin to your PATH environment variable
    echo 4. Run 'flutter doctor' to verify installation
    echo.
    pause
    exit /b 1
)

echo [1/5] Checking Flutter installation...
flutter --version
echo.

echo [2/5] Getting dependencies...
flutter pub get
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to get dependencies
    pause
    exit /b 1
)
echo.

echo [3/5] Running code generation (this may take 2-3 minutes)...
flutter pub run build_runner build --delete-conflicting-outputs
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Code generation failed
    pause
    exit /b 1
)
echo.

echo [4/5] Building release APK (this may take 5-10 minutes)...
flutter build apk --release
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] APK build failed
    pause
    exit /b 1
)
echo.

echo [5/5] APK Build Complete!
echo.
echo ========================================
echo APK Location:
echo build\app\outputs\flutter-apk\app-release.apk
echo.
echo File size:
dir /s build\app\outputs\flutter-apk\app-release.apk | find "app-release.apk"
echo ========================================
echo.
echo Next steps:
echo 1. Copy app-release.apk to your phone
echo 2. Open the APK file on your phone
echo 3. Tap 'Install' (allow unknown sources if needed)
echo.
pause
