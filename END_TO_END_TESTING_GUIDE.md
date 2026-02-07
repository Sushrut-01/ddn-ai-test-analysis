# End-to-End Testing Guide: Multi-Project Architecture

**Date:** 2026-01-14
**Purpose:** Complete testing guide for DDN + Guruttava multi-tenant AI test analysis platform
**Audience:** DevOps Engineers, QA Engineers, Developers

---

## 🎯 Testing Objectives

This guide ensures that the multi-project architecture:
1. ✅ Maintains complete data isolation between DDN and Guruttava projects
2. ✅ Routes test failures to correct project-specific services
3. ✅ Creates Jira tickets in correct project (DDN vs GURU)
4. ✅ Stores data in correct MongoDB collections and Pinecone namespaces
5. ✅ Supports Robot Framework for Guruttava mobile/web tests
6. ✅ Provides project-scoped dashboard views

---

## 📋 Pre-Requisites Checklist

### Database Setup
- [ ] PostgreSQL database running (port 5434)
- [ ] MongoDB Atlas connection configured
- [ ] SQL migration `002_add_guruttava_project.sql` executed
- [ ] MongoDB collections created via `002_setup_guruttava_mongodb.py`

### Service Configuration
- [ ] `.env` file updated with Guruttava credentials
- [ ] Docker containers running (`docker compose up -d`)
- [ ] Jenkins accessible at `localhost:8081`
- [ ] Appium server accessible at `localhost:4723`

### Network Connectivity
- [ ] All services in `ddn-network` bridge
- [ ] DNS resolution working (8.8.8.8, 1.1.1.1)
- [ ] Ports not conflicting with existing services

---

## 🧪 Test Suite

### Test 1: Database Data Isolation

**Objective:** Verify DDN and Guruttava data never mix

**Steps:**

```sql
-- Connect to PostgreSQL
psql -U postgres -d ddn_ai_analysis -h localhost -p 5434

-- 1. Verify projects exist
SELECT id, slug, name, status FROM projects;
-- Expected: 2 rows (ddn, guruttava)

-- 2. Verify project configurations
SELECT
    p.slug,
    pc.jira_project_key,
    pc.mongodb_collection_prefix,
    pc.pinecone_namespace
FROM projects p
JOIN project_configurations pc ON p.id = pc.project_id;
-- Expected:
--   ddn | DDN | ddn_ | ddn
--   guruttava | GURU | guruttava_ | guruttava

-- 3. Check failure_analysis isolation
SELECT
    project_id,
    COUNT(*) as failure_count
FROM failure_analysis
GROUP BY project_id;
-- Expected: Separate counts for project_id 1 (DDN) and 2 (Guruttava)

-- 4. Verify no cross-project contamination
SELECT COUNT(*) FROM failure_analysis
WHERE project_id = 1 AND build_id LIKE '%Guruttava%';
-- Expected: 0 (DDN should not have Guruttava builds)

SELECT COUNT(*) FROM failure_analysis
WHERE project_id = 2 AND build_id LIKE '%DDN%';
-- Expected: 0 (Guruttava should not have DDN builds)
```

**✅ Pass Criteria:** All queries return expected results with no data leakage

---

### Test 2: MongoDB Collection Isolation

**Objective:** Verify MongoDB collections are properly segregated

**Steps:**

```javascript
// Connect to MongoDB Atlas
use ddn_tests;

// 1. List all collections
db.getCollectionNames().filter(name =>
    name.startsWith('ddn_') || name.startsWith('guruttava_')
);
// Expected:
// - ddn_test_failures
// - ddn_build_results
// - guruttava_test_failures
// - guruttava_build_results

// 2. Verify Guruttava collection structure
db.guruttava_test_failures.findOne();
// Expected: Document with project_id: 2

// 3. Count documents per project
db.ddn_test_failures.count();
db.guruttava_test_failures.count();
// Expected: Separate counts, no overlap

// 4. Verify indexes exist
db.guruttava_test_failures.getIndexes();
// Expected: Indexes on build_id, test_name, timestamp, error_category, project_id

// 5. Check for data leakage
db.guruttava_test_failures.find({project_id: 1}).count();
// Expected: 0 (Guruttava collection should only have project_id: 2)

db.ddn_test_failures.find({project_id: 2}).count();
// Expected: 0 (DDN collection should only have project_id: 1)
```

