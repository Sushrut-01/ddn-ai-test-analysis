"""
Project Management API
Handles multi-project support with complete CRUD operations
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import jwt
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Blueprint
project_bp = Blueprint('projects', __name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=int(os.getenv('POSTGRES_PORT', 5432)),
        database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', '')
    )

JWT_SECRET = os.getenv('JWT_SECRET_KEY', os.getenv('JWT_SECRET', 'your-secret-key-change-in-production'))

# ============================================
# MIDDLEWARE: Project Access Control
# ============================================

def require_project_access(required_role=None):
    """
    Decorator to validate project access and role

    Args:
        required_role: Minimum role required (viewer, developer, project_admin, project_owner)

    Role Hierarchy:
        project_owner > project_admin > developer > viewer > guest
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract project_id from URL
            project_id = kwargs.get('project_id')

            if not project_id:
                return jsonify({'error': 'project_id required in URL'}), 400

            # Get user from JWT token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')

            if not token:
                return jsonify({'error': 'Authorization token required'}), 401

            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                user_id = payload['user_id']
            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401

            # Check project access
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            cur.execute("""
                SELECT up.role, up.permissions, p.slug, p.name, p.status
                FROM user_projects up
                JOIN projects p ON up.project_id = p.id
                WHERE up.user_id = %s AND up.project_id = %s
            """, (user_id, project_id))

            result = cur.fetchone()

            if not result:
                cur.close()
                conn.close()
                return jsonify({'error': 'Access denied to this project'}), 403

            role = result['role']
            permissions = result['permissions']
            project_slug = result['slug']
            project_name = result['name']
            project_status = result['status']

            # Check if project is active
            if project_status != 'active':
                cur.close()
                conn.close()
                return jsonify({'error': f'Project is {project_status}'}), 403

            # Role hierarchy check
            role_hierarchy = {
                'guest': 0,
                'viewer': 1,
                'developer': 2,
                'project_admin': 3,
                'project_owner': 4
            }

            if required_role:
                user_role_level = role_hierarchy.get(role, 0)
                required_role_level = role_hierarchy.get(required_role, 0)

                if user_role_level < required_role_level:
                    cur.close()
                    conn.close()
                    return jsonify({
                        'error': f'Requires {required_role} role',
                        'your_role': role
                    }), 403

            # Store in request context
            g.project_id = project_id
            g.user_id = user_id
            g.project_role = role
            g.project_permissions = permissions
            g.project_slug = project_slug
            g.project_name = project_name

            # Update last accessed time
            cur.execute("""
                UPDATE user_projects
                SET last_accessed_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND project_id = %s
            """, (user_id, project_id))
            conn.commit()

            cur.close()
            conn.close()

            return f(*args, **kwargs)

        return decorated_function
    return decorator

def require_auth(f):
    """Basic authentication check"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({'error': 'Authorization token required'}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            g.user_id = payload['user_id']
            g.user_email = payload.get('email')
            g.user_role = payload.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated_function

# ============================================
# PROJECT MANAGEMENT ENDPOINTS
# ============================================

@project_bp.route('/api/projects', methods=['GET'])
@require_auth
def get_user_projects():
    """Get all projects accessible to current user"""
    user_id = g.user_id

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            p.id,
            p.slug,
            p.name,
            p.description,
            p.status,
            up.role as my_role,
            up.permissions as my_permissions,
            up.last_accessed_at,
            up.joined_at,
            (
                SELECT COUNT(*)
                FROM failure_analysis fa
                WHERE fa.project_id = p.id
                AND fa.created_at > NOW() - INTERVAL '30 days'
            ) as recent_failure_count
        FROM projects p
        JOIN user_projects up ON p.id = up.project_id
        WHERE up.user_id = %s AND p.status = 'active'
        ORDER BY up.last_accessed_at DESC NULLS LAST, p.created_at DESC
    """, (user_id,))

    projects = []
    for row in cur.fetchall():
        projects.append({
            'id': row['id'],
            'slug': row['slug'],
            'name': row['name'],
            'description': row['description'],
            'status': row['status'],
            'my_role': row['my_role'],
            'my_permissions': row['my_permissions'],
            'last_accessed': row['last_accessed_at'].isoformat() if row['last_accessed_at'] else None,
            'joined_at': row['joined_at'].isoformat() if row['joined_at'] else None,
            'recent_failure_count': row['recent_failure_count']
        })

    cur.close()
    conn.close()

    return jsonify({'projects': projects, 'count': len(projects)})

