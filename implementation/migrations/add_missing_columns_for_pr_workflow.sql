-- ============================================================================
-- CRITICAL MIGRATION: Add Missing Columns for PR Workflow Integration
-- Date: 2026-01-12
-- ============================================================================
--
-- PURPOSE:
-- Add missing columns to failure_analysis table that are required by:
-- 1. code_fix_automation.py (PR creation workflow)
-- 2. Analytics page (complete error data)
-- 3. PR Workflow page (fix history)
--
-- USAGE:
-- psql -U postgres -d ddn_ai_analysis -f migrations/add_missing_columns_for_pr_workflow.sql
--
-- Or from Python:
-- python -c "import psycopg2, os; from dotenv import load_dotenv; load_dotenv();
-- conn = psycopg2.connect(host='localhost', port=5432, database='ddn_ai_analysis',
-- user='postgres', password=os.getenv('POSTGRES_PASSWORD'));
-- cursor = conn.cursor(); cursor.execute(open('migrations/add_missing_columns_for_pr_workflow.sql').read());
-- conn.commit(); print('Migration complete')"
--
-- ============================================================================

\c ddn_ai_analysis;

-- ============================================================================
-- 1. ADD MISSING COLUMNS TO failure_analysis TABLE
-- ============================================================================

-- Add error_type (e.g., "NullPointerException", "FileNotFoundException")
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS error_type VARCHAR(255);

-- Add error_message (full error message text)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add component (affected component/service name)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS component VARCHAR(255);

-- Add file_path (path to file where error occurred)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS file_path VARCHAR(500);

-- Add line_number (line number where error occurred)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS line_number INTEGER;

-- Add stack_trace (full stack trace)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS stack_trace TEXT;

-- Add severity (LOW, MEDIUM, HIGH, CRITICAL)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'MEDIUM';

-- Add classification (replaces error_category for consistency)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS classification VARCHAR(50);

-- Update mongodb_failure_id if missing (links to MongoDB test_failures collection)
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS mongodb_failure_id VARCHAR(255);

-- ============================================================================
-- 2. ADD MISSING COLUMNS TO code_fix_applications TABLE
-- ============================================================================

-- Add job_name for tracking which CI/CD job the fix is for
ALTER TABLE code_fix_applications
ADD COLUMN IF NOT EXISTS job_name VARCHAR(255);

-- Add file_path for quick reference
ALTER TABLE code_fix_applications
ADD COLUMN IF NOT EXISTS file_path VARCHAR(500);

-- Add fix_type for categorization
ALTER TABLE code_fix_applications
ADD COLUMN IF NOT EXISTS fix_type VARCHAR(100);

-- ============================================================================
-- 3. CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index on error_type for faster filtering
CREATE INDEX IF NOT EXISTS idx_failure_analysis_error_type
    ON failure_analysis(error_type);

-- Index on component for component-level analytics
CREATE INDEX IF NOT EXISTS idx_failure_analysis_component
    ON failure_analysis(component);

-- Index on file_path for file-level analysis
CREATE INDEX IF NOT EXISTS idx_failure_analysis_file_path
    ON failure_analysis(file_path);

-- Index on severity for priority filtering
CREATE INDEX IF NOT EXISTS idx_failure_analysis_severity
    ON failure_analysis(severity);

-- Index on classification (replaces error_category)
CREATE INDEX IF NOT EXISTS idx_failure_analysis_classification
    ON failure_analysis(classification);

-- Index on job_name in code_fix_applications
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_job_name
    ON code_fix_applications(job_name);

-- Index on file_path in code_fix_applications
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_file_path
    ON code_fix_applications(file_path);

-- Index on fix_type in code_fix_applications
CREATE INDEX IF NOT EXISTS idx_code_fix_applications_fix_type
    ON code_fix_applications(fix_type);

-- ============================================================================
-- 4. UPDATE EXISTING DATA BEFORE ADDING CONSTRAINTS
-- ============================================================================

-- Set default severity for existing NULL or invalid values
UPDATE failure_analysis
SET severity = 'MEDIUM'
WHERE severity IS NULL
   OR severity NOT IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

-- ============================================================================
-- 5. ADD CONSTRAINTS
-- ============================================================================

-- Add check constraint for severity
ALTER TABLE failure_analysis
DROP CONSTRAINT IF EXISTS check_severity;

ALTER TABLE failure_analysis
ADD CONSTRAINT check_severity CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL'));

-- ============================================================================
-- 6. ADD COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON COLUMN failure_analysis.error_type IS 'Specific error type (e.g., NullPointerException, FileNotFoundException)';
COMMENT ON COLUMN failure_analysis.error_message IS 'Full error message text from failure';
COMMENT ON COLUMN failure_analysis.component IS 'Component or service name where error occurred';
COMMENT ON COLUMN failure_analysis.file_path IS 'Path to source file where error occurred';
COMMENT ON COLUMN failure_analysis.line_number IS 'Line number in source file where error occurred';
COMMENT ON COLUMN failure_analysis.stack_trace IS 'Full stack trace from error';
COMMENT ON COLUMN failure_analysis.severity IS 'Error severity: LOW, MEDIUM, HIGH, CRITICAL';
COMMENT ON COLUMN failure_analysis.classification IS 'Error classification for analytics (replaces error_category)';
COMMENT ON COLUMN failure_analysis.mongodb_failure_id IS 'Reference to MongoDB test_failures collection _id';