**✅ Pass Criteria:** Collections properly isolated, indexes exist, no cross-contamination

---

### Test 3: Python Workflow API Multi-Project Routing

**Objective:** Test `/api/trigger-analysis` endpoint with project context

**Steps:**

```bash
# 1. Test with DDN project
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Test-1234",
    "project_id": 1,
    "project_slug": "ddn",
    "triggered_by_user": "test@example.com"
  }'

# Expected Response:
# {
#   "success": true,
#   "project": {"id": 1, "slug": "ddn", "name": "DDN Project"},
#   "build_id": "DDN-Test-1234",
#   ...
# }

# 2. Test with Guruttava project
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "Guruttava-Android-Tests-42",
    "project_id": 2,
    "project_slug": "guruttava",
    "platform": "Android",
    "test_type": "Smoke",
    "triggered_by_user": "test@example.com"
  }'

# Expected Response:
# {
#   "success": true,
#   "project": {"id": 2, "slug": "guruttava", "name": "Guruttava"},
#   "build_id": "Guruttava-Android-Tests-42",
#   ...
# }

# 3. Test inference from build_id (backward compatibility)
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "Guruttava-iOS-Tests-99",
    "triggered_by_user": "test@example.com"
  }'

# Expected: Should infer project_id=2 from "Guruttava" in build_id
```

**✅ Pass Criteria:** API correctly routes requests based on project_id, stores in correct collections

---

### Test 4: Dashboard API Project Context Validation

**Objective:** Test `/api/analysis/store` with multi-project support

**Steps:**

```bash
# 1. Store DDN analysis
curl -X POST http://localhost:5006/api/analysis/store \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Nightly-789",
    "project_id": 1,
    "error_category": "CODE_ERROR",
    "root_cause": "Null pointer exception",
    "fix_recommendation": "Add null check",
    "confidence_score": 0.85,
    "analysis_type": "GEMINI_DEEP_ANALYSIS"
  }'

# Expected: analysis_id returned, stored with project_id=1

# 2. Store Guruttava analysis
curl -X POST http://localhost:5006/api/analysis/store \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "Guruttava-Web-Tests-55",
    "project_id": 2,
    "test_name": "Login Test",
    "platform": "Web",
    "test_type": "Regression",
    "error_category": "ELEMENT_NOT_FOUND",
    "root_cause": "Button locator changed",
    "fix_recommendation": "Update XPath selector",
    "confidence_score": 0.92,
    "analysis_type": "RAG_BASED"
  }'

# Expected: analysis_id returned, stored with project_id=2

# 3. Verify storage in PostgreSQL
psql -U postgres -d ddn_ai_analysis -c \
  "SELECT build_id, project_id, platform, test_type FROM failure_analysis ORDER BY id DESC LIMIT 5;"

# Expected: See both DDN (project_id=1) and Guruttava (project_id=2) entries
```

**✅ Pass Criteria:** Data stored with correct project_id, new fields (platform, test_type) populated

---

### Test 5: Jira Integration Multi-Project Support

**Objective:** Verify Jira tickets created in correct project (DDN vs GURU)

**Steps:**

