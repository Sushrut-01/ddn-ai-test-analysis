# Phase 7: Create Management and Backup Scripts
# This script generates useful management scripts for daily operations

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Create Management Scripts" -ForegroundColor Cyan
Write-Host "Phase 7: Operational Tools Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$scriptDir = "scripts\rancher-management"

# Create management scripts directory
if (-not (Test-Path $scriptDir)) {
    Write-Host "`nCreating management scripts directory..." -ForegroundColor Yellow
    New-Item -Path $scriptDir -ItemType Directory -Force | Out-Null
    Write-Host "  [+] Created: $scriptDir" -ForegroundColor Green
} else {
    Write-Host "  [+] Directory exists: $scriptDir" -ForegroundColor Green
}

# Script 1: Verify Rancher Setup
Write-Host "`nCreating verification script..." -ForegroundColor Yellow
$verifyScript = @'
# Verify Rancher Desktop Setup
# Quick health check for Rancher Desktop installation and configuration

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Rancher Desktop Health Check" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$results = @()

# Check Rancher Desktop
Write-Host "`n[1/10] Checking Rancher Desktop..." -ForegroundColor Yellow
try {
    $rdVersion = & rancher-desktop --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: $rdVersion" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Not responding" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: Not installed" -ForegroundColor Red
    $results += "FAIL"
}

# Check Docker
Write-Host "`n[2/10] Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVer = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: $dockerVer" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Not responding" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: Not accessible" -ForegroundColor Red
    $results += "FAIL"
}

# Check Kubernetes
Write-Host "`n[3/10] Checking Kubernetes..." -ForegroundColor Yellow
try {
    $k8sVer = kubectl version --client --short 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: $k8sVer" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Not responding" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: Not accessible" -ForegroundColor Red
    $results += "FAIL"
}

# Check WSL2
Write-Host "`n[4/10] Checking WSL2..." -ForegroundColor Yellow
try {
    $wslList = wsl --list -v 2>&1
    if ($wslList -match "rancher-desktop") {
        Write-Host "  [+] PASS: rancher-desktop distribution found" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Distribution not found" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: WSL2 error" -ForegroundColor Red
    $results += "FAIL"
}

# Check D: drive storage
Write-Host "`n[5/10] Checking D: drive storage..." -ForegroundColor Yellow
if (Test-Path "D:\rancher-storage") {
    Write-Host "  [+] PASS: Storage directory exists" -ForegroundColor Green
    $results += "PASS"
} else {
    Write-Host "  [!] FAIL: Storage directory not found" -ForegroundColor Red
    $results += "FAIL"
}

# Check Docker storage location
Write-Host "`n[6/10] Checking Docker storage location..." -ForegroundColor Yellow
try {
    $dockerInfo = docker info 2>&1 | Select-String "Docker Root Dir"
    if ($dockerInfo -match "D:") {
        Write-Host "  [+] PASS: Using D: drive" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] WARN: Not using D: drive" -ForegroundColor Yellow
        Write-Host "  $dockerInfo" -ForegroundColor Gray
        $results += "WARN"
    }
} catch {
    Write-Host "  [!] FAIL: Cannot check storage location" -ForegroundColor Red
    $results += "FAIL"
}

# Check running containers
Write-Host "`n[7/10] Checking running containers..." -ForegroundColor Yellow
try {
    $containers = docker ps --format "{{.Names}}" 2>&1
    $count = ($containers | Measure-Object -Line).Lines
    Write-Host "  [+] PASS: $count containers running" -ForegroundColor Green
    $results += "PASS"
} catch {
    Write-Host "  [!] FAIL: Cannot list containers" -ForegroundColor Red
    $results += "FAIL"
}

# Check docker-compose
Write-Host "`n[8/10] Checking docker-compose..." -ForegroundColor Yellow
try {
    $composeVer = docker-compose --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: $composeVer" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Not responding" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: Not accessible" -ForegroundColor Red
    $results += "FAIL"
}

# Check disk space
Write-Host "`n[9/10] Checking disk space..." -ForegroundColor Yellow
$dDrive = Get-Volume -DriveLetter D -ErrorAction SilentlyContinue
if ($dDrive) {
    $freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
    if ($freeGB -gt 20) {
        Write-Host "  [+] PASS: ${freeGB}GB free" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] WARN: Only ${freeGB}GB free" -ForegroundColor Yellow
        $results += "WARN"
    }
} else {
    Write-Host "  [!] FAIL: D: drive not found" -ForegroundColor Red
    $results += "FAIL"
}

