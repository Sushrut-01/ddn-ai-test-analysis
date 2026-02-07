# Analytics & PR Workflow Pages - Integration Status & Setup Guide

**Date:** 2026-01-12
**Status:** ⚠️ PARTIALLY INTEGRATED - Database migration required

---

## 📊 Current Integration Status

### ✅ What's Already Implemented

#### 1. **Frontend Pages** (FULLY FUNCTIONAL)
- ✅ `AnalyticsPreview.jsx` - Complete with all charts and metrics
- ✅ `PRWorkflowPreview.jsx` - Complete with PR tracking UI
- ✅ Error handling and fallback data
- ✅ Real-time refresh functionality
- ✅ Empty state handling

#### 2. **Backend API Endpoints** (FULLY IMPLEMENTED)
- ✅ `/api/stats` - System statistics
- ✅ `/api/analytics/summary` - Analytics summary
- ✅ `/api/analytics/trends` - Failure trends
- ✅ `/api/analytics/patterns` - Top failure patterns
- ✅ `/api/analytics/acceptance-rate` - AI acceptance metrics
- ✅ `/api/fixes/history` - PR/fix history
- ✅ `/api/fixes/approve` - Approve code fixes
- ✅ `/api/fixes/reject` - Reject code fixes

#### 3. **Database Tables** (PARTIALLY COMPLETE)
- ✅ `failure_analysis` - Exists but missing columns
- ✅ `code_fix_applications` - Exists but missing columns
- ✅ `acceptance_tracking` - Complete
- ✅ `manual_trigger_log` - Complete
- ✅ All indexes and triggers defined

#### 4. **GitHub PR Integration** (FULLY IMPLEMENTED)
- ✅ `github_client.py` - Complete GitHub API wrapper
  - `create_branch()` - Create feature branches
  - `update_file()` - Commit code changes
  - `create_pull_request()` - Create PRs with reviewers/labels
  - `close_pull_request()` - Close/rollback PRs
- ✅ `code_fix_automation.py` - End-to-end PR creation workflow
  - Fetches approved fixes from database
  - Creates GitHub branches
  - Applies code patches
  - Creates PRs with AI-generated descriptions
  - Tracks all stages in database

---

## ❌ What's Missing (CRITICAL)

### Database Schema Incomplete

The `failure_analysis` and `code_fix_applications` tables are **missing required columns**.

#### Missing Columns in `failure_analysis`:
```sql
- error_type          VARCHAR(255)    -- e.g., "NullPointerException"
- error_message       TEXT            -- Full error message
- component           VARCHAR(255)    -- Affected component/service
- file_path           VARCHAR(500)    -- Source file path
- line_number         INTEGER         -- Error line number
- stack_trace         TEXT            -- Full stack trace
- severity            VARCHAR(20)     -- LOW, MEDIUM, HIGH, CRITICAL
- classification      VARCHAR(50)     -- For analytics (replaces error_category)
- mongodb_failure_id  VARCHAR(255)    -- Link to MongoDB collection
```

#### Missing Columns in `code_fix_applications`:
```sql
- job_name            VARCHAR(255)    -- CI/CD job name
- file_path           VARCHAR(500)    -- File being fixed
- fix_type            VARCHAR(100)    -- Type of fix applied
```

### Impact of Missing Columns:
- ❌ PR creation workflow WILL FAIL
- ❌ Analytics charts show incomplete data
- ❌ PR Workflow page can't fetch proper fix history
- ❌ Code fix automation can't find required fields

---

## 🔧 Setup Instructions

### Step 1: Run Database Migration

**CRITICAL:** Run this migration first before using the pages.

```bash
# Navigate to implementation directory
cd C:\DDN-AI-Project-Documentation\implementation

# Run migration
psql -U postgres -d ddn_ai_analysis -f migrations/add_missing_columns_for_pr_workflow.sql
```

**Or from Python:**
```python
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='ddn_ai_analysis',
    user='postgres',
    password=os.getenv('POSTGRES_PASSWORD')
)

cursor = conn.cursor()
with open('migrations/add_missing_columns_for_pr_workflow.sql', 'r') as f:
    cursor.execute(f.read())
conn.commit()

print("✓ Migration completed successfully!")
```

### Step 2: Verify Database Tables

