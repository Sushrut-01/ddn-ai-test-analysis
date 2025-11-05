"""
MongoDB-Only Dashboard API
Temporary solution until PostgreSQL is installed
Reads test failures directly from MongoDB Atlas
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend at localhost:5173

# MongoDB Atlas Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests?retryWrites=true&w=majority')
MONGODB_DB = os.getenv('MONGODB_DB', 'ddn_tests')

print("=" * 80)
print("MongoDB-Only Dashboard API")
print("=" * 80)
print(f"MongoDB URI: {MONGODB_URI[:50]}...")
print(f"Database: {MONGODB_DB}")
print("=" * 80)

# Connect to MongoDB
try:
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    failures_collection = db['test_failures']

    # Test connection
    client.admin.command('ping')
    count = failures_collection.count_documents({})
    print(f"[OK] Connected to MongoDB Atlas")
    print(f"[OK] Found {count} test failures")
    print("=" * 80)
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    print("=" * 80)


def serialize_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if doc is None:
        return None

    if '_id' in doc:
        doc['_id'] = str(doc['_id'])

    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            doc[key] = str(value)

    return doc


# ==================== HEALTH CHECK ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        client.admin.command('ping')
        count = failures_collection.count_documents({})

        return jsonify({
            'status': 'healthy',
            'service': 'mongodb-dashboard-api',
            'port': 5005,
            'mongodb_connected': True,
            'total_failures': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


# ==================== ANALYTICS ENDPOINTS ====================

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Get analytics summary for dashboard"""
    try:
        time_range = request.args.get('time_range', '7d')

        # Calculate date range
        days = 7 if time_range == '7d' else (30 if time_range == '30d' else 90)
        start_date = datetime.now() - timedelta(days=days)

        # Total failures in time range
        total_failures = failures_collection.count_documents({
            'timestamp': {'$gte': start_date}
        })

        # Group by category
        pipeline_category = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {'$group': {
                '_id': '$test_category',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        categories = list(failures_collection.aggregate(pipeline_category))

        # Group by build
        unique_builds = failures_collection.distinct('build_id', {'timestamp': {'$gte': start_date}})

        # Recent failures
        recent = list(failures_collection.find({'timestamp': {'$gte': start_date}})
                     .sort('timestamp', -1)
                     .limit(10))

        return jsonify({
            'status': 'success',
            'data': {
                'overview': {
                    'total_failures': total_failures,
                    'unique_builds': len(unique_builds),
                    'avg_confidence': 0,  # Not available without AI analysis
                    'success_rate': 0,
                    'avg_resolution_time_seconds': 0
                },
                'categories': [serialize_doc(c) for c in categories],
                'trends': [],  # Would need daily aggregation
                'recent_failures': [serialize_doc(r) for r in recent]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/analytics/trends', methods=['GET'])
def get_failure_trends():
    """Get failure trends over time"""
    try:
        time_range = request.args.get('time_range', '30d')
        days = 7 if time_range == '7d' else (30 if time_range == '30d' else 90)
        start_date = datetime.now() - timedelta(days=days)

        # Group by date
        pipeline = [
            {'$match': {'timestamp': {'$gte': start_date}}},
            {'$group': {
                '_id': {
                    '$dateToString': {
                        'format': '%Y-%m-%d',
                        'date': '$timestamp'
                    }
                },
                'total_failures': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]

        trends = list(failures_collection.aggregate(pipeline))

        return jsonify({
            'status': 'success',
            'data': {
                'trends': [serialize_doc(t) for t in trends]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== FAILURES ENDPOINTS ====================

@app.route('/api/failures', methods=['GET'])
def get_failures():
    """Get paginated list of failures"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category', None)

        # Build query
        query = {}
        if category:
            query['test_category'] = category

        # Get total count
        total = failures_collection.count_documents(query)

        # Get paginated results
        offset = (page - 1) * limit
        failures = list(failures_collection.find(query)
                       .sort('timestamp', -1)
                       .skip(offset)
                       .limit(limit))

        return jsonify({
            'status': 'success',
            'data': {
                'failures': [serialize_doc(f) for f in failures],
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
    """Get failure details for a specific build"""
    try:
        failures = list(failures_collection.find({'build_id': build_id})
                       .sort('timestamp', -1))

        if not failures:
            return jsonify({
                'status': 'error',
                'message': 'Build not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {
                'failure': serialize_doc(failures[0]),
                'feedback': [],  # Not available without PostgreSQL
                'full_context': {
                    'console_log': None,
                    'error_details': serialize_doc(failures[0]),
                    'test_results': None,
                    'system_info': None
                }
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== STATUS ENDPOINTS ====================

@app.route('/api/status/live', methods=['GET'])
def get_live_status():
    """Get real-time system status"""
    try:
        yesterday = datetime.now() - timedelta(days=1)

        failures_24h = failures_collection.count_documents({
            'timestamp': {'$gte': yesterday}
        })

        latest = failures_collection.find_one(
            {},
            sort=[('timestamp', -1)]
        )

        return jsonify({
            'status': 'success',
            'data': {
                'activity_24h': {
                    'failures_24h': failures_24h,
                    'successes_24h': 0,
                    'avg_confidence_24h': None
                },
                'latest_failure': serialize_doc(latest) if latest else None,
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==================== STUB ENDPOINTS ====================
# These endpoints return empty data until PostgreSQL is available

@app.route('/api/analytics/patterns', methods=['GET'])
def get_failure_patterns():
    """Placeholder - needs PostgreSQL"""
    return jsonify({
        'status': 'success',
        'data': {'patterns': []}
    })


@app.route('/api/trigger/manual', methods=['POST'])
def trigger_manual_analysis():
    """Placeholder - needs AI service"""
    return jsonify({
        'status': 'success',
        'message': 'Manual trigger not available yet - AI service not running'
    })


@app.route('/api/trigger/history', methods=['GET'])
def get_trigger_history():
    """Placeholder - needs PostgreSQL"""
    return jsonify({
        'status': 'success',
        'data': {'triggers': [], 'pagination': {'page': 1, 'limit': 20, 'total': 0, 'pages': 0}}
    })


@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    """Placeholder - needs PostgreSQL"""
    return jsonify({
        'status': 'success',
        'message': 'Feedback submission not available yet - PostgreSQL not installed'
    })


@app.route('/api/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """Placeholder - needs PostgreSQL"""
    return jsonify({
        'status': 'success',
        'data': {'feedback': []}
    })


@app.route('/api/metrics/model', methods=['GET'])
def get_model_metrics():
    """Placeholder - needs PostgreSQL"""
    return jsonify({
        'status': 'success',
        'data': {'metrics': []}
    })


# ==================== MAIN ====================

if __name__ == '__main__':
    print("\nStarting MongoDB-Only Dashboard API...")
    print(f"Dashboard will be available at: http://localhost:5005")
    print(f"Frontend should connect from: http://localhost:5173")
    print()
    print("NOTE: This is a temporary solution")
    print("      Some features require PostgreSQL (waiting for IT approval)")
    print("      Currently showing test failures from MongoDB Atlas only")
    print()
    print("=" * 80)

    app.run(host='0.0.0.0', port=5005, debug=True)
