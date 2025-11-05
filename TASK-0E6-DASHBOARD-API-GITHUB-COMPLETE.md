# Task 0E.6 Complete: Dashboard API GitHub Integration

**Task ID:** 0E.6
**Task:** Update dashboard_api_full.py to return github_code in API responses
**Date:** 2025-11-02
**Status:** COMPLETED ✅

## Summary

Successfully integrated GitHub source code into Dashboard API responses. GitHub files fetched by ReAct agent (Task 0E.4) and formatted by Gemini (Task 0E.5) now flow through PostgreSQL storage and are returned in all API endpoints for failure analysis.

## Changes Made

### 1. PostgreSQL Schema Migration

**File:** [implementation/add_github_columns_migration.sql](implementation/add_github_columns_migration.sql) (new)

Added two columns to `failure_analysis` table:

```sql
-- GitHub files as JSONB array
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS github_files JSONB DEFAULT '[]'::jsonb;

-- Boolean flag for quick filtering
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS github_code_included BOOLEAN DEFAULT FALSE;

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_failure_analysis_github_code
ON failure_analysis(github_code_included)
WHERE github_code_included = TRUE;
```

**Why JSONB:**
- Structured storage of GitHub file metadata
- Efficient querying and indexing
- Native PostgreSQL JSON support
- Preserves all file information (content, line_range, sha, url, repo, branch)

### 2. Updated ai_analysis_service.py

**File:** [implementation/ai_analysis_service.py](implementation/ai_analysis_service.py)
**Function:** `save_analysis_to_postgres()` (Lines 774-836)

#### Changes:
1. **Extract GitHub data** (Lines 783-789):
```python
# Task 0E.6: Extract GitHub files from analysis (if available)
github_files = analysis.get('github_files', [])
github_code_included = analysis.get('github_code_included', False)

# Convert github_files to JSON string for PostgreSQL JSONB
import json
github_files_json = json.dumps(github_files) if github_files else '[]'
```

2. **Updated INSERT query** (Lines 791-806):
```sql
INSERT INTO failure_analysis (
    mongodb_failure_id,
    classification,
    root_cause,
    severity,
    recommendation,
    confidence_score,
    similar_failures_count,
    analyzed_at,
    ai_model,
    github_files,          -- NEW
    github_code_included   -- NEW
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
```

3. **Enhanced logging** (Lines 827-831):
```python
# Task 0E.6: Log GitHub files inclusion
if github_code_included:
    logger.info(f"Saved analysis to PostgreSQL: ID {analysis_id} (with {len(github_files)} GitHub files)")
else:
    logger.info(f"Saved analysis to PostgreSQL: ID {analysis_id}")
```

### 3. Updated dashboard_api_full.py

**File:** [implementation/dashboard_api_full.py](implementation/dashboard_api_full.py)

#### Endpoint 1: GET /api/failures (Lines 344-360)
**Purpose:** List all test failures with AI analysis

```python
# Task 0E.6: Include GitHub files in query
cursor.execute("""
    SELECT
        classification,
        root_cause,
        severity,
        recommendation,
        confidence_score,
        analyzed_at,
        ai_model,
        github_files,          -- NEW
        github_code_included   -- NEW
    FROM failure_analysis
    WHERE mongodb_failure_id = %s
    ORDER BY analyzed_at DESC
    LIMIT 1
""", (failure['_id'],))
```

**Response Format:**
```json
{
    "failures": [
        {
            "_id": "507f1f77bcf86cd799439011",
            "test_name": "test_storage",
            "error_log": "NullPointerException...",
            "ai_analysis": {
                "classification": "CODE",
                "root_cause": "...",
                "github_files": [
                    {
                        "file_path": "src/storage/DDNStorage.java",
                        "content": "...",
                        "line_range": "Lines 138-148"
                    }
                ],
                "github_code_included": true
            }
        }
    ]
}
```

#### Endpoint 2: GET /api/failures/<failure_id> (Lines 416-433)
**Purpose:** Get detailed information for single failure

```python
# Task 0E.6: Include GitHub files in query
cursor.execute("""
    SELECT
        classification,
        root_cause,
        severity,
        recommendation,
        confidence_score,
        analyzed_at,
        ai_model,
        similar_cases,
        github_files,          -- NEW
        github_code_included   -- NEW
    FROM failure_analysis
    WHERE mongodb_failure_id = %s
    ORDER BY analyzed_at DESC
    LIMIT 1
""", (failure_id,))
```

