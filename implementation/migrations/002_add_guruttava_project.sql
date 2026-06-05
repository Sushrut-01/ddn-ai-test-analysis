-- Migration: Add Guruttava Project to Multi-Project Architecture
-- Date: 2026-01-14
-- Description: Creates Guruttava project with complete configuration for Robot Framework automation

-- ============================================================================
-- STEP 1: Create Guruttava Project Record
-- ============================================================================

INSERT INTO projects (slug, name, description, status, created_by, created_at)
VALUES (
    'guruttava',
    'Guruttava',
    'Mobile (Android/iOS) and Web test automation using Robot Framework with Python. Supports Appium for mobile testing and Selenium for web testing.',
    'active',
    1,  -- Replace with actual admin user ID
    CURRENT_TIMESTAMP
)
ON CONFLICT (slug) DO NOTHING
RETURNING id;

-- Get the project ID for subsequent inserts
-- Note: If project already exists, you'll need to query: SELECT id FROM projects WHERE slug = 'guruttava';

-- ============================================================================
-- STEP 2: Configure Guruttava Project Settings
-- ============================================================================

-- IMPORTANT: Update these values with your actual Guruttava credentials:
-- - jira_url: Your Jira instance URL
-- - jira_email: Service account email
-- - jira_api_token_encrypted: Encrypted API token (use encryption function)
-- - github_repo_owner: GitHub organization or user
-- - github_repo_name: Repository name
-- - github_token_encrypted: Encrypted GitHub PAT (use encryption function)

