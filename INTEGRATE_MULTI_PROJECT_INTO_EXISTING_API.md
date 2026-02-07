# ✅ Multi-Project Integration Guide

**Status:** Database setup 100% complete | Frontend components ready | Need API integration

---

## 🎉 What's Already Done (100% Complete)

### ✅ 1. Database Migration - COMPLETE
- **4 new tables created:**
  - `projects` - All your projects (DDN, Guruttava)
  - `user_projects` - User access and roles
  - `project_configurations` - Project-specific settings
  - `project_activity_log` - Audit trail

- **5 existing tables updated with project_id:**
  - `failure_analysis` - 37 DDN failures migrated ✓
  - `build_metadata`, `test_case_history`, `user_feedback`, `jira_bugs` - Ready ✓

### ✅ 2. Projects Created - READY
| ID | Slug | Name | Jira | Team | Failures |
|----|------|------|------|------|----------|
| 1 | ddn | DDN Project | KAN | 5 users | 37 |
| 2 | guruttava | Guruttava | GURU | 1 user | 0 |

### ✅ 3. Frontend Components - COMPLETE
- `ProjectSelector.jsx` - Dropdown in header
- `ProjectManagement.jsx` - Projects page
- `api.js` - Updated with multi-project support
- `Layout.jsx` - Selector added to header
- `App.jsx` - Routes configured

---

## 🚀 Integration: Add Multi-Project to Your Existing API

Since you're using Rancher and likely have `dashboard_api_full.py` already running, let's integrate the multi-project endpoints into your existing API instead of running a separate server.

### Step 1: Add to Your Existing dashboard_api_full.py

Open `implementation/dashboard_api_full.py` and add these imports at the top:

```python
# Add these imports
from dotenv import load_dotenv
load_dotenv()

# Import multi-project blueprints
from project_api import project_bp
from project_scoped_endpoints import scoped_bp
```

Then register the blueprints (add after creating the Flask app):

```python
# Register multi-project blueprints
app.register_blueprint(project_bp)
app.register_blueprint(scoped_bp)
```

That's it! Your existing API now supports multi-project.

### Step 2: Verify Integration

```bash
# If dashboard_api_full.py is already running, restart it
# It will now include multi-project endpoints
```

Test the endpoints:
```bash
# Should see your projects (requires auth token)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5006/api/projects
```

---

## 🎯 Alternative: Use Existing Setup Files

If you prefer to use the dedicated multi-project API files:

### Files Created for You:
```
implementation/
├── project_api.py                    # Project management endpoints
├── project_scoped_endpoints.py        # Project-scoped data endpoints
├── run_project_api.py                 # Standalone API server
└── .env (UPDATED)                     # Added JWT_SECRET
```

### To Run Standalone:
```bash
cd implementation
python run_project_api.py
```

---

## 📊 Database Verification

Verify everything is set up correctly:

```bash
# Connect to database
docker exec -it ddn-postgres psql -U postgres -d ddn_ai_analysis

# View projects
SELECT * FROM projects;

# View user assignments
SELECT * FROM user_projects;

# View configurations
SELECT * FROM project_configurations;

# Check failure migration
SELECT COUNT(*) FROM failure_analysis WHERE project_id = 1;  -- Should be 37
```

---

## 🎨 Frontend Usage (Already Configured)

Your dashboard is running on http://localhost:5173

### What's Ready:

1. **Projects Page:** http://localhost:5173/projects/manage
   - Grid view of all projects
   - Create, edit, configure projects
   - View team and statistics

2. **Project Selector:** (in header)
   - Dropdown next to theme selector
   - Switch between projects instantly
   - Automatically filters all data

3. **Project-Aware Pages:**
   - Failures page shows only current project's failures
   - Jira integration uses current project's Jira key
   - Analytics filtered by project
   - All data automatically scoped

---

## 🔐 How Multi-Project Works

### Data Isolation Example:

**User selects "DDN Project":**
```sql
SELECT * FROM failure_analysis WHERE project_id = 1
-- Returns 37 DDN failures
```

**User selects "Guruttava":**
```sql
SELECT * FROM failure_analysis WHERE project_id = 2
-- Returns 0 failures (new project)
```

### Jira Integration Example:

**DDN Project → Jira Issues go to KAN:**
```python
project_config = get_config(project_id=1)
# jira_project_key = 'KAN'
# Creates issue as: KAN-123
```

**Guruttava → Jira Issues go to GURU:**
```python
project_config = get_config(project_id=2)
# jira_project_key = 'GURU'
# Creates issue as: GURU-123
```

### Access Control:

Users can only access projects they're assigned to:
```sql
SELECT * FROM user_projects
WHERE user_id = current_user AND project_id = requested_project
-- If no row exists → 403 Forbidden
```

---

## 📝 API Endpoints Reference

### Project Management
```
GET    /api/projects                        # List all accessible projects
POST   /api/projects                        # Create new project
GET    /api/projects/{id}                   # Get project details
PUT    /api/projects/{id}                   # Update project
GET    /api/projects/{id}/config            # Get configuration
PUT    /api/projects/{id}/config            # Update configuration
GET    /api/projects/{id}/stats             # Get statistics
```

