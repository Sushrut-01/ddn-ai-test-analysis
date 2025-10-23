@echo off
cls
color 0A

echo ========================================
echo   UPDATE JENKINS JOBS (Windows Fix)
echo ========================================
echo.
echo This will:
echo  1. Delete old Linux-based jobs
echo  2. Create new Windows-compatible jobs
echo.
pause

:: Configuration
set JENKINS_URL=http://localhost:8081
set JENKINS_USER=admin
set /p JENKINS_TOKEN=Enter your Jenkins API Token:

echo.
echo ========================================
echo   Step 1: Deleting Old Jobs
echo ========================================
echo.

echo Deleting DDN-Basic-Tests...
curl -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% "%JENKINS_URL%/job/DDN-Basic-Tests/doDelete"
echo.

echo Deleting DDN-Advanced-Tests...
curl -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% "%JENKINS_URL%/job/DDN-Advanced-Tests/doDelete"
echo.

echo Deleting DDN-Nightly-Tests...
curl -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% "%JENKINS_URL%/job/DDN-Nightly-Tests/doDelete"
echo.

echo ========================================
echo   Step 2: Creating New Windows Jobs
echo ========================================
echo.

echo Creating DDN-Basic-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-basic-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Basic-Tests"
echo [OK]
echo.

echo Creating DDN-Advanced-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-advanced-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Advanced-Tests"
echo [OK]
echo.

echo Creating DDN-Nightly-Tests...
curl -s -X POST -u %JENKINS_USER%:%JENKINS_TOKEN% ^
     -H "Content-Type: application/xml" ^
     --data-binary @jobs\ddn-nightly-tests.xml ^
     "%JENKINS_URL%/createItem?name=DDN-Nightly-Tests"
echo [OK]
echo.

echo ========================================
echo   Jobs Updated Successfully!
echo ========================================
echo.
echo New Windows-compatible jobs created:
echo  - DDN-Basic-Tests
echo  - DDN-Advanced-Tests
echo  - DDN-Nightly-Tests
echo.
echo These jobs now use Windows batch commands
echo and will work correctly on your system!
echo.
pause