```sql
-- Check failure_analysis columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'failure_analysis'
ORDER BY column_name;

-- Check code_fix_applications columns
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'code_fix_applications'
ORDER BY column_name;

-- Check if data exists
SELECT COUNT(*) FROM failure_analysis;
SELECT COUNT(*) FROM code_fix_applications;
```

### Step 3: Configure GitHub Integration

Edit `.env` file:

```bash
# GitHub Configuration
GITHUB_TOKEN=your-github-personal-access-token-with-write-permissions
GITHUB_REPO=your-org/your-repo-name
GITHUB_BRANCH=main
GITHUB_FIX_BRANCH_PREFIX=fix/build-
GITHUB_DEFAULT_REVIEWERS=teammate1,teammate2
GITHUB_PR_LABELS=automated-fix,ai-generated,needs-review
GITHUB_AUTO_ASSIGN_REVIEWERS=true
```

**GitHub Token Requirements:**
- Must have `repo` scope (full repository access)
- Must have write permissions
- Get token from: https://github.com/settings/tokens

### Step 4: Start Backend Services

```bash
# Start dashboard API (port 5006)
python dashboard_api_full.py

# Verify API is running
curl http://localhost:5006/api/stats
curl http://localhost:5006/api/fixes/history
```

### Step 5: Start Frontend

```bash
cd implementation/dashboard-ui
npm install
npm run dev
```

Access pages:
- Analytics: `http://localhost:5173/analytics`
- PR Workflow: `http://localhost:5173/pr-workflow`

---

## 📋 Complete End-to-End Flow

### Analytics Page Flow:
```
1. User opens /analytics page
2. Frontend calls:
   - GET /api/stats (system statistics)
   - GET /api/analytics/trends (failure trends)
   - GET /api/analytics/patterns (top patterns)
   - GET /api/analytics/acceptance-rate (AI metrics)
3. Backend queries:
   - failure_analysis table
   - manual_trigger_log table
   - acceptance_tracking table
   - MongoDB test_failures collection
4. Frontend displays:
   - Metric cards (failures, analyses, confidence)
   - Acceptance rate chart
   - Validation distribution pie chart
   - Error category trends bar chart
   - Confidence distribution bars
   - Top failure patterns table
```

### PR Workflow Flow:
```
1. User opens /pr-workflow page
2. Frontend calls:
   - GET /api/fixes/history?limit=50
3. Backend queries:
   - code_fix_applications table
4. Frontend displays:
   - Stats cards (total PRs, merged, in progress, failed)
   - PR workflow stages diagram
   - List of PRs with expandable details
   - Timeline and change statistics

When user approves a fix:
5. Frontend calls:
   - POST /api/fixes/approve {analysis_id, approved_by}
6. Backend (code_fix_automation.py):
   - Fetches fix from failure_analysis table
   - Creates GitHub branch via github_client.py
   - Applies code patch to branch
   - Creates Pull Request on GitHub
   - Updates code_fix_applications table
7. PR appears in GitHub with:
   - AI-generated title and description
   - Code changes committed
   - Reviewers assigned
   - Labels added (automated-fix, ai-generated)
8. Frontend refreshes and shows new PR
```

---

## 🧪 Testing Instructions

### Test 1: Analytics Page

```bash
# 1. Insert test data
psql -U postgres -d ddn_ai_analysis << EOF
INSERT INTO failure_analysis (
    build_id, job_name, error_type, error_message,
    component, file_path, line_number, classification,
    root_cause, fix_recommendation, confidence_score,
    severity, created_at
) VALUES (
    'test-build-001',
    'DDN-Smoke-Tests',
    'NullPointerException',
    'Cannot invoke method on null object',
    'UserService',
    'src/main/java/UserService.java',
    125,
    'CODE_ERROR',
    'Null check missing before method invocation',
    'Add null check: if (user != null) { user.getName(); }',
    0.92,
    'HIGH',
    NOW()
);
EOF

# 2. Open Analytics page
# Navigate to: http://localhost:5173/analytics

# 3. Verify:
# - Total Failures count increases
# - Total Analyzed shows data
# - Charts render with sample data
# - Top Patterns table shows "CODE_ERROR"
```

### Test 2: PR Workflow Page

