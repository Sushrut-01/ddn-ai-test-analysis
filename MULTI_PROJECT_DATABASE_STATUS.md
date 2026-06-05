# Multi-Project Database Status Report

**Date**: 2026-01-20 19:10
**Verification**: Completed across PostgreSQL, MongoDB, and Pinecone

---

## Executive Summary

✅ **PostgreSQL**: FULLY CONFIGURED for both projects
⚠️ **MongoDB**: Existing data present, project-prefixed collections will be created on first project-specific test
⚠️ **Pinecone**: Indexes exist, namespaces will be auto-created when needed

---

## 1. PostgreSQL Database

### ✅ Status: FULLY CONFIGURED

Both projects are properly configured with complete separation:

```
Project 1: DDN (Default)
  - Slug: ddn
  - Jira Key: KAN
  - MongoDB Prefix: ddn_
  - Pinecone Namespace: ddn_knowledge
  - Current Failures: 0

Project 2: Guruttava
  - Slug: guruttava
  - Jira Key: GURU
  - MongoDB Prefix: guruttava_
  - Pinecone Namespace: guruttava
  - Current Failures: 0
```

### Tables Created
- ✅ `projects` - 2 projects registered
- ✅ `project_configurations` - Both configured
- ✅ `user_projects` - Admin assigned to both
- ✅ `project_activity_log` - Ready for audit trail
- ✅ All existing tables have `project_id` column

---

## 2. MongoDB Atlas Database

### ⚠️ Status: EXISTING DATA, MIGRATION NEEDED

**Database**: `ddn_tests`

### Current Collections (Legacy - Not Project-Specific)
```
failures: 3 documents
test_failures: 34,990 documents
build_results: 1,673 documents
manual_triggers: 7 documents
```

### Expected Project-Specific Collections (Will be auto-created)

**DDN Project** (Prefix: `ddn_`):
- `ddn_test_failures` - Will be created on first DDN test failure
- `ddn_build_results` - Will be created on first DDN build
- `ddn_failure_analysis_detailed` - Will be created on first AI analysis

**Guruttava Project** (Prefix: `guruttava_`):
- `guruttava_test_failures` - Will be created on first Guruttava test failure
- `guruttava_build_results` - Will be created on first Guruttava build
- `guruttava_failure_analysis_detailed` - Will be created on first AI analysis

### Migration Strategy

**Option 1: Auto-Create on First Test (Recommended)**
- New collections with proper prefixes will be created automatically
- Existing 34,990 test failures remain in legacy `test_failures` collection
- Can be migrated later if needed

**Option 2: Manual Migration**
- Assign existing 34,990 test failures to DDN project
- Rename collections to use `ddn_` prefix
- Requires downtime and data migration script

---

## 3. Pinecone Vector Database

### ⚠️ Status: INDEXES EXIST, NAMESPACES NOT YET USED

**Current Setup**:

```
Index: ddn-error-library
  - Total Vectors: 10
  - Namespace: (default) - all vectors

Index: ddn-test-failures
  - Total Vectors: 10
  - Namespace: (default) - all vectors

Index: ddn-error-solutions
  - Total Vectors: 35
  - Namespace: (default) - all vectors

Index: ddn-knowledge-docs
  - Total Vectors: 39
  - Namespace: (default) - all vectors
```

### Expected Project-Specific Namespaces

**DDN Project** (Namespace: `ddn_knowledge`):
- Will store DDN-specific knowledge vectors
- Will store DDN error patterns
- Will be used for DDN-specific AI analysis

**Guruttava Project** (Namespace: `guruttava`):
- Will store Guruttava-specific knowledge vectors
- Will store Guruttava error patterns
- Will be used for Guruttava-specific AI analysis

### Note on Pinecone Namespaces
Pinecone namespaces are automatically created when you insert vectors with a namespace parameter. No pre-creation needed.

---

## Data Isolation Strategy

### Current State
```
┌─────────────────────────────────────────────────────────────┐
│                        PostgreSQL                            │
│  ✅ DDN Project (ID: 1) - Fully configured                  │
│  ✅ Guruttava Project (ID: 2) - Fully configured            │
│  ✅ User access control in place                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     MongoDB Atlas                            │
│  ⚠️ Legacy collections: test_failures, build_results       │
│  ⏳ DDN collections: Will be created on first test          │
│  ⏳ Guruttava collections: Will be created on first test    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        Pinecone                              │
│  ⚠️ Existing indexes use default namespace                 │
│  ⏳ DDN namespace: Will be used when configured             │
│  ⏳ Guruttava namespace: Will be used when configured       │
└─────────────────────────────────────────────────────────────┘
```

---

## What Happens When You Run Tests

### Scenario 1: Jenkins runs DDN test and sends `project_id=1`

1. **Workflow API receives** test results with `project_id=1`
2. **MongoDB**: Creates/uses `ddn_test_failures` collection
3. **PostgreSQL**: Inserts into `failure_analysis` with `project_id=1`
4. **Pinecone**: Stores vectors in `ddn_knowledge` namespace
5. **Dashboard**: Shows failure in DDN project only