# Check Kubernetes nodes
Write-Host "`n[10/10] Checking Kubernetes nodes..." -ForegroundColor Yellow
try {
    $nodes = kubectl get nodes 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PASS: Nodes available" -ForegroundColor Green
        $results += "PASS"
    } else {
        Write-Host "  [!] FAIL: Nodes not available" -ForegroundColor Red
        $results += "FAIL"
    }
} catch {
    Write-Host "  [!] FAIL: Cannot check nodes" -ForegroundColor Red
    $results += "FAIL"
}

# Summary
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$passed = ($results | Where-Object { $_ -eq "PASS" } | Measure-Object).Count
$failed = ($results | Where-Object { $_ -eq "FAIL" } | Measure-Object).Count
$warned = ($results | Where-Object { $_ -eq "WARN" } | Measure-Object).Count

Write-Host "`nResults: PASS: $passed | WARN: $warned | FAIL: $failed" -ForegroundColor Cyan

if ($failed -eq 0 -and $warned -eq 0) {
    Write-Host "`nAll checks passed!" -ForegroundColor Green
} elseif ($failed -eq 0) {
    Write-Host "`nSetup OK with warnings" -ForegroundColor Yellow
} else {
    Write-Host "`nSome checks failed. Please review." -ForegroundColor Red
}
'@

Set-Content -Path "$scriptDir\verify-setup.ps1" -Value $verifyScript
Write-Host "  [+] Created: verify-setup.ps1" -ForegroundColor Green

# Script 2: Backup Volumes
Write-Host "`nCreating backup script..." -ForegroundColor Yellow
$backupScript = @'
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
'@

Set-Content -Path "$scriptDir\backup-volumes.ps1" -Value $backupScript
Write-Host "  [+] Created: backup-volumes.ps1" -ForegroundColor Green

# Script 3: Start/Stop Stack
Write-Host "`nCreating stack management script..." -ForegroundColor Yellow
$stackScript = @'
# Manage Docker Compose Stack
# Easy start/stop/restart of services

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "status", "logs")]
    [string]$Action,

    [string]$Service = ""
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Stack Management: $Action" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "`nERROR: docker-compose.yml not found!" -ForegroundColor Red
    Write-Host "Please run this from the project root directory." -ForegroundColor Yellow
    exit 1
}

switch ($Action) {
    "start" {
        Write-Host "`nStarting services..." -ForegroundColor Yellow
        if ($Service) {
            docker-compose up -d $Service
        } else {
            docker-compose up -d
        }
        Write-Host "`nServices started. Use 'status' to check." -ForegroundColor Green
    }
    "stop" {
        Write-Host "`nStopping services..." -ForegroundColor Yellow
        if ($Service) {
            docker-compose stop $Service
        } else {
            docker-compose stop
        }
        Write-Host "`nServices stopped." -ForegroundColor Green
    }
    "restart" {
        Write-Host "`nRestarting services..." -ForegroundColor Yellow
        if ($Service) {
            docker-compose restart $Service
        } else {
            docker-compose restart
        }
        Write-Host "`nServices restarted." -ForegroundColor Green
    }
    "status" {
        Write-Host "`nService Status:" -ForegroundColor Yellow
        docker-compose ps
    }
    "logs" {
        Write-Host "`nShowing logs (Ctrl+C to exit):" -ForegroundColor Yellow
        if ($Service) {
            docker-compose logs -f --tail=100 $Service
        } else {
            docker-compose logs -f --tail=100
        }
    }
}
'@

Set-Content -Path "$scriptDir\manage-stack.ps1" -Value $stackScript
Write-Host "  [+] Created: manage-stack.ps1" -ForegroundColor Green

# Script 4: Cleanup Script
Write-Host "`nCreating cleanup script..." -ForegroundColor Yellow
$cleanupScript = @'
# Cleanup Unused Docker Resources
# Removes unused containers, images, volumes, and networks

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Docker Cleanup Utility" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nThis will remove:" -ForegroundColor Yellow
Write-Host "  - Stopped containers" -ForegroundColor White
Write-Host "  - Unused networks" -ForegroundColor White
Write-Host "  - Dangling images" -ForegroundColor White
Write-Host "  - Build cache" -ForegroundColor White

Write-Host "`nDo you want to continue? (y/n)" -ForegroundColor Yellow
$confirm = Read-Host

