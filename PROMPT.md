# DDN AI Test Analysis Platform - Project Context

## Overview
This is a **Multi-Tenant AI-Powered Test Analysis Platform** supporting multiple independent projects with complete data isolation. The platform analyzes test failures using AI, creates Jira tickets, generates PR workflows, and provides intelligent root cause analysis.

## Project Architecture

### Current Projects
1. **DDN Project** (project_id: 1, slug: "ddn")
   - **Type**: Web Application Testing
   - **Technologies**: Selenium, API Testing, Robot Framework
   - **GitHub Repo**: https://github.com/Sushrut-01/ddn-jenkins-testing.git
   - **Jira Project**: DDN
   - **MongoDB Collections**: `ddn_test_failures`, `ddn_build_results`
   - **Pinecone Namespace**: `ddn`
   - **Jenkins Job**: DDN-Tests (port 8081)

2. **Guruttava Project** (project_id: 2, slug: "guruttava")
   - **Type**: Mobile + Web Automation
   - **Technologies**: Robot Framework, Appium, Android/iOS, Web
   - **GitHub Repo**: https://github.com/Sushrut-01/gurutattva-e2e-automation
   - **Jira Project**: GURU
   - **MongoDB Collections**: `guruttava_test_failures`, `guruttava_build_results`
   - **Pinecone Namespace**: `guruttava`
   - **Jenkins Job**: Guruttava-Tests (port 8081)

## Critical Data Isolation Rules

### ⚠️ NEVER MIX PROJECT DATA
1. **PostgreSQL**: ALL queries MUST include `WHERE project_id = ?`
2. **MongoDB**: Use project-specific collections (prefix: `ddn_`, `guruttava_`)
3. **Pinecone**: Query within project-specific namespace only
4. **Jenkins**: Each project has its own pipeline with PROJECT_ID and PROJECT_SLUG environment variables
5. **GitHub**: Separate repositories - never cross-reference

## System Components

### 1. Database Layer
- **PostgreSQL** (port 5434): Stores analysis results, Jira issues, PR workflows
  - Tables: `projects`, `user_projects`, `project_configurations`, `failure_analysis`, `jira_bugs`, `pr_workflows`
  - All tables have `project_id` column for isolation

- **MongoDB Atlas**: Stores raw test failures and build results
  - Collections use project prefix: `{project_slug}_test_failures`, `{project_slug}_build_results`
  - Each document includes `project_id` field

- **Pinecone**: Vector database for RAG-based analysis
  - Index: `ddn-knowledge-docs` (shared index)
  - Namespaces: `ddn` (DDN project), `guruttava` (Guruttava project)

### 2. Backend Services

#### A. Manual Trigger API (Python Workflow) - Port 5004
- **File**: `implementation/manual_trigger_api.py`
- **Purpose**: Triggers AI analysis for test failures
- **Key Endpoints**:
  - `POST /api/trigger-analysis` - Accepts `project_id` and `project_slug`
  - Queries project-specific MongoDB collections
  - Passes project context to LangGraph classifier
  - Stores results with `project_id`

#### B. Dashboard API - Port 5006
- **File**: `implementation/dashboard_api_full.py`
- **Purpose**: Serves dashboard data and stores analysis
- **Key Endpoints**:
  - `POST /api/analysis/store` - Stores analysis with `project_id`
  - `GET /api/projects` - Lists user's projects
  - `GET /api/projects/{id}` - Project details
- **Multi-Project Blueprints**:
  - `project_api.py` - CRUD operations for projects
  - `project_scoped_endpoints.py` - Project-filtered data endpoints

#### C. Jira Integration Service - Port 5009
- **File**: `implementation/jira_integration_service.py`
- **Purpose**: Creates/updates Jira tickets per project
- **Key Features**:
  - Fetches project-specific Jira configuration from database
  - Uses project's Jira key (DDN vs GURU)
  - Stores tickets with `project_id`