INSERT INTO project_configurations (
    project_id,
    jira_project_key,
    jira_url,
    jira_email,
    jira_api_token_encrypted,
    github_repo_owner,
    github_repo_name,
    github_default_branch,
    github_token_encrypted,
    ci_provider,
    ci_webhook_url,
    mongodb_collection_prefix,
    pinecone_namespace,
    confidence_threshold,
    auto_create_jira_tickets,
    auto_assign_failures,
    notification_channels,
    ai_model_preferences,
    created_at,
    updated_at
) VALUES (
    (SELECT id FROM projects WHERE slug = 'guruttava'),  -- project_id
    'GURU',  -- jira_project_key (UPDATE THIS with your actual Jira project key)
    'https://your-org.atlassian.net',  -- jira_url (UPDATE THIS)
    'guruttava-bot@example.com',  -- jira_email (UPDATE THIS)
    NULL,  -- jira_api_token_encrypted (UPDATE THIS - use pgcrypto encrypt function)
    'Guruttava-Org',  -- github_repo_owner (UPDATE THIS)
    'guruttava-automation',  -- github_repo_name (UPDATE THIS)
    'main',  -- github_default_branch
    NULL,  -- github_token_encrypted (UPDATE THIS - use pgcrypto encrypt function)
    'jenkins',  -- ci_provider
    'http://host.docker.internal:5004/api/trigger-analysis',  -- ci_webhook_url (Python Workflow API)
    'guruttava_',  -- mongodb_collection_prefix
    'guruttava',  -- pinecone_namespace
    0.70,  -- confidence_threshold
    true,  -- auto_create_jira_tickets
    true,  -- auto_assign_failures
    '["email", "slack"]',  -- notification_channels (JSON array)
    '{"primary_model": "claude-sonnet-4", "fallback_model": "gpt-4o", "classification_model": "claude-sonnet-4"}',  -- ai_model_preferences
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (project_id) DO UPDATE SET
    jira_project_key = EXCLUDED.jira_project_key,
    mongodb_collection_prefix = EXCLUDED.mongodb_collection_prefix,
    pinecone_namespace = EXCLUDED.pinecone_namespace,
    updated_at = CURRENT_TIMESTAMP;

-- ============================================================================
-- STEP 3: Assign Users to Guruttava Project
-- ============================================================================

-- Assign admin user (user_id = 1) as project owner
INSERT INTO user_projects (user_id, project_id, role, permissions, joined_at)
VALUES (
    1,  -- Admin user (UPDATE THIS with actual user ID)
    (SELECT id FROM projects WHERE slug = 'guruttava'),
    'project_owner',
    '["*"]',  -- All permissions
    CURRENT_TIMESTAMP
)
ON CONFLICT (user_id, project_id) DO UPDATE SET
    role = EXCLUDED.role,
    permissions = EXCLUDED.permissions;

-- Assign additional developers (UPDATE THESE with actual user IDs)
-- Example: Assign user_id 8 as developer
INSERT INTO user_projects (user_id, project_id, role, permissions, joined_at)
VALUES (
    8,  -- Developer user (UPDATE THIS)
    (SELECT id FROM projects WHERE slug = 'guruttava'),
    'developer',
    '[]',  -- Default developer permissions (inherits from role)
    CURRENT_TIMESTAMP
)
ON CONFLICT (user_id, project_id) DO NOTHING;

-- Example: Assign user_id 5 as developer
INSERT INTO user_projects (user_id, project_id, role, permissions, joined_at)
VALUES (
    5,  -- Developer user (UPDATE THIS)
    (SELECT id FROM projects WHERE slug = 'guruttava'),
    'developer',
    '[]',
    CURRENT_TIMESTAMP
)
ON CONFLICT (user_id, project_id) DO NOTHING;

-- ============================================================================
-- STEP 4: Create Indexes for Performance (if not exist)
-- ============================================================================

-- Index on projects.slug for fast lookups
CREATE INDEX IF NOT EXISTS idx_projects_slug ON projects(slug);

-- Index on project_configurations.project_id
CREATE INDEX IF NOT EXISTS idx_project_configs_project_id ON project_configurations(project_id);

-- Index on user_projects for access control queries
CREATE INDEX IF NOT EXISTS idx_user_projects_user_id ON user_projects(user_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_project_id ON user_projects(project_id);
CREATE INDEX IF NOT EXISTS idx_user_projects_composite ON user_projects(user_id, project_id);

-- Index on failure_analysis.project_id for data isolation
CREATE INDEX IF NOT EXISTS idx_failure_analysis_project_id ON failure_analysis(project_id);
CREATE INDEX IF NOT EXISTS idx_failure_analysis_project_build ON failure_analysis(project_id, build_id);

-- Index on build_metadata.project_id
CREATE INDEX IF NOT EXISTS idx_build_metadata_project_id ON build_metadata(project_id);

-- Index on jira_bugs.project_id
CREATE INDEX IF NOT EXISTS idx_jira_bugs_project_id ON jira_bugs(project_id);

-- Index on workflow_executions.build_id for tracking
CREATE INDEX IF NOT EXISTS idx_workflow_executions_build_id ON workflow_executions(build_id);

-- ============================================================================
-- STEP 5: Verify Installation
-- ============================================================================

-- Check if Guruttava project was created
SELECT
    id,
    slug,
    name,
    description,
    status,
    created_at
FROM projects
WHERE slug = 'guruttava';

-- Check project configuration
SELECT
    pc.project_id,
    p.slug,
    pc.jira_project_key,
    pc.github_repo_owner,
    pc.github_repo_name,
    pc.mongodb_collection_prefix,
    pc.pinecone_namespace,
    pc.confidence_threshold,
    pc.ci_provider
FROM project_configurations pc
JOIN projects p ON pc.project_id = p.id
WHERE p.slug = 'guruttava';

-- Check user assignments
SELECT
    u.id AS user_id,
    u.email,
    up.role,
    p.name AS project_name,
    up.joined_at
FROM user_projects up
JOIN users u ON up.user_id = u.id
JOIN projects p ON up.project_id = p.id
WHERE p.slug = 'guruttava'
ORDER BY up.role, u.email;

-- ============================================================================
-- STEP 6: MongoDB Collection Setup Commands
-- ============================================================================

/*
Run these commands in MongoDB shell or via Python script:

use ddn_tests;

// Create Guruttava test failures collection
db.createCollection("guruttava_test_failures");
db.guruttava_test_failures.createIndex({ "build_id": 1 });
db.guruttava_test_failures.createIndex({ "test_name": 1 });
db.guruttava_test_failures.createIndex({ "timestamp": -1 });
db.guruttava_test_failures.createIndex({ "error_category": 1 });
db.guruttava_test_failures.createIndex({ "project_id": 1 });
db.guruttava_test_failures.createIndex({ "analyzed": 1 });

// Create Guruttava build results collection
db.createCollection("guruttava_build_results");
db.guruttava_build_results.createIndex({ "build_id": 1 }, { unique: true });
db.guruttava_build_results.createIndex({ "job_name": 1 });
db.guruttava_build_results.createIndex({ "timestamp": -1 });
db.guruttava_build_results.createIndex({ "status": 1 });
db.guruttava_build_results.createIndex({ "analyzed": 1 });
db.guruttava_build_results.createIndex({ "project_id": 1 });

// Create Guruttava failure analysis detailed collection
db.createCollection("guruttava_failure_analysis_detailed");
db.guruttava_failure_analysis_detailed.createIndex({ "analysis_id": 1 });
db.guruttava_failure_analysis_detailed.createIndex({ "project_id": 1 });
db.guruttava_failure_analysis_detailed.createIndex({ "timestamp": -1 });

// Verify collections
db.getCollectionNames().filter(name => name.startsWith('guruttava_'));
*/

-- ============================================================================
-- STEP 7: Post-Migration Validation Queries
-- ============================================================================

-- Verify data isolation: DDN and Guruttava should have separate records
SELECT
    p.slug AS project,
    COUNT(fa.id) AS failure_count
FROM projects p
LEFT JOIN failure_analysis fa ON p.id = fa.project_id
WHERE p.slug IN ('ddn', 'guruttava')
GROUP BY p.slug;

-- Verify user access control
SELECT
    u.email,
    STRING_AGG(p.slug || ' (' || up.role || ')', ', ') AS projects
FROM users u
JOIN user_projects up ON u.id = up.user_id
JOIN projects p ON up.project_id = p.id
GROUP BY u.id, u.email
ORDER BY u.email;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

/*
-- Uncomment to rollback the migration:

-- Delete user assignments
DELETE FROM user_projects WHERE project_id = (SELECT id FROM projects WHERE slug = 'guruttava');

-- Delete project configuration
DELETE FROM project_configurations WHERE project_id = (SELECT id FROM projects WHERE slug = 'guruttava');

-- Delete project
DELETE FROM projects WHERE slug = 'guruttava';

-- MongoDB cleanup (run in MongoDB shell):
use ddn_tests;
db.guruttava_test_failures.drop();
db.guruttava_build_results.drop();
db.guruttava_failure_analysis_detailed.drop();
*/

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================

-- Next Steps:
-- 1. Update the placeholders in this script with actual values:
--    - jira_url, jira_email, jira_api_token_encrypted
--    - github_repo_owner, github_repo_name, github_token_encrypted
--    - User IDs for project assignments
--
-- 2. Encrypt sensitive tokens using pgcrypto:
--    SELECT pgp_sym_encrypt('your-jira-token', 'encryption-key');
--    SELECT pgp_sym_encrypt('your-github-token', 'encryption-key');
--
-- 3. Run MongoDB collection creation commands
--
-- 4. Configure Jenkins jobs for Guruttava
--
-- 5. Update service code with project-aware endpoints
--
-- 6. Test end-to-end flow with a test failure

SELECT 'Guruttava project migration script ready. Please update placeholders with actual values before running.' AS status;