```bash
# 1. Insert test fix application
psql -U postgres -d ddn_ai_analysis << EOF
INSERT INTO code_fix_applications (
    analysis_id, build_id, approved_by_name, approved_by_email,
    approved_at, branch_name, pr_number, pr_url,
    status, job_name, file_path, fix_type
) VALUES (
    1,
    'test-build-001',
    'Test User',
    'test@example.com',
    NOW(),
    'fix/build-test-build-001',
    123,
    'https://github.com/your-org/your-repo/pull/123',
    'merged',
    'DDN-Smoke-Tests',
    'src/main/java/UserService.java',
    'code_fix'
);
EOF

# 2. Open PR Workflow page
# Navigate to: http://localhost:5173/pr-workflow

# 3. Verify:
# - Total PRs count shows 1
# - Merged count shows 1
# - PR card displays with all details
# - Timeline shows completion stages
```

### Test 3: End-to-End PR Creation

```python
# test_pr_creation.py
from code_fix_automation import CodeFixAutomation

service = CodeFixAutomation()

# Test with actual analysis_id from your database
result = service.apply_approved_fix(
    analysis_id=1,  # Replace with real ID
    approved_by_name="Test User",
    approved_by_email="test@example.com"
)

if result['success']:
    print(f"✓ PR created successfully!")
    print(f"  PR Number: {result['pr_number']}")
    print(f"  PR URL: {result['pr_url']}")
    print(f"  Branch: {result['branch_name']}")
else:
    print(f"✗ Failed: {result['error']}")
```

---

## 🐛 Troubleshooting

### Issue: "No PR data found"
**Cause:** No records in `code_fix_applications` table
**Solution:** Insert test data or approve a fix to create PR

### Issue: "Cannot connect to server"
**Cause:** Backend API not running
**Solution:** Start `python dashboard_api_full.py`

### Issue: PR creation fails with "Column does not exist"
**Cause:** Database migration not run
**Solution:** Run `add_missing_columns_for_pr_workflow.sql`

### Issue: GitHub API error "Bad credentials"
**Cause:** Invalid GITHUB_TOKEN
**Solution:** Generate new token with `repo` scope

### Issue: Charts show no data
**Cause:** No failures in database
**Solution:** Insert test data or trigger actual failures

### Issue: "Database connection failed"
**Cause:** PostgreSQL not running or wrong credentials
**Solution:** Check PostgreSQL service and .env credentials

---

## 📁 File Locations

```
implementation/
├── dashboard_api_full.py                    # Backend API (port 5006)
├── code_fix_automation.py                   # PR creation service
├── github_client.py                         # GitHub API wrapper
├── migrations/
│   ├── add_missing_columns_for_pr_workflow.sql  # CRITICAL MIGRATION
│   ├── add_code_fix_applications_table.sql      # PR tracking table
│   └── add_acceptance_tracking_table.sql        # Analytics table
├── postgresql_schema.sql                    # Base schema
└── dashboard-ui/
    └── src/
        ├── pages/
        │   ├── AnalyticsPreview.jsx         # Analytics page
        │   └── PRWorkflowPreview.jsx        # PR Workflow page
        └── services/
            └── api.js                        # Frontend API client
```

---

## ✅ Verification Checklist

Before deploying to production, verify:

- [ ] Database migration completed successfully
- [ ] All required columns exist in `failure_analysis`
- [ ] All required columns exist in `code_fix_applications`
- [ ] GitHub token configured with write permissions
- [ ] Backend API running on port 5006
- [ ] Frontend can fetch analytics data
- [ ] Frontend can fetch PR history
- [ ] Test PR creation works end-to-end
- [ ] All charts render correctly
- [ ] Empty states display properly
- [ ] Error handling works for network failures

---

## 🎯 Summary

**Current State:**
- ✅ Frontend pages: COMPLETE
- ✅ Backend APIs: COMPLETE
- ✅ GitHub integration: COMPLETE
- ⚠️ Database schema: INCOMPLETE (missing columns)

**To Make It Work:**
1. Run database migration (`add_missing_columns_for_pr_workflow.sql`)
2. Configure GitHub token in `.env`
3. Start backend API
4. Test Analytics and PR Workflow pages

**After Migration:**
- All pages will be fully functional
- PR creation workflow will work end-to-end
- Analytics will show complete data
- Ready for production use

---

**Need Help?** Check the troubleshooting section or review the test instructions above.
