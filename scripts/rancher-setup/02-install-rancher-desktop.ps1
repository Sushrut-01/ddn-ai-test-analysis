# Phase 2: Install Rancher Desktop
# This script helps install Rancher Desktop using various methods

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Rancher Desktop Installation" -ForegroundColor Cyan
Write-Host "Phase 2: Installation Guide" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Rancher Desktop is already installed
Write-Host "`nChecking for existing Rancher Desktop installation..." -ForegroundColor Yellow
$rancherInstalled = $false
try {
    $rdVersion = & rancher-desktop --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $rancherInstalled = $true
        Write-Host "  [+] Rancher Desktop is already installed: $rdVersion" -ForegroundColor Green
        $overwrite = Read-Host "`nDo you want to continue anyway? (y/n)"
        if ($overwrite -ne "y") {
            Write-Host "Installation cancelled." -ForegroundColor Yellow
            Write-Host "`nTo configure existing installation, run: 03-move-wsl-to-d-drive.ps1" -ForegroundColor Cyan
            exit 0
        }
    }
} catch {
    Write-Host "  [-] Rancher Desktop not found" -ForegroundColor Gray
}

# Check for installation methods
Write-Host "`nDetecting available installation methods..." -ForegroundColor Yellow

# Check for WinGet
$wingetAvailable = $false
try {
    $wingetVersion = winget --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $wingetAvailable = $true
        Write-Host "  [+] WinGet available: $wingetVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  [-] WinGet not available" -ForegroundColor Gray
}

