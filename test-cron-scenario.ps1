# Test Cron Job Scenario - Verify Jenkins Auto-Triggering
# This script simulates what happens when cron triggers Jenkins builds

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "   CRON JOB SCENARIO TEST" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Step 1: Check Jenkins is running
Write-Host "`n[Step 1] Checking Jenkins Status..." -ForegroundColor Yellow
try {
    $jenkins = Invoke-WebRequest -Uri "http://localhost:8081/api/json" -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Jenkins is running on port 8081" -ForegroundColor Green
} catch {
    Write-Host "✗ Jenkins is not accessible at http://localhost:8081" -ForegroundColor Red
    Write-Host "  Please start Jenkins first!" -ForegroundColor Red
    exit 1
}

# Step 2: Check current cron configuration
Write-Host "`n[Step 2] Checking Cron Configuration..." -ForegroundColor Yellow
try {
    $config = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/config.xml" -UseBasicParsing
    if ($config.Content -match '<spec>(.*?)</spec>') {
        $cronSchedule = $matches[1]
        Write-Host "Current cron schedule: $cronSchedule" -ForegroundColor Green
        
        if ($cronSchedule -eq "*/10 * * * *") {
            Write-Host "Cron is set to every 10 minutes!" -ForegroundColor Green
        } elseif ($cronSchedule -match "^\s*$") {
            Write-Host "No cron schedule configured" -ForegroundColor Yellow
            Write-Host "   Configure at: http://localhost:8081/job/DDN-Nightly-Tests/configure" -ForegroundColor Yellow
        } else {
            Write-Host "Cron schedule is set to: $cronSchedule" -ForegroundColor Cyan
        }
    } else {
        Write-Host "No build triggers found in configuration" -ForegroundColor Yellow
        Write-Host "   Add trigger at: http://localhost:8081/job/DDN-Nightly-Tests/configure" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not read Jenkins configuration" -ForegroundColor Yellow
}

# Step 3: Check recent build history
Write-Host "`n[Step 3] Checking Recent Build History..." -ForegroundColor Yellow
try {
    $api = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/api/json?tree=builds[number,result,timestamp,duration]" -UseBasicParsing
    $data = $api.Content | ConvertFrom-Json
    
    $recentBuilds = $data.builds | Select-Object -First 5
    Write-Host "✓ Last 5 builds:" -ForegroundColor Green
    
    foreach ($build in $recentBuilds) {
        $buildTime = [DateTimeOffset]::FromUnixTimeMilliseconds($build.timestamp).LocalDateTime
        $durationSec = [math]::Round($build.duration / 1000, 1)
        
        $resultIcon = "?"
        if ($build.result -eq "SUCCESS") { $resultIcon = "+" }
        elseif ($build.result -eq "FAILURE") { $resultIcon = "X" }
        elseif ($build.result -eq $null) { $resultIcon = "..." }
        
        Write-Host "   [$resultIcon] Build #$($build.number) - $($build.result) - $buildTime - ${durationSec}s" -ForegroundColor Gray
    }
    
    # Calculate time between builds
    if ($recentBuilds.Count -ge 2) {
        $lastBuild = [DateTimeOffset]::FromUnixTimeMilliseconds($recentBuilds[0].timestamp).LocalDateTime
        $prevBuild = [DateTimeOffset]::FromUnixTimeMilliseconds($recentBuilds[1].timestamp).LocalDateTime
        $timeDiff = ($lastBuild - $prevBuild).TotalMinutes
        
        Write-Host "`n   Time between last 2 builds: $([math]::Round($timeDiff, 1)) minutes" -ForegroundColor Cyan
        
        if ($timeDiff -ge 9 -and $timeDiff -le 11) {
            Write-Host "   [OK] Builds are ~10 minutes apart (cron working!)" -ForegroundColor Green
        } elseif ($timeDiff -le 1) {
            Write-Host "   [INFO] Builds are manual (less than 1 minute apart)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "✗ Could not fetch build history" -ForegroundColor Red
}

# Step 4: Check MongoDB connection
Write-Host "`n[Step 4] Checking MongoDB Atlas Connection..." -ForegroundColor Yellow
try {
    $result = python check_recent_atlas.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ MongoDB Atlas connection working" -ForegroundColor Green
        Write-Host "$result" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  MongoDB Atlas connection issue" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not check MongoDB (check_recent_atlas.py not found)" -ForegroundColor Yellow
}

# Step 5: Simulate next cron trigger
Write-Host "`n[Step 5] Simulating Next Cron Trigger..." -ForegroundColor Yellow
$now = Get-Date
$nextMinute = $now.AddMinutes(1).AddSeconds(-$now.Second)
$minutesUntilNext10 = 10 - ($now.Minute % 10)
$nextCron = $now.AddMinutes($minutesUntilNext10).AddSeconds(-$now.Second).AddMilliseconds(-$now.Millisecond)

Write-Host "Current time: $($now.ToString('HH:mm:ss'))" -ForegroundColor Gray
Write-Host "Next cron trigger (*/10): $($nextCron.ToString('HH:mm:ss')) (in $minutesUntilNext10 minutes)" -ForegroundColor Cyan

# Step 6: Test manual build trigger
Write-Host "`n[Step 6] Testing Manual Build Trigger..." -ForegroundColor Yellow
Write-Host "Triggering Build Now (simulating cron)..." -ForegroundColor Cyan

try {
    # Trigger build via API
    $trigger = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/build" -Method Post -UseBasicParsing -ErrorAction Stop
    Write-Host "✓ Build triggered successfully!" -ForegroundColor Green
    
    # Wait for build to start
    Start-Sleep -Seconds 3
    
    # Get latest build number
    $lastBuild = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/lastBuild/api/json" -UseBasicParsing
    $buildInfo = $lastBuild.Content | ConvertFrom-Json
    
    Write-Host "✓ Build #$($buildInfo.number) started" -ForegroundColor Green
    Write-Host "   Monitor at: http://localhost:8081/job/DDN-Nightly-Tests/$($buildInfo.number)/console" -ForegroundColor Cyan
    
    # Wait for build to complete
    Write-Host "`n   Waiting for build to complete..." -ForegroundColor Yellow
    $maxWait = 120 # 2 minutes
    $waited = 0
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 5
        $waited += 5
        
        $buildStatus = Invoke-WebRequest -Uri "http://localhost:8081/job/DDN-Nightly-Tests/lastBuild/api/json" -UseBasicParsing
        $status = ($buildStatus.Content | ConvertFrom-Json)
        
        if ($status.building -eq $false) {
            $result = $status.result
            $duration = [math]::Round($status.duration / 1000, 1)
            
            if ($result -eq "SUCCESS") {
                Write-Host "   [OK] Build COMPLETED successfully in $duration seconds" -ForegroundColor Green
            } elseif ($result -eq "FAILURE") {
                Write-Host "   [FAIL] Build FAILED in $duration seconds" -ForegroundColor Red
            } else {
                Write-Host "   [WARN] Build finished with result: $result" -ForegroundColor Yellow
            }
            break
        }
        
        Write-Host "   ... still running ($waited seconds)" -ForegroundColor Gray
    }
    
    if ($waited -ge $maxWait) {
        Write-Host "   [WARN] Build still running after $maxWait seconds (check Jenkins)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "✗ Failed to trigger build: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Verify MongoDB received failures
Write-Host "`n[Step 7] Verifying MongoDB Received Test Failures..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
try {
    $result = python check_recent_atlas.py 2>&1
    Write-Host "$result" -ForegroundColor Gray
    
    if ($result -match "Failures in last 24 hours: (\d+)") {
        $recentFailures = [int]$matches[1]
        if ($recentFailures -gt 0) {
            Write-Host "✓ Found $recentFailures recent failure(s) in MongoDB!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  No recent failures in MongoDB (check listener)" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "⚠️  Could not verify MongoDB data" -ForegroundColor Yellow
}

# Step 8: Check Dashboard
Write-Host "`n[Step 8] Checking Dashboard Status..." -ForegroundColor Yellow
try {
    $dashboard = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5
    Write-Host "✓ Dashboard is accessible at http://localhost:5173" -ForegroundColor Green
    Write-Host "   Open in browser to see latest failures" -ForegroundColor Cyan
} catch {
    Write-Host "⚠️  Dashboard not accessible (is it running?)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "   TEST SUMMARY" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ CRON JOB SCENARIO TEST COMPLETE!" -ForegroundColor Green
Write-Host ""
Write-Host "What happens when cron triggers:" -ForegroundColor Yellow
Write-Host "  1. Jenkins Build #N starts automatically" -ForegroundColor Gray
Write-Host "  2. Linux bash script executes" -ForegroundColor Gray
Write-Host "  3. Robot Framework tests run" -ForegroundColor Gray
Write-Host "  4. mongodb_robot_listener.py captures failures" -ForegroundColor Gray
Write-Host "  5. Failures written to MongoDB Atlas" -ForegroundColor Gray
Write-Host "  6. Dashboard refreshes automatically" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Configure cron in Jenkins: http://localhost:8081/job/DDN-Nightly-Tests/configure" -ForegroundColor Cyan
Write-Host "  2. Add schedule: */10 * * * *" -ForegroundColor Cyan
Write-Host "  3. Wait 10 minutes for next auto-build" -ForegroundColor Cyan
Write-Host "  4. Run this script again to verify" -ForegroundColor Cyan
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
