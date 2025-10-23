@echo off
cls
color 0B
title Starting REAL React Dashboard

echo.
echo ================================================
echo   STARTING REAL REACT DASHBOARD
echo ================================================
echo.
echo This will start the actual React dashboard
echo with all features and backend connectivity.
echo.
pause

:: Check Node.js
echo [1/4] Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    cls
    color 0C
    echo.
    echo ================================================
    echo   ERROR: NODE.JS NOT INSTALLED!
    echo ================================================
    echo.
    echo You MUST install Node.js to run the real dashboard.
    echo.
    echo STEPS TO INSTALL:
    echo.
    echo 1. Open this link: https://nodejs.org/
    echo 2. Click the BIG GREEN "LTS" button (left side)
    echo 3. Download and run the installer
    echo 4. Click: Next, Next, Install, Finish
    echo 5. RESTART YOUR COMPUTER
    echo 6. Run this script again
    echo.
    echo ================================================
    echo.
    echo Opening Node.js download page in browser...
    timeout /t 3
    start https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo    [OK] Node.js is installed:
node --version
npm --version
echo.

:: Navigate to dashboard
echo [2/4] Navigating to dashboard folder...
cd /d C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
if %errorlevel% neq 0 (
    color 0C
    echo    [ERROR] Cannot find dashboard folder!
    pause
    exit /b 1
)
echo    [OK] In dashboard folder
echo.

:: Install dependencies
echo [3/4] Installing dependencies...
if not exist node_modules (
    echo    This is the first time running.
    echo    Installing React, Vite, and all dependencies...
    echo    This will take 2-3 minutes. Please wait...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        color 0C
        echo.
        echo    [ERROR] npm install failed!
        echo.
        pause
        exit /b 1
    )
    echo.
    echo    [OK] All dependencies installed successfully!
) else (
    echo    [OK] Dependencies already installed (skipping)
)
echo.

:: Start the server
echo [4/4] Starting React development server...
echo.
echo ================================================
echo   REAL DASHBOARD STARTING...
echo ================================================
echo.
echo The dashboard will open automatically at:
echo    http://localhost:5173
echo.
echo Features:
echo  - Full React application
echo  - Live backend API connection
echo  - Real-time data updates
echo  - Manual trigger functionality
echo  - Analytics and reporting
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

:: Start Vite dev server
call npm run dev

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start dashboard!
    pause
    exit /b 1
)

pause