if ($confirm -ne "y") {
    Write-Host "Cleanup cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`nRunning cleanup..." -ForegroundColor Cyan

# Remove stopped containers
Write-Host "`n[1/4] Removing stopped containers..." -ForegroundColor Yellow
docker container prune -f

# Remove unused networks
Write-Host "`n[2/4] Removing unused networks..." -ForegroundColor Yellow
docker network prune -f

# Remove dangling images
Write-Host "`n[3/4] Removing dangling images..." -ForegroundColor Yellow
docker image prune -f

# Remove build cache
Write-Host "`n[4/4] Removing build cache..." -ForegroundColor Yellow
docker builder prune -f

# Check disk space
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Disk Space After Cleanup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

$dDrive = Get-Volume -DriveLetter D
$freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
Write-Host "`nD: drive free space: ${freeGB}GB" -ForegroundColor Green

Write-Host "`nCleanup complete!" -ForegroundColor Green
'@

Set-Content -Path "$scriptDir\cleanup.ps1" -Value $cleanupScript
Write-Host "  [+] Created: cleanup.ps1" -ForegroundColor Green

# Create README for management scripts
Write-Host "`nCreating management scripts README..." -ForegroundColor Yellow
$readmeContent = @"
# Rancher Desktop Management Scripts

This directory contains utility scripts for managing Rancher Desktop and your Docker Compose stack.

## Available Scripts

### 1. verify-setup.ps1
**Purpose:** Health check for Rancher Desktop installation and configuration

**Usage:**
\`\`\`powershell
.\verify-setup.ps1
\`\`\`

**Checks:**
- Rancher Desktop installation
- Docker engine status
- Kubernetes cluster status
- WSL2 distribution
- D: drive storage configuration
- Running containers
- Disk space

---

### 2. backup-volumes.ps1
**Purpose:** Backup volume data to prevent data loss

**Usage:**
\`\`\`powershell
# Live backup (containers keep running)
.\backup-volumes.ps1

# Full backup (stops containers for consistency)
.\backup-volumes.ps1 -Full
\`\`\`

**Backups:**
- MongoDB data
- PostgreSQL data
- Langfuse database
- Redis data
- n8n workflows

**Location:** D:\rancher-storage\backups\volumes-[timestamp]

---

### 3. manage-stack.ps1
**Purpose:** Easy management of Docker Compose services

**Usage:**
\`\`\`powershell
# Start all services
.\manage-stack.ps1 -Action start

# Stop all services
.\manage-stack.ps1 -Action stop

# Restart all services
.\manage-stack.ps1 -Action restart

# Check status
.\manage-stack.ps1 -Action status

# View logs
.\manage-stack.ps1 -Action logs

# Manage specific service
.\manage-stack.ps1 -Action start -Service ddn-mongodb
.\manage-stack.ps1 -Action logs -Service ddn-langgraph
\`\`\`

---

### 4. cleanup.ps1
**Purpose:** Remove unused Docker resources to free up disk space

**Usage:**
\`\`\`powershell
.\cleanup.ps1
\`\`\`

**Removes:**
- Stopped containers
- Unused networks
- Dangling images
- Build cache

---

## Common Workflows

### Daily Operations
\`\`\`powershell
# Check health
.\verify-setup.ps1

# View service status
.\manage-stack.ps1 -Action status

# View logs
.\manage-stack.ps1 -Action logs
\`\`\`

### Weekly Maintenance
\`\`\`powershell
# Backup volumes
.\backup-volumes.ps1 -Full

# Cleanup unused resources
.\cleanup.ps1

# Verify setup
.\verify-setup.ps1
\`\`\`

### Troubleshooting
\`\`\`powershell
# Check logs for specific service
.\manage-stack.ps1 -Action logs -Service [service-name]

# Restart problematic service
.\manage-stack.ps1 -Action restart -Service [service-name]

# Verify configuration
.\verify-setup.ps1
\`\`\`

---

## Best Practices

1. **Regular Backups:** Run \`backup-volumes.ps1\` at least weekly
2. **Monitor Disk Space:** Check D: drive space regularly
3. **Review Logs:** Periodically check service logs for errors
4. **Cleanup:** Run \`cleanup.ps1\` monthly to free space

---

## Support

For issues or questions:
1. Run \`verify-setup.ps1\` to identify problems
2. Check service logs with \`manage-stack.ps1 -Action logs\`
3. Refer to main documentation in RANCHER-SETUP.md
"@

Set-Content -Path "$scriptDir\README.md" -Value $readmeContent
Write-Host "  [+] Created: README.md" -ForegroundColor Green

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 7 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nManagement scripts created in: $scriptDir" -ForegroundColor Green

Write-Host "`nAvailable scripts:" -ForegroundColor Yellow
Write-Host "  1. verify-setup.ps1      - Health check" -ForegroundColor White
Write-Host "  2. backup-volumes.ps1    - Backup data" -ForegroundColor White
Write-Host "  3. manage-stack.ps1      - Manage services" -ForegroundColor White
Write-Host "  4. cleanup.ps1           - Free disk space" -ForegroundColor White
Write-Host "  5. README.md             - Documentation" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Test the management scripts" -ForegroundColor White
Write-Host "2. Run: 08-create-documentation.ps1" -ForegroundColor White

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
