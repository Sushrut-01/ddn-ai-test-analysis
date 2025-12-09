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

# AI Service (use Docker service name in containerized environment)
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://langgraph-service:5000')

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

        # Combined pinecone status for UI compatibility
        status['components']['pinecone'] = {
            'status': 'healthy',
            'connected': True,
            'total_vectors': knowledge_stats.total_vector_count + failures_stats.total_vector_count,
            'last_check': datetime.utcnow().isoformat()
        }
    except Exception as e:
        status['components']['pinecone'] = {
            'status': 'error',
            'connected': False,
            'error': str(e)[:200]
        }

    # 4. AI Service Status (langgraph uses /health not /api/health)
    try:
        response = requests.get(f'{AI_SERVICE_URL}/health', timeout=5)
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
        build_id = request.args.get('build_id')
        feedback_status = request.args.get('feedback_status')  # Task 0-HITL.15: New filter
        category = request.args.get('category')
        search = request.args.get('search')
        analyzed_only = request.args.get('analyzed', '').lower() == 'true'  # Filter for analyzed builds only

        # If analyzed_only, get build_ids that have AI analysis from PostgreSQL first
        analyzed_build_ids = []
        if analyzed_only:
            try:
                conn = get_postgres_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT DISTINCT build_id FROM failure_analysis
                    ORDER BY build_id DESC
                    LIMIT 100
                """)
                analyzed_build_ids = [row['build_id'] for row in cursor.fetchall()]
                cursor.close()
                conn.close()
                logger.info(f"📊 Found {len(analyzed_build_ids)} builds with AI analysis")
            except Exception as e:
                logger.error(f"Error getting analyzed build_ids: {e}")

        # Build query
        query = {}
        if build_number:
            query['build_number'] = build_number
        if build_id:
            query['build_id'] = build_id
        if analyzed_only and analyzed_build_ids:
            query['build_id'] = {'$in': analyzed_build_ids}

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
                # Use build_id for matching (mongodb_failure_id is often not set)
                cursor.execute("""
                    SELECT
                        fa.id as analysis_id,
                        fa.classification,
                        fa.root_cause,
                        fa.severity,
                        fa.fix_recommendation as recommendation,
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
                    WHERE fa.build_id = %s OR fa.mongodb_failure_id = %s
                    ORDER BY fa.analyzed_at DESC, at.created_at DESC
                    LIMIT 1
                """, (failure.get('build_id'), failure['_id']))

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
        from bson.errors import InvalidId

        failure = None

        # First try as ObjectId
        try:
            failure = mongo_db['test_failures'].find_one({'_id': ObjectId(failure_id)})
        except (InvalidId, Exception):
            # If not a valid ObjectId, try as build_id
            failure = mongo_db['test_failures'].find_one({'build_id': failure_id})

            # If still not found, also check in PostgreSQL for analyzed failures
            if not failure:
                try:
                    conn = get_postgres_connection()
                    cursor = conn.cursor(cursor_factory=RealDictCursor)
                    cursor.execute("""
                        SELECT id, build_id, job_name, test_name, error_message, stack_trace,
                               classification, root_cause, severity, fix_recommendation as recommendation,
                               confidence_score, analyzed_at, ai_model, similar_cases,
                               github_files, github_code_included, triggered_by, trigger_type
                        FROM failure_analysis
                        WHERE build_id = %s
                        ORDER BY analyzed_at DESC
                        LIMIT 1
                    """, (failure_id,))
                    pg_failure = cursor.fetchone()
                    cursor.close()
                    conn.close()

                    if pg_failure:
                        # Convert PostgreSQL result to failure format
                        failure = {
                            '_id': str(pg_failure['id']),
                            'build_id': pg_failure['build_id'],
                            'job_name': pg_failure['job_name'],
                            'test_name': pg_failure['test_name'],
                            'error_message': pg_failure['error_message'],
                            'stack_trace': pg_failure['stack_trace'],
                            'timestamp': pg_failure['analyzed_at'].isoformat() if pg_failure.get('analyzed_at') else None,
                            'ai_analysis': {
                                'classification': pg_failure['classification'],
                                'root_cause': pg_failure['root_cause'],
                                'severity': pg_failure['severity'],
                                'recommendation': pg_failure['recommendation'],
                                'confidence_score': float(pg_failure['confidence_score']) if pg_failure.get('confidence_score') else None,
                                'analyzed_at': pg_failure['analyzed_at'].isoformat() if pg_failure.get('analyzed_at') else None,
                                'ai_model': pg_failure['ai_model'],
                                'similar_cases': pg_failure['similar_cases'],
                                'github_files': pg_failure['github_files'],
                                'github_code_included': pg_failure['github_code_included']
                            }
                        }
                        return jsonify({'failure': failure})
                except Exception as pg_err:
                    logger.error(f"Error fetching from PostgreSQL: {pg_err}")

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
                    fix_recommendation as recommendation,
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
# BUILD-LEVEL METRICS (Phase 6-7: Dual Metrics Support)
# ============================================================================

@app.route('/api/builds/summary', methods=['GET'])
def get_builds_summary():
    """
    Phase 7: Get build-level summary with dual metrics.
    Returns both failed_build_count (Jenkins pipeline failures) and
    failed_test_count (test case failures within builds).

    Query params:
    - job_name: Filter by specific job (optional)
    - days: Limit to last N days (default: 30)
    """
    try:
        job_filter = request.args.get('job_name')
        days = int(request.args.get('days', 30))

        # Get build-level data from build_results collection
        build_results = mongo_db['build_results']

        # Build match stage
        match_stage = {}
        if job_filter:
            match_stage['job_name'] = job_filter
        if days > 0:
            match_stage['timestamp'] = {'$gte': datetime.utcnow() - timedelta(days=days)}

        # Aggregation pipeline
        pipeline = [
            {'$match': match_stage} if match_stage else {'$match': {}},
            {
                '$group': {
                    '_id': '$job_name',
                    'total_builds': {'$sum': 1},
                    'failed_builds': {
                        '$sum': {'$cond': [{'$eq': ['$build_result', 'FAILURE']}, 1, 0]}
                    },
                    'success_builds': {
                        '$sum': {'$cond': [{'$eq': ['$build_result', 'SUCCESS']}, 1, 0]}
                    },
                    'unstable_builds': {
                        '$sum': {'$cond': [{'$eq': ['$build_result', 'UNSTABLE']}, 1, 0]}
                    },
                    'total_test_failures': {'$sum': {'$ifNull': ['$test_fail_count', 0]}},
                    'total_test_passes': {'$sum': {'$ifNull': ['$test_pass_count', 0]}},
                    'latest_build': {'$max': '$build_number'},
                    'latest_timestamp': {'$max': '$timestamp'},
                    'avg_duration_ms': {'$avg': '$build_duration_ms'}
                }
            },
            {
                '$project': {
                    'job_name': '$_id',
                    'total_builds': 1,
                    'failed_builds': 1,
                    'success_builds': 1,
                    'unstable_builds': 1,
                    'total_test_failures': 1,
                    'total_test_passes': 1,
                    'latest_build': 1,
                    'latest_timestamp': 1,
                    'avg_duration_ms': 1,
                    'build_success_rate': {
                        '$cond': [
                            {'$eq': ['$total_builds', 0]},
                            0,
                            {'$multiply': [{'$divide': ['$success_builds', '$total_builds']}, 100]}
                        ]
                    }
                }
            },
            {'$sort': {'total_builds': -1}}
        ]

        results = list(build_results.aggregate(pipeline))

        # Build response
        by_job = {}
        totals = {
            'total_builds': 0,
            'failed_build_count': 0,
            'success_build_count': 0,
            'unstable_build_count': 0,
            'failed_test_count': 0,
            'passed_test_count': 0
        }

        for r in results:
            job_name = r.get('job_name') or r.get('_id')
            job_data = {
                'total_builds': r.get('total_builds', 0),
                'failed_builds': r.get('failed_builds', 0),
                'success_builds': r.get('success_builds', 0),
                'unstable_builds': r.get('unstable_builds', 0),
                'total_test_failures': r.get('total_test_failures', 0),
                'total_test_passes': r.get('total_test_passes', 0),
                'latest_build': r.get('latest_build', 0),
                'latest_timestamp': r.get('latest_timestamp').isoformat() if r.get('latest_timestamp') else None,
                'avg_duration_ms': round(r.get('avg_duration_ms', 0) or 0),
                'build_success_rate': round(r.get('build_success_rate', 0) or 0, 1)
            }
            by_job[job_name] = job_data

            # Accumulate totals
            totals['total_builds'] += job_data['total_builds']
            totals['failed_build_count'] += job_data['failed_builds']
            totals['success_build_count'] += job_data['success_builds']
            totals['unstable_build_count'] += job_data['unstable_builds']
            totals['failed_test_count'] += job_data['total_test_failures']
            totals['passed_test_count'] += job_data['total_test_passes']

        # Calculate overall success rate
        totals['build_success_rate'] = round(
            (totals['success_build_count'] / totals['total_builds'] * 100)
            if totals['total_builds'] > 0 else 0, 1
        )

        return jsonify({
            'success': True,
            'totals': totals,
            'by_job': by_job,
            'days': days,
            'generated_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting builds summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/builds/recent', methods=['GET'])
def get_recent_builds():
    """
    Get recent builds with their results.

    Query params:
    - limit: Max results (default: 20)
    - job_name: Filter by job (optional)
    - result: Filter by build_result (SUCCESS, FAILURE, UNSTABLE)
    """
    try:
        limit = int(request.args.get('limit', 20))
        job_filter = request.args.get('job_name')
        result_filter = request.args.get('result')

        build_results = mongo_db['build_results']

        query = {}
        if job_filter:
            query['job_name'] = job_filter
        if result_filter:
            query['build_result'] = result_filter

        builds = list(build_results.find(query)
                     .sort('timestamp', -1)
                     .limit(limit))

        # Convert ObjectId and datetime
        for build in builds:
            build['_id'] = str(build['_id'])
            if isinstance(build.get('timestamp'), datetime):
                build['timestamp'] = build['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'count': len(builds),
            'builds': builds
        })

    except Exception as e:
        logger.error(f"Error getting recent builds: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/builds/<build_id>', methods=['GET'])
def get_build_details(build_id):
    """
    Get detailed information for a specific build including test failures.
    """
    try:
        build_results = mongo_db['build_results']
        test_failures = mongo_db['test_failures']

        # Get build info
        build = build_results.find_one({'build_id': build_id})

        if not build:
            return jsonify({'success': False, 'error': 'Build not found'}), 404

        build['_id'] = str(build['_id'])
        if isinstance(build.get('timestamp'), datetime):
            build['timestamp'] = build['timestamp'].isoformat()

        # Get test failures for this build
        failures = list(test_failures.find({'build_id': build_id})
                       .sort('timestamp', -1))

        for f in failures:
            f['_id'] = str(f['_id'])
            if isinstance(f.get('timestamp'), datetime):
                f['timestamp'] = f['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'build': build,
            'test_failures': failures,
            'test_failure_count': len(failures)
        })

    except Exception as e:
        logger.error(f"Error getting build details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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

@app.route('/api/analytics/trends', methods=['GET'])
def get_analytics_trends():
    """
    Get failure trends over time for charts

    Query params:
    - time_range: '7d', '30d', '90d' (default: '30d')
    - aggregation: 'daily', 'weekly' (default: 'daily')
    """
    try:
        time_range = request.args.get('time_range', '30d')
        aggregation = request.args.get('aggregation', 'daily')

        days_map = {'7d': 7, '30d': 30, '90d': 90}
        days = days_map.get(time_range, 30)

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get failure trends by category over time
            cursor.execute("""
                SELECT
                    DATE(created_at) as date,
                    classification,
                    COUNT(*) as count
                FROM failure_analysis
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(created_at), classification
                ORDER BY date
            """, (days,))

            rows = cursor.fetchall()

            # Process into chart format
            date_data = {}
            for row in rows:
                date_str = row['date'].strftime('%Y-%m-%d') if row['date'] else 'Unknown'
                if date_str not in date_data:
                    date_data[date_str] = {
                        'name': date_str,
                        'codeError': 0,
                        'testFailure': 0,
                        'infraError': 0,
                        'depError': 0,
                        'configError': 0,
                        'unknown': 0
                    }

                classification = (row['classification'] or 'unknown').lower()
                count = row['count'] or 0

                if 'code' in classification:
                    date_data[date_str]['codeError'] += count
                elif 'test' in classification:
                    date_data[date_str]['testFailure'] += count
                elif 'infra' in classification:
                    date_data[date_str]['infraError'] += count
                elif 'dep' in classification:
                    date_data[date_str]['depError'] += count
                elif 'config' in classification:
                    date_data[date_str]['configError'] += count
                else:
                    date_data[date_str]['unknown'] += count

            trends = list(date_data.values())

            cursor.close()
            conn.close()

            return jsonify({
                'data': trends,
                'time_range': time_range,
                'aggregation': aggregation
            })

        except Exception as e:
            conn.close()
            logger.error(f"Error querying trends: {e}")
            return jsonify({'data': [], 'error': str(e)})

    except Exception as e:
        logger.error(f"Error getting analytics trends: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/patterns', methods=['GET'])
def get_analytics_patterns():
    """
    Get top failure patterns identified by AI
    """
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Get most common error patterns from root cause analysis
            cursor.execute("""
                SELECT
                    COALESCE(classification, 'Unknown') as pattern,
                    COUNT(*) as count,
                    AVG(CASE WHEN confidence_score IS NOT NULL THEN confidence_score ELSE 0 END) * 100 as success_rate
                FROM failure_analysis
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY classification
                ORDER BY count DESC
                LIMIT 10
            """)

            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'pattern': row['pattern'] or 'Unknown',
                    'count': row['count'] or 0,
                    'successRate': round(float(row['success_rate'] or 0), 1),
                    'trend': 'stable'  # Could calculate actual trend with more data
                })

            cursor.close()
            conn.close()

            return jsonify({
                'data': patterns
            })

        except Exception as e:
            conn.close()
            logger.error(f"Error querying patterns: {e}")
            return jsonify({'data': [], 'error': str(e)})

    except Exception as e:
        logger.error(f"Error getting analytics patterns: {e}")
        return jsonify({'error': str(e)}), 500


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
# AI ANALYSIS STORAGE ENDPOINT (Best Practice: Centralized Data Entry)
# ============================================================================

@app.route('/api/analysis/store', methods=['POST'])
def store_analysis():
    """
    Store AI analysis result from n8n workflows (Workflows 1, 2, 3).

    This endpoint follows the architecture best practice of using Dashboard API
    as the single entry point for data storage (like Workflow 4 does with /api/fixes).

    Request body:
    {
        "build_id": "123",
        "mongodb_failure_id": "optional_mongo_id",
        "error_category": "CODE_ERROR",
        "root_cause": "...",
        "fix_recommendation": "...",
        "confidence_score": 0.85,
        "analysis_type": "RAG_BASED|CLAUDE_DEEP_ANALYSIS|REFINED_ANALYSIS",
        "trigger_type": "AUTO|MANUAL|REFINEMENT",
        "job_name": "DDN-Nightly-Tests",
        "test_suite": "...",
        "github_files": [...],
        "estimated_cost_usd": 0.05,
        "token_usage": 1000,
        "triggered_by": "user@email.com"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Required fields
        build_id = data.get('build_id')
        if not build_id:
            return jsonify({'success': False, 'error': 'build_id required'}), 400

        # Extract all fields
        error_category = data.get('error_category', 'UNKNOWN')
        root_cause = data.get('root_cause', '')
        fix_recommendation = data.get('fix_recommendation', data.get('recommendation', ''))
        confidence_score = float(data.get('confidence_score', 0))
        analysis_type = data.get('analysis_type', 'RAG_BASED')
        trigger_type = data.get('trigger_type', 'AUTO')
        job_name = data.get('job_name', '')
        test_suite = data.get('test_suite', '')
        github_files = data.get('github_files', data.get('links', {}).get('github_files', []))
        estimated_cost = float(data.get('estimated_cost_usd', 0))
        token_usage = int(data.get('token_usage', 0))
        mongodb_failure_id = data.get('mongodb_failure_id', '')
        triggered_by = data.get('triggered_by', 'system')
        code_fix = data.get('code_fix', '')
        prevention_strategy = data.get('prevention_strategy', '')
        severity = data.get('severity', data.get('priority', 'MEDIUM'))

        # Determine AI model based on analysis type
        ai_model = 'gemini-1.5-pro' if analysis_type == 'RAG_BASED' else 'claude-3.5-sonnet'

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()

            # Insert into failure_analysis (main analysis table)
            cursor.execute("""
                INSERT INTO failure_analysis (
                    build_id,
                    job_name,
                    test_suite,
                    mongodb_failure_id,
                    classification,
                    root_cause,
                    severity,
                    fix_recommendation,
                    confidence_score,
                    analyzed_at,
                    ai_model,
                    github_files,
                    github_code_included,
                    token_usage,
                    cost_usd,
                    trigger_type,
                    triggered_by,
                    code_fix,
                    prevention_strategy
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id, analyzed_at
            """, (
                build_id,
                job_name or 'Unknown',
                test_suite or None,
                mongodb_failure_id or None,
                error_category,
                root_cause,
                severity,
                fix_recommendation,
                confidence_score,
                ai_model,
                str(github_files) if github_files else None,
                bool(github_files),
                token_usage,
                estimated_cost,
                trigger_type,
                triggered_by,
                code_fix,
                prevention_strategy
            ))

            result = cursor.fetchone()
            analysis_id = result[0]
            analyzed_at = result[1]

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✓ Analysis stored for build {build_id}, analysis_id={analysis_id}")

            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'build_id': build_id,
                'analyzed_at': analyzed_at.isoformat() if analyzed_at else None,
                'message': 'Analysis stored successfully'
            }), 201

        except Exception as e:
            conn.rollback()
            logger.error(f"Database error storing analysis: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analysis/update', methods=['PUT'])
def update_analysis():
    """
    Update existing AI analysis (for refinement workflow).

    Request body:
    {
        "build_id": "123",
        "refinement_version": 1,
        "user_feedback": "The issue is actually...",
        "error_category": "CONFIG_ERROR",  (may change from original)
        "root_cause": "Updated root cause...",
        "fix_recommendation": "Updated fix...",
        "confidence_score": 0.92
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        build_id = data.get('build_id')
        if not build_id:
            return jsonify({'success': False, 'error': 'build_id required'}), 400

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        try:
            cursor = conn.cursor()

            # Update the latest analysis for this build_id
            cursor.execute("""
                UPDATE failure_analysis
                SET
                    classification = COALESCE(%s, classification),
                    root_cause = COALESCE(%s, root_cause),
                    fix_recommendation = COALESCE(%s, fix_recommendation),
                    confidence_score = COALESCE(%s, confidence_score),
                    code_fix = COALESCE(%s, code_fix),
                    prevention_strategy = COALESCE(%s, prevention_strategy),
                    refinement_count = COALESCE(refinement_count, 0) + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE build_id = %s
                AND id = (SELECT id FROM failure_analysis WHERE build_id = %s ORDER BY analyzed_at DESC LIMIT 1)
                RETURNING id, refinement_count
            """, (
                data.get('error_category'),
                data.get('root_cause'),
                data.get('fix_recommendation'),
                data.get('confidence_score'),
                data.get('code_fix'),
                data.get('prevention_strategy'),
                build_id,
                build_id
            ))

            result = cursor.fetchone()

            if not result:
                conn.rollback()
                return jsonify({'success': False, 'error': 'No analysis found to update'}), 404

            analysis_id = result[0]
            refinement_count = result[1]

            # Log refinement history
            if data.get('user_feedback'):
                cursor.execute("""
                    INSERT INTO refinement_history (
                        failure_id,
                        analysis_id,
                        refinement_version,
                        user_feedback,
                        category_before,
                        category_after,
                        original_confidence_score,
                        refined_confidence_score,
                        refinement_timestamp,
                        refined_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s
                    )
                """, (
                    build_id,
                    analysis_id,
                    refinement_count,
                    data.get('user_feedback'),
                    data.get('original_category'),
                    data.get('error_category'),
                    data.get('original_confidence'),
                    data.get('confidence_score'),
                    data.get('triggered_by', 'system')
                ))

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"✓ Analysis updated for build {build_id}, refinement #{refinement_count}")

            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'build_id': build_id,
                'refinement_count': refinement_count,
                'message': 'Analysis updated successfully'
            }), 200

        except Exception as e:
            conn.rollback()
            logger.error(f"Database error updating analysis: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500

    except Exception as e:
        logger.error(f"Error updating analysis: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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

        # Build query - uses actual table columns
        query = """
            SELECT
                id,
                failure_id,
                build_id,
                branch_name,
                pr_number,
                pr_url,
                status,
                applied_by,
                applied_at,
                fix_type,
                job_name,
                file_path,
                merged_at,
                rollback_at
            FROM code_fix_applications
            WHERE 1=1
        """

        params = []

        if status_filter:
            query += " AND status = %s"
            params.append(status_filter)

        if category_filter:
            query += " AND fix_type = %s"
            params.append(category_filter)

        query += " ORDER BY applied_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        fixes = []
        for row in rows:
            fixes.append({
                'id': row[0],
                'failure_id': row[1],
                'build_id': row[2],
                'branch_name': row[3],
                'pr_number': row[4],
                'pr_url': row[5],
                'status': row[6],
                'applied_by': row[7],
                'applied_at': row[8].isoformat() if row[8] else None,
                'fix_type': row[9],
                'job_name': row[10],
                'file_path': row[11],
                'merged_at': row[12].isoformat() if row[12] else None,
                'rollback_at': row[13].isoformat() if row[13] else None
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
# MANUAL TRIGGER PROXY (proxies to manual-trigger-api on port 5004)
# ============================================================================

MANUAL_TRIGGER_API_URL = os.getenv('MANUAL_TRIGGER_API_URL', 'http://ddn-manual-trigger:5004')

@app.route('/api/trigger/manual', methods=['POST', 'OPTIONS'])
def proxy_manual_trigger():
    """
    Proxy manual trigger requests to the manual-trigger-api service

    Request body:
    {
        "build_id": "12345",
        "failure_id": "abc123",
        "triggered_by_user": "user@example.com"
    }
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response, 200

    try:
        data = request.get_json() or {}
        logger.info(f"Proxying manual trigger request: {data}")

        # Forward to manual-trigger-api
        response = requests.post(
            f"{MANUAL_TRIGGER_API_URL}/api/trigger-analysis",
            json=data,
            timeout=120  # Longer timeout for AI analysis
        )

        return jsonify(response.json()), response.status_code

    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to manual-trigger-api service")
        return jsonify({
            'success': False,
            'error': 'Manual trigger service unavailable. Please ensure ddn-manual-trigger is running.'
        }), 503
    except requests.exceptions.Timeout:
        logger.error("Manual trigger request timed out")
        return jsonify({
            'success': False,
            'error': 'Analysis request timed out. The AI analysis may take longer than expected.'
        }), 504
    except Exception as e:
        logger.error(f"Error proxying manual trigger: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TRIGGER HISTORY
# ============================================================================

@app.route('/api/trigger/history', methods=['GET'])
def get_trigger_history():
    """
    Get manual trigger history

    Query params:
    - limit: Max results (default: 50)
    - user: Filter by user
    """
    try:
        limit = int(request.args.get('limit', 50))
        user_filter = request.args.get('user')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()

        query = """
            SELECT
                t.id,
                t.build_id,
                t.triggered_by_user,
                t.trigger_source,
                t.consecutive_failures_at_trigger,
                t.reason,
                t.analysis_id,
                t.trigger_successful,
                t.triggered_at,
                f.job_name,
                f.error_category
            FROM manual_trigger_log t
            LEFT JOIN failure_analysis f ON t.analysis_id = f.id
            WHERE 1=1
        """
        params = []

        if user_filter:
            query += " AND t.triggered_by_user = %s"
            params.append(user_filter)

        query += " ORDER BY t.triggered_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Get stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN trigger_successful = true THEN 1 END) as successful,
                COUNT(CASE WHEN trigger_successful = false THEN 1 END) as failed
            FROM manual_trigger_log
        """)
        stats_row = cursor.fetchone()

        cursor.close()
        conn.close()

        triggers = []
        for row in rows:
            triggers.append({
                'id': row[0],
                'build_id': row[1],
                'triggered_by': row[2],
                'trigger_source': row[3],
                'consecutive_failures': row[4],
                'reason': row[5],
                'analysis_id': row[6],
                'successful': row[7],
                'triggered_at': row[8].isoformat() if row[8] else None,
                'job_name': row[9],
                'error_category': row[10]
            })

        return jsonify({
            'success': True,
            'count': len(triggers),
            'stats': {
                'total': stats_row[0] or 0,
                'successful': stats_row[1] or 0,
                'failed': stats_row[2] or 0
            },
            'triggers': triggers
        }), 200

    except Exception as e:
        logger.error(f"Error getting trigger history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# FEEDBACK
# ============================================================================

@app.route('/api/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """
    Get recent user feedback

    Query params:
    - limit: Max results (default: 50)
    - type: Filter by feedback type
    """
    try:
        limit = int(request.args.get('limit', 50))
        type_filter = request.args.get('type')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()

        query = """
            SELECT
                uf.id,
                uf.analysis_id,
                uf.feedback_type,
                uf.feedback_text,
                uf.user_email,
                uf.validation_status,
                uf.submitted_at,
                fa.job_name,
                fa.error_category
            FROM user_feedback uf
            LEFT JOIN failure_analysis fa ON uf.analysis_id = fa.id
            WHERE 1=1
        """
        params = []

        if type_filter:
            query += " AND uf.feedback_type = %s"
            params.append(type_filter)

        query += " ORDER BY uf.submitted_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Get stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN feedback_type = 'positive' THEN 1 END) as positive,
                COUNT(CASE WHEN feedback_type = 'negative' THEN 1 END) as negative,
                COUNT(CASE WHEN validation_status = 'accepted' THEN 1 END) as accepted
            FROM user_feedback
        """)
        stats_row = cursor.fetchone()

        cursor.close()
        conn.close()

        feedbacks = []
        for row in rows:
            feedbacks.append({
                'id': row[0],
                'analysis_id': row[1],
                'feedback_type': row[2],
                'feedback_text': row[3],
                'user_email': row[4],
                'validation_status': row[5],
                'submitted_at': row[6].isoformat() if row[6] else None,
                'job_name': row[7],
                'error_category': row[8]
            })

        return jsonify({
            'success': True,
            'count': len(feedbacks),
            'stats': {
                'total': stats_row[0] or 0,
                'positive': stats_row[1] or 0,
                'negative': stats_row[2] or 0,
                'accepted': stats_row[3] or 0
            },
            'feedbacks': feedbacks
        }), 200

    except Exception as e:
        logger.error(f"Error getting recent feedback: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# JIRA BUGS API
# ============================================================================

@app.route('/api/jira/bugs', methods=['GET'])
def get_jira_bugs():
    """
    Get list of Jira bugs created from AI analyses

    Query params:
    - limit: Max results (default: 50)
    - status: Filter by bug status (open, in_progress, resolved, closed)
    - priority: Filter by priority (critical, high, medium, low)
    """
    try:
        limit = int(request.args.get('limit', 50))
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                jb.id,
                jb.jira_key,
                jb.jira_url,
                jb.summary,
                jb.description,
                jb.priority,
                jb.status,
                jb.assignee,
                jb.reporter,
                jb.analysis_id,
                jb.created_at,
                jb.updated_at,
                fa.classification,
                fa.root_cause,
                fa.confidence_score,
                fa.build_id
            FROM jira_bugs jb
            LEFT JOIN failure_analysis fa ON jb.analysis_id = fa.id
            WHERE 1=1
        """
        params = []

        if status_filter:
            query += " AND jb.status = %s"
            params.append(status_filter)

        if priority_filter:
            query += " AND jb.priority = %s"
            params.append(priority_filter)

        query += " ORDER BY jb.created_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        bugs = cursor.fetchall()

        # Get stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'open' THEN 1 END) as open_count,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status = 'resolved' THEN 1 END) as resolved,
                COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed,
                COUNT(CASE WHEN priority = 'critical' THEN 1 END) as critical,
                COUNT(CASE WHEN priority = 'high' THEN 1 END) as high
            FROM jira_bugs
        """)
        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for bug in bugs:
            if bug.get('created_at'):
                bug['created_at'] = bug['created_at'].isoformat()
            if bug.get('updated_at'):
                bug['updated_at'] = bug['updated_at'].isoformat()

        return jsonify({
            'success': True,
            'count': len(bugs),
            'stats': dict(stats) if stats else {},
            'bugs': [dict(b) for b in bugs]
        }), 200

    except Exception as e:
        logger.error(f"Error getting Jira bugs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jira/bugs', methods=['POST'])
def create_jira_bug():
    """
    Create a Jira bug from an approved AI analysis

    Request body:
    {
        "analysis_id": 123,
        "summary": "Bug title",
        "priority": "high",
        "assignee": "john.doe@company.com",
        "additional_context": "Optional extra info"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        analysis_id = data.get('analysis_id')
        summary = data.get('summary')
        priority = data.get('priority', 'medium')
        assignee = data.get('assignee')

        if not analysis_id or not summary:
            return jsonify({'success': False, 'error': 'analysis_id and summary required'}), 400

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get analysis details
        cursor.execute("""
            SELECT classification, root_cause, fix_recommendation as recommendation, build_id
            FROM failure_analysis
            WHERE id = %s
        """, (analysis_id,))

        analysis = cursor.fetchone()
        if not analysis:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Analysis not found'}), 404

        # Generate Jira key (in production, this would come from Jira API)
        cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM jira_bugs")
        next_id = cursor.fetchone()['coalesce']
        jira_key = f"DDN-{1000 + next_id}"
        jira_url = f"https://jira.example.com/browse/{jira_key}"

        # Build description
        description = f"""
**Classification:** {analysis['classification']}
**Build ID:** {analysis['build_id']}

**Root Cause:**
{analysis['root_cause']}

**AI Recommendation:**
{analysis['recommendation']}

---
*This bug was automatically created from AI analysis #{analysis_id}*
        """

        # Insert bug record
        cursor.execute("""
            INSERT INTO jira_bugs (
                jira_key, jira_url, summary, description, priority,
                status, assignee, reporter, analysis_id, created_at
            )
            VALUES (%s, %s, %s, %s, %s, 'open', %s, 'AI System', %s, CURRENT_TIMESTAMP)
            RETURNING id, jira_key, jira_url
        """, (jira_key, jira_url, summary, description, priority, assignee, analysis_id))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'bug': {
                'id': result['id'],
                'jira_key': result['jira_key'],
                'jira_url': result['jira_url']
            },
            'message': f'Bug {jira_key} created successfully'
        }), 201

    except Exception as e:
        logger.error(f"Error creating Jira bug: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/jira/approved-analyses', methods=['GET'])
def get_approved_analyses():
    """
    Get AI analyses that have been approved but don't have bugs yet
    These are candidates for bug creation
    """
    try:
        limit = int(request.args.get('limit', 50))

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                fa.id as analysis_id,
                fa.build_id,
                fa.classification,
                fa.root_cause,
                fa.fix_recommendation as recommendation,
                fa.confidence_score,
                fa.severity,
                fa.analyzed_at,
                at.validation_status,
                at.validator_name,
                at.validated_at
            FROM failure_analysis fa
            JOIN acceptance_tracking at ON fa.id = at.analysis_id
            LEFT JOIN jira_bugs jb ON fa.id = jb.analysis_id
            WHERE at.validation_status = 'accepted'
            AND jb.id IS NULL
            ORDER BY fa.analyzed_at DESC
            LIMIT %s
        """, (limit,))

        analyses = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for a in analyses:
            if a.get('analyzed_at'):
                a['analyzed_at'] = a['analyzed_at'].isoformat()
            if a.get('validated_at'):
                a['validated_at'] = a['validated_at'].isoformat()

        return jsonify({
            'success': True,
            'count': len(analyses),
            'analyses': [dict(a) for a in analyses]
        }), 200

    except Exception as e:
        logger.error(f"Error getting approved analyses: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PIPELINE JOBS API (Active Analysis Jobs)
# ============================================================================

@app.route('/api/pipeline/jobs', methods=['GET'])
def get_pipeline_jobs():
    """
    Get active and recent analysis jobs with their stage status

    Query params:
    - limit: Max results (default: 20)
    - status: Filter by status (active, completed, failed)
    """
    try:
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get jobs from manual_trigger_log with analysis status
        query = """
            SELECT
                mtl.id as job_id,
                mtl.build_id,
                mtl.triggered_by_user,
                mtl.trigger_source,
                mtl.reason,
                mtl.triggered_at,
                mtl.trigger_successful,
                fa.id as analysis_id,
                fa.classification,
                fa.confidence_score,
                fa.analyzed_at,
                fa.ai_model,
                CASE
                    WHEN fa.analyzed_at IS NOT NULL THEN 'completed'
                    WHEN mtl.trigger_successful = false THEN 'failed'
                    WHEN mtl.triggered_at > NOW() - INTERVAL '5 minutes' THEN 'active'
                    ELSE 'pending'
                END as status,
                CASE
                    WHEN fa.analyzed_at IS NOT NULL THEN 'complete'
                    WHEN mtl.triggered_at > NOW() - INTERVAL '1 minute' THEN 'react'
                    WHEN mtl.triggered_at > NOW() - INTERVAL '3 minutes' THEN 'crag'
                    WHEN mtl.triggered_at > NOW() - INTERVAL '4 minutes' THEN 'gemini'
                    ELSE 'queue'
                END as current_stage
            FROM manual_trigger_log mtl
            LEFT JOIN failure_analysis fa ON mtl.analysis_id = fa.id
            WHERE 1=1
        """
        params = []

        if status_filter:
            if status_filter == 'active':
                query += " AND fa.analyzed_at IS NULL AND mtl.trigger_successful = true"
            elif status_filter == 'completed':
                query += " AND fa.analyzed_at IS NOT NULL"
            elif status_filter == 'failed':
                query += " AND mtl.trigger_successful = false"

        query += " ORDER BY mtl.triggered_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        jobs = cursor.fetchall()

        # Get stats
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN fa.analyzed_at IS NULL AND mtl.trigger_successful = true
                      AND mtl.triggered_at > NOW() - INTERVAL '10 minutes' THEN 1 END) as active,
                COUNT(CASE WHEN fa.analyzed_at IS NOT NULL THEN 1 END) as completed,
                COUNT(CASE WHEN mtl.trigger_successful = false THEN 1 END) as failed
            FROM manual_trigger_log mtl
            LEFT JOIN failure_analysis fa ON mtl.analysis_id = fa.id
        """)
        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for job in jobs:
            if job.get('triggered_at'):
                job['triggered_at'] = job['triggered_at'].isoformat()
            if job.get('analyzed_at'):
                job['analyzed_at'] = job['analyzed_at'].isoformat()

        return jsonify({
            'success': True,
            'count': len(jobs),
            'stats': dict(stats) if stats else {},
            'jobs': [dict(j) for j in jobs]
        }), 200

    except Exception as e:
        logger.error(f"Error getting pipeline jobs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pipeline/jobs/<int:job_id>/logs', methods=['GET'])
def get_job_logs(job_id):
    """
    Get logs for a specific pipeline job
    """
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get job info
        cursor.execute("""
            SELECT
                mtl.id, mtl.build_id, mtl.triggered_at, mtl.trigger_successful,
                fa.classification, fa.analyzed_at
            FROM manual_trigger_log mtl
            LEFT JOIN failure_analysis fa ON mtl.analysis_id = fa.id
            WHERE mtl.id = %s
        """, (job_id,))

        job = cursor.fetchone()
        if not job:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Job not found'}), 404

        # Generate simulated logs based on job state
        logs = []
        base_time = job['triggered_at']

        logs.append({
            'time': base_time.isoformat(),
            'level': 'INFO',
            'stage': 'trigger',
            'message': f'Analysis triggered for build {job["build_id"]}',
            'source': 'TriggerService'
        })

        if job['trigger_successful']:
            logs.append({
                'time': (base_time + timedelta(seconds=1)).isoformat(),
                'level': 'INFO',
                'stage': 'queue',
                'message': 'Task queued in Celery worker',
                'source': 'CeleryDispatcher'
            })

            logs.append({
                'time': (base_time + timedelta(seconds=5)).isoformat(),
                'level': 'INFO',
                'stage': 'react',
                'message': 'ReAct Agent analyzing error...',
                'source': 'ReActAgent'
            })

            if job['analyzed_at']:
                logs.append({
                    'time': (base_time + timedelta(seconds=15)).isoformat(),
                    'level': 'INFO',
                    'stage': 'crag',
                    'message': 'CRAG verification complete',
                    'source': 'CRAGVerifier'
                })

                logs.append({
                    'time': (base_time + timedelta(seconds=25)).isoformat(),
                    'level': 'INFO',
                    'stage': 'gemini',
                    'message': 'Gemini formatting complete',
                    'source': 'GeminiFormatter'
                })

                logs.append({
                    'time': job['analyzed_at'].isoformat(),
                    'level': 'INFO',
                    'stage': 'complete',
                    'message': f'Analysis complete: {job["classification"]}',
                    'source': 'AnalysisService'
                })
        else:
            logs.append({
                'time': (base_time + timedelta(seconds=2)).isoformat(),
                'level': 'ERROR',
                'stage': 'trigger',
                'message': 'Trigger failed - check service status',
                'source': 'TriggerService'
            })

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'job_id': job_id,
            'build_id': job['build_id'],
            'logs': logs
        }), 200

    except Exception as e:
        logger.error(f"Error getting job logs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# NOTIFICATIONS API
# ============================================================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """
    Get user notifications

    Query params:
    - limit: Max results (default: 50)
    - unread_only: Only unread notifications (true/false)
    - type: Filter by type (analysis, bug, fix, system)
    """
    try:
        limit = int(request.args.get('limit', 50))
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        type_filter = request.args.get('type')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                id,
                type,
                title,
                message,
                severity,
                is_read,
                action_url,
                created_at
            FROM notifications
            WHERE 1=1
        """
        params = []

        if unread_only:
            query += " AND is_read = false"

        if type_filter:
            query += " AND type = %s"
            params.append(type_filter)

        query += " ORDER BY created_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        notifications = cursor.fetchall()

        # Get counts
        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN is_read = false THEN 1 END) as unread,
                COUNT(CASE WHEN type = 'analysis' THEN 1 END) as analysis_count,
                COUNT(CASE WHEN type = 'bug' THEN 1 END) as bug_count,
                COUNT(CASE WHEN type = 'fix' THEN 1 END) as fix_count,
                COUNT(CASE WHEN type = 'system' THEN 1 END) as system_count
            FROM notifications
        """)
        stats = cursor.fetchone()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for n in notifications:
            if n.get('created_at'):
                n['created_at'] = n['created_at'].isoformat()

        return jsonify({
            'success': True,
            'count': len(notifications),
            'stats': dict(stats) if stats else {},
            'notifications': [dict(n) for n in notifications]
        }), 200

    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET is_read = true, read_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
        """, (notification_id,))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({'success': False, 'error': 'Notification not found'}), 404

        return jsonify({'success': True, 'message': 'Notification marked as read'}), 200

    except Exception as e:
        logger.error(f"Error marking notification read: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        cursor.execute("""
            UPDATE notifications
            SET is_read = true, read_at = CURRENT_TIMESTAMP
            WHERE is_read = false
        """)

        count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({'success': True, 'marked_read': count}), 200

    except Exception as e:
        logger.error(f"Error marking all notifications read: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# AUDIT LOG API
# ============================================================================

@app.route('/api/audit-log', methods=['GET'])
def get_audit_log():
    """
    Get audit log entries

    Query params:
    - limit: Max results (default: 100)
    - action: Filter by action type
    - user: Filter by user
    - resource: Filter by resource type
    - start_date: Filter from date (ISO format)
    - end_date: Filter to date (ISO format)
    """
    try:
        limit = int(request.args.get('limit', 100))
        action_filter = request.args.get('action')
        user_filter = request.args.get('user')
        resource_filter = request.args.get('resource')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                id,
                timestamp,
                user_email,
                user_name,
                action,
                resource_type,
                resource_id,
                details,
                ip_address,
                user_agent,
                status
            FROM audit_log
            WHERE 1=1
        """
        params = []

        if action_filter:
            query += " AND action = %s"
            params.append(action_filter)

        if user_filter:
            query += " AND (user_email ILIKE %s OR user_name ILIKE %s)"
            params.extend([f'%{user_filter}%', f'%{user_filter}%'])

        if resource_filter:
            query += " AND resource_type = %s"
            params.append(resource_filter)

        if start_date:
            query += " AND timestamp >= %s"
            params.append(start_date)

        if end_date:
            query += " AND timestamp <= %s"
            params.append(end_date)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        entries = cursor.fetchall()

        # Get action types and counts for filters
        cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM audit_log
            GROUP BY action
            ORDER BY count DESC
        """)
        action_counts = cursor.fetchall()

        # Get resource types
        cursor.execute("""
            SELECT resource_type, COUNT(*) as count
            FROM audit_log
            GROUP BY resource_type
            ORDER BY count DESC
        """)
        resource_counts = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert datetime objects
        for entry in entries:
            if entry.get('timestamp'):
                entry['timestamp'] = entry['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'count': len(entries),
            'filters': {
                'actions': [dict(a) for a in action_counts],
                'resources': [dict(r) for r in resource_counts]
            },
            'entries': [dict(e) for e in entries]
        }), 200

    except Exception as e:
        logger.error(f"Error getting audit log: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/audit-log/export', methods=['GET'])
def export_audit_log():
    """
    Export audit log as CSV

    Query params same as get_audit_log
    """
    try:
        import csv
        from io import StringIO
        from flask import Response

        # Get entries (reuse same filtering logic)
        limit = int(request.args.get('limit', 1000))

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id, timestamp, user_email, user_name, action,
                resource_type, resource_id, details, ip_address, status
            FROM audit_log
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))

        entries = cursor.fetchall()
        cursor.close()
        conn.close()

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(['ID', 'Timestamp', 'User Email', 'User Name', 'Action',
                        'Resource Type', 'Resource ID', 'Details', 'IP Address', 'Status'])

        # Data
        for entry in entries:
            writer.writerow([
                entry['id'],
                entry['timestamp'].isoformat() if entry.get('timestamp') else '',
                entry.get('user_email', ''),
                entry.get('user_name', ''),
                entry.get('action', ''),
                entry.get('resource_type', ''),
                entry.get('resource_id', ''),
                entry.get('details', ''),
                entry.get('ip_address', ''),
                entry.get('status', '')
            ])

        output.seek(0)

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=audit_log_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
        )

    except Exception as e:
        logger.error(f"Error exporting audit log: {str(e)}")
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
# RAG APPROVAL HITL ENDPOINTS (Human-in-the-Loop for Non-Code Errors)
# ============================================================================

# Database schema for RAG approval queue
RAG_APPROVAL_SCHEMA = """
CREATE TABLE IF NOT EXISTS rag_approval_queue (
    id SERIAL PRIMARY KEY,
    build_id VARCHAR(255) NOT NULL,
    job_name VARCHAR(255),
    error_category VARCHAR(100) NOT NULL,
    original_category VARCHAR(100),
    rag_suggestion TEXT,
    rag_confidence DECIMAL(3,2),
    similar_cases_count INTEGER DEFAULT 0,
    similar_case_ids TEXT,
    review_status VARCHAR(20) DEFAULT 'pending',
    reviewed_by VARCHAR(100),
    reviewed_at TIMESTAMP,
    review_feedback TEXT,
    escalated_to_ai BOOLEAN DEFAULT FALSE,
    ai_analysis_id INTEGER,
    trigger_type VARCHAR(50) DEFAULT 'MANUAL',
    triggered_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rag_approval_status ON rag_approval_queue(review_status);
CREATE INDEX IF NOT EXISTS idx_rag_approval_build ON rag_approval_queue(build_id);
-- Add columns if table exists (for migration)
ALTER TABLE rag_approval_queue ADD COLUMN IF NOT EXISTS original_category VARCHAR(100);
ALTER TABLE rag_approval_queue ADD COLUMN IF NOT EXISTS trigger_type VARCHAR(50) DEFAULT 'MANUAL';
ALTER TABLE rag_approval_queue ADD COLUMN IF NOT EXISTS triggered_by VARCHAR(100);
"""


@app.route('/api/rag/pending', methods=['GET'])
def get_rag_pending():
    """Get pending RAG approvals for human review"""
    try:
        limit = int(request.args.get('limit', 50))
        category = request.args.get('category')

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, build_id, job_name, error_category, rag_suggestion,
                   rag_confidence, similar_cases_count, review_status, created_at,
                   trigger_type, triggered_by,
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


@app.route('/api/rag/approve', methods=['POST'])
def approve_rag():
    """
    Approve a RAG suggestion - CATEGORY-BASED flow:

    - CODE_ERROR: Human approves → AI Deep Analysis starts
      (Claude analyzes XML reports, debug logs, console output to find exact error line in code)
    - Non-code errors (ENV_CONFIG, NETWORK_ERROR, INFRA_ERROR):
      Just mark resolved - RAG already provided the fix, no AI analysis needed

    Supports category change: If new_category is provided, use that for flow decision
    """
    try:
        data = request.get_json()
        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        feedback = data.get('feedback', '')
        new_category = data.get('new_category')  # Optional: allows human to change category

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get the approval record first
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
        original_category = approval['error_category']

        # Use new_category if provided (human override), otherwise use original
        category_changed = new_category and new_category != original_category
        effective_category = new_category if category_changed else original_category

        if category_changed:
            logger.info(f"📝 Category changed by human: {original_category} → {effective_category} (build: {build_id})")

        # CATEGORY-BASED FLOW DECISION (uses effective_category)
        ai_analysis_id = None
        ai_triggered = False

        # Only trigger AI analysis for CODE_ERROR category
        # (needs to analyze XML reports, debug logs, console to find exact code line)
        if effective_category == 'CODE_ERROR':
            try:
                trigger_url = os.getenv('MANUAL_TRIGGER_URL', 'http://ddn-manual-trigger:5004')
                trigger_response = requests.post(
                    f"{trigger_url}/api/trigger-analysis",
                    json={
                        "build_id": build_id,
                        "triggered_by_user": reviewed_by,
                        "reason": f"CODE_ERROR approved - AI to analyze XML reports, console logs, find exact error line: {feedback}",
                        "trigger_source": "rag_code_error_approval"
                    },
                    timeout=120
                )
                trigger_response.raise_for_status()
                trigger_result = trigger_response.json()
                ai_analysis_id = trigger_result.get('analysis_result', {}).get('storage_id')
                ai_triggered = True
                logger.info(f"🤖 AI DEEP ANALYSIS triggered for CODE_ERROR (build: {build_id}, analysis_id: {ai_analysis_id})")
            except Exception as e:
                logger.error(f"AI trigger failed for CODE_ERROR: {e}")
        else:
            # Non-code errors: RAG already provided the solution, just mark resolved
            logger.info(f"✅ Non-code error ({effective_category}) approved - RAG solution accepted, NO AI analysis needed")

        # Update approval status (including category if changed)
        if category_changed:
            cursor.execute("""
                UPDATE rag_approval_queue
                SET review_status = 'approved', reviewed_by = %s,
                    reviewed_at = NOW(), review_feedback = %s,
                    ai_analysis_id = %s, error_category = %s,
                    original_category = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, build_id, error_category
            """, (reviewed_by, feedback, ai_analysis_id, effective_category, original_category, approval_id))
        else:
            cursor.execute("""
                UPDATE rag_approval_queue
                SET review_status = 'approved', reviewed_by = %s,
                    reviewed_at = NOW(), review_feedback = %s,
                    ai_analysis_id = %s, updated_at = NOW()
                WHERE id = %s
                RETURNING id, build_id, error_category
            """, (reviewed_by, feedback, ai_analysis_id, approval_id))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        # Response message based on category
        if effective_category == 'CODE_ERROR':
            message = 'CODE_ERROR approved → AI deep analysis triggered (analyzing XML, console, code)'
        else:
            message = f'{effective_category} approved → RAG solution accepted (no AI analysis needed)'

        if category_changed:
            message = f'Category changed ({original_category} → {effective_category}). ' + message

        logger.info(f"✅ RAG approved: {result['build_id']} by {reviewed_by} | Category: {effective_category} | Changed: {category_changed} | AI: {ai_triggered}")
        return jsonify({
            'success': True,
            'message': message,
            'approval_id': result['id'],
            'build_id': result['build_id'],
            'error_category': effective_category,
            'original_category': original_category if category_changed else None,
            'category_changed': category_changed,
            'ai_analysis_id': ai_analysis_id,
            'ai_triggered': ai_triggered
        }), 200

    except Exception as e:
        logger.error(f"Error approving RAG: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rag/reject', methods=['POST'])
def reject_rag():
    """Reject a RAG suggestion with feedback"""
    try:
        data = request.get_json()
        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        feedback = data.get('feedback', '')
        correct_category = data.get('correct_category')

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        full_feedback = f"{feedback} [Correct: {correct_category}]" if correct_category else feedback

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            UPDATE rag_approval_queue
            SET review_status = 'rejected', reviewed_by = %s,
                reviewed_at = NOW(), review_feedback = %s, updated_at = NOW()
            WHERE id = %s AND review_status = 'pending'
            RETURNING id, build_id
        """, (reviewed_by, full_feedback, approval_id))

        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Approval not found or already processed'}), 404

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"❌ RAG rejected for build {result['build_id']} by {reviewed_by}")
        return jsonify({
            'success': True,
            'message': 'RAG suggestion rejected',
            'approval_id': result['id'],
            'build_id': result['build_id']
        }), 200

    except Exception as e:
        logger.error(f"Error rejecting RAG: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rag/escalate', methods=['POST'])
def escalate_rag():
    """Escalate to AI for deeper analysis"""
    try:
        data = request.get_json()
        approval_id = data.get('approval_id')
        reviewed_by = data.get('reviewed_by', 'anonymous')
        reason = data.get('reason', 'Escalated for deeper AI analysis')

        if not approval_id:
            return jsonify({'success': False, 'error': 'approval_id required'}), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, build_id FROM rag_approval_queue
            WHERE id = %s AND review_status = 'pending'
        """, (approval_id,))
        approval = cursor.fetchone()

        if not approval:
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': 'Approval not found or already processed'}), 404

        build_id = approval['build_id']

        # Trigger AI analysis
        try:
            trigger_url = os.getenv('MANUAL_TRIGGER_URL', 'http://ddn-manual-trigger:5004')
            trigger_response = requests.post(
                f"{trigger_url}/api/trigger-analysis",
                json={
                    "build_id": build_id,
                    "triggered_by_user": reviewed_by,
                    "reason": f"Escalated from RAG: {reason}",
                    "trigger_source": "rag_escalation"
                },
                timeout=120
            )
            trigger_response.raise_for_status()
            trigger_result = trigger_response.json()
            ai_analysis_id = trigger_result.get('analysis_result', {}).get('storage_id')
        except Exception as e:
            logger.error(f"AI trigger failed: {e}")
            cursor.close()
            conn.close()
            return jsonify({'success': False, 'error': f'AI analysis failed: {str(e)}'}), 500

        cursor.execute("""
            UPDATE rag_approval_queue
            SET review_status = 'escalated', reviewed_by = %s, reviewed_at = NOW(),
                review_feedback = %s, escalated_to_ai = TRUE, ai_analysis_id = %s, updated_at = NOW()
            WHERE id = %s
        """, (reviewed_by, reason, ai_analysis_id, approval_id))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"🔄 RAG escalated to AI for build {build_id}")
        return jsonify({
            'success': True,
            'message': 'Escalated to AI analysis',
            'approval_id': approval_id,
            'build_id': build_id,
            'ai_analysis_id': ai_analysis_id
        }), 200

    except Exception as e:
        logger.error(f"Error escalating: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rag/stats', methods=['GET'])
def get_rag_stats():
    """Get RAG approval statistics"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE review_status = 'pending') as pending,
                COUNT(*) FILTER (WHERE review_status = 'approved') as approved,
                COUNT(*) FILTER (WHERE review_status = 'rejected') as rejected,
                COUNT(*) FILTER (WHERE review_status = 'escalated') as escalated,
                ROUND(AVG(rag_confidence)::numeric, 2) as avg_confidence
            FROM rag_approval_queue
        """)
        overall = cursor.fetchone()

        cursor.execute("""
            SELECT error_category, COUNT(*) as total,
                   COUNT(*) FILTER (WHERE review_status = 'approved') as approved,
                   ROUND(100.0 * COUNT(*) FILTER (WHERE review_status = 'approved') / NULLIF(COUNT(*), 0), 1) as approval_rate
            FROM rag_approval_queue GROUP BY error_category ORDER BY total DESC
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
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rag/history', methods=['GET'])
def get_rag_history():
    """Get RAG approval history (approved, rejected, escalated items)"""
    try:
        limit = int(request.args.get('limit', 50))
        status_filter = request.args.get('status')  # approved, rejected, escalated
        category = request.args.get('category')

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT id, build_id, job_name, error_category, original_category,
                   rag_suggestion, rag_confidence, review_status, reviewed_by,
                   reviewed_at, review_feedback, ai_analysis_id, trigger_type,
                   triggered_by, created_at
            FROM rag_approval_queue
            WHERE review_status != 'pending'
        """
        params = []

        if status_filter:
            query += " AND review_status = %s"
            params.append(status_filter)

        if category:
            query += " AND error_category = %s"
            params.append(category)

        query += " ORDER BY reviewed_at DESC NULLS LAST, created_at DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        history = cursor.fetchall()

        cursor.close()
        conn.close()

        # Format dates
        for item in history:
            if item.get('created_at'):
                item['created_at'] = item['created_at'].isoformat()
            if item.get('reviewed_at'):
                item['reviewed_at'] = item['reviewed_at'].isoformat()
            # Determine if category was changed
            item['category_changed'] = bool(item.get('original_category') and item['original_category'] != item['error_category'])

        return jsonify({
            'success': True,
            'count': len(history),
            'history': history
        }), 200

    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/rag/add', methods=['POST'])
def add_to_rag_queue():
    """Add a RAG result to approval queue (called when non-code error detected)"""
    try:
        data = request.get_json()
        build_id = data.get('build_id')
        if not build_id:
            return jsonify({'success': False, 'error': 'build_id required'}), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO rag_approval_queue (
                build_id, job_name, error_category, rag_suggestion,
                rag_confidence, similar_cases_count, similar_case_ids,
                trigger_type, triggered_by, review_status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """, (
            build_id,
            data.get('job_name', ''),
            data.get('error_category', 'UNKNOWN'),
            data.get('rag_suggestion', ''),
            float(data.get('rag_confidence', 0)),
            int(data.get('similar_cases_count', 0)),
            str(data.get('similar_case_ids', [])),
            data.get('trigger_type', 'MANUAL'),
            data.get('triggered_by', 'system')
        ))

        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"📋 Added build {build_id} to RAG queue (ID: {result['id']}, type: {data.get('trigger_type', 'MANUAL')})")
        return jsonify({
            'success': True,
            'approval_id': result['id'],
            'build_id': build_id,
            'trigger_type': data.get('trigger_type', 'MANUAL')
        }), 201

    except Exception as e:
        logger.error(f"Error adding to queue: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# AI CHATBOT API
# ============================================================================

# OpenAI client for chat
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    logger.info("✓ OpenAI client initialized")
except Exception as e:
    openai_client = None
    logger.warning(f"⚠ OpenAI client not available: {e}")


def get_system_context():
    """Get current system stats for AI context"""
    try:
        conn = get_postgres_connection()
        if not conn:
            return {}

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get failure stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_failures,
                COUNT(CASE WHEN analyzed_at IS NOT NULL THEN 1 END) as analyzed,
                COUNT(CASE WHEN DATE(created_at) = CURRENT_DATE THEN 1 END) as today_failures,
                AVG(confidence_score) as avg_confidence
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '7 days'
        """)
        stats = cursor.fetchone()

        # Get recent failures
        cursor.execute("""
            SELECT build_id, classification, confidence_score, created_at
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '24 hours'
            ORDER BY created_at DESC
            LIMIT 5
        """)
        recent = cursor.fetchall()

        # Get acceptance stats
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN validation_status = 'accepted' THEN 1 END) as accepted,
                COUNT(CASE WHEN validation_status = 'rejected' THEN 1 END) as rejected,
                COUNT(*) as total
            FROM acceptance_tracking
            WHERE validated_at > NOW() - INTERVAL '7 days'
        """)
        acceptance = cursor.fetchone()

        cursor.close()
        conn.close()

        acceptance_rate = 0
        if acceptance and acceptance['total'] > 0:
            acceptance_rate = round((acceptance['accepted'] / acceptance['total']) * 100, 1)

        return {
            'total_failures_7d': stats['total_failures'] if stats else 0,
            'analyzed_count': stats['analyzed'] if stats else 0,
            'today_failures': stats['today_failures'] if stats else 0,
            'avg_confidence': round(float(stats['avg_confidence'] or 0) * 100, 1) if stats else 0,
            'acceptance_rate': acceptance_rate,
            'recent_failures': [dict(r) for r in recent] if recent else []
        }
    except Exception as e:
        logger.error(f"Error getting system context: {e}")
        return {}


