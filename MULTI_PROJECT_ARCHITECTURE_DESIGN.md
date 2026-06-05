# Multi-Project Architecture Design
## DDN AI Platform - Enterprise Multi-Tenancy Strategy

**Document Version:** 1.0
**Date:** 2026-01-13
**Status:** Architecture Design & Implementation Plan
**Architect:** Senior Technical Planner

---

## Executive Summary

Transform the DDN AI Platform from a **single-project system** to an **enterprise-grade multi-tenant platform** capable of managing unlimited projects (DDN, Guruttava, and beyond) with complete data isolation, project-specific configurations, and scalable architecture.

### Current State
- ❌ Single project hardcoded (DDN/KAN)
- ❌ No project isolation in database
- ❌ Global authentication without project-scoped roles
- ❌ Hardcoded Jira/GitHub configurations
- ❌ No tenant separation in MongoDB/Pinecone

### Target State
- ✅ Multi-project support with complete isolation
- ✅ Project-scoped RBAC (Role-Based Access Control)
- ✅ Per-project configurations (Jira, GitHub, CI/CD)
- ✅ Scalable data architecture with tenant separation
- ✅ Project management UI and APIs

---

## 1. ARCHITECTURE OPTIONS ANALYSIS

### Option A: Multi-Tenant Single Database (RECOMMENDED)
**Pattern:** Shared Database, Shared Schema with `project_id` discriminator

```
┌─────────────────────────────────────────────────┐
│           PostgreSQL Database                    │
│  ┌───────────────────────────────────────────┐  │
│  │  failure_analysis                         │  │
│  │  - id, project_id, build_id, error_msg   │  │
│  │  WHERE project_id = ?                     │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │  build_metadata                           │  │
│  │  - id, project_id, job_name, status      │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Pros:**
- ✅ Simpler infrastructure management
- ✅ Cross-project analytics possible
- ✅ Cost-effective for small-medium scale
- ✅ Easier backup/restore strategy
- ✅ Single connection pool

**Cons:**
- ❌ Must implement Row-Level Security (RLS)
- ❌ Query filtering required on every query
- ❌ Risk of data leakage if filtering missed
- ❌ Noisy neighbor problem at scale

**Best For:** 10-100 projects, shared infrastructure

---

### Option B: Database-per-Tenant
**Pattern:** Separate PostgreSQL database for each project

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ddn_project  │  │ guruttava_db │  │ projectX_db  │
│              │  │              │  │              │
│ - failures   │  │ - failures   │  │ - failures   │
│ - builds     │  │ - builds     │  │ - builds     │
└──────────────┘  └──────────────┘  └──────────────┘
```

**Pros:**
- ✅ Complete data isolation
- ✅ Per-project backups
- ✅ No query filtering needed
- ✅ Easier compliance (GDPR, SOC2)
- ✅ Independent scaling

**Cons:**
- ❌ Complex database management
- ❌ Cross-project analytics difficult
- ❌ Higher infrastructure costs
- ❌ Schema migrations to all DBs

**Best For:** Enterprise, 100+ projects, strict isolation requirements

---

### Option C: Hybrid Approach (ENTERPRISE RECOMMENDED)
**Pattern:** Shared metadata DB + Project-specific data DBs

```
┌───────────────────────┐
│  Central Metadata DB  │
│  - projects           │
│  - users              │
│  - user_projects      │
│  - configurations     │
└───────────────────────┘
         │
    ┌────┴────┬─────────┬─────────┐
    │         │         │         │
┌───▼───┐ ┌──▼────┐ ┌──▼────┐ ┌──▼────┐
│ DDN   │ │Gurutta│ │Project│ │Project│
│  DB   │ │va DB  │ │  3 DB │ │  N DB │
└───────┘ └───────┘ └───────┘ └───────┘
```

**Pros:**
- ✅ Best security and isolation
- ✅ Centralized user management
- ✅ Scalable to unlimited projects
- ✅ Per-project performance tuning

**Cons:**
- ❌ Most complex implementation
- ❌ Requires dynamic DB routing

**Best For:** SaaS platform, unlimited scale

---

## 2. RECOMMENDED ARCHITECTURE: Option A + C Migration Path

**Phase 1-2:** Implement Option A (Multi-tenant single DB)
**Phase 3+:** Migrate to Option C as project count grows

### Why This Approach?
1. **Start Simple:** Option A provides quick multi-project support
2. **Proven Pattern:** Used by Slack, Atlassian, GitHub for early growth
3. **Migration Path:** Easy to migrate projects to separate DBs later
4. **Cost-Effective:** Optimize infrastructure costs initially

---

## 3. DETAILED TECHNICAL DESIGN

### 3.1 Database Schema Design

#### A. Core Multi-Tenancy Tables