@project_bp.route('/api/projects', methods=['POST'])
@require_auth
def create_project():
    """Create new project (any authenticated user can create)"""
    data = request.json
    user_id = g.user_id

    # Validate required fields
    if not data.get('name') or not data.get('slug'):
        return jsonify({'error': 'name and slug are required'}), 400

    # Validate slug format (lowercase, alphanumeric, hyphens only)
    import re
    if not re.match(r'^[a-z0-9-]+$', data['slug']):
        return jsonify({'error': 'slug must contain only lowercase letters, numbers, and hyphens'}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Create project
        cur.execute("""
            INSERT INTO projects (slug, name, description, created_by, status)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (data['slug'], data['name'], data.get('description', ''), user_id, 'active'))

        project_id = cur.fetchone()['id']

        # Add creator as project_owner
        cur.execute("""
            INSERT INTO user_projects (user_id, project_id, role, invited_by)
            VALUES (%s, %s, 'project_owner', %s)
        """, (user_id, project_id, user_id))

        # Create default configuration
        cur.execute("""
            INSERT INTO project_configurations (
                project_id,
                mongodb_collection_prefix,
                pinecone_namespace,
                confidence_threshold
            ) VALUES (%s, %s, %s, %s)
        """, (project_id, f"{data['slug']}_", f"{data['slug']}_knowledge", 0.70))

        # Log activity
        cur.execute("""
            INSERT INTO project_activity_log (
                project_id, user_id, activity_type, action, new_values
            ) VALUES (%s, %s, 'project_created', 'create', %s)
        """, (project_id, user_id, psycopg2.extras.Json({'name': data['name'], 'slug': data['slug']})))

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': 'Project created successfully'
        }), 201

    except psycopg2.IntegrityError as e:
        conn.rollback()
        cur.close()
        conn.close()

        if 'unique' in str(e).lower() and 'slug' in str(e).lower():
            return jsonify({'error': 'Project slug already exists'}), 409
        return jsonify({'error': 'Failed to create project'}), 500

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@project_bp.route('/api/projects/<int:project_id>', methods=['GET'])
@require_project_access()
def get_project_details(project_id):
    """Get detailed project information"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Project details
    cur.execute("""
        SELECT p.*, pc.jira_project_key, pc.github_repo_owner, pc.github_repo_name,
               pc.ci_provider, pc.confidence_threshold
        FROM projects p
        LEFT JOIN project_configurations pc ON p.id = pc.project_id
        WHERE p.id = %s
    """, (project_id,))

    project = cur.fetchone()

    if not project:
        cur.close()
        conn.close()
        return jsonify({'error': 'Project not found'}), 404

    # Team members
    cur.execute("""
        SELECT u.id, u.email, u.name, up.role, up.joined_at, up.last_accessed_at
        FROM users u
        JOIN user_projects up ON u.id = up.user_id
        WHERE up.project_id = %s
        ORDER BY up.joined_at
    """, (project_id,))

    team = []
    for row in cur.fetchall():
        team.append({
            'id': row['id'],
            'email': row['email'],
            'name': row['name'],
            'role': row['role'],
            'joined_at': row['joined_at'].isoformat() if row['joined_at'] else None,
            'last_accessed_at': row['last_accessed_at'].isoformat() if row['last_accessed_at'] else None
        })

    cur.close()
    conn.close()

    return jsonify({
        'project': dict(project),
        'team': team,
        'my_role': g.project_role
    })

@project_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
@require_project_access(required_role='project_admin')
def update_project(project_id):
    """Update project details (admin only)"""
    data = request.json
    user_id = g.user_id

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Build update query
        update_fields = []
        params = []

        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])

        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])

        if 'status' in data and data['status'] in ['active', 'archived', 'suspended']:
            update_fields.append("status = %s")
            params.append(data['status'])

        if not update_fields:
            cur.close()
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(project_id)

        query = f"UPDATE projects SET {', '.join(update_fields)} WHERE id = %s"
        cur.execute(query, params)

        # Log activity
        cur.execute("""
            INSERT INTO project_activity_log (
                project_id, user_id, activity_type, action, new_values
            ) VALUES (%s, %s, 'project_updated', 'update', %s)
        """, (project_id, user_id, psycopg2.extras.Json(data)))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Project updated successfully'})

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@project_bp.route('/api/projects/<int:project_id>/config', methods=['GET'])
@require_project_access(required_role='project_admin')
def get_project_config(project_id):
    """Get project configuration (admin only)"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM project_configurations WHERE project_id = %s", (project_id,))
    config = cur.fetchone()

    cur.close()
    conn.close()

    if not config:
        return jsonify({'error': 'Configuration not found'}), 404

    # Don't return sensitive tokens
    safe_config = dict(config)
    if 'jira_api_token' in safe_config:
        safe_config['jira_api_token'] = '***' if safe_config['jira_api_token'] else None
    if 'github_token' in safe_config:
        safe_config['github_token'] = '***' if safe_config['github_token'] else None

    return jsonify({'config': safe_config})

@project_bp.route('/api/projects/<int:project_id>/config', methods=['PUT'])
@require_project_access(required_role='project_admin')
def update_project_config(project_id):
    """Update project configuration (admin only)"""
    data = request.json
    user_id = g.user_id

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Build update query
        update_fields = []
        params = []

        allowed_fields = [
            'jira_project_key', 'jira_url', 'jira_email', 'jira_api_token',
            'github_repo_owner', 'github_repo_name', 'github_default_branch', 'github_token',
            'ci_provider', 'ci_webhook_url', 'mongodb_collection_prefix',
            'pinecone_namespace', 'confidence_threshold'
        ]

        for field in allowed_fields:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])

        if not update_fields:
            cur.close()
            conn.close()
            return jsonify({'error': 'No fields to update'}), 400

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(project_id)

        query = f"UPDATE project_configurations SET {', '.join(update_fields)} WHERE project_id = %s"
        cur.execute(query, params)

        # Log activity
        cur.execute("""
            INSERT INTO project_activity_log (
                project_id, user_id, activity_type, action, new_values
            ) VALUES (%s, %s, 'config_updated', 'update', %s)
        """, (project_id, user_id, psycopg2.extras.Json(data)))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Configuration updated successfully'})

    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@project_bp.route('/api/projects/<int:project_id>/stats', methods=['GET'])
@require_project_access()
def get_project_stats(project_id):
    """Get project statistics"""
    time_range = request.args.get('time_range', '30')  # days

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Total failures
    cur.execute("""
        SELECT COUNT(*) as total
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
    """, (project_id, int(time_range)))
    total_failures = cur.fetchone()['total']

    # Classification breakdown
    cur.execute("""
        SELECT classification, COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY classification
        ORDER BY count DESC
    """, (project_id, int(time_range)))
    classification_breakdown = {row['classification']: row['count'] for row in cur.fetchall()}

    # Trend data
    cur.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM failure_analysis
        WHERE project_id = %s AND created_at > NOW() - INTERVAL '%s days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """, (project_id, int(time_range)))
    trend = [{'date': row['date'].isoformat(), 'count': row['count']} for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        'project_id': project_id,
        'project_name': g.project_name,
        'time_range_days': int(time_range),
        'total_failures': total_failures,
        'classification_breakdown': classification_breakdown,
        'trend': trend
    })

# Helper function to log activities
def log_project_activity(project_id, user_id, activity_type, entity_type, entity_id, action, old_values=None, new_values=None):
    """Log project activity"""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO project_activity_log (
            project_id, user_id, activity_type, entity_type, entity_id,
            action, old_values, new_values
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        project_id, user_id, activity_type, entity_type, entity_id,
        action,
        psycopg2.extras.Json(old_values) if old_values else None,
        psycopg2.extras.Json(new_values) if new_values else None
    ))

    conn.commit()
    cur.close()
    conn.close()
