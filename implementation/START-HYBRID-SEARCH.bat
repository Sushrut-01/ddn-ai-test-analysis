@echo off
echo ========================================
echo Starting Hybrid Search Service (Phase 3)
echo Port: 5005
echo ========================================

cd /d "%~dp0"

echo Checking if port 5005 is already in use...
netstat -ano | findstr ":5005" >nul
if %errorlevel% == 0 (
    echo ERROR: Port 5005 is already in use!
    echo Please stop the existing service first.
    pause
    exit /b 1
)

echo.
echo Starting hybrid_search_service.py...
python hybrid_search_service.py

pause
