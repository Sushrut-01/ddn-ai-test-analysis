# Middleware Integration Guide
## How to Integrate Project Context Middleware into Existing APIs

**Date:** 2026-02-02
**Status:** Ready for Review

---

## BEFORE vs AFTER Comparison

### BEFORE: Manual Validation (Current Code)

```python
# dashboard_api_full.py (Current approach - INCONSISTENT)

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
def get_failures(project_id):
    # Manual token extraction
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'error': 'Auth required'}), 401

    # Manual token validation
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
    except:
        return jsonify({'error': 'Invalid token'}), 401

    # Manual project access check
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT role FROM user_projects
        WHERE user_id = %s AND project_id = %s
    """, (user_id, project_id))

    result = cur.fetchone()
    if not result:
        return jsonify({'error': 'Access denied'}), 403

    # Manual query with WHERE clause (EASY TO FORGET!)
    cur.execute("""
        SELECT * FROM failure_analysis
        WHERE project_id = %s
        ORDER BY created_at DESC
    """, (project_id,))

    failures = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({'failures': failures})
```

**Problems:**
- 🔴 20+ lines of boilerplate per endpoint
- 🔴 Easy to forget `WHERE project_id = ?`
- 🔴 Inconsistent validation across endpoints
- 🔴 No audit trail
- 🔴 No RLS enforcement

---

### AFTER: Using Middleware (Clean & Secure)

```python
# dashboard_api_refactored.py (New approach - CONSISTENT)

from middleware import require_auth, require_project_access

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # That's it! All validation done by decorators

    # g.project_id is validated
    # g.project_role contains user's role
    # PostgreSQL RLS automatically filters

    conn = get_db_connection()
    cur = conn.cursor()

    # No WHERE clause needed - RLS handles it!
    cur.execute("""
        SELECT * FROM failure_analysis
        ORDER BY created_at DESC
    """)

    failures = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({
        'project_id': g.project_id,
        'your_role': g.project_role,
        'failures': failures
    })
```

**Benefits:**
- ✅ 3 lines instead of 20+
- ✅ Impossible to forget WHERE clause (RLS enforces it)
- ✅ Consistent validation everywhere
- ✅ Automatic audit trail (last_accessed_at updated)
- ✅ Database-level security (RLS)

---

## Integration Steps

### Step 1: Apply RLS Migration

```bash
# Run this FIRST to enable Row-Level Security
psql -U postgres -d ddn_ai_analysis -f implementation/migrations/003_enable_row_level_security.sql
```

**This enables:**
- Automatic project filtering at database level
- Session variable `set_project_context(project_id)`
- RLS policies on all multi-tenant tables

---

### Step 2: Update Existing Endpoints

#### Example 1: Failures Endpoint

**File:** `dashboard_api_full.py:1234`

**BEFORE:**
```python
@app.route('/api/failures', methods=['GET'])
def get_all_failures():
    # Manual validation here (50 lines)...
    project_id = request.args.get('project_id', 1)  # Unsafe default!
    # ...
```

**AFTER:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_all_failures(project_id):
    # g.project_id, g.project_role available
    # RLS automatically filters
    pass
```

---

#### Example 2: Manual Trigger Endpoint

**File:** `manual_trigger_api.py:767`

**BEFORE:**
```python
@app.route('/api/trigger-manual', methods=['POST'])
def trigger_manual_analysis():
    data = request.json
    project_id = data.get('project_id', 1)  # Unsafe default!

    # No validation of project access!
    build_id = data.get('build_id')
    # ...
```

**AFTER:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/trigger-manual', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')  # Need developer role to trigger
def trigger_manual_analysis(project_id):
    data = request.json
    build_id = data['build_id']

    # g.project_id validated
    # Use project-specific configs
    # ...
```

---

#### Example 3: Jira Integration

**File:** `jira_integration_service.py:80`

