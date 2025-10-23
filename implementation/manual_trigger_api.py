"""
Manual Trigger & Feedback API for DDN AI Test Failure Analysis
Phase 2 Implementation: Manual triggers and feedback loop

Endpoints:
- POST /api/trigger-analysis - Manual trigger for specific build
- POST /api/feedback - Submit feedback on AI recommendation
- GET /api/feedback/:build_id - Get feedback for a build
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard access

# Configuration
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/ddn-test-failure")
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://ddn_ai_app:password@localhost:5432/ddn_ai_analysis")
PINECONE_SERVICE_URL = os.getenv("PINECONE_SERVICE_URL", "http://localhost:5003")

# PostgreSQL connection
def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        raise

# ============================================================================
# MANUAL TRIGGER ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        postgres_connected = True
    except:
        postgres_connected = False

    return jsonify({
        "status": "healthy" if postgres_connected else "degraded",
        "service": "Manual Trigger & Feedback API",
        "version": "2.0.0",
        "postgres_connected": postgres_connected
    }), 200


@app.route('/api/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    """
    Manually trigger AI analysis for a specific build

    Request:
    {
        "build_id": "12345",
        "triggered_by_user": "john.doe@company.com",
        "reason": "Critical production issue"
    }

    Response:
    {
        "success": true,
        "message": "Analysis triggered successfully",
        "trigger_id": 123,
        "build_id": "12345",
        "webhook_response": {...}
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data:
            return jsonify({
                "error": "Missing required field: build_id"
            }), 400

        build_id = data['build_id']
        triggered_by_user = data.get('triggered_by_user', 'anonymous')
        reason = data.get('reason', 'Manual trigger from dashboard')
        trigger_source = data.get('trigger_source', 'dashboard')

        logger.info(f"🎯 Manual trigger requested for build: {build_id} by {triggered_by_user}")

        # Get current consecutive failures count from PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT consecutive_failures
            FROM failure_analysis
            WHERE build_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (build_id,))

        result = cursor.fetchone()
        consecutive_failures = result['consecutive_failures'] if result else 1

        # Log manual trigger in database
        cursor.execute("""
            INSERT INTO manual_trigger_log (
                build_id,
                triggered_by_user,
                trigger_source,
                consecutive_failures_at_trigger,
                reason,
                triggered_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (build_id, triggered_by_user, trigger_source, consecutive_failures, reason))

        trigger_id = cursor.fetchone()['id']
        conn.commit()

        logger.info(f"📝 Manual trigger logged with ID: {trigger_id}")

        # Trigger n8n workflow with manual_trigger flag
        webhook_payload = {
            "build_id": build_id,
            "manual_trigger": True,
            "triggered_by_user": triggered_by_user,
            "trigger_reason": reason,
            "trigger_id": trigger_id
        }

        logger.info(f"📤 Sending webhook to n8n: {N8N_WEBHOOK_URL}")

        webhook_response = requests.post(
            N8N_WEBHOOK_URL,
            json=webhook_payload,
            timeout=10
        )

        webhook_response.raise_for_status()

        # Update trigger log with success
        cursor.execute("""
            UPDATE manual_trigger_log
            SET trigger_successful = TRUE
            WHERE id = %s
        """, (trigger_id,))
        conn.commit()

        cursor.close()
        conn.close()

        logger.info(f"✅ Manual trigger successful for build: {build_id}")

        return jsonify({
            "success": True,
            "message": "Analysis triggered successfully",
            "trigger_id": trigger_id,
            "build_id": build_id,
            "consecutive_failures": consecutive_failures,
            "webhook_response": webhook_response.json() if webhook_response.content else {}
        }), 200

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Webhook request failed: {e}")
        return jsonify({
            "error": "Failed to trigger workflow",
            "details": str(e)
        }), 500
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {e}")
        return jsonify({
            "error": "Manual trigger failed",
            "details": str(e)
        }), 500


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback on AI recommendation

    Request:
    {
        "build_id": "12345",
        "feedback_type": "success",  // success, failed, partial, incorrect_classification
        "feedback_text": "Fix worked perfectly!",
        "user_id": "john.doe@company.com",
        "alternative_root_cause": "...",  // if feedback_type = incorrect_classification
        "alternative_fix": "..."
    }

    Response:
    {
        "success": true,
        "feedback_id": 456,
        "message": "Feedback recorded successfully",
        "pinecone_updated": true
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data or 'feedback_type' not in data:
            return jsonify({
                "error": "Missing required fields: build_id, feedback_type"
            }), 400

        build_id = data['build_id']
        feedback_type = data['feedback_type']
        feedback_text = data.get('feedback_text', '')
        user_id = data.get('user_id', 'anonymous')
        alternative_root_cause = data.get('alternative_root_cause')
        alternative_fix = data.get('alternative_fix')

        logger.info(f"📊 Feedback received for build: {build_id} - Type: {feedback_type}")

        # Record feedback in PostgreSQL using stored procedure
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT record_feedback(%s, %s, %s, %s)
        """, (build_id, feedback_type, feedback_text, user_id))

        feedback_id = cursor.fetchone()['record_feedback']

        # If alternative solution provided, store it
        if alternative_root_cause or alternative_fix:
            cursor.execute("""
                UPDATE user_feedback
                SET
                    alternative_root_cause = %s,
                    alternative_fix = %s
                WHERE id = %s
            """, (alternative_root_cause, alternative_fix, feedback_id))

        conn.commit()

        logger.info(f"✅ Feedback recorded with ID: {feedback_id}")

        # Update Pinecone vector database with feedback
        pinecone_updated = False
        try:
            # Get the vector ID for this build
            cursor.execute("""
                SELECT build_id
                FROM failure_analysis
                WHERE build_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (build_id,))

            result = cursor.fetchone()
            if result:
                # Update success rate in Pinecone
                feedback_successful = feedback_type in ['success', 'partial']

                pinecone_response = requests.post(
                    f"{PINECONE_SERVICE_URL}/api/update-feedback",
                    json={
                        "vector_id": f"{build_id}_{int(datetime.now().timestamp())}",
                        "success": feedback_successful,
                        "increment_usage": True
                    },
                    timeout=10
                )

                if pinecone_response.status_code == 200:
                    pinecone_updated = True
                    logger.info(f"✅ Pinecone updated with feedback for build: {build_id}")

        except Exception as e:
            logger.warning(f"⚠️  Pinecone update failed: {e}")

        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback recorded successfully",
            "pinecone_updated": pinecone_updated
        }), 200

    except Exception as e:
        logger.error(f"❌ Feedback submission failed: {e}")
        return jsonify({
            "error": "Feedback submission failed",
            "details": str(e)
        }), 500


@app.route('/api/feedback/<build_id>', methods=['GET'])
def get_feedback(build_id):
    """
    Get feedback for a specific build

    Response:
    {
        "build_id": "12345",
        "has_feedback": true,
        "feedback": [
            {
                "id": 456,
                "feedback_type": "success",
                "feedback_text": "...",
                "user_id": "...",
                "submitted_at": "..."
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                uf.id,
                uf.feedback_type,
                uf.feedback_text,
                uf.user_id,
                uf.alternative_root_cause,
                uf.alternative_fix,
                uf.submitted_at
            FROM user_feedback uf
            WHERE uf.build_id = %s
            ORDER BY uf.submitted_at DESC
        """, (build_id,))

        feedback_records = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "build_id": build_id,
            "has_feedback": len(feedback_records) > 0,
            "feedback_count": len(feedback_records),
            "feedback": [dict(record) for record in feedback_records]
        }), 200

    except Exception as e:
        logger.error(f"❌ Get feedback failed: {e}")
        return jsonify({
            "error": "Failed to retrieve feedback",
            "details": str(e)
        }), 500


@app.route('/api/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """
    Get recent feedback across all builds

    Query params:
    - limit: Number of records (default: 50)
    - feedback_type: Filter by type (optional)

    Response:
    {
        "total": 123,
        "feedback": [...]
    }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        feedback_type = request.args.get('feedback_type')

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                uf.id,
                uf.build_id,
                uf.feedback_type,
                uf.feedback_text,
                uf.user_id,
                uf.submitted_at,
                fa.job_name,
                fa.error_category,
                fa.confidence_score
            FROM user_feedback uf
            JOIN failure_analysis fa ON uf.analysis_id = fa.id
        """

        if feedback_type:
            query += " WHERE uf.feedback_type = %s"
            cursor.execute(query + " ORDER BY uf.submitted_at DESC LIMIT %s", (feedback_type, limit))
        else:
            cursor.execute(query + " ORDER BY uf.submitted_at DESC LIMIT %s", (limit,))

        feedback_records = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "total": len(feedback_records),
            "feedback": [dict(record) for record in feedback_records]
        }), 200

    except Exception as e:
        logger.error(f"❌ Get recent feedback failed: {e}")
        return jsonify({
            "error": "Failed to retrieve feedback",
            "details": str(e)
        }), 500


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get analytics summary

    Response:
    {
        "total_analyses": 123,
        "analysis_breakdown": {...},
        "feedback_stats": {...},
        "cost_stats": {...}
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get recent metrics
        cursor.execute("""
            SELECT
                COUNT(*) as total_analyses,
                SUM(CASE WHEN analysis_type = 'RAG_BASED' THEN 1 ELSE 0 END) as rag_analyses,
                SUM(CASE WHEN analysis_type = 'CLAUDE_DEEP_ANALYSIS' THEN 1 ELSE 0 END) as claude_analyses,
                SUM(estimated_cost_usd) as total_cost,
                AVG(confidence_score) as avg_confidence,
                AVG(processing_time_ms) as avg_processing_time,
                SUM(CASE WHEN feedback_received THEN 1 ELSE 0 END) as feedback_count,
                SUM(CASE WHEN feedback_result = 'success' THEN 1 ELSE 0 END) as positive_feedback
            FROM failure_analysis
            WHERE timestamp > CURRENT_DATE - INTERVAL '30 days'
        """)

        summary = dict(cursor.fetchone())

        cursor.close()
        conn.close()

        # Calculate success rate
        if summary['feedback_count'] > 0:
            summary['feedback_success_rate'] = round(
                (summary['positive_feedback'] / summary['feedback_count']) * 100,
                2
            )
        else:
            summary['feedback_success_rate'] = None

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"❌ Get analytics failed: {e}")
        return jsonify({
            "error": "Failed to retrieve analytics",
            "details": str(e)
        }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting Manual Trigger & Feedback API...")
    logger.info(f"📍 Server will run on: http://localhost:5004")
    logger.info(f"📍 Health Check: http://localhost:5004/health")

    # Verify environment
    if not POSTGRES_URI:
        logger.warning("⚠️  POSTGRES_URI not set!")

    if not N8N_WEBHOOK_URL:
        logger.warning("⚠️  N8N_WEBHOOK_URL not set!")

    # Test PostgreSQL connection
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("✅ PostgreSQL connected successfully")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.warning("⚠️  Server will start but database features may not work!")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5004,
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        threaded=True
    )