#### D. LangGraph AI Service - Port 5000
- **File**: LangGraph workflow
- **Purpose**: AI-powered test failure classification and analysis
- **Key Features**:
  - Classifier agent (CODE_ERROR, CONFIG_ERROR, etc.)
  - Root cause analyzer
  - Fix recommendation generator

### 3. Frontend (React Dashboard) - Port 5173
- **Location**: `implementation/dashboard-ui/`
- **Key Components**:
  - `ProjectSelector.jsx` - Dropdown for project switching
  - `ProjectManagement.jsx` - Project CRUD interface
  - `Layout.jsx` - Main layout with project selector in header
  - All pages filter data by selected project_id (from localStorage)

### 4. Jenkins CI/CD - Port 8081
- **DDN Jenkins Pipeline**:
  - Job: `DDN-Tests`
  - Config: `jenkins-jobs/DDN-Jenkinsfile`
  - Environment: `PROJECT_ID=1`, `PROJECT_SLUG=ddn`

- **Guruttava Jenkins Pipeline**:
  - Job: `Guruttava-Tests`
  - Config: `jenkins-jobs/Guruttava-Jenkinsfile`
  - Environment: `PROJECT_ID=2`, `PROJECT_SLUG=guruttava`

## Common Tasks and Guidelines

### Adding a New Project
1. Run SQL migration: Create record in `projects` and `project_configurations` tables
2. Create MongoDB collections: `{slug}_test_failures`, `{slug}_build_results` with indexes
3. Create Pinecone namespace: `{slug}`
4. Update `.env` with project-specific credentials
5. Create Jenkins pipeline with correct PROJECT_ID and PROJECT_SLUG
6. Assign users to project via `user_projects` table

### Debugging Data Issues
1. **Check Project Context**: Verify `project_id` is being passed through the entire flow
2. **Verify Database Queries**: Ensure all queries include `WHERE project_id = ?`
3. **Check MongoDB Collections**: Verify using correct collection prefix
4. **Inspect Frontend**: Check localStorage for selected project_id
5. **Review Jenkins Logs**: Confirm PROJECT_ID and PROJECT_SLUG environment variables

### Working with APIs

#### Triggering Analysis
```bash
curl -X POST http://localhost:5004/api/trigger-analysis \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Test-123",
    "project_id": 1,
    "project_slug": "ddn",
    "triggered_by_user": "user@example.com"
  }'
```

#### Storing Analysis
```bash
curl -X POST http://localhost:5006/api/analysis/store \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Test-123",
    "project_id": 1,
    "error_category": "CODE_ERROR",
    "root_cause": "Null pointer exception",
    "fix_recommendation": "Add null check",
    "confidence_score": 0.85
  }'
```

#### Creating Jira Issue
```bash
curl -X POST http://localhost:5009/api/jira/create-issue \
  -H "Content-Type: application/json" \
  -d '{
    "build_id": "DDN-Test-123",
    "project_id": 1,
    "error_category": "CODE_ERROR",
    "error_message": "Critical bug",
    "root_cause": "Race condition",
    "fix_recommendation": "Add mutex lock",
    "confidence_score": 0.95
  }'
```

## Code Modification Guidelines

### When Modifying Backend Code
1. **Always preserve project_id**: Never remove or modify project_id parameters
2. **Maintain isolation**: All database queries must filter by project_id
3. **Pass project context**: Include project_id and project_slug in all service calls
4. **Backward compatibility**: Default to project_id=1 (DDN) if not provided

### When Modifying Frontend Code
1. **Check project selection**: Always read project_id from localStorage or context
2. **Include in API calls**: Pass project_id in all API requests
3. **Filter data**: Display only data for selected project
4. **Handle switching**: Reload data when project changes

### When Creating Jenkins Jobs
1. **Set environment variables**: Always define PROJECT_ID and PROJECT_SLUG
2. **Use correct GitHub repo**: Each project has its own repository
3. **Parse results correctly**: Pass project context to robot_framework_parser.py
4. **Trigger API properly**: Include project_id in workflow trigger payload

## Environment Variables

