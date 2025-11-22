#Requires -Version 5.1

<#
.SYNOPSIS
    Complete Rancher Desktop Setup on D: Drive - Strict Mode

.DESCRIPTION
    This master script runs all setup phases in sequence, strictly enforcing
    D: drive storage for ALL Rancher Desktop components.

.NOTES
    - Run this from project root directory
    - Requires Administrator rights for Phase 3 (WSL2 migration)
    - Total time: 2-3 hours including downloads
    - Minimum 50GB free space required on D: drive
#>

param(
    [switch]$SkipBackup,
    [switch]$AutoYes
)

$ErrorActionPreference = "Stop"

Write-Host @"
====================================================================
    RANCHER DESKTOP - STRICT D: DRIVE SETUP
====================================================================

This script will:
1. Document current Docker setup (if exists)
2. Create D: drive directory structure
3. Install Rancher Desktop
4. Move WSL2 distribution to D: drive
5. Configure ALL storage on D: drive
6. Update docker-compose files for D: drive
7. Deploy and test services
8. Create management tools
9. Generate documentation

STRICT D: DRIVE MODE:
- WSL2 distribution: D:\WSL-Distributions\
- Kubernetes data: D:\rancher-storage\k3s-data\
- Docker images: D:\rancher-storage\docker-images\
- Volumes: D:\rancher-storage\volumes\
- Backups: D:\rancher-storage\backups\

====================================================================
"@ -ForegroundColor Cyan

# Pre-flight checks
Write-Host "`nPRE-FLIGHT CHECKS" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow

# Check 1: D: drive exists
Write-Host "`n[1/6] Checking D: drive exists..." -ForegroundColor White
if (-not (Test-Path "D:\")) {
    Write-Host "  [!] FAIL: D: drive not found!" -ForegroundColor Red
    Write-Host "  Please ensure D: drive is mounted and accessible." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [+] PASS: D: drive found" -ForegroundColor Green

# Check 2: D: drive space
Write-Host "`n[2/6] Checking D: drive space..." -ForegroundColor White
$dDrive = Get-Volume -DriveLetter D
$freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
$totalGB = [math]::Round($dDrive.Size / 1GB, 2)
Write-Host "  Total: ${totalGB}GB, Free: ${freeGB}GB" -ForegroundColor Gray

if ($freeGB -lt 50) {
    Write-Host "  [!] WARNING: Only ${freeGB}GB free space on D: drive" -ForegroundColor Yellow
    Write-Host "  Recommended: At least 50GB free space" -ForegroundColor Yellow
    if (-not $AutoYes) {
        $continue = Read-Host "  Continue anyway? (y/n)"
        if ($continue -ne "y") {
            Write-Host "Setup cancelled." -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "  [+] PASS: Sufficient space (${freeGB}GB free)" -ForegroundColor Green
}

# Check 3: PowerShell version
Write-Host "`n[3/6] Checking PowerShell version..." -ForegroundColor White
$psVersion = $PSVersionTable.PSVersion
Write-Host "  Version: $($psVersion.Major).$($psVersion.Minor)" -ForegroundColor Gray
if ($psVersion.Major -lt 5) {
    Write-Host "  [!] FAIL: PowerShell 5.1 or newer required" -ForegroundColor Red
    exit 1
}
Write-Host "  [+] PASS: PowerShell version OK" -ForegroundColor Green

# Check 4: WSL2 installed
Write-Host "`n[4/6] Checking WSL2..." -ForegroundColor White
try {
    $wslVersion = wsl --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: WSL2 is installed" -ForegroundColor Green
    } else {
        throw "WSL not responding"
    }
} catch {
    Write-Host "  [!] FAIL: WSL2 not installed or not responding" -ForegroundColor Red
    Write-Host "  Please install WSL2: wsl --install" -ForegroundColor Yellow
    Write-Host "  Then restart your computer and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check 5: Script location
Write-Host "`n[5/6] Checking script location..." -ForegroundColor White
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "  [!] FAIL: docker-compose.yml not found" -ForegroundColor Red
    Write-Host "  Please run this script from the project root directory." -ForegroundColor Yellow
    exit 1
}
Write-Host "  [+] PASS: Running from project root" -ForegroundColor Green

# Check 6: Setup scripts exist
Write-Host "`n[6/6] Checking setup scripts..." -ForegroundColor White
$requiredScripts = @(
    "scripts\rancher-setup\00-document-current-setup.ps1",
    "scripts\rancher-setup\01-create-d-drive-structure.ps1",
    "scripts\rancher-setup\02-install-rancher-desktop.ps1",
    "scripts\rancher-setup\03-move-wsl-to-d-drive.ps1",
    "scripts\rancher-setup\04-configure-storage-locations.ps1",
    "scripts\rancher-setup\05-update-docker-compose.ps1",
    "scripts\rancher-setup\06-test-deployment.ps1",
    "scripts\rancher-setup\07-create-management-scripts.ps1",
    "scripts\rancher-setup\08-create-documentation.ps1"
)

$allScriptsExist = $true
foreach ($script in $requiredScripts) {
    if (-not (Test-Path $script)) {
        Write-Host "  [!] Missing: $script" -ForegroundColor Red
        $allScriptsExist = $false
    }
}

if (-not $allScriptsExist) {
    Write-Host "  [!] FAIL: Some setup scripts are missing" -ForegroundColor Red
    exit 1
}
Write-Host "  [+] PASS: All setup scripts found" -ForegroundColor Green

# Summary
Write-Host "`n====================================================================`n" -ForegroundColor Cyan

Write-Host "PRE-FLIGHT CHECK SUMMARY" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "  D: Drive:        ${freeGB}GB free" -ForegroundColor White
Write-Host "  PowerShell:      $($psVersion.Major).$($psVersion.Minor)" -ForegroundColor White
Write-Host "  WSL2:            Installed" -ForegroundColor White
Write-Host "  Scripts:         Ready" -ForegroundColor White

Write-Host "`n====================================================================`n" -ForegroundColor Cyan

if (-not $AutoYes) {
    Write-Host "Ready to begin Rancher Desktop setup on D: drive." -ForegroundColor Yellow
    Write-Host "`nThis will take approximately 2-3 hours." -ForegroundColor Yellow
    Write-Host "The script will pause at key points for your input." -ForegroundColor Yellow
    Write-Host "`nContinue? (y/n)" -ForegroundColor Yellow
    $proceed = Read-Host
    if ($proceed -ne "y") {
        Write-Host "`nSetup cancelled." -ForegroundColor Red
        exit 0
    }
}

Write-Host "`n====================================================================`n" -ForegroundColor Cyan

# Track progress
$totalPhases = 9
$currentPhase = 0

# Helper function for phase execution
function Invoke-SetupPhase {
    param(
        [int]$PhaseNumber,
        [string]$PhaseName,
        [string]$ScriptPath,
        [switch]$RequiresAdmin,
        [switch]$Optional
    )

    $script:currentPhase++

    Write-Host "`n====================================================================`n" -ForegroundColor Cyan
    Write-Host "PHASE ${PhaseNumber}/${totalPhases}: $PhaseName" -ForegroundColor Cyan
    Write-Host "====================================================================`n" -ForegroundColor Cyan

    if ($RequiresAdmin) {
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            Write-Host "[!] This phase requires Administrator rights." -ForegroundColor Yellow
            Write-Host "`nPlease:" -ForegroundColor Yellow
            Write-Host "1. Close this window" -ForegroundColor White
            Write-Host "2. Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor White
            Write-Host "3. Navigate back to: $PWD" -ForegroundColor White
            Write-Host "4. Run: $ScriptPath" -ForegroundColor White
            Write-Host "5. After completion, re-run this master script" -ForegroundColor White
            Write-Host "`nSetup paused. Press Enter to exit..." -ForegroundColor Gray
            Read-Host
            exit 0
        }
    }

    if (Test-Path $ScriptPath) {
        try {
            & $ScriptPath
            Write-Host "`n[+] Phase $PhaseNumber completed successfully" -ForegroundColor Green
        } catch {
            Write-Host "`n[!] Phase $PhaseNumber encountered an error: $($_.Exception.Message)" -ForegroundColor Red
            if (-not $Optional) {
                Write-Host "Setup cannot continue. Please resolve the error and try again." -ForegroundColor Yellow
                exit 1
            }
        }
    } else {
        Write-Host "[!] Script not found: $ScriptPath" -ForegroundColor Red
        if (-not $Optional) {
            exit 1
        }
    }
}

# PHASE 0: Document current setup
if (-not $SkipBackup) {
    Invoke-SetupPhase -PhaseNumber 0 -PhaseName "Document Current Docker Setup" `
                      -ScriptPath ".\scripts\rancher-setup\00-document-current-setup.ps1" `
                      -Optional
}

# PHASE 1: Create D: drive structure
Invoke-SetupPhase -PhaseNumber 1 -PhaseName "Create D: Drive Structure" `
                  -ScriptPath ".\scripts\rancher-setup\01-create-d-drive-structure.ps1"

# PHASE 2: Install Rancher Desktop
Invoke-SetupPhase -PhaseNumber 2 -PhaseName "Install Rancher Desktop" `
                  -ScriptPath ".\scripts\rancher-setup\02-install-rancher-desktop.ps1"

Write-Host "`n====================================================================`n" -ForegroundColor Cyan
Write-Host "ADMINISTRATOR RIGHTS REQUIRED FOR NEXT PHASE" -ForegroundColor Yellow
Write-Host "====================================================================`n" -ForegroundColor Cyan

Write-Host "The next phase (WSL2 Migration) requires Administrator privileges." -ForegroundColor Yellow
Write-Host "`nOptions:" -ForegroundColor Yellow
Write-Host "1. Continue (if already running as Administrator)" -ForegroundColor White
Write-Host "2. Exit and restart PowerShell as Administrator" -ForegroundColor White

if (-not $AutoYes) {
    $adminChoice = Read-Host "`nEnter choice (1 or 2)"
    if ($adminChoice -eq "2") {
        Write-Host "`nExiting..." -ForegroundColor Yellow
        Write-Host "`nNext steps:" -ForegroundColor Cyan
        Write-Host "1. Right-click PowerShell -> Run as Administrator" -ForegroundColor White
        Write-Host "2. Navigate to: $PWD" -ForegroundColor White
        Write-Host "3. Run: .\scripts\rancher-setup\03-move-wsl-to-d-drive.ps1" -ForegroundColor White
        Write-Host "4. After completion, run remaining phases manually or re-run this script" -ForegroundColor White
        exit 0
    }
}

# PHASE 3: Move WSL2 to D: drive (REQUIRES ADMIN)
Invoke-SetupPhase -PhaseNumber 3 -PhaseName "Move WSL2 to D: Drive" `
                  -ScriptPath ".\scripts\rancher-setup\03-move-wsl-to-d-drive.ps1" `
                  -RequiresAdmin

# PHASE 4: Configure storage locations
Invoke-SetupPhase -PhaseNumber 4 -PhaseName "Configure Storage on D: Drive" `
                  -ScriptPath ".\scripts\rancher-setup\04-configure-storage-locations.ps1"

# PHASE 5: Update docker-compose files
Invoke-SetupPhase -PhaseNumber 5 -PhaseName "Update Docker Compose for D: Drive" `
                  -ScriptPath ".\scripts\rancher-setup\05-update-docker-compose.ps1"

Write-Host "`n====================================================================`n" -ForegroundColor Cyan
Write-Host "ENVIRONMENT CONFIGURATION REQUIRED" -ForegroundColor Yellow
Write-Host "====================================================================`n" -ForegroundColor Cyan

Write-Host "Before deploying services, you need to configure the .env file." -ForegroundColor Yellow
Write-Host "`nRequired configuration:" -ForegroundColor Yellow
Write-Host "  - API keys (Anthropic, OpenAI, Gemini)" -ForegroundColor White
Write-Host "  - Database credentials" -ForegroundColor White
Write-Host "  - Integration tokens (GitHub, Jira, Slack)" -ForegroundColor White

if (Test-Path ".env") {
    Write-Host "`n.env file already exists." -ForegroundColor Green
} else {
    Write-Host "`n.env file not found. Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item -Path ".env.example" -Destination ".env" -Force
        Write-Host "[+] Created .env file" -ForegroundColor Green
    }
}

if (-not $AutoYes) {
    Write-Host "`nDo you want to edit .env now? (y/n)" -ForegroundColor Yellow
    $editEnv = Read-Host
    if ($editEnv -eq "y") {
        notepad .env
        Write-Host "`nAfter saving .env, press Enter to continue..." -ForegroundColor Gray
        Read-Host
    } else {
        Write-Host "`n[!] WARNING: Services may not start correctly without proper .env configuration" -ForegroundColor Yellow
        Write-Host "You can edit .env later and then run: docker-compose up -d" -ForegroundColor Gray
    }
}

# PHASE 6: Test deployment
if (-not $AutoYes) {
    Write-Host "`n====================================================================`n" -ForegroundColor Cyan
    Write-Host "Do you want to deploy and test services now? (y/n)" -ForegroundColor Yellow
    $deployNow = Read-Host
    if ($deployNow -eq "y") {
        Invoke-SetupPhase -PhaseNumber 6 -PhaseName "Deploy and Test Services" `
                          -ScriptPath ".\scripts\rancher-setup\06-test-deployment.ps1"
    } else {
        Write-Host "`n[~] Skipping deployment. You can deploy later with:" -ForegroundColor Yellow
        Write-Host "    docker-compose up -d" -ForegroundColor Cyan
    }
} else {
    Invoke-SetupPhase -PhaseNumber 6 -PhaseName "Deploy and Test Services" `
                      -ScriptPath ".\scripts\rancher-setup\06-test-deployment.ps1"
}

# PHASE 7: Create management scripts
Invoke-SetupPhase -PhaseNumber 7 -PhaseName "Create Management Scripts" `
                  -ScriptPath ".\scripts\rancher-setup\07-create-management-scripts.ps1"

# PHASE 8: Create documentation
Invoke-SetupPhase -PhaseNumber 8 -PhaseName "Generate Documentation" `
                  -ScriptPath ".\scripts\rancher-setup\08-create-documentation.ps1"

# Final verification
Write-Host "`n====================================================================`n" -ForegroundColor Cyan
Write-Host "FINAL VERIFICATION" -ForegroundColor Cyan
Write-Host "====================================================================`n" -ForegroundColor Cyan

Write-Host "Running health check..." -ForegroundColor Yellow

if (Test-Path ".\scripts\rancher-management\verify-setup.ps1") {
    & .\scripts\rancher-management\verify-setup.ps1
} else {
    Write-Host "[!] Verification script not found. Skipping..." -ForegroundColor Yellow
}

# Setup complete
Write-Host "`n====================================================================`n" -ForegroundColor Cyan
Write-Host "RANCHER DESKTOP SETUP COMPLETE!" -ForegroundColor Green
Write-Host "====================================================================`n" -ForegroundColor Cyan

Write-Host "Storage Configuration (STRICT D: DRIVE):" -ForegroundColor Yellow
Write-Host "  WSL2 Distribution:  D:\WSL-Distributions\rancher-desktop" -ForegroundColor White
Write-Host "  Kubernetes Data:    D:\rancher-storage\k3s-data" -ForegroundColor White
Write-Host "  Docker Images:      D:\rancher-storage\docker-images" -ForegroundColor White
Write-Host "  Container Volumes:  D:\rancher-storage\volumes" -ForegroundColor White
Write-Host "  Backups:            D:\rancher-storage\backups" -ForegroundColor White

Write-Host "`nManagement Tools:" -ForegroundColor Yellow
Write-Host "  Health Check:       .\scripts\rancher-management\verify-setup.ps1" -ForegroundColor White
Write-Host "  Backup Volumes:     .\scripts\rancher-management\backup-volumes.ps1" -ForegroundColor White
Write-Host "  Manage Stack:       .\scripts\rancher-management\manage-stack.ps1" -ForegroundColor White
Write-Host "  Cleanup:            .\scripts\rancher-management\cleanup.ps1" -ForegroundColor White

Write-Host "`nDocumentation:" -ForegroundColor Yellow
Write-Host "  Full Guide:         RANCHER-SETUP.md" -ForegroundColor White
Write-Host "  Quick Reference:    RANCHER-QUICK-REF.md" -ForegroundColor White
Write-Host "  Install Summary:    RANCHER-INSTALL-SUMMARY.md" -ForegroundColor White

Write-Host "`nCommon Commands:" -ForegroundColor Yellow
Write-Host "  Start services:     docker-compose up -d" -ForegroundColor White
Write-Host "  Stop services:      docker-compose stop" -ForegroundColor White
Write-Host "  View logs:          docker-compose logs -f" -ForegroundColor White
Write-Host "  Check status:       docker-compose ps" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Verify .env configuration is complete" -ForegroundColor White
Write-Host "  2. Start services: docker-compose up -d" -ForegroundColor White
Write-Host "  3. Access dashboard: http://localhost:3000" -ForegroundColor White
Write-Host "  4. Create regular backups: .\scripts\rancher-management\backup-volumes.ps1" -ForegroundColor White

Write-Host "`n====================================================================`n" -ForegroundColor Cyan

# Create completion marker
$completionInfo = @"
Rancher Desktop Setup Completed
================================

Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Mode: STRICT D: DRIVE

Storage Verification:
- WSL2 Distribution: D:\WSL-Distributions\rancher-desktop
- Kubernetes Data: D:\rancher-storage\k3s-data
- Docker Images: D:\rancher-storage\docker-images
- Container Volumes: D:\rancher-storage\volumes
- Backups: D:\rancher-storage\backups

Verification Commands:
wsl --list -v
docker info | Select-String "Docker Root Dir"
Get-ChildItem D:\rancher-storage
Get-ChildItem D:\WSL-Distributions

All storage is configured on D: drive.
"@

Set-Content -Path "RANCHER-SETUP-COMPLETE.txt" -Value $completionInfo
Write-Host "Setup completion marker created: RANCHER-SETUP-COMPLETE.txt" -ForegroundColor Gray

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
