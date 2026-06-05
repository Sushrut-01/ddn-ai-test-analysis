# Claude Skills for DDN AI Test Analysis Platform

## Core Skills and Capabilities

This document defines the specialized skills Claude should use when working on the DDN AI Test Analysis Platform. Each skill represents a specific capability or workflow that Claude can execute autonomously.

---

## 1. Multi-Project Architecture Skills

### Skill: `analyze-project-isolation`
**Purpose**: Verify data isolation between DDN and Guruttava projects
**When to Use**: After any database changes, API modifications, or when investigating data leakage

**Execution Steps**:
1. Query PostgreSQL for project_id=1 (DDN) and project_id=2 (Guruttava)
2. Verify no cross-project contamination in failure_analysis table
3. Check MongoDB collections for correct project_id values
4. Validate Pinecone namespaces are queried correctly
5. Report any isolation issues found

**Success Criteria**:
- No DDN data has project_id=2
- No Guruttava data has project_id=1
- MongoDB collections only contain their project's data
- Pinecone queries return project-specific results

---

### Skill: `add-new-project`
**Purpose**: Add a new project to the multi-tenant system
**When to Use**: When user requests to onboard a new testing project

**Execution Steps**:
1. Gather project requirements (name, slug, GitHub repo, Jira config)
2. Create PostgreSQL records in `projects` and `project_configurations` tables
3. Set up MongoDB collections with proper indexes
4. Create Pinecone namespace
5. Generate Jenkins pipeline configuration
6. Update `.env` file with project-specific variables
7. Assign initial users to project
8. Create documentation for the new project

**Required Inputs**:
- Project name (e.g., "QA Automation")
- Project slug (e.g., "qa-automation")
- GitHub repository URL
- Jira project key
- Initial user assignments

---

## 2. Debugging and Troubleshooting Skills

### Skill: `diagnose-data-issue`
**Purpose**: Investigate why data is not displaying correctly in dashboard
**When to Use**: When user reports missing or incorrect data in UI

**Execution Steps**:
1. Check frontend localStorage for selected project_id
2. Inspect API calls in browser DevTools (verify project_id in requests)
3. Query PostgreSQL directly for the project_id
4. Check MongoDB collections for test failures
5. Verify Jenkins job is passing correct PROJECT_ID
6. Review API logs for errors
7. Test API endpoints directly with curl
8. Provide diagnostic report with findings

**Common Issues to Check**:
- project_id missing from API requests
- Wrong MongoDB collection being queried
- Jenkins not setting PROJECT_ID environment variable
- User not assigned to project in user_projects table
- Database connection issues

---

### Skill: `fix-jenkins-pipeline`
**Purpose**: Fix Jenkins pipeline issues for DDN or Guruttava
**When to Use**: When Jenkins builds fail or don't trigger AI analysis correctly

**Execution Steps**:
1. Read Jenkins console output for the failed build
2. Identify error type (test failure, connection issue, parser failure, etc.)
3. Check Jenkins environment variables (PROJECT_ID, PROJECT_SLUG)
4. Verify GitHub repository checkout succeeded
5. Check Appium/Selenium server connectivity (if applicable)
6. Verify robot_framework_parser.py is being called correctly
7. Test API endpoint availability
8. Apply fix to Jenkinsfile
9. Recommend manual test of updated pipeline

---

### Skill: `trace-failure-flow`
**Purpose**: Trace the complete flow of a test failure through the system
**When to Use**: To understand how a specific failure is processed or debug issues

**Execution Steps**:
1. Start with Jenkins build ID
2. Trace: Jenkins → Robot Framework → Parser → MongoDB
3. Trace: MongoDB → Python Workflow API → LangGraph → Dashboard API
4. Trace: Dashboard API → PostgreSQL → Frontend Display
5. Check each step for project_id preservation
6. Identify where data is lost or corrupted
7. Provide complete flow diagram with results

**Example Flow**:
```
Jenkins Build (DDN-Test-123, PROJECT_ID=1)
  ↓
Robot Framework Tests Execute
  ↓
output.xml Generated
  ↓
robot_framework_parser.py (--project-id 1)
  ↓
MongoDB: ddn_test_failures (project_id: 1)
  ↓
POST /api/trigger-analysis (project_id: 1)
  ↓
LangGraph Classifier
  ↓
POST /api/analysis/store (project_id: 1)
  ↓
PostgreSQL: failure_analysis (project_id: 1)
  ↓
Dashboard: GET /api/failures?project_id=1
  ↓
Frontend Display
```

---

## 3. Development and Code Modification Skills

### Skill: `add-api-endpoint`
**Purpose**: Add a new API endpoint with multi-project support
**When to Use**: When adding new features to the API

**Execution Steps**:
1. Identify which service the endpoint belongs to (Dashboard, Manual Trigger, Jira)
2. Define endpoint signature with project_id parameter
3. Implement database query with project_id filter
4. Add access control check (verify user has access to project)
5. Update API documentation
6. Write test cases for the endpoint
7. Test with both DDN and Guruttava projects

