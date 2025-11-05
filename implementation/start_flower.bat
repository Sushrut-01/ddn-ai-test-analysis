@echo off
REM ============================================================================
REM Flower Dashboard Startup Script for Windows
REM ============================================================================
REM This script starts the Flower web dashboard for monitoring Celery workers
REM Dashboard will be available at: http://localhost:5555
REM ============================================================================

echo ========================================
echo Starting Flower Dashboard
echo ========================================
echo.

REM Check if Redis is running
echo [1/4] Checking Redis connection...
redis-cli ping >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Redis is not running!
    echo.
    echo Please start Redis first:
    echo   Option 1: docker run -d -p 6379:6379 redis
    echo   Option 2: wsl -e redis-server
    echo   Option 3: Start Memurai Windows service
    echo.
    pause
    exit /b 1
)
echo [OK] Redis is running
echo.

REM Activate virtual environment if it exists
echo [2/4] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [WARNING] Virtual environment not found, using global Python
)
echo.

REM Load environment variables from .env file
echo [3/4] Loading environment variables...
if exist ".env" (
    for /f "usebackq tokens=*" %%a in (".env") do (
        echo %%a | findstr /r "^[^#]" >nul
        if not errorlevel 1 set %%a
    )
    echo [OK] Environment variables loaded from .env
) else if exist ".env.MASTER" (
    for /f "usebackq tokens=*" %%a in (".env.MASTER") do (
        echo %%a | findstr /r "^[^#]" >nul
        if not errorlevel 1 set %%a
    )
    echo [OK] Environment variables loaded from .env.MASTER
) else (
    echo [WARNING] No .env file found, using defaults
)
echo.

REM Set default port if not set
if not defined FLOWER_PORT set FLOWER_PORT=5555

REM Start Flower
echo [4/4] Starting Flower Dashboard...
echo.
echo ============================================
echo Flower Configuration:
echo   - Port: %FLOWER_PORT%
echo   - URL: http://localhost:%FLOWER_PORT%
echo   - Broker: %REDIS_URL%
echo   - Tasks: Monitoring all Celery tasks
echo ============================================
echo.
echo Press Ctrl+C to stop Flower
echo.

REM Start Flower with Windows-compatible settings
celery -A tasks.celery_tasks flower --port=%FLOWER_PORT%

REM If Flower exits, show message
echo.
echo ========================================
echo Flower Dashboard stopped
echo ========================================
pause