```sql
-- ============================================
-- PROJECTS TABLE - Central project registry
-- ============================================
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,  -- URL-safe: 'ddn', 'guruttava'
    name VARCHAR(255) NOT NULL,        -- Display name
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, archived, suspended

    -- Project ownership
    created_by INTEGER REFERENCES users(id),

    -- Metadata
    settings JSONB DEFAULT '{}',  -- Project-specific settings
    metadata JSONB DEFAULT '{}',  -- Custom fields

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_status CHECK (status IN ('active', 'archived', 'suspended'))
);

CREATE INDEX idx_projects_slug ON projects(slug);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- ============================================
-- USER_PROJECTS - Junction table with roles
-- ============================================
CREATE TABLE user_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Project-specific role
    role VARCHAR(50) NOT NULL,  -- project_owner, project_admin, developer, viewer

    -- Access control
    permissions JSONB DEFAULT '[]',  -- ['create_issues', 'approve_fixes', 'view_analytics']

    -- Audit
    invited_by INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,

    -- Constraints
    UNIQUE(user_id, project_id),
    CONSTRAINT valid_project_role CHECK (role IN ('project_owner', 'project_admin', 'developer', 'viewer', 'guest'))
);

CREATE INDEX idx_user_projects_user ON user_projects(user_id);
CREATE INDEX idx_user_projects_project ON user_projects(project_id);
CREATE INDEX idx_user_projects_role ON user_projects(role);

-- ============================================
-- PROJECT_CONFIGURATIONS - Integration settings
-- ============================================
CREATE TABLE project_configurations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Jira Configuration
    jira_project_key VARCHAR(50),
    jira_url VARCHAR(255),
    jira_email VARCHAR(255),
    jira_api_token_encrypted TEXT,  -- Encrypted token

    -- GitHub Configuration
    github_repo_owner VARCHAR(255),
    github_repo_name VARCHAR(255),
    github_default_branch VARCHAR(100) DEFAULT 'main',
    github_token_encrypted TEXT,

    -- CI/CD Configuration
    ci_provider VARCHAR(50),  -- jenkins, github_actions, gitlab_ci
    ci_webhook_url TEXT,
    ci_job_patterns JSONB DEFAULT '[]',  -- ['unit-tests', 'integration-tests']

    -- MongoDB Configuration
    mongodb_collection_prefix VARCHAR(50),  -- 'ddn_', 'guruttava_'

    -- Pinecone Configuration
    pinecone_namespace VARCHAR(100),  -- 'ddn_knowledge', 'guruttava_knowledge'

    -- AI Configuration
    ai_model_preferences JSONB DEFAULT '{}',
    confidence_threshold DECIMAL(3,2) DEFAULT 0.70,

    -- Metadata
    custom_config JSONB DEFAULT '{}',

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_project_config UNIQUE(project_id)
);

CREATE INDEX idx_project_config_project ON project_configurations(project_id);
```

#### B. Modified Existing Tables (Add project_id)

```sql
-- ============================================
-- FAILURE_ANALYSIS - Add project isolation
-- ============================================
ALTER TABLE failure_analysis
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_failure_analysis_project ON failure_analysis(project_id);

-- Row-Level Security Policy
ALTER TABLE failure_analysis ENABLE ROW LEVEL SECURITY;

CREATE POLICY project_isolation_policy ON failure_analysis
    USING (project_id IN (
        SELECT project_id FROM user_projects WHERE user_id = current_setting('app.current_user_id')::INTEGER
    ));

-- ============================================
-- BUILD_METADATA - Add project isolation
-- ============================================
ALTER TABLE build_metadata
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_build_metadata_project ON build_metadata(project_id);

-- ============================================
-- TEST_CASE_HISTORY - Add project isolation
-- ============================================
ALTER TABLE test_case_history
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_test_case_history_project ON test_case_history(project_id);

-- ============================================
-- USER_FEEDBACK - Add project context
-- ============================================
ALTER TABLE user_feedback
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_user_feedback_project ON user_feedback(project_id);

-- ============================================
-- FAILURE_PATTERNS - Project-scoped patterns
-- ============================================
ALTER TABLE failure_patterns
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_failure_patterns_project ON failure_patterns(project_id);

-- ============================================
-- AI_MODEL_METRICS - Per-project metrics
-- ============================================
ALTER TABLE ai_model_metrics
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_ai_model_metrics_project ON ai_model_metrics(project_id);

-- ============================================
-- JIRA_BUGS - Link to projects
-- ============================================
ALTER TABLE jira_bugs
ADD COLUMN project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE;

CREATE INDEX idx_jira_bugs_project ON jira_bugs(project_id);
```

#### C. Project Activity Audit Table

```sql
-- ============================================
-- PROJECT_ACTIVITY_LOG - Comprehensive audit
-- ============================================
CREATE TABLE project_activity_log (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),

    -- Activity details
    activity_type VARCHAR(50) NOT NULL,  -- 'failure_analyzed', 'jira_created', 'config_updated'
    entity_type VARCHAR(50),             -- 'failure', 'build', 'configuration'
    entity_id INTEGER,

    -- Changes
    action VARCHAR(20) NOT NULL,         -- 'create', 'update', 'delete', 'view'
    old_values JSONB,
    new_values JSONB,

    -- Context
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete'))
);

CREATE INDEX idx_project_activity_project ON project_activity_log(project_id);
CREATE INDEX idx_project_activity_user ON project_activity_log(user_id);
CREATE INDEX idx_project_activity_type ON project_activity_log(activity_type);
CREATE INDEX idx_project_activity_created ON project_activity_log(created_at);
```

---

### 3.2 API Architecture Design

#### A. Project Context Middleware

