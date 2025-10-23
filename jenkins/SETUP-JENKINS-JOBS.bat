@echo off
cls
color 0A

echo ========================================
echo   DDN AI Test Analysis System
echo   Jenkins Jobs Setup Script
echo ========================================
echo.
echo This script will create 3 Jenkins jobs:
echo   1. DDN-Basic-Tests (runs on every commit)
echo   2. DDN-Advanced-Tests (multi-tenancy, security)
echo   3. DDN-Nightly-Tests (comprehensive, runs at 2 AM)
echo.
echo ========================================
echo   Prerequisites
echo ========================================
echo.
echo  1. Jenkins running at http://localhost:8080
echo  2. Jenkins CLI jar downloaded
echo  3. Jenkins credentials configured
echo.

pause

:: Configuration
set JENKINS_URL=http://localhost:8080
set JENKINS_USER=admin
set /p JENKINS_TOKEN=Enter your Jenkins API Token:

echo.
echo ========================================
echo   Step 1: Testing Jenkins Connection
echo ========================================
echo.

curl -s -u %JENKINS_USER%:%JENKINS_TOKEN% %JENKINS_URL%/api/json >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Connected to Jenkins successfully
) else (
    echo [ERROR] Cannot connect to Jenkins
    echo.
    echo Please check:
    echo  1. Jenkins is running at %JENKINS_URL%
    echo  2. Username and token are correct
    echo  3. Network connectivity
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Step 2: Creating Jenkins Jobs
echo ========================================
echo.

:: Job 1: DDN Basic Tests
echo Creating job: DDN-Basic-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-basic-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Basic-Tests"

if %ERRORLEVEL% EQU 0 (
    echo [OK] DDN-Basic-Tests created
) else (
    echo [WARN] Job may already exist or error occurred
)

echo.

:: Job 2: DDN Advanced Tests
echo Creating job: DDN-Advanced-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-advanced-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Advanced-Tests"

if %ERRORLEVEL% EQU 0 (
    echo [OK] DDN-Advanced-Tests created
) else (
    echo [WARN] Job may already exist or error occurred
)

echo.

:: Job 3: DDN Nightly Tests
echo Creating job: DDN-Nightly-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-nightly-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Nightly-Tests"

if %ERRORLEVEL% EQU 0 (
    echo [OK] DDN-Nightly-Tests created
) else (
    echo [WARN] Job may already exist or error occurred
)

echo.
echo ========================================
echo   Step 3: Creating Jenkins Folder
echo ========================================
echo.

echo Creating folder: DDN-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/x-www-form-urlencoded" ^
     --data "mode=com.cloudbees.hudson.plugins.folder.Folder&name=DDN-Tests&Submit=OK" ^
     "%JENKINS_URL%/createItem"

echo [OK] Folder created

echo.
echo ========================================
echo   Step 4: Configuring GitHub Webhook
echo ========================================
echo.

echo To configure GitHub webhook:
echo.
echo 1. Go to your GitHub repository:
echo    https://github.com/Sushrut-01/ddn-ai-test-analysis
echo.
echo 2. Click Settings -^> Webhooks -^> Add webhook
echo.
echo 3. Fill in:
echo    Payload URL: %JENKINS_URL%/github-webhook/
echo    Content type: application/json
echo    Secret: (leave empty or use your secret)
echo    Which events: Just the push event
echo.
echo 4. Click "Add webhook"
echo.

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Jenkins jobs created successfully:
echo.
echo  1. DDN-Basic-Tests
echo     URL: %JENKINS_URL%/job/DDN-Basic-Tests/
echo     Trigger: Every commit to main branch
echo.
echo  2. DDN-Advanced-Tests
echo     URL: %JENKINS_URL%/job/DDN-Advanced-Tests/
echo     Trigger: Every commit + manual
echo.
echo  3. DDN-Nightly-Tests
echo     URL: %JENKINS_URL%/job/DDN-Nightly-Tests/
echo     Trigger: Daily at 2 AM
echo.
echo ========================================
echo   Next Steps
echo ========================================
echo.
echo 1. Open Jenkins: %JENKINS_URL%
echo 2. View jobs in Jenkins dashboard
echo 3. Run a test build manually
echo 4. Configure GitHub webhook (see above)
echo 5. Push code to GitHub to trigger automatic builds
echo.
echo ========================================
echo.

:: Open Jenkins in browser
set /p OPEN_BROWSER=Open Jenkins in browser now? (Y/N):
if /i "%OPEN_BROWSER%"=="Y" (
    start %JENKINS_URL%
)

pause
