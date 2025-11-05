-- ============================================================================
-- PHASE B: Automated Code Fixing - Database Migration
-- Task B.9: Add fix success tracking
-- Created: 2025-11-03
-- ============================================================================
--
-- PURPOSE:
-- Track all automated code fix applications, PR creation, and rollbacks
-- Provides audit trail and success rate analytics for Phase B
--
-- USAGE:
-- psql -U postgres -d ddn_ai_analysis -f add_code_fix_applications_table.sql
--
-- Or from Python:
-- python -c "import psycopg2, os; from dotenv import load_dotenv; load_dotenv();
-- conn = psycopg2.connect(host='localhost', port=5432, database='ddn_ai_analysis',
-- user='postgres', password=os.getenv('POSTGRES_PASSWORD'));
-- cursor = conn.cursor(); cursor.execute(open('migrations/add_code_fix_applications_table.sql').read());
-- conn.commit(); print('Migration complete')"
--
-- ============================================================================

-- Create code_fix_applications table
CREATE TABLE IF NOT EXISTS code_fix_applications (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Link to AI analysis
    analysis_id INTEGER NOT NULL,
    build_id VARCHAR(255) NOT NULL,

    -- Approval tracking
    approved_by_name VARCHAR(100),
    approved_by_email VARCHAR(255),
    approved_at TIMESTAMP,

    -- GitHub branch details
    branch_name VARCHAR(255),
    base_branch VARCHAR(100) DEFAULT 'main',

    -- GitHub PR details
    pr_number INTEGER,
    pr_url VARCHAR(500),
    pr_title TEXT,
    pr_body TEXT,
    pr_state VARCHAR(50) DEFAULT 'open', -- open, closed, merged

    -- Fix application status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    -- Status values:
    --   pending: Fix approved, PR being created
    --   pr_created: PR created successfully
    --   tests_running: CI tests in progress
    --   tests_passed: CI tests passed
    --   tests_failed: CI tests failed (may trigger rollback)
    --   merged: PR merged successfully
    --   reverted: Fix rolled back
    --   failed: PR creation or application failed

    CONSTRAINT valid_status CHECK (status IN (
        'pending', 'pr_created', 'tests_running', 'tests_passed',
        'tests_failed', 'merged', 'reverted', 'failed'
    )),

    -- Files changed
    files_changed JSONB,
    -- Format: [
    --   {
    --     "file_path": "src/main/java/DDNStorage.java",
    --     "lines_changed": 5,
    --     "lines_added": 3,
    --     "lines_removed": 2,
    --     "diff": "unified diff content"
    --   }
    -- ]

    -- Test results from CI
    test_results JSONB,
    -- Format: {
    --   "passed": 150,
    --   "failed": 2,
    --   "skipped": 5,
    --   "duration_ms": 45000,
    --   "coverage_percent": 85.5,
    --   "ci_url": "https://ci-server/build/12345"
    -- }

    -- Rollback information
    rollback_reason TEXT,
    rollback_at TIMESTAMP,
    rollback_by VARCHAR(100),
    rollback_type VARCHAR(50), -- auto, manual, ci_failure

    -- GitHub reviewers
    reviewers JSONB,
    -- Format: ["username1", "username2"]

    -- Labels applied to PR
    labels JSONB,
    -- Format: ["automated-fix", "ai-generated", "needs-review"]

    -- Performance metrics
    time_to_pr_creation_ms INTEGER, -- Time from approval to PR creation
    time_to_tests_complete_ms INTEGER, -- Time from PR creation to test completion
    time_to_merge_ms INTEGER, -- Time from PR creation to merge

    -- Error category (for analytics)
    error_category VARCHAR(100),
    error_type VARCHAR(255),
    error_severity VARCHAR(50),

    -- AI confidence (for correlation analysis)
    ai_confidence_score DECIMAL(5,4), -- 0.0000 to 1.0000

    -- Success indicator (derived from status)
    success BOOLEAN,
    -- TRUE if status = 'merged'
    -- FALSE if status = 'failed', 'reverted', 'tests_failed'
    -- NULL if status = 'pending', 'pr_created', 'tests_running', 'tests_passed'

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key constraint (optional - depends on your schema)
    -- CONSTRAINT fk_analysis FOREIGN KEY (analysis_id)
    --     REFERENCES failure_analysis(id) ON DELETE CASCADE

    -- Add comment
    COMMENT ON COLUMN code_fix_applications.status IS 'Fix application status: pending, pr_created, tests_running, tests_passed, tests_failed, merged, reverted, failed'
);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index on analysis_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_analysis_id
    ON code_fix_applications(analysis_id);

-- Index on build_id for correlating with test runs
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_build_id
    ON code_fix_applications(build_id);

-- Index on status for filtering by fix state
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_status
    ON code_fix_applications(status);

-- Index on PR number for GitHub webhook lookups
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_pr_number
    ON code_fix_applications(pr_number) WHERE pr_number IS NOT NULL;

-- Index on approved_at for time-based analytics
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_approved_at
    ON code_fix_applications(approved_at DESC);

-- Index on success for success rate analytics
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_success
    ON code_fix_applications(success) WHERE success IS NOT NULL;

-- Index on error_category for category-based analytics
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_error_category
    ON code_fix_applications(error_category);

-- Index on created_at for time-series queries
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_created_at
    ON code_fix_applications(created_at DESC);

-- Partial index on active fixes (not completed/failed)
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_active
    ON code_fix_applications(id, status, created_at)
    WHERE status IN ('pending', 'pr_created', 'tests_running');

-- GIN index on files_changed JSONB for searching by file path
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_files_changed
    ON code_fix_applications USING GIN (files_changed);

-- ============================================================================
-- CREATE TRIGGER FOR AUTOMATIC updated_at
-- ============================================================================

