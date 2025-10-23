@echo off
echo ===================================
echo    STARTING JENKINS SERVICE
echo ===================================
echo.

echo Checking if Jenkins is already running on port 8081...
netstat -ano | findstr :8081 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Jenkins is already running on port 8081
    echo Access Jenkins at: http://localhost:8081
    pause
    exit /b 0
)

echo Starting Jenkins on port 8081...
echo Setting JENKINS_HOME...
set JENKINS_HOME=C:\Users\sushrut.nistane\.jenkins

echo Changing to Jenkins directory...
cd /d "C:\Users\sushrut.nistane\.jenkins"

echo Launching Jenkins with Java 24 compatibility...
start "Jenkins Service" cmd /k "java -jar jenkins.war --httpPort=8081 --enable-future-java"

echo.
echo ⏳ Waiting for Jenkins to start (this may take 30-60 seconds)...
timeout /t 10 /nobreak >nul

echo.
echo 🔍 Checking Jenkins startup status...
:CHECK_JENKINS
timeout /t 5 /nobreak >nul
curl -s http://localhost:8081 >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Still starting... Please wait.
    goto CHECK_JENKINS
)

echo.
echo ===================================
echo    ✅ JENKINS STARTED SUCCESSFULLY!
echo ===================================
echo.
echo 🌐 Jenkins Dashboard: http://localhost:8081
echo 📁 Jenkins Home: %JENKINS_HOME%
echo 📋 Java Version: Java 24 (with future compatibility)
echo.
echo Note: If this is your first time, you may need the initial admin password.
echo Check: %JENKINS_HOME%\secrets\initialAdminPassword
echo.
pause