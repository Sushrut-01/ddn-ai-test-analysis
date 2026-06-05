-- ============================================
-- CRITICAL SECURITY FIX: Row-Level Security
-- Date: 2026-02-02
-- Purpose: Enforce project-level data isolation at database level
-- ============================================

-- ============================================
-- STEP 1: Create Security Context Functions
-- ============================================

-- Function to set current project context
CREATE OR REPLACE FUNCTION set_project_context(p_project_id INTEGER)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_project_id', p_project_id::TEXT, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current project context
CREATE OR REPLACE FUNCTION get_current_project_id()
RETURNS INTEGER AS $$
BEGIN
    RETURN NULLIF(current_setting('app.current_project_id', TRUE), '')::INTEGER;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- STEP 2: Enable RLS on All Multi-Project Tables
-- ============================================

ALTER TABLE failure_analysis ENABLE ROW LEVEL SECURITY;
ALTER TABLE build_metadata ENABLE ROW LEVEL SECURITY;
ALTER TABLE test_case_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE acceptance_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE failure_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE manual_trigger_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_doc_changes ENABLE ROW LEVEL SECURITY;

-- ============================================
-- STEP 3: Create RLS Policies
-- ============================================

-- Policy for failure_analysis
CREATE POLICY project_isolation_select ON failure_analysis
    FOR SELECT
    USING (
        project_id = get_current_project_id()
        OR get_current_project_id() IS NULL
    );

CREATE POLICY project_isolation_insert ON failure_analysis
    FOR INSERT
    WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_update ON failure_analysis
    FOR UPDATE
    USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_delete ON failure_analysis
    FOR DELETE
    USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for build_metadata
CREATE POLICY project_isolation_select ON build_metadata
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON build_metadata
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_update ON build_metadata
    FOR UPDATE USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_delete ON build_metadata
    FOR DELETE USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for test_case_history
CREATE POLICY project_isolation_select ON test_case_history
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON test_case_history
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for user_feedback
CREATE POLICY project_isolation_select ON user_feedback
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON user_feedback
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for acceptance_tracking
CREATE POLICY project_isolation_select ON acceptance_tracking
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON acceptance_tracking
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for failure_patterns
CREATE POLICY project_isolation_select ON failure_patterns
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON failure_patterns
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for manual_trigger_log
CREATE POLICY project_isolation_select ON manual_trigger_log
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON manual_trigger_log
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for ai_model_metrics
CREATE POLICY project_isolation_select ON ai_model_metrics
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON ai_model_metrics
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- Policy for knowledge_doc_changes
CREATE POLICY project_isolation_select ON knowledge_doc_changes
    FOR SELECT USING (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

CREATE POLICY project_isolation_insert ON knowledge_doc_changes
    FOR INSERT WITH CHECK (project_id = get_current_project_id() OR get_current_project_id() IS NULL);

-- ============================================
-- STEP 4: Create Composite Indexes for Performance
-- ============================================

-- Drop existing single-column indexes if they exist
DROP INDEX IF EXISTS idx_failure_analysis_project;
DROP INDEX IF EXISTS idx_build_metadata_project;

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_failure_analysis_project_created
    ON failure_analysis(project_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_failure_analysis_project_status
    ON failure_analysis(project_id, status, created_at DESC) WHERE status IS NOT NULL;
