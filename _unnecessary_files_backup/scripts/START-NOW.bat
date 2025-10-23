@echo off
cls
color 0A

echo.
echo ========================================
echo   STARTING YOUR REAL DASHBOARD NOW
echo ========================================
echo.
echo Node.js detected! Starting React dashboard...
echo.

cd /d C:\DDN-AI-Project-Documentation\implementation\dashboard-ui

echo Installing dependencies (first time may take 2-3 minutes)...
echo.

call npm install

echo.
echo Starting dashboard...
echo.

call npm run dev

pause
