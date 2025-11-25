# Simple Cron Job Test - Verify Jenkins Auto-Triggering

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "  CRON JOB SCENARIO TEST" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Step 1: Check Jenkins
Write-Host "[Step 1] Checking Jenkins Status..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8081/api/json" -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Jenkins is running on port 8081`n" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Jenkins is not accessible`n" -ForegroundColor Red
    exit 1
}

# Step 2: Check Build History
Write-Host "[Step 2] Checking Recent Builds..." -ForegroundColor Yellow
try {
    $api = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/api/json?tree=builds[number,result,timestamp]" -UseBasicParsing
    $data = $api.Content | ConvertFrom-Json
    
    $recentBuilds = $data.builds | Select-Object -First 3
    Write-Host "Last 3 builds:" -ForegroundColor Green
    
    foreach ($build in $recentBuilds) {
        $buildTime = [DateTimeOffset]::FromUnixTimeMilliseconds($build.timestamp).LocalDateTime.ToString('HH:mm:ss')
        Write-Host "  Build #$($build.number) - $($build.result) - $buildTime" -ForegroundColor Gray
    }
    Write-Host ""
} catch {
    Write-Host "[ERROR] Could not fetch build history`n" -ForegroundColor Red
}

# Step 3: Trigger Test Build
Write-Host "[Step 3] Triggering Test Build..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/build" -Method Post -UseBasicParsing -ErrorAction Stop
    Write-Host "[OK] Build triggered!`n" -ForegroundColor Green
    
    Start-Sleep -Seconds 5
    
    $lastBuild = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/lastBuild/api/json" -UseBasicParsing
    $buildInfo = $lastBuild.Content | ConvertFrom-Json
    
    Write-Host "Build #$($buildInfo.number) started" -ForegroundColor Cyan
    Write-Host "Monitor: http://localhost:8081/job/DDN-Nightly-Tests/$($buildInfo.number)/console`n" -ForegroundColor Gray
    
} catch {
    Write-Host "[ERROR] Failed to trigger build`n" -ForegroundColor Red
}

# Step 4: Check MongoDB
Write-Host "[Step 4] Checking MongoDB..." -ForegroundColor Yellow
try {
    python check_recent_atlas.py
    Write-Host ""
} catch {
    Write-Host "[WARN] Could not check MongoDB`n" -ForegroundColor Yellow
}

# Step 5: Summary
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  SETUP CRON JOB" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

Write-Host "1. Open: http://localhost:8081/job/DDN-Nightly-Tests/configure" -ForegroundColor Yellow
Write-Host "2. Check: Build periodically" -ForegroundColor Yellow
Write-Host "3. Schedule: */10 * * * *" -ForegroundColor Yellow
Write-Host "4. Click: Save`n" -ForegroundColor Yellow

Write-Host "This will run tests every 10 minutes automatically!" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Cyan
