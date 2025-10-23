-- ===================================================================
-- DDN AI Test Failure Analysis - PostgreSQL Schema
-- Phase 2 Implementation: Structured metadata storage
-- ===================================================================

-- Create database (run as superuser)
CREATE DATABASE ddn_ai_analysis
    WITH
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

\c ddn_ai_analysis;

-- ===================================================================
-- 1. FAILURE ANALYSIS TABLE
-- Stores AI analysis results and metadata
-- ===================================================================

CREATE TABLE IF NOT EXISTS failure_analysis (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    test_suite VARCHAR(255),

    -- Error classification
    error_category VARCHAR(50),  -- CODE_ERROR, INFRA_ERROR, etc.

    -- Analysis results
    root_cause TEXT,
    fix_recommendation TEXT,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Phase 2: Consecutive failures tracking
    consecutive_failures INTEGER DEFAULT 1,

    -- Analysis metadata
    analysis_type VARCHAR(50),  -- RAG_BASED, CLAUDE_DEEP_ANALYSIS
    estimated_cost_usd DECIMAL(10,4),
    processing_time_ms INTEGER,

    -- Timestamps
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Phase 2: Feedback tracking
    feedback_requested BOOLEAN DEFAULT TRUE,
    feedback_received BOOLEAN DEFAULT FALSE,
    feedback_result VARCHAR(20),  -- success, failed, partial
    feedback_timestamp TIMESTAMP,
    feedback_notes TEXT,

    -- Indexes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_failure_analysis_build_id ON failure_analysis(build_id);
CREATE INDEX idx_failure_analysis_job_name ON failure_analysis(job_name);
CREATE INDEX idx_failure_analysis_error_category ON failure_analysis(error_category);
CREATE INDEX idx_failure_analysis_timestamp ON failure_analysis(timestamp DESC);
CREATE INDEX idx_failure_analysis_consecutive ON failure_analysis(consecutive_failures DESC);
CREATE INDEX idx_failure_analysis_feedback ON failure_analysis(feedback_requested, feedback_received);

-- ===================================================================
-- 2. BUILD METADATA TABLE
-- Stores structured build information
-- ===================================================================

CREATE TABLE IF NOT EXISTS build_metadata (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) UNIQUE NOT NULL,
    job_name VARCHAR(255) NOT NULL,
    test_suite VARCHAR(255),
    build_url TEXT,
    status VARCHAR(20),  -- FAILURE, SUCCESS

    -- Build metrics
    build_duration_ms INTEGER,
    total_tests INTEGER,
    passed_tests INTEGER,
    failed_tests INTEGER,
    skipped_tests INTEGER,

    -- Environment
    os_type VARCHAR(50),
    python_version VARCHAR(20),
    java_version VARCHAR(20),

    -- Timestamps
    build_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key to analysis
    analysis_id INTEGER REFERENCES failure_analysis(id) ON DELETE CASCADE
);

CREATE INDEX idx_build_metadata_build_id ON build_metadata(build_id);
CREATE INDEX idx_build_metadata_job_name ON build_metadata(job_name);
CREATE INDEX idx_build_metadata_status ON build_metadata(status);
CREATE INDEX idx_build_metadata_timestamp ON build_metadata(build_timestamp DESC);

-- ===================================================================
-- 3. TEST CASE HISTORY TABLE
-- Tracks individual test case failures over time
-- ===================================================================