**BEFORE:**
```python
@app.route('/api/jira/create-issue', methods=['POST'])
def create_jira_issue():
    data = request.get_json()
    project_id = data.get('project_id', 1)  # Default to DDN

    # Get project config from DB
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT jira_project_key, jira_url
        FROM project_configurations
        WHERE project_id = %s
    """, (project_id,))
    # ...
```

**AFTER:**
```python
from middleware import require_auth, require_project_access
from flask import g

@app.route('/api/projects/<int:project_id>/jira/create-issue', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def create_jira_issue(project_id):
    data = request.get_json()

    # g.project_id validated
    # g.project_info contains project config

    # Get project-specific Jira config (RLS filtered)
    conn = get_postgres_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT jira_project_key, jira_url
        FROM project_configurations
    """)  # No WHERE needed - RLS handles it!
    # ...
```

---

### Step 3: Update MongoDB Queries

**BEFORE:**
```python
# manual_trigger_api.py
def store_build_data(build_id, project_id):
    # Hardcoded collection name - WRONG!
    collection = db['ddn_test_failures']

    collection.insert_one({
        'build_id': build_id,
        'project_id': project_id,
        'error': '...'
    })
```

**AFTER:**
```python
from middleware import MongoDBProjectContext
from flask import g

def store_build_data(build_id):
    # Use project context to get correct collection
    prefix = MongoDBProjectContext.get_collection_prefix(g.project_id)
    collection_name = f'{prefix}test_failures'
    collection = db[collection_name]

    collection.insert_one({
        'build_id': build_id,
        'project_id': g.project_id,  # From validated context
        'error': '...'
    })
```

**EVEN BETTER (Database per project):**
```python
from middleware import MongoDBProjectContext
from flask import g

def store_build_data(build_id):
    # Use separate database per project
    db_name = MongoDBProjectContext.get_database_name(g.project_id)
    project_db = mongo_client[db_name]

    # Same collection name across all projects
    collection = project_db['test_failures']

    collection.insert_one({
        'build_id': build_id,
        'error': '...'
    })
```

---

### Step 4: Update Pinecone Queries

**BEFORE:**
```python
# langgraph_agent.py
def search_similar_failures(error_text):
    embedding = get_embedding(error_text)

    # Hardcoded namespace - WRONG!
    results = index.query(
        vector=embedding,
        namespace='ddn_knowledge',
        top_k=10
    )
    return results
```

**AFTER:**
```python
from middleware import PineconeProjectContext
from flask import g

def search_similar_failures(error_text):
    embedding = get_embedding(error_text)

    # Use project-specific namespace
    namespace = PineconeProjectContext.get_namespace(g.project_id)

    results = index.query(
        vector=embedding,
        namespace=namespace,
        top_k=10
    )
    return results
```

---

## Testing the Middleware

### Test 1: Verify Access Control

```python
# test_middleware.py
import pytest
from middleware import require_auth, require_project_access

def test_user_can_access_own_project():
    """User with viewer role can access project"""
    # Login as user with access to project 1
    token = login('john@company.com', 'password')

    response = client.get(
        '/api/projects/1/failures',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200

def test_user_cannot_access_other_project():
    """User cannot access project they don't belong to"""
    # Login as user with access to project 1 only
    token = login('john@company.com', 'password')

    # Try to access project 2
    response = client.get(
        '/api/projects/2/failures',
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 403
    assert 'Access denied' in response.json['error']

def test_viewer_cannot_trigger_analysis():
    """Viewer role cannot trigger analysis (needs developer)"""
    # Login as viewer
    token = login('viewer@company.com', 'password')

    response = client.post(
        '/api/projects/1/trigger-analysis',
        headers={'Authorization': f'Bearer {token}'},
        json={'build_id': 'TEST-123'}
    )

    assert response.status_code == 403
    assert 'Requires developer role' in response.json['error']
```

---

### Test 2: Verify Data Isolation

