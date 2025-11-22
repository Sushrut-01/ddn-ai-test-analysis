# Phase 1: Create D: Drive Directory Structure for Rancher Desktop
# This script creates the necessary directory structure on D: drive

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Rancher Desktop - D: Drive Setup" -ForegroundColor Cyan
Write-Host "Phase 1: Creating Directory Structure" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if D: drive exists
if (-not (Test-Path "D:\")) {
    Write-Host "ERROR: D: drive not found!" -ForegroundColor Red
    Write-Host "Please ensure D: drive is mounted and accessible." -ForegroundColor Red
    exit 1
}

Write-Host "`nChecking D: drive space..." -ForegroundColor Yellow
$dDrive = Get-Volume -DriveLetter D
$freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
$totalGB = [math]::Round($dDrive.Size / 1GB, 2)
Write-Host "D: drive has ${freeGB}GB free space out of ${totalGB}GB total" -ForegroundColor Green

if ($freeGB -lt 20) {
    Write-Host "WARNING: Low disk space on D: drive. At least 20GB recommended." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        Write-Host "Setup cancelled." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nCreating directory structure on D: drive..." -ForegroundColor Yellow

# Define directory structure
$directories = @(
    "D:\rancher-storage",
    "D:\rancher-storage\k3s-data",
    "D:\rancher-storage\docker-images",
    "D:\rancher-storage\volumes",
    "D:\rancher-storage\volumes\mongodb-data",
    "D:\rancher-storage\volumes\postgres-data",
    "D:\rancher-storage\volumes\langfuse-db-data",
    "D:\rancher-storage\volumes\redis-data",
    "D:\rancher-storage\volumes\n8n-data",
    "D:\rancher-storage\backups",
    "D:\WSL-Distributions"
)

$created = 0
$skipped = 0

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        try {
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
            Write-Host "  [+] Created: $dir" -ForegroundColor Green
            $created++
        } catch {
            Write-Host "  [!] Failed to create: $dir" -ForegroundColor Red
            Write-Host "      Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  [~] Already exists: $dir" -ForegroundColor Gray
        $skipped++
    }
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Directory Creation Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Created: $created directories" -ForegroundColor Green
Write-Host "Skipped: $skipped directories (already exist)" -ForegroundColor Gray

# Set proper permissions
Write-Host "`nSetting permissions..." -ForegroundColor Yellow
try {
    $acl = Get-Acl "D:\rancher-storage"
    $identity = New-Object System.Security.Principal.NTAccount("$env:USERDOMAIN\$env:USERNAME")
    $permission = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $identity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
    )
    $acl.SetAccessRule($permission)
    Set-Acl "D:\rancher-storage" $acl
    Write-Host "  [+] Permissions set successfully" -ForegroundColor Green
} catch {
    Write-Host "  [!] Failed to set permissions: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "      You may need to run this script as Administrator" -ForegroundColor Yellow
}

# Create a README file in the rancher-storage directory
$readmeContent = @"
# Rancher Desktop Storage Directory

This directory contains all Rancher Desktop data stored on D: drive.

## Directory Structure:

- **k3s-data/** - Kubernetes (K3s) data including etcd, manifests, and pod data
- **docker-images/** - Docker container images storage
- **volumes/** - Persistent volumes for containers
  - mongodb-data/ - MongoDB database files
  - postgres-data/ - PostgreSQL database files
  - langfuse-db-data/ - Langfuse database files
  - redis-data/ - Redis data files
  - n8n-data/ - n8n workflow data
- **backups/** - Automated backups of volumes and images

## Important Notes:

- Do NOT delete these directories while Rancher Desktop is running
- These directories may consume significant disk space
- Regular backups are recommended

Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

Set-Content -Path "D:\rancher-storage\README.md" -Value $readmeContent
Write-Host "  [+] Created README.md in rancher-storage" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 1 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Install Rancher Desktop (run 02-install-rancher-desktop.ps1)" -ForegroundColor White
Write-Host "2. Configure storage locations" -ForegroundColor White
Write-Host "3. Deploy docker-compose services" -ForegroundColor White

Write-Host "`nDirectory structure ready at: D:\rancher-storage" -ForegroundColor Green
