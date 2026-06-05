"""
Project-Scoped Endpoints
Add these routes to your dashboard_api_full.py to support multi-project filtering
"""

from flask import Blueprint, request, jsonify, g
from project_api import require_project_access, get_db_connection
from psycopg2.extras import RealDictCursor

# Create Blueprint
scoped_bp = Blueprint('project_scoped', __name__)

# ============================================
# PROJECT-SCOPED FAILURES API
# ============================================

@scoped_bp.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_project_access(required_role='viewer')
def get_project_failures(project_id):
    """Get failures for specific project"""
    # Pagination
    limit = int(request.args.get('limit', 50))
    skip = int(request.args.get('skip', 0))

    # Filters
    category = request.args.get('category')
    feedback_status = request.args.get('feedback_status')
    search = request.args.get('search')
    build_id = request.args.get('build_id')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Build query with project isolation
    query = """
        SELECT
            fa.id,
            fa.build_id,
            fa.error_message,
            fa.classification,
            fa.confidence_score,
            fa.root_cause,
            fa.suggested_fix,
            fa.feedback_status,
            fa.created_at,
            bm.job_name,
            bm.build_url,
            bm.status as build_status
        FROM failure_analysis fa
        LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id AND fa.project_id = bm.project_id
        WHERE fa.project_id = %s
    """
    params = [project_id]

    if category:
        query += " AND fa.classification = %s"
        params.append(category)

    if feedback_status:
        query += " AND fa.feedback_status = %s"
        params.append(feedback_status)

    if search:
        query += " AND (fa.error_message ILIKE %s OR fa.root_cause ILIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    if build_id:
        query += " AND fa.build_id = %s"
        params.append(build_id)

    query += " ORDER BY fa.created_at DESC LIMIT %s OFFSET %s"
    params.extend([limit, skip])

    cur.execute(query, params)

    failures = []
    for row in cur.fetchall():
        failures.append({
            'id': row['id'],
            'build_id': row['build_id'],
            'error_message': row['error_message'],
            'classification': row['classification'],
            'confidence_score': float(row['confidence_score']) if row['confidence_score'] else 0.0,
            'root_cause': row['root_cause'],
            'suggested_fix': row['suggested_fix'],
            'feedback_status': row['feedback_status'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'job_name': row['job_name'],
            'build_url': row['build_url'],
            'build_status': row['build_status']
        })

    # Get total count
    cur.execute("SELECT COUNT(*) as total FROM failure_analysis WHERE project_id = %s", (project_id,))
    total_count = cur.fetchone()['total']

    cur.close()
    conn.close()

    return jsonify({
        'failures': failures,
        'total': total_count,
        'limit': limit,
        'skip': skip,
        'project_id': project_id,
        'project_name': g.project_name
    })

@scoped_bp.route('/api/projects/<int:project_id>/failures/<int:failure_id>', methods=['GET'])
@require_project_access(required_role='viewer')
def get_failure_details(project_id, failure_id):
    """Get detailed failure information"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT fa.*, bm.job_name, bm.build_url, bm.status as build_status
        FROM failure_analysis fa
        LEFT JOIN build_metadata bm ON fa.build_id = bm.build_id AND fa.project_id = bm.project_id
        WHERE fa.id = %s AND fa.project_id = %s
    """, (failure_id, project_id))

    failure = cur.fetchone()

    cur.close()
    conn.close()

    if not failure:
        return jsonify({'error': 'Failure not found'}), 404

    return jsonify({'failure': dict(failure)})

# ============================================
# PROJECT-SCOPED BUILDS API
# ============================================