### Required for All Projects
- `MONGODB_URI` - MongoDB Atlas connection string
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `PINECONE_API_KEY`, `PINECONE_KNOWLEDGE_INDEX`
- `GITHUB_TOKEN` (for GitHub API access)

### Project-Specific (DDN)
- `GITHUB_REPO_OWNER=Sushrut-01`
- `GITHUB_REPO_NAME=ddn-test-data`
- `JIRA_PROJECT_KEY=DDN`
- `JIRA_URL`, `JIRA_EMAIL`, `JIRA_TOKEN`

### Project-Specific (Guruttava)
- `GURUTTAVA_GITHUB_REPO_OWNER=Sushrut-01`
- `GURUTTAVA_GITHUB_REPO_NAME=gurutattva-e2e-automation`
- `GURUTTAVA_JIRA_PROJECT_KEY=GURU`
- `GURUTTAVA_JIRA_URL`, `GURUTTAVA_JIRA_EMAIL`, `GURUTTAVA_JIRA_TOKEN`
- `GURUTTAVA_MONGODB_PREFIX=guruttava_`
- `GURUTTAVA_PINECONE_NAMESPACE=guruttava`

## Testing Checklist

### Data Isolation Test
- [ ] Query failures for project_id=1, verify only DDN data returned
- [ ] Query failures for project_id=2, verify only Guruttava data returned
- [ ] Check MongoDB: ddn_test_failures only has project_id=1
- [ ] Check MongoDB: guruttava_test_failures only has project_id=2

### API Integration Test
- [ ] Trigger analysis for DDN, verify stored with project_id=1
- [ ] Trigger analysis for Guruttava, verify stored with project_id=2
- [ ] Create Jira ticket for DDN, verify uses "DDN" project key
- [ ] Create Jira ticket for Guruttava, verify uses "GURU" project key

### Dashboard Test
- [ ] Select DDN project, verify failures page shows only DDN data
- [ ] Select Guruttava project, verify failures page shows only Guruttava data
- [ ] Switch between projects, verify data refreshes correctly
- [ ] Check localStorage for project_id persistence

## Common Pitfalls to Avoid

1. **❌ Hardcoding project_id**: Always pass as parameter
2. **❌ Querying without project_id filter**: Will mix data across projects
3. **❌ Using wrong MongoDB collection**: Check project prefix
4. **❌ Querying wrong Pinecone namespace**: Use project-specific namespace
5. **❌ Missing PROJECT_ID in Jenkins**: Pipeline won't know which project
6. **❌ Cross-referencing GitHub repos**: Each project has its own repo
7. **❌ Reusing Jira project keys**: Each project has unique key

## Documentation Files

- `MULTI_PROJECT_ARCHITECTURE_DESIGN.md` - Complete architecture details
- `MULTI_PROJECT_IMPLEMENTATION_STATUS.md` - Implementation progress
- `END_TO_END_TESTING_GUIDE.md` - 9 comprehensive test cases
- `IMPLEMENTATION_COMPLETE_SUMMARY.md` - Summary of deliverables
- `READY_TO_TEST_NOW.md` - Quick test guide

## When Working on This Project, Always:

1. **Understand the project context** - Which project (DDN or Guruttava) are you working on?
2. **Maintain data isolation** - Never mix data between projects
3. **Pass project_id everywhere** - From Jenkins → API → Database
4. **Test thoroughly** - Verify data isolation after any changes
5. **Document changes** - Update relevant documentation files
6. **Follow existing patterns** - Study how other endpoints handle multi-project support

## Emergency Contacts & Resources

- **Database Migrations**: `implementation/migrations/`
- **API Services**: `implementation/` (Python files)
- **Frontend Code**: `implementation/dashboard-ui/src/`
- **Jenkins Configs**: `jenkins-jobs/`
- **Test Scripts**: `ddn-jenkins-testing/` and Guruttava repo

---

**Remember**: This is a multi-tenant system. Data isolation is CRITICAL. When in doubt, always verify project_id is being used correctly throughout the entire request flow.
