"""
Enhanced Dashboard API with Full System Monitoring
===================================================

Shows:
- Test failures from MongoDB
- AI analysis from PostgreSQL
- System health status
- Component connectivity
- Pipeline flow status
- Recent activity logs
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
from pinecone import Pinecone
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging
import requests
from bson import ObjectId

# Load environment from master config (or rely on calling script)
# Only load if not already loaded by parent script
if not os.getenv('POSTGRES_HOST'):
    load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB', 'ddn_tests')
mongo_client = None
mongo_db = None

# PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

# Pinecone - Dual-Index Architecture
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_KNOWLEDGE_INDEX = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')
PINECONE_FAILURES_INDEX = os.getenv('PINECONE_FAILURES_INDEX', 'ddn-error-library')

# AI Service
AI_SERVICE_URL = 'http://localhost:5000'

def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, mongo_db
    try:
        if not MONGODB_URI:
            logger.error("❌ MONGODB_URI not configured. Please set MONGODB_URI to your MongoDB Atlas connection string.")
            return False
        mongo_client = MongoClient(MONGODB_URI)
        mongo_db = mongo_client[MONGODB_DB]
        # Test connection
        mongo_client.server_info()
        logger.info("✓ MongoDB connected")
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {str(e)}")
        return False

def get_postgres_connection():
    """Get PostgreSQL connection"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {str(e)}")
        return None

# ============================================================================
# SYSTEM STATUS & HEALTH
# ============================================================================

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """
    Get complete system status
    Returns health of all components
    """
    status = {
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }

    # 1. MongoDB Status
    try:
        mongo_client.server_info()
        failure_count = mongo_db['test_failures'].count_documents({})
        status['components']['mongodb'] = {
            'status': 'healthy',
            'connected': True,
            'total_failures': failure_count,
            'last_check': datetime.utcnow().isoformat()
        }
    except Exception as e:
        status['components']['mongodb'] = {
            'status': 'error',
            'connected': False,
            'error': str(e)[:200]
        }

    # 2. PostgreSQL Status
    try:
        conn = get_postgres_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM failure_analysis")
            analysis_count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            status['components']['postgresql'] = {
                'status': 'healthy',
                'connected': True,
                'total_analyses': analysis_count,
                'last_check': datetime.utcnow().isoformat()
            }
        else:
            status['components']['postgresql'] = {
                'status': 'error',
                'connected': False,
                'error': 'Connection failed'
            }
    except Exception as e:
        status['components']['postgresql'] = {
            'status': 'error',
            'connected': False,
            'error': str(e)[:200]
        }

    # 3. Pinecone Status - Dual-Index Architecture
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Check Knowledge Index (Source A)
        knowledge_index = pc.Index(PINECONE_KNOWLEDGE_INDEX)
        knowledge_stats = knowledge_index.describe_index_stats()

        # Check Error Library (Source B)
        failures_index = pc.Index(PINECONE_FAILURES_INDEX)
        failures_stats = failures_index.describe_index_stats()

        status['components']['pinecone_knowledge'] = {
            'status': 'healthy',
            'connected': True,
            'index_name': PINECONE_KNOWLEDGE_INDEX,
            'purpose': 'Error Documentation (Source A)',
            'total_vectors': knowledge_stats.total_vector_count,
            'dimension': knowledge_stats.dimension,
            'last_check': datetime.utcnow().isoformat()
        }

        status['components']['pinecone_failures'] = {
            'status': 'healthy',
            'connected': True,
            'index_name': PINECONE_FAILURES_INDEX,
            'purpose': 'Past Error Cases (Source B)',
            'total_vectors': failures_stats.total_vector_count,
            'dimension': failures_stats.dimension,
            'last_check': datetime.utcnow().isoformat()
        }
    except Exception as e:
        status['components']['pinecone'] = {
            'status': 'error',
            'connected': False,
            'error': str(e)[:200]
        }

    # 4. AI Service Status
    try:
        response = requests.get(f'{AI_SERVICE_URL}/api/health', timeout=5)
        if response.status_code == 200:
            ai_health = response.json()
            status['components']['ai_service'] = {
                'status': 'healthy',
                'connected': True,
                'gemini_available': ai_health.get('gemini_available', False),
                'openai_available': ai_health.get('openai_available', False),
                'rag_enabled': ai_health.get('rag_enabled', False),
                'last_check': datetime.utcnow().isoformat()
            }
        else:
            status['components']['ai_service'] = {
                'status': 'degraded',
                'connected': True,
                'http_status': response.status_code
            }
    except Exception as e:
        status['components']['ai_service'] = {
            'status': 'error',
            'connected': False,
            'error': str(e)[:200]
        }

    # Overall system health
    all_healthy = all(
        comp.get('status') == 'healthy'
        for comp in status['components'].values()
    )
    status['overall_status'] = 'healthy' if all_healthy else 'degraded'

    return jsonify(status)

