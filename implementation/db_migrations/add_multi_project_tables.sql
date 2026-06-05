-- =============================================
-- DDN AI Platform - Multi-Project Support
-- Migration: Add Multi-Project Tables
-- =============================================

-- Step 1: Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_by INTEGER,
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_status CHECK (status IN ('active', 'archived', 'suspended'))
);

CREATE INDEX idx_projects_slug ON projects(slug);
CREATE INDEX idx_projects_status ON projects(status);

-- Step 2: Create user_projects junction table
CREATE TABLE IF NOT EXISTS user_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    permissions JSONB DEFAULT '[]',
    invited_by INTEGER,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    UNIQUE(user_id, project_id),
    CONSTRAINT valid_project_role CHECK (role IN ('project_owner', 'project_admin', 'developer', 'viewer', 'guest'))
);

CREATE INDEX idx_user_projects_user ON user_projects(user_id);
CREATE INDEX idx_user_projects_project ON user_projects(project_id);
CREATE INDEX idx_user_projects_role ON user_projects(role);

-- Step 3: Create project_configurations table
CREATE TABLE IF NOT EXISTS project_configurations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    jira_project_key VARCHAR(50),
    jira_url VARCHAR(255),
    jira_email VARCHAR(255),
    jira_api_token TEXT,
    github_repo_owner VARCHAR(255),
    github_repo_name VARCHAR(255),
    github_default_branch VARCHAR(100) DEFAULT 'main',
    github_token TEXT,
    ci_provider VARCHAR(50),
    ci_webhook_url TEXT,
    mongodb_collection_prefix VARCHAR(50),
    pinecone_namespace VARCHAR(100),
    confidence_threshold DECIMAL(3,2) DEFAULT 0.70,
    custom_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_project_config UNIQUE(project_id)
);

CREATE INDEX idx_project_config_project ON project_configurations(project_id);

-- Step 4: Create project_activity_log table
CREATE TABLE IF NOT EXISTS project_activity_log (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER,
    activity_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete'))
);

CREATE INDEX idx_project_activity_project ON project_activity_log(project_id);
CREATE INDEX idx_project_activity_user ON project_activity_log(user_id);
CREATE INDEX idx_project_activity_type ON project_activity_log(activity_type);
CREATE INDEX idx_project_activity_created ON project_activity_log(created_at);

-- Step 5: Add project_id columns to existing tables (if they exist)
DO $$
BEGIN
    -- Add project_id to failure_analysis if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'failure_analysis') THEN
        ALTER TABLE failure_analysis ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
        CREATE INDEX IF NOT EXISTS idx_failure_analysis_project ON failure_analysis(project_id);
    END IF;

    -- Add project_id to build_metadata if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'build_metadata') THEN
        ALTER TABLE build_metadata ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
        CREATE INDEX IF NOT EXISTS idx_build_metadata_project ON build_metadata(project_id);
    END IF;

    -- Add project_id to test_case_history if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_case_history') THEN
        ALTER TABLE test_case_history ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
        CREATE INDEX IF NOT EXISTS idx_test_case_history_project ON test_case_history(project_id);
    END IF;

    -- Add project_id to user_feedback if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_feedback') THEN
        ALTER TABLE user_feedback ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
        CREATE INDEX IF NOT EXISTS idx_user_feedback_project ON user_feedback(project_id);
    END IF;

    -- Add project_id to jira_bugs if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jira_bugs') THEN
        ALTER TABLE jira_bugs ADD COLUMN IF NOT EXISTS project_id INTEGER REFERENCES projects(id);
        CREATE INDEX IF NOT EXISTS idx_jira_bugs_project ON jira_bugs(project_id);
    END IF;
END $$;

-- Step 6: Create default project for existing data
INSERT INTO projects (slug, name, description, status, created_at)
VALUES ('ddn', 'DDN Project', 'Default project for existing data', 'active', CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO NOTHING;

-- Step 7: Create default configuration for the default project
INSERT INTO project_configurations (project_id, jira_project_key, mongodb_collection_prefix, pinecone_namespace)
SELECT p.id, 'KAN', 'ddn_', 'ddn_knowledge'
FROM projects p
WHERE p.slug = 'ddn'
ON CONFLICT (project_id) DO NOTHING;

-- Step 8: Assign all existing users to the default project as developers
DO $$
DECLARE
    default_project_id INTEGER;
BEGIN
    SELECT id INTO default_project_id FROM projects WHERE slug = 'ddn';

    IF default_project_id IS NOT NULL THEN
        -- Check if users table exists
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
            INSERT INTO user_projects (user_id, project_id, role, joined_at)
            SELECT id, default_project_id, 'developer', CURRENT_TIMESTAMP
            FROM users
            ON CONFLICT (user_id, project_id) DO NOTHING;

            -- Make first admin user the project owner
            UPDATE user_projects
            SET role = 'project_owner'
            WHERE project_id = default_project_id
            AND user_id = (SELECT id FROM users WHERE role = 'admin' ORDER BY id LIMIT 1);
        END IF;
    END IF;
END $$;

-- Step 9: Backfill existing data with default project_id
DO $$
DECLARE
    default_project_id INTEGER;
BEGIN
    SELECT id INTO default_project_id FROM projects WHERE slug = 'ddn';

    IF default_project_id IS NOT NULL THEN
        -- Update failure_analysis
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'failure_analysis') THEN
            UPDATE failure_analysis SET project_id = default_project_id WHERE project_id IS NULL;
        END IF;

        -- Update build_metadata
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'build_metadata') THEN
            UPDATE build_metadata SET project_id = default_project_id WHERE project_id IS NULL;
        END IF;

        -- Update test_case_history
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'test_case_history') THEN
            UPDATE test_case_history SET project_id = default_project_id WHERE project_id IS NULL;
        END IF;

        -- Update user_feedback
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_feedback') THEN
            UPDATE user_feedback SET project_id = default_project_id WHERE project_id IS NULL;
        END IF;

        -- Update jira_bugs
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jira_bugs') THEN
            UPDATE jira_bugs SET project_id = default_project_id WHERE project_id IS NULL;
        END IF;
    END IF;
END $$;

-- Step 10: Create helper functions
CREATE OR REPLACE FUNCTION user_has_project_access(p_user_id INTEGER, p_project_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_projects
        WHERE user_id = p_user_id AND project_id = p_project_id
    );
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user_project_role(p_user_id INTEGER, p_project_id INTEGER)
RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR(50);
BEGIN
    SELECT role INTO user_role
    FROM user_projects
    WHERE user_id = p_user_id AND project_id = p_project_id;

    RETURN COALESCE(user_role, 'none');
END;
$$ LANGUAGE plpgsql;

-- Verification
DO $$
DECLARE
    project_count INTEGER;
    user_project_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO project_count FROM projects;
    SELECT COUNT(*) INTO user_project_count FROM user_projects;

    RAISE NOTICE 'Migration Complete!';
    RAISE NOTICE 'Projects created: %', project_count;
    RAISE NOTICE 'User-project assignments: %', user_project_count;
END $$;
