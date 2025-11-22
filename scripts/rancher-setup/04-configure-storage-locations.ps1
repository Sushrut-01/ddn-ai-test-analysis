# Phase 4: Configure Storage Locations on D: Drive
# This script configures Rancher Desktop to use D: drive for all storage

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Configure Storage Locations" -ForegroundColor Cyan
Write-Host "Phase 4: D: Drive Storage Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if Rancher Desktop is installed
Write-Host "`nChecking Rancher Desktop installation..." -ForegroundColor Yellow
try {
    $rdVersion = & rancher-desktop --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Rancher Desktop not found"
    }
    Write-Host "  [+] Rancher Desktop found: $rdVersion" -ForegroundColor Green
} catch {
    Write-Host "  [!] Rancher Desktop not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if D: drive directories exist
Write-Host "`nChecking D: drive directory structure..." -ForegroundColor Yellow
$requiredDirs = @(
    "D:\rancher-storage\k3s-data",
    "D:\rancher-storage\docker-images",
    "D:\rancher-storage\volumes"
)

$missingDirs = @()
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        $missingDirs += $dir
        Write-Host "  [!] Missing: $dir" -ForegroundColor Yellow
    } else {
        Write-Host "  [+] Found: $dir" -ForegroundColor Green
    }
}

if ($missingDirs.Count -gt 0) {
    Write-Host "`nCreating missing directories..." -ForegroundColor Yellow
    foreach ($dir in $missingDirs) {
        New-Item -Path $dir -ItemType Directory -Force | Out-Null
        Write-Host "  [+] Created: $dir" -ForegroundColor Green
    }
}

# Stop Rancher Desktop for configuration
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Stopping Rancher Desktop" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nPlease close Rancher Desktop if it's running..." -ForegroundColor Yellow
Write-Host "Checking for running processes..." -ForegroundColor Gray

$rdProcess = Get-Process "Rancher Desktop" -ErrorAction SilentlyContinue
if ($rdProcess) {
    Write-Host "  Rancher Desktop is running. Closing it..." -ForegroundColor Yellow
    try {
        Stop-Process -Name "Rancher Desktop" -Force
        Write-Host "  Waiting for shutdown..." -ForegroundColor Gray
        Start-Sleep -Seconds 15
        Write-Host "  [+] Rancher Desktop stopped" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not stop Rancher Desktop" -ForegroundColor Red
        Write-Host "  Please close it manually and press Enter to continue" -ForegroundColor Yellow
        Read-Host
    }
} else {
    Write-Host "  [-] Rancher Desktop is not running" -ForegroundColor Gray
}

# Configuration file paths
$appDataPath = "$env:LOCALAPPDATA\Rancher Desktop"
$settingsFile = "$appDataPath\rdctl-settings.json"
$daemonJsonFile = "$appDataPath\docker\daemon.json"

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Configuring Storage Paths" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Backup existing configuration
Write-Host "`nBacking up existing configuration..." -ForegroundColor Yellow
$backupDir = "D:\rancher-storage\backups\config-backup-$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss')"
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null

if (Test-Path $settingsFile) {
    Copy-Item -Path $settingsFile -Destination "$backupDir\rdctl-settings.json.backup" -Force
    Write-Host "  [+] Backed up rdctl-settings.json" -ForegroundColor Green
}

if (Test-Path $daemonJsonFile) {
    Copy-Item -Path $daemonJsonFile -Destination "$backupDir\daemon.json.backup" -Force
    Write-Host "  [+] Backed up daemon.json" -ForegroundColor Green
}

# Configure Kubernetes data location
Write-Host "`n[1/2] Configuring Kubernetes data location..." -ForegroundColor Cyan

if (Test-Path $settingsFile) {
    try {
        $settings = Get-Content $settingsFile | ConvertFrom-Json

        # Update Kubernetes data root
        if (-not $settings.kubernetes) {
            $settings | Add-Member -MemberType NoteProperty -Name "kubernetes" -Value @{}
        }
        $settings.kubernetes | Add-Member -MemberType NoteProperty -Name "dataRoot" -Value "D:\\rancher-storage\\k3s-data" -Force

        # Save updated settings
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsFile
        Write-Host "  [+] Kubernetes data root set to: D:\rancher-storage\k3s-data" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not update rdctl-settings.json: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "      You may need to configure this manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [!] Settings file not found: $settingsFile" -ForegroundColor Yellow
    Write-Host "      This will be created on first launch of Rancher Desktop" -ForegroundColor Gray

    # Create default settings
    $defaultSettings = @{
        version = 5
        kubernetes = @{
            enabled = $true
            version = "v1.29.0"
            port = 6443
            dataRoot = "D:\\rancher-storage\\k3s-data"
        }
        containerEngine = @{
            imageBuilder = @{
                buildkitVersion = "latest"
            }
        }
    }

    # Ensure parent directory exists
    if (-not (Test-Path $appDataPath)) {
        New-Item -Path $appDataPath -ItemType Directory -Force | Out-Null
    }

    $defaultSettings | ConvertTo-Json -Depth 10 | Set-Content $settingsFile
    Write-Host "  [+] Created new settings file with D: drive configuration" -ForegroundColor Green
}

# Configure Docker daemon (image storage)
Write-Host "`n[2/2] Configuring Docker image storage..." -ForegroundColor Cyan

$dockerDir = "$appDataPath\docker"
if (-not (Test-Path $dockerDir)) {
    New-Item -Path $dockerDir -ItemType Directory -Force | Out-Null
    Write-Host "  [+] Created docker configuration directory" -ForegroundColor Green
}

$daemonConfig = @{
    "data-root" = "D:\\rancher-storage\\docker-images"
    "storage-driver" = "overlay2"
    "log-driver" = "json-file"
    "log-opts" = @{
        "max-size" = "10m"
        "max-file" = "3"
    }
    "insecure-registries" = @()
    "registry-mirrors" = @()
}

try {
    $daemonConfig | ConvertTo-Json -Depth 10 | Set-Content $daemonJsonFile
    Write-Host "  [+] Docker data root set to: D:\rancher-storage\docker-images" -ForegroundColor Green
} catch {
    Write-Host "  [!] Could not create daemon.json: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Configuration Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nStorage Configuration:" -ForegroundColor Yellow
Write-Host "  Kubernetes (K3s) data: D:\rancher-storage\k3s-data" -ForegroundColor White
Write-Host "  Docker images:         D:\rancher-storage\docker-images" -ForegroundColor White
Write-Host "  Container volumes:     D:\rancher-storage\volumes" -ForegroundColor White
Write-Host "  Backups:               D:\rancher-storage\backups" -ForegroundColor White

Write-Host "`nConfiguration Files:" -ForegroundColor Yellow
Write-Host "  rdctl-settings.json:   $settingsFile" -ForegroundColor White
Write-Host "  daemon.json:           $daemonJsonFile" -ForegroundColor White
Write-Host "  Backup location:       $backupDir" -ForegroundColor White

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 4 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Start Rancher Desktop from Start Menu" -ForegroundColor White
Write-Host "2. Wait for initialization (may take 5-10 minutes)" -ForegroundColor White
Write-Host "3. Verify storage configuration with verification script" -ForegroundColor White
Write-Host "4. Run: 05-update-docker-compose.ps1" -ForegroundColor White

Write-Host "`nTo verify storage is configured correctly after starting Rancher Desktop:" -ForegroundColor Cyan
Write-Host "  docker info | Select-String 'Docker Root Dir'" -ForegroundColor Gray
Write-Host "  kubectl config view" -ForegroundColor Gray

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
