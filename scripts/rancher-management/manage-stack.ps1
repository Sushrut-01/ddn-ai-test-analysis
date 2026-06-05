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
