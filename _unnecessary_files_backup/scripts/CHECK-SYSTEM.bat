@echo off
echo ========================================
echo System Diagnostic Check
echo ========================================
echo.

echo Checking your system...
echo.

:: Check Node.js
echo [1] Checking Node.js...
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Node.js is installed
    node --version
) else (
    echo     [X] Node.js NOT installed
    echo     Download from: https://nodejs.org/
)
echo.

:: Check npm
echo [2] Checking npm...
where npm >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] npm is installed
    npm --version
) else (
    echo     [X] npm NOT installed
)
echo.

:: Check Docker
echo [3] Checking Docker...
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Docker is installed
    docker --version
    docker ps >nul 2>&1
    if %errorlevel% equ 0 (
        echo     [OK] Docker is RUNNING
    ) else (
        echo     [!] Docker installed but NOT RUNNING
        echo     Please start Docker Desktop
    )
) else (
    echo     [X] Docker NOT installed
    echo     Download from: https://www.docker.com/products/docker-desktop
)
echo.

:: Check Git
echo [4] Checking Git...
where git >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Git is installed
    git --version
) else (
    echo     [!] Git NOT installed (optional)
)
echo.

:: Check Python
echo [5] Checking Python...
where python >nul 2>&1
if %errorlevel% equ 0 (
    echo     [OK] Python is installed
    python --version
) else (
    echo     [!] Python NOT installed (optional)
)
echo.

:: Check ports
echo [6] Checking if ports are available...
netstat -ano | findstr :3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo     [!] Port 3000 is IN USE
    netstat -ano | findstr :3000
) else (
    echo     [OK] Port 3000 is available
)

netstat -ano | findstr :5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo     [!] Port 5173 is IN USE
    netstat -ano | findstr :5173
) else (
    echo     [OK] Port 5173 is available
)
echo.

:: Check dashboard files
echo [7] Checking dashboard files...
if exist implementation\dashboard-ui\package.json (
    echo     [OK] package.json exists
) else (
    echo     [X] package.json NOT FOUND
)

if exist implementation\dashboard-ui\src\main.jsx (
    echo     [OK] main.jsx exists
) else (
    echo     [X] main.jsx NOT FOUND
)

if exist implementation\dashboard-ui\index.html (
    echo     [OK] index.html exists
) else (
    echo     [X] index.html NOT FOUND
)
echo.

:: Summary
echo ========================================
echo Summary
echo ========================================
echo.

where node >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] You CAN run dashboard with Node.js
    echo     Run: START-DASHBOARD-ONLY.bat
    echo     or follow MANUAL-DASHBOARD-SETUP.md
) else (
    echo [X] You CANNOT run dashboard with Node.js
    echo     Install Node.js first: https://nodejs.org/
)
echo.

where docker >nul 2>&1
if %errorlevel% equ 0 (
    docker ps >nul 2>&1
    if %errorlevel% equ 0 (
        echo [✓] You CAN run dashboard with Docker
        echo     Run: docker-compose up -d dashboard-ui
    ) else (
        echo [!] You CAN run with Docker (but start Docker Desktop first)
        echo     Start Docker Desktop, then run: docker-compose up -d
    )
) else (
    echo [X] You CANNOT run dashboard with Docker
    echo     Install Docker Desktop: https://www.docker.com/products/docker-desktop
)
echo.

echo ========================================
echo.
pause
