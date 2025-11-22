# Phase 1: Document Current Docker Setup
# This script documents the current Docker/Docker Desktop configuration before migration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Documenting Current Docker Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$outputDir = "D:\rancher-storage\backups\pre-migration-$timestamp"

Write-Host "`nCreating backup directory..." -ForegroundColor Yellow
try {
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
    Write-Host "  [+] Created: $outputDir" -ForegroundColor Green
} catch {
    Write-Host "  [!] Failed to create backup directory" -ForegroundColor Red
    Write-Host "      Creating in current directory instead..." -ForegroundColor Yellow
    $outputDir = ".\pre-migration-backup-$timestamp"
    New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}

# Check if Docker is installed
Write-Host "`nChecking for existing Docker installation..." -ForegroundColor Yellow
$dockerInstalled = $false
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerInstalled = $true
        Write-Host "  [+] Docker found: $dockerVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "  [-] Docker not found or not running" -ForegroundColor Gray
}

if ($dockerInstalled) {
    # Document running containers
    Write-Host "`nDocumenting running containers..." -ForegroundColor Yellow
    try {
        $containers = docker ps -a --format "{{.ID}}|{{.Names}}|{{.Image}}|{{.Status}}" 2>&1
        $containers | Out-File -FilePath "$outputDir\docker-containers.txt"
        Write-Host "  [+] Container list saved to docker-containers.txt" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not list containers" -ForegroundColor Yellow
    }

    # Document images
    Write-Host "`nDocumenting Docker images..." -ForegroundColor Yellow
    try {
        $images = docker images --format "{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}" 2>&1
        $images | Out-File -FilePath "$outputDir\docker-images.txt"
        Write-Host "  [+] Image list saved to docker-images.txt" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not list images" -ForegroundColor Yellow
    }

    # Document volumes
    Write-Host "`nDocumenting Docker volumes..." -ForegroundColor Yellow
    try {
        $volumes = docker volume ls --format "{{.Name}}|{{.Driver}}" 2>&1
        $volumes | Out-File -FilePath "$outputDir\docker-volumes.txt"
        Write-Host "  [+] Volume list saved to docker-volumes.txt" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not list volumes" -ForegroundColor Yellow
    }

    # Document networks
    Write-Host "`nDocumenting Docker networks..." -ForegroundColor Yellow
    try {
        $networks = docker network ls --format "{{.Name}}|{{.Driver}}|{{.Scope}}" 2>&1
        $networks | Out-File -FilePath "$outputDir\docker-networks.txt"
        Write-Host "  [+] Network list saved to docker-networks.txt" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not list networks" -ForegroundColor Yellow
    }

    # Get Docker info
    Write-Host "`nGathering Docker system information..." -ForegroundColor Yellow
    try {
        docker info > "$outputDir\docker-info.txt" 2>&1
        Write-Host "  [+] Docker info saved to docker-info.txt" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not get Docker info" -ForegroundColor Yellow
    }
}

# Copy docker-compose files
Write-Host "`nBacking up docker-compose files..." -ForegroundColor Yellow
$composeFiles = @(
    "docker-compose.yml",
    "docker-compose-unified.yml",
    "docker-compose-langfuse.yml"
)

$copiedFiles = 0
foreach ($file in $composeFiles) {
    if (Test-Path $file) {
        try {
            Copy-Item -Path $file -Destination "$outputDir\$file" -Force
            Write-Host "  [+] Copied: $file" -ForegroundColor Green
            $copiedFiles++
        } catch {
            Write-Host "  [!] Failed to copy: $file" -ForegroundColor Yellow
        }
    }
}

# Copy .env.example
if (Test-Path ".env.example") {
    try {
        Copy-Item -Path ".env.example" -Destination "$outputDir\.env.example" -Force
        Write-Host "  [+] Copied: .env.example" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Failed to copy .env.example" -ForegroundColor Yellow
    }
}

# Create summary report
Write-Host "`nCreating summary report..." -ForegroundColor Yellow
$summaryContent = @"
# Docker Setup Documentation
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

## System Information
- Computer: $env:COMPUTERNAME
- User: $env:USERNAME
- OS: $(Get-CimInstance Win32_OperatingSystem | Select-Object -ExpandProperty Caption)

## Docker Installation
$(if ($dockerInstalled) { "- Docker Version: $dockerVersion" } else { "- Docker: Not found or not running" })

## Backup Contents
- Docker containers list
- Docker images list
- Docker volumes list
- Docker networks list
- Docker system information
- docker-compose files ($copiedFiles files)

## Notes
This backup was created before migrating to Rancher Desktop.
All files are stored in: $outputDir

## Next Steps
1. Install Rancher Desktop
2. Import important images (if needed)
3. Deploy docker-compose services on Rancher Desktop
4. Verify all services are working
5. Optionally uninstall Docker Desktop

## Important docker-compose Files
$($composeFiles | ForEach-Object { "- $_`n" })

## Migration Checklist
- [ ] Rancher Desktop installed
- [ ] WSL2 moved to D: drive
- [ ] Storage configured on D: drive
- [ ] docker-compose files updated
- [ ] Services deployed and tested
- [ ] Old Docker Desktop uninstalled (optional)
"@

Set-Content -Path "$outputDir\MIGRATION-SUMMARY.md" -Value $summaryContent
Write-Host "  [+] Summary report created: MIGRATION-SUMMARY.md" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Documentation Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "`nBackup location: $outputDir" -ForegroundColor Green
Write-Host "`nNext: Run 01-create-d-drive-structure.ps1" -ForegroundColor Yellow