```python
def test_data_isolation_postgresql():
    """Verify PostgreSQL RLS isolates project data"""
    # Create test data for project 1
    create_failure(project_id=1, build_id='DDN-001')

    # Create test data for project 2
    create_failure(project_id=2, build_id='GURU-001')

    # Login as project 1 user
    token = login_project_user(project_id=1)

    response = client.get(
        '/api/projects/1/failures',
        headers={'Authorization': f'Bearer {token}'}
    )

    failures = response.json['failures']

    # Should only see project 1 data
    assert len(failures) == 1
    assert failures[0]['build_id'] == 'DDN-001'
    assert 'GURU-001' not in str(failures)

def test_data_isolation_mongodb():
    """Verify MongoDB collections are isolated"""
    from middleware import MongoDBProjectContext

    # Get collection for project 1
    g.project_id = 1
    db_name = MongoDBProjectContext.get_database_name(1)
    db1 = mongo_client[db_name]

    # Get collection for project 2
    g.project_id = 2
    db_name = MongoDBProjectContext.get_database_name(2)
    db2 = mongo_client[db_name]

    # Insert data
    db1['test_failures'].insert_one({'build_id': 'DDN-001'})
    db2['test_failures'].insert_one({'build_id': 'GURU-001'})

    # Verify isolation
    ddn_data = list(db1['test_failures'].find())
    guru_data = list(db2['test_failures'].find())

    assert len(ddn_data) == 1
    assert len(guru_data) == 1
    assert ddn_data[0]['build_id'] == 'DDN-001'
    assert guru_data[0]['build_id'] == 'GURU-001'
```

---

## Rollout Plan

### Phase 1: Enable RLS (Week 1)
1. ✅ Apply RLS migration on staging
2. ✅ Test with existing queries
3. ✅ Verify no performance regression
4. ✅ Apply to production

### Phase 2: Add Middleware (Week 2)
1. ✅ Add middleware to 5 critical endpoints
2. ✅ Test access control
3. ✅ Monitor for issues
4. ✅ Roll out to remaining endpoints

### Phase 3: MongoDB Migration (Week 3)
1. ✅ Create project-specific databases
2. ✅ Migrate data
3. ✅ Update queries to use MongoDBProjectContext
4. ✅ Decommission old collections

### Phase 4: Validation (Week 4)
1. ✅ Penetration testing
2. ✅ Load testing
3. ✅ Security audit
4. ✅ Documentation update

---

## Endpoints to Update (Priority Order)

### HIGH PRIORITY (Week 1)
1. ✅ `/api/failures` → Add middleware
2. ✅ `/api/trigger-analysis` → Add middleware
3. ✅ `/api/jira/create-issue` → Add middleware
4. ✅ `/api/projects/<id>/config` → Add middleware
5. ✅ `/api/analytics` → Add middleware

### MEDIUM PRIORITY (Week 2)
6. ✅ `/api/github/*` → Add middleware
7. ✅ `/api/user-feedback` → Add middleware
8. ✅ `/api/manual-trigger` → Add middleware
9. ✅ `/api/knowledge/*` → Add middleware
10. ✅ `/api/self-healing/*` → Add middleware

### LOW PRIORITY (Week 3)
11. ✅ `/api/slack/*` → Add middleware
12. ✅ `/api/notifications/*` → Add middleware
13. ✅ `/api/workflow-executions` → Add middleware

---

## Success Metrics

After integration, verify:

1. **Security**
   - ✅ No cross-project data leakage
   - ✅ All endpoints require authentication
   - ✅ Role-based access enforced
   - ✅ Audit trail of access

2. **Performance**
   - ✅ Response time < 100ms overhead
   - ✅ RLS queries indexed properly
   - ✅ No N+1 queries introduced

3. **Code Quality**
   - ✅ Reduced code by 30% (remove boilerplate)
   - ✅ Consistent validation everywhere
   - ✅ 100% test coverage on middleware

---

## Questions?

**Contact:** Architecture Team
**Documentation:** See `project_context.py` docstrings
**Support:** #engineering-platform Slack channel