COMMENT ON COLUMN code_fix_applications.job_name IS 'CI/CD job name that triggered this fix';
COMMENT ON COLUMN code_fix_applications.file_path IS 'Path to file being fixed';
COMMENT ON COLUMN code_fix_applications.fix_type IS 'Type of fix applied (e.g., code_fix, config_fix)';

-- ============================================================================
-- 7. MIGRATE EXISTING DATA (if error_category exists)
-- ============================================================================

-- Copy error_category to classification if it exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'failure_analysis'
        AND column_name = 'error_category'
    ) THEN
        UPDATE failure_analysis
        SET classification = error_category
        WHERE classification IS NULL AND error_category IS NOT NULL;
    END IF;
END $$;

-- ============================================================================
-- 8. VERIFICATION QUERIES
-- ============================================================================

-- Verify columns were added to failure_analysis
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'failure_analysis'
AND column_name IN ('error_type', 'error_message', 'component', 'file_path',
                    'line_number', 'stack_trace', 'severity', 'classification', 'mongodb_failure_id')
ORDER BY column_name;

-- Verify columns were added to code_fix_applications
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'code_fix_applications'
AND column_name IN ('job_name', 'file_path', 'fix_type')
ORDER BY column_name;

-- Show indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('failure_analysis', 'code_fix_applications')
AND indexname LIKE '%error_type%'
   OR indexname LIKE '%component%'
   OR indexname LIKE '%file_path%'
   OR indexname LIKE '%severity%'
   OR indexname LIKE '%classification%'
   OR indexname LIKE '%job_name%'
   OR indexname LIKE '%fix_type%'
ORDER BY tablename, indexname;

-- Count existing records
SELECT
    'failure_analysis' as table_name,
    COUNT(*) as total_records,
    COUNT(error_type) as with_error_type,
    COUNT(classification) as with_classification
FROM failure_analysis
UNION ALL
SELECT
    'code_fix_applications' as table_name,
    COUNT(*) as total_records,
    COUNT(job_name) as with_job_name,
    COUNT(file_path) as with_file_path
FROM code_fix_applications;

-- ============================================================================
-- 9. SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
    RAISE NOTICE 'MIGRATION COMPLETED SUCCESSFULLY';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Added columns to failure_analysis:';
    RAISE NOTICE '  - error_type';
    RAISE NOTICE '  - error_message';
    RAISE NOTICE '  - component';
    RAISE NOTICE '  - file_path';
    RAISE NOTICE '  - line_number';
    RAISE NOTICE '  - stack_trace';
    RAISE NOTICE '  - severity';
    RAISE NOTICE '  - classification';
    RAISE NOTICE '  - mongodb_failure_id';
    RAISE NOTICE '';
    RAISE NOTICE 'Added columns to code_fix_applications:';
    RAISE NOTICE '  - job_name';
    RAISE NOTICE '  - file_path';
    RAISE NOTICE '  - fix_type';
    RAISE NOTICE '';
    RAISE NOTICE 'Created indexes for performance optimization';
    RAISE NOTICE 'Added constraints for data validation';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Update AI analysis service to populate these columns';
    RAISE NOTICE '  2. Run code_fix_automation.py to test PR creation';
    RAISE NOTICE '  3. Verify Analytics page displays data correctly';
    RAISE NOTICE '  4. Verify PR Workflow page shows fix history';
    RAISE NOTICE '';
    RAISE NOTICE '============================================================';
END $$;

-- ============================================================================
-- ROLLBACK INSTRUCTIONS (if needed)
-- ============================================================================
/*
-- To rollback this migration:

ALTER TABLE failure_analysis DROP COLUMN IF EXISTS error_type CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS error_message CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS component CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS file_path CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS line_number CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS stack_trace CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS severity CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS classification CASCADE;
ALTER TABLE failure_analysis DROP COLUMN IF EXISTS mongodb_failure_id CASCADE;

ALTER TABLE code_fix_applications DROP COLUMN IF EXISTS job_name CASCADE;
ALTER TABLE code_fix_applications DROP COLUMN IF EXISTS file_path CASCADE;
ALTER TABLE code_fix_applications DROP COLUMN IF EXISTS fix_type CASCADE;

DROP INDEX IF EXISTS idx_failure_analysis_error_type;
DROP INDEX IF EXISTS idx_failure_analysis_component;
DROP INDEX IF EXISTS idx_failure_analysis_file_path;
DROP INDEX IF EXISTS idx_failure_analysis_severity;
DROP INDEX IF EXISTS idx_failure_analysis_classification;
DROP INDEX IF EXISTS idx_code_fix_applications_job_name;
DROP INDEX IF EXISTS idx_code_fix_applications_file_path;
DROP INDEX IF EXISTS idx_code_fix_applications_fix_type;
*/

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
