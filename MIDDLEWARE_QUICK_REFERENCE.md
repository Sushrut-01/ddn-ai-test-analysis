# Middleware Quick Reference Card
## Copy-Paste Examples for Common Scenarios

---

## 🚀 IMPORT STATEMENT

```python
from middleware import (
    require_auth,
    require_project_access,
    require_project_permission,
    MongoDBProjectContext,
    PineconeProjectContext
)
from flask import g
```

---

## 📋 COMMON PATTERNS

### Pattern 1: Read-Only Endpoint (Viewer Access)

```python
@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # g.project_id = validated project ID
    # g.project_role = user's role
    # g.project_info = project details

    conn = get_db_connection()
    cur = conn.cursor()

    # RLS automatically filters by project_id
    cur.execute("SELECT * FROM failure_analysis ORDER BY created_at DESC")

    return jsonify({'failures': cur.fetchall()})
```

---

### Pattern 2: Action Endpoint (Developer Access)

```python
@app.route('/api/projects/<int:project_id>/trigger', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def trigger_analysis(project_id):
    data = request.json

    # Only developers+ can trigger
    build_id = data['build_id']

    # Your logic here...

    return jsonify({'status': 'started'})
```

---

### Pattern 3: Admin Endpoint (Admin Access)

```python
@app.route('/api/projects/<int:project_id>/config', methods=['PUT'])
@require_auth
@require_project_access(required_role='project_admin')
def update_config(project_id):
    # Only admins can update config

    config = request.json

    # Update project settings...

    return jsonify({'updated': True})
```

---

### Pattern 4: MongoDB Query

```python
@app.route('/api/projects/<int:project_id>/test-results')
@require_auth
@require_project_access(required_role='viewer')
def get_test_results(project_id):
    # Get project-specific database
    db_name = MongoDBProjectContext.get_database_name(g.project_id)
    db = mongo_client[db_name]

    # Query isolated to this project
    results = db['test_failures'].find().limit(50)

    return jsonify({'results': list(results)})
```

---

### Pattern 5: Pinecone RAG Query

```python
@app.route('/api/projects/<int:project_id>/search', methods=['POST'])
@require_auth
@require_project_access(required_role='viewer')
def search_similar(project_id):
    error_text = request.json['error']

    # Get embedding
    embedding = get_embedding(error_text)

    # Get project-specific namespace
    namespace = PineconeProjectContext.get_namespace(g.project_id)

    # Query isolated to this project
    results = index.query(
        vector=embedding,
        namespace=namespace,
        top_k=10
    )

    return jsonify({'results': results})
```

---

### Pattern 6: System Admin Bypass

```python
@app.route('/api/projects/<int:project_id>/audit')
@require_auth
@require_project_access(required_role='viewer', allow_system_admin=True)
def get_audit(project_id):
    if g.project_role == 'system_admin':
        # Admin can see everything
        query = "SELECT * FROM audit_log"
    else:
        # Normal users see filtered data
        query = "SELECT * FROM audit_log WHERE sensitive = false"

    # Execute query...
    return jsonify({'logs': []})
```

---

## 🔧 ROLE HIERARCHY

```
guest (0)           ← Read-only, limited
  ↓
viewer (1)          ← Can view all data
  ↓
developer (2)       ← Can trigger analysis
  ↓
project_admin (3)   ← Can manage settings
  ↓
project_owner (4)   ← Full project control
  ↓
system_admin (10)   ← Can access all projects
```

---

## 🎯 WHAT'S AVAILABLE IN Flask g

After using `@require_project_access`:

```python
g.user_id           # User ID from JWT (int)
g.user_email        # User email (str)
g.user_role         # System role: 'user', 'admin' (str)
g.project_id        # Validated project ID (int)
g.project_role      # Role in project: 'viewer', 'developer', etc. (str)
g.project_info      # Full project details (dict)
    ├─ slug         # Project slug: 'ddn', 'guruttava'
    ├─ name         # Project name
    ├─ status       # Project status
    └─ permissions  # User permissions in project (list)
```

