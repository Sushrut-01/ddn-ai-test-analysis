@echo off
REM ===================================================================
REM Import n8n Workflows via CLI (No Browser Needed!)
REM ===================================================================

echo.
echo =====================================================================
echo   n8n Workflow Import - Automated via CLI
echo =====================================================================
echo.

REM Check if n8n is installed
where n8n >nul 2>&1
if errorlevel 1 (
    echo ERROR: n8n CLI not found
    echo.
    echo Install n8n globally:
    echo   npm install -g n8n
    echo.
    pause
    exit /b 1
)

echo n8n CLI found! Proceeding with imports...
echo.

REM Set workflow directory
set WORKFLOW_DIR=.\workflows

REM Import workflows
echo [1/3] Importing Auto-Trigger Workflow...
n8n import:workflow --input="%WORKFLOW_DIR%\ddn_ai_complete_workflow_v2.json"
echo.

echo [2/3] Importing Manual Trigger Workflow...
n8n import:workflow --input="%WORKFLOW_DIR%\workflow_2_manual_trigger.json"
echo.

echo [3/3] Importing Refinement Workflow...
n8n import:workflow --input="%WORKFLOW_DIR%\workflow_3_refinement.json"
echo.

echo =====================================================================
echo   All workflows imported successfully!
echo =====================================================================
echo.
echo Next steps:
echo   1. Start n8n: n8n start
echo   2. Open http://localhost:5678
echo   3. Activate the workflows
echo   4. Configure credentials (MongoDB, Anthropic)
echo.

pause