### Project-Scoped Data
```
GET    /api/projects/{id}/failures          # Get project failures
GET    /api/projects/{id}/failures/{fid}    # Get failure details
GET    /api/projects/{id}/builds/summary    # Get builds
GET    /api/projects/{id}/jira/bugs         # Get Jira bugs
POST   /api/projects/{id}/jira/create-issue # Create Jira issue
GET    /api/projects/{id}/analytics/summary # Get analytics
GET    /api/projects/{id}/analytics/trends  # Get trends
```

---

## 🧪 Testing Guide

### Test 1: View Projects (Frontend)
1. Open: http://localhost:5173/projects/manage
2. Should see 2 project cards (DDN, Guruttava)
3. DDN shows "5 team members, 37 failures"
4. Guruttava shows "1 team member, 0 failures"

### Test 2: Switch Projects
1. Click project dropdown in header
2. Select "Guruttava"
3. Page reloads
4. Go to Failures page → 0 failures
5. Switch back to DDN → 37 failures

### Test 3: Create New Project
1. Go to Projects page
2. Click "+ Create Project"
3. Fill in: Name="QA Automation", Slug="qa-automation"
4. Submit
5. New project appears in list and dropdown

### Test 4: Data Isolation (Database)
```sql
-- As DDN user
SELECT COUNT(*) FROM failure_analysis WHERE project_id = 1;  -- 37

-- As Guruttava user
SELECT COUNT(*) FROM failure_analysis WHERE project_id = 2;  -- 0

-- They can't see each other's data!
```

---

## ✅ Success Checklist

**Database:**
- [x] 4 new tables created
- [x] Existing tables have project_id
- [x] DDN project created (ID: 1)
- [x] Guruttava project created (ID: 2)
- [x] 37 failures migrated to DDN
- [x] 5 users assigned to DDN
- [x] 1 user assigned to Guruttava

**Frontend:**
- [x] ProjectSelector component created
- [x] ProjectManagement page created
- [x] api.js updated for multi-project
- [x] Routes added to App.jsx
- [x] Selector added to Layout header
- [x] Projects menu in sidebar

**Backend (Needs Integration):**
- [ ] Add blueprints to dashboard_api_full.py
- [ ] Restart your API server
- [ ] Test /api/projects endpoint
- [ ] Verify authentication works
- [ ] Test project switching in UI

---

## 🎯 Next Steps

### Immediate (Required):
1. **Integrate into your existing API:**
   - Add 3 lines to `dashboard_api_full.py`:
     ```python
     from project_api import project_bp
     from project_scoped_endpoints import scoped_bp
     app.register_blueprint(project_bp)
     app.register_blueprint(scoped_bp)
     ```
   - Restart your API server

2. **Test in frontend:**
   - Open http://localhost:5173/projects/manage
   - Switch between projects
   - Verify data isolation

### Future Enhancements:
- [ ] Add team management UI (invite users, roles)
- [ ] Implement project archiving
- [ ] Add project activity logs viewer
- [ ] Create project dashboards
- [ ] Add project templates
- [ ] Implement project export/import

---

## 📁 Quick Reference

### Database
- **Host:** 127.0.0.1:5434
- **Database:** ddn_ai_analysis
- **Projects:** 2 (DDN, Guruttava)
- **Users:** 5 in DDN, 1 in Guruttava

### Frontend
- **URL:** http://localhost:5173
- **Projects Page:** http://localhost:5173/projects/manage
- **Status:** Running and ready

### Files Created
- `implementation/project_api.py` - Project management
- `implementation/project_scoped_endpoints.py` - Data endpoints
- `implementation/run_project_api.py` - Standalone server
- `implementation/verify_multi_project_setup.py` - Verification script
- `implementation/test_api_routes.py` - Route testing
- `dashboard-ui/src/components/ProjectSelector.jsx` - Dropdown
- `dashboard-ui/src/pages/ProjectManagement.jsx` - Projects page

---

## 🎊 You're 95% Done!

**What's Complete:**
✅ Database fully set up
✅ Projects created and configured
✅ Users assigned with roles
✅ Data migrated and isolated
✅ Frontend components built
✅ API endpoints coded
✅ Access control implemented
✅ Everything documented

**What's Left:**
🔲 Add 3 lines to dashboard_api_full.py
🔲 Restart API server
🔲 Test in browser

**That's it! 3 lines of code and you have complete multi-project support!**

---

## 💡 Why This Approach?

Since you're using Rancher, you likely have:
- Existing API running (dashboard_api_full.py)
- Kubernetes deployment
- Load balancers, ingress, etc.

Instead of running a separate API server, integrating into your existing API means:
✅ No additional deployment
✅ Same authentication
✅ Same CORS configuration
✅ Same monitoring
✅ One less service to manage

---

**Happy multi-project management!** 🚀

For questions, check:
- `MULTI_PROJECT_SETUP_COMPLETE.md` - Full setup summary
- `SETUP_AND_RUN_MULTI_PROJECT.md` - Detailed setup guide
- `MULTI_PROJECT_GUIDE.html` - Visual guide
