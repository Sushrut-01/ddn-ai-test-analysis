# Phase 3: Move WSL2 Distribution to D: Drive
# This script moves the Rancher Desktop WSL distribution from C: to D: drive

#Requires -RunAsAdministrator

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Move WSL2 to D: Drive" -ForegroundColor Cyan
Write-Host "Phase 3: WSL Distribution Migration" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check if running as Administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "`nERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click and select 'Run as Administrator'" -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Check if D: drive exists
if (-not (Test-Path "D:\")) {
    Write-Host "`nERROR: D: drive not found!" -ForegroundColor Red
    exit 1
}

# Check if WSL-Distributions directory exists
if (-not (Test-Path "D:\WSL-Distributions")) {
    Write-Host "`nCreating D:\WSL-Distributions directory..." -ForegroundColor Yellow
    New-Item -Path "D:\WSL-Distributions" -ItemType Directory -Force | Out-Null
}

Write-Host "`nListing current WSL distributions..." -ForegroundColor Yellow
wsl --list -v

Write-Host "`nLooking for Rancher Desktop distribution..." -ForegroundColor Yellow
$wslList = wsl --list -v
$rancherDistro = $null

# Check for various possible distribution names
$possibleNames = @("rancher-desktop", "rancher-desktop-data")
foreach ($name in $possibleNames) {
    if ($wslList -match $name) {
        $rancherDistro = $name
        Write-Host "  [+] Found distribution: $rancherDistro" -ForegroundColor Green
        break
    }
}

if (-not $rancherDistro) {
    Write-Host "`n  [!] Rancher Desktop WSL distribution not found!" -ForegroundColor Red
    Write-Host "`nAvailable distributions:" -ForegroundColor Yellow
    wsl --list -v
    Write-Host "`nPlease ensure Rancher Desktop is installed and has been launched at least once." -ForegroundColor Yellow
    Read-Host "`nPress Enter to exit"
    exit 1
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Migration Plan" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Source Distribution: $rancherDistro" -ForegroundColor White
Write-Host "Export Location: D:\WSL-Distributions\$rancherDistro-backup.tar" -ForegroundColor White
Write-Host "Import Location: D:\WSL-Distributions\$rancherDistro" -ForegroundColor White

Write-Host "`nWARNING: This process will:" -ForegroundColor Yellow
Write-Host "1. Stop Rancher Desktop and terminate the WSL distribution" -ForegroundColor White
Write-Host "2. Export the distribution (this may take 10-15 minutes)" -ForegroundColor White
Write-Host "3. Unregister the original distribution from C: drive" -ForegroundColor White
Write-Host "4. Import the distribution to D: drive" -ForegroundColor White

Write-Host "`nDo you want to continue? (y/n)" -ForegroundColor Yellow
$continue = Read-Host

if ($continue -ne "y") {
    Write-Host "`nMigration cancelled." -ForegroundColor Yellow
    exit 0
}

# Step 1: Stop Rancher Desktop
Write-Host "`n[Step 1/4] Stopping Rancher Desktop..." -ForegroundColor Cyan
try {
    $rdProcess = Get-Process "Rancher Desktop" -ErrorAction SilentlyContinue
    if ($rdProcess) {
        Write-Host "  Closing Rancher Desktop..." -ForegroundColor Yellow
        Stop-Process -Name "Rancher Desktop" -Force -ErrorAction SilentlyContinue
        Write-Host "  Waiting for shutdown..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
    } else {
        Write-Host "  Rancher Desktop is not running" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Could not stop Rancher Desktop: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Terminate WSL distribution
Write-Host "`n  Terminating WSL distribution..." -ForegroundColor Yellow
wsl --terminate $rancherDistro
Start-Sleep -Seconds 5

# Verify it's terminated
$wslStatus = wsl --list -v
if ($wslStatus -match "$rancherDistro.*Running") {
    Write-Host "  [!] Distribution still running. Forcing shutdown..." -ForegroundColor Yellow
    wsl --shutdown
    Start-Sleep -Seconds 10
}
Write-Host "  [+] WSL distribution terminated" -ForegroundColor Green

# Step 2: Export distribution
Write-Host "`n[Step 2/4] Exporting WSL distribution to D: drive..." -ForegroundColor Cyan
$exportPath = "D:\WSL-Distributions\$rancherDistro-backup.tar"
Write-Host "  Export path: $exportPath" -ForegroundColor Gray
Write-Host "  This may take 10-15 minutes depending on size..." -ForegroundColor Yellow

try {
    $exportStart = Get-Date
    wsl --export $rancherDistro $exportPath
    $exportEnd = Get-Date
    $exportDuration = ($exportEnd - $exportStart).TotalMinutes

    if (Test-Path $exportPath) {
        $fileSize = (Get-Item $exportPath).Length / 1GB
        Write-Host "  [+] Export successful!" -ForegroundColor Green
        Write-Host "  Export size: $([math]::Round($fileSize, 2)) GB" -ForegroundColor Gray
        Write-Host "  Duration: $([math]::Round($exportDuration, 1)) minutes" -ForegroundColor Gray
    } else {
        throw "Export file not found"
    }
} catch {
    Write-Host "  [!] Export failed: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Step 3: Unregister original distribution
Write-Host "`n[Step 3/4] Unregistering original distribution from C: drive..." -ForegroundColor Cyan
Write-Host "  WARNING: This will remove the distribution from C: drive!" -ForegroundColor Yellow
Write-Host "  Confirm unregister? (y/n)" -ForegroundColor Yellow
$confirmUnregister = Read-Host

if ($confirmUnregister -eq "y") {
    try {
        wsl --unregister $rancherDistro
        Write-Host "  [+] Distribution unregistered successfully" -ForegroundColor Green
        Start-Sleep -Seconds 3
    } catch {
        Write-Host "  [!] Unregister failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  The export is safe at: $exportPath" -ForegroundColor Yellow
        Read-Host "`nPress Enter to exit"
        exit 1
    }
} else {
    Write-Host "  [-] Unregister cancelled. Export is available at: $exportPath" -ForegroundColor Yellow
    Write-Host "  You can manually unregister later with: wsl --unregister $rancherDistro" -ForegroundColor Cyan
    exit 0
}

# Step 4: Import to D: drive
Write-Host "`n[Step 4/4] Importing distribution to D: drive..." -ForegroundColor Cyan
$importPath = "D:\WSL-Distributions\$rancherDistro"
Write-Host "  Import path: $importPath" -ForegroundColor Gray
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Yellow

try {
    $importStart = Get-Date
    wsl --import $rancherDistro $importPath $exportPath
    $importEnd = Get-Date
    $importDuration = ($importEnd - $importStart).TotalMinutes

    Write-Host "  [+] Import successful!" -ForegroundColor Green
    Write-Host "  Duration: $([math]::Round($importDuration, 1)) minutes" -ForegroundColor Gray
} catch {
    Write-Host "  [!] Import failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`n  RECOVERY: Your distribution backup is safe at:" -ForegroundColor Yellow
    Write-Host "  $exportPath" -ForegroundColor Cyan
    Write-Host "`n  You can manually import with:" -ForegroundColor Yellow
    Write-Host "  wsl --import $rancherDistro D:\WSL-Distributions\$rancherDistro $exportPath" -ForegroundColor Cyan
    Read-Host "`nPress Enter to exit"
    exit 1
}

# Verify import
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nCurrent WSL distributions:" -ForegroundColor Yellow
wsl --list -v

# Test access to D: drive from WSL
Write-Host "`nTesting D: drive access from WSL..." -ForegroundColor Yellow
try {
    $testResult = wsl -d $rancherDistro -- ls /mnt/d/ 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] D: drive is accessible from WSL" -ForegroundColor Green
        Write-Host "  [+] D: drive mounts at: /mnt/d/" -ForegroundColor Gray
    } else {
        Write-Host "  [!] Could not access D: drive from WSL" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [!] WSL test failed: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Check disk space usage
Write-Host "`nDisk space usage:" -ForegroundColor Yellow
$importSize = (Get-ChildItem -Path $importPath -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host "  Distribution size on D:: $([math]::Round($importSize, 2)) GB" -ForegroundColor Gray

$dDrive = Get-Volume -DriveLetter D
$freeGB = [math]::Round($dDrive.SizeRemaining / 1GB, 2)
Write-Host "  Free space on D:: ${freeGB} GB" -ForegroundColor Gray

# Cleanup option
Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Cleanup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nThe export backup file is still present:" -ForegroundColor Yellow
Write-Host "  $exportPath" -ForegroundColor Gray
Write-Host "  Size: $([math]::Round($fileSize, 2)) GB" -ForegroundColor Gray

Write-Host "`nDo you want to delete the backup file to save space? (y/n)" -ForegroundColor Yellow
Write-Host "  (Recommended: Keep it until you verify everything works)" -ForegroundColor Gray
$deleteBackup = Read-Host

if ($deleteBackup -eq "y") {
    try {
        Remove-Item -Path $exportPath -Force
        Write-Host "  [+] Backup file deleted" -ForegroundColor Green
    } catch {
        Write-Host "  [!] Could not delete backup: $($_.Exception.Message)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [-] Backup file retained" -ForegroundColor Gray
    Write-Host "  You can manually delete it later if needed" -ForegroundColor Gray
}

Write-Host "`n=====================================" -ForegroundColor Cyan
Write-Host "Phase 3 Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan

Write-Host "`nWSL Distribution successfully moved to D: drive!" -ForegroundColor Green
Write-Host "`nLocation: D:\WSL-Distributions\$rancherDistro" -ForegroundColor Cyan

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Start Rancher Desktop from Start Menu" -ForegroundColor White
Write-Host "2. Wait for it to initialize (it may take longer on first launch)" -ForegroundColor White
Write-Host "3. Verify docker and kubectl are working" -ForegroundColor White
Write-Host "4. Run: 04-configure-storage-locations.ps1" -ForegroundColor White

Write-Host "`nPress Enter to exit..." -ForegroundColor Gray
Read-Host
