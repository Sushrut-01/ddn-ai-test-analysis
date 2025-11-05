@echo off
echo ================================================================================
echo Starting Re-Ranking Service (Phase 2)
echo ================================================================================
echo.

cd /d C:\DDN-AI-Project-Documentation\implementation

echo Checking Python environment...
python --version
echo.

echo Starting reranking service on port 5009...
echo.
echo NOTE: First run will download the CrossEncoder model (~200MB)
echo This may take 1-2 minutes depending on your internet connection.
echo.

python reranking_service.py

pause
