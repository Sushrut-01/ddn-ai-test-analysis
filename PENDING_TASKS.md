# Pending Tasks - Architecture Implementation
## What's Left to Complete

**Date:** 2026-02-02
**Status:** Database Secured ✅ | API Integration Pending ⏳

---

## 🎯 QUICK SUMMARY

### ✅ COMPLETED (By Architect)
- Database security (RLS applied to 9 tables)
- Schema fixes (5 tables got project_id)
- Middleware code created (650 lines, production-ready)
- Documentation (5 comprehensive guides)
- Performance indexes

### ⏳ PENDING (Your Team's Work)
- Integrate middleware into 20+ API endpoints
- Test RLS enforcement
- MongoDB database-per-project migration
- Frontend updates
- API refactoring (break down 251KB file)

---

## 📋 DETAILED PENDING TASKS

### 🔴 CRITICAL (Must Do This Week)

#### Task 1: Fix PostgreSQL Connection Issue
**Status:** ⏳ BLOCKED - PostgreSQL connection failing
**Priority:** P0 - CRITICAL
**Time:** 10 minutes
**Owner:** DevOps/You

**Problem:**
```
connection to server at "127.0.0.1", port 5434 failed:
server closed the connection unexpectedly
```

**Solution:**
```bash
# Option 1: Restart PostgreSQL service
docker restart ddn-postgres

# Option 2: Check if PostgreSQL is running
docker ps | grep postgres

# Option 3: Check logs
docker logs ddn-postgres

# After restart, test connection:
cd implementation/migrations
python check_database_state.py
```

**Impact:** Cannot test RLS enforcement until fixed

---

#### Task 2: Test RLS Enforcement
**Status:** ⏳ PENDING (waiting for Task 1)
**Priority:** P0 - CRITICAL
**Time:** 5 minutes
**Owner:** You

**Command:**
```bash
cd implementation/migrations
python test_rls_enforcement.py
```

**Expected Output:**
```
[TEST 1] Query without project context → Returns all projects
[TEST 2] Set context to project 1 → Returns only project 1
[TEST 3] Set context to project 2 → Returns only project 2
[SUCCESS] RLS IS WORKING CORRECTLY
```

**If Test Fails:**
- Check if RLS migration was applied
- Check PostgreSQL logs
- Run: `python check_database_state.py`

---

#### Task 3: Integrate Middleware into 5 Critical Endpoints
**Status:** ⏳ PENDING
**Priority:** P0 - CRITICAL
**Time:** 4 hours
**Owner:** Backend Team

**Endpoints to Update:**

##### 3.1 Failures Endpoint
**File:** `implementation/dashboard_api_full.py` (line ~3000-3100)

**Current Code:**
```python
@app.route('/api/failures', methods=['GET'])
def get_failures():
    # 45 lines of manual validation...
    project_id = request.args.get('project_id', 1)  # UNSAFE!
    # ...
```

**New Code:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # Remove all manual validation - middleware handles it
    # Use g.project_id instead of parameter

    conn = get_db_connection()
    cur = conn.cursor()

    # RLS automatically filters - no WHERE clause needed!
    cur.execute("""
        SELECT * FROM failure_analysis
        ORDER BY created_at DESC
        LIMIT 50
    """)

    failures = cur.fetchall()

    return jsonify({
        'project_id': g.project_id,
        'your_role': g.project_role,
        'failures': failures
    })
```

**Testing:**
```bash
# As DDN user (project 1)
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5006/api/projects/1/failures

