@echo off
echo ===================================
echo    STARTING MONGODB DATABASE
echo ===================================
echo.

echo Checking if MongoDB is already running on port 27017...
netstat -ano | findstr :27017 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ MongoDB is already running on port 27017
    echo MongoDB is ready for connections
    pause
    exit /b 0
)

echo Starting MongoDB v7.0.4...
echo Setting up MongoDB paths...
set MONGODB_HOME=C:\DDN-Project\mongodb
set MONGODB_DATA=C:\DDN-Project\mongodb-data
set MONGODB_LOGS=C:\DDN-Project\logs

echo Creating logs directory if it doesn't exist...
if not exist "%MONGODB_LOGS%" mkdir "%MONGODB_LOGS%"

echo Changing to MongoDB directory...
cd /d "%MONGODB_HOME%\bin"

echo Launching MongoDB daemon...
start "MongoDB Service" cmd /k "mongod.exe --dbpath %MONGODB_DATA% --logpath %MONGODB_LOGS%\mongodb.log --port 27017 --bind_ip 127.0.0.1"

echo.
echo ⏳ Waiting for MongoDB to start (this may take 10-20 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo 🔍 Checking MongoDB startup status...
:CHECK_MONGODB
timeout /t 3 /nobreak >nul
netstat -ano | findstr :27017 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Still starting... Please wait.
    goto CHECK_MONGODB
)

echo.
echo ===================================
echo    ✅ MONGODB STARTED SUCCESSFULLY!
echo ===================================
echo.
echo 🌐 MongoDB Server: mongodb://localhost:27017
echo 📁 Data Directory: %MONGODB_DATA%
echo 📋 Log File: %MONGODB_LOGS%\mongodb.log
echo 🔧 Version: MongoDB v7.0.4
echo.
echo 🔌 Connection Details:
echo    • Host: localhost
echo    • Port: 27017
echo    • Auth: Not required (development mode)
echo.
echo 📊 For n8n Integration:
echo    • Connection String: mongodb://localhost:27017
echo    • Database: Use any name (e.g., 'ddn_database')
echo    • Collection: Auto-created on first insert
echo.
echo 🎯 DDN Collections Ready For:
echo    • Test Results Storage
echo    • Workflow Execution Logs
echo    • Performance Metrics
echo    • Error Analysis Data
echo.
pause