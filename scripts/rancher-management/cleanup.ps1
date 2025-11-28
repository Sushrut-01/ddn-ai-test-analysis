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
