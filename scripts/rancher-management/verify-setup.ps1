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
