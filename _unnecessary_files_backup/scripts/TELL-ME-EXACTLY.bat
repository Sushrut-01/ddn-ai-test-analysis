@echo off
echo ========================================
echo Dashboard Diagnostic Report
echo ========================================
echo.
echo Please copy ALL of this output and share it!
echo.
echo ========================================
echo 1. SYSTEM CHECK
echo ========================================
echo.

echo Current Directory:
cd
echo.

echo Node.js Check:
where node
if %errorlevel% equ 0 (
    node --version
) else (
    echo NOT INSTALLED - This is the problem!
)
echo.

echo npm Check:
where npm
if %errorlevel% equ 0 (
    npm --version
) else (
    echo NOT INSTALLED
)
echo.

echo Docker Check:
where docker
if %errorlevel% equ 0 (
    docker --version
) else (
    echo NOT INSTALLED
)
echo.

echo ========================================
echo 2. FILE CHECK
echo ========================================
echo.

echo Checking if dashboard folder exists...
if exist implementation\dashboard-ui (
    echo [OK] Dashboard folder exists
    dir implementation\dashboard-ui\package.json
) else (
    echo [ERROR] Dashboard folder NOT FOUND!
)
echo.

echo ========================================
echo 3. PORT CHECK
echo ========================================
echo.

echo Checking port 5173...
netstat -ano | findstr :5173
if %errorlevel% equ 0 (
    echo Port 5173 is IN USE
) else (
    echo Port 5173 is FREE
)
echo.

echo Checking port 3000...
netstat -ano | findstr :3000
if %errorlevel% equ 0 (
    echo Port 3000 is IN USE
) else (
    echo Port 3000 is FREE
)
echo.

echo ========================================
echo 4. TRYING TO START DASHBOARD
echo ========================================
echo.

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Cannot start - Node.js not installed!
    echo.
    echo SOLUTION:
    echo 1. Go to: https://nodejs.org/
    echo 2. Download LTS version
    echo 3. Install it
    echo 4. Restart this terminal
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

echo Node.js found! Attempting to start...
echo.

cd implementation\dashboard-ui
if %errorlevel% neq 0 (
    echo [ERROR] Cannot navigate to dashboard folder!
    pause
    exit /b 1
)

echo Current directory:
cd
echo.

echo Checking for node_modules...
if exist node_modules (
    echo [OK] node_modules exists
) else (
    echo [INFO] node_modules not found, will install...
    echo.
    echo Running npm install...
    call npm install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install FAILED!
        pause
        exit /b 1
    )
)
echo.

echo Starting development server...
echo.
echo If you see "Local: http://localhost:5173/" below, CLICK THAT LINK!
echo.
echo ========================================
echo.

call npm run dev

pause