---

## 📊 PROJECT CONTEXT HELPERS

### MongoDB

```python
# Get collection prefix (current approach)
prefix = MongoDBProjectContext.get_collection_prefix(g.project_id)
collection = db[f'{prefix}test_failures']

# Get database name (recommended approach)
db_name = MongoDBProjectContext.get_database_name(g.project_id)
db = mongo_client[db_name]
collection = db['test_failures']
```

### Pinecone

```python
# Get namespace for project
namespace = PineconeProjectContext.get_namespace(g.project_id)

results = index.query(
    vector=embedding,
    namespace=namespace,
    top_k=10
)
```

---

## ⚠️ COMMON MISTAKES TO AVOID

### ❌ DON'T: Manual project_id extraction

```python
@app.route('/api/failures')
def get_failures():
    project_id = request.args.get('project_id', 1)  # UNSAFE!
    # No validation...
```

### ✅ DO: Use middleware

```python
@app.route('/api/projects/<int:project_id>/failures')
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # g.project_id validated automatically
```

---

### ❌ DON'T: Hardcode collection names

```python
collection = db['ddn_test_failures']  # WRONG!
```

### ✅ DO: Use context helper

```python
db_name = MongoDBProjectContext.get_database_name(g.project_id)
collection = mongo_client[db_name]['test_failures']
```

---

### ❌ DON'T: Hardcode namespaces

```python
results = index.query(vector=v, namespace='ddn_knowledge')  # WRONG!
```

### ✅ DO: Use context helper

```python
namespace = PineconeProjectContext.get_namespace(g.project_id)
results = index.query(vector=v, namespace=namespace)
```

---

## 🧪 TESTING CHECKLIST

```python
# Test 1: User can access own project
✅ Login as project 1 user
✅ Request /api/projects/1/failures
✅ Should return 200

# Test 2: User cannot access other project
✅ Login as project 1 user
✅ Request /api/projects/2/failures
✅ Should return 403

# Test 3: Role enforcement
✅ Login as viewer
✅ Request /api/projects/1/trigger (needs developer)
✅ Should return 403

# Test 4: Data isolation
✅ Create data for project 1 and 2
✅ Query as project 1 user
✅ Should only see project 1 data

# Test 5: RLS enforcement
✅ Set project context
✅ Execute query without WHERE clause
✅ Should still only return project data
```

---

## 🔥 EMERGENCY ROLLBACK

If something breaks:

```bash
# Disable RLS on all tables
psql -U postgres -d ddn_ai_analysis <<EOF
ALTER TABLE failure_analysis DISABLE ROW LEVEL SECURITY;
ALTER TABLE build_metadata DISABLE ROW LEVEL SECURITY;
ALTER TABLE test_case_history DISABLE ROW LEVEL SECURITY;
-- etc...
EOF

# Remove middleware decorators
# Replace with old validation code
```

---

## 📞 SUPPORT

- **Documentation:** `implementation/middleware/project_context.py`
- **Integration Guide:** `MIDDLEWARE_INTEGRATION_GUIDE.md`
- **Architecture Review:** `ARCHITECTURAL_ANALYSIS_REPORT.md`
- **Flow Analysis:** `FUNCTIONAL_FLOW_ANALYSIS.md`

---

## ✅ APPROVAL CHECKLIST

Before deploying to production:

- [ ] RLS migration tested on staging
- [ ] Middleware tested with all roles
- [ ] Data isolation verified
- [ ] Performance benchmarked (<100ms overhead)
- [ ] Security audit completed
- [ ] Rollback plan documented
- [ ] Team trained on new patterns
- [ ] Documentation updated

---

**Version:** 1.0
**Last Updated:** 2026-02-02
**Status:** Ready for Review