```python
# implementation/middleware/project_context.py

from functools import wraps
from flask import request, g, jsonify
import jwt

def require_project_access(required_role=None):
    """
    Middleware to validate project access

    Usage:
        @require_project_access(required_role='developer')
        def update_failure(project_id, failure_id):
            # User has developer role or higher in this project
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract project_id from URL or body
            project_id = kwargs.get('project_id') or request.json.get('project_id')

            if not project_id:
                return jsonify({'error': 'project_id required'}), 400

            # Get user from JWT token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = payload['user_id']
            except:
                return jsonify({'error': 'Invalid token'}), 401

            # Check project access
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT role, permissions FROM user_projects
                WHERE user_id = %s AND project_id = %s
            """, (user_id, project_id))

            result = cur.fetchone()
            if not result:
                return jsonify({'error': 'Access denied to this project'}), 403

            role, permissions = result

            # Role hierarchy check
            role_hierarchy = ['viewer', 'developer', 'project_admin', 'project_owner']
            if required_role:
                if role_hierarchy.index(role) < role_hierarchy.index(required_role):
                    return jsonify({'error': f'Requires {required_role} role'}), 403

            # Store in request context
            g.project_id = project_id
            g.user_id = user_id
            g.project_role = role
            g.project_permissions = permissions

            return f(*args, **kwargs)

        return decorated_function
    return decorator
```

#### B. Updated API Endpoints Structure

