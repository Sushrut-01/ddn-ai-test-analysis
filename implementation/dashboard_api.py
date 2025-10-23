"""
Dashboard Backend API Service
Port: 5005
Purpose: Provides REST API endpoints for the Analytics Dashboard UI
Features:
- Failure analytics and trends
- Real-time status monitoring
- Manual trigger interface
- Feedback submission
- Historical data visualization
- AI model performance metrics
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import pymongo
from bson import ObjectId
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'jenkins_failure_analysis')

MANUAL_TRIGGER_API = os.getenv('MANUAL_TRIGGER_API', 'http://localhost:5004')

# Database connections
def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)

def get_mongodb_connection():
    """Create MongoDB connection"""
    client = pymongo.MongoClient(MONGODB_URI)
    return client[MONGODB_DB]


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get high-level analytics summary for dashboard homepage
    Returns: Overall metrics, trends, recent activity
    """
    try:
        time_range = request.args.get('time_range', '7d')  # 7d, 30d, 90d

        days = 7
        if time_range == '30d':
            days = 30
        elif time_range == '90d':
            days = 90

        start_date = datetime.now() - timedelta(days=days)

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Overall metrics
        cursor.execute("""
            SELECT
                COUNT(*) as total_failures,
                COUNT(DISTINCT build_id) as unique_builds,
                AVG(confidence_score) as avg_confidence,
                COUNT(CASE WHEN feedback_result = 'success' THEN 1 END) as successful_fixes,
                COUNT(CASE WHEN feedback_result = 'failed' THEN 1 END) as failed_fixes,
                AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_resolution_time
            FROM failure_analysis
            WHERE created_at >= %s
        """, (start_date,))

        overall = cursor.fetchone()

        # Error category breakdown
        cursor.execute("""
            SELECT
                error_category,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence
            FROM failure_analysis
            WHERE created_at >= %s
            GROUP BY error_category
            ORDER BY count DESC
        """, (start_date,))

        categories = cursor.fetchall()

        # Daily trend
        cursor.execute("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as failure_count,
                COUNT(CASE WHEN feedback_result = 'success' THEN 1 END) as success_count
            FROM failure_analysis
            WHERE created_at >= %s
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (start_date,))

        trends = cursor.fetchall()

        # Recent failures (last 10)
        cursor.execute("""
            SELECT
                fa.id,
                fa.build_id,
                fa.error_category,
                fa.root_cause,
                fa.confidence_score,
                fa.consecutive_failures,
                fa.feedback_result,
                fa.created_at,
                bm.job_name,
                bm.test_suite
            FROM failure_analysis fa
            LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id
            WHERE fa.created_at >= %s
            ORDER BY fa.created_at DESC
            LIMIT 10
        """, (start_date,))

        recent = cursor.fetchall()

        # Calculate success rate
        success_rate = 0
        if overall['successful_fixes'] or overall['failed_fixes']:
            total_feedback = overall['successful_fixes'] + overall['failed_fixes']
            success_rate = round((overall['successful_fixes'] / total_feedback) * 100, 2)

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'overview': {
                    'total_failures': overall['total_failures'],
                    'unique_builds': overall['unique_builds'],
                    'avg_confidence': round(float(overall['avg_confidence'] or 0), 2),
                    'success_rate': success_rate,
                    'avg_resolution_time_seconds': int(overall['avg_resolution_time'] or 0)
                },
                'categories': [dict(cat) for cat in categories],
                'trends': [dict(t) for t in trends],
                'recent_failures': [dict(r) for r in recent]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/analytics/trends', methods=['GET'])
def get_failure_trends():
    """
    Get detailed failure trends over time
    Supports: daily, weekly, monthly aggregation
    """
    try:
        time_range = request.args.get('time_range', '30d')
        aggregation = request.args.get('aggregation', 'daily')  # daily, weekly, monthly

        days = 30
        if time_range == '7d':
            days = 7
        elif time_range == '90d':
            days = 90

        start_date = datetime.now() - timedelta(days=days)

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if aggregation == 'daily':
            cursor.execute("""
                SELECT
                    DATE(created_at) as period,
                    COUNT(*) as total_failures,
                    COUNT(DISTINCT build_id) as unique_builds,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(CASE WHEN error_category = 'CODE_ERROR' THEN 1 END) as code_errors,
                    COUNT(CASE WHEN error_category = 'TEST_FAILURE' THEN 1 END) as test_failures,
                    COUNT(CASE WHEN error_category = 'INFRA_ERROR' THEN 1 END) as infra_errors,
                    COUNT(CASE WHEN error_category = 'DEPENDENCY_ERROR' THEN 1 END) as dep_errors,
                    COUNT(CASE WHEN error_category = 'CONFIG_ERROR' THEN 1 END) as config_errors
                FROM failure_analysis
                WHERE created_at >= %s
                GROUP BY DATE(created_at)
                ORDER BY period
            """, (start_date,))

        trends = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'trends': [dict(t) for t in trends]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/analytics/patterns', methods=['GET'])
def get_failure_patterns():
    """
    Get identified failure patterns and their frequency
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                pattern_type,
                pattern_description,
                occurrence_count,
                last_seen,
                suggested_fix,
                success_rate
            FROM failure_patterns
            ORDER BY occurrence_count DESC, last_seen DESC
            LIMIT 20
        """)

        patterns = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'patterns': [dict(p) for p in patterns]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== FAILURE DETAILS ENDPOINTS ====================

@app.route('/api/failures', methods=['GET'])
def get_failures():
    """
    Get paginated list of failures with filtering
    Query params: page, limit, category, date_from, date_to
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category', None)
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)

        offset = (page - 1) * limit

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build query
        query = """
            SELECT
                fa.id,
                fa.build_id,
                fa.error_category,
                fa.root_cause,
                fa.fix_recommendation,
                fa.confidence_score,
                fa.consecutive_failures,
                fa.feedback_result,
                fa.created_at,
                bm.job_name,
                bm.test_suite,
                bm.build_url
            FROM failure_analysis fa
            LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id
            WHERE 1=1
        """

        params = []

        if category:
            query += " AND fa.error_category = %s"
            params.append(category)

        if date_from:
            query += " AND fa.created_at >= %s"
            params.append(date_from)

        if date_to:
            query += " AND fa.created_at <= %s"
            params.append(date_to)

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as subquery"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # Get paginated results
        query += " ORDER BY fa.created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        failures = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'failures': [dict(f) for f in failures],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/failures/<build_id>', methods=['GET'])
def get_failure_details(build_id):
    """
    Get complete failure details including full context
    Combines PostgreSQL metadata with MongoDB full logs
    """
    try:
        # Get PostgreSQL data
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                fa.*,
                bm.job_name,
                bm.test_suite,
                bm.build_url,
                bm.jenkins_url,
                bm.test_status
            FROM failure_analysis fa
            LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id
            WHERE fa.build_id = %s
            ORDER BY fa.created_at DESC
            LIMIT 1
        """, (build_id,))

        failure = cursor.fetchone()

        if not failure:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Failure not found'
            }), 404

        # Get feedback history
        cursor.execute("""
            SELECT *
            FROM user_feedback
            WHERE analysis_id = %s
            ORDER BY created_at DESC
        """, (failure['id'],))

        feedback_list = cursor.fetchall()

        cursor.close()
        conn.close()

        # Get MongoDB full context
        mongodb = get_mongodb_connection()

        console_log = mongodb.console_logs.find_one({'build_id': build_id})
        error_details = mongodb.error_details.find_one({'build_id': build_id})
        test_results = mongodb.test_results.find_one({'build_id': build_id})
        system_info = mongodb.system_info.find_one({'build_id': build_id})

        return jsonify({
            'status': 'success',
            'data': {
                'failure': dict(failure),
                'feedback': [dict(f) for f in feedback_list],
                'full_context': {
                    'console_log': console_log['log'] if console_log else None,
                    'error_details': error_details if error_details else None,
                    'test_results': test_results if test_results else None,
                    'system_info': system_info if system_info else None
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== MANUAL TRIGGER ENDPOINTS ====================

@app.route('/api/trigger/manual', methods=['POST'])
def trigger_manual_analysis():
    """
    Manual trigger endpoint for dashboard
    Proxies request to manual_trigger_api.py
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('build_id'):
            return jsonify({
                'status': 'error',
                'message': 'build_id is required'
            }), 400

        # Forward to manual trigger API
        response = requests.post(
            f"{MANUAL_TRIGGER_API}/api/trigger-analysis",
            json=data,
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/trigger/history', methods=['GET'])
def get_trigger_history():
    """
    Get manual trigger history
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))

        offset = (page - 1) * limit

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get total count
        cursor.execute("SELECT COUNT(*) as total FROM manual_trigger_log")
        total = cursor.fetchone()['total']

        # Get paginated results
        cursor.execute("""
            SELECT *
            FROM manual_trigger_log
            ORDER BY triggered_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        triggers = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'triggers': [dict(t) for t in triggers],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'pages': (total + limit - 1) // limit
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== FEEDBACK ENDPOINTS ====================

@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """
    Submit feedback for AI recommendation
    Proxies request to manual_trigger_api.py
    """
    try:
        data = request.get_json()

        # Forward to manual trigger API
        response = requests.post(
            f"{MANUAL_TRIGGER_API}/api/feedback",
            json=data,
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """
    Get recent feedback across all builds
    """
    try:
        limit = int(request.args.get('limit', 20))

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                uf.*,
                fa.build_id,
                fa.error_category,
                fa.root_cause
            FROM user_feedback uf
            JOIN failure_analysis fa ON uf.analysis_id = fa.id
            ORDER BY uf.created_at DESC
            LIMIT %s
        """, (limit,))

        feedback = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'feedback': [dict(f) for f in feedback]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== AI MODEL METRICS ENDPOINTS ====================

@app.route('/api/metrics/model', methods=['GET'])
def get_model_metrics():
    """
    Get AI model performance metrics
    """
    try:
        time_range = request.args.get('time_range', '7d')

        days = 7
        if time_range == '30d':
            days = 30
        elif time_range == '90d':
            days = 90

        start_date = datetime.now() - timedelta(days=days)

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT *
            FROM ai_model_metrics
            WHERE date >= %s
            ORDER BY date
        """, (start_date,))

        metrics = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'metrics': [dict(m) for m in metrics]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== REAL-TIME STATUS ENDPOINT ====================

@app.route('/api/status/live', methods=['GET'])
def get_live_status():
    """
    Get real-time system status
    Returns: Recent activity, service health, current load
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Last 24 hours activity
        yesterday = datetime.now() - timedelta(days=1)

        cursor.execute("""
            SELECT
                COUNT(*) as failures_24h,
                COUNT(CASE WHEN feedback_result = 'success' THEN 1 END) as successes_24h,
                AVG(confidence_score) as avg_confidence_24h
            FROM failure_analysis
            WHERE created_at >= %s
        """, (yesterday,))

        activity = cursor.fetchone()

        # Most recent failure
        cursor.execute("""
            SELECT
                fa.build_id,
                fa.error_category,
                fa.created_at,
                bm.job_name
            FROM failure_analysis fa
            LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id
            ORDER BY fa.created_at DESC
            LIMIT 1
        """)

        latest = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'activity_24h': dict(activity) if activity else {},
                'latest_failure': dict(latest) if latest else None,
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Check PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()

        # Check MongoDB
        mongodb = get_mongodb_connection()
        mongodb.command('ping')

        return jsonify({
            'status': 'healthy',
            'service': 'dashboard-api',
            'port': 5005,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


if __name__ == '__main__':
    print("=" * 60)
    print("Dashboard Backend API Service")
    print("=" * 60)
    print(f"Port: 5005")
    print(f"CORS: Enabled")
    print(f"PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
    print(f"MongoDB: {MONGODB_URI}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                    - Health check")
    print("  GET  /api/analytics/summary     - Analytics summary")
    print("  GET  /api/analytics/trends      - Failure trends")
    print("  GET  /api/analytics/patterns    - Failure patterns")
    print("  GET  /api/failures              - List failures (paginated)")
    print("  GET  /api/failures/<build_id>   - Failure details")
    print("  POST /api/trigger/manual        - Manual trigger")
    print("  GET  /api/trigger/history       - Trigger history")
    print("  POST /api/feedback/submit       - Submit feedback")
    print("  GET  /api/feedback/recent       - Recent feedback")
    print("  GET  /api/metrics/model         - AI model metrics")
    print("  GET  /api/status/live           - Real-time status")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=5005, debug=True)
