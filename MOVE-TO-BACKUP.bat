@echo off
cls
color 0A

echo ========================================
echo   MOVING UNNECESSARY FILES TO BACKUP
echo ========================================
echo.
echo This will move 53 unnecessary files to:
echo _unnecessary_files_backup\
echo.
pause

:: Create backup folders
echo Creating backup folders...
mkdir _unnecessary_files_backup 2>nul
mkdir _unnecessary_files_backup\documentation 2>nul
mkdir _unnecessary_files_backup\scripts 2>nul
mkdir _unnecessary_files_backup\html_demos 2>nul
mkdir _unnecessary_files_backup\other 2>nul
echo    [OK] Backup folders created
echo.

:: Move documentation files (28 files)
echo Moving documentation files...
if exist "DASHBOARD-TROUBLESHOOTING.md" move "DASHBOARD-TROUBLESHOOTING.md" "_unnecessary_files_backup\documentation\" >nul
if exist "FIX-DASHBOARD-NOW.md" move "FIX-DASHBOARD-NOW.md" "_unnecessary_files_backup\documentation\" >nul
if exist "MANUAL-DASHBOARD-SETUP.md" move "MANUAL-DASHBOARD-SETUP.md" "_unnecessary_files_backup\documentation\" >nul
if exist "DO-THIS-NOW.md" move "DO-THIS-NOW.md" "_unnecessary_files_backup\documentation\" >nul
if exist "WHAT-TO-EXPECT.md" move "WHAT-TO-EXPECT.md" "_unnecessary_files_backup\documentation\" >nul
if exist "EMERGENCY-HELP.md" move "EMERGENCY-HELP.md" "_unnecessary_files_backup\documentation\" >nul
if exist "GET-REAL-DASHBOARD-WORKING.md" move "GET-REAL-DASHBOARD-WORKING.md" "_unnecessary_files_backup\documentation\" >nul
if exist "SETUP-COMPLETE-SUMMARY.md" move "SETUP-COMPLETE-SUMMARY.md" "_unnecessary_files_backup\documentation\" >nul
if exist "FINAL-CHECKLIST.md" move "FINAL-CHECKLIST.md" "_unnecessary_files_backup\documentation\" >nul
if exist "ONE-COMMAND-SETUP.md" move "ONE-COMMAND-SETUP.md" "_unnecessary_files_backup\documentation\" >nul
if exist "README-FIRST.md" move "README-FIRST.md" "_unnecessary_files_backup\documentation\" >nul
if exist "SYSTEM-READY-SUMMARY.md" move "SYSTEM-READY-SUMMARY.md" "_unnecessary_files_backup\documentation\" >nul
if exist "ACTIVATION-GUIDE.md" move "ACTIVATION-GUIDE.md" "_unnecessary_files_backup\documentation\" >nul
if exist "ARCHITECTURE-DECISION.md" move "ARCHITECTURE-DECISION.md" "_unnecessary_files_backup\documentation\" >nul
if exist "COMPLETE-SETUP-CHECKLIST.md" move "COMPLETE-SETUP-CHECKLIST.md" "_unnecessary_files_backup\documentation\" >nul
if exist "COMPLETE-WORKFLOW.md" move "COMPLETE-WORKFLOW.md" "_unnecessary_files_backup\documentation\" >nul
if exist "DOCUMENTATION-AUDIT-REPORT.md" move "DOCUMENTATION-AUDIT-REPORT.md" "_unnecessary_files_backup\documentation\" >nul
if exist "DOCUMENTATION-CLEANUP-SUMMARY.md" move "DOCUMENTATION-CLEANUP-SUMMARY.md" "_unnecessary_files_backup\documentation\" >nul
if exist "DOCUMENTATION-INDEX.md" move "DOCUMENTATION-INDEX.md" "_unnecessary_files_backup\documentation\" >nul
if exist "FILE-CLEANUP-ANALYSIS.md" move "FILE-CLEANUP-ANALYSIS.md" "_unnecessary_files_backup\documentation\" >nul
if exist "FINAL-DELIVERY-SUMMARY.md" move "FINAL-DELIVERY-SUMMARY.md" "_unnecessary_files_backup\documentation\" >nul
if exist "MONGODB-OPTIONS-GUIDE.md" move "MONGODB-OPTIONS-GUIDE.md" "_unnecessary_files_backup\documentation\" >nul
if exist "MONGODB-QUICKSTART.md" move "MONGODB-QUICKSTART.md" "_unnecessary_files_backup\documentation\" >nul
if exist "QUICK-START-CHECKLIST.md" move "QUICK-START-CHECKLIST.md" "_unnecessary_files_backup\documentation\" >nul
if exist "RAG-ARCHITECTURE-DETAILED.md" move "RAG-ARCHITECTURE-DETAILED.md" "_unnecessary_files_backup\documentation\" >nul
if exist "RAG-COMPLETE-LIFECYCLE.md" move "RAG-COMPLETE-LIFECYCLE.md" "_unnecessary_files_backup\documentation\" >nul
if exist "RAG-MASTER-GUIDE.md" move "RAG-MASTER-GUIDE.md" "_unnecessary_files_backup\documentation\" >nul
if exist "RAG-TECHNICAL-PRESENTATION-GUIDE.md" move "RAG-TECHNICAL-PRESENTATION-GUIDE.md" "_unnecessary_files_backup\documentation\" >nul
if exist "VECTOR-VS-NONVECTOR-DATA.md" move "VECTOR-VS-NONVECTOR-DATA.md" "_unnecessary_files_backup\documentation\" >nul
if exist "VECTORIZATION-STRATEGY-COMPARISON.md" move "VECTORIZATION-STRATEGY-COMPARISON.md" "_unnecessary_files_backup\documentation\" >nul
if exist "WHY-VECTOR-DB-ALONE-WONT-WORK.md" move "WHY-VECTOR-DB-ALONE-WONT-WORK.md" "_unnecessary_files_backup\documentation\" >nul
if exist "WORKFLOW-COMPARISON-SUMMARY.md" move "WORKFLOW-COMPARISON-SUMMARY.md" "_unnecessary_files_backup\documentation\" >nul
if exist "RAG-DATA-SOURCES-EXPLAINED.md" move "RAG-DATA-SOURCES-EXPLAINED.md" "_unnecessary_files_backup\documentation\" >nul
echo    [OK] Documentation files moved
echo.

