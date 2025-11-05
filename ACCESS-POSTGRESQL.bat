@echo off
echo ============================================================
echo PostgreSQL Command Line Access
echo ============================================================
echo.
echo Connecting to PostgreSQL database...
echo Database: ddn_ai_analysis
echo Username: postgres
echo Password: Sharu@051220 (you'll need to enter this when prompted)
echo.

"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d ddn_ai_analysis -h localhost -p 5432

pause