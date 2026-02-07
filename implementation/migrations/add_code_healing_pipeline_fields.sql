-- ============================================================================
-- Code Healing Pipeline Migration
-- Date: 2026-01-12
-- ============================================================================
--
-- PURPOSE:
-- Add fields to failure_analysis table to support Code Healing Pipeline:
-- AI Analysis → Human Approval → PR Created → Build Running → Build Passed → Jira Created
--
-- USAGE:
-- psql -U postgres -d ddn_ai_analysis -f migrations/add_code_healing_pipeline_fields.sql
--
-- ============================================================================

-- ============================================================================
-- 1. ADD HEALING PIPELINE FIELDS TO failure_analysis
-- ============================================================================

-- Healing stage tracking
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS healing_stage VARCHAR(50) DEFAULT 'ai_analysis';

-- Human approval tracking
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS ai_approved BOOLEAN DEFAULT FALSE;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS approved_by VARCHAR(255);

-- PR tracking
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS pr_number INTEGER;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS pr_url TEXT;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS pr_created_at TIMESTAMP;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS pr_status VARCHAR(50);

-- Build tracking
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS build_status VARCHAR(50) DEFAULT 'pending';

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS build_url TEXT;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS build_started_at TIMESTAMP;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS build_completed_at TIMESTAMP;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS build_result TEXT;

-- Jira tracking
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS jira_key VARCHAR(50);

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS jira_url TEXT;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS jira_created_at TIMESTAMP;

ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS jira_created_by VARCHAR(255);

-- ============================================================================
-- 2. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_failure_analysis_healing_stage
    ON failure_analysis(healing_stage);

CREATE INDEX IF NOT EXISTS idx_failure_analysis_ai_approved
    ON failure_analysis(ai_approved);

CREATE INDEX IF NOT EXISTS idx_failure_analysis_pr_number
    ON failure_analysis(pr_number);

CREATE INDEX IF NOT EXISTS idx_failure_analysis_build_status
    ON failure_analysis(build_status);

CREATE INDEX IF NOT EXISTS idx_failure_analysis_jira_key
    ON failure_analysis(jira_key);

-- Composite index for querying CODE_ERROR items in healing pipeline
CREATE INDEX IF NOT EXISTS idx_failure_analysis_healing_pipeline
    ON failure_analysis(classification, healing_stage, ai_approved)
    WHERE classification = 'CODE_ERROR';

-- ============================================================================
-- 3. ADD CONSTRAINTS
-- ============================================================================

-- Healing stage constraint
ALTER TABLE failure_analysis
DROP CONSTRAINT IF EXISTS check_healing_stage;

ALTER TABLE failure_analysis
ADD CONSTRAINT check_healing_stage CHECK (
    healing_stage IN (
        'ai_analysis',
        'human_approval',
        'pr_created',
        'build_running',
        'build_passed',
        'build_failed',
        'jira_created',
        'completed',
        'rejected'
    )
);

-- Build status constraint
ALTER TABLE failure_analysis
DROP CONSTRAINT IF EXISTS check_build_status;

ALTER TABLE failure_analysis
ADD CONSTRAINT check_build_status CHECK (
    build_status IN ('pending', 'running', 'passed', 'failed', 'skipped')
);

-- PR status constraint
ALTER TABLE failure_analysis
DROP CONSTRAINT IF EXISTS check_pr_status;

ALTER TABLE failure_analysis
ADD CONSTRAINT check_pr_status CHECK (
    pr_status IN ('open', 'merged', 'closed', 'draft')
);

-- ============================================================================
-- 4. UPDATE EXISTING DATA
-- ============================================================================

-- Set healing stage for existing CODE_ERROR items
UPDATE failure_analysis
SET healing_stage = CASE
    -- If has Jira key, it's at final stage
    WHEN jira_key IS NOT NULL THEN 'jira_created'
    -- If has PR and build passed
    WHEN pr_number IS NOT NULL AND build_status = 'passed' THEN 'build_passed'
    -- If has PR and build running
    WHEN pr_number IS NOT NULL AND build_status = 'running' THEN 'build_running'
    -- If has PR created
    WHEN pr_number IS NOT NULL THEN 'pr_created'
    -- If AI approved but no PR
    WHEN ai_approved = TRUE THEN 'pr_created'
    -- Default: awaiting human approval
    ELSE 'human_approval'
END
WHERE classification = 'CODE_ERROR'
  AND healing_stage = 'ai_analysis';

