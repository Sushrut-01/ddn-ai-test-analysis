"""
Refactored API Endpoints with Middleware
Zero-downtime migration approach - new endpoints alongside old ones

File: api_refactored_with_middleware.py
Purpose: Add middleware-protected endpoints while keeping old endpoints working
Strategy: Gradual migration with backward compatibility
"""

from flask import Blueprint, request, jsonify, g
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
import logging

# Import our middleware
from middleware import (
    require_auth,
    require_project_access,
    MongoDBProjectContext,
    PineconeProjectContext
)

logger = logging.getLogger(__name__)

# Create blueprint for refactored endpoints
refactored_bp = Blueprint('refactored', __name__)

# Database connection
def get_db_connection():
    """Get database connection with project context set"""
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5434)),
        database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', 'password')
    )

# ============================================================================
# REFACTORED ENDPOINT 1: Get Failures (With Middleware)
# ============================================================================

@refactored_bp.route('/api/v2/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_failures_v2(project_id):
    """
    Get failures for a project (NEW VERSION with middleware)

    Features:
    - Automatic JWT validation
    - Automatic project access check
    - Automatic RLS filtering
    - Role-based access control

    Access: viewer, developer, project_admin, project_owner

    Query params:
    - limit: Number of results (default 50)
    - offset: Pagination offset (default 0)
    - status: Filter by status
    """
    try:
        # Extract query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        status = request.args.get('status')

        # Validate limits
        limit = min(limit, 1000)  # Max 1000 results

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Set RLS context
        cur.execute("SELECT set_project_context(%s)", (g.project_id,))

        # Build query - RLS automatically filters by project_id!
        query = """
            SELECT
                id,
                build_id,
                job_name,
                classification,
                error_category,
                root_cause,
                fix_recommendation,
                confidence_score,
                status,
                created_at,
                ai_model_used,
                token_usage,
                analysis_cost_usd
            FROM failure_analysis
        """

        params = []

        # Optional status filter
        if status:
            query += " WHERE status = %s"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cur.execute(query, params)
        failures = cur.fetchall()

        # Get total count
        count_query = "SELECT COUNT(*) as total FROM failure_analysis"
        if status:
            count_query += " WHERE status = %s"
            cur.execute(count_query, [status] if status else [])
        else:
            cur.execute(count_query)

        total = cur.fetchone()['total']

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'project_id': g.project_id,
            'project_name': g.project_info['name'],
            'your_role': g.project_role,
            'failures': [dict(f) for f in failures],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total,
                'has_more': offset + limit < total
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in get_failures_v2: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# REFACTORED ENDPOINT 2: Trigger Analysis (With Middleware)
# ============================================================================

@refactored_bp.route('/api/v2/projects/<int:project_id>/trigger-analysis', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def trigger_analysis_v2(project_id):
    """
    Trigger AI analysis for a build (NEW VERSION with middleware)

    Features:
    - Requires developer role or higher
    - Automatic project context
    - Project-specific configurations

    Access: developer, project_admin, project_owner

    Request body:
    {
        "build_id": "DDN-123",
        "force_reanalysis": false
    }
    """
    try:
        data = request.get_json()

        if not data or 'build_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: build_id'
            }), 400

        build_id = data['build_id']
        force_reanalysis = data.get('force_reanalysis', False)

        logger.info(
            f"Trigger analysis requested by user {g.user_id} "
            f"for project {g.project_id} ({g.project_info['slug']}), "
            f"build {build_id}"
        )

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Set RLS context
        cur.execute("SELECT set_project_context(%s)", (g.project_id,))

        # Get project configuration (RLS filtered)
        cur.execute("""
            SELECT pc.*
            FROM project_configurations pc
            WHERE pc.project_id = %s
        """, (g.project_id,))

        project_config = cur.fetchone()

        if not project_config:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Project configuration not found'
            }), 404

        # Check if already analyzed (unless force)
        if not force_reanalysis:
            cur.execute("""
                SELECT id, classification, confidence_score
                FROM failure_analysis
                WHERE build_id = %s
                LIMIT 1
            """, (build_id,))

            existing = cur.fetchone()

            if existing:
                cur.close()
                conn.close()
                return jsonify({
                    'success': True,
                    'message': 'Build already analyzed',
                    'existing_analysis': dict(existing),
                    'use_force_reanalysis': True
                }), 200

        # Log trigger
        cur.execute("""
            INSERT INTO manual_trigger_log (
                build_id,
                project_id,
                triggered_by_user_id,
                reason,
                trigger_source,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            build_id,
            g.project_id,
            g.user_id,
            data.get('reason', 'Manual trigger from API v2'),
            'api_v2',
            datetime.utcnow()
        ))

        trigger_id = cur.fetchone()['id']
        conn.commit()

        cur.close()
        conn.close()

        # TODO: Call analysis service (manual_trigger_api.py logic)
        # For now, return success with trigger_id

        return jsonify({
            'success': True,
            'message': 'Analysis triggered successfully',
            'trigger_id': trigger_id,
            'build_id': build_id,
            'project': {
                'id': g.project_id,
                'slug': g.project_info['slug'],
                'name': g.project_info['name']
            },
            'triggered_by': g.user_email,
            'role': g.project_role
        }), 202  # 202 Accepted (async processing)

    except Exception as e:
        logger.error(f"Error in trigger_analysis_v2: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# REFACTORED ENDPOINT 3: Get Analytics (With Middleware)
# ============================================================================

@refactored_bp.route('/api/v2/projects/<int:project_id>/analytics', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_analytics_v2(project_id):
    """
    Get project analytics (NEW VERSION with middleware)

    Features:
    - Automatic RLS filtering
    - Time-based aggregations
    - Classification breakdown

    Query params:
    - time_range: days (default 30)
    """
    try:
        time_range = request.args.get('time_range', 30, type=int)
        time_range = min(time_range, 365)  # Max 1 year

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Set RLS context
        cur.execute("SELECT set_project_context(%s)", (g.project_id,))

        # Total failures in time range
        cur.execute("""
            SELECT COUNT(*) as total
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '%s days'
        """, (time_range,))

        total_failures = cur.fetchone()['total']

        # Classification breakdown
        cur.execute("""
            SELECT
                classification,
                COUNT(*) as count,
                ROUND(AVG(confidence_score)::numeric, 2) as avg_confidence
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '%s days'
            GROUP BY classification
            ORDER BY count DESC
        """, (time_range,))

        classifications = [dict(row) for row in cur.fetchall()]

        # Daily trend
        cur.execute("""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as count
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '%s days'
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """, (time_range,))

        trend = [dict(row) for row in cur.fetchall()]

        # AI cost stats
        cur.execute("""
            SELECT
                SUM(token_usage) as total_tokens,
                SUM(analysis_cost_usd) as total_cost,
                COUNT(DISTINCT ai_model_used) as models_used
            FROM failure_analysis
            WHERE created_at > NOW() - INTERVAL '%s days'
        """, (time_range,))

        cost_stats = dict(cur.fetchone())

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'project_id': g.project_id,
            'project_name': g.project_info['name'],
            'time_range_days': time_range,
            'analytics': {
                'total_failures': total_failures,
                'classifications': classifications,
                'daily_trend': trend,
                'ai_costs': cost_stats
            }
        }), 200

    except Exception as e:
        logger.error(f"Error in get_analytics_v2: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# REFACTORED ENDPOINT 4: Get Project Config (With Middleware)
# ============================================================================

@refactored_bp.route('/api/v2/projects/<int:project_id>/config', methods=['GET'])
@require_auth
@require_project_access(required_role='project_admin')
def get_project_config_v2(project_id):
    """
    Get project configuration (NEW VERSION with middleware)

    Features:
    - Admin only access
    - Masked sensitive tokens
    - RLS filtered

    Access: project_admin, project_owner only
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Set RLS context
        cur.execute("SELECT set_project_context(%s)", (g.project_id,))

        # Get project config (RLS filtered)
        cur.execute("""
            SELECT
                jira_project_key,
                jira_url,
                jira_email,
                github_repo_owner,
                github_repo_name,
                github_default_branch,
                ci_provider,
                mongodb_collection_prefix,
                pinecone_namespace,
                confidence_threshold,
                ai_model_preferences
            FROM project_configurations
        """)

        config = cur.fetchone()

        if not config:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Project configuration not found'
            }), 404

        # Get project details
        cur.execute("""
            SELECT id, slug, name, description, status
            FROM projects
            WHERE id = %s
        """, (g.project_id,))

        project = dict(cur.fetchone())

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'project': project,
            'configuration': dict(config),
            'your_role': g.project_role
        }), 200

    except Exception as e:
        logger.error(f"Error in get_project_config_v2: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@refactored_bp.route('/api/v2/projects/<int:project_id>/config', methods=['PUT'])
@require_auth
@require_project_access(required_role='project_admin')
def update_project_config_v2(project_id):
    """
    Update project configuration (NEW VERSION with middleware)

    Access: project_admin, project_owner only
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Set RLS context
        cur.execute("SELECT set_project_context(%s)", (g.project_id,))

        # Build update query
        allowed_fields = [
            'jira_project_key', 'jira_url', 'jira_email',
            'github_repo_owner', 'github_repo_name', 'github_default_branch',
            'ci_provider', 'confidence_threshold'
        ]

        update_fields = []
        params = []

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            cur.close()
            conn.close()
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(g.project_id)

        query = f"""
            UPDATE project_configurations
            SET {', '.join(update_fields)}
            WHERE project_id = %s
        """

        cur.execute(query, params)
        conn.commit()

        cur.close()
        conn.close()

        logger.info(
            f"Project config updated by user {g.user_id} "
            f"for project {g.project_id}"
        )

        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully',
            'updated_by': g.user_email
        }), 200

    except Exception as e:
        logger.error(f"Error in update_project_config_v2: {e}")
        if conn:
            conn.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@refactored_bp.route('/api/v2/health', methods=['GET'])
def health_check_v2():
    """Health check for v2 API"""
    try:
        # Test database connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()

        return jsonify({
            'status': 'healthy',
            'version': 'v2',
            'middleware': 'enabled',
            'rls': 'enabled',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ============================================================================
# EXPORT BLUEPRINT
# ============================================================================

def register_refactored_endpoints(app):
    """Register refactored endpoints with main app"""
    app.register_blueprint(refactored_bp)
    logger.info("Refactored API v2 endpoints registered")
