# Android SDK Installation Script for Windows
# This script downloads and installs Android command-line tools

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Android SDK Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$androidHome = "C:\Android"
$cmdlineToolsUrl = "https://dl.google.com/android/repository/commandlinetools-win-11076708_latest.zip"
$downloadPath = "$env:TEMP\android-cmdline-tools.zip"

# Step 1: Create Android SDK directory
Write-Host "[1/6] Creating Android SDK directory..." -ForegroundColor Green

if (-not (Test-Path $androidHome)) {
    New-Item -ItemType Directory -Path $androidHome -Force | Out-Null
    Write-Host "Created directory: $androidHome" -ForegroundColor Green
} else {
    Write-Host "Android SDK directory already exists" -ForegroundColor Yellow
}

Write-Host ""

# Step 2: Download Android command-line tools
Write-Host "[2/6] Downloading Android command-line tools (this may take 2-3 minutes)..." -ForegroundColor Green
Write-Host "URL: $cmdlineToolsUrl" -ForegroundColor Gray
Write-Host ""

try {
    if (Test-Path $downloadPath) {
        Write-Host "Android command-line tools already downloaded. Skipping..." -ForegroundColor Yellow
    } else {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $cmdlineToolsUrl -OutFile $downloadPath
        $ProgressPreference = 'Continue'
        Write-Host "Download complete!" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to download Android command-line tools" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 3: Extract command-line tools
Write-Host "[3/6] Extracting command-line tools..." -ForegroundColor Green

try {
    $extractPath = "$androidHome\cmdline-tools"

    if (Test-Path $extractPath) {
        Write-Host "Removing old command-line tools..." -ForegroundColor Yellow
        Remove-Item -Path $extractPath -Recurse -Force
    }

    Expand-Archive -Path $downloadPath -DestinationPath $androidHome -Force

    # Android expects cmdline-tools to be in cmdline-tools/latest
    if (Test-Path "$extractPath\cmdline-tools") {
        Move-Item -Path "$extractPath\cmdline-tools" -Destination "$extractPath\latest" -Force
    }

    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to extract command-line tools" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Set environment variables
Write-Host "[4/6] Setting environment variables..." -ForegroundColor Green

try {
    # Set ANDROID_HOME (deprecated but still used)
    [Environment]::SetEnvironmentVariable("ANDROID_HOME", $androidHome, "User")
    $env:ANDROID_HOME = $androidHome

    # Set ANDROID_SDK_ROOT (official)
    [Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", $androidHome, "User")
    $env:ANDROID_SDK_ROOT = $androidHome

    # Add to PATH
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")

    $pathsToAdd = @(
        "$androidHome\cmdline-tools\latest\bin",
        "$androidHome\platform-tools",
        "$androidHome\emulator"
    )

    foreach ($pathToAdd in $pathsToAdd) {
        if ($userPath -notlike "*$pathToAdd*") {
            $userPath = "$pathToAdd;$userPath"
        }
    }

    [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
    $env:Path = "$androidHome\cmdline-tools\latest\bin;$androidHome\platform-tools;$env:Path"

    Write-Host "Environment variables set:" -ForegroundColor Green
    Write-Host "  ANDROID_HOME = $androidHome" -ForegroundColor Cyan
    Write-Host "  ANDROID_SDK_ROOT = $androidHome" -ForegroundColor Cyan
} catch {
    Write-Host "[WARNING] Could not set environment variables automatically" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Install required SDK components
Write-Host "[5/6] Installing required Android SDK components..." -ForegroundColor Green
Write-Host "This will download:" -ForegroundColor Yellow
Write-Host "  - Platform Tools (adb, fastboot)" -ForegroundColor White
Write-Host "  - Build Tools (for compiling)" -ForegroundColor White
Write-Host "  - Android Platform 34 (latest)" -ForegroundColor White
Write-Host "This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    $sdkmanager = "$androidHome\cmdline-tools\latest\bin\sdkmanager.bat"

    # Accept licenses first
    Write-Host "Accepting Android SDK licenses..." -ForegroundColor Yellow
    & $sdkmanager --licenses 2>&1 | ForEach-Object {
        if ($_ -match "Accept") {
            Write-Host "y" -NoNewline
        }
    }

    Write-Host ""
    Write-Host "Installing SDK components..." -ForegroundColor Yellow

    # Install required components
    & $sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0" 2>&1 | Out-Null

    Write-Host "SDK components installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to install SDK components" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "You may need to run manually:" -ForegroundColor Yellow
    Write-Host "  $sdkmanager --licenses" -ForegroundColor Cyan
    Write-Host "  $sdkmanager `"platform-tools`" `"platforms;android-34`" `"build-tools;34.0.0`"" -ForegroundColor Cyan
}

Write-Host ""

# Step 6: Configure Flutter
Write-Host "[6/6] Configuring Flutter to use Android SDK..." -ForegroundColor Green

try {
    & "C:\flutter\bin\flutter.bat" config --android-sdk $androidHome
    Write-Host "Flutter configured successfully!" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Could not configure Flutter automatically" -ForegroundColor Yellow
    Write-Host "Please run manually: flutter config --android-sdk $androidHome" -ForegroundColor Yellow
}

Write-Host ""

# Clean up
Write-Host "Cleaning up temporary files..." -ForegroundColor Green
if (Test-Path $downloadPath) {
    Remove-Item -Path $downloadPath -Force
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Android SDK Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Android SDK installed at: $androidHome" -ForegroundColor Cyan
Write-Host "Environment variables set" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close this PowerShell window" -ForegroundColor White
Write-Host "2. Open a NEW Command Prompt or PowerShell window" -ForegroundColor White
Write-Host "3. Run: flutter doctor" -ForegroundColor White
Write-Host "4. Run: build_apk.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or continue in this session (environment may not be fully updated):" -ForegroundColor Yellow
Write-Host "   cd C:\DDN-AI-Project-Documentation\ddn_ai_mobile" -ForegroundColor Cyan
Write-Host "   flutter doctor --android-licenses" -ForegroundColor Cyan
Write-Host "   flutter build apk --release" -ForegroundColor Cyan
Write-Host ""

# Pause
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
