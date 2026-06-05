-- ============================================
-- MIGRATION: Multi-Project Support
-- Version: 001
-- Date: 2026-01-13
-- Description: Add multi-tenancy support with project isolation
-- ============================================

-- ============================================
-- STEP 1: Create Core Multi-Tenancy Tables
-- ============================================

-- Projects table: Central registry of all projects
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active',

    -- Ownership
    created_by INTEGER REFERENCES users(id),

    -- Settings
    settings JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_status CHECK (status IN ('active', 'archived', 'suspended'))
);

CREATE INDEX idx_projects_slug ON projects(slug);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);

COMMENT ON TABLE projects IS 'Central registry of all projects in the system';
COMMENT ON COLUMN projects.slug IS 'URL-safe identifier for project (e.g., ddn, guruttava)';

-- User-Project association with roles
CREATE TABLE IF NOT EXISTS user_projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Role in this project
    role VARCHAR(50) NOT NULL,

    -- Additional permissions (array of permission strings)
    permissions JSONB DEFAULT '[]',

    -- Audit fields
    invited_by INTEGER REFERENCES users(id),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,

    UNIQUE(user_id, project_id),
    CONSTRAINT valid_project_role CHECK (role IN ('project_owner', 'project_admin', 'developer', 'viewer', 'guest'))
);

CREATE INDEX idx_user_projects_user ON user_projects(user_id);
CREATE INDEX idx_user_projects_project ON user_projects(project_id);
CREATE INDEX idx_user_projects_role ON user_projects(role);

COMMENT ON TABLE user_projects IS 'Junction table managing user access and roles in projects';

-- Project configurations for integrations
CREATE TABLE IF NOT EXISTS project_configurations (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- Jira Configuration
    jira_project_key VARCHAR(50),
    jira_url VARCHAR(255),
    jira_email VARCHAR(255),
    jira_api_token_encrypted TEXT,

    -- GitHub Configuration
    github_repo_owner VARCHAR(255),
    github_repo_name VARCHAR(255),
    github_default_branch VARCHAR(100) DEFAULT 'main',
    github_token_encrypted TEXT,

    -- CI/CD Configuration
    ci_provider VARCHAR(50),
    ci_webhook_url TEXT,
    ci_job_patterns JSONB DEFAULT '[]',

    -- MongoDB Configuration
    mongodb_collection_prefix VARCHAR(50),

    -- Pinecone Configuration
    pinecone_namespace VARCHAR(100),

    -- AI Configuration
    ai_model_preferences JSONB DEFAULT '{}',
    confidence_threshold DECIMAL(3,2) DEFAULT 0.70,

    -- Custom settings
    custom_config JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_project_config UNIQUE(project_id)
);

CREATE INDEX idx_project_config_project ON project_configurations(project_id);

COMMENT ON TABLE project_configurations IS 'Project-specific integration and service configurations';

-- Project activity audit log
CREATE TABLE IF NOT EXISTS project_activity_log (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),

    -- Activity details
    activity_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,

    -- Action performed
    action VARCHAR(20) NOT NULL,
    old_values JSONB,
    new_values JSONB,

    -- Request context
    ip_address VARCHAR(45),
    user_agent TEXT,

    -- Additional metadata
    metadata JSONB DEFAULT '{}',

    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_action CHECK (action IN ('create', 'read', 'update', 'delete'))
);

CREATE INDEX idx_project_activity_project ON project_activity_log(project_id);
CREATE INDEX idx_project_activity_user ON project_activity_log(user_id);
CREATE INDEX idx_project_activity_type ON project_activity_log(activity_type);
CREATE INDEX idx_project_activity_created ON project_activity_log(created_at);

COMMENT ON TABLE project_activity_log IS 'Comprehensive audit trail of all project activities';

-- ============================================
-- STEP 2: Add project_id to Existing Tables
-- ============================================

-- failure_analysis
ALTER TABLE failure_analysis ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE failure_analysis ADD CONSTRAINT fk_failure_analysis_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_failure_analysis_project ON failure_analysis(project_id);
CREATE INDEX IF NOT EXISTS idx_failure_analysis_project_created ON failure_analysis(project_id, created_at DESC);

-- build_metadata
ALTER TABLE build_metadata ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE build_metadata ADD CONSTRAINT fk_build_metadata_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_build_metadata_project ON build_metadata(project_id);
CREATE INDEX IF NOT EXISTS idx_build_metadata_project_status ON build_metadata(project_id, status);

-- test_case_history
ALTER TABLE test_case_history ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE test_case_history ADD CONSTRAINT fk_test_case_history_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_test_case_history_project ON test_case_history(project_id);

-- user_feedback
ALTER TABLE user_feedback ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE user_feedback ADD CONSTRAINT fk_user_feedback_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_user_feedback_project ON user_feedback(project_id);

-- acceptance_tracking
ALTER TABLE acceptance_tracking ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE acceptance_tracking ADD CONSTRAINT fk_acceptance_tracking_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_acceptance_tracking_project ON acceptance_tracking(project_id);