# Check for Chocolatey
$chocoAvailable = $false
try {
    $chocoVersion = choco --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $chocoAvailable = $true
        Write-Host "  [+] Chocolatey available: $chocoVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  [-] Chocolatey not available" -ForegroundColor Gray
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Installation Options" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nPlease select an installation method:" -ForegroundColor Yellow
Write-Host "`n1. WinGet (Recommended)" -ForegroundColor White
if ($wingetAvailable) {
    Write-Host "   Status: Available" -ForegroundColor Green
    Write-Host "   Command: winget install RancherLabs.RancherDesktop" -ForegroundColor Gray
} else {
    Write-Host "   Status: Not Available" -ForegroundColor Red
}

Write-Host "`n2. Chocolatey" -ForegroundColor White
if ($chocoAvailable) {
    Write-Host "   Status: Available" -ForegroundColor Green
    Write-Host "   Command: choco install rancher-desktop" -ForegroundColor Gray
} else {
    Write-Host "   Status: Not Available" -ForegroundColor Red
}

Write-Host "`n3. Manual Download" -ForegroundColor White
Write-Host "   Status: Always Available" -ForegroundColor Green
Write-Host "   URL: https://github.com/rancher-sandbox/rancher-desktop/releases" -ForegroundColor Gray

Write-Host "`n4. Exit and install manually" -ForegroundColor White

Write-Host "`n=====================================" -ForegroundColor Cyan
$choice = Read-Host "`nEnter your choice (1-4)"

switch ($choice) {
    "1" {
        if ($wingetAvailable) {
            Write-Host "`nInstalling Rancher Desktop via WinGet..." -ForegroundColor Yellow
            Write-Host "This may take several minutes. Please wait..." -ForegroundColor Gray
            try {
                winget install --id=RancherLabs.RancherDesktop -e --accept-package-agreements --accept-source-agreements
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "`n  [+] Installation successful!" -ForegroundColor Green
                } else {
                    Write-Host "`n  [!] Installation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
                }
            } catch {
                Write-Host "`n  [!] Installation error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "`nWinGet is not available on this system." -ForegroundColor Red
            Write-Host "Please choose option 2 (Chocolatey) or 3 (Manual Download)" -ForegroundColor Yellow
        }
    }
    "2" {
        if ($chocoAvailable) {
            Write-Host "`nInstalling Rancher Desktop via Chocolatey..." -ForegroundColor Yellow
            Write-Host "This may take several minutes. Please wait..." -ForegroundColor Gray
            try {
                choco install rancher-desktop -y
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "`n  [+] Installation successful!" -ForegroundColor Green
                } else {
                    Write-Host "`n  [!] Installation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
                }
            } catch {
                Write-Host "`n  [!] Installation error: $($_.Exception.Message)" -ForegroundColor Red
            }
        } else {
            Write-Host "`nChocolatey is not available on this system." -ForegroundColor Red
            Write-Host "Please install Chocolatey first or choose option 3 (Manual Download)" -ForegroundColor Yellow
        }
    }
    "3" {
        Write-Host "`nOpening download page in browser..." -ForegroundColor Yellow
        Start-Process "https://github.com/rancher-sandbox/rancher-desktop/releases/latest"
        Write-Host "`nPlease download and install the .exe file for Windows." -ForegroundColor Yellow
        Write-Host "After installation is complete, return here and press Enter." -ForegroundColor Yellow
        Read-Host
    }
    "4" {
        Write-Host "`nExiting..." -ForegroundColor Yellow
        Write-Host "`nManual installation instructions:" -ForegroundColor Cyan
        Write-Host "1. Visit: https://rancherdesktop.io/" -ForegroundColor White
        Write-Host "2. Download the Windows installer (.exe)" -ForegroundColor White
        Write-Host "3. Run the installer and follow the prompts" -ForegroundColor White
        Write-Host "4. After installation, run: 03-move-wsl-to-d-drive.ps1" -ForegroundColor White
        exit 0
    }
    default {
        Write-Host "`nInvalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

try {
    $rdVersion = & rancher-desktop --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] Rancher Desktop version: $rdVersion" -ForegroundColor Green
    } else {
        Write-Host "  [!] Verification failed" -ForegroundColor Red
        Write-Host "      You may need to restart your terminal or system" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [!] Command 'rancher-desktop' not found" -ForegroundColor Yellow
    Write-Host "      You may need to restart your terminal or add Rancher Desktop to PATH" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Initial Configuration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nBefore proceeding, please configure Rancher Desktop:" -ForegroundColor Yellow
Write-Host "`n1. Launch Rancher Desktop from Start Menu" -ForegroundColor White
Write-Host "2. On first launch, choose these settings:" -ForegroundColor White
Write-Host "   - Container Engine: dockerd (moby) [Docker compatible]" -ForegroundColor Cyan
Write-Host "   - Kubernetes: Enabled" -ForegroundColor Cyan
Write-Host "   - Kubernetes version: Latest stable (v1.29.x or newer)" -ForegroundColor Cyan
Write-Host "3. Wait for initialization to complete (5-10 minutes)" -ForegroundColor White
Write-Host "4. Allow any Windows Firewall prompts" -ForegroundColor White

Write-Host "`nHave you completed the initial configuration? (y/n)" -ForegroundColor Yellow
$configured = Read-Host

if ($configured -eq "y") {
    Write-Host "`nTesting Rancher Desktop..." -ForegroundColor Yellow

    # Test docker
    try {
        $dockerVer = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [+] Docker: $dockerVer" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [!] Docker not accessible" -ForegroundColor Red
    }

    # Test kubectl
    try {
        $k8sVer = kubectl version --client --short 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [+] Kubernetes: $k8sVer" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [!] kubectl not accessible" -ForegroundColor Red
    }

    # Test docker-compose
    try {
        $composeVer = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [+] docker-compose: $composeVer" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [!] docker-compose not accessible" -ForegroundColor Red
    }
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 2 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Ensure Rancher Desktop is running" -ForegroundColor White
Write-Host "2. Run: 03-move-wsl-to-d-drive.ps1" -ForegroundColor White
Write-Host "3. Configure storage locations" -ForegroundColor White

Write-Host "`nIMPORTANT: Keep Rancher Desktop running before proceeding to next step!" -ForegroundColor Cyan