**Code Template**:
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    data = request.get_json()
    project_id = data.get('project_id')

    # Validate project_id
    if not project_id:
        return jsonify({'error': 'project_id required'}), 400

    # TODO: Verify user access to project

    # Query with project_id filter
    query = "SELECT * FROM table WHERE project_id = %s"

    # Return results
    return jsonify({'project_id': project_id, 'data': results})
```

---

### Skill: `update-frontend-component`
**Purpose**: Modify React components with project awareness
**When to Use**: When adding/modifying dashboard UI features

**Execution Steps**:
1. Identify affected components
2. Check if component needs project_id from context or localStorage
3. Update API calls to include project_id
4. Add data filtering by project
5. Handle project switching (reload data when project changes)
6. Update PropTypes/TypeScript types
7. Test in both DDN and Guruttava contexts

**Key Patterns**:
```javascript
// Get project_id from localStorage
const projectId = localStorage.getItem('selected_project_id');

// Include in API calls
const response = await fetch(`/api/endpoint`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ project_id: projectId, ...data })
});

// Listen for project changes
useEffect(() => {
  loadData();
}, [projectId]);
```

---

### Skill: `create-database-migration`
**Purpose**: Create SQL migration scripts for schema changes
**When to Use**: When adding new tables or columns

**Execution Steps**:
1. Analyze current schema
2. Design new schema changes
3. Write SQL migration with project_id columns (if applicable)
4. Include indexes for project_id
5. Write rollback script
6. Test migration on local database
7. Document migration in IMPLEMENTATION_STATUS.md

**Migration Template**:
```sql
-- Migration: Add new feature table
-- Date: YYYY-MM-DD

