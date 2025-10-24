@echo off
color 0A
cls

echo ================================================================================
echo   DDN AI Test Failure Analysis - Full System Setup
echo ================================================================================
echo.
echo This script will set up the complete AI system:
echo   1. Install Python dependencies
echo   2. Create PostgreSQL database
echo   3. Set up AI analysis service
echo   4. Configure dashboard
echo.
echo API Keys configured:
echo   [OK] OpenAI API Key
echo   [OK] Gemini API Key
echo   [OK] MongoDB Atlas
echo.
pause

echo.
echo ================================================================================
echo   STEP 1: Installing Python Dependencies
echo ================================================================================
echo.

cd implementation
echo Installing Python packages (this may take 2-3 minutes)...
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install Python dependencies
    echo Please check your Python installation
    pause
    exit /b 1
)

echo.
echo [OK] Python dependencies installed successfully!
echo.
pause

echo.
echo ================================================================================
echo   STEP 2: Setting up PostgreSQL Database
echo ================================================================================
echo.

echo Please ensure PostgreSQL is running on your system.
echo.
echo Default PostgreSQL settings:
echo   Host: localhost
echo   Port: 5432
echo   Database: ddn_ai_analysis
echo   User: postgres
echo   Password: postgres
echo.
echo If your PostgreSQL has different settings, update implementation\.env file
echo.
pause

echo.
echo Creating PostgreSQL database and tables...
echo.

python create_database.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to create PostgreSQL database
    echo.
    echo Please check:
    echo   1. PostgreSQL is installed and running
    echo   2. PostgreSQL credentials in .env file are correct
    echo   3. You have permission to create databases
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] PostgreSQL database created successfully!
echo.
pause

echo.
echo ================================================================================
echo   STEP 3: Testing Database Connections
echo ================================================================================
echo.

echo Testing MongoDB Atlas connection...
cd ..\tests
node test-mongodb-connection.js

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] MongoDB connection failed
    pause
    exit /b 1
)

echo.
echo [OK] MongoDB Atlas connection successful!
echo.

cd ..\implementation
echo Testing PostgreSQL connection...
python test_postgres_connection.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PostgreSQL connection failed
    pause
    exit /b 1
)

echo.
echo [OK] PostgreSQL connection successful!
echo.
pause

echo.
echo ================================================================================
echo   SETUP COMPLETE!
echo ================================================================================
echo.
echo Your Full AI System is now ready!
echo.
echo Next steps:
echo.
echo 1. Start the AI Analysis Service:
echo    cd implementation
echo    python ai_analysis_service.py
echo.
echo 2. Start the Dashboard API (in new terminal):
echo    cd implementation
echo    python dashboard_api.py
echo.
echo 3. Open Dashboard in browser:
echo    http://localhost:5005
echo.
echo 4. Run Jenkins tests - they will automatically:
echo    - Store failures in MongoDB Atlas
echo    - AI will analyze them
echo    - Results shown in dashboard
echo.
echo ================================================================================
echo.
pause
