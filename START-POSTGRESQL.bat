@echo off
echo Starting PostgreSQL Service...
echo.

net start postgresql-x64-18

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] PostgreSQL service started successfully!
    echo.
) else if %ERRORLEVEL% EQU 2182 (
    echo.
    echo [OK] PostgreSQL is already running!
    echo.
) else (
    echo.
    echo [ERROR] Failed to start PostgreSQL (Error code: %ERRORLEVEL%)
    echo.
    echo Please check:
    echo 1. Run this script as Administrator
    echo 2. PostgreSQL is installed
    echo 3. Check services.msc for postgresql-x64-18
    echo.
)

pause
