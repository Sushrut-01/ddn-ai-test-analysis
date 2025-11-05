@echo off
echo ============================================================
echo DDN AI Dashboard - Standalone Startup
echo ============================================================
echo.
echo This will start:
echo   - Dashboard API (Backend) on port 5006
echo   - Dashboard UI (Frontend) on port 5173
echo.

REM Check if .env file exists
if not exist ".env.MASTER" (
    echo [WARNING] .env.MASTER file not found!
    echo Dashboard may not work without environment variables.
)

echo [1/2] Starting Dashboard API (Port 5006)...
start "Dashboard API" cmd /c "cd implementation && python start_dashboard_api_port5006.py"
timeout /t 3 /nobreak > nul
echo [OK] Dashboard API starting on port 5006...
echo.

echo [2/2] Starting Dashboard UI (Port 5173)...
start "Dashboard UI" cmd /c "cd implementation\dashboard-ui && npm run dev"
timeout /t 3 /nobreak > nul
echo [OK] Dashboard UI starting on port 5173...
echo.

echo ============================================================
echo Dashboard is starting up!
echo ============================================================
echo.
echo URLs:
echo   - Dashboard API: http://localhost:5006/api
echo   - Dashboard UI:  http://localhost:5173
echo.
echo Note: The Dashboard requires:
echo   - PostgreSQL running (port 5432)
echo   - MongoDB Atlas connection
echo   - Pinecone connection
echo.
echo Wait 10 seconds, then open: http://localhost:5173
echo.
pause
