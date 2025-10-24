@echo off
color 0A
cls

echo ========================================
echo   PostgreSQL Installation Guide
echo ========================================
echo.
echo This script will guide you through PostgreSQL installation.
echo.
echo STEP 1: Download PostgreSQL
echo ========================================
echo.
echo Please download PostgreSQL 16 (Windows x86-64) from:
echo https://www.postgresql.org/download/windows/
echo.
echo Direct download link:
echo https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
echo.
echo Click on "Windows x86-64" for PostgreSQL 16.x
echo.
pause
echo.

echo STEP 2: Installation Instructions
echo ========================================
echo.
echo During installation:
echo   1. Click "Next" through the wizard
echo   2. Installation Directory: C:\Program Files\PostgreSQL\16
echo   3. Components: Select ALL (PostgreSQL Server, pgAdmin, Command Line Tools)
echo   4. Data Directory: C:\Program Files\PostgreSQL\16\data
echo   5. Password: Enter a password (REMEMBER THIS!)
echo      Suggested password: postgres
echo   6. Port: 5432 (default)
echo   7. Locale: Default locale
echo   8. Click "Next" and then "Finish"
echo.
pause
echo.

echo STEP 3: Verify Installation
echo ========================================
echo.
echo After installation completes, we will verify it works.
echo.
pause

echo.
echo Checking PostgreSQL installation...
echo.

REM Check if PostgreSQL is installed
if exist "C:\Program Files\PostgreSQL\16\bin\psql.exe" (
    echo [OK] PostgreSQL found at: C:\Program Files\PostgreSQL\16
    echo.

    REM Add to PATH temporarily
    set PATH=%PATH%;C:\Program Files\PostgreSQL\16\bin

    echo Testing connection...
    echo.
    psql --version
    echo.

    echo ========================================
    echo   Installation Successful!
    echo ========================================
    echo.
    echo PostgreSQL is installed and ready!
    echo.
    echo Next step: Run SETUP-DATABASE.bat to create the database
    echo.
) else (
    echo [ERROR] PostgreSQL not found!
    echo.
    echo Please install PostgreSQL first, then run this script again.
    echo.
)

pause
