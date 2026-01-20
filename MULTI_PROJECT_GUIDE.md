# Multi-Project Guide: Working with DDN and Guruttava Separately

## Overview

You now have **2 projects** configured in your dashboard:

1. **DDN (Default)** - Default project for existing data
2. **Guruttava** - Mobile (Android/iOS) and Web test automation using Robot Framework

Both projects are completely isolated - test failures, build data, analytics, and configurations are kept separate for each project.

---

## How to Switch Between Projects

### Option 1: Project Selection Modal (Recommended)

1. **Login** to http://localhost:5173/
   - Email: `admin@example.com`
   - Password: `admin123`

2. **Project Selection Modal** appears automatically after login
   - Shows both DDN and Guruttava projects
   - Each project shows: name, description, role, and recent failure count

3. **Click on a project** to enter it
   - All dashboard pages will now show data for that project only
   - Project name appears in the header/navigation

4. **Switch Projects** anytime:
   - Click the project selector in the top navigation bar
   - Choose the other project from the dropdown
   - Dashboard will reload with the selected project's data

### Option 2: Direct URL with Project Context

Each API endpoint accepts a project context:

```bash
# Get DDN project data
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5006/api/failures?project_id=1"

# Get Guruttava project data
curl -H "Authorization: Bearer TOKEN" \
  "http://localhost:5006/api/failures?project_id=2"
```

---

## Your Project Access

As **project_owner** of both projects, you have:
- ✅ Full read/write access to all data
- ✅ Can manage project settings
- ✅ Can invite other users to projects
- ✅ Can create/delete test failures
- ✅ Can configure integrations (Jira, GitHub)

---

## Project Configuration

### DDN Project
```
ID: 1
Slug: ddn
Jira Key: KAN
MongoDB Prefix: ddn_
Pinecone Namespace: ddn_knowledge
GitHub Repo: Sushrut-01/DDN_01
```

### Guruttava Project
```
ID: 2
Slug: guruttava
Jira Key: GURU
MongoDB Prefix: guruttava_
Pinecone Namespace: guruttava
GitHub Repo: Sushrut-01/DDN_01
CI Provider: Jenkins
```

---

## Data Isolation

Each project has **completely separate**:

### 1. Test Failures
- **DDN failures** stored with `project_id = 1`
- **Guruttava failures** stored with `project_id = 2`
- No cross-project visibility

### 2. MongoDB Collections
- **DDN**: `ddn_test_failures`, `ddn_build_results`
- **Guruttava**: `guruttava_test_failures`, `guruttava_build_results`

### 3. Pinecone Indexes
- **DDN**: Namespace `ddn_knowledge`
- **Guruttava**: Namespace `guruttava`
- Knowledge bases don't overlap

### 4. Analytics & Dashboards
- **DDN Dashboard**: Shows only DDN test results, trends, and failures
- **Guruttava Dashboard**: Shows only Guruttava test results, trends, and failures

---

## Working with Multiple Projects

### Scenario 1: Different Test Suites
- **DDN Project**: Web application tests (Selenium, Playwright)
- **Guruttava Project**: Mobile app tests (Appium, Robot Framework)

Each project maintains separate:
- Test case history
- Failure patterns
- AI analysis results
- Jira integration (different Jira projects)

### Scenario 2: Multiple Teams
- **Team A** works on DDN web tests
- **Team B** works on Guruttava mobile tests
- Both teams see only their project's data
- Admins can access both projects

### Scenario 3: Client Separation
- **Client 1 (DDN)**: All test data, reports, and analytics
- **Client 2 (Guruttava)**: Separate test data, reports, and analytics
- Perfect for consulting/service companies

---

## Jenkins Configuration

### DDN Jenkins Jobs
Configure webhook to send `project_id=1` or `project_slug=ddn`:
```bash
POST http://localhost:5004/api/trigger-analysis
{
  "project_id": 1,
  "build_id": "DDN-123",
  "job_name": "DDN-Test-Job"
}
```