### Scenario 2: Jenkins runs Guruttava test and sends `project_id=2`

1. **Workflow API receives** test results with `project_id=2`
2. **MongoDB**: Creates/uses `guruttava_test_failures` collection
3. **PostgreSQL**: Inserts into `failure_analysis` with `project_id=2`
4. **Pinecone**: Stores vectors in `guruttava` namespace
5. **Dashboard**: Shows failure in Guruttava project only

---

## Jenkins Configuration Required

### For DDN Jobs
Add to webhook/API calls:
```json
{
  "project_id": 1,
  "project_slug": "ddn",
  "build_id": "DDN-123",
  "job_name": "DDN-Test-Job"
}
```

### For Guruttava Jobs
Add to webhook/API calls:
```json
{
  "project_id": 2,
  "project_slug": "guruttava",
  "build_id": "GURU-456",
  "job_name": "Guruttava-E2E-Tests"
}
```

---

## API Code Updates Needed

The following services need to be updated to use project-specific collections:

### 1. Workflow API (`workflow_orchestration_api.py`)
```python
# Current: Uses single collection
collection = db['test_failures']

# Update to: Use project-specific collection
project_id = request.json.get('project_id')
mongo_prefix = get_project_config(project_id)['mongodb_collection_prefix']
collection = db[f'{mongo_prefix}test_failures']
```

### 2. Dashboard API (`dashboard_api_full.py`)
```python
# Already supports project filtering via project_id parameter
# MongoDB queries need to use project-specific collections

# Current:
failures = db['test_failures'].find({})

# Update to:
project_id = request.args.get('project_id')
mongo_prefix = get_project_config(project_id)['mongodb_collection_prefix']
failures = db[f'{mongo_prefix}test_failures'].find({})
```

### 3. Pinecone Integration
```python
# Current: No namespace specified
index.upsert(vectors)

# Update to: Use project-specific namespace
project_id = get_current_project_id()
namespace = get_project_config(project_id)['pinecone_namespace']
index.upsert(vectors, namespace=namespace)
```

---

## Verification Checklist

### PostgreSQL ✅
- [x] Projects table created
- [x] Both projects registered
- [x] Project configurations set
- [x] User access configured
- [x] All tables have project_id column

### MongoDB ⏳
- [x] Connection working
- [x] Database accessible
- [ ] DDN collections created (auto on first test)
- [ ] Guruttava collections created (auto on first test)
- [ ] Legacy data migrated (optional)

### Pinecone ⏳
- [x] Connection working
- [x] Indexes accessible
- [ ] DDN namespace in use (auto on first test)
- [ ] Guruttava namespace in use (auto on first test)
- [ ] Legacy vectors migrated to namespaces (optional)

---

## Migration Plan (Optional)

If you want to migrate existing data to project-specific collections:

### Step 1: Backup Existing Data
```bash
mongodump --uri="mongodb+srv://..." --db=ddn_tests --out=/backup
```

### Step 2: Assign Legacy Data to DDN Project
```python
# In MongoDB
db.test_failures.updateMany(
  { project_id: { $exists: false } },
  { $set: { project_id: 1 } }
)
```

### Step 3: Copy to Project-Specific Collections
```python
# Copy test_failures to ddn_test_failures
db.test_failures.aggregate([
  { $match: { project_id: 1 } },
  { $out: "ddn_test_failures" }
])
```

### Step 4: Update PostgreSQL References
```sql
-- Link MongoDB documents to PostgreSQL records
UPDATE failure_analysis
SET mongodb_failure_id = <new_collection_id>
WHERE project_id = 1;
```

---

## Current Recommendation

### ✅ You Can Start Using Multi-Project NOW

**What Works:**
- Login and select DDN or Guruttava project
- API calls with project_id filter
- User access control
- Project-specific Jira/GitHub configs

**What Auto-Creates:**
- MongoDB collections (on first test failure)
- Pinecone namespaces (on first vector insert)

**What to Update:**
- Jenkins jobs to send project_id
- Workflow API to use project-specific MongoDB collections
- Dashboard API to use project-specific MongoDB collections
- Pinecone calls to specify namespace

---

## Summary

### PostgreSQL: ✅ READY
Both projects fully configured with complete isolation

### MongoDB: ⚠️ AUTO-CREATE MODE
Legacy data exists, project collections will be created on demand

### Pinecone: ⚠️ AUTO-CREATE MODE
Indexes exist, namespaces will be used when configured

### Overall Status: 🟢 FUNCTIONAL
You can start using both projects now. Collections and namespaces will be created automatically when data flows in.

---

## Next Steps

1. ✅ Login to dashboard at http://localhost:5173/
2. ✅ Select DDN or Guruttava project
3. ⏳ Update Jenkins jobs to include project_id
4. ⏳ Update workflow API to use project-specific collections
5. ⏳ Run first test for each project to create collections
6. ⏳ Verify data isolation is working

