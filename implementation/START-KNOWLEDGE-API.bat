@echo off
REM ============================================================================
REM Start Knowledge Management API
REM Task 0-HITL-KM.1 - Knowledge Management Backend
REM ============================================================================

echo ============================================================================
echo Starting Knowledge Management API
echo ============================================================================
echo.

REM Check if .env file exists
if not exist "..\\.env.MASTER" (
    echo ERROR: .env.MASTER file not found!
    echo Please ensure .env.MASTER exists in the project root.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check required packages
echo Checking required packages...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask is not installed!
    echo Run: pip install flask flask-cors
    pause
    exit /b 1
)

python -c "import openai" >nul 2>&1
if errorlevel 1 (
    echo ERROR: OpenAI package is not installed!
    echo Run: pip install openai
    pause
    exit /b 1
)

python -c "import pinecone" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Pinecone package is not installed!
    echo Run: pip install pinecone-client
    pause
    exit /b 1
)

echo.
echo All dependencies found!
echo.
echo Starting Knowledge Management API on port 5008...
echo Press Ctrl+C to stop the server
echo.

REM Copy .env.MASTER to .env if not exists
if not exist ".env" (
    copy "..\\.env.MASTER" ".env" >nul 2>&1
)

REM Start the API
python knowledge_management_api.py

pause