:: Move BAT scripts (8 files)
echo Moving BAT scripts...
if exist "START-DASHBOARD-ONLY.bat" move "START-DASHBOARD-ONLY.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "CHECK-SYSTEM.bat" move "CHECK-SYSTEM.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "TELL-ME-EXACTLY.bat" move "TELL-ME-EXACTLY.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "ABSOLUTE-SIMPLEST.bat" move "ABSOLUTE-SIMPLEST.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "WORKS-100-PERCENT.bat" move "WORKS-100-PERCENT.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "START-REAL-DASHBOARD.bat" move "START-REAL-DASHBOARD.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "START-NOW.bat" move "START-NOW.bat" "_unnecessary_files_backup\scripts\" >nul
if exist "cleanup-duplicate-files.bat" move "cleanup-duplicate-files.bat" "_unnecessary_files_backup\scripts\" >nul
echo    [OK] BAT scripts moved
echo.

:: Move HTML demo files (4 files)
echo Moving HTML demo files...
if exist "SIMPLE-HTML-DASHBOARD.html" move "SIMPLE-HTML-DASHBOARD.html" "_unnecessary_files_backup\html_demos\" >nul
if exist "INSTANT-DASHBOARD.html" move "INSTANT-DASHBOARD.html" "_unnecessary_files_backup\html_demos\" >nul
if exist "DASHBOARD-BEFORE-AFTER-COMPARISON.html" move "DASHBOARD-BEFORE-AFTER-COMPARISON.html" "_unnecessary_files_backup\html_demos\" >nul
if exist "TEAMS-NOTIFICATION-PREVIEW.html" move "TEAMS-NOTIFICATION-PREVIEW.html" "_unnecessary_files_backup\html_demos\" >nul
echo    [OK] HTML demo files moved
echo.

:: Move other files (13 files)
echo Moving other files...
if exist "Architecture_process.jpg" move "Architecture_process.jpg" "_unnecessary_files_backup\other\" >nul
if exist "Overall-Architecture.jpg" move "Overall-Architecture.jpg" "_unnecessary_files_backup\other\" >nul
if exist "RAG-Architecture-Diagram.jpg" move "RAG-Architecture-Diagram.jpg" "_unnecessary_files_backup\other\" >nul
if exist "RAG-Technical-Deep-Dive.jpg" move "RAG-Technical-Deep-Dive.jpg" "_unnecessary_files_backup\other\" >nul
if exist "VECTOR-VS-NONVECTOR-DIAGRAM.jpg" move "VECTOR-VS-NONVECTOR-DIAGRAM.jpg" "_unnecessary_files_backup\other\" >nul
if exist "WHY-3-DATABASES-NEEDED.jpg" move "WHY-3-DATABASES-NEEDED.jpg" "_unnecessary_files_backup\other\" >nul
if exist "create_detailed_rag_technical.py" move "create_detailed_rag_technical.py" "_unnecessary_files_backup\other\" >nul
if exist "create_overall_architecture.py" move "create_overall_architecture.py" "_unnecessary_files_backup\other\" >nul
if exist "create_updated_rag_diagram.py" move "create_updated_rag_diagram.py" "_unnecessary_files_backup\other\" >nul
if exist "create_vector_decision_diagram.py" move "create_vector_decision_diagram.py" "_unnecessary_files_backup\other\" >nul
if exist "create_why_3databases_diagram.py" move "create_why_3databases_diagram.py" "_unnecessary_files_backup\other\" >nul
if exist "setup-system.sh" move "setup-system.sh" "_unnecessary_files_backup\other\" >nul
if exist "start-dashboard.sh" move "start-dashboard.sh" "_unnecessary_files_backup\other\" >nul
echo    [OK] Other files moved
echo.

echo ========================================
echo   CLEANUP COMPLETE
echo ========================================
echo.
echo All 53 unnecessary files moved to:
echo _unnecessary_files_backup\
echo.
echo Folder structure:
echo   documentation\  (28 files)
echo   scripts\        (8 files)
echo   html_demos\     (4 files)
echo   other\          (13 files)
echo.
echo Your project is now clean and ready for GitHub!
echo.
echo Next step: Run PUSH-TO-GITHUB-NOW.bat
echo.
pause
