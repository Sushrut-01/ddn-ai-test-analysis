@echo off
echo ========================================
echo Starting DDN AI Dashboard (Standalone)
echo ========================================
echo.

echo This will start ONLY the dashboard UI for testing.
echo For full system, use COMPLETE-SETUP-WIZARD.bat
echo.

:: Check if Node.js is installed
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Node.js not found!
    echo.
    echo Please install Node.js from: https://nodejs.org/
    echo Then run this script again.
    pause
    exit /b 1
)

echo [OK] Node.js found:
node --version
echo.

:: Navigate to dashboard directory
cd implementation\dashboard-ui

:: Check if node_modules exists
if not exist node_modules (
    echo Installing dependencies (first time only)...
    echo This may take 2-3 minutes...
    echo.
    call npm install
    if %errorlevel% neq 0 (
        echo [X] npm install failed!
        pause
        exit /b 1
    )
    echo.
    echo [OK] Dependencies installed!
    echo.
)

:: Check if .env exists, create if not
if not exist .env (
    echo Creating .env file...
    (
        echo VITE_API_URL=http://localhost:5005
    ) > .env
    echo [OK] .env file created
    echo.
)

echo ========================================
echo Starting Dashboard Development Server
echo ========================================
echo.
echo The dashboard will be available at:
echo.
echo    http://localhost:5173
echo.
echo Note: Port 5173 is Vite's default dev server port
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

:: Start development server
call npm run dev

pause