```python
# implementation/dashboard_api_full.py

from middleware.project_context import require_project_access

# ============================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================

@app.route('/api/projects', methods=['GET'])
@require_auth
def get_user_projects():
    """Get all projects accessible to current user"""
    user_id = g.user_id

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.slug, p.name, p.description, p.status,
               up.role, up.permissions, up.last_accessed_at,
               COUNT(fa.id) as failure_count
        FROM projects p
        JOIN user_projects up ON p.id = up.project_id
        LEFT JOIN failure_analysis fa ON p.id = fa.project_id AND fa.created_at > NOW() - INTERVAL '30 days'
        WHERE up.user_id = %s AND p.status = 'active'
        GROUP BY p.id, up.role, up.permissions, up.last_accessed_at
        ORDER BY up.last_accessed_at DESC
    """, (user_id,))

    projects = []
    for row in cur.fetchall():
        projects.append({
            'id': row[0],
            'slug': row[1],
            'name': row[2],
            'description': row[3],
            'status': row[4],
            'my_role': row[5],
            'my_permissions': row[6],
            'last_accessed': row[7].isoformat() if row[7] else None,
            'recent_failure_count': row[8]
        })

    return jsonify({'projects': projects})

@app.route('/api/projects', methods=['POST'])
@require_auth
@require_role('admin')  # Only global admins can create projects
def create_project():
    """Create new project"""
    data = request.json
    user_id = g.user_id

    # Validate
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'name and slug required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Create project
        cur.execute("""
            INSERT INTO projects (slug, name, description, created_by)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (data['slug'], data['name'], data.get('description'), user_id))

        project_id = cur.fetchone()[0]

        # Add creator as project_owner
        cur.execute("""
            INSERT INTO user_projects (user_id, project_id, role, invited_by)
            VALUES (%s, %s, 'project_owner', %s)
        """, (user_id, project_id, user_id))

        # Create default configuration
        cur.execute("""
            INSERT INTO project_configurations (project_id, mongodb_collection_prefix, pinecone_namespace)
            VALUES (%s, %s, %s)
        """, (project_id, f"{data['slug']}_", f"{data['slug']}_knowledge"))

        conn.commit()

        return jsonify({'project_id': project_id, 'message': 'Project created'}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects/<int:project_id>', methods=['GET'])
@require_project_access()
def get_project_details(project_id):
    """Get detailed project information"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Project details
    cur.execute("""
        SELECT p.*, pc.*
        FROM projects p
        LEFT JOIN project_configurations pc ON p.id = pc.project_id
        WHERE p.id = %s
    """, (project_id,))

    project = cur.fetchone()

    # Team members
    cur.execute("""
        SELECT u.id, u.email, u.name, up.role, up.joined_at
        FROM users u
        JOIN user_projects up ON u.id = up.user_id
        WHERE up.project_id = %s
        ORDER BY up.joined_at
    """, (project_id,))

    team = [{'id': row[0], 'email': row[1], 'name': row[2], 'role': row[3], 'joined_at': row[4].isoformat()}
            for row in cur.fetchall()]

    return jsonify({
        'project': dict(project),
        'team': team
    })

# ============================================
# FAILURE ANALYSIS ENDPOINTS (Project-scoped)
# ============================================

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_project_access(required_role='viewer')
def get_project_failures(project_id):
    """Get failures for specific project"""
    # Pagination
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))

    # Filters
    category = request.args.get('category')
    feedback_status = request.args.get('feedback_status')

    conn = get_db_connection()
    cur = conn.cursor()

    # Build query with project isolation
    query = """
        SELECT fa.*, bm.job_name, bm.build_url
        FROM failure_analysis fa
        JOIN build_metadata bm ON fa.build_id = bm.build_id
        WHERE fa.project_id = %s
    """
    params = [project_id]

    if category:
        query += " AND fa.classification = %s"
        params.append(category)

    if feedback_status:
        query += " AND fa.feedback_status = %s"
        params.append(feedback_status)

    query += " ORDER BY fa.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    cur.execute(query, params)

    failures = []
    for row in cur.fetchall():
        failures.append({
            'id': row[0],
            'build_id': row[1],
            'error_message': row[2],
            'classification': row[3],
            'confidence_score': float(row[4]),
            'root_cause': row[5],
            'suggested_fix': row[6],
            'job_name': row[-2],
            'build_url': row[-1]
        })

    return jsonify({'failures': failures, 'total': len(failures)})

@app.route('/api/projects/<int:project_id>/stats', methods=['GET'])
@require_project_access(required_role='viewer')
def get_project_stats(project_id):
    """Get analytics for specific project"""
    time_range = request.args.get('time_range', '30')  # days

    conn = get_db_connection()
    cur = conn.cursor()

    # Total failures
    cur.execute("""
        SELECT COUNT(*) FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
    """, (project_id, time_range))
    total_failures = cur.fetchone()[0]

    # Classification breakdown
    cur.execute("""
        SELECT classification, COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY classification
    """, (project_id, time_range))
    classification_breakdown = {row[0]: row[1] for row in cur.fetchall()}

    # Trend data
    cur.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """, (project_id, time_range))
    trend = [{'date': row[0].isoformat(), 'count': row[1]} for row in cur.fetchall()]

    return jsonify({
        'total_failures': total_failures,
        'classification_breakdown': classification_breakdown,
        'trend': trend,
        'project_id': project_id
    })

# ============================================
# JIRA INTEGRATION (Project-scoped)
# ============================================

@app.route('/api/projects/<int:project_id>/jira/create-issue', methods=['POST'])
@require_project_access(required_role='developer')
def create_jira_issue_for_project(project_id):
    """Create Jira issue in project's Jira project"""
    data = request.json

    # Get project configuration
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT jira_project_key, jira_url, jira_email, jira_api_token_encrypted
        FROM project_configurations
        WHERE project_id = %s
    """, (project_id,))

    config = cur.fetchone()
    if not config or not config[0]:
        return jsonify({'error': 'Jira not configured for this project'}), 400

    jira_key, jira_url, jira_email, encrypted_token = config

    # Decrypt token
    jira_token = decrypt_token(encrypted_token)

    # Create Jira client
    jira = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))

    # Create issue
    issue_dict = {
        'project': {'key': jira_key},
        'summary': data['summary'],
        'description': data['description'],
        'issuetype': {'name': data.get('issue_type', 'Bug')},
        'priority': {'name': data.get('priority', 'Medium')}
    }

    new_issue = jira.create_issue(fields=issue_dict)

    # Log to database
    cur.execute("""
        INSERT INTO jira_bugs (project_id, jira_key, jira_url, summary, description, priority, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (project_id, new_issue.key, new_issue.permalink(), data['summary'],
          data['description'], data.get('priority', 'Medium'), 'Open'))

    conn.commit()

    return jsonify({'jira_key': new_issue.key, 'url': new_issue.permalink()})

# ============================================
# PROJECT CONFIGURATION ENDPOINTS
# ============================================

@app.route('/api/projects/<int:project_id>/config', methods=['GET'])
@require_project_access(required_role='project_admin')
def get_project_config(project_id):
    """Get project configuration (admin only)"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM project_configurations WHERE project_id = %s", (project_id,))

    config = cur.fetchone()

    # Don't return encrypted tokens
    return jsonify({
        'jira_project_key': config[2],
        'jira_url': config[3],
        'github_repo_owner': config[6],
        'github_repo_name': config[7],
        'ci_provider': config[10],
        'confidence_threshold': float(config[15]) if config[15] else 0.70
    })

@app.route('/api/projects/<int:project_id>/config', methods=['PUT'])
@require_project_access(required_role='project_admin')
def update_project_config(project_id):
    """Update project configuration"""
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    # Build dynamic update query
    update_fields = []
    params = []

    if 'jira_project_key' in data:
        update_fields.append("jira_project_key = %s")
        params.append(data['jira_project_key'])

    if 'jira_api_token' in data:
        encrypted_token = encrypt_token(data['jira_api_token'])
        update_fields.append("jira_api_token_encrypted = %s")
        params.append(encrypted_token)

    if 'github_repo_owner' in data:
        update_fields.append("github_repo_owner = %s")
        params.append(data['github_repo_owner'])

    if 'confidence_threshold' in data:
        update_fields.append("confidence_threshold = %s")
        params.append(data['confidence_threshold'])

    if not update_fields:
        return jsonify({'error': 'No fields to update'}), 400

    params.append(project_id)

    query = f"""
        UPDATE project_configurations
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE project_id = %s
    """

    cur.execute(query, params)
    conn.commit()

    # Log activity
    log_project_activity(project_id, g.user_id, 'config_updated', 'configuration', None, data)

    return jsonify({'message': 'Configuration updated'})
```

---

### 3.3 Frontend Architecture

#### A. Project Selector Component

```jsx
// implementation/dashboard-ui/src/components/ProjectSelector.jsx

import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getProjects } from '../services/api';

export default function ProjectSelector() {
    const [projects, setProjects] = useState([]);
    const [currentProject, setCurrentProject] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const response = await getProjects();
            setProjects(response.projects);

            // Get current project from localStorage or URL
            const storedProjectId = localStorage.getItem('current_project_id');
            const urlProjectId = new URLSearchParams(location.search).get('project_id');

            const projectId = urlProjectId || storedProjectId;
            if (projectId) {
                const project = response.projects.find(p => p.id === parseInt(projectId));
                if (project) {
                    setCurrentProject(project);
                }
            } else if (response.projects.length > 0) {
                // Default to first project
                setCurrentProject(response.projects[0]);
                localStorage.setItem('current_project_id', response.projects[0].id);
            }
        } catch (error) {
            console.error('Failed to load projects:', error);
        }
    };

    const handleProjectChange = (project) => {
        setCurrentProject(project);
        localStorage.setItem('current_project_id', project.id);

        // Update URL with project context
        const params = new URLSearchParams(location.search);
        params.set('project_id', project.id);
        navigate(`${location.pathname}?${params.toString()}`);

        // Reload page data
        window.location.reload();
    };

    return (
        <div className="project-selector">
            <select
                value={currentProject?.id || ''}
                onChange={(e) => {
                    const project = projects.find(p => p.id === parseInt(e.target.value));
                    handleProjectChange(project);
                }}
                className="project-dropdown"
            >
                {projects.map(project => (
                    <option key={project.id} value={project.id}>
                        {project.name} ({project.slug})
                    </option>
                ))}
            </select>

            {currentProject && (
                <div className="project-info">
                    <span className="role-badge">{currentProject.my_role}</span>
                    <span className="failure-count">{currentProject.recent_failure_count} failures (30d)</span>
                </div>
            )}
        </div>
    );
}
```

#### B. Updated API Service

```javascript
// implementation/dashboard-ui/src/services/api.js

const getCurrentProjectId = () => {
    return localStorage.getItem('current_project_id');
};

const projectAPI = {
    getAll: () => axios.get(`${API_BASE_URL}/api/projects`),

    getDetails: (projectId) => axios.get(`${API_BASE_URL}/api/projects/${projectId}`),

    create: (data) => axios.post(`${API_BASE_URL}/api/projects`, data),

    getConfig: (projectId) => axios.get(`${API_BASE_URL}/api/projects/${projectId}/config`),

    updateConfig: (projectId, data) => axios.put(`${API_BASE_URL}/api/projects/${projectId}/config`, data)
};

const failuresAPI = {
    getList: (params = {}) => {
        const projectId = getCurrentProjectId();
        if (!projectId) throw new Error('No project selected');

        return axios.get(`${API_BASE_URL}/api/projects/${projectId}/failures`, { params });
    },

    getById: (failureId) => {
        const projectId = getCurrentProjectId();
        return axios.get(`${API_BASE_URL}/api/projects/${projectId}/failures/${failureId}`);
    }
};

const analyticsAPI = {
    getStats: (timeRange = '30') => {
        const projectId = getCurrentProjectId();
        return axios.get(`${API_BASE_URL}/api/projects/${projectId}/stats`, {
            params: { time_range: timeRange }
        });
    }
};

const jiraAPI = {
    createIssue: (data) => {
        const projectId = getCurrentProjectId();
        return axios.post(`${API_BASE_URL}/api/projects/${projectId}/jira/create-issue`, data);
    }
};

export { projectAPI, failuresAPI, analyticsAPI, jiraAPI, getCurrentProjectId };
```

---

### 3.4 MongoDB Multi-Tenancy Strategy

#### Option 1: Shared Database with project_id (Recommended)

```python
# implementation/mongodb_service.py

class MongoDBService:
    def __init__(self):
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client[MONGODB_DB]

        # Ensure indexes for project isolation
        self.db.test_failures.create_index([('project_id', 1), ('build_id', 1)])
        self.db.build_results.create_index([('project_id', 1), ('timestamp', -1)])

    def insert_failure(self, project_id, failure_data):
        """Insert failure with project context"""
        failure_data['project_id'] = project_id
        failure_data['created_at'] = datetime.utcnow()

        result = self.db.test_failures.insert_one(failure_data)
        return str(result.inserted_id)

    def get_failures(self, project_id, filters=None):
        """Get failures for specific project"""
        query = {'project_id': project_id}

        if filters:
            query.update(filters)

        return list(self.db.test_failures.find(query).sort('created_at', -1))

    def get_build_results(self, project_id, build_id=None):
        """Get build results for project"""
        query = {'project_id': project_id}

        if build_id:
            query['build_id'] = build_id

        return list(self.db.build_results.find(query))
```

#### Option 2: Separate Collections per Project

```python
def get_collection_name(project_slug, collection_type):
    """Generate project-specific collection name"""
    return f"{project_slug}_{collection_type}"

class ProjectMongoDBService:
    def insert_failure(self, project_slug, failure_data):
        collection_name = get_collection_name(project_slug, 'test_failures')
        collection = self.db[collection_name]

        return collection.insert_one(failure_data)
```

---

### 3.5 Pinecone Multi-Tenancy (Namespaces)

