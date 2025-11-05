@echo off
echo ============================================================
echo Opening DDN AI Services in Browser
echo ============================================================
echo.

echo Opening Jenkins (try both ports)...
start http://localhost:8080
start http://localhost:8081
echo.

echo Opening other services...
start http://localhost:5173
echo Dashboard UI opened
start http://localhost:5678
echo n8n Workflows opened
echo.

echo ============================================================
echo PostgreSQL Connection Info:
echo ============================================================
echo Host: localhost
echo Port: 5432
echo Database: ddn_ai_analysis
echo Username: postgres
echo Password: Sharu@051220
echo.
echo To connect to PostgreSQL, you need:
echo   - pgAdmin (download from pgadmin.org)
echo   - OR DBeaver (download from dbeaver.io)
echo   - OR use command: psql -U postgres -h localhost -d ddn_ai_analysis
echo.
echo ============================================================
echo All browser windows opened!
echo Check which Jenkins port works (8080 or 8081)
echo ============================================================
pause