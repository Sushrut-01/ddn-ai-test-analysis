@echo off
REM ============================================================================
REM DDN AI Project - File Cleanup Script
REM Removes duplicate and outdated documentation files
REM ============================================================================

echo.
echo ========================================================================
echo   DDN AI Project - File Cleanup
echo ========================================================================
echo.
echo This script will delete 12 duplicate/outdated files:
echo.
echo   Root Level (6 files):
echo   - 00-START-HERE.md
echo   - DEVELOPER-SETUP-GUIDE.md
echo   - SETUP-VERIFICATION.md
echo   - PROJECT-STRUCTURE.md
echo   - QUICK-REFERENCE.md
echo   - QUICK-START.md
echo.
echo   Implementation (3 files):
echo   - implementation\README.md
echo   - implementation\IMPLEMENTATION-GUIDE.md
echo   - implementation\workflows\WORKFLOW-IMPORT-GUIDE.md
echo.
echo   Technical Guides (3 files):
echo   - technical-guides\jenkins-ai-blueprint-md.md
echo   - technical-guides\JENKINS-AI-BLUEPRINT-UPDATED.md
echo   - technical-guides\PHASE3-IMPLEMENTATION-COMPLETE.md
echo.
echo ========================================================================
echo.
echo WARNING: This will permanently delete these files!
echo.

choice /C YN /M "Do you want to create a backup first"
if errorlevel 2 goto SKIP_BACKUP
if errorlevel 1 goto CREATE_BACKUP

:CREATE_BACKUP
echo.
echo Creating backup...
if not exist "backup" mkdir backup
xcopy *.md backup\ /Y >nul 2>&1
xcopy implementation\*.md backup\implementation\ /Y /S >nul 2>&1
xcopy technical-guides\*.md backup\technical-guides\ /Y /S >nul 2>&1
echo [OK] Backup created in: backup\
echo.

:SKIP_BACKUP
echo.
choice /C YN /M "Continue with file deletion"
if errorlevel 2 goto CANCEL
if errorlevel 1 goto DELETE_FILES

:DELETE_FILES
echo.
echo Deleting files...
echo.

REM Root level duplicates
if exist "00-START-HERE.md" (
    del "00-START-HERE.md"
    echo [DELETED] 00-START-HERE.md
) else (
    echo [SKIP] 00-START-HERE.md (not found^)
)

if exist "DEVELOPER-SETUP-GUIDE.md" (
    del "DEVELOPER-SETUP-GUIDE.md"
    echo [DELETED] DEVELOPER-SETUP-GUIDE.md
) else (
    echo [SKIP] DEVELOPER-SETUP-GUIDE.md (not found^)
)

if exist "SETUP-VERIFICATION.md" (
    del "SETUP-VERIFICATION.md"
    echo [DELETED] SETUP-VERIFICATION.md
) else (
    echo [SKIP] SETUP-VERIFICATION.md (not found^)
)

if exist "PROJECT-STRUCTURE.md" (
    del "PROJECT-STRUCTURE.md"
    echo [DELETED] PROJECT-STRUCTURE.md
) else (
    echo [SKIP] PROJECT-STRUCTURE.md (not found^)
)

if exist "QUICK-REFERENCE.md" (
    del "QUICK-REFERENCE.md"
    echo [DELETED] QUICK-REFERENCE.md
) else (
    echo [SKIP] QUICK-REFERENCE.md (not found^)
)

if exist "QUICK-START.md" (
    del "QUICK-START.md"
    echo [DELETED] QUICK-START.md
) else (
    echo [SKIP] QUICK-START.md (not found^)
)

REM Implementation duplicates
if exist "implementation\README.md" (
    del "implementation\README.md"
    echo [DELETED] implementation\README.md
) else (
    echo [SKIP] implementation\README.md (not found^)
)

if exist "implementation\IMPLEMENTATION-GUIDE.md" (
    del "implementation\IMPLEMENTATION-GUIDE.md"
    echo [DELETED] implementation\IMPLEMENTATION-GUIDE.md
) else (
    echo [SKIP] implementation\IMPLEMENTATION-GUIDE.md (not found^)
)

if exist "implementation\workflows\WORKFLOW-IMPORT-GUIDE.md" (
    del "implementation\workflows\WORKFLOW-IMPORT-GUIDE.md"
    echo [DELETED] implementation\workflows\WORKFLOW-IMPORT-GUIDE.md
) else (
    echo [SKIP] implementation\workflows\WORKFLOW-IMPORT-GUIDE.md (not found^)
)

REM Technical guides outdated
if exist "technical-guides\jenkins-ai-blueprint-md.md" (
    del "technical-guides\jenkins-ai-blueprint-md.md"
    echo [DELETED] technical-guides\jenkins-ai-blueprint-md.md
) else (
    echo [SKIP] technical-guides\jenkins-ai-blueprint-md.md (not found^)
)

if exist "technical-guides\JENKINS-AI-BLUEPRINT-UPDATED.md" (
    del "technical-guides\JENKINS-AI-BLUEPRINT-UPDATED.md"
    echo [DELETED] technical-guides\JENKINS-AI-BLUEPRINT-UPDATED.md
) else (
    echo [SKIP] technical-guides\JENKINS-AI-BLUEPRINT-UPDATED.md (not found^)
)

if exist "technical-guides\PHASE3-IMPLEMENTATION-COMPLETE.md" (
    del "technical-guides\PHASE3-IMPLEMENTATION-COMPLETE.md"
    echo [DELETED] technical-guides\PHASE3-IMPLEMENTATION-COMPLETE.md
) else (
    echo [SKIP] technical-guides\PHASE3-IMPLEMENTATION-COMPLETE.md (not found^)
)

echo.
echo ========================================================================
echo   Cleanup Complete!
echo ========================================================================
echo.
echo Essential files remaining:
echo.
echo   Root:
echo   - README.md
echo   - MONGODB-QUICKSTART.md
echo   - COMPLETE-SETUP-CHECKLIST.md
echo   - PROJECT-COMPLETION-SUMMARY.md
echo   - DOCUMENTATION-INDEX.md
echo   - 00-PROJECT-OVERVIEW.md
echo.
echo   Architecture:
echo   - architecture\COMPLETE-ARCHITECTURE.md
echo.
echo   Implementation:
echo   - implementation\workflows\README.md
echo   - implementation\workflows\COMPLETE_SYSTEM_OVERVIEW.md
echo   - implementation\database\mongodb-setup-guide.md
echo   - implementation\dashboard\DASHBOARD_INTEGRATION_GUIDE.md
echo.
echo   Technical:
echo   - technical-guides\MCP-CONNECTOR-GUIDE.md
echo.
echo ========================================================================
echo.
echo Next Steps:
echo   1. Review FILE-CLEANUP-ANALYSIS.md for details
echo   2. Start with: MONGODB-QUICKSTART.md
echo   3. Follow: COMPLETE-SETUP-CHECKLIST.md
echo.

goto END

:CANCEL
echo.
echo [CANCELLED] No files were deleted.
echo.

:END
pause
