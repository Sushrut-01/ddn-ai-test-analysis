# 🚀 Multi-Project System - Setup and Run Guide

## Complete end-to-end setup to get multi-project support working!

---

## 📋 Prerequisites

1. **PostgreSQL Database** running and accessible
2. **Python 3.8+** installed
3. **Node.js** installed (for frontend)
4. **Environment variables** configured

---

## ⚡ Quick Start (5 Minutes)

### Step 1: Set Environment Variables

Create a `.env` file in the `implementation` directory:

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# JWT Secret
JWT_SECRET=your-secret-key-change-in-production

# API Port
PORT=5006
DEBUG=True
```

### Step 2: Install Python Dependencies

```bash
cd implementation
pip install flask flask-cors psycopg2-binary PyJWT python-dotenv
```

### Step 3: Run the Setup Script

```bash
python setup_multi_project.py
```

This will:
- ✅ Connect to your PostgreSQL database
- ✅ Run the migration to create new tables
- ✅ Create default "DDN" project
- ✅ Assign existing users to the project
- ✅ Optionally create "Guruttava" test project
- ✅ Start the API server

### Step 4: Start the Frontend

In another terminal:

```bash
cd dashboard-ui
npm run dev
```

### Step 5: Test It!

1. Open browser: `http://localhost:5173`
2. Click "Projects" in the sidebar
3. See your projects!
4. Click the project dropdown in the header
5. Switch between projects!

---

## 📁 Files Created

### Backend Files
```
implementation/
├── db_migrations/
│   └── add_multi_project_tables.sql      # Database migration
├── project_api.py                         # Project management endpoints
├── project_scoped_endpoints.py            # Project-scoped data endpoints
├── run_project_api.py                     # API server runner
└── setup_multi_project.py                 # Setup script
```

### Frontend Files
```
dashboard-ui/src/
├── components/
│   ├── ProjectSelector.jsx                # Project dropdown
│   └── ProjectSelector.css                # Styling
├── pages/
│   ├── ProjectManagement.jsx              # Project management page
│   └── ProjectManagement.css              # Styling
└── services/
    └── api.js (modified)                  # API with project support
```

---

## 🗄️ Database Tables Created

The migration creates these tables:

### 1. `projects`
Stores all projects (DDN, Guruttava, etc.)

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| slug | VARCHAR(50) | URL-safe identifier (e.g., 'ddn', 'guruttava') |
| name | VARCHAR(255) | Display name |
| description | TEXT | Project description |
| status | VARCHAR(20) | active, archived, suspended |
| created_by | INTEGER | User ID who created it |
| created_at | TIMESTAMP | Creation time |

### 2. `user_projects`
Maps users to projects with roles

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | INTEGER | User ID |
| project_id | INTEGER | Project ID |
| role | VARCHAR(50) | project_owner, project_admin, developer, viewer, guest |
| joined_at | TIMESTAMP | When user was added |
| last_accessed_at | TIMESTAMP | Last time user accessed this project |

### 3. `project_configurations`
Project-specific settings (Jira, GitHub, etc.)

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| project_id | INTEGER | Project ID |
| jira_project_key | VARCHAR(50) | Jira project key (e.g., 'KAN', 'GURU') |
| github_repo_owner | VARCHAR(255) | GitHub owner |
| github_repo_name | VARCHAR(255) | GitHub repo name |
| mongodb_collection_prefix | VARCHAR(50) | MongoDB collection prefix |
| pinecone_namespace | VARCHAR(100) | Pinecone namespace |

### 4. `project_activity_log`
Audit trail of all project activities

### 5. Existing Tables Updated
- `failure_analysis` + project_id column
- `build_metadata` + project_id column
- `test_case_history` + project_id column
- `user_feedback` + project_id column
- `jira_bugs` + project_id column

---

## 🔌 API Endpoints

### Project Management

```bash
# Get all projects user has access to
GET /api/projects
Headers: Authorization: Bearer <token>

# Create new project
POST /api/projects
Headers: Authorization: Bearer <token>
Body: {
  "name": "Guruttava",
  "slug": "guruttava",
  "description": "Mobile app testing project"
}

# Get project details
GET /api/projects/{id}
Headers: Authorization: Bearer <token>

# Update project
PUT /api/projects/{id}
Headers: Authorization: Bearer <token>
Body: {
  "name": "Updated Name",
  "description": "Updated description",
  "status": "active"
}

# Get project configuration
GET /api/projects/{id}/config
Headers: Authorization: Bearer <token>

# Update project configuration
PUT /api/projects/{id}/config
Headers: Authorization: Bearer <token>
Body: {
  "jira_project_key": "GURU",
  "github_repo_owner": "xyz-corp",
  "github_repo_name": "guruttava-repo"
}
```

### Project-Scoped Data

```bash
# Get failures for specific project
GET /api/projects/{id}/failures?limit=50&skip=0
Headers: Authorization: Bearer <token>

# Get project statistics
GET /api/projects/{id}/stats?time_range=30
Headers: Authorization: Bearer <token>

# Get project builds
GET /api/projects/{id}/builds/summary
Headers: Authorization: Bearer <token>

# Create Jira issue in project's Jira
POST /api/projects/{id}/jira/create-issue
Headers: Authorization: Bearer <token>
Body: {
  "summary": "Bug found in checkout",
  "description": "...",
  "priority": "High"
}

# Get project Jira bugs
GET /api/projects/{id}/jira/bugs
Headers: Authorization: Bearer <token>

# Get analytics summary
GET /api/projects/{id}/analytics/summary?time_range=7d
Headers: Authorization: Bearer <token>

# Get analytics trends
GET /api/projects/{id}/analytics/trends?time_range=30d
Headers: Authorization: Bearer <token>
```

