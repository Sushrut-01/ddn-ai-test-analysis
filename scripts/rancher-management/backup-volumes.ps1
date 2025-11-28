# Backup Rancher Desktop Volumes
# Creates timestamped backups of all volume data

param(
    [switch]$Full = $false
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Rancher Desktop Volume Backup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = "D:\rancher-storage\backups\volumes-$timestamp"

Write-Host "`nCreating backup directory..." -ForegroundColor Yellow
New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
Write-Host "  [+] Backup location: $backupDir" -ForegroundColor Green

# Volumes to backup
$volumes = @(
    @{Name="mongodb-data"; Path="D:\rancher-storage\volumes\mongodb-data"},
    @{Name="postgres-data"; Path="D:\rancher-storage\volumes\postgres-data"},
    @{Name="langfuse-db-data"; Path="D:\rancher-storage\volumes\langfuse-db-data"},
    @{Name="redis-data"; Path="D:\rancher-storage\volumes\redis-data"},
    @{Name="n8n-data"; Path="D:\rancher-storage\volumes\n8n-data"}
)

if ($Full) {
    Write-Host "`nWarning: This will stop all containers for a consistent backup." -ForegroundColor Yellow
    Write-Host "Continue? (y/n)" -ForegroundColor Yellow
    $confirm = Read-Host
    if ($confirm -eq "y") {
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        docker-compose stop
        Start-Sleep -Seconds 5
    } else {
        Write-Host "Backup cancelled." -ForegroundColor Red
        exit 0
    }
}

Write-Host "`nBacking up volumes..." -ForegroundColor Yellow
$backupCount = 0

foreach ($vol in $volumes) {
    if (Test-Path $vol.Path) {
        Write-Host "`n  Backing up $($vol.Name)..." -ForegroundColor Cyan
        $destPath = "$backupDir\$($vol.Name)"
        try {
            Copy-Item -Path $vol.Path -Destination $destPath -Recurse -Force
            $size = (Get-ChildItem -Path $destPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB
            Write-Host "    [+] Backed up: $([math]::Round($size, 2)) MB" -ForegroundColor Green
            $backupCount++
        } catch {
            Write-Host "    [!] Failed: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "  [~] Skipped $($vol.Name): Directory not found" -ForegroundColor Gray
    }
}

if ($Full) {
    Write-Host "`nRestarting containers..." -ForegroundColor Yellow
    docker-compose start
}

# Create backup manifest
$manifest = @"
Rancher Desktop Volume Backup
Created: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Type: $(if ($Full) { "Full (with container stop)" } else { "Live backup" })
Volumes backed up: $backupCount

Volumes:
$($volumes | ForEach-Object { "- $($_.Name)`n" })

Location: $backupDir
"@

Set-Content -Path "$backupDir\BACKUP-MANIFEST.txt" -Value $manifest

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nBackup location: $backupDir" -ForegroundColor Cyan
Write-Host "Volumes backed up: $backupCount" -ForegroundColor Green
