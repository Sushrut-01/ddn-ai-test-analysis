# Bug #4 Progress Checker
# Quick script to see how many reportFailure() calls Claude has fixed

Write-Host "`n╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       Bug #4 Fix Progress Tracker                 ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$file = "C:\DDN-AI-Project-Documentation\tests\ddn-advanced-scenarios.js"

if (-not (Test-Path $file)) {
    Write-Host "❌ ERROR: File not found!" -ForegroundColor Red
    Write-Host "   Expected: $file" -ForegroundColor Gray
    exit 1
}

# Count reportFailure calls
$content = Get-Content $file -Raw
$totalCalls = ([regex]::Matches($content, 'reportFailure\(')).Count
$withSuite = ([regex]::Matches($content, 'suite_name:')).Count
$remaining = $totalCalls - $withSuite
$progress = [math]::Round($withSuite / $totalCalls * 100, 1)

Write-Host "📊 Current Status:" -ForegroundColor Yellow
Write-Host "   Total reportFailure() calls: $totalCalls" -ForegroundColor White
Write-Host "   ✅ Fixed (with suite_name):  $withSuite" -ForegroundColor Green
Write-Host "   ⚠️  Still need fixing:        $remaining" -ForegroundColor $(if($remaining -eq 0){'Green'}else{'Yellow'})
Write-Host ""

# Progress bar
$barLength = 40
$filled = [math]::Floor($barLength * $progress / 100)
$empty = $barLength - $filled
$bar = "█" * $filled + "░" * $empty

Write-Host "   Progress: [$bar] $progress%" -ForegroundColor Cyan
Write-Host ""

# Status message
if ($remaining -eq 0) {
    Write-Host "🎉 ALL DONE! Bug #4 is FIXED!" -ForegroundColor Green
    Write-Host "   Next step: Run tests to verify MongoDB integration" -ForegroundColor White
    Write-Host "   Command: cd tests; npm run test:advanced" -ForegroundColor Gray
} elseif ($withSuite -eq 0) {
    Write-Host "🔴 NOT STARTED - Need to add suite metadata to all calls" -ForegroundColor Red
    Write-Host "   See: BUG4-PROGRESS-FOR-CLAUDE.md for instructions" -ForegroundColor Gray
} else {
    Write-Host "🟡 IN PROGRESS - Keep going!" -ForegroundColor Yellow
    Write-Host "   $remaining locations remaining" -ForegroundColor White
    Write-Host "   Next: Continue adding suite_name to remaining reportFailure calls" -ForegroundColor Gray
}

Write-Host ""

# Show last 3 fixed locations (for confirmation)
if ($withSuite -gt 0) {
    Write-Host "📝 Last Fixed Locations:" -ForegroundColor Cyan
    $lines = Get-Content $file
    $lineNum = 0
    $found = 0
    
    foreach ($line in $lines) {
        $lineNum++
        if ($line -match "suite_name:" -and $found -lt 3) {
            $found++
            $suiteName = $line -replace ".*suite_name:\s*'([^']+)'.*", '$1'
            Write-Host "   Line $lineNum`: $suiteName" -ForegroundColor Gray
        }
    }
}

Write-Host ""