@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    AI Chatbot endpoint for natural language queries

    Request body:
    {
        "message": "Show me recent failures",
        "conversation_history": [...]  // Optional
    }

    Response:
    {
        "success": true,
        "response": "Here are the recent failures...",
        "data": {...}  // Optional structured data
    }
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Message required'}), 400

        user_message = data['message']
        conversation_history = data.get('conversation_history', [])

        # Get current system context
        context = get_system_context()

        # Build system prompt with real data
        system_prompt = f"""You are an AI Analysis Assistant for the DDN Test Failure Analysis Dashboard.
You help users understand test failures, generate reports, and get insights.

CURRENT SYSTEM STATUS:
- Failures in last 7 days: {context.get('total_failures_7d', 0)}
- Failures today: {context.get('today_failures', 0)}
- AI analyzed: {context.get('analyzed_count', 0)}
- Average AI confidence: {context.get('avg_confidence', 0)}%
- AI acceptance rate: {context.get('acceptance_rate', 0)}%

RECENT FAILURES (last 24h):
{chr(10).join([f"- Build {f.get('build_id')}: {f.get('classification')} ({round(float(f.get('confidence_score', 0)) * 100)}% confidence)" for f in context.get('recent_failures', [])[:5]])}

CAPABILITIES:
- Show failure statistics and trends
- Explain AI analysis results
- Provide recommendations for fixing errors
- Generate reports (mention this is available)
- Create Jira bugs from failures (mention this is available)
- Search for similar past errors

When answering:
1. Use the real data provided above
2. Format responses with markdown for readability
3. Be concise but informative
4. Suggest relevant follow-up actions
5. If asked for reports, mention PDF/Excel export is available in the UI"""

        if not openai_client:
            # Fallback response if OpenAI not available
            return jsonify({
                'success': True,
                'response': f"""Based on current system data:

**System Status:**
- Failures (7 days): {context.get('total_failures_7d', 0)}
- Today's failures: {context.get('today_failures', 0)}
- AI Acceptance Rate: {context.get('acceptance_rate', 0)}%

I can help you with failure analysis, reports, and recommendations.
Note: Full AI chat requires OpenAI API configuration.""",
                'data': context
            }), 200

        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 10 messages)
        for msg in conversation_history[-10:]:
            messages.append({
                "role": msg.get('role', 'user'),
                "content": msg.get('content', '')
            })

        # Add current message
        messages.append({"role": "user", "content": user_message})

        # Call OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        return jsonify({
            'success': True,
            'response': ai_response,
            'data': context,
            'model': 'gpt-4o-mini'
        }), 200

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'response': "I'm having trouble processing your request. Please try again."
        }), 500