-- ============================================================================
-- 5. CREATE HELPER VIEW FOR CODE HEALING DASHBOARD
-- ============================================================================

CREATE OR REPLACE VIEW code_healing_pipeline AS
SELECT
    fa.id,
    fa.build_id,
    fa.job_name,
    fa.test_name,
    fa.error_type,
    fa.error_message,
    fa.root_cause,
    fa.fix_recommendation,
    fa.file_path,
    fa.line_number,
    fa.classification,
    fa.confidence_score,
    fa.healing_stage,
    fa.ai_approved,
    fa.approved_at,
    fa.approved_by,
    fa.pr_number,
    fa.pr_url,
    fa.pr_created_at,
    fa.pr_status,
    fa.build_status,
    fa.build_url,
    fa.build_started_at,
    fa.build_completed_at,
    fa.jira_key,
    fa.jira_url,
    fa.jira_created_at,
    fa.created_at,
    fa.updated_at,
    -- Calculate time in each stage
    EXTRACT(EPOCH FROM (
        COALESCE(fa.approved_at, NOW()) - fa.created_at
    ))::INTEGER AS ai_analysis_duration_seconds,
    EXTRACT(EPOCH FROM (
        COALESCE(fa.pr_created_at, NOW()) - COALESCE(fa.approved_at, fa.created_at)
    ))::INTEGER AS approval_duration_seconds,
    EXTRACT(EPOCH FROM (
        COALESCE(fa.build_completed_at, NOW()) - COALESCE(fa.pr_created_at, fa.approved_at, fa.created_at)
    ))::INTEGER AS build_duration_seconds,
    -- Overall pipeline duration
    EXTRACT(EPOCH FROM (
        COALESCE(fa.jira_created_at, NOW()) - fa.created_at
    ))::INTEGER AS total_pipeline_duration_seconds
FROM
    failure_analysis fa
WHERE
    fa.classification = 'CODE_ERROR'
ORDER BY
    fa.created_at DESC;

-- ============================================================================
-- 6. ADD COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON COLUMN failure_analysis.healing_stage IS 'Current stage in code healing pipeline: ai_analysis, human_approval, pr_created, build_running, build_passed, jira_created';
COMMENT ON COLUMN failure_analysis.ai_approved IS 'Whether AI-suggested fix has been approved by human';
COMMENT ON COLUMN failure_analysis.approved_at IS 'Timestamp when fix was approved';
COMMENT ON COLUMN failure_analysis.approved_by IS 'User who approved the fix';
COMMENT ON COLUMN failure_analysis.pr_number IS 'GitHub Pull Request number for the fix';
COMMENT ON COLUMN failure_analysis.pr_url IS 'Full URL to GitHub Pull Request';
COMMENT ON COLUMN failure_analysis.pr_created_at IS 'Timestamp when PR was created';
COMMENT ON COLUMN failure_analysis.pr_status IS 'PR status: open, merged, closed, draft';
COMMENT ON COLUMN failure_analysis.build_status IS 'Build verification status: pending, running, passed, failed';
COMMENT ON COLUMN failure_analysis.build_url IS 'URL to build/CI job';
COMMENT ON COLUMN failure_analysis.build_started_at IS 'Timestamp when build started';
COMMENT ON COLUMN failure_analysis.build_completed_at IS 'Timestamp when build completed';
COMMENT ON COLUMN failure_analysis.build_result IS 'Build result details (logs, errors)';
COMMENT ON COLUMN failure_analysis.jira_key IS 'Jira ticket key (e.g., PROJ-123)';
COMMENT ON COLUMN failure_analysis.jira_url IS 'Full URL to Jira ticket';
COMMENT ON COLUMN failure_analysis.jira_created_at IS 'Timestamp when Jira ticket was created';
COMMENT ON COLUMN failure_analysis.jira_created_by IS 'User who created Jira ticket';

COMMENT ON VIEW code_healing_pipeline IS 'View showing CODE_ERROR items in healing pipeline with stage durations';

-- ============================================================================
-- 7. CREATE FUNCTION TO UPDATE HEALING STAGE AUTOMATICALLY
-- ============================================================================