-- failure_patterns
ALTER TABLE failure_patterns ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE failure_patterns ADD CONSTRAINT fk_failure_patterns_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_failure_patterns_project ON failure_patterns(project_id);

-- manual_trigger_log
ALTER TABLE manual_trigger_log ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE manual_trigger_log ADD CONSTRAINT fk_manual_trigger_log_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_manual_trigger_log_project ON manual_trigger_log(project_id);

-- ai_model_metrics
ALTER TABLE ai_model_metrics ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE ai_model_metrics ADD CONSTRAINT fk_ai_model_metrics_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_ai_model_metrics_project ON ai_model_metrics(project_id);

-- knowledge_doc_changes
ALTER TABLE knowledge_doc_changes ADD COLUMN IF NOT EXISTS project_id INTEGER;
ALTER TABLE knowledge_doc_changes ADD CONSTRAINT fk_knowledge_doc_changes_project
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_knowledge_doc_changes_project ON knowledge_doc_changes(project_id);

-- Add project_id to jira_bugs if table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jira_bugs') THEN
        ALTER TABLE jira_bugs ADD COLUMN IF NOT EXISTS project_id INTEGER;
        ALTER TABLE jira_bugs ADD CONSTRAINT fk_jira_bugs_project
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE;
        CREATE INDEX IF NOT EXISTS idx_jira_bugs_project ON jira_bugs(project_id);
    END IF;
END $$;

-- ============================================
-- STEP 3: Create Default Project for Existing Data
-- ============================================

-- Insert default "DDN" project
INSERT INTO projects (slug, name, description, status, created_at)
VALUES ('ddn', 'DDN (Default)', 'Default project for existing data', 'active', CURRENT_TIMESTAMP)
ON CONFLICT (slug) DO NOTHING;

-- Get the default project ID
DO $$
DECLARE
    default_project_id INTEGER;
BEGIN
    SELECT id INTO default_project_id FROM projects WHERE slug = 'ddn';

    -- Update all existing records with default project_id
    UPDATE failure_analysis SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE build_metadata SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE test_case_history SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE user_feedback SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE acceptance_tracking SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE failure_patterns SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE manual_trigger_log SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE ai_model_metrics SET project_id = default_project_id WHERE project_id IS NULL;
    UPDATE knowledge_doc_changes SET project_id = default_project_id WHERE project_id IS NULL;

    -- Update jira_bugs if exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jira_bugs') THEN
        EXECUTE 'UPDATE jira_bugs SET project_id = $1 WHERE project_id IS NULL' USING default_project_id;
    END IF;

    -- Create default configuration
    INSERT INTO project_configurations (
        project_id,
        jira_project_key,
        mongodb_collection_prefix,
        pinecone_namespace,
        confidence_threshold
    ) VALUES (
        default_project_id,
        'KAN',  -- Existing Jira project key
        'ddn_',
        'ddn_knowledge',
        0.70
    ) ON CONFLICT (project_id) DO NOTHING;

    -- Add all existing users to default project as developers
    INSERT INTO user_projects (user_id, project_id, role, joined_at)
    SELECT id, default_project_id, 'developer', CURRENT_TIMESTAMP
    FROM users
    ON CONFLICT (user_id, project_id) DO NOTHING;

    -- Make first admin user the project owner
    UPDATE user_projects
    SET role = 'project_owner'
    WHERE project_id = default_project_id
    AND user_id = (SELECT id FROM users WHERE role = 'admin' ORDER BY id LIMIT 1);
END $$;

-- ============================================
-- STEP 4: Make project_id NOT NULL (After Backfill)
-- ============================================

-- Now that all records have project_id, make it NOT NULL
ALTER TABLE failure_analysis ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE build_metadata ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE test_case_history ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE user_feedback ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE acceptance_tracking ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE failure_patterns ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE manual_trigger_log ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE ai_model_metrics ALTER COLUMN project_id SET NOT NULL;
ALTER TABLE knowledge_doc_changes ALTER COLUMN project_id SET NOT NULL;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'jira_bugs') THEN
        ALTER TABLE jira_bugs ALTER COLUMN project_id SET NOT NULL;
    END IF;
END $$;

-- ============================================
-- STEP 5: Create Helper Functions
-- ============================================

-- Function to check if user has access to project
CREATE OR REPLACE FUNCTION user_has_project_access(
    p_user_id INTEGER,
    p_project_id INTEGER
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM user_projects
        WHERE user_id = p_user_id AND project_id = p_project_id
    );
END;
$$ LANGUAGE plpgsql;

-- Function to get user's role in project
CREATE OR REPLACE FUNCTION get_user_project_role(
    p_user_id INTEGER,
    p_project_id INTEGER
) RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR(50);
BEGIN
    SELECT role INTO user_role
    FROM user_projects
    WHERE user_id = p_user_id AND project_id = p_project_id;

    RETURN COALESCE(user_role, 'none');
END;
$$ LANGUAGE plpgsql;

