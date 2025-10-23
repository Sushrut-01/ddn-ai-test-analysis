@echo off
REM DDN AI Project - Developer 1 Quick Setup Script
REM Run this script to automatically set up Python environment

echo ========================================
echo DDN AI Project - Developer 1 Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is installed
python --version
echo.

REM Check if we're in the correct directory
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found
    echo Please run this script from the implementation folder
    pause
    exit /b 1
)

echo [OK] In correct directory
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [STEP 1/5] Creating Python virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [SKIP] Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo [STEP 2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo [STEP 3/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded
echo.

REM Install dependencies
echo [STEP 4/5] Installing Python dependencies...
echo This may take a few minutes...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Verify installation
echo [STEP 5/5] Verifying installation...
pip list | findstr langgraph >nul 2>&1
if errorlevel 1 (
    echo [ERROR] LangGraph not found in pip list
    pause
    exit /b 1
)
echo [OK] LangGraph installed successfully
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found
    echo Creating .env from .env.example...
    copy .env.example .env >nul
    echo [ACTION REQUIRED] Please edit .env file with your API keys
    echo.
)

REM Final instructions
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next Steps:
echo 1. Edit .env file with your API keys:
echo    - ANTHROPIC_API_KEY
echo    - OPENAI_API_KEY
echo    - MONGODB_URI
echo    - PINECONE_API_KEY
echo    - GITHUB_TOKEN
echo.
echo 2. Start the LangGraph service:
echo    python langgraph_agent.py
echo.
echo 3. Test health check (in another terminal):
echo    curl http://localhost:5000/health
echo.
echo ========================================
echo.
pause