# ============================================================================
# PIPELINE FLOW MONITORING
# ============================================================================

@app.route('/api/pipeline/flow', methods=['GET'])
def get_pipeline_flow():
    """
    Show complete pipeline flow with recent activity
    """
    flow = {
        'timestamp': datetime.utcnow().isoformat(),
        'stages': []
    }

    # Stage 1: Test Execution (Jenkins)
    recent_failures = list(mongo_db['test_failures'].find(
        {},
        {'test_name': 1, 'timestamp': 1, 'build_number': 1}
    ).sort('timestamp', -1).limit(5))

    flow['stages'].append({
        'stage': 1,
        'name': 'Test Execution (Jenkins)',
        'status': 'active' if recent_failures else 'idle',
        'recent_activity': [
            {
                'test': f['test_name'],
                'build': f.get('build_number', 'unknown'),
                'timestamp': f['timestamp'].isoformat() if isinstance(f.get('timestamp'), datetime) else str(f.get('timestamp'))
            }
            for f in recent_failures
        ]
    })

    # Stage 2: MongoDB Storage
    total_failures = mongo_db['test_failures'].count_documents({})
    last_24h = mongo_db['test_failures'].count_documents({
        'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)}
    })

    flow['stages'].append({
        'stage': 2,
        'name': 'MongoDB Storage',
        'status': 'active',
        'total_failures': total_failures,
        'last_24h': last_24h
    })

    # Stage 3: AI Analysis
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE analyzed_at >= NOW() - INTERVAL '24 hours') as last_24h,
                AVG(confidence_score) as avg_confidence
            FROM failure_analysis
        """)
        ai_stats = cursor.fetchone()
        cursor.close()
        conn.close()

        flow['stages'].append({
            'stage': 3,
            'name': 'AI Analysis',
            'status': 'active',
            'total_analyzed': ai_stats['total'],
            'last_24h': ai_stats['last_24h'],
            'avg_confidence': round(float(ai_stats['avg_confidence'] or 0), 2)
        })
    except:
        flow['stages'].append({
            'stage': 3,
            'name': 'AI Analysis',
            'status': 'error'
        })

    # Stage 4: Dashboard Display
    flow['stages'].append({
        'stage': 4,
        'name': 'Dashboard Display',
        'status': 'active',
        'viewing_now': True
    })

    return jsonify(flow)

# ============================================================================
# TEST FAILURES (Enhanced)
# ============================================================================

@app.route('/api/failures', methods=['GET'])
def get_failures():
    """Get test failures with AI analysis and validation status (Task 0-HITL.15)"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        build_number = request.args.get('build_number')
        feedback_status = request.args.get('feedback_status')  # Task 0-HITL.15: New filter
        category = request.args.get('category')
        search = request.args.get('search')

        # Build query
        query = {}
        if build_number:
            query['build_number'] = build_number

        # Get failures from MongoDB
        failures = list(mongo_db['test_failures'].find(query)
                       .sort('timestamp', -1)
                       .skip(skip)
                       .limit(limit))

        # Convert ObjectId to string
        for failure in failures:
            failure['_id'] = str(failure['_id'])
            if isinstance(failure.get('timestamp'), datetime):
                failure['timestamp'] = failure['timestamp'].isoformat()

        # Get AI analysis AND acceptance tracking for each failure from PostgreSQL (Task 0-HITL.15)
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Filter failures based on feedback_status before processing (if filter applied)
            filtered_failures = []

            for failure in failures:
                # Task 0-HITL.15: Join with acceptance_tracking to get validation status
                cursor.execute("""
                    SELECT
                        fa.id as analysis_id,
                        fa.classification,
                        fa.root_cause,
                        fa.severity,
                        fa.recommendation,
                        fa.confidence_score,
                        fa.analyzed_at,
                        fa.ai_model,
                        fa.github_files,
                        fa.github_code_included,
                        at.validation_status as feedback_status,
                        at.refinement_count,
                        at.final_acceptance,
                        at.validator_name,
                        at.validator_email,
                        at.feedback_comment,
                        at.validated_at as feedback_timestamp
                    FROM failure_analysis fa
                    LEFT JOIN acceptance_tracking at ON fa.id = at.analysis_id
                    WHERE fa.mongodb_failure_id = %s
                    ORDER BY fa.analyzed_at DESC, at.created_at DESC
                    LIMIT 1
                """, (failure['_id'],))

                analysis = cursor.fetchone()
                if analysis:
                    failure['ai_analysis'] = {
                        'classification': analysis['classification'],
                        'root_cause': analysis['root_cause'],
                        'severity': analysis['severity'],
                        'recommendation': analysis['recommendation'],
                        'confidence_score': float(analysis['confidence_score']) if analysis['confidence_score'] else None,
                        'analyzed_at': analysis['analyzed_at'].isoformat() if analysis['analyzed_at'] else None,
                        'ai_model': analysis['ai_model'],
                        'github_files': analysis['github_files'],
                        'github_code_included': analysis['github_code_included']
                    }

                    # Add acceptance tracking fields (Task 0-HITL.15)
                    failure['feedback_status'] = analysis['feedback_status'] or 'pending'
                    failure['refinement_count'] = analysis['refinement_count'] or 0
                    failure['final_acceptance'] = analysis['final_acceptance']
                    failure['validator_name'] = analysis['validator_name']
                    failure['validator_email'] = analysis['validator_email']
                    failure['feedback_comment'] = analysis['feedback_comment']
                    failure['feedback_timestamp'] = analysis['feedback_timestamp'].isoformat() if analysis['feedback_timestamp'] else None
                else:
                    failure['ai_analysis'] = None
                    failure['feedback_status'] = 'pending'
                    failure['refinement_count'] = 0
                    failure['final_acceptance'] = None
                    failure['validator_name'] = None
                    failure['validator_email'] = None
                    failure['feedback_comment'] = None
                    failure['feedback_timestamp'] = None

                # Task 0-HITL.15: Apply feedback_status filter
                if feedback_status:
                    if failure['feedback_status'] == feedback_status:
                        filtered_failures.append(failure)
                else:
                    filtered_failures.append(failure)

            cursor.close()
            conn.close()

            # Use filtered failures
            failures = filtered_failures

        except Exception as e:
            logger.error(f"Error fetching AI analysis: {str(e)}")
            # Continue without AI analysis if PostgreSQL fails

        total_count = mongo_db['test_failures'].count_documents(query)

        return jsonify({
            'status': 'success',
            'data': {
                'failures': failures,
                'total': total_count,
                'limit': limit,
                'skip': skip
            }
        })

    except Exception as e:
        logger.error(f"Error fetching failures: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# SINGLE FAILURE DETAILS
# ============================================================================

@app.route('/api/failures/<failure_id>', methods=['GET'])
def get_failure_details(failure_id):
    """Get detailed information for a single failure"""
    try:
        from bson.objectid import ObjectId

        # Get failure from MongoDB
        failure = mongo_db['test_failures'].find_one({'_id': ObjectId(failure_id)})

        if not failure:
            return jsonify({'error': 'Failure not found'}), 404

        # Convert ObjectId to string
        failure['_id'] = str(failure['_id'])
        if isinstance(failure.get('timestamp'), datetime):
            failure['timestamp'] = failure['timestamp'].isoformat()

        # Get AI analysis from PostgreSQL
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Task 0E.6: Include GitHub files in query
            cursor.execute("""
                SELECT
                    classification,
                    root_cause,
                    severity,
                    recommendation,
                    confidence_score,
                    analyzed_at,
                    ai_model,
                    similar_cases,
                    github_files,
                    github_code_included
                FROM failure_analysis
                WHERE mongodb_failure_id = %s
                ORDER BY analyzed_at DESC
                LIMIT 1
            """, (failure_id,))

            analysis = cursor.fetchone()
            if analysis:
                failure['ai_analysis'] = dict(analysis)
                if isinstance(analysis.get('analyzed_at'), datetime):
                    failure['ai_analysis']['analyzed_at'] = analysis['analyzed_at'].isoformat()
            else:
                failure['ai_analysis'] = None

            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error fetching AI analysis for {failure_id}: {str(e)}")
            failure['ai_analysis'] = None

        return jsonify({
            'failure': failure
        })

    except Exception as e:
        logger.error(f"Error fetching failure details: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# AI ANALYSIS DETAILS
# ============================================================================

@app.route('/api/analysis/<failure_id>', methods=['GET'])
def get_analysis_details(failure_id):
    """Get detailed AI analysis for a failure"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get analysis
        cursor.execute("""
            SELECT *
            FROM failure_analysis
            WHERE mongodb_failure_id = %s
            ORDER BY analyzed_at DESC
            LIMIT 1
        """, (failure_id,))

        analysis = cursor.fetchone()

        if analysis:
            # Convert datetime
            if isinstance(analysis['analyzed_at'], datetime):
                analysis['analyzed_at'] = analysis['analyzed_at'].isoformat()

            # Get similar failures
            cursor.execute("""
                SELECT
                    sf.similar_failure_id,
                    sf.similarity_score,
                    fa.classification,
                    fa.root_cause
                FROM similar_failures sf
                LEFT JOIN failure_analysis fa ON sf.similar_failure_id = fa.mongodb_failure_id
                WHERE sf.failure_id = %s
                ORDER BY sf.similarity_score DESC
                LIMIT 5
            """, (analysis['id'],))

            similar = cursor.fetchall()
            analysis['similar_failures'] = [dict(s) for s in similar]

        cursor.close()
        conn.close()

        if analysis:
            return jsonify(dict(analysis))
        else:
            return jsonify({'error': 'Analysis not found'}), 404

    except Exception as e:
        logger.error(f"Error fetching analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# STATISTICS & METRICS
# ============================================================================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = {}

        # MongoDB stats
        stats['total_failures'] = mongo_db['test_failures'].count_documents({})
        stats['failures_last_24h'] = mongo_db['test_failures'].count_documents({
            'timestamp': {'$gte': datetime.utcnow() - timedelta(hours=24)}
        })
        stats['failures_last_7d'] = mongo_db['test_failures'].count_documents({
            'timestamp': {'$gte': datetime.utcnow() - timedelta(days=7)}
        })

        # PostgreSQL stats
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    COUNT(*) as total_analyzed,
                    COUNT(*) FILTER (WHERE analyzed_at >= NOW() - INTERVAL '24 hours') as analyzed_24h,
                    AVG(confidence_score) as avg_confidence,
                    COUNT(DISTINCT classification) as unique_classifications
                FROM failure_analysis
            """)
            pg_stats = cursor.fetchone()
            stats.update(dict(pg_stats))

            # Classification breakdown
            cursor.execute("""
                SELECT classification, COUNT(*) as count
                FROM failure_analysis
                GROUP BY classification
                ORDER BY count DESC
            """)
            stats['classification_breakdown'] = [dict(r) for r in cursor.fetchall()]

            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"PostgreSQL stats error: {str(e)}")
            stats['postgresql_error'] = str(e)[:200]

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ACTIVITY LOG
# ============================================================================