-- Function to log project activity
CREATE OR REPLACE FUNCTION log_project_activity(
    p_project_id INTEGER,
    p_user_id INTEGER,
    p_activity_type VARCHAR(50),
    p_entity_type VARCHAR(50),
    p_entity_id INTEGER,
    p_action VARCHAR(20),
    p_old_values JSONB DEFAULT NULL,
    p_new_values JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO project_activity_log (
        project_id, user_id, activity_type, entity_type, entity_id,
        action, old_values, new_values, created_at
    ) VALUES (
        p_project_id, p_user_id, p_activity_type, p_entity_type, p_entity_id,
        p_action, p_old_values, p_new_values, CURRENT_TIMESTAMP
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 6: Create Views for Multi-Project Analytics
-- ============================================

-- View: Project summary with stats
CREATE OR REPLACE VIEW v_project_summary AS
SELECT
    p.id,
    p.slug,
    p.name,
    p.status,
    p.created_at,
    COUNT(DISTINCT up.user_id) as team_size,
    COUNT(DISTINCT fa.id) as total_failures,
    COUNT(DISTINCT CASE WHEN fa.created_at > NOW() - INTERVAL '7 days' THEN fa.id END) as failures_7d,
    COUNT(DISTINCT CASE WHEN fa.created_at > NOW() - INTERVAL '30 days' THEN fa.id END) as failures_30d,
    COUNT(DISTINCT bm.build_id) as total_builds
FROM projects p
LEFT JOIN user_projects up ON p.id = up.project_id
LEFT JOIN failure_analysis fa ON p.id = fa.project_id
LEFT JOIN build_metadata bm ON p.id = bm.project_id
GROUP BY p.id, p.slug, p.name, p.status, p.created_at;

COMMENT ON VIEW v_project_summary IS 'Summary statistics for each project';

-- View: User's accessible projects
CREATE OR REPLACE VIEW v_user_projects AS
SELECT
    u.id as user_id,
    u.email,
    p.id as project_id,
    p.slug,
    p.name,
    up.role,
    up.permissions,
    up.joined_at,
    up.last_accessed_at
FROM users u
JOIN user_projects up ON u.id = up.user_id
JOIN projects p ON up.project_id = p.id
WHERE p.status = 'active';

COMMENT ON VIEW v_user_projects IS 'All active projects accessible to each user';

-- ============================================
-- STEP 7: Create Triggers for Audit Logging
-- ============================================

-- Trigger function to update last_accessed_at
CREATE OR REPLACE FUNCTION update_project_access_time()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE user_projects
    SET last_accessed_at = CURRENT_TIMESTAMP
    WHERE user_id = NEW.user_id AND project_id = NEW.project_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: Trigger will be attached to failure_analysis table
-- This trigger fires when user accesses failure data
CREATE TRIGGER trg_update_project_access_after_failure_read
AFTER SELECT ON failure_analysis
FOR EACH ROW
EXECUTE FUNCTION update_project_access_time();

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify migration success
DO $$
DECLARE
    table_count INTEGER;
    default_project_count INTEGER;
    user_project_count INTEGER;
BEGIN
    -- Check if all tables exist
    SELECT COUNT(*) INTO table_count
    FROM information_schema.tables
    WHERE table_name IN ('projects', 'user_projects', 'project_configurations', 'project_activity_log');

    IF table_count < 4 THEN
        RAISE EXCEPTION 'Migration failed: Not all tables created';
    END IF;

    -- Check if default project exists
    SELECT COUNT(*) INTO default_project_count FROM projects WHERE slug = 'ddn';
    IF default_project_count = 0 THEN
        RAISE EXCEPTION 'Migration failed: Default project not created';
    END IF;

    -- Check if users are assigned to project
    SELECT COUNT(*) INTO user_project_count FROM user_projects;
    IF user_project_count = 0 THEN
        RAISE WARNING 'Warning: No users assigned to projects';
    END IF;

    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'Created tables: %', table_count;
    RAISE NOTICE 'Default project created: %', default_project_count;
    RAISE NOTICE 'User-project assignments: %', user_project_count;
END $$;

-- ============================================
-- ROLLBACK SCRIPT (Save for emergency)
-- ============================================

-- To rollback this migration, run:
-- DROP TABLE IF EXISTS project_activity_log CASCADE;
-- DROP TABLE IF EXISTS project_configurations CASCADE;
-- DROP TABLE IF EXISTS user_projects CASCADE;
-- DROP TABLE IF EXISTS projects CASCADE;
-- DROP VIEW IF EXISTS v_project_summary CASCADE;
-- DROP VIEW IF EXISTS v_user_projects CASCADE;
-- DROP FUNCTION IF EXISTS user_has_project_access CASCADE;
-- DROP FUNCTION IF EXISTS get_user_project_role CASCADE;
-- DROP FUNCTION IF EXISTS log_project_activity CASCADE;
-- ALTER TABLE failure_analysis DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE build_metadata DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE test_case_history DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE user_feedback DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE acceptance_tracking DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE failure_patterns DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE manual_trigger_log DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE ai_model_metrics DROP COLUMN IF EXISTS project_id CASCADE;
-- ALTER TABLE knowledge_doc_changes DROP COLUMN IF EXISTS project_id CASCADE;

-- ============================================
-- END OF MIGRATION
-- ============================================