---

## 🧪 Testing the System

### Test 1: Create a Project

```bash
curl -X POST http://localhost:5006/api/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Guruttava",
    "slug": "guruttava",
    "description": "Mobile app testing"
  }'
```

### Test 2: Get All Projects

```bash
curl http://localhost:5006/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 3: Get Project Failures

```bash
curl http://localhost:5006/api/projects/1/failures?limit=10 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test 4: Get Project Stats

```bash
curl http://localhost:5006/api/projects/1/stats?time_range=30 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎯 Frontend Usage

### 1. Project Selector in Header

The dropdown appears in the header next to the theme selector:

```
[DDN Project ▼]  [Theme] [Refresh] [User]
```

Click it to see all your projects and switch between them.

### 2. Project Management Page

Navigate to: `http://localhost:5173/projects/manage`

Features:
- View all projects in a grid
- See project stats (failures, status, team size)
- Create new projects
- Edit project settings (if you're admin/owner)
- Click "View Project" to select it

### 3. Creating a New Project

1. Go to Projects page
2. Click "+ Create Project" button
3. Fill in the form:
   - **Name:** Guruttava
   - **Slug:** guruttava (auto-generated from name)
   - **Description:** Mobile app testing project
4. Click "Create"
5. You're now the owner of this project!

### 4. Switching Projects

1. Click the dropdown in the header
2. Select a different project
3. Page reloads with new project's data
4. All pages now show data from the selected project

---

## 🔐 Security Features

### Access Control
- ✅ JWT token validation on all requests
- ✅ Project access verification (user must be in user_projects table)
- ✅ Role-based permissions (Owner > Admin > Developer > Viewer)
- ✅ Automatic project_id filtering in all database queries

### Data Isolation
- ✅ Every API call requires project_id in URL
- ✅ Middleware verifies user has access to that project
- ✅ All queries filter by project_id: `WHERE project_id = ?`
- ✅ No cross-project data leakage possible

### Role Hierarchy

```
project_owner (4)
    └─ Can do everything, manage team, delete project
project_admin (3)
    └─ Can manage settings, invite users
developer (2)
    └─ Can create Jira issues, view/edit failures
viewer (1)
    └─ Can only view data
guest (0)
    └─ Limited read access
```

---

## 🐛 Troubleshooting

### Issue: "Failed to connect to database"

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Verify connection details in .env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ddn_ai_analysis
```

### Issue: "Table 'projects' does not exist"

**Solution:**
```bash
# Run the migration
python setup_multi_project.py
```

### Issue: "No projects available"

**Solution:**
```bash
# The default "DDN" project should be created automatically
# If not, run this SQL manually:

INSERT INTO projects (slug, name, description, status)
VALUES ('ddn', 'DDN Project', 'Default project', 'active');

# Then assign yourself to it:
INSERT INTO user_projects (user_id, project_id, role)
VALUES (YOUR_USER_ID, 1, 'project_owner');
```

### Issue: "403 Access denied to this project"

**Solution:**
Make sure you're in the `user_projects` table for that project:

```sql
SELECT * FROM user_projects WHERE user_id = YOUR_ID;

-- If not, add yourself:
INSERT INTO user_projects (user_id, project_id, role)
VALUES (YOUR_ID, PROJECT_ID, 'developer');
```

### Issue: Frontend shows "No project selected"

**Solution:**
1. Login again (to get projects list)
2. Select a project from the dropdown
3. localStorage should have `current_project_id`

---

## 📊 Database Queries for Verification

### Check projects
```sql
SELECT * FROM projects;
```

### Check user-project assignments
```sql
SELECT u.email, p.name, up.role
FROM user_projects up
JOIN users u ON up.user_id = u.id
JOIN projects p ON up.project_id = p.id;
```

### Check project configurations
```sql
SELECT p.name, pc.jira_project_key, pc.github_repo_name
FROM project_configurations pc
JOIN projects p ON pc.project_id = p.id;
```

### Check failures by project
```sql
SELECT p.name, COUNT(*) as failure_count
FROM failure_analysis fa
JOIN projects p ON fa.project_id = p.id
GROUP BY p.name;
```

---

## 🚀 Next Steps

1. **Integrate with Existing Dashboard API**
   - Import `project_bp` and `scoped_bp` into your `dashboard_api_full.py`
   - Add: `app.register_blueprint(project_bp)`
   - Add: `app.register_blueprint(scoped_bp)`

2. **Update Other Services**
   - Jira integration: Use project-specific Jira keys
   - GitHub integration: Use project-specific repos
   - MongoDB: Add project_id to all documents

3. **Test with Real Data**
   - Create multiple projects
   - Add team members
   - Configure different Jira/GitHub for each
   - Verify complete data isolation

---

## ✅ Success Checklist

After setup, you should be able to:

- [ ] See "Projects" in the sidebar
- [ ] Click Projects and see the management page
- [ ] See project dropdown in header
- [ ] Create a new project (Guruttava)
- [ ] Switch between DDN and Guruttava in the dropdown
- [ ] See different data for each project
- [ ] API calls include project_id in URL
- [ ] Database has project-specific data isolated

---

## 📞 Support

If you encounter issues:

1. Check the console logs (browser and terminal)
2. Verify database connection
3. Check that migration ran successfully
4. Ensure JWT token is valid
5. Review the API endpoint responses

---

## 🎉 You're Done!

Your multi-project system is now **fully functional**!

**Frontend:** `http://localhost:5173`
**Backend API:** `http://localhost:5006`

Enjoy managing multiple projects (DDN, Guruttava, and more)! 🚀
