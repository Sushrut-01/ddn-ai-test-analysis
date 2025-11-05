@echo off
echo ============================================================
echo DDN AI Test Failure Analysis System - Service Startup Script
echo ============================================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please ensure .env file exists with all required configurations.
    pause
    exit /b 1
)

echo [1/6] Starting PostgreSQL Service...
net start postgresql-x64-18 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] PostgreSQL service started
) else if %ERRORLEVEL% EQU 2182 (
    echo [OK] PostgreSQL already running
) else (
    echo [WARNING] Could not start PostgreSQL - may require admin privileges
)
echo.

echo [2/6] Starting Re-Ranking Service (Port 5009) - Phase 2...
start "Re-Ranking Service" cmd /c "cd implementation && python reranking_service.py"
timeout /t 5 /nobreak > nul
echo [OK] Re-Ranking Service starting on port 5009 (CrossEncoder model loading)...
echo.

echo [3/6] Starting AI Analysis Service (Port 5000)...
start "AI Analysis Service" cmd /c "cd implementation && python ai_analysis_service.py"
timeout /t 3 /nobreak > nul
echo [OK] AI Analysis Service starting on port 5000...
echo.

echo [4/6] Starting Dashboard API (Port 5006)...
start "Dashboard API" cmd /c "cd implementation && python start_dashboard_api_port5006.py"
timeout /t 3 /nobreak > nul
echo [OK] Dashboard API starting on port 5006...
echo.

echo [5/6] Starting Dashboard UI (Port 5173)...
start "Dashboard UI" cmd /c "cd implementation\dashboard-ui && npm run dev"
timeout /t 3 /nobreak > nul
echo [OK] Dashboard UI starting on port 5173...
echo.

echo [6/6] Starting n8n Workflow Service (Port 5678)...
start "n8n Workflows" cmd /c "n8n start"
timeout /t 5 /nobreak > nul
echo [OK] n8n starting on port 5678...
echo.

echo ============================================================
echo All services are starting up!
echo ============================================================
echo.
echo Service URLs:
echo   - Re-Ranking Service:  http://localhost:5009 (Phase 2 - CrossEncoder)
echo   - AI Analysis Service: http://localhost:5000
echo   - Dashboard API:       http://localhost:5006/api
echo   - Dashboard UI:        http://localhost:5173
echo   - n8n Workflows:       http://localhost:5678
echo   - Jenkins:             http://localhost:8081
echo.
echo Database Services:
echo   - PostgreSQL (Docker): localhost:5434
echo   - MongoDB Atlas:       Cloud (ddn-cluster.wudcfln.mongodb.net)
echo   - Pinecone:           Cloud (ddn-error-solutions index)
echo.
echo Press any key to exit...
pause > nul