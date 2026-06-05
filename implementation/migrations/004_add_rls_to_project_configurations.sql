-- ============================================
-- Add RLS to project_configurations Table
-- Date: 2026-02-02
-- Purpose: Complete RLS migration by adding project_configurations
-- ============================================

-- Enable RLS
ALTER TABLE project_configurations ENABLE ROW LEVEL SECURITY;

-- Create policies for project_configurations
-- SELECT policy: Users can only see config for their projects
CREATE POLICY project_isolation_select ON project_configurations
    FOR SELECT
    USING (
        project_id = get_current_project_id()
        OR get_current_project_id() IS NULL
    );

-- INSERT policy: Can only insert config for the current project context
CREATE POLICY project_isolation_insert ON project_configurations
    FOR INSERT
    WITH CHECK (
        project_id = get_current_project_id()
        OR get_current_project_id() IS NULL
    );

-- UPDATE policy: Can only update config for the current project context
CREATE POLICY project_isolation_update ON project_configurations
    FOR UPDATE
    USING (
        project_id = get_current_project_id()
        OR get_current_project_id() IS NULL
    );

-- DELETE policy: Can only delete config for the current project context
CREATE POLICY project_isolation_delete ON project_configurations
    FOR DELETE
    USING (
        project_id = get_current_project_id()
        OR get_current_project_id() IS NULL
    );

-- Verify RLS is enabled
SELECT
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename = 'project_configurations';
