@echo off
REM ===================================================================
REM DDN Aging Service Startup Script
REM Automatically processes old unanalyzed test failures
REM ===================================================================

echo.
echo =====================================================================
echo   DDN AGING SERVICE - Auto-Process Old Failures
echo =====================================================================
echo   Port: 5007
echo   Check Interval: Every 6 hours
echo   Criteria: 2+ failures over 3+ day span
echo   Logic: Groups by build_id, tracks failure patterns
echo =====================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    if exist ".env.MASTER" (
        echo INFO: Copying .env.MASTER to .env
        copy ".env.MASTER" ".env" >nul
    ) else (
        echo WARNING: No .env file found. Using default configuration.
    )
)

REM Install/update dependencies if needed
echo Checking dependencies...
pip install apscheduler pymongo psycopg2-binary requests flask python-dotenv --quiet

REM Start the aging service
echo.
echo Starting Aging Service on port 5007...
echo.
echo Endpoints:
echo   - Health Check: http://localhost:5007/health
echo   - Manual Trigger: POST http://localhost:5007/trigger-now
echo   - Statistics: http://localhost:5007/stats
echo   - Recent Triggers: http://localhost:5007/recent-triggers
echo.
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
python aging_service.py

pause
