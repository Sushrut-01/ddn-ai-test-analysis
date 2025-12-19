# Flutter Installation Script for Windows
# This script will download and install Flutter SDK

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Flutter SDK Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some operations may fail. For best results, run PowerShell as Administrator." -ForegroundColor Yellow
    Write-Host ""
}

# Configuration
$flutterVersion = "3.16.9"
$flutterDownloadUrl = "https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_$flutterVersion-stable.zip"
$installPath = "C:\flutter"
$downloadPath = "$env:TEMP\flutter.zip"

# Step 1: Check if Flutter already installed
Write-Host "[1/7] Checking existing Flutter installation..." -ForegroundColor Green

if (Test-Path "$installPath\bin\flutter.bat") {
    Write-Host "Flutter is already installed at: $installPath" -ForegroundColor Yellow
    & "$installPath\bin\flutter.bat" --version
    Write-Host ""

    $response = Read-Host "Do you want to reinstall Flutter? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Skipping Flutter installation." -ForegroundColor Yellow
        Write-Host ""

        # Just update PATH and continue
        $env:Path = "$installPath\bin;$env:Path"
        Write-Host "[DONE] Flutter is ready to use!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next step: Run build_apk.bat to build the APK" -ForegroundColor Cyan
        exit 0
    }

    Write-Host "Removing existing installation..." -ForegroundColor Yellow
    Remove-Item -Path $installPath -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Flutter not found. Proceeding with installation..." -ForegroundColor Green
Write-Host ""

# Step 2: Download Flutter SDK
Write-Host "[2/7] Downloading Flutter SDK (this may take 5-10 minutes)..." -ForegroundColor Green
Write-Host "URL: $flutterDownloadUrl" -ForegroundColor Gray
Write-Host "Downloading to: $downloadPath" -ForegroundColor Gray
Write-Host ""

try {
    # Check if already downloaded
    if (Test-Path $downloadPath) {
        Write-Host "Flutter SDK already downloaded. Skipping download..." -ForegroundColor Yellow
    } else {
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $flutterDownloadUrl -OutFile $downloadPath
        $ProgressPreference = 'Continue'
        Write-Host "Download complete!" -ForegroundColor Green
    }
} catch {
    Write-Host "[ERROR] Failed to download Flutter SDK" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually from:" -ForegroundColor Yellow
    Write-Host "https://docs.flutter.dev/get-started/install/windows" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 3: Extract Flutter SDK
Write-Host "[3/7] Extracting Flutter SDK to C:\flutter..." -ForegroundColor Green

try {
    # Create C:\ directory if it doesn't exist
    if (-not (Test-Path "C:\")) {
        New-Item -ItemType Directory -Path "C:\" -Force | Out-Null
    }

    # Extract using Expand-Archive
    Expand-Archive -Path $downloadPath -DestinationPath "C:\" -Force
    Write-Host "Extraction complete!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Failed to extract Flutter SDK" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 4: Add Flutter to PATH (User Environment Variable)
Write-Host "[4/7] Adding Flutter to PATH..." -ForegroundColor Green

try {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")

    if ($userPath -notlike "*$installPath\bin*") {
        $newPath = "$installPath\bin;$userPath"
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        Write-Host "Added $installPath\bin to User PATH" -ForegroundColor Green

        # Also update current session PATH
        $env:Path = "$installPath\bin;$env:Path"
    } else {
        Write-Host "Flutter is already in PATH" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[WARNING] Could not update PATH automatically" -ForegroundColor Yellow
    Write-Host "Please add C:\flutter\bin to your PATH manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Verify Flutter installation
Write-Host "[5/7] Verifying Flutter installation..." -ForegroundColor Green

try {
    & "$installPath\bin\flutter.bat" --version
    Write-Host ""
    Write-Host "Flutter installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Flutter installation verification failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 6: Accept Android licenses
Write-Host "[6/7] Checking Android SDK and licenses..." -ForegroundColor Green
Write-Host "This will download Android SDK if not already installed (may take 10-15 minutes)" -ForegroundColor Yellow
Write-Host ""

try {
    # Run flutter doctor to trigger Android SDK download
    & "$installPath\bin\flutter.bat" doctor
    Write-Host ""

    # Accept licenses
    Write-Host "Accepting Android licenses (press 'y' when prompted)..." -ForegroundColor Yellow
    & "$installPath\bin\flutter.bat" doctor --android-licenses

} catch {
    Write-Host "[WARNING] Android SDK setup incomplete" -ForegroundColor Yellow
    Write-Host "You may need to run 'flutter doctor' manually" -ForegroundColor Yellow
}

Write-Host ""

# Step 7: Clean up
Write-Host "[7/7] Cleaning up temporary files..." -ForegroundColor Green

try {
    if (Test-Path $downloadPath) {
        Remove-Item -Path $downloadPath -Force
        Write-Host "Temporary files removed" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARNING] Could not remove temporary files" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Flutter Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Flutter installed at: $installPath" -ForegroundColor Cyan
Write-Host "Flutter added to PATH" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Close this PowerShell window" -ForegroundColor White
Write-Host "2. Open a NEW Command Prompt or PowerShell window" -ForegroundColor White
Write-Host "3. Run: flutter doctor" -ForegroundColor White
Write-Host "4. Navigate to ddn_ai_mobile folder" -ForegroundColor White
Write-Host "5. Run: build_apk.bat" -ForegroundColor White
Write-Host ""
Write-Host "Or run directly:" -ForegroundColor Yellow
Write-Host "   cd C:\DDN-AI-Project-Documentation\ddn_ai_mobile" -ForegroundColor Cyan
Write-Host "   .\build_apk.bat" -ForegroundColor Cyan
Write-Host ""

# Pause to let user read the output
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