```bash
# 1. Create Jira ticket for DDN
curl -X POST http://localhost:5009/api/jira/create-issue \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Critical-999",
    "project_id": 1,
    "error_category": "CODE_ERROR",
    "error_message": "Critical bug in payment module",
    "root_cause": "Race condition in transaction processing",
    "fix_recommendation": "Add mutex lock",
    "confidence_score": 0.95,
    "consecutive_failures": 5
  }'

# Expected Response:
# {
#   "status": "success",
#   "action": "created",
#   "jira_issue_key": "DDN-123",  <-- DDN project key
#   "jira_url": "https://your-org.atlassian.net/browse/DDN-123",
#   "project_id": 1,
#   "project_slug": "ddn"
# }

# 2. Create Jira ticket for Guruttava
curl -X POST http://localhost:5009/api/jira/create-issue \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "Guruttava-Mobile-888",
    "project_id": 2,
    "error_category": "MOBILE_ERROR",
    "error_message": "App crash on startup",
    "root_cause": "Missing permission in AndroidManifest.xml",
    "fix_recommendation": "Add CAMERA permission",
    "confidence_score": 0.88,
    "consecutive_failures": 3
  }'

# Expected Response:
# {
#   "status": "success",
#   "action": "created",
#   "jira_issue_key": "GURU-456",  <-- GURU project key
#   "jira_url": "https://your-org.atlassian.net/browse/GURU-456",
#   "project_id": 2,
#   "project_slug": "guruttava"
# }

# 3. Verify in Jira UI
# - Navigate to DDN project: Should see DDN-123
# - Navigate to GURU project: Should see GURU-456
```

**✅ Pass Criteria:** Tickets created in correct Jira project, issue keys use correct prefix

---

### Test 6: Robot Framework Parser Integration

**Objective:** Test Robot Framework output parsing for Guruttava

**Preparation:**

```bash
# Create sample Robot Framework output.xml
cat > /tmp/sample_output.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<robot generator="Robot 6.1" generated="20240114 12:30:00">
  <suite name="Guruttava Android Tests" source="/tests/android">
    <test name="Login Test">
      <kw name="Click Element" library="AppiumLibrary">
        <arg>id=loginButton</arg>
        <status status="FAIL">Element not found: id=loginButton</status>
      </kw>
      <status status="FAIL" starttime="20240114 12:30:45.123" endtime="20240114 12:31:02.456"/>
    </test>
  </suite>
  <statistics>
    <total>
      <stat pass="0" fail="1">All Tests</stat>
    </total>
  </statistics>
</robot>
EOF
```

**Steps:**

```bash
# 1. Parse Robot Framework output
python implementation/robot_framework_parser.py \
    --output /tmp/sample_output.xml \
    --build-id Guruttava-Android-Test-Parser-1 \
    --project-id 2 \
    --project-slug guruttava \
    --platform Android \
    --test-type Smoke \
    --mongodb-uri "$MONGODB_URI" \
    --api-url http://localhost:5004/api/trigger-analysis

# Expected Output:
# ✅ Extracted 1 test failures
# ✅ Stored failures in MongoDB
# ✅ Analysis triggered successfully

# 2. Verify in MongoDB
mongo "$MONGODB_URI" --eval "
  db = db.getSiblingDB('ddn_tests');
  db.guruttava_test_failures.find({
    build_id: 'Guruttava-Android-Test-Parser-1'
  }).pretty();
"

# Expected: Document with:
# - project_id: 2
# - test_name: "Login Test"
# - platform: "Android"
# - error_category: "ELEMENT_NOT_FOUND"

# 3. Verify in PostgreSQL
psql -U postgres -d ddn_ai_analysis -c \
  "SELECT * FROM failure_analysis WHERE build_id = 'Guruttava-Android-Test-Parser-1';"

# Expected: Analysis entry with project_id=2
```

**✅ Pass Criteria:** Parser extracts failures, stores in correct collections, triggers analysis

---

### Test 7: Jenkins + Robot Framework End-to-End

**Objective:** Complete Jenkins → Robot Framework → Python Workflow flow

**Prerequisites:**
- Jenkins running at `localhost:8081`
- Guruttava-Jenkinsfile deployed to repo
- Appium server running at `localhost:4723`

**Steps:**