#### Endpoint 3: GET /api/analysis/<failure_id> (Line 464)
**Already included:** Uses `SELECT *` so automatically includes new columns

## Data Flow

### Complete End-to-End Flow (Tasks 0E.2 → 0E.6)

```
1. Error Detected
   ↓
2. ReAct Agent (Task 0E.4)
   - Classify: CODE_ERROR
   - Fetch GitHub code via GitHubClient
   - Returns github_files array
   ↓
3. ai_analysis_service (Task 0E.5)
   - Format GitHub code for Gemini
   - Enhance analysis with code context
   - Returns analysis with github_files
   ↓
4. save_analysis_to_postgres (Task 0E.6) ← NEW
   - Extract github_files from analysis
   - Store in PostgreSQL as JSONB
   - Set github_code_included flag
   ↓
5. PostgreSQL Database
   - github_files stored as JSONB
   - Indexed for quick filtering
   ↓
6. Dashboard API (Task 0E.6) ← NEW
   - SELECT includes github_files
   - Returns in API response
   ↓
7. Frontend (Tasks 0E.7-0E.8 - Future)
   - Display GitHub code with syntax highlighting
   - Link to repository
```

## GitHub Files Data Structure

### In PostgreSQL (JSONB):
```json
[
    {
        "file_path": "src/storage/DDNStorage.java",
        "content": "public class DDNStorage {\n    private ByteBuffer buffer;\n    ...",
        "total_lines": 245,
        "line_range": "Lines 138-148",
        "sha": "abc123def456",
        "url": "https://github.com/org/repo/blob/main/src/storage/DDNStorage.java",
        "size_bytes": 12450,
        "repo": "your-org/your-repo",
        "branch": "main"
    }
]
```

### API Response Fields:
- `github_files` (array): List of GitHub source files
- `github_code_included` (boolean): Quick check if code was fetched

## Benefits

### 1. Persistent Storage
**Before:** GitHub code only in transient API responses
**After:** Stored in PostgreSQL for historical analysis

### 2. Query Performance
- JSONB indexing for fast lookups
- Boolean flag for quick filtering (`WHERE github_code_included = TRUE`)
- Efficient storage with native PostgreSQL JSON support

### 3. API Completeness
All Dashboard API endpoints now return GitHub code:
- `/api/failures` - List view with code
- `/api/failures/<id>` - Detail view with code
- `/api/analysis/<id>` - Analysis view with code

### 4. Data Consistency
- Single source of truth in PostgreSQL
- GitHub code preserved across sessions
- Historical analysis with code context

## Migration Instructions

### Step 1: Run Migration Script
```bash
cd implementation
psql -U postgres -d ddn_ai_analysis -f add_github_columns_migration.sql
```

**Expected Output:**
```
ALTER TABLE
ALTER TABLE
CREATE INDEX
COMMENT
COMMENT

column_name           | data_type | is_nullable | column_default
----------------------|-----------+-------------+----------------
github_code_included  | boolean   | YES         | false
github_files          | jsonb     | YES         | '[]'::jsonb
```

### Step 2: Restart Services
```bash
# Restart AI Analysis Service (to pick up new code)
cd implementation
python ai_analysis_service.py

# Restart Dashboard API (to pick up new code)
python dashboard_api_full.py
```

### Step 3: Verify Integration
```bash
# Test endpoint returns github_files
curl http://localhost:5006/api/failures | jq '.failures[0].ai_analysis.github_files'
```

## Testing

### Test 1: Check Migration Applied
```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'failure_analysis'
AND column_name IN ('github_files', 'github_code_included');
```

**Expected:** 2 rows returned

### Test 2: Test API Response
```bash
# Get recent failure with AI analysis
curl http://localhost:5006/api/failures?limit=1 | jq '.failures[0].ai_analysis | keys'
```

**Expected:** Includes "github_files" and "github_code_included"

### Test 3: Query GitHub Code
```sql
SELECT
    id,
    mongodb_failure_id,
    classification,
    github_code_included,
    jsonb_array_length(github_files) as file_count
FROM failure_analysis
WHERE github_code_included = TRUE
LIMIT 5;
```

**Expected:** Shows failures with GitHub code count

## Configuration

No additional configuration required. Integration works automatically when:
1. PostgreSQL migration applied ✅
2. ai_analysis_service.py updated ✅
3. dashboard_api_full.py updated ✅
4. Services restarted

**Environment Variables (from previous tasks):**
```bash
# GitHub Integration (Tasks 0E.2-0E.4)
GITHUB_TOKEN=your-github-token
GITHUB_REPO=your-org/your-repo
MCP_GITHUB_SERVER_URL=http://localhost:5002

# PostgreSQL (already configured)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
```

## API Examples

### Example 1: List Failures with GitHub Code
```bash
GET /api/failures?limit=10

Response:
{
    "failures": [
        {
            "_id": "507f1f77bcf86cd799439011",
            "test_name": "test_storage",
            "ai_analysis": {
                "classification": "CODE",
                "root_cause": "Null pointer at DDNStorage.java:142",
                "github_files": [
                    {
                        "file_path": "src/storage/DDNStorage.java",
                        "content": "...",
                        "line_range": "Lines 138-148"
                    }
                ],
                "github_code_included": true
            }
        }
    ],
    "total": 50
}
```

### Example 2: Get Single Failure Detail
```bash
GET /api/failures/507f1f77bcf86cd799439011

Response:
{
    "failure": {
        "_id": "507f1f77bcf86cd799439011",
        "test_name": "test_storage",
        "error_log": "NullPointerException at DDNStorage.java:142",
        "ai_analysis": {
            "classification": "CODE",
            "root_cause": "Null pointer dereference",
            "github_files": [...],
            "github_code_included": true
        }
    }
}
```

### Example 3: Filter by GitHub Code Presence
```sql
-- Backend query to find all CODE_ERROR with GitHub code
SELECT
    mongodb_failure_id,
    classification,
    root_cause,
    jsonb_array_length(github_files) as file_count
FROM failure_analysis
WHERE classification = 'CODE'
AND github_code_included = TRUE
ORDER BY analyzed_at DESC;
```

## Next Steps

### Task 0E.7 (Next - 3 hours)
Create [CodeSnippet.jsx](implementation/dashboard-ui/src/components/CodeSnippet.jsx):
1. Syntax highlighting component (react-syntax-highlighter)
2. Line numbers display
3. Error line highlighting
4. GitHub repository link

### Task 0E.8 (After 0E.7 - 2 hours)
Update [FailureDetails.jsx](implementation/dashboard-ui/src/pages/FailureDetails.jsx):
1. Display GitHub code snippets from API
2. Show file metadata (path, lines, repo)
3. Link to GitHub repository
4. Collapsible code sections

### Task 0E.9 (After 0E.7 - 10 min)
Install dependencies:
```bash
cd dashboard-ui
npm install react-syntax-highlighter
```

## Files Modified

1. **[implementation/add_github_columns_migration.sql](implementation/add_github_columns_migration.sql)** (new)
   - PostgreSQL migration script
   - Adds github_files and github_code_included columns
   - Creates index for performance

2. **[implementation/ai_analysis_service.py](implementation/ai_analysis_service.py)**
   - Lines 774-836: Updated `save_analysis_to_postgres()` function
   - Extracts github_files from analysis
   - Stores in PostgreSQL as JSONB
   - Enhanced logging

3. **[implementation/dashboard_api_full.py](implementation/dashboard_api_full.py)**
   - Lines 344-360: Updated `/api/failures` SELECT statement
   - Lines 416-433: Updated `/api/failures/<id>` SELECT statement
   - Both now include github_files and github_code_included

## Coordination Update

**Session Tasks Completed:**
- Task 0E.2 ✅ Complete (MCP server verification)
- Task 0E.3 ✅ Complete (GitHub client wrapper)
- Task 0E.4 ✅ Complete (ReAct agent integration)
- Task 0E.5 ✅ Complete (Gemini integration)
- Task 0E.6 ✅ Complete (Dashboard API integration)

**Overall Progress:** 27/170 tasks (15.88%)
**Phase 0E Progress:** 6/11 tasks (54.55%)

**Next Available:**
- Task 0E.7 🔜 Ready (CodeSnippet.jsx component)

---
**Completed By:** Claude (Task Execution Agent)
**Completion Date:** 2025-11-02
**Integration Status:** GitHub code flows through full stack (ReAct → ai_analysis → PostgreSQL → Dashboard API) ✅
**Ready for:** Task 0E.7 (Frontend code display component) ✅