-- Create trigger function if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_proc
        WHERE proname = 'update_updated_at_column'
    ) THEN
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $trigger$ LANGUAGE plpgsql;
    END IF;
END $$;

-- Create trigger
DROP TRIGGER IF EXISTS update_code_fix_applications_updated_at
    ON code_fix_applications;

CREATE TRIGGER update_code_fix_applications_updated_at
    BEFORE UPDATE ON code_fix_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- CREATE TRIGGER FOR AUTOMATIC success FIELD
-- ============================================================================

-- Create trigger function to auto-set success field based on status
CREATE OR REPLACE FUNCTION update_code_fix_success_field()
RETURNS TRIGGER AS $trigger$
BEGIN
    -- Set success based on status
    IF NEW.status = 'merged' THEN
        NEW.success = TRUE;
    ELSIF NEW.status IN ('failed', 'reverted', 'tests_failed') THEN
        NEW.success = FALSE;
    ELSE
        NEW.success = NULL;
    END IF;

    RETURN NEW;
END;
$trigger$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS update_code_fix_applications_success
    ON code_fix_applications;

CREATE TRIGGER update_code_fix_applications_success
    BEFORE INSERT OR UPDATE OF status ON code_fix_applications
    FOR EACH ROW
    EXECUTE FUNCTION update_code_fix_success_field();

-- ============================================================================
-- ADD TABLE COMMENTS
-- ============================================================================

COMMENT ON TABLE code_fix_applications IS 'Tracks automated code fix applications, PR creation, and rollbacks for Phase B';

COMMENT ON COLUMN code_fix_applications.analysis_id IS 'Reference to failure_analysis.id';
COMMENT ON COLUMN code_fix_applications.build_id IS 'Jenkins/CI build identifier';
COMMENT ON COLUMN code_fix_applications.files_changed IS 'JSONB array of files modified with diffs';
COMMENT ON COLUMN code_fix_applications.test_results IS 'JSONB object with CI test results';
COMMENT ON COLUMN code_fix_applications.reviewers IS 'JSONB array of GitHub reviewer usernames';
COMMENT ON COLUMN code_fix_applications.labels IS 'JSONB array of PR labels';
COMMENT ON COLUMN code_fix_applications.success IS 'Derived from status: TRUE=merged, FALSE=failed/reverted, NULL=in-progress';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table was created
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'code_fix_applications'
    ) THEN
        RAISE NOTICE '✓ Table code_fix_applications created successfully';
    ELSE
        RAISE EXCEPTION '✗ Table creation failed';
    END IF;
END $$;

-- Show table structure
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'code_fix_applications'
ORDER BY ordinal_position;

-- Show indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'code_fix_applications'
ORDER BY indexname;

-- ============================================================================
-- SAMPLE QUERIES (For Reference)
-- ============================================================================

-- Get fix success rate by category
/*
SELECT
    error_category,
    COUNT(*) as total_fixes,
    COUNT(*) FILTER (WHERE success = TRUE) as successful,
    COUNT(*) FILTER (WHERE success = FALSE) as failed,
    ROUND(100.0 * COUNT(*) FILTER (WHERE success = TRUE) / COUNT(*), 2) as success_rate_percent
FROM code_fix_applications
WHERE success IS NOT NULL
GROUP BY error_category
ORDER BY total_fixes DESC;
*/

-- Get average time to merge by category
/*
SELECT
    error_category,
    COUNT(*) as merged_count,
    ROUND(AVG(time_to_merge_ms) / 1000.0, 2) as avg_time_to_merge_seconds,
    ROUND(MIN(time_to_merge_ms) / 1000.0, 2) as min_time_seconds,
    ROUND(MAX(time_to_merge_ms) / 1000.0, 2) as max_time_seconds
FROM code_fix_applications
WHERE status = 'merged' AND time_to_merge_ms IS NOT NULL
GROUP BY error_category
ORDER BY merged_count DESC;
*/

-- Get recent fix applications
/*
SELECT
    id,
    build_id,
    status,
    pr_number,
    pr_url,
    error_category,
    approved_by_name,
    approved_at,
    time_to_pr_creation_ms
FROM code_fix_applications
ORDER BY created_at DESC
LIMIT 10;
*/

-- Get rollback statistics
/*
SELECT
    COUNT(*) as total_rollbacks,
    rollback_type,
    COUNT(*) FILTER (WHERE rollback_type = 'auto') as auto_rollbacks,
    COUNT(*) FILTER (WHERE rollback_type = 'manual') as manual_rollbacks,
    COUNT(*) FILTER (WHERE rollback_type = 'ci_failure') as ci_failure_rollbacks
FROM code_fix_applications
WHERE status = 'reverted'
GROUP BY rollback_type;
*/

-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
/*
-- To rollback this migration:
DROP TRIGGER IF EXISTS update_code_fix_applications_success ON code_fix_applications;
DROP TRIGGER IF EXISTS update_code_fix_applications_updated_at ON code_fix_applications;
DROP FUNCTION IF EXISTS update_code_fix_success_field();
DROP TABLE IF EXISTS code_fix_applications CASCADE;

-- Note: The update_updated_at_column() function is shared with other tables,
-- so we don't drop it here.
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

RAISE NOTICE '';
RAISE NOTICE '============================================================';
RAISE NOTICE 'MIGRATION COMPLETE: code_fix_applications table created';
RAISE NOTICE '============================================================';
RAISE NOTICE 'Table: code_fix_applications';
RAISE NOTICE 'Indexes: 10 indexes created';
RAISE NOTICE 'Triggers: 2 triggers created';
RAISE NOTICE '';
RAISE NOTICE 'You can now track automated code fix applications!';
RAISE NOTICE '============================================================';