```python
# implementation/knowledge_base_service.py

from pinecone import Pinecone

class KnowledgeBaseService:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(PINECONE_INDEX_NAME)

    def get_namespace(self, project_id):
        """Get Pinecone namespace for project"""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT pinecone_namespace FROM project_configurations WHERE project_id = %s
        """, (project_id,))

        result = cur.fetchone()
        return result[0] if result else f"project_{project_id}"

    def upsert_knowledge(self, project_id, doc_id, embedding, metadata):
        """Upsert knowledge document to project namespace"""
        namespace = self.get_namespace(project_id)

        self.index.upsert(
            vectors=[(doc_id, embedding, metadata)],
            namespace=namespace
        )

    def query_knowledge(self, project_id, query_embedding, top_k=5):
        """Query knowledge base within project namespace"""
        namespace = self.get_namespace(project_id)

        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            namespace=namespace,
            include_metadata=True
        )

        return results['matches']

    def delete_project_data(self, project_id):
        """Delete all data for a project (namespace)"""
        namespace = self.get_namespace(project_id)

        # Delete all vectors in namespace
        self.index.delete(delete_all=True, namespace=namespace)
```

---

## 4. MIGRATION STRATEGY

### Phase 1: Foundation (Week 1-2)
**Goal:** Setup multi-tenant database schema

**Tasks:**
1. Create migration script for new tables
   - `projects`
   - `user_projects`
   - `project_configurations`
   - `project_activity_log`

2. Add `project_id` columns to existing tables
   - Use `ALTER TABLE ADD COLUMN`
   - Create indexes

3. Create default project for existing data
   - Project name: "DDN (Legacy)"
   - Slug: "ddn"
   - Backfill `project_id` for all existing records

4. Test migration on staging environment

**Rollback Plan:**
```sql
-- Rollback script
DROP TABLE IF EXISTS project_activity_log;
DROP TABLE IF EXISTS project_configurations;
DROP TABLE IF EXISTS user_projects;
DROP TABLE IF EXISTS projects;

ALTER TABLE failure_analysis DROP COLUMN IF EXISTS project_id;
ALTER TABLE build_metadata DROP COLUMN IF EXISTS project_id;
-- ... for all tables
```

---

### Phase 2: Backend API (Week 3-4)
**Goal:** Implement project-aware APIs

**Tasks:**
1. Create middleware
   - `require_project_access` decorator
   - JWT token validation with projects

2. Implement project management endpoints
   - `/api/projects` (CRUD)
   - `/api/projects/<id>/config`
   - `/api/projects/<id>/team`

3. Update existing endpoints
   - Add project_id parameter
   - Filter queries by project
   - Update response schemas

4. Update integration services
   - Jira: Dynamic project key lookup
   - GitHub: Project-specific repos
   - MongoDB: Project filtering

5. Write unit tests
   - Test project isolation
   - Test access control
   - Test configuration management

**Testing:**
```bash
# Test project isolation
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5006/api/projects/1/failures"

# Should return 403 if user not in project
curl -H "Authorization: Bearer $OTHER_USER_TOKEN" \
  "http://localhost:5006/api/projects/1/failures"
```

---

### Phase 3: Frontend UI (Week 5-6)
**Goal:** Add project selector and update all pages

**Tasks:**
1. Create ProjectSelector component
   - Dropdown with user's projects
   - Store selection in localStorage
   - Update URL with project context

2. Update all pages
   - FailuresPreview: Filter by project
   - AnalyticsPreview: Project-specific stats
   - JiraBugsPreview: Project's Jira issues
   - ConfigurationPreview: Project settings

3. Add project management UI
   - Create project modal
   - Project settings page
   - Team management page

4. Update API service layer
   - Add `getCurrentProjectId()` helper
   - Include project_id in all API calls

5. Handle project switching
   - Clear cached data
   - Reload current page with new project context

**UI Mock:**
```
┌─────────────────────────────────────────────┐
│  [DDN ▼]  Failures | Analytics | Jira | ... │
│   └─ DDN                                     │
│   └─ Guruttava                               │
│   └─ Project X                               │
└─────────────────────────────────────────────┘
```

---

### Phase 4: Integration Services (Week 7-8)
**Goal:** Make Jira, GitHub, MongoDB project-aware

**Tasks:**
1. Update Jira integration
   - Fetch project config from DB
   - Use project-specific Jira key
   - Store credentials securely (encrypted)

2. Update GitHub integration
   - Support multiple repos per project
   - Project-specific PR tracking

3. Update MongoDB service
   - Add project_id to all documents
   - Create project-specific indexes

4. Update Pinecone integration
   - Use namespaces per project
   - Implement namespace management

5. Update AI analysis service
   - Pass project context to AI models
   - Use project-specific knowledge base

---

### Phase 5: Authentication & Authorization (Week 9)
**Goal:** Implement project-based RBAC

**Tasks:**
1. Update JWT token structure
   - Include projects array
   - Add project roles

2. Implement role hierarchy
   - `project_owner` > `project_admin` > `developer` > `viewer` > `guest`

3. Create permission system
   - Define permissions (e.g., `create_issues`, `approve_fixes`)
   - Check permissions in middleware

4. Add team management APIs
   - Invite users to projects
   - Update user roles
   - Remove users from projects

5. Implement Row-Level Security (RLS) in PostgreSQL
   - Enable RLS on all tables
   - Create policies for project isolation

