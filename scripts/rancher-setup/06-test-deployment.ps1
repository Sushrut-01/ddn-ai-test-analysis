# Phase 6: Test Deployment
# This script tests the docker-compose deployment on Rancher Desktop with D: drive storage

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Test Deployment" -ForegroundColor Cyan
Write-Host "Phase 6: Service Deployment & Verification" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if in project root
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "`nERROR: docker-compose.yml not found!" -ForegroundColor Red
    Write-Host "Please run this script from the project root directory." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Check if Rancher Desktop is running
Write-Host "`nChecking Rancher Desktop status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker not responding"
    }
    Write-Host "  [+] Rancher Desktop is running" -ForegroundColor Green
} catch {
    Write-Host "  [!] Rancher Desktop is not running!" -ForegroundColor Red
    Write-Host "  Please start Rancher Desktop and try again." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Check .env file
Write-Host "`nChecking environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "  [!] .env file not found!" -ForegroundColor Red
    Write-Host "  Creating from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item -Path ".env.example" -Destination ".env" -Force
        Write-Host "  [+] Created .env file" -ForegroundColor Green
        Write-Host "  [!] Please update .env with your API keys before continuing" -ForegroundColor Yellow
        Write-Host "`nDo you want to edit .env now? (y/n)" -ForegroundColor Yellow
        $editEnv = Read-Host
        if ($editEnv -eq "y") {
            notepad .env
            Write-Host "  After saving, press Enter to continue..." -ForegroundColor Gray
            Read-Host
        }
    } else {
        Write-Host "  [!] .env.example not found. Cannot continue." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  [+] .env file exists" -ForegroundColor Green
}

# Deployment options
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Deployment Options" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nSelect deployment mode:" -ForegroundColor Yellow
Write-Host "`n1. Test with basic services only (MongoDB + PostgreSQL)" -ForegroundColor White
Write-Host "2. Deploy full stack (docker-compose.yml)" -ForegroundColor White
Write-Host "3. Deploy unified stack with observability (docker-compose-unified.yml)" -ForegroundColor White
Write-Host "4. Custom service selection" -ForegroundColor White

$choice = Read-Host "`nEnter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`nTesting basic services..." -ForegroundColor Cyan
        $services = @("ddn-mongodb", "ddn-postgres")
        $composeFile = "docker-compose.yml"
    }
    "2" {
        Write-Host "`nDeploying full stack..." -ForegroundColor Cyan
        $services = @()  # Deploy all services
        $composeFile = "docker-compose.yml"
    }
    "3" {
        Write-Host "`nDeploying unified stack..." -ForegroundColor Cyan
        $services = @()  # Deploy all services
        $composeFile = "docker-compose-unified.yml"
        if (-not (Test-Path $composeFile)) {
            Write-Host "  [!] $composeFile not found!" -ForegroundColor Red
            exit 1
        }
    }
    "4" {
        Write-Host "`nCustom service selection..." -ForegroundColor Cyan
        Write-Host "Enter service names separated by spaces (e.g., ddn-mongodb ddn-postgres ddn-langgraph):" -ForegroundColor Yellow
        $serviceInput = Read-Host
        $services = $serviceInput -split "\s+"
        $composeFile = "docker-compose.yml"
    }
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

# Create volumes directories if they don't exist
Write-Host "`nEnsuring volume directories exist..." -ForegroundColor Yellow
$volumePaths = @(
    "D:\rancher-storage\volumes\mongodb-data",
    "D:\rancher-storage\volumes\postgres-data",
    "D:\rancher-storage\volumes\langfuse-db-data",
    "D:\rancher-storage\volumes\redis-data",
    "D:\rancher-storage\volumes\n8n-data"
)

foreach ($path in $volumePaths) {
    if (-not (Test-Path $path)) {
        New-Item -Path $path -ItemType Directory -Force | Out-Null
        Write-Host "  [+] Created: $path" -ForegroundColor Green
    }
}

# Pull images first
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Pulling Docker Images" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nPulling images (this may take several minutes)..." -ForegroundColor Yellow
if ($services.Count -gt 0) {
    docker-compose -f $composeFile pull $services
} else {
    docker-compose -f $composeFile pull
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] Image pull encountered errors" -ForegroundColor Yellow
    Write-Host "  Continuing with deployment..." -ForegroundColor Gray
}

# Deploy services
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Deploying Services" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nStarting services..." -ForegroundColor Yellow
if ($services.Count -gt 0) {
    docker-compose -f $composeFile up -d $services
} else {
    docker-compose -f $composeFile up -d
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "  [!] Deployment encountered errors" -ForegroundColor Red
    Write-Host "`nCheck logs with: docker-compose -f $composeFile logs" -ForegroundColor Yellow
} else {
    Write-Host "  [+] Services started successfully" -ForegroundColor Green
}

# Wait for services to initialize
Write-Host "`nWaiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check service status
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Service Status" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

docker-compose -f $composeFile ps

# Verify volumes are on D: drive
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Volume Verification" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nChecking volume locations..." -ForegroundColor Yellow
$volumes = docker volume ls --format "{{.Name}}"
foreach ($vol in $volumes) {
    $inspectOutput = docker volume inspect $vol | ConvertFrom-Json
    if ($inspectOutput.Mountpoint -match "D:") {
        Write-Host "  [+] $vol -> $($inspectOutput.Mountpoint)" -ForegroundColor Green
    } else {
        Write-Host "  [~] $vol -> $($inspectOutput.Mountpoint)" -ForegroundColor Gray
    }
}

# Test database connectivity
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Service Connectivity Tests" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Test MongoDB
if ($services.Count -eq 0 -or $services -contains "ddn-mongodb") {
    Write-Host "`nTesting MongoDB..." -ForegroundColor Yellow
    $mongoTest = docker-compose -f $composeFile exec -T ddn-mongodb mongosh --eval "db.adminCommand('ping')" 2>&1
    if ($LASTEXITCODE -eq 0 -and $mongoTest -match "ok.*1") {
        Write-Host "  [+] MongoDB is responding" -ForegroundColor Green
    } else {
        Write-Host "  [!] MongoDB test failed" -ForegroundColor Red
        Write-Host "  Check logs: docker-compose -f $composeFile logs ddn-mongodb" -ForegroundColor Gray
    }
}

# Test PostgreSQL
if ($services.Count -eq 0 -or $services -contains "ddn-postgres") {
    Write-Host "`nTesting PostgreSQL..." -ForegroundColor Yellow
    $pgTest = docker-compose -f $composeFile exec -T ddn-postgres pg_isready 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] PostgreSQL is responding" -ForegroundColor Green
    } else {
        Write-Host "  [!] PostgreSQL test failed" -ForegroundColor Red
        Write-Host "  Check logs: docker-compose -f $composeFile logs ddn-postgres" -ForegroundColor Gray
    }
}

# Disk usage check
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Disk Usage" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nChecking D: drive usage..." -ForegroundColor Yellow
$dDrive = Get-Volume -DriveLetter D
$freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
$totalGB = [math]::Round($dDrive.Size / 1GB, 2)
$usedGB = $totalGB - $freeGB
Write-Host "  Total: ${totalGB} GB" -ForegroundColor White
Write-Host "  Used:  ${usedGB} GB" -ForegroundColor White
Write-Host "  Free:  ${freeGB} GB" -ForegroundColor White

if ($freeGB -lt 10) {
    Write-Host "  [!] WARNING: Low disk space on D: drive!" -ForegroundColor Yellow
}

# Generate test report
$reportPath = "D:\rancher-storage\deployment-test-report.txt"
$report = @"
Rancher Desktop Deployment Test Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Configuration:
- Compose File: $composeFile
- Services: $(if ($services.Count -gt 0) { $services -join ", " } else { "All" })

Status:
$(docker-compose -f $composeFile ps 2>&1)

Disk Usage:
- D: Drive Total: ${totalGB} GB
- D: Drive Used: ${usedGB} GB
- D: Drive Free: ${freeGB} GB

Next Steps:
1. View logs: docker-compose -f $composeFile logs -f
2. Access services via configured ports
3. Run backup script for regular backups
"@

$report | Out-File -FilePath $reportPath
Write-Host "`nTest report saved to: $reportPath" -ForegroundColor Gray

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 6 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nDeployment Summary:" -ForegroundColor Yellow
Write-Host "  - Compose file: $composeFile" -ForegroundColor White
Write-Host "  - Services deployed: $(if ($services.Count -gt 0) { $services.Count } else { "All" })" -ForegroundColor White
Write-Host "  - Storage: D:\rancher-storage\volumes" -ForegroundColor White

Write-Host "`nUseful Commands:" -ForegroundColor Yellow
Write-Host "  View logs:        docker-compose -f $composeFile logs -f" -ForegroundColor Gray
Write-Host "  Stop services:    docker-compose -f $composeFile stop" -ForegroundColor Gray
Write-Host "  Restart services: docker-compose -f $composeFile restart" -ForegroundColor Gray
Write-Host "  Remove services:  docker-compose -f $composeFile down" -ForegroundColor Gray

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Monitor service logs for any errors" -ForegroundColor White
Write-Host "2. Test application functionality" -ForegroundColor White
Write-Host "3. Run: 07-create-management-scripts.ps1" -ForegroundColor White

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