### Guruttava Jenkins Jobs
Configure webhook to send `project_id=2` or `project_slug=guruttava`:
```bash
POST http://localhost:5004/api/trigger-analysis
{
  "project_id": 2,
  "build_id": "GURU-456",
  "job_name": "Guruttava-E2E-Tests"
}
```

---

## API Endpoints with Project Support

All API endpoints now support project filtering:

### Get Project-Specific Failures
```bash
GET /api/failures?project_id=1  # DDN failures only
GET /api/failures?project_id=2  # Guruttava failures only
```

### Get Project-Specific Analytics
```bash
GET /api/analytics/failure-trends?project_id=1  # DDN trends
GET /api/analytics/failure-trends?project_id=2  # Guruttava trends
```

### Get Project-Specific Jira Bugs
```bash
GET /api/jira/bugs?project_id=1  # DDN Jira issues
GET /api/jira/bugs?project_id=2  # Guruttava Jira issues
```

---

## Adding More Projects

To add a third project (e.g., "QA-Automation"):

```sql
-- Create project
INSERT INTO projects (slug, name, description, status, created_by)
VALUES ('qa-automation', 'QA Automation', 'Description here', 'active', 1);

-- Configure project
INSERT INTO project_configurations (project_id, jira_project_key, mongodb_collection_prefix, pinecone_namespace)
VALUES ((SELECT id FROM projects WHERE slug = 'qa-automation'), 'QA', 'qa_', 'qa_automation');

-- Assign user access
INSERT INTO user_projects (user_id, project_id, role)
VALUES (1, (SELECT id FROM projects WHERE slug = 'qa-automation'), 'project_owner');
```

---

## Project Roles

Each user can have different roles in different projects:

- **project_owner**: Full control over project (you have this for both)
- **project_admin**: Can manage settings and users
- **developer**: Can view and create test data
- **viewer**: Read-only access
- **guest**: Limited temporary access

Example: User can be `project_owner` in DDN but only `developer` in Guruttava.

---

## Best Practices

### 1. Use Project Context Everywhere
Always specify which project you're working with:
- In API calls: Pass `project_id` or `project_slug`
- In UI: Select project before viewing data
- In Jenkins: Configure project context in webhooks

### 2. Keep Configurations Separate
- Different Jira projects for each team
- Different GitHub repos or branches
- Different MongoDB collections
- Different Pinecone namespaces

### 3. Invite Team Members Appropriately
- Only invite users to projects they need access to
- Use appropriate roles (don't give everyone project_owner)
- Review user access regularly

---

## Troubleshooting

### Can't See Expected Data
- **Check**: Are you in the correct project?
- **Solution**: Switch projects using the project selector

### Failures Not Showing
- **Check**: Is Jenkins sending the correct `project_id`?
- **Solution**: Verify webhook configuration includes project context

### Wrong Project Data
- **Check**: Is the API call including `project_id` parameter?
- **Solution**: Add `?project_id=X` to API requests

---

## Dashboard Features Per Project

Each project has its own:

1. **Test Failures List** (filtered by project)
2. **Analytics Dashboard** (project-specific metrics)
3. **AI Root Cause Analysis** (project knowledge base)
4. **PR Workflow** (project GitHub repo)
5. **Jira Integration** (project Jira tickets)
6. **Manual Trigger** (creates failures in selected project)
7. **Test Case Generator** (uses project patterns)
8. **Activity Log** (project-specific actions)

---

## Summary

**You Can Now:**
- ✅ Switch between DDN and Guruttava projects anytime
- ✅ Each project has completely isolated data
- ✅ Same beautiful emerald theme across both projects
- ✅ Full project_owner access to both projects
- ✅ Configure Jenkins to send data to correct project
- ✅ Invite different teams to different projects
- ✅ Scale to unlimited projects as needed

**Login Now**: http://localhost:5173/
- Select DDN project → See DDN data
- Select Guruttava project → See Guruttava data
- Switch anytime using the project selector!
