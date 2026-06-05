"""
RAG Approval HITL (Human-in-the-Loop) Flow
==========================================

Flow: Error Detection → RAG Analysis → Human Review → Approve/Reject/Escalate
                                              ↓ (if escalated)
                                         AI Deep Analysis

Use Case: Non-code errors identified by RAG need human validation before:
1. Marking as resolved (approved)
2. Rejecting the RAG suggestion (rejected)
3. Escalating to AI for deeper analysis (escalated)

Endpoints:
- GET  /api/rag/pending           - Get pending RAG approvals
- POST /api/rag/approve           - Approve RAG suggestion
- POST /api/rag/reject            - Reject RAG suggestion
- POST /api/rag/escalate          - Escalate to AI analysis
- GET  /api/rag/stats             - Get approval statistics
"""

from flask import Blueprint, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
rag_approval_bp = Blueprint('rag_approval', __name__, url_prefix='/api/rag')

# Configuration
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:password@postgres:5432/ddn_ai_analysis")
MANUAL_TRIGGER_URL = os.getenv("MANUAL_TRIGGER_URL", "http://ddn-manual-trigger:5004")


def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        raise


# ============================================================================
# DATABASE SCHEMA (Run once to create table)
# ============================================================================
RAG_APPROVAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS rag_approval_queue (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL,
    job_name VARCHAR(255),
    error_category VARCHAR(100) NOT NULL,  -- e.g., ENV_CONFIG, NETWORK_ERROR, INFRA_ERROR
    rag_suggestion TEXT,                    -- RAG's recommended solution
    rag_confidence DECIMAL(3,2),            -- RAG confidence score (0.00-1.00)
    similar_cases_count INTEGER DEFAULT 0,  -- Number of similar cases found
    similar_case_ids TEXT,                  -- JSON array of similar case IDs

    -- Human review fields
    review_status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected, escalated
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    review_feedback TEXT,

    -- Escalation tracking
    escalated_to_ai BOOLEAN DEFAULT FALSE,
    ai_analysis_id INTEGER,                 -- FK to failure_analysis if escalated

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT fk_ai_analysis FOREIGN KEY (ai_analysis_id) REFERENCES failure_analysis(id)
);