---

### Phase 6: Testing & Validation (Week 10)
**Goal:** Comprehensive testing of multi-tenancy

**Test Cases:**
1. **Data Isolation**
   - User A (DDN project) cannot see User B's data (Guruttava)
   - API calls with wrong project_id return 403

2. **Role-Based Access**
   - Viewers can only read, not create/update
   - Project admins can modify configurations
   - Project owners can manage team

3. **Configuration Isolation**
   - Project A's Jira issues go to JIRA_KEY_A
   - Project B's GitHub PRs tracked in REPO_B

4. **Performance Testing**
   - Simulate 100 projects with 10,000 failures each
   - Ensure query performance < 500ms

5. **Security Testing**
   - SQL injection attempts
   - Authorization bypass attempts
   - Cross-project data leakage

---

### Phase 7: Deployment (Week 11-12)
**Goal:** Production deployment with zero downtime

**Steps:**
1. **Pre-deployment:**
   - Backup production database
   - Test migration on staging
   - Prepare rollback scripts

2. **Deployment:**
   - Enable maintenance mode (optional)
   - Run database migrations
   - Deploy backend services
   - Deploy frontend
   - Verify health checks

3. **Post-deployment:**
   - Create default project for existing data
   - Assign all existing users to default project
   - Monitor error logs
   - Verify data integrity

4. **Rollout:**
   - Phase 1: Internal testing (1 week)
   - Phase 2: Beta users (2 weeks)
   - Phase 3: Full rollout

---

## 5. SECURITY CONSIDERATIONS

### 5.1 Data Isolation

**Row-Level Security (RLS) in PostgreSQL:**
```sql
-- Enable RLS on all sensitive tables
ALTER TABLE failure_analysis ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see data from their projects
CREATE POLICY project_isolation_policy ON failure_analysis
    FOR ALL
    USING (
        project_id IN (
            SELECT project_id
            FROM user_projects
            WHERE user_id = current_setting('app.current_user_id')::INTEGER
        )
    );

-- Set user context in application
SET LOCAL app.current_user_id = 123;
```

### 5.2 Credential Management

**Encryption for Project Credentials:**
```python
from cryptography.fernet import Fernet

class CredentialManager:
    def __init__(self):
        self.key = os.getenv('ENCRYPTION_KEY').encode()
        self.cipher = Fernet(self.key)

    def encrypt_token(self, token):
        """Encrypt API token"""
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token):
        """Decrypt API token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()

# Usage
cm = CredentialManager()
encrypted = cm.encrypt_token(jira_api_token)

# Store in database
cur.execute("""
    UPDATE project_configurations
    SET jira_api_token_encrypted = %s
    WHERE project_id = %s
""", (encrypted, project_id))
```

### 5.3 API Security

**Rate Limiting per Project:**
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: f"{g.user_id}_{g.project_id}",
    default_limits=["1000 per hour", "100 per minute"]
)

@app.route('/api/projects/<int:project_id>/failures')
@limiter.limit("500 per hour")
@require_project_access()
def get_failures(project_id):
    # Rate limited per user per project
    pass
```

---

## 6. MONITORING & OBSERVABILITY

### 6.1 Project-Level Metrics

```python
# implementation/monitoring/project_metrics.py

from prometheus_client import Counter, Histogram, Gauge

# Metrics
project_requests = Counter('project_requests_total', 'Total requests per project', ['project_id', 'endpoint'])
project_latency = Histogram('project_request_latency_seconds', 'Request latency per project', ['project_id'])
project_active_users = Gauge('project_active_users', 'Active users per project', ['project_id'])

# Usage in middleware
@app.before_request
def track_project_metrics():
    if hasattr(g, 'project_id'):
        project_requests.labels(project_id=g.project_id, endpoint=request.endpoint).inc()

        start_time = time.time()

        @after_this_request
        def after_request(response):
            latency = time.time() - start_time
            project_latency.labels(project_id=g.project_id).observe(latency)
            return response
```

### 6.2 Alerting Rules

```yaml
# alerting_rules.yml

groups:
  - name: project_health
    rules:
      - alert: ProjectHighFailureRate
        expr: rate(failure_analysis_created[5m]) > 10
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High failure rate in project {{ $labels.project_id }}"

      - alert: ProjectAPILatency
        expr: project_request_latency_seconds{quantile="0.95"} > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency for project {{ $labels.project_id }}"
```

---

## 7. SCALING CONSIDERATIONS

### 7.1 Performance Optimization

**Database Indexing Strategy:**
```sql
-- Composite indexes for common queries
CREATE INDEX idx_failure_analysis_project_created ON failure_analysis(project_id, created_at DESC);
CREATE INDEX idx_build_metadata_project_status ON build_metadata(project_id, status);

-- Partial indexes for active projects
CREATE INDEX idx_active_projects ON projects(id) WHERE status = 'active';
```

**Query Optimization:**
```python
# Use connection pooling per project
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True  # Health check before using connection
)
```

### 7.2 Caching Strategy

```python
# Redis caching with project namespace
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_project_stats(project_id):
    # Check cache
    cache_key = f"project:{project_id}:stats:30d"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    # Query database
    stats = query_stats_from_db(project_id)

    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(stats))

    return stats
