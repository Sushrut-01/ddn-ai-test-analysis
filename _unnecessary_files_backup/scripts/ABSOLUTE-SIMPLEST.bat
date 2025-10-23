@echo off
echo.
echo ========================================
echo   SIMPLEST DASHBOARD START
echo ========================================
echo.

:: Step 1: Check Node.js
echo Step 1: Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [X] Node.js is NOT installed!
    echo.
    echo You MUST install Node.js first:
    echo.
    echo 1. Open this link: https://nodejs.org/
    echo 2. Click the big green "Download LTS" button
    echo 3. Run the installer
    echo 4. Click Next, Next, Install
    echo 5. After installation, CLOSE this window
    echo 6. Open a NEW Command Prompt
    echo 7. Run this script again
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js is installed:
node --version
echo.

:: Step 2: Go to dashboard folder
echo Step 2: Going to dashboard folder...
cd /d C:\DDN-AI-Project-Documentation\implementation\dashboard-ui
if %errorlevel% neq 0 (
    echo [X] Cannot find dashboard folder!
    pause
    exit /b 1
)
echo [OK] In dashboard folder
echo.

:: Step 3: Install dependencies if needed
echo Step 3: Checking dependencies...
if not exist node_modules (
    echo Installing dependencies for the first time...
    echo This will take 2-3 minutes. Please wait...
    echo.
    npm install
    echo.
    echo [OK] Dependencies installed!
) else (
    echo [OK] Dependencies already installed
)
echo.

:: Step 4: Start the server
echo Step 4: Starting dashboard server...
echo.
echo ========================================
echo.
echo The dashboard will open at:
echo    http://localhost:5173
echo.
echo When you see "Local: http://localhost:5173"
echo Click that link or open it in your browser!
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm run dev

pause
