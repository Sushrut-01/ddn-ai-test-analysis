# Fix Mobile Connectivity - Windows Firewall Configuration
# Run this as Administrator

Write-Host "=== DDN AI Mobile - Network Connectivity Fix ===" -ForegroundColor Cyan
Write-Host ""

# Remove existing rule if it exists
Write-Host "Removing old firewall rules (if any)..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "DDN Dashboard API*" -ErrorAction SilentlyContinue

# Add new firewall rule
Write-Host "Adding new firewall rule for port 5006..." -ForegroundColor Yellow
New-NetFirewallRule `
    -DisplayName "DDN Dashboard API - Mobile Access" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5006 `
    -Action Allow `
    -Profile Any `
    -Enabled True

Write-Host ""
Write-Host "✅ Firewall rule added successfully!" -ForegroundColor Green
Write-Host ""

# Test the connection
Write-Host "Testing connection to backend..." -ForegroundColor Yellow
$response = Invoke-WebRequest -Uri "http://192.168.1.7:5006/api/health" -UseBasicParsing -ErrorAction SilentlyContinue

if ($response.StatusCode -eq 200) {
    Write-Host "✅ Backend is accessible at http://192.168.1.7:5006" -ForegroundColor Green
    Write-Host ""
    Write-Host "NEXT STEPS:" -ForegroundColor Cyan
    Write-Host "1. Open Chrome on your Android phone" -ForegroundColor White
    Write-Host "2. Go to: http://192.168.1.7:5006/api/health" -ForegroundColor White
    Write-Host "3. You should see: {`"service`":`"dashboard-api-full`",`"status`":`"healthy`"}" -ForegroundColor White
    Write-Host "4. If you see this, install the APK and it will work!" -ForegroundColor White
} else {
    Write-Host "❌ Cannot reach backend. Check if Docker containers are running." -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