@app.route('/api/activity', methods=['GET'])
def get_activity_log():
    """Get recent activity across all systems"""
    try:
        limit = int(request.args.get('limit', 20))
        activities = []

        # Recent test failures from MongoDB
        recent_failures = list(mongo_db['test_failures'].find(
            {},
            {'test_name': 1, 'timestamp': 1, 'build_number': 1, 'error_message': 1}
        ).sort('timestamp', -1).limit(limit))

        for f in recent_failures:
            activities.append({
                'type': 'test_failure',
                'timestamp': f['timestamp'].isoformat() if isinstance(f.get('timestamp'), datetime) else str(f.get('timestamp')),
                'description': f'Test failed: {f["test_name"]}',
                'details': {
                    'test': f['test_name'],
                    'build': f.get('build_number'),
                    'error': f.get('error_message', '')[:100]
                }
            })

        # Recent AI analyses from PostgreSQL
        try:
            conn = get_postgres_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    mongodb_failure_id,
                    classification,
                    analyzed_at,
                    confidence_score
                FROM failure_analysis
                ORDER BY analyzed_at DESC
                LIMIT %s
            """, (limit,))

            analyses = cursor.fetchall()
            for a in analyses:
                activities.append({
                    'type': 'ai_analysis',
                    'timestamp': a['analyzed_at'].isoformat() if isinstance(a['analyzed_at'], datetime) else str(a['analyzed_at']),
                    'description': f'AI analyzed failure as {a["classification"]}',
                    'details': {
                        'classification': a['classification'],
                        'confidence': round(float(a['confidence_score'] or 0), 2),
                        'failure_id': a['mongodb_failure_id']
                    }
                })

            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Activity log PostgreSQL error: {str(e)}")

        # Sort all activities by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)

        return jsonify({
            'activities': activities[:limit],
            'total': len(activities)
        })

    except Exception as e:
        logger.error(f"Error getting activity log: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ANALYTICS & FEEDBACK
# ============================================================================

@app.route('/api/analytics/acceptance-rate', methods=['GET'])
def get_acceptance_rate():
    """
    Get AI analysis acceptance rate statistics

    Query params:
    - time_range: '7d', '30d', '90d' (default: '30d')
    - start_date: ISO format start date (optional)
    - end_date: ISO format end date (optional)
    """
    try:
        # Get time range parameter
        time_range = request.args.get('time_range', '30d')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Calculate date range
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
        else:
            # Parse time_range
            days_map = {'7d': 7, '30d': 30, '90d': 90}
            days = days_map.get(time_range, 30)
            end_dt = datetime.utcnow()
            start_dt = end_dt - timedelta(days=days)

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Query feedback data
            cursor.execute("""
                SELECT
                    validation_status,
                    COUNT(*) as count
                FROM user_feedback
                WHERE feedback_timestamp >= %s AND feedback_timestamp <= %s
                GROUP BY validation_status
            """, (start_dt, end_dt))

            status_counts = {row['validation_status']: row['count'] for row in cursor.fetchall()}

            # Calculate totals
            total = sum(status_counts.values())
            accepted = status_counts.get('accepted', 0)
            rejected = status_counts.get('rejected', 0)
            refining = status_counts.get('refining', 0)
            refined = status_counts.get('refined', 0)
            pending = status_counts.get('pending', 0)

            # Calculate percentages
            acceptance_rate = (accepted / total * 100) if total > 0 else 0
            rejection_rate = (rejected / total * 100) if total > 0 else 0
            refinement_rate = ((refining + refined) / total * 100) if total > 0 else 0

            # Get daily trend
            cursor.execute("""
                SELECT
                    DATE(feedback_timestamp) as date,
                    validation_status,
                    COUNT(*) as count
                FROM user_feedback
                WHERE feedback_timestamp >= %s AND feedback_timestamp <= %s
                GROUP BY DATE(feedback_timestamp), validation_status
                ORDER BY date
            """, (start_dt, end_dt))

            daily_data = {}
            for row in cursor.fetchall():
                date_str = str(row['date'])
                if date_str not in daily_data:
                    daily_data[date_str] = {'accepted': 0, 'rejected': 0, 'refining': 0, 'refined': 0}
                daily_data[date_str][row['validation_status']] = row['count']

            # Convert to list format for charts
            trend = [
                {
                    'date': date,
                    'accepted': counts['accepted'],
                    'rejected': counts['rejected'],
                    'refining': counts['refining'],
                    'refined': counts['refined'],
                    'total': sum(counts.values())
                }
                for date, counts in sorted(daily_data.items())
            ]

            cursor.close()
            conn.close()

            return jsonify({
                'time_range': {
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat()
                },
                'summary': {
                    'total_feedback': total,
                    'accepted': accepted,
                    'rejected': rejected,
                    'refining': refining,
                    'refined': refined,
                    'pending': pending,
                    'acceptance_rate': round(acceptance_rate, 2),
                    'rejection_rate': round(rejection_rate, 2),
                    'refinement_rate': round(refinement_rate, 2)
                },
                'trend': trend
            })

        except Exception as e:
            logger.error(f"Acceptance rate query error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        logger.error(f"Acceptance rate error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/refinement-stats', methods=['GET'])
def get_refinement_stats():
    """
    Get refinement effectiveness statistics

    Query params:
    - time_range: '7d', '30d', '90d' (default: '30d')
    """
    try:
        # Get time range parameter
        time_range = request.args.get('time_range', '30d')

        # Parse time_range
        days_map = {'7d': 7, '30d': 30, '90d': 90}
        days = days_map.get(time_range, 30)
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=days)

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get refinement stats
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT failure_id) as total_refined,
                    AVG(iteration_number) as avg_refinement_count,
                    MAX(iteration_number) as max_refinement_count
                FROM refinement_history
                WHERE refinement_timestamp >= %s AND refinement_timestamp <= %s
            """, (start_dt, end_dt))

            stats = cursor.fetchone()

            # Get final acceptance rate for refined failures
            cursor.execute("""
                SELECT
                    COUNT(CASE WHEN uf.validation_status = 'accepted' THEN 1 END) as accepted_after_refinement,
                    COUNT(*) as total_refined_with_feedback
                FROM refinement_history rh
                JOIN user_feedback uf ON rh.failure_id = uf.failure_id
                WHERE rh.refinement_timestamp >= %s AND rh.refinement_timestamp <= %s
                AND uf.feedback_timestamp > rh.refinement_timestamp
            """, (start_dt, end_dt))

            effectiveness = cursor.fetchone()

            # Calculate effectiveness percentage
            total_refined_with_feedback = effectiveness['total_refined_with_feedback'] or 0
            accepted_after_refinement = effectiveness['accepted_after_refinement'] or 0
            effectiveness_rate = (accepted_after_refinement / total_refined_with_feedback * 100) if total_refined_with_feedback > 0 else 0

            # Get improvement in confidence scores
            cursor.execute("""
                SELECT
                    AVG(confidence_improvement) as avg_confidence_improvement
                FROM (
                    SELECT
                        rh.failure_id,
                        (refined_confidence_score - original_confidence_score) as confidence_improvement
                    FROM refinement_history rh
                    WHERE rh.refinement_timestamp >= %s AND rh.refinement_timestamp <= %s
                    AND refined_confidence_score IS NOT NULL
                    AND original_confidence_score IS NOT NULL
                ) AS improvements
            """, (start_dt, end_dt))

            confidence_data = cursor.fetchone()
            avg_confidence_improvement = confidence_data['avg_confidence_improvement'] or 0

            cursor.close()
            conn.close()

            return jsonify({
                'time_range': {
                    'start': start_dt.isoformat(),
                    'end': end_dt.isoformat()
                },
                'summary': {
                    'total_refined': stats['total_refined'] or 0,
                    'avg_refinement_count': round(float(stats['avg_refinement_count'] or 0), 2),
                    'max_refinement_count': stats['max_refinement_count'] or 0,
                    'accepted_after_refinement': accepted_after_refinement,
                    'total_refined_with_feedback': total_refined_with_feedback,
                    'effectiveness_rate': round(effectiveness_rate, 2),
                    'avg_confidence_improvement': round(float(avg_confidence_improvement) * 100, 2)
                }
            })

        except Exception as e:
            logger.error(f"Refinement stats query error: {str(e)}")
            return jsonify({'error': str(e)}), 500

    except Exception as e:
        logger.error(f"Refinement stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PHASE B: AUTOMATED CODE FIXING ENDPOINTS
# ============================================================================

@app.route('/api/fixes/approve', methods=['POST'])
def approve_fix():
    """
    Approve a code fix and trigger PR creation

    Request body:
    {
        "analysis_id": 123,
        "approved_by_name": "John Doe",
        "approved_by_email": "john@example.com"
    }

    Returns:
    {
        "success": true,
        "pr_number": 456,
        "pr_url": "https://github.com/...",
        "fix_application_id": 789
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        analysis_id = data.get('analysis_id')
        approved_by_name = data.get('approved_by_name', 'Unknown')
        approved_by_email = data.get('approved_by_email', 'unknown@example.com')

        if not analysis_id:
            return jsonify({'success': False, 'error': 'analysis_id required'}), 400

        # Import code fix service
        import sys
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from code_fix_automation import get_code_fix_service

        # Apply fix
        service = get_code_fix_service()
        result = service.apply_approved_fix(
            analysis_id=analysis_id,
            approved_by_name=approved_by_name,
            approved_by_email=approved_by_email
        )

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"Error approving fix: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fixes/reject', methods=['POST'])
def reject_fix():
    """
    Reject a code fix

    Request body:
    {
        "analysis_id": 123,
        "rejected_by_name": "Jane Smith",
        "rejected_by_email": "jane@example.com",
        "reason": "Not confident in this fix"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        analysis_id = data.get('analysis_id')
        rejected_by_name = data.get('rejected_by_name', 'Unknown')
        rejected_by_email = data.get('rejected_by_email', 'unknown@example.com')
        reason = data.get('reason', 'No reason provided')

        if not analysis_id:
            return jsonify({'success': False, 'error': 'analysis_id required'}), 400

        # Log rejection to database (optional)
        conn = get_postgres_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO code_fix_applications (
                        analysis_id,
                        build_id,
                        approved_by_name,
                        approved_by_email,
                        status,
                        rollback_reason,
                        approved_at
                    )
                    SELECT
                        id,
                        build_id,
                        %s,
                        %s,
                        'failed',
                        %s,
                        CURRENT_TIMESTAMP
                    FROM failure_analysis
                    WHERE id = %s
                """, (rejected_by_name, rejected_by_email, f"Rejected: {reason}", analysis_id))

                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                logger.error(f"Failed to log rejection: {str(e)}")

        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Fix rejected successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error rejecting fix: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fixes/<int:fix_id>/status', methods=['GET'])
def get_fix_status(fix_id):
    """
    Get status of a fix application

    Returns PR status, test results, etc.
    """
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                id,
                analysis_id,
                build_id,
                branch_name,
                pr_number,
                pr_url,
                pr_title,
                pr_state,
                status,
                approved_by_name,
                approved_at,
                time_to_pr_creation_ms,
                files_changed,
                test_results,
                error_category,
                ai_confidence_score,
                created_at,
                updated_at
            FROM code_fix_applications
            WHERE id = %s
        """, (fix_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if not row:
            return jsonify({'success': False, 'error': 'Fix not found'}), 404

        return jsonify({
            'success': True,
            'fix': {
                'id': row[0],
                'analysis_id': row[1],
                'build_id': row[2],
                'branch_name': row[3],
                'pr_number': row[4],
                'pr_url': row[5],
                'pr_title': row[6],
                'pr_state': row[7],
                'status': row[8],
                'approved_by_name': row[9],
                'approved_at': row[10].isoformat() if row[10] else None,
                'time_to_pr_creation_ms': row[11],
                'files_changed': row[12],
                'test_results': row[13],
                'error_category': row[14],
                'ai_confidence_score': float(row[15]) if row[15] else None,
                'created_at': row[16].isoformat() if row[16] else None,
                'updated_at': row[17].isoformat() if row[17] else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error getting fix status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fixes/history', methods=['GET'])
def get_fix_history():
    """
    Get history of all fix applications

    Query params:
    - limit: Max results (default: 50)
    - status: Filter by status
    - category: Filter by error category
    """
    try:
        limit = int(request.args.get('limit', 50))
        status_filter = request.args.get('status')
        category_filter = request.args.get('category')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()

        # Build query
        query = """
            SELECT
                id,
                analysis_id,
                build_id,
                branch_name,
                pr_number,
                pr_url,
                status,
                approved_by_name,
                approved_at,
                error_category,
                error_type,
                ai_confidence_score,
                success,
                created_at
            FROM code_fix_applications
            WHERE 1=1
        """

        params = []

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        if category_filter:
            query += " AND error_category = %s"
            params.append(category_filter)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        fixes = []
        for row in rows:
            fixes.append({
                'id': row[0],
                'analysis_id': row[1],
                'build_id': row[2],
                'branch_name': row[3],
                'pr_number': row[4],
                'pr_url': row[5],
                'status': row[6],
                'approved_by_name': row[7],
                'approved_at': row[8].isoformat() if row[8] else None,
                'error_category': row[9],
                'error_type': row[10],
                'ai_confidence_score': float(row[11]) if row[11] else None,
                'success': row[12],
                'created_at': row[13].isoformat() if row[13] else None
            })

        return jsonify({
            'success': True,
            'count': len(fixes),
            'fixes': fixes
        }), 200

    except Exception as e:
        logger.error(f"Error getting fix history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fixes/rollback', methods=['POST'])
def rollback_fix():
    """
    Rollback a fix application (close PR, mark as reverted)

    Request body:
    {
        "fix_id": 789,
        "reason": "Tests failed",
        "rollback_by": "John Doe"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        fix_id = data.get('fix_id')
        reason = data.get('reason', 'No reason provided')
        rollback_by = data.get('rollback_by', 'Unknown')

        if not fix_id:
            return jsonify({'success': False, 'error': 'fix_id required'}), 400

        # Get fix details
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        cursor.execute("""
            SELECT pr_number, status
            FROM code_fix_applications
            WHERE id = %s
        """, (fix_id,))

        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Fix not found'}), 404

        pr_number = row[0]
        current_status = row[1]

        # Close PR if exists
        if pr_number:
            try:
                from github_client import get_github_client
                github_client = get_github_client()
                close_result = github_client.close_pull_request(pr_number)

                if not close_result.success:
                    logger.warning(f"Failed to close PR #{pr_number}: {close_result.error}")
            except Exception as e:
                logger.error(f"Error closing PR: {str(e)}")

        # Update fix status to reverted
        cursor.execute("""
            UPDATE code_fix_applications
            SET status = 'reverted',
                rollback_reason = %s,
                rollback_at = CURRENT_TIMESTAMP,
                rollback_by = %s,
                rollback_type = 'manual',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (reason, rollback_by, fix_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'fix_id': fix_id,
            'pr_number': pr_number,
            'message': 'Fix rolled back successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error rolling back fix: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/fixes/analytics', methods=['GET'])
def get_fix_analytics():
    """
    Get fix success analytics

    Returns success rates by category, time metrics, etc.
    """
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()

        # Overall stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_fixes,
                COUNT(*) FILTER (WHERE success = TRUE) as successful,
                COUNT(*) FILTER (WHERE success = FALSE) as failed,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'pr_created') as pr_created,
                COUNT(*) FILTER (WHERE status = 'merged') as merged,
                COUNT(*) FILTER (WHERE status = 'reverted') as reverted,
                AVG(time_to_pr_creation_ms) as avg_time_to_pr_ms,
                AVG(time_to_merge_ms) FILTER (WHERE time_to_merge_ms IS NOT NULL) as avg_time_to_merge_ms
            FROM code_fix_applications
        """)

        overall_row = cursor.fetchone()

        # By category
        cursor.execute("""
            SELECT
                error_category,
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE success = TRUE) as successful,
                ROUND(100.0 * COUNT(*) FILTER (WHERE success = TRUE) / COUNT(*), 2) as success_rate
            FROM code_fix_applications
            WHERE success IS NOT NULL
            GROUP BY error_category
            ORDER BY total DESC
        """)

        category_rows = cursor.fetchall()

        cursor.close()
        conn.close()

        # Build response
        categories = []
        for row in category_rows:
            categories.append({
                'category': row[0],
                'total': row[1],
                'successful': row[2],
                'success_rate': float(row[3]) if row[3] else 0
            })

        return jsonify({
            'success': True,
            'overall': {
                'total_fixes': overall_row[0] or 0,
                'successful': overall_row[1] or 0,
                'failed': overall_row[2] or 0,
                'pending': overall_row[3] or 0,
                'pr_created': overall_row[4] or 0,
                'merged': overall_row[5] or 0,
                'reverted': overall_row[6] or 0,
                'avg_time_to_pr_ms': int(overall_row[7]) if overall_row[7] else 0,
                'avg_time_to_merge_ms': int(overall_row[8]) if overall_row[8] else 0
            },
            'by_category': categories
        }), 200

    except Exception as e:
        logger.error(f"Error getting fix analytics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'dashboard-api-full',
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# INITIALIZATION & STARTUP
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("DDN Dashboard API (Full System Monitoring)")
    logger.info("=" * 60)

    # Initialize MongoDB
    if not init_mongodb():
        logger.error("Failed to connect to MongoDB")
        exit(1)

    # Test PostgreSQL
    conn = get_postgres_connection()
    if conn:
        logger.info("✓ PostgreSQL connected")
        conn.close()
    else:
        logger.warning("⚠ PostgreSQL connection issue")

    # Test Pinecone - Dual-Index Architecture
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)

        # Test Knowledge Index (Source A)
        knowledge_index = pc.Index(PINECONE_KNOWLEDGE_INDEX)
        knowledge_stats = knowledge_index.describe_index_stats()
        logger.info(f"✓ Knowledge Index connected: {PINECONE_KNOWLEDGE_INDEX} ({knowledge_stats.total_vector_count} vectors)")

        # Test Error Library (Source B)
        failures_index = pc.Index(PINECONE_FAILURES_INDEX)
        failures_stats = failures_index.describe_index_stats()
        logger.info(f"✓ Error Library connected: {PINECONE_FAILURES_INDEX} ({failures_stats.total_vector_count} vectors)")

    except Exception as e:
        logger.warning(f"⚠ Pinecone connection issue: {str(e)[:100]}")

    # Use port 5006 to match frontend API_BASE_URL expectation
    port = int(os.environ.get('DASHBOARD_API_PORT', 5006))

    logger.info("=" * 60)
    logger.info(f"Dashboard API running on http://0.0.0.0:{port}")
    logger.info("=" * 60)
    logger.info("\nAvailable Endpoints:")
    logger.info("  GET /api/system/status    - System health status")
    logger.info("  GET /api/pipeline/flow    - Pipeline flow monitoring")
    logger.info("  GET /api/failures         - Test failures with AI analysis")
    logger.info("  GET /api/analysis/<id>    - Detailed AI analysis")
    logger.info("  GET /api/stats            - System statistics")
    logger.info("  GET /api/activity         - Recent activity log")
    logger.info("  GET /api/health           - Health check")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