-- Create table with project_id
CREATE TABLE new_feature (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    feature_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index on project_id
CREATE INDEX idx_new_feature_project_id ON new_feature(project_id);

-- Rollback script
-- DROP TABLE IF EXISTS new_feature;
```

---

## 4. Testing and Validation Skills

### Skill: `run-integration-tests`
**Purpose**: Execute end-to-end integration tests for multi-project system
**When to Use**: After major changes or before deployment

**Execution Steps**:
1. Follow END_TO_END_TESTING_GUIDE.md
2. Execute Test 1: Database Data Isolation
3. Execute Test 2: MongoDB Collection Isolation
4. Execute Test 3: Python Workflow API Multi-Project Routing
5. Execute Test 4: Dashboard API Project Context Validation
6. Execute Test 5: Jira Integration Multi-Project Support
7. Execute Test 6-9 as applicable
8. Document all test results
9. Report any failures with detailed logs

---

### Skill: `validate-jenkins-config`
**Purpose**: Verify Jenkins pipeline configuration is correct
**When to Use**: After creating/modifying Jenkins pipelines

**Execution Steps**:
1. Read Jenkinsfile content
2. Verify PROJECT_ID and PROJECT_SLUG are set correctly
3. Check GitHub repository URL matches project
4. Validate robot_framework_parser.py call includes project parameters
5. Verify API trigger URL is correct
6. Check robot publisher configuration
7. Test pipeline with dry-run (if possible)
8. Provide configuration checklist

**Checklist**:
- [ ] PROJECT_ID matches database record
- [ ] PROJECT_SLUG matches database record
- [ ] GitHub URL is correct for this project
- [ ] Parser includes --project-id and --project-slug
- [ ] TRIGGER_API_URL points to correct service
- [ ] MONGODB_URI is configured
- [ ] Robot publisher outputs to correct directory

---

## 5. Documentation Skills

### Skill: `update-architecture-docs`
**Purpose**: Update architecture documentation after changes
**When to Use**: After implementing new features or making significant changes

**Execution Steps**:
1. Identify affected documentation files
2. Update MULTI_PROJECT_ARCHITECTURE_DESIGN.md if architecture changed
3. Update IMPLEMENTATION_COMPLETE_SUMMARY.md with new deliverables
4. Update END_TO_END_TESTING_GUIDE.md if new tests needed
5. Update this SKILL.md if new skills were created
6. Update PROMPT.md if context changed
7. Create/update inline code comments
8. Generate changelog entry

---

### Skill: `create-troubleshooting-guide`
**Purpose**: Document common issues and solutions
**When to Use**: After resolving complex issues that may recur

**Execution Steps**:
1. Document the issue encountered
2. List symptoms observed
3. Detail diagnostic steps taken
4. Explain root cause
5. Provide step-by-step solution
6. Include prevention recommendations
7. Add to appropriate documentation file

---

## 6. Operational Skills

### Skill: `start-all-services`
**Purpose**: Start the complete DDN AI platform stack
**When to Use**: When user wants to run the system

**Execution Steps**:
1. Check Docker is running
2. Start databases: `docker-compose up -d postgres mongodb`
3. Start backend services: `docker-compose up -d dashboard-api manual-trigger-api jira-service`
4. Start LangGraph AI service: `docker-compose up -d langgraph-service`
5. Start frontend: `cd implementation/dashboard-ui && npm run dev`
6. Start Appium (for Guruttava): `docker-compose up -d appium`
7. Verify all services healthy
8. Display service URLs for user

**Service URLs**:
- Frontend: http://localhost:5173
- Dashboard API: http://localhost:5006
- Manual Trigger API: http://localhost:5004
- Jira Service: http://localhost:5009
- Jenkins: http://localhost:8081

---

### Skill: `check-system-health`
**Purpose**: Verify all system components are operational
**When to Use**: Regularly or when user reports issues

**Execution Steps**:
1. Check PostgreSQL connectivity and recent activity
2. Check MongoDB connectivity and collection sizes
3. Check Pinecone index status
4. Test all API endpoints (/health endpoints)
5. Check Jenkins is running and jobs are configured
6. Verify frontend is accessible
7. Check Docker container status
8. Generate health report

**Health Check Commands**:
```bash
# PostgreSQL
psql -U postgres -d ddn_ai_analysis -c "SELECT COUNT(*) FROM projects;"

# MongoDB
mongo $MONGODB_URI --eval "db.ddn_test_failures.count()"

# APIs
curl http://localhost:5004/health
curl http://localhost:5006/health
curl http://localhost:5009/health

# Frontend
curl http://localhost:5173

# Jenkins
curl http://localhost:8081

# Docker
docker compose ps
```

---

### Skill: `backup-and-restore`
**Purpose**: Backup or restore project data
**When to Use**: Before major changes or after data loss

**Execution Steps**:
1. Backup PostgreSQL: `pg_dump ddn_ai_analysis > backup.sql`
2. Backup MongoDB: `mongodump --uri="$MONGODB_URI"`
3. Backup .env files
4. Backup Jenkins configs
5. Create backup manifest with timestamp
6. Store securely with documentation

**Restore Steps**:
1. Stop all services
2. Restore PostgreSQL: `psql ddn_ai_analysis < backup.sql`
3. Restore MongoDB: `mongorestore --uri="$MONGODB_URI" dump/`
4. Restore .env and configs
5. Restart services
6. Verify data integrity

---

## 7. Advanced Skills

### Skill: `optimize-query-performance`
**Purpose**: Improve database query performance
**When to Use**: When dashboard is slow or queries timeout

**Execution Steps**:
1. Identify slow queries using PostgreSQL EXPLAIN ANALYZE
2. Check if project_id indexes exist and are being used
3. Analyze MongoDB query performance
4. Add missing indexes
5. Optimize JOIN operations
6. Consider query result caching
7. Test performance improvements
8. Document optimizations

---

### Skill: `implement-new-error-category`
**Purpose**: Add a new error classification category
**When to Use**: When identifying new types of test failures

**Execution Steps**:
1. Define new category name (e.g., MEMORY_LEAK)
2. Update LangGraph classifier with new category
3. Update database enum/constraints
4. Update frontend UI to display new category
5. Add documentation for category
6. Test classification with sample failures
7. Train team on new category

---

## How to Use These Skills

### For Claude (AI Assistant)
When working on the DDN AI Test Analysis Platform:
1. Read PROMPT.md first for project context
2. Identify which skill(s) apply to the current task
3. Follow the skill's execution steps systematically
4. Always maintain data isolation between projects
5. Test changes in both DDN and Guruttava contexts
6. Update documentation after completing tasks

### For Developers
These skills serve as:
- **Standard Operating Procedures** for common tasks
- **Debugging playbooks** for troubleshooting
- **Training materials** for new team members
- **Quality checklists** to ensure nothing is missed

---

## Skill Priority Matrix

| Task Type | Primary Skill | Secondary Skills |
|-----------|--------------|------------------|
| Data not showing | `diagnose-data-issue` | `trace-failure-flow`, `analyze-project-isolation` |
| Jenkins failing | `fix-jenkins-pipeline` | `validate-jenkins-config`, `check-system-health` |
| Adding feature | `add-api-endpoint`, `update-frontend-component` | `create-database-migration`, `update-architecture-docs` |
| New project | `add-new-project` | `create-database-migration`, `validate-jenkins-config` |
| Performance issues | `optimize-query-performance` | `check-system-health` |
| After deployment | `run-integration-tests` | `check-system-health`, `backup-and-restore` |

---

## Continuous Improvement

These skills should evolve as the platform grows:
1. Add new skills when common patterns emerge
2. Update existing skills when processes improve
3. Remove obsolete skills when no longer needed
4. Share skill improvements with team

---

**Remember**: Skills are templates, not rigid rules. Adapt them based on the specific situation while always maintaining data isolation and system integrity.