```bash
# 1. Check Jenkins job exists
curl -u admin:$JENKINS_TOKEN \
  http://localhost:8081/job/Guruttava-Android-Tests/config.xml

# Expected: XML configuration with PROJECT_ID=2, PROJECT_SLUG=guruttava

# 2. Trigger Jenkins job manually
curl -X POST -u admin:$JENKINS_TOKEN \
  "http://localhost:8081/job/Guruttava-Android-Tests/buildWithParameters?PLATFORM=Android&TEST_TYPE=Smoke"

# 3. Monitor build progress
curl -u admin:$JENKINS_TOKEN \
  http://localhost:8081/job/Guruttava-Android-Tests/lastBuild/api/json

# 4. Check build console output
curl -u admin:$JENKINS_TOKEN \
  http://localhost:8081/job/Guruttava-Android-Tests/lastBuild/consoleText

# Expected in console:
# - "Running Android tests"
# - "Parsing Robot Framework test results"
# - "Uploading test results to DDN AI Platform"
# - "Analysis triggered successfully"

# 5. Verify Robot Framework report published
curl http://localhost:8081/job/Guruttava-Android-Tests/lastBuild/robot/report/report.html

# 6. Verify data in PostgreSQL
psql -U postgres -d ddn_ai_analysis -c \
  "SELECT build_id, project_id, platform, classification FROM failure_analysis
   WHERE job_name = 'Guruttava-Android-Tests' ORDER BY created_at DESC LIMIT 1;"

# Expected: Latest build with project_id=2, platform=Android
```

**✅ Pass Criteria:** Jenkins executes tests, parses results, stores data with correct project context

---

### Test 8: Dashboard Project Switching

**Objective:** Verify dashboard shows only project-specific data

**Steps:**

1. **Login to Dashboard:**
   - Navigate to `http://localhost:5173`
   - Login with: `demo@ddn.com` / `demo1234`
   - Expected: Project selection modal appears

2. **Select DDN Project:**
   - Click on "DDN Project" card
   - Click "Continue to Dashboard"
   - Expected:
     - Dashboard loads with DDN data
     - Failures table shows only DDN builds
     - Analytics charts reflect DDN metrics only

3. **Switch to Guruttava Project:**
   - Click project selector dropdown (top-right)
   - Select "Guruttava"
   - Expected:
     - Dashboard refreshes
     - Failures table shows only Guruttava builds
     - No DDN data visible
     - Platform filter shows: Android, iOS, Web

4. **Verify API Calls:**
   - Open browser DevTools → Network tab
   - Check API requests have `X-Project-ID: 2` header
   - Responses should only contain Guruttava data

5. **Test User Access Control:**
   ```sql
   -- Remove user access to Guruttava
   DELETE FROM user_projects WHERE user_id = 8 AND project_id = 2;
   ```
   - Refresh project selector
   - Expected: Guruttava no longer appears in list

**✅ Pass Criteria:** Dashboard enforces project-level data isolation, user access control works

---

### Test 9: Pinecone Namespace Isolation

**Objective:** Verify RAG searches stay within project namespace

**Steps:**

```python
# Test script: test_pinecone_isolation.py
import os
from pinecone import Pinecone

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))

# 1. Query DDN namespace
ddn_results = index.query(
    vector=[0.1] * 1536,  # Dummy vector
    namespace='ddn',
    top_k=5,
    include_metadata=True
)
print(f"DDN Results: {len(ddn_results['matches'])} matches")
# All results should have metadata indicating DDN project

# 2. Query Guruttava namespace
guruttava_results = index.query(
    vector=[0.1] * 1536,
    namespace='guruttava',
    top_k=5,
    include_metadata=True
)
print(f"Guruttava Results: {len(guruttava_results['matches'])} matches")
# All results should have metadata indicating Guruttava project

# 3. Verify no cross-namespace leakage
assert all('ddn' in m['metadata'].get('project', '') for m in ddn_results['matches'])
assert all('guruttava' in m['metadata'].get('project', '') for m in guruttava_results['matches'])
```

**✅ Pass Criteria:** Queries return only results from specified namespace, no cross-contamination

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "Project not found" error

**Symptom:** API returns 404 "Project {id} not found"

**Solution:**
```sql
-- Check if project exists
SELECT * FROM projects WHERE id = 2;

-- If missing, run migration:
\i implementation/migrations/002_add_guruttava_project.sql
```