```

### 7.3 Horizontal Scaling

**Microservices Architecture (Future):**
```
┌─────────────────┐
│   API Gateway   │ (Route by project_id)
└────────┬────────┘
         │
    ┌────┴────┬─────────────┬──────────────┐
    │         │             │              │
┌───▼───┐ ┌──▼────┐ ┌──────▼─────┐ ┌──────▼─────┐
│Project│ │Failure│ │   Jira     │ │  Analytics │
│Service│ │Service│ │  Service   │ │   Service  │
└───────┘ └───────┘ └────────────┘ └────────────┘
```

---

## 8. COST ESTIMATION

### 8.1 Infrastructure Costs (Monthly)

| Component | Single Project | 10 Projects | 100 Projects |
|-----------|---------------|-------------|--------------|
| PostgreSQL RDS | $100 | $200 | $500 |
| MongoDB Atlas | $50 | $100 | $300 |
| Redis Cache | $30 | $50 | $100 |
| Pinecone | $70 | $150 | $500 |
| API Servers (EC2) | $100 | $200 | $800 |
| Load Balancer | $20 | $30 | $50 |
| **Total** | **$370** | **$730** | **$2,250** |

### 8.2 Development Costs

| Phase | Duration | Effort | Cost (Est.) |
|-------|----------|--------|-------------|
| Phase 1: Foundation | 2 weeks | 80 hours | $8,000 |
| Phase 2: Backend API | 2 weeks | 80 hours | $8,000 |
| Phase 3: Frontend | 2 weeks | 80 hours | $8,000 |
| Phase 4: Integration | 2 weeks | 80 hours | $8,000 |
| Phase 5: Auth & RBAC | 1 week | 40 hours | $4,000 |
| Phase 6: Testing | 1 week | 40 hours | $4,000 |
| Phase 7: Deployment | 2 weeks | 80 hours | $8,000 |
| **Total** | **12 weeks** | **480 hours** | **$48,000** |

---

## 9. RISK ASSESSMENT & MITIGATION

### Risk Matrix

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data leakage between projects | Critical | Medium | Implement RLS, thorough testing |
| Migration data loss | Critical | Low | Backup before migration, rollback plan |
| Performance degradation | High | Medium | Load testing, query optimization |
| Incorrect project assignment | High | Medium | Audit logs, validation checks |
| Third-party API limits | Medium | High | Rate limiting, retry logic |

---

## 10. SUCCESS CRITERIA

### Definition of Done

- [ ] Database schema supports unlimited projects
- [ ] API endpoints filter by project_id
- [ ] Frontend has project selector
- [ ] Users can create/manage projects
- [ ] Project-specific Jira/GitHub integrations work
- [ ] Complete data isolation verified
- [ ] RBAC enforced (viewer, developer, admin roles)
- [ ] Migration script tested and documented
- [ ] Performance benchmarks met (<500ms API response)
- [ ] Security audit passed (no cross-project data leakage)
- [ ] Documentation complete (API, user guide, admin guide)
- [ ] Monitoring and alerting in place

---

## 11. NEXT STEPS

### Immediate Actions (This Week)

1. **Review & Approve Architecture**
   - Stakeholder review
   - Choose architecture option (A, B, or C)
   - Approve migration strategy

2. **Setup Development Environment**
   - Create `feature/multi-project` branch
   - Setup staging database
   - Configure test projects

3. **Start Phase 1: Foundation**
   - Write migration scripts
   - Create new tables
   - Test on staging

### Questions for Decision

1. **Architecture Choice:**
   - Start with Option A (Single DB) or jump to Option C (Hybrid)?
   - Expected number of projects in 1 year? 5 years?

2. **Migration Strategy:**
   - Migrate existing data to "DDN (Legacy)" project?
   - Or create separate "DDN" and "KAN" projects?

3. **Access Control:**
   - Should some users have access to all projects (super admin)?
   - Should projects be isolated or allow cross-project views?

4. **Billing:**
   - Will projects be tied to billing/subscriptions?
   - Need usage tracking per project?

---

## 12. APPENDIX

### A. Sample Migration Script

See: `implementation/migrations/add_multi_project_support.sql`

### B. API Documentation

See: `docs/API_MULTI_PROJECT.md`

### C. Frontend Component Library

See: `implementation/dashboard-ui/src/components/project/`

### D. Testing Checklist

See: `docs/MULTI_PROJECT_TESTING.md`

---

**Document Prepared By:** Senior Technical Architect
**Last Updated:** 2026-01-13
**Next Review:** Upon approval for Phase 1 implementation

---

## Summary

This architecture transforms the DDN AI Platform from a single-project tool into an **enterprise-grade multi-tenant system** capable of supporting DDN, Guruttava, and unlimited future projects with:

✅ Complete data isolation
✅ Project-specific configurations
✅ Scalable architecture
✅ Role-based access control
✅ Secure credential management
✅ Performance optimizations
✅ Clear migration path

**Recommended Approach:** Start with Option A (Multi-tenant single DB) and migrate to Option C (Hybrid) as you scale.

**Timeline:** 12 weeks for full implementation
**Cost:** ~$48,000 development + $730/month infrastructure (10 projects)

Ready to proceed with Phase 1?