@app.route('/api/chat/query', methods=['POST'])
def chat_query_endpoint():
    """
    Execute specific data queries from chat

    Request body:
    {
        "query_type": "failures" | "stats" | "patterns" | "acceptance",
        "params": {...}
    }
    """
    try:
        data = request.get_json()
        query_type = data.get('query_type', 'stats')
        params = data.get('params', {})

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)
        result = {}

        if query_type == 'failures':
            limit = params.get('limit', 10)
            cursor.execute("""
                SELECT build_id, job_name, classification, root_cause,
                       confidence_score, severity, created_at
                FROM failure_analysis
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            result['failures'] = [dict(r) for r in cursor.fetchall()]

        elif query_type == 'patterns':
            cursor.execute("""
                SELECT classification, COUNT(*) as count,
                       AVG(confidence_score) as avg_confidence
                FROM failure_analysis
                WHERE created_at > NOW() - INTERVAL '30 days'
                GROUP BY classification
                ORDER BY count DESC
                LIMIT 10
            """)
            result['patterns'] = [dict(r) for r in cursor.fetchall()]

        elif query_type == 'acceptance':
            cursor.execute("""
                SELECT
                    DATE(validated_at) as date,
                    COUNT(CASE WHEN validation_status = 'accepted' THEN 1 END) as accepted,
                    COUNT(CASE WHEN validation_status = 'rejected' THEN 1 END) as rejected
                FROM acceptance_tracking
                WHERE validated_at > NOW() - INTERVAL '30 days'
                GROUP BY DATE(validated_at)
                ORDER BY date DESC
            """)
            result['acceptance_trend'] = [dict(r) for r in cursor.fetchall()]

        else:  # stats
            result = get_system_context()

        cursor.close()
        conn.close()

        return jsonify({'success': True, 'data': result}), 200

    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# AGENTIC WORKFLOWS API (Python-based Workflows)
# ============================================================================

import json
import glob as glob_module

WORKFLOWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workflows')

@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """
    Get all Python-based agentic workflows

    Returns workflow definitions from JSON files with execution status
    """
    try:
        workflows = []
        workflow_files = glob_module.glob(os.path.join(WORKFLOWS_DIR, '*.json'))

        # Also try Docker path
        if not workflow_files:
            workflow_files = glob_module.glob('/app/workflows/*.json')

        for file_path in workflow_files:
            try:
                with open(file_path, 'r') as f:
                    workflow_data = json.load(f)

                # Extract key info from workflow
                name = workflow_data.get('name', os.path.basename(file_path))
                version = workflow_data.get('version', '1.0.0')
                description = workflow_data.get('description', '')
                nodes = workflow_data.get('nodes', [])

                # Count node types
                node_count = len(nodes)

                # Determine workflow type from name
                workflow_type = 'complete'
                if 'manual' in name.lower():
                    workflow_type = 'manual_trigger'
                elif 'refinement' in name.lower():
                    workflow_type = 'refinement'
                elif 'auto_fix' in name.lower():
                    workflow_type = 'auto_fix'

                workflows.append({
                    'id': os.path.basename(file_path).replace('.json', ''),
                    'name': name,
                    'version': version,
                    'description': description[:200] + '...' if len(description) > 200 else description,
                    'node_count': node_count,
                    'type': workflow_type,
                    'status': 'active',  # All defined workflows are active
                    'file_path': os.path.basename(file_path),
                    'updated_at': workflow_data.get('updatedAt', datetime.utcnow().isoformat()),
                    'tags': [t.get('name', '') for t in workflow_data.get('tags', [])]
                })
            except Exception as e:
                logger.warning(f"Error reading workflow {file_path}: {e}")
                continue

        # Get execution stats from database
        conn = get_postgres_connection()
        execution_stats = {'total': 0, 'successful': 0, 'failed': 0}

        if conn:
            try:
                cursor = conn.cursor(cursor_factory=RealDictCursor)

                # Get manual trigger stats as proxy for workflow executions
                cursor.execute("""
                    SELECT
                        COUNT(*) as total,
                        COUNT(CASE WHEN trigger_successful = true THEN 1 END) as successful,
                        COUNT(CASE WHEN trigger_successful = false THEN 1 END) as failed
                    FROM manual_trigger_log
                    WHERE triggered_at > NOW() - INTERVAL '30 days'
                """)
                stats = cursor.fetchone()
                if stats:
                    execution_stats = dict(stats)

                cursor.close()
                conn.close()
            except Exception as e:
                logger.warning(f"Error getting workflow stats: {e}")

        return jsonify({
            'success': True,
            'count': len(workflows),
            'workflows': workflows,
            'execution_stats': execution_stats
        }), 200

    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow_details(workflow_id):
    """Get detailed workflow definition"""
    try:
        # Try local path first
        file_path = os.path.join(WORKFLOWS_DIR, f'{workflow_id}.json')

        # Try Docker path
        if not os.path.exists(file_path):
            file_path = f'/app/workflows/{workflow_id}.json'

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': 'Workflow not found'}), 404

        with open(file_path, 'r') as f:
            workflow_data = json.load(f)

        return jsonify({
            'success': True,
            'workflow': workflow_data
        }), 200

    except Exception as e:
        logger.error(f"Error getting workflow details: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/workflows/executions', methods=['GET'])
def get_workflow_executions():
    """Get recent workflow executions (from manual trigger log)"""
    try:
        limit = int(request.args.get('limit', 20))

        conn = get_postgres_connection()
        if not conn:
            return jsonify({'success': False, 'error': 'Database connection failed'}), 500

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                mtl.id,
                mtl.build_id,
                mtl.triggered_by_user,
                mtl.trigger_source,
                mtl.trigger_successful,
                mtl.triggered_at,
                fa.classification as error_category,
                fa.confidence_score,
                CASE
                    WHEN fa.analyzed_at IS NOT NULL THEN 'completed'
                    WHEN mtl.trigger_successful = false THEN 'failed'
                    ELSE 'running'
                END as status
            FROM manual_trigger_log mtl
            LEFT JOIN failure_analysis fa ON mtl.analysis_id = fa.id
            ORDER BY mtl.triggered_at DESC
            LIMIT %s
        """, (limit,))

        executions = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert datetimes
        for ex in executions:
            if ex.get('triggered_at'):
                ex['triggered_at'] = ex['triggered_at'].isoformat()

        return jsonify({
            'success': True,
            'count': len(executions),
            'executions': [dict(e) for e in executions]
        }), 200

    except Exception as e:
        logger.error(f"Error getting workflow executions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
