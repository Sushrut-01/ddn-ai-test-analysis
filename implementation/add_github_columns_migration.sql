-- ===================================================================
-- Migration: Add GitHub Integration Columns (Task 0E.6)
-- ===================================================================
-- This migration adds columns to store GitHub source code information
-- for CODE_ERROR category failures
-- ===================================================================

\c ddn_ai_analysis;

-- Add github_files column (JSONB for structured storage)
-- Stores array of file objects with: file_path, content, line_range, etc.
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS github_files JSONB DEFAULT '[]'::jsonb;

-- Add github_code_included flag
-- Quick boolean check if GitHub code was fetched for this failure
ALTER TABLE failure_analysis
ADD COLUMN IF NOT EXISTS github_code_included BOOLEAN DEFAULT FALSE;

-- Add index for quick filtering of failures with GitHub code
CREATE INDEX IF NOT EXISTS idx_failure_analysis_github_code
ON failure_analysis(github_code_included)
WHERE github_code_included = TRUE;

-- Add comment for documentation
COMMENT ON COLUMN failure_analysis.github_files IS
'JSON array of GitHub source code files fetched for CODE_ERROR analysis. Each file contains: file_path, content (50 lines max), total_lines, line_range, sha, url, repo, branch';

COMMENT ON COLUMN failure_analysis.github_code_included IS
'Boolean flag indicating if GitHub source code was successfully fetched and included in analysis (CODE_ERROR category only)';

-- ===================================================================
-- Verification
-- ===================================================================

-- Check column was added
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'failure_analysis'
AND column_name IN ('github_files', 'github_code_included')
ORDER BY column_name;

-- Check index was created
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'failure_analysis'
AND indexname = 'idx_failure_analysis_github_code';

-- Sample query to test
SELECT
    id,
    mongodb_failure_id,
    classification,
    github_code_included,
    jsonb_array_length(github_files) as github_files_count
FROM failure_analysis
LIMIT 5;

-- ===================================================================
-- END OF MIGRATION
-- ===================================================================