CREATE TABLE IF NOT EXISTS test_case_history (
    id SERIAL PRIMARY KEY,
    test_case_name VARCHAR(255) NOT NULL,
    test_suite VARCHAR(255),
    job_name VARCHAR(255) NOT NULL,

    -- Test execution
    status VARCHAR(20),  -- PASSED, FAILED, SKIPPED
    error_message TEXT,
    execution_time_ms INTEGER,

    -- Build reference
    build_id VARCHAR(255) REFERENCES build_metadata(build_id) ON DELETE CASCADE,

    -- Timestamps
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_test_case_history_name ON test_case_history(test_case_name);
CREATE INDEX idx_test_case_history_status ON test_case_history(status);
CREATE INDEX idx_test_case_history_build_id ON test_case_history(build_id);
CREATE INDEX idx_test_case_history_executed_at ON test_case_history(executed_at DESC);

-- ===================================================================
-- 4. FEEDBACK TABLE
-- Phase 2: Stores user feedback on AI recommendations
-- ===================================================================

CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES failure_analysis(id) ON DELETE CASCADE,
    build_id VARCHAR(255) NOT NULL,

    -- Feedback details
    feedback_type VARCHAR(20) NOT NULL,  -- success, failed, partial, incorrect_classification
    feedback_text TEXT,

    -- User info
    user_id VARCHAR(100),
    user_email VARCHAR(255),

    -- Alternative solution (if AI was wrong)
    alternative_root_cause TEXT,
    alternative_fix TEXT,

    -- Timestamps
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_feedback_analysis_id ON user_feedback(analysis_id);
CREATE INDEX idx_user_feedback_build_id ON user_feedback(build_id);
CREATE INDEX idx_user_feedback_type ON user_feedback(feedback_type);
CREATE INDEX idx_user_feedback_submitted_at ON user_feedback(submitted_at DESC);

-- ===================================================================
-- 5. FAILURE PATTERN TABLE
-- Tracks recurring failure patterns
-- ===================================================================

CREATE TABLE IF NOT EXISTS failure_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(255) UNIQUE NOT NULL,
    error_category VARCHAR(50),

    -- Pattern detection
    error_signature TEXT,  -- Unique signature/hash of error
    occurrence_count INTEGER DEFAULT 1,

    -- Common attributes
    common_job_names TEXT[],
    common_test_suites TEXT[],
    common_files TEXT[],

    -- Solution tracking
    best_solution_id INTEGER REFERENCES failure_analysis(id),
    solution_success_rate DECIMAL(3,2),

    -- Timestamps
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_failure_patterns_error_category ON failure_patterns(error_category);
CREATE INDEX idx_failure_patterns_occurrence ON failure_patterns(occurrence_count DESC);
CREATE INDEX idx_failure_patterns_last_seen ON failure_patterns(last_seen DESC);

-- ===================================================================
-- 6. MANUAL TRIGGER LOG TABLE
-- Phase 2: Tracks manual AI analysis triggers
-- ===================================================================

CREATE TABLE IF NOT EXISTS manual_trigger_log (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL,

    -- User info
    triggered_by_user VARCHAR(100),
    trigger_source VARCHAR(50),  -- dashboard, api, teams

    -- Trigger metadata
    consecutive_failures_at_trigger INTEGER,
    reason TEXT,

    -- Result
    analysis_id INTEGER REFERENCES failure_analysis(id),
    trigger_successful BOOLEAN DEFAULT TRUE,

    -- Timestamps
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_manual_trigger_log_build_id ON manual_trigger_log(build_id);
CREATE INDEX idx_manual_trigger_log_user ON manual_trigger_log(triggered_by_user);
CREATE INDEX idx_manual_trigger_log_triggered_at ON manual_trigger_log(triggered_at DESC);

-- ===================================================================
-- 7. AI MODEL METRICS TABLE
-- Tracks AI model performance over time
-- ===================================================================

CREATE TABLE IF NOT EXISTS ai_model_metrics (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,

    -- Analysis metrics
    total_analyses INTEGER DEFAULT 0,
    rag_based_analyses INTEGER DEFAULT 0,
    claude_deep_analyses INTEGER DEFAULT 0,
    skipped_analyses INTEGER DEFAULT 0,

    -- Cost metrics
    total_cost_usd DECIMAL(10,2) DEFAULT 0,
    avg_cost_per_analysis DECIMAL(10,4),

    -- Performance metrics
    avg_processing_time_ms INTEGER,
    avg_confidence_score DECIMAL(3,2),

    -- Feedback metrics
    feedback_received_count INTEGER DEFAULT 0,
    positive_feedback_count INTEGER DEFAULT 0,
    negative_feedback_count INTEGER DEFAULT 0,
    feedback_success_rate DECIMAL(3,2),

    -- Token usage
    total_tokens_used BIGINT DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(date)
);

CREATE INDEX idx_ai_model_metrics_date ON ai_model_metrics(date DESC);

-- ===================================================================
-- VIEWS FOR ANALYTICS
-- ===================================================================

-- View: Recent failures with analysis
CREATE OR REPLACE VIEW v_recent_failures AS
SELECT
    fa.id,
    fa.build_id,
    fa.job_name,
    fa.test_suite,
    fa.error_category,
    fa.root_cause,
    fa.consecutive_failures,
    fa.confidence_score,
    fa.analysis_type,
    fa.feedback_received,
    fa.feedback_result,
    fa.timestamp,
    bm.build_url,
    bm.status as build_status,
    bm.total_tests,
    bm.failed_tests
FROM failure_analysis fa
LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id
ORDER BY fa.timestamp DESC
LIMIT 100;

-- View: Failure patterns summary
CREATE OR REPLACE VIEW v_failure_patterns_summary AS
SELECT
    fp.pattern_name,
    fp.error_category,
    fp.occurrence_count,
    fp.solution_success_rate,
    fp.last_seen,
    fa.root_cause as recommended_solution,
    fa.fix_recommendation
FROM failure_patterns fp
LEFT JOIN failure_analysis fa ON fp.best_solution_id = fa.id
ORDER BY fp.occurrence_count DESC;

-- View: Consecutive failures tracking
CREATE OR REPLACE VIEW v_consecutive_failures AS
SELECT
    job_name,
    test_suite,
    COUNT(*) as total_failures,
    MAX(consecutive_failures) as max_consecutive,
    AVG(consecutive_failures) as avg_consecutive,
    MAX(timestamp) as last_failure
FROM failure_analysis
WHERE timestamp > CURRENT_DATE - INTERVAL '30 days'
GROUP BY job_name, test_suite
HAVING COUNT(*) >= 3
ORDER BY max_consecutive DESC;

-- View: Feedback summary
CREATE OR REPLACE VIEW v_feedback_summary AS
SELECT
    fa.error_category,
    fa.analysis_type,
    COUNT(uf.id) as total_feedback,
    SUM(CASE WHEN uf.feedback_type = 'success' THEN 1 ELSE 0 END) as positive_feedback,
    SUM(CASE WHEN uf.feedback_type = 'failed' THEN 1 ELSE 0 END) as negative_feedback,
    ROUND(
        SUM(CASE WHEN uf.feedback_type = 'success' THEN 1 ELSE 0 END)::DECIMAL /
        NULLIF(COUNT(uf.id), 0) * 100,
        2
    ) as success_rate_percent
FROM failure_analysis fa
LEFT JOIN user_feedback uf ON fa.id = uf.analysis_id
WHERE fa.timestamp > CURRENT_DATE - INTERVAL '30 days'
GROUP BY fa.error_category, fa.analysis_type
ORDER BY total_feedback DESC;

-- ===================================================================
-- FUNCTIONS
-- ===================================================================

-- Function: Update AI model metrics daily
CREATE OR REPLACE FUNCTION update_daily_metrics()
RETURNS void AS $$
BEGIN
    INSERT INTO ai_model_metrics (
        date,
        total_analyses,
        rag_based_analyses,
        claude_deep_analyses,
        skipped_analyses,
        total_cost_usd,
        avg_cost_per_analysis,
        avg_processing_time_ms,
        avg_confidence_score,
        feedback_received_count,
        positive_feedback_count,
        negative_feedback_count,
        feedback_success_rate
    )
    SELECT
        CURRENT_DATE,
        COUNT(*),
        SUM(CASE WHEN analysis_type = 'RAG_BASED' THEN 1 ELSE 0 END),
        SUM(CASE WHEN analysis_type = 'CLAUDE_DEEP_ANALYSIS' THEN 1 ELSE 0 END),
        SUM(CASE WHEN analysis_type = 'SKIPPED' THEN 1 ELSE 0 END),
        SUM(estimated_cost_usd),
        AVG(estimated_cost_usd),
        AVG(processing_time_ms),
        AVG(confidence_score),
        SUM(CASE WHEN feedback_received THEN 1 ELSE 0 END),
        SUM(CASE WHEN feedback_result = 'success' THEN 1 ELSE 0 END),
        SUM(CASE WHEN feedback_result = 'failed' THEN 1 ELSE 0 END),
        CASE
            WHEN SUM(CASE WHEN feedback_received THEN 1 ELSE 0 END) > 0
            THEN SUM(CASE WHEN feedback_result = 'success' THEN 1 ELSE 0 END)::DECIMAL /
                 SUM(CASE WHEN feedback_received THEN 1 ELSE 0 END)
            ELSE NULL
        END
    FROM failure_analysis
    WHERE DATE(timestamp) = CURRENT_DATE
    ON CONFLICT (date) DO UPDATE SET
        total_analyses = EXCLUDED.total_analyses,
        rag_based_analyses = EXCLUDED.rag_based_analyses,
        claude_deep_analyses = EXCLUDED.claude_deep_analyses,
        total_cost_usd = EXCLUDED.total_cost_usd,
        avg_cost_per_analysis = EXCLUDED.avg_cost_per_analysis,
        updated_at = CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- Function: Record feedback
CREATE OR REPLACE FUNCTION record_feedback(
    p_build_id VARCHAR(255),
    p_feedback_type VARCHAR(20),
    p_feedback_text TEXT DEFAULT NULL,
    p_user_id VARCHAR(100) DEFAULT NULL
)
RETURNS INTEGER AS $$
DECLARE
    v_analysis_id INTEGER;
    v_feedback_id INTEGER;
BEGIN
    -- Get analysis ID
    SELECT id INTO v_analysis_id
    FROM failure_analysis
    WHERE build_id = p_build_id
    ORDER BY timestamp DESC
    LIMIT 1;

    IF v_analysis_id IS NULL THEN
        RAISE EXCEPTION 'No analysis found for build_id: %', p_build_id;
    END IF;

    -- Insert feedback
    INSERT INTO user_feedback (
        analysis_id,
        build_id,
        feedback_type,
        feedback_text,
        user_id
    ) VALUES (
        v_analysis_id,
        p_build_id,
        p_feedback_type,
        p_feedback_text,
        p_user_id
    )
    RETURNING id INTO v_feedback_id;

    -- Update failure_analysis
    UPDATE failure_analysis
    SET
        feedback_received = TRUE,
        feedback_result = p_feedback_type,
        feedback_timestamp = CURRENT_TIMESTAMP
    WHERE id = v_analysis_id;

    RETURN v_feedback_id;
END;
$$ LANGUAGE plpgsql;

-- ===================================================================
-- TRIGGERS
-- ===================================================================

-- Trigger: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_failure_analysis_updated_at
    BEFORE UPDATE ON failure_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===================================================================
-- SAMPLE DATA (for testing)
-- ===================================================================

-- Insert sample failure analysis
INSERT INTO failure_analysis (
    build_id, job_name, test_suite, error_category,
    root_cause, fix_recommendation, confidence_score,
    consecutive_failures, analysis_type, estimated_cost_usd
) VALUES
(
    'sample_001',
    'DDN-Smoke-Tests',
    'Health_Check',
    'INFRA_ERROR',
    'OutOfMemoryError: Java heap space insufficient',
    'Increase JVM heap size to 4GB using -Xmx4g parameter',
    0.95,
    3,
    'RAG_BASED',
    0.01
);

-- ===================================================================
-- GRANTS (adjust as needed)
-- ===================================================================

-- Create application user
CREATE USER ddn_ai_app WITH PASSWORD 'your_secure_password_here';

-- Grant permissions
GRANT CONNECT ON DATABASE ddn_ai_analysis TO ddn_ai_app;
GRANT USAGE ON SCHEMA public TO ddn_ai_app;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO ddn_ai_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ddn_ai_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ddn_ai_app;

-- ===================================================================
-- CLEANUP (Optional)
-- ===================================================================

-- Function to clean old data
CREATE OR REPLACE FUNCTION cleanup_old_data(days_to_keep INTEGER DEFAULT 90)
RETURNS void AS $$
BEGIN
    -- Delete old failure analyses
    DELETE FROM failure_analysis
    WHERE timestamp < CURRENT_DATE - (days_to_keep || ' days')::INTERVAL;

    -- Delete old feedback
    DELETE FROM user_feedback
    WHERE submitted_at < CURRENT_DATE - (days_to_keep || ' days')::INTERVAL;

    -- Delete old manual trigger logs
    DELETE FROM manual_trigger_log
    WHERE triggered_at < CURRENT_DATE - (days_to_keep || ' days')::INTERVAL;

    RAISE NOTICE 'Cleanup completed: Deleted data older than % days', days_to_keep;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-old-data', '0 2 * * 0', 'SELECT cleanup_old_data(90)');

-- ===================================================================
-- VERIFICATION QUERIES
-- ===================================================================

-- Check table creation
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check views
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public'
ORDER BY table_name;

-- ===================================================================
-- END OF SCHEMA
-- ===================================================================
