# Phase 5: Update Docker Compose Files for D: Drive
# This script updates docker-compose files to use D: drive for volume storage

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Update Docker Compose Files" -ForegroundColor Cyan
Write-Host "Phase 5: Volume Path Configuration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if we're in the project root
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "`nERROR: docker-compose.yml not found in current directory!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# List docker-compose files to update
$composeFiles = @(
    "docker-compose.yml",
    "docker-compose-unified.yml",
    "docker-compose-langfuse.yml"
)

Write-Host "`nFound docker-compose files:" -ForegroundColor Yellow
foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        Write-Host "  [+] $file" -ForegroundColor Green
    } else {
        Write-Host "  [-] $file (not found)" -ForegroundColor Gray
    }
}

# Create backup
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = "D:\rancher-storage\backups\docker-compose-backup-$timestamp"
Write-Host "`nCreating backup..." -ForegroundColor Yellow
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null

foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination "$backupDir\$file" -Force
        Write-Host "  [+] Backed up: $file" -ForegroundColor Green
    }
}

Write-Host "  Backup location: $backupDir" -ForegroundColor Gray

# Volume mapping configuration
$volumeMapping = @{
    "mongodb_data" = "D:/rancher-storage/volumes/mongodb-data"
    "postgres_data" = "D:/rancher-storage/volumes/postgres-data"
    "langfuse_db_data" = "D:/rancher-storage/volumes/langfuse-db-data"
    "redis_data" = "D:/rancher-storage/volumes/redis-data"
    "n8n_data" = "D:/rancher-storage/volumes/n8n-data"
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Volume Mappings" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nThe following volume mappings will be configured:" -ForegroundColor Yellow
foreach ($vol in $volumeMapping.Keys) {
    Write-Host "  $vol -> $($volumeMapping[$vol])" -ForegroundColor White
}

Write-Host "`nDo you want to proceed with updating the files? (y/n)" -ForegroundColor Yellow
$proceed = Read-Host

if ($proceed -ne "y") {
    Write-Host "`nUpdate cancelled. Backups are preserved at:" -ForegroundColor Yellow
    Write-Host "  $backupDir" -ForegroundColor Cyan
    exit 0
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Updating Configuration Files" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Function to create named volume sections with driver_opts
function Get-NamedVolumeConfig {
    param($volumeName, $hostPath)
    return @"
  $volumeName:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: $hostPath
"@
}

# Update each docker-compose file
foreach ($file in $composeFiles) {
    if (-not (Test-Path $file)) {
        continue
    }

    Write-Host "`nProcessing: $file" -ForegroundColor Cyan
    $content = Get-Content $file -Raw

    # Check if file already uses D: drive
    if ($content -match "D:/rancher-storage") {
        Write-Host "  [~] File already configured for D: drive" -ForegroundColor Yellow
        continue
    }

    # Create modified version indicator
    $modifiedContent = $content

    # Add comment at the top
    $header = @"
# Modified for Rancher Desktop with D: drive storage
# Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
# Original backup: $backupDir\$file

"@

    if ($modifiedContent -notmatch "Modified for Rancher Desktop") {
        $modifiedContent = $header + $modifiedContent
    }

    # Replace volume definitions with D: drive paths
    # This preserves the docker-compose structure but updates the volume locations

    # For named volumes at the bottom of the file
    if ($modifiedContent -match "volumes:\s*\n([\s\S]*?)(\n\S|\z)") {
        $volumesSection = ""
        foreach ($volName in $volumeMapping.Keys) {
            $volumesSection += Get-NamedVolumeConfig $volName $volumeMapping[$volName]
            $volumesSection += "`n"
        }

        # Replace the volumes section
        $modifiedContent = $modifiedContent -replace "(?ms)^volumes:\s*\n.*?(?=\n\S|\z)", "volumes:`n$volumesSection"
    }

    # Save modified file
    try {
        $modifiedContent | Set-Content $file -NoNewline
        Write-Host "  [+] Updated successfully" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Failed to update: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Create volume directories
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Creating Volume Directories" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

foreach ($vol in $volumeMapping.Values) {
    $winPath = $vol -replace "/", "\"
    if (-not (Test-Path $winPath)) {
        try {
            New-Item -Path $winPath -ItemType Directory -Force | Out-Null
            Write-Host "  [+] Created: $winPath" -ForegroundColor Green
        } catch {
            Write-Host "  [!] Failed to create: $winPath" -ForegroundColor Red
        }
    } else {
        Write-Host "  [~] Already exists: $winPath" -ForegroundColor Gray
    }
}

# Create .env file if it doesn't exist
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Environment Configuration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "`nCreating .env file from .env.example..." -ForegroundColor Yellow
        Copy-Item -Path ".env.example" -Destination ".env" -Force
        Write-Host "  [+] Created .env file" -ForegroundColor Green
        Write-Host "  [!] Please update .env with your API keys and credentials" -ForegroundColor Yellow
    } else {
        Write-Host "  [!] .env.example not found" -ForegroundColor Yellow
        Write-Host "  Please create .env manually with required environment variables" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [+] .env file already exists" -ForegroundColor Green
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 5 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nDocker Compose Configuration Updated:" -ForegroundColor Green
Write-Host "  - Volume paths updated to D: drive" -ForegroundColor White
Write-Host "  - Volume directories created" -ForegroundColor White
Write-Host "  - Original files backed up" -ForegroundColor White

Write-Host "`nBackup location:" -ForegroundColor Yellow
Write-Host "  $backupDir" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Ensure Rancher Desktop is running" -ForegroundColor White
Write-Host "2. Update .env file with your credentials" -ForegroundColor White
Write-Host "3. Run: 06-test-deployment.ps1" -ForegroundColor White
Write-Host "4. Or manually test with: docker-compose up -d" -ForegroundColor White

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
