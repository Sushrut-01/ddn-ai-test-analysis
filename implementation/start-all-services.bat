@echo off
REM ============================================================================
REM DDN AI Services - Start All
REM Starts all Python services needed for the workflow
REM ============================================================================

echo.
echo ========================================
echo   DDN AI Services - Starting All
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate

echo [1/4] Starting LangGraph Classification Service (Port 5000)...
start "LangGraph Service" cmd /k "cd /d %~dp0 && .venv\Scripts\activate && python langgraph_agent.py"
timeout /t 3 /nobreak >nul

echo [2/4] Starting MongoDB MCP Server (Port 5001)...
start "MongoDB MCP" cmd /k "cd /d %~dp0..\mcp-configs && ..\.venv\Scripts\activate && python mcp_mongodb_server.py"
timeout /t 3 /nobreak >nul

echo [3/4] Starting GitHub MCP Server (Port 5002)...
start "GitHub MCP" cmd /k "cd /d %~dp0..\mcp-configs && ..\..\.venv\Scripts\activate && python mcp_github_server.py"
timeout /t 3 /nobreak >nul

echo [4/4] Starting Pinecone Storage Service (Port 5003)...
start "Pinecone Service" cmd /k "cd /d %~dp0..\mcp-configs && ..\..\.venv\Scripts\activate && python pinecone_storage_service.py"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All Services Started!
echo ========================================
echo.
echo Check each window to verify services started successfully.
echo.
echo Health Check URLs:
echo   - LangGraph:  http://localhost:5000/health
echo   - MongoDB:    http://localhost:5001/health
echo   - GitHub:     http://localhost:5002/health
echo   - Pinecone:   http://localhost:5003/health
echo.
echo Press any key to open health check in browser...
pause >nul

start http://localhost:5000/health
start http://localhost:5001/health
start http://localhost:5002/health
start http://localhost:5003/health

echo.
echo All services are running in separate windows.
echo Close those windows to stop the services.
echo.
pause