---

### Issue 2: Jira tickets not created

**Symptom:** Jira integration returns "Jira not configured for project_id=2"

**Solution:**
```sql
-- Check Jira configuration
SELECT jira_project_key, jira_url FROM project_configurations WHERE project_id = 2;

-- If empty, update configuration:
UPDATE project_configurations
SET jira_project_key = 'GURU',
    jira_url = 'https://your-org.atlassian.net'
WHERE project_id = 2;
```

---

### Issue 3: MongoDB collections not found

**Symptom:** "Collection guruttava_test_failures not found"

**Solution:**
```bash
# Run MongoDB setup script
python implementation/migrations/002_setup_guruttava_mongodb.py

# Verify collections created
mongo "$MONGODB_URI" --eval "
  db.getSiblingDB('ddn_tests').getCollectionNames().filter(n => n.startsWith('guruttava_'))
"
```

---

### Issue 4: Appium server not accessible

**Symptom:** Jenkins job fails with "Appium server not accessible at http://localhost:4723"

**Solution:**
```bash
# Check Appium container status
docker ps | grep appium

# Restart if needed
docker compose restart appium

# Verify health
curl http://localhost:4723/wd/hub/status
```

---

### Issue 5: Robot Framework parser fails

**Symptom:** "Could not parse output.xml"

**Solution:**
```bash
# Validate XML structure
xmllint --noout /path/to/output.xml

# Check file permissions
ls -l /path/to/output.xml

# Run parser with debug logging
python robot_framework_parser.py ... --verbose
```

---

## ✅ Test Results Checklist

Use this checklist to track test completion:

- [ ] **Test 1:** Database Data Isolation ✅
- [ ] **Test 2:** MongoDB Collection Isolation ✅
- [ ] **Test 3:** Python Workflow API Multi-Project Routing ✅
- [ ] **Test 4:** Dashboard API Project Context Validation ✅
- [ ] **Test 5:** Jira Integration Multi-Project Support ✅
- [ ] **Test 6:** Robot Framework Parser Integration ✅
- [ ] **Test 7:** Jenkins + Robot Framework End-to-End ✅
- [ ] **Test 8:** Dashboard Project Switching ✅
- [ ] **Test 9:** Pinecone Namespace Isolation ✅

---

## 📊 Performance Benchmarks

Expected performance metrics:

| Metric | Target | Acceptable | Critical |
|--------|--------|------------|----------|
| API Response Time (/api/trigger-analysis) | < 500ms | < 1s | < 2s |
| MongoDB Query Time | < 100ms | < 300ms | < 500ms |
| Jira Ticket Creation | < 2s | < 5s | < 10s |
| Robot Framework Parsing | < 1s per 100 tests | < 3s | < 5s |
| Dashboard Project Switch | < 300ms | < 1s | < 2s |

---

## 🎓 Testing Best Practices

1. **Isolate Test Data:** Always use separate test build IDs (e.g., `TEST-XXX-999`)
2. **Clean Up:** Remove test data after verification
3. **Document Issues:** Log all failures in GitHub Issues with reproduction steps
4. **Automate Where Possible:** Convert manual tests to automated scripts
5. **Regular Validation:** Run isolation tests after any schema changes

---

## 📚 Additional Resources

- **Architecture Document:** `MULTI_PROJECT_ARCHITECTURE_DESIGN.md`
- **Implementation Status:** `MULTI_PROJECT_IMPLEMENTATION_STATUS.md`
- **SQL Migration:** `implementation/migrations/002_add_guruttava_project.sql`
- **MongoDB Setup:** `implementation/migrations/002_setup_guruttava_mongodb.py`
- **Jenkins Pipeline:** `jenkins-jobs/Guruttava-Jenkinsfile`
- **Robot Parser:** `implementation/robot_framework_parser.py`

---

**Testing Completed By:** _________________
**Date:** _________________
**Sign-Off:** _________________

---

**END OF TESTING GUIDE**
