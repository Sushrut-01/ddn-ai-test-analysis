-- ===================================================================
-- Migration Script: Add acceptance_tracking table
-- Task: 0-HITL.13
-- Date: 2025-11-02
-- Description: Adds acceptance_tracking table to track validation lifecycle
--              and refinement iterations for AI analyses
-- ===================================================================

-- Connect to database
\c ddn_ai_analysis;

-- ===================================================================
-- 1. CREATE TABLE
-- ===================================================================

CREATE TABLE IF NOT EXISTS acceptance_tracking (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER NOT NULL REFERENCES failure_analysis(id) ON DELETE CASCADE,
    build_id VARCHAR(255) NOT NULL,

    -- Validation status tracking
    validation_status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, accepted, rejected, refining, refined
    refinement_count INTEGER DEFAULT 0,
    final_acceptance BOOLEAN DEFAULT NULL,  -- NULL until final decision made

    -- Validator information
    validator_name VARCHAR(100),
    validator_email VARCHAR(255),

    -- Feedback details
    feedback_comment TEXT,

    -- Refinement tracking
    previous_analysis_id INTEGER REFERENCES failure_analysis(id),  -- Links to previous version if refined
    confidence_improvement DECIMAL(3,2),  -- Improvement in confidence after refinement

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP,  -- When final validation occurred

    -- Constraints
    CHECK (validation_status IN ('pending', 'accepted', 'rejected', 'refining', 'refined')),
    CHECK (refinement_count >= 0)
);

-- ===================================================================
-- 2. CREATE INDEXES
-- ===================================================================

-- Drop indexes if they exist (for idempotency)
DROP INDEX IF EXISTS idx_acceptance_tracking_analysis_id;
DROP INDEX IF EXISTS idx_acceptance_tracking_build_id;
DROP INDEX IF EXISTS idx_acceptance_tracking_validation_status;
DROP INDEX IF EXISTS idx_acceptance_tracking_final_acceptance;
DROP INDEX IF EXISTS idx_acceptance_tracking_created_at;
DROP INDEX IF EXISTS idx_acceptance_tracking_validator;

-- Create indexes
CREATE INDEX idx_acceptance_tracking_analysis_id ON acceptance_tracking(analysis_id);
CREATE INDEX idx_acceptance_tracking_build_id ON acceptance_tracking(build_id);
CREATE INDEX idx_acceptance_tracking_validation_status ON acceptance_tracking(validation_status);
CREATE INDEX idx_acceptance_tracking_final_acceptance ON acceptance_tracking(final_acceptance);
CREATE INDEX idx_acceptance_tracking_created_at ON acceptance_tracking(created_at DESC);
CREATE INDEX idx_acceptance_tracking_validator ON acceptance_tracking(validator_email);

-- ===================================================================
-- 3. CREATE TRIGGER
-- ===================================================================

-- Drop trigger if exists (for idempotency)
DROP TRIGGER IF EXISTS update_acceptance_tracking_updated_at ON acceptance_tracking;

-- Create trigger to auto-update updated_at timestamp
CREATE TRIGGER update_acceptance_tracking_updated_at
    BEFORE UPDATE ON acceptance_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- 4. GRANT PERMISSIONS
-- ===================================================================

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE ON acceptance_tracking TO ddn_ai_app;
GRANT USAGE, SELECT ON SEQUENCE acceptance_tracking_id_seq TO ddn_ai_app;

-- ===================================================================
-- 5. VERIFICATION
-- ===================================================================

-- Verify table creation
SELECT
    'acceptance_tracking table created' as status,
    COUNT(*) as column_count
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name = 'acceptance_tracking';

-- Verify indexes
SELECT
    'Indexes created' as status,
    COUNT(*) as index_count
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename = 'acceptance_tracking';

-- Verify trigger
SELECT
    'Trigger created' as status,
    COUNT(*) as trigger_count
FROM pg_trigger t
JOIN pg_class c ON t.tgrelid = c.oid
WHERE c.relname = 'acceptance_tracking';

-- ===================================================================
-- 6. MIGRATION COMPLETE
-- ===================================================================

DO $$
BEGIN
    RAISE NOTICE 'Migration completed successfully!';
    RAISE NOTICE 'acceptance_tracking table added with 6 indexes and 1 trigger';
    RAISE NOTICE 'Table tracks: validation_status, refinement_count, final_acceptance';
END $$;

-- ===================================================================
-- ROLLBACK SCRIPT (if needed)
-- ===================================================================
-- To rollback this migration, run:
-- DROP TABLE IF EXISTS acceptance_tracking CASCADE;