@scoped_bp.route('/api/projects/<int:project_id>/builds/summary', methods=['GET'])
@require_project_access(required_role='viewer')
def get_builds_summary(project_id):
    """Get build summary for project"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Total builds
    cur.execute("""
        SELECT COUNT(*) as total
        FROM build_metadata
        WHERE project_id = %s
    """, (project_id,))
    total_builds = cur.fetchone()['total']

    # Recent builds
    cur.execute("""
        SELECT build_id, job_name, status, build_url, created_at
        FROM build_metadata
        WHERE project_id = %s
        ORDER BY created_at DESC
        LIMIT 10
    """, (project_id,))

    recent_builds = [dict(row) for row in cur.fetchall()]

    # Status breakdown
    cur.execute("""
        SELECT status, COUNT(*) as count
        FROM build_metadata
        WHERE project_id = %s
        GROUP BY status
    """, (project_id,))

    status_breakdown = {row['status']: row['count'] for row in cur.fetchall()}

    cur.close()
    conn.close()

    return jsonify({
        'total_builds': total_builds,
        'recent_builds': recent_builds,
        'status_breakdown': status_breakdown,
        'project_id': project_id
    })

# ============================================
# PROJECT-SCOPED JIRA API
# ============================================

@scoped_bp.route('/api/projects/<int:project_id>/jira/create-issue', methods=['POST'])
@require_project_access(required_role='developer')
def create_jira_issue_for_project(project_id):
    """Create Jira issue in project's Jira"""
    data = request.json
    user_id = g.user_id

    # Get project configuration
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT jira_project_key, jira_url, jira_email, jira_api_token
        FROM project_configurations
        WHERE project_id = %s
    """, (project_id,))

    config = cur.fetchone()

    if not config or not config['jira_project_key']:
        cur.close()
        conn.close()
        return jsonify({
            'error': 'Jira not configured for this project',
            'project_name': g.project_name
        }), 400

    # Here you would integrate with actual Jira API
    # For now, we'll just log it to database

    try:
        cur.execute("""
            INSERT INTO jira_bugs (
                project_id, jira_key, summary, description, priority,
                status, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id
        """, (
            project_id,
            f"{config['jira_project_key']}-{data.get('id', 'NEW')}",
            data.get('summary', ''),
            data.get('description', ''),
            data.get('priority', 'Medium'),
            'Open',
            user_id
        ))

        jira_bug_id = cur.fetchone()['id']
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'jira_key': f"{config['jira_project_key']}-{jira_bug_id}",
            'message': 'Jira issue created'
        }), 201

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@scoped_bp.route('/api/projects/<int:project_id>/jira/bugs', methods=['GET'])
@require_project_access(required_role='viewer')
def get_project_jira_bugs(project_id):
    """Get Jira bugs for project"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT *
        FROM jira_bugs
        WHERE project_id = %s
        ORDER BY created_at DESC
    """, (project_id,))

    bugs = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        'bugs': bugs,
        'count': len(bugs),
        'project_id': project_id
    })

# ============================================
# PROJECT-SCOPED ANALYTICS API
# ============================================

@scoped_bp.route('/api/projects/<int:project_id>/analytics/summary', methods=['GET'])
@require_project_access(required_role='viewer')
def get_analytics_summary(project_id):
    """Get analytics summary for project"""
    time_range = request.args.get('time_range', '7d')

    # Extract days from time_range (e.g., "7d" -> 7)
    days = int(time_range.replace('d', ''))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Total failures
    cur.execute("""
        SELECT COUNT(*) as total
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
    """, (project_id, days))
    total_failures = cur.fetchone()['total']

    # Average confidence score
    cur.execute("""
        SELECT AVG(confidence_score) as avg_confidence
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
    """, (project_id, days))
    avg_confidence = cur.fetchone()['avg_confidence'] or 0.0

    # Top categories
    cur.execute("""
        SELECT classification, COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY classification
        ORDER BY count DESC
        LIMIT 5
    """, (project_id, days))

    top_categories = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        'total_failures': total_failures,
        'avg_confidence': float(avg_confidence),
        'top_categories': top_categories,
        'time_range': time_range,
        'project_id': project_id
    })

@scoped_bp.route('/api/projects/<int:project_id>/analytics/trends', methods=['GET'])
@require_project_access(required_role='viewer')
def get_analytics_trends(project_id):
    """Get analytics trends for project"""
    time_range = request.args.get('time_range', '30d')
    days = int(time_range.replace('d', ''))

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            DATE(created_at) as date,
            COUNT(*) as count,
            AVG(confidence_score) as avg_confidence
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """, (project_id, days))

    trends = []
    for row in cur.fetchall():
        trends.append({
            'date': row['date'].isoformat(),
            'count': row['count'],
            'avg_confidence': float(row['avg_confidence']) if row['avg_confidence'] else 0.0
        })

    cur.close()
    conn.close()

    return jsonify({
        'trends': trends,
        'project_id': project_id
    })

# ============================================
# PROJECT-SCOPED PIPELINE API
# ============================================

@scoped_bp.route('/api/projects/<int:project_id>/pipeline/flow', methods=['GET'])
@require_project_access(required_role='viewer')
def get_pipeline_flow(project_id):
    """Get pipeline flow status for project"""
    # This is a placeholder - implement based on your pipeline structure
    return jsonify({
        'project_id': project_id,
        'project_name': g.project_name,
        'pipeline': {
            'status': 'active',
            'stages': [
                {'name': 'Test Execution', 'status': 'success'},
                {'name': 'Failure Detection', 'status': 'success'},
                {'name': 'AI Analysis', 'status': 'in_progress'},
                {'name': 'Jira Creation', 'status': 'pending'}
            ]
        }
    })
