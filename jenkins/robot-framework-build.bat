@echo off
REM ============================================================================
REM DDN Robot Framework Test - Jenkins Build Command
REM Copy this into Jenkins job configuration
REM ============================================================================

echo =========================================
echo DDN Robot Framework Tests - Build %BUILD_NUMBER%
echo =========================================

REM Set Python path (adjust if needed)
set PYTHON=python
set PIP=pip

REM Install Robot Framework and dependencies
echo Installing Robot Framework...
%PIP% install --upgrade pip
%PIP% install robotframework
%PIP% install robotframework-requests
%PIP% install robotframework-seleniumlibrary
%PIP% install robotframework-databaselibrary
%PIP% install pymongo
%PIP% install python-dotenv

REM Set MongoDB reporter environment
set MONGODB_URI=mongodb+srv://sushrutnistane097_db_user:Sharu@051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true^&w=majority
set MONGODB_DB=ddn_tests

REM Create output directory
if not exist "robot-results" mkdir robot-results

REM Run Robot Framework tests
echo Running Robot Framework tests...
%PYTHON% -m robot ^
  --outputdir robot-results ^
  --output output.xml ^
  --log log.html ^
  --report report.html ^
  --loglevel INFO ^
  --listener implementation\mongodb_robot_listener.py ^
  robot-tests\

echo =========================================
echo Tests completed!
echo =========================================
echo Results saved to robot-results/
