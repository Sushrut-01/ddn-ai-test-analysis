@echo off
REM ============================================================================
REM Start Celery Workers for DDN AI Analysis System
REM PHASE 7: Task Queue System
REM ============================================================================

echo.
echo ========================================
echo Starting Celery Workers
echo ========================================
echo.

REM Check if Redis is running
echo [1/4] Checking Redis connection...
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping(); print('Redis is running')" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Redis is not running!
    echo Please start Redis first:
    echo   - Option 1: redis-server
    echo   - Option 2: docker run -d -p 6379:6379 redis
    echo   - Option 3: wsl -e redis-server
    echo.
    pause
    exit /b 1
)
echo [OK] Redis is running

REM Navigate to implementation directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist "..\venv\Scripts\activate.bat" (
    echo [2/4] Activating virtual environment...
    call ..\venv\Scripts\activate.bat
    echo [OK] Virtual environment activated
) else (
    echo [2/4] No virtual environment found, using system Python
)

REM Set environment variables
echo [3/4] Setting environment variables...
if exist "..\env.MASTER" (
    for /f "usebackq tokens=1,* delims==" %%a in ("..\env.MASTER") do (
        set "%%a=%%b"
    )
    echo [OK] Environment variables loaded
) else (
    echo [WARNING] .env.MASTER not found, using defaults
)

REM Start Celery worker
echo [4/4] Starting Celery workers...
echo.
echo Configuration:
echo   - Workers: 4
echo   - Concurrency: 4
echo   - Pool: solo (Windows compatible)
echo   - Log Level: info
echo.

REM Start worker with Windows-compatible settings
celery -A tasks.celery_tasks worker ^
    --loglevel=info ^
    --concurrency=4 ^
    --pool=solo ^
    --hostname=worker1@%%h ^
    --without-gossip ^
    --without-mingle ^
    --without-heartbeat

REM If worker stops, show error
echo.
echo ========================================
echo Worker Stopped
echo ========================================
pause