# Try to access Guruttava (project 2) - should get 403
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:5006/api/projects/2/failures
```

---

##### 3.2 Manual Trigger Endpoint
**File:** `implementation/manual_trigger_api.py` (line 767)

**Current Code:**
```python
@app.route('/api/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    data = request.get_json()
    project_id = data.get('project_id', 1)  # UNSAFE DEFAULT!
    # 50+ lines...
```

**New Code:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/trigger-analysis', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')  # Need developer role
def trigger_manual_analysis(project_id):
    data = request.get_json()
    build_id = data['build_id']

    # Use g.project_id for queries
    # Middleware already validated access

    # Your existing analysis logic...
    return jsonify({'status': 'started', 'project_id': g.project_id})
```

---

##### 3.3 Jira Integration
**File:** `implementation/jira_integration_service.py` (line 80)

**Current Code:**
```python
@app.route('/api/jira/create-issue', methods=['POST'])
def create_jira_issue():
    data = request.get_json()
    project_id = data.get('project_id', 1)  # Default to DDN
    # ...
```

**New Code:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/jira/create-issue', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def create_jira_issue(project_id):
    data = request.get_json()

    # Get project-specific Jira config (RLS filtered automatically)
    conn = get_postgres_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT jira_project_key, jira_url, jira_email
        FROM project_configurations
    """)  # No WHERE needed - RLS handles it!

    config = cursor.fetchone()
    # ... create Jira issue with config
```

---

##### 3.4 Project Configuration
**File:** `implementation/dashboard_api_full.py` (search for `/config`)

**Current Code:**
```python
@app.route('/api/config', methods=['GET'])
def get_config():
    # Manual validation...
```

**New Code:**
```python
@app.route('/api/projects/<int:project_id>/config', methods=['GET'])
@require_auth
@require_project_access(required_role='project_admin')  # Admin only
def get_config(project_id):
    # Only admins can view config
    # RLS ensures they see only their project's config
    pass
```

---

##### 3.5 Analytics Dashboard
**File:** `implementation/dashboard_api_full.py` (search for `/analytics`)

**Current Code:**
```python
@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    # Manual validation...
```

**New Code:**
```python
@app.route('/api/projects/<int:project_id>/analytics', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_analytics(project_id):
    # RLS automatically filters all queries
    pass
```

---

### 🟡 HIGH PRIORITY (This Week)

#### Task 4: Update Frontend API Calls
**Status:** ⏳ PENDING
**Priority:** P1 - HIGH
**Time:** 2 hours
**Owner:** Frontend Team

**Files to Update:**
- `implementation/dashboard-ui/src/services/api.js`
- All React components that call API

**Changes Needed:**

**Current Frontend Code:**
```javascript
// BEFORE: No project context
fetch('/api/failures?project_id=1')
```

**New Frontend Code:**
```javascript
// AFTER: Project ID in URL path
const projectId = localStorage.getItem('currentProjectId') || 1;
fetch(`/api/projects/${projectId}/failures`)
```

**Implementation:**
```javascript
// src/services/api.js
export const API_BASE = 'http://localhost:5006';

// Get current project from context/localStorage
export const getCurrentProjectId = () => {
  return parseInt(localStorage.getItem('currentProjectId') || '1');
};

// Updated API calls
export const getFailures = async () => {
  const projectId = getCurrentProjectId();
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/failures`, {
    headers: {
      'Authorization': `Bearer ${getToken()}`
    }
  });
  return response.json();
};

export const triggerAnalysis = async (buildId) => {
  const projectId = getCurrentProjectId();
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/trigger-analysis`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ build_id: buildId })
  });
  return response.json();
};
```

---

#### Task 5: Add Integration Tests
**Status:** ⏳ PENDING
**Priority:** P1 - HIGH
**Time:** 3 hours
**Owner:** QA/Backend Team

**Create:** `implementation/tests/test_project_isolation.py`

```python
"""
Integration tests for project isolation
"""

import pytest
import requests

BASE_URL = 'http://localhost:5006'

def test_user_cannot_access_other_project():
    """User from project 1 cannot access project 2"""
    # Login as DDN user (project 1)
    token = login('ddn_user@company.com', 'password')

    # Try to access Guruttava data (project 2)
    response = requests.get(
        f'{BASE_URL}/api/projects/2/failures',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    assert 'Access denied' in response.json()['error']

def test_rls_prevents_data_leakage():
    """RLS prevents data leakage even with direct database access"""
    # This test requires database connection
    conn = get_db_connection()
    cur = conn.cursor()

    # Set context to project 1
    cur.execute("SELECT set_project_context(1)")

    # Query without WHERE clause
    cur.execute("SELECT DISTINCT project_id FROM failure_analysis")
    results = [row[0] for row in cur.fetchall()]

    # Should only see project 1
    assert results == [1], f"RLS failed! Saw: {results}"

def test_viewer_cannot_trigger_analysis():
    """Viewer role cannot trigger analysis"""
    token = login('viewer@company.com', 'password')

    response = requests.post(
        f'{BASE_URL}/api/projects/1/trigger-analysis',
        headers={'Authorization': f'Bearer {token}'},
        json={'build_id': 'TEST-123'}
    )

    assert response.status_code == 403
    assert 'developer role' in response.json()['error']
```

**Run Tests:**
```bash
cd implementation
pytest tests/test_project_isolation.py -v
```

---

### 🟢 MEDIUM PRIORITY (Next Week)

#### Task 6: MongoDB Database-Per-Project Migration
**Status:** ⏳ PENDING
**Priority:** P2 - MEDIUM
**Time:** 1 day
**Owner:** Backend Team

**Current State:**
```
MongoDB: ddn_tests (single database)
├── ddn_test_failures          ← DDN data
├── ddn_build_results
├── guruttava_test_failures    ← Guruttava data
└── guruttava_build_results
```

**Target State:**
```
MongoDB Cluster:
├── ddn_project_db             ← DDN database
│   ├── test_failures
│   └── build_results
└── guruttava_project_db       ← Guruttava database
    ├── test_failures
    └── build_results
```

**Migration Script:**
```python
# implementation/migrations/migrate_mongodb_to_databases.py

from pymongo import MongoClient
from middleware import MongoDBProjectContext

def migrate_to_databases():
    """Migrate from collection prefixes to separate databases"""

    client = MongoClient(MONGODB_URI)
    old_db = client['ddn_tests']

    # Migrate DDN data
    ddn_db_name = MongoDBProjectContext.get_database_name(1)
    ddn_db = client[ddn_db_name]

    # Copy ddn_test_failures → ddn_project_db.test_failures
    old_db['ddn_test_failures'].aggregate([
        {'$out': {'db': ddn_db_name, 'coll': 'test_failures'}}
    ])

    # Migrate Guruttava data
    guru_db_name = MongoDBProjectContext.get_database_name(2)
    guru_db = client[guru_db_name]

    old_db['guruttava_test_failures'].aggregate([
        {'$out': {'db': guru_db_name, 'coll': 'test_failures'}}
    ])

    print("Migration complete!")
```

---

#### Task 7: Break Down Monolithic API
**Status:** ⏳ PENDING
**Priority:** P2 - MEDIUM
**Time:** 1 week
**Owner:** Backend Team Lead

**Current:**
```
dashboard_api_full.py (251KB - MONOLITH!)
```

**Target:**
```
services/
├── failures_service.py      (Port 5018) - Failure endpoints
├── analytics_service.py     (Port 5019) - Analytics endpoints
├── trigger_service.py       (Port 5004) - Already exists
├── jira_service.py          (Port 5009) - Already exists
└── api_gateway.py           (Port 5006) - Route requests
```

**Steps:**
1. Extract failures endpoints → `failures_service.py`
2. Extract analytics endpoints → `analytics_service.py`
3. Update `api_gateway.py` to proxy requests
4. Update `docker-compose.yml` with new services
5. Test each service independently

---

#### Task 8: Add Connection Pooling
**Status:** ⏳ PENDING
**Priority:** P2 - MEDIUM
**Time:** 2 hours
**Owner:** Backend Team

**Create:** `implementation/utils/db_pool.py`

```python
from psycopg2 import pool
import os

class DatabasePool:
    _instance = None
    _pool = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._pool = pool.ThreadedConnectionPool(
                minconn=5,
                maxconn=20,
                host=os.getenv('POSTGRES_HOST'),
                database=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD')
            )
        return cls._instance

    def get_connection(self):
        return self._pool.getconn()

    def return_connection(self, conn):
        self._pool.putconn(conn)

# Usage in services
db_pool = DatabasePool()

def get_db_connection():
    return db_pool.get_connection()
```

---

### 🔵 LOW PRIORITY (Later)

#### Task 9: Add Request Validation (Pydantic)
**Status:** ⏳ PENDING
**Priority:** P3 - LOW
**Time:** 1 day

**Example:**
```python
from pydantic import BaseModel, Field

class TriggerAnalysisRequest(BaseModel):
    build_id: str = Field(..., min_length=1, max_length=100)
    force_reanalysis: bool = False

@app.route('/api/projects/<int:project_id>/trigger', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def trigger_analysis(project_id):
    data = TriggerAnalysisRequest(**request.json)
    # data.build_id is now validated
```

---

#### Task 10: Add Rate Limiting
**Status:** ⏳ PENDING
**Priority:** P3 - LOW
**Time:** 1 day

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    storage_uri="redis://redis:6379/0"
)

@app.route('/api/projects/<int:project_id>/trigger', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit expensive operations
@require_auth
@require_project_access(required_role='developer')
def trigger_analysis(project_id):
    pass
```

---

## 📊 PROGRESS TRACKER

### Overall Progress

```
Phase 1: Database Security    [████████████████████] 100% ✅
Phase 2: Middleware Creation   [████████████████████] 100% ✅
Phase 3: API Integration       [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
Phase 4: Testing               [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
Phase 5: MongoDB Migration     [░░░░░░░░░░░░░░░░░░░░]   0% ⏳
Phase 6: API Refactoring       [░░░░░░░░░░░░░░░░░░░░]   0% ⏳

Overall: 33% Complete
```

### By Priority

```
P0 - CRITICAL (5 tasks):     [████░░░░░░░░░░░░░░░░]  20% (1/5 done)
P1 - HIGH (5 tasks):         [░░░░░░░░░░░░░░░░░░░░]   0% (0/5 done)
P2 - MEDIUM (4 tasks):       [░░░░░░░░░░░░░░░░░░░░]   0% (0/4 done)
P3 - LOW (2 tasks):          [░░░░░░░░░░░░░░░░░░░░]   0% (0/2 done)
```

---

## ⏱️ TIME ESTIMATES

### This Week (40 hours total):
```
Task 1: Fix PostgreSQL       0.5h  ← BLOCKING
Task 2: Test RLS             0.5h
Task 3: Integrate 5 endpoints 4h
Task 4: Update frontend      2h
Task 5: Integration tests    3h
────────────────────────────────
Total:                       10h
```

### Next Week (40 hours total):
```
Task 6: MongoDB migration    8h
Task 7: API refactoring      40h (full week)
────────────────────────────────
Total:                       48h
```

### Later (as needed):
```
Task 8: Connection pooling   2h
Task 9: Request validation   8h
Task 10: Rate limiting       8h
```

---

## 🎯 SUCCESS CRITERIA

**Week 1 Complete When:**
- [ ] PostgreSQL connection working
- [ ] RLS test passes
- [ ] 5 endpoints using middleware
- [ ] Frontend updated
- [ ] Integration tests passing

**Week 2 Complete When:**
- [ ] MongoDB migrated to database-per-project
- [ ] API broken into microservices
- [ ] All endpoints using middleware
- [ ] Performance tested

**Project Complete When:**
- [ ] All endpoints refactored
- [ ] Connection pooling implemented
- [ ] Request validation added
- [ ] Rate limiting added
- [ ] Security audit passed

---

## 📞 WHO DOES WHAT

### DevOps:
- Task 1: Fix PostgreSQL connection
- Task 6: MongoDB migration (assist)
- Task 7: Docker compose updates

### Backend Team:
- Task 3: Integrate middleware (5 endpoints)
- Task 5: Integration tests
- Task 6: MongoDB migration
- Task 7: API refactoring
- Task 8: Connection pooling

### Frontend Team:
- Task 4: Update API calls
- Task 4: Add project selector UI

### QA Team:
- Task 2: Test RLS enforcement
- Task 5: Integration tests
- All: Test each phase

---

## 🔥 BLOCKERS

### Current Blockers:
1. **PostgreSQL Connection Issue** - BLOCKING Task 2
   - Impact: Cannot test RLS
   - Fix: Restart PostgreSQL
   - Owner: DevOps/You
   - ETA: 10 minutes

### Potential Blockers:
1. **Team Availability** - Who will do Task 3?
2. **Frontend Dependencies** - Need project selector UI?
3. **MongoDB Downtime** - Need maintenance window for Task 6?

---

## 📋 QUICK ACTION CHECKLIST

**Right Now (Next 30 Minutes):**
- [ ] Restart PostgreSQL: `docker restart ddn-postgres`
- [ ] Test connection: `python migrations/check_database_state.py`
- [ ] Test RLS: `python migrations/test_rls_enforcement.py`
- [ ] Read integration guide: `MIDDLEWARE_INTEGRATION_GUIDE.md`

**Today:**
- [ ] Assign Task 3 to backend developer
- [ ] Assign Task 4 to frontend developer
- [ ] Schedule standup to review progress
- [ ] Create tickets in Jira for each task

**This Week:**
- [ ] Complete Tasks 1-5 (Critical + High priority)
- [ ] Daily standups to track progress
- [ ] Test on staging environment
- [ ] Prepare for production deployment

---

## 📄 REFERENCE DOCUMENTS

1. **ARCHITECT_WORK_COMPLETED.md** - What's been done
2. **MIDDLEWARE_INTEGRATION_GUIDE.md** - How to integrate
3. **MIDDLEWARE_QUICK_REFERENCE.md** - Copy-paste examples
4. **ARCHITECTURAL_ANALYSIS_REPORT.md** - Why these changes
5. **FUNCTIONAL_FLOW_ANALYSIS.md** - How system works
6. **THIS FILE** - What's pending

---

## ✅ COMPLETION CHECKLIST

When all tasks done, verify:
- [ ] All endpoints use middleware
- [ ] All tests passing
- [ ] MongoDB uses database-per-project
- [ ] API broken into microservices
- [ ] Connection pooling working
- [ ] Request validation added
- [ ] Rate limiting configured
- [ ] Documentation updated
- [ ] Team trained on new patterns
- [ ] Production deployment successful

---

**Last Updated:** 2026-02-02
**Next Review:** After Task 3 completion
**Owner:** You (coordinate with team)