CREATE INDEX IF NOT EXISTS idx_rag_approval_status ON rag_approval_queue(review_status);
CREATE INDEX IF NOT EXISTS idx_rag_approval_build ON rag_approval_queue(build_id);
CREATE INDEX IF NOT EXISTS idx_rag_approval_created ON rag_approval_queue(created_at DESC);
"""


@rag_approval_bp.route('/pending', methods=['GET'])
def get_pending_approvals():
    """
    Get all pending RAG approvals for human review

    Query params:
    - limit: Max results (default: 50)
    - category: Filter by error category
    """
    try:
        limit = int(request.args.get('limit', 50))
        category = request.args.get('category')

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                id,
                build_id,
                job_name,
                error_category,
                rag_suggestion,
                rag_confidence,
                similar_cases_count,
                similar_case_ids,
                review_status,
                created_at,
                EXTRACT(EPOCH FROM (NOW() - created_at))/3600 as hours_waiting
            FROM rag_approval_queue
            WHERE review_status = 'pending'
        """
        params = []

        if category:
            query += " AND error_category = %s"
            params.append(category)

        query += " ORDER BY created_at ASC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        pending = cursor.fetchall()

        # Get stats
        cursor.execute("""
            SELECT
                COUNT(*) FILTER (WHERE review_status = 'pending') as pending,
                COUNT(*) FILTER (WHERE review_status = 'approved') as approved,
                COUNT(*) FILTER (WHERE review_status = 'rejected') as rejected,
                COUNT(*) FILTER (WHERE review_status = 'escalated') as escalated
            FROM rag_approval_queue
        """)
        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for item in pending:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('hours_waiting'):
                item['hours_waiting'] = round(float(item['hours_waiting']), 1)

        return jsonify({
            'success': True,
            'count': len(pending),
            'stats': dict(stats) if stats else {},
            'pending': [dict(p) for p in pending]
        }), 200

    except Exception as e:
        logger.error(f"Error getting pending approvals: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@rag_approval_bp.route('/approve', methods=['POST'])
def approve_rag_suggestion():
    """
    Approve a RAG suggestion - marks the issue as resolved

    Request:
    {
        "approval_id": 123,
        "reviewed_by": "user@company.com",
        "feedback": "Solution worked, confirmed fix"
    }
    """
    try:
        data = request.get_json()

        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        feedback = data.get('feedback', '')

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            UPDATE rag_approval_queue
            SET
                review_status = 'approved',
                reviewed_by = %s,
                reviewed_at = NOW(),
                review_feedback = %s,
                updated_at = NOW()
            WHERE id = %s AND review_status = 'pending'
            RETURNING id, build_id, error_category
        """, (reviewed_by, feedback, approval_id))

        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Approval not found or already processed'}), 404

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✅ RAG suggestion approved for build {result['build_id']} by {reviewed_by}")

        return jsonify({
            'success': True,
            'message': 'RAG suggestion approved',
            'approval_id': result['id'],
            'build_id': result['build_id']
        }), 200

    except Exception as e:
        logger.error(f"Error approving RAG suggestion: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@rag_approval_bp.route('/reject', methods=['POST'])
def reject_rag_suggestion():
    """
    Reject a RAG suggestion - marks as incorrect, feedback used for RAG improvement

    Request:
    {
        "approval_id": 123,
        "reviewed_by": "user@company.com",
        "feedback": "Wrong category, this is actually a code error",
        "correct_category": "CODE_ERROR"  // optional - helps RAG learn
    }
    """
    try:
        data = request.get_json()

        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        feedback = data.get('feedback', '')
        correct_category = data.get('correct_category')

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Include correct_category in feedback if provided
        full_feedback = feedback
        if correct_category:
            full_feedback = f"{feedback} [Correct category: {correct_category}]"

        cursor.execute("""
            UPDATE rag_approval_queue
            SET
                review_status = 'rejected',
                reviewed_by = %s,
                reviewed_at = NOW(),
                review_feedback = %s,
                updated_at = NOW()
            WHERE id = %s AND review_status = 'pending'
            RETURNING id, build_id, error_category, rag_suggestion
        """, (reviewed_by, full_feedback, approval_id))

        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Approval not found or already processed'}), 404

        conn.commit()

        # TODO: Send feedback to RAG system for learning
        # This would update the knowledge base or reranking model

        cursor.close()
        conn.close()

        logger.info(f"❌ RAG suggestion rejected for build {result['build_id']} by {reviewed_by}")

        return jsonify({
            'success': True,
            'message': 'RAG suggestion rejected',
            'approval_id': result['id'],
            'build_id': result['build_id'],
            'feedback_recorded': True
        }), 200

    except Exception as e:
        logger.error(f"Error rejecting RAG suggestion: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@rag_approval_bp.route('/escalate', methods=['POST'])
def escalate_to_ai():
    """
    Escalate to AI for deeper analysis - triggers Claude deep analysis

    Request:
    {
        "approval_id": 123,
        "reviewed_by": "user@company.com",
        "reason": "RAG solution unclear, needs deeper code analysis"
    }
    """
    try:
        data = request.get_json()

        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        reason = data.get('reason', 'Escalated for deeper AI analysis')

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the approval record
        cursor.execute("""
            SELECT id, build_id, error_category, rag_suggestion
            FROM rag_approval_queue
            WHERE id = %s AND review_status = 'pending'
        """, (approval_id,))

        approval = cursor.fetchone()

        if not approval:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Approval not found or already processed'}), 404

        build_id = approval['build_id']

        # Trigger AI analysis via Manual Trigger API
        try:
            trigger_response = requests.post(
                f"{MANUAL_TRIGGER_URL}/api/trigger-analysis",
                json={
                    "build_id": build_id,
                    "triggered_by_user": reviewed_by,
                    "reason": f"Escalated from RAG review: {reason}",
                    "trigger_source": "rag_escalation"
                },
                timeout=120
            )
            trigger_response.raise_for_status()
            trigger_result = trigger_response.json()

            # Get the analysis_id if available
            ai_analysis_id = trigger_result.get('analysis_result', {}).get('storage_id')

        except Exception as e:
            logger.error(f"Failed to trigger AI analysis: {e}")
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': f'AI analysis trigger failed: {str(e)}'
            }), 500

        # Update the approval record
        cursor.execute("""
            UPDATE rag_approval_queue
            SET
                review_status = 'escalated',
                reviewed_by = %s,
                reviewed_at = NOW(),
                review_feedback = %s,
                escalated_to_ai = TRUE,
                ai_analysis_id = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (reviewed_by, reason, ai_analysis_id, approval_id))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"🔄 RAG suggestion escalated to AI for build {build_id} by {reviewed_by}")

        return jsonify({
            'success': True,
            'message': 'Escalated to AI analysis',
            'approval_id': approval_id,
            'build_id': build_id,
            'ai_analysis_id': ai_analysis_id,
            'analysis_result': trigger_result.get('analysis_result')
        }), 200

    except Exception as e:
        logger.error(f"Error escalating to AI: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@rag_approval_bp.route('/stats', methods=['GET'])
def get_approval_stats():
    """
    Get RAG approval statistics

    Returns stats on approval rates, escalation rates, category distribution
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Overall stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE review_status = 'pending') as pending,
                COUNT(*) FILTER (WHERE review_status = 'approved') as approved,
                COUNT(*) FILTER (WHERE review_status = 'rejected') as rejected,
                COUNT(*) FILTER (WHERE review_status = 'escalated') as escalated,
                ROUND(AVG(rag_confidence)::numeric, 2) as avg_confidence,
                ROUND(AVG(CASE WHEN review_status = 'approved' THEN rag_confidence END)::numeric, 2) as approved_avg_confidence,
                ROUND(AVG(CASE WHEN review_status = 'rejected' THEN rag_confidence END)::numeric, 2) as rejected_avg_confidence
            FROM rag_approval_queue
        """)
        overall = cursor.fetchone()

        # Category breakdown
        cursor.execute("""
            SELECT
                error_category,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE review_status = 'approved') as approved,
                COUNT(*) FILTER (WHERE review_status = 'rejected') as rejected,
                COUNT(*) FILTER (WHERE review_status = 'escalated') as escalated,
                ROUND(100.0 * COUNT(*) FILTER (WHERE review_status = 'approved') / NULLIF(COUNT(*), 0), 1) as approval_rate
            FROM rag_approval_queue
            GROUP BY error_category
            ORDER BY total DESC
        """)
        by_category = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'overall': dict(overall) if overall else {},
            'by_category': [dict(c) for c in by_category]
        }), 200

    except Exception as e:
        logger.error(f"Error getting approval stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@rag_approval_bp.route('/add', methods=['POST'])
def add_to_approval_queue():
    """
    Add a RAG result to the approval queue (called by RAG system when non-code error detected)

    Request:
    {
        "build_id": "DDN-Basic-Tests-123",
        "job_name": "DDN-Basic-Tests",
        "error_category": "ENV_CONFIG",
        "rag_suggestion": "Check environment variable X...",
        "rag_confidence": 0.85,
        "similar_cases_count": 3,
        "similar_case_ids": ["case-1", "case-2", "case-3"]
    }
    """
    try:
        data = request.get_json()

        build_id = data.get('build_id')
        if not build_id:
            return jsonify({'success': False, 'error': 'build_id required'}), 400

        job_name = data.get('job_name', '')
        error_category = data.get('error_category', 'UNKNOWN')
        rag_suggestion = data.get('rag_suggestion', '')
        rag_confidence = float(data.get('rag_confidence', 0))
        similar_cases_count = int(data.get('similar_cases_count', 0))
        similar_case_ids = data.get('similar_case_ids', [])

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO rag_approval_queue (
                build_id, job_name, error_category, rag_suggestion,
                rag_confidence, similar_cases_count, similar_case_ids,
                review_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending', NOW())
            RETURNING id
        """, (
            build_id, job_name, error_category, rag_suggestion,
            rag_confidence, similar_cases_count, str(similar_case_ids)
        ))

        result = cursor.fetchone()
        approval_id = result['id']

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"📋 Added build {build_id} to RAG approval queue (ID: {approval_id})")

        return jsonify({
            'success': True,
            'message': 'Added to approval queue',
            'approval_id': approval_id,
            'build_id': build_id
        }), 201

    except Exception as e:
        logger.error(f"Error adding to approval queue: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Schema creation function (call on startup)
def ensure_schema():
    """Create the rag_approval_queue table if it doesn't exist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(RAG_APPROVAL_SCHEMA)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("✓ RAG approval queue schema ensured")
    except Exception as e:
        logger.error(f"Failed to create schema: {e}")
