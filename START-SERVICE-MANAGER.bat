@echo off
echo ============================================================
echo Starting Service Manager API (Port 5007)
echo ============================================================
echo.
echo This service provides:
echo - START/STOP/RESTART all services from Dashboard
echo - Service status monitoring
echo - Control panel for PostgreSQL, AI Analysis, Dashboard, n8n, Jenkins
echo.
echo Dashboard Service Control will be available at:
echo http://localhost:5173 (Service Control section)
echo.
echo API Endpoints:
echo http://localhost:5007/api/services/status
echo http://localhost:5007/health
echo.
echo ============================================================
echo.

cd implementation
python service_manager_api.py

pause