CREATE OR REPLACE FUNCTION update_healing_stage()
RETURNS TRIGGER AS $$
BEGIN
    -- Only process CODE_ERROR items
    IF NEW.classification != 'CODE_ERROR' THEN
        RETURN NEW;
    END IF;

    -- Auto-update healing stage based on data changes
    IF NEW.jira_key IS NOT NULL AND OLD.jira_key IS NULL THEN
        NEW.healing_stage := 'jira_created';
    ELSIF NEW.build_status = 'passed' AND OLD.build_status != 'passed' THEN
        NEW.healing_stage := 'build_passed';
    ELSIF NEW.build_status = 'failed' AND OLD.build_status != 'failed' THEN
        NEW.healing_stage := 'build_failed';
    ELSIF NEW.build_status = 'running' AND OLD.build_status != 'running' THEN
        NEW.healing_stage := 'build_running';
    ELSIF NEW.pr_number IS NOT NULL AND OLD.pr_number IS NULL THEN
        NEW.healing_stage := 'pr_created';
    ELSIF NEW.ai_approved = TRUE AND OLD.ai_approved = FALSE THEN
        NEW.healing_stage := 'pr_created';
        NEW.approved_at := NOW();
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
DROP TRIGGER IF EXISTS trigger_update_healing_stage ON failure_analysis;
CREATE TRIGGER trigger_update_healing_stage
    BEFORE UPDATE ON failure_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_healing_stage();

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================

-- Check columns were added
SELECT
    column_name,
    data_type,
    column_default,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'failure_analysis'
AND column_name IN (
    'healing_stage', 'ai_approved', 'approved_at', 'approved_by',
    'pr_number', 'pr_url', 'pr_created_at', 'pr_status',
    'build_status', 'build_url', 'build_started_at', 'build_completed_at',
    'jira_key', 'jira_url', 'jira_created_at', 'jira_created_by'
)
ORDER BY column_name;

-- Check indexes
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'failure_analysis'
AND indexname LIKE '%healing%'
   OR indexname LIKE '%pr_%'
   OR indexname LIKE '%build_%'
   OR indexname LIKE '%jira_%'
ORDER BY indexname;

-- Check view
SELECT COUNT(*) as code_error_items
FROM code_healing_pipeline;

-- Show healing stage distribution
SELECT
    healing_stage,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE ai_approved = TRUE) as approved_count,
    COUNT(*) FILTER (WHERE pr_number IS NOT NULL) as with_pr,
    COUNT(*) FILTER (WHERE jira_key IS NOT NULL) as with_jira
FROM failure_analysis
WHERE classification = 'CODE_ERROR'
GROUP BY healing_stage
ORDER BY healing_stage;

-- ============================================================================
-- 9. SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'CODE HEALING PIPELINE MIGRATION COMPLETED';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Added columns:';
    RAISE NOTICE '  - healing_stage (tracks pipeline progress)';
    RAISE NOTICE '  - ai_approved, approved_at, approved_by';
    RAISE NOTICE '  - pr_number, pr_url, pr_created_at, pr_status';
    RAISE NOTICE '  - build_status, build_url, build_started_at, build_completed_at';
    RAISE NOTICE '  - jira_key, jira_url, jira_created_at, jira_created_by';
    RAISE NOTICE '';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - 6 indexes for performance';
    RAISE NOTICE '  - code_healing_pipeline view';
    RAISE NOTICE '  - Auto-update trigger for healing stages';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Update code_fix_automation.py to set PR fields';
    RAISE NOTICE '  2. Add build status webhook handler';
    RAISE NOTICE '  3. Test Jira integration';
    RAISE NOTICE '  4. Access Code Healing page at /code-healing';
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
END $$;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ============================================================================
/*
-- To rollback this migration:

DROP TRIGGER IF EXISTS trigger_update_healing_stage ON failure_analysis;
DROP FUNCTION IF EXISTS update_healing_stage();
DROP VIEW IF EXISTS code_healing_pipeline;

ALTER TABLE failure_analysis DROP COLUMN IF EXISTS healing_stage CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS ai_approved CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS approved_at CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS approved_by CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS pr_number CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS pr_url CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS pr_created_at CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS pr_status CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS build_status CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS build_url CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS build_started_at CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS build_completed_at CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS build_result CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS jira_key CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS jira_url CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS jira_created_at CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS jira_created_by CASCADE;

DROP INDEX IF EXISTS idx_failure_analysis_healing_stage;
DROP INDEX IF EXISTS idx_failure_analysis_ai_approved;
DROP INDEX IF EXISTS idx_failure_analysis_pr_number;
DROP INDEX IF EXISTS idx_failure_analysis_build_status;
DROP INDEX IF EXISTS idx_failure_analysis_jira_key;
DROP INDEX IF EXISTS idx_failure_analysis_healing_pipeline;
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
