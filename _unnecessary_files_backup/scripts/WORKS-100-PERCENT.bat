@echo off
color 0A
title DDN Dashboard - Auto Launcher

echo.
echo ========================================
echo   DDN DASHBOARD AUTO-LAUNCHER
echo ========================================
echo.
echo This will try EVERY method until one works!
echo.
pause

:: Method 1: Try Python (most systems have this)
echo.
echo [Method 1] Trying Python server...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found! Starting simple dashboard...
    cd C:\DDN-AI-Project-Documentation
    python simple-dashboard-server.py
    exit /b 0
)
echo [SKIP] Python not found, trying next method...

:: Method 2: Try Node.js
echo.
echo [Method 2] Trying Node.js server...
node --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js found! Starting dashboard...
    cd C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
    if not exist node_modules (
        echo Installing dependencies first...
        call npm install
    )
    call npm run dev
    exit /b 0
)
echo [SKIP] Node.js not found, trying next method...

:: Method 3: Try Docker
echo.
echo [Method 3] Trying Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker ps >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Docker running! Starting dashboard...
        cd C:\DDN-AI-Project-Documentation
        docker-compose up -d dashboard-ui
        timeout /t 60
        start http://localhost:3000
        exit /b 0
    )
)
echo [SKIP] Docker not available, trying next method...

:: Method 4: Open static HTML
echo.
echo [Method 4] Opening static HTML dashboard...
echo.
echo NOTE: This is a simple info page, not the full dashboard.
echo For full dashboard, install Node.js from: https://nodejs.org/
echo.
timeout /t 3
start C:\DDN-AI-Project-Documentation\SIMPLE-HTML-DASHBOARD.html
echo.
echo [INFO] Opened static HTML page in your browser.
echo.

:: Final message
echo.
echo ========================================
echo  INSTALLATION NEEDED
echo ========================================
echo.
echo None of the required tools are installed.
echo.
echo To run the dashboard, install ONE of these:
echo.
echo [RECOMMENDED] Node.js
echo   Download: https://nodejs.org/
echo   After install: Run this script again
echo.
echo [ALTERNATIVE] Docker Desktop
echo   Download: https://www.docker.com/products/docker-desktop
echo   After install: Run this script again
echo.
echo ========================================
pause
