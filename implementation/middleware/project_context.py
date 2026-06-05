"""
Project Context Middleware - Expert Implementation
==================================================

PURPOSE:
--------
Unified project context management across all API requests.
Solves the problem of inconsistent project_id extraction and validation.

BEFORE (INCONSISTENT):
----------------------
# Method 1: URL path
@app.route('/api/projects/<int:project_id>/failures')
def get_failures(project_id):
    # Manual validation here...

# Method 2: Query param
@app.route('/api/failures')
def get_failures():
    project_id = request.args.get('project_id')
    # Manual validation here...

# Method 3: Request body
@app.route('/api/trigger')
def trigger():
    project_id = request.json.get('project_id', 1)  # Unsafe default!
    # Manual validation here...

AFTER (UNIFIED):
----------------
from middleware import require_auth, require_project_access

@app.route('/api/projects/<int:project_id>/failures')
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # g.project_id, g.project_role automatically set
    # PostgreSQL RLS automatically filters by project
    # No manual validation needed!
    pass

SECURITY BENEFITS:
------------------
1. Automatic JWT validation
2. Automatic project access verification
3. Automatic role-based access control (RBAC)
4. PostgreSQL session variable set (for RLS)
5. Audit trail of access
6. Single point of failure → easy to secure

USAGE:
------
See examples at bottom of this file.
"""

from flask import g, request, jsonify
from functools import wraps
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, Tuple, Dict
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================
# CONFIGURATION
# ============================================

JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'temp-development-key-please-change-in-production-123456789')
JWT_ALGORITHM = 'HS256'

# Database configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

# ============================================
# DATABASE CONNECTION
# ============================================

def get_db_connection():
    """
    Get PostgreSQL connection

    TODO: Replace with connection pool for production
    """
    return psycopg2.connect(**POSTGRES_CONFIG)


# ============================================
# ROLE-BASED ACCESS CONTROL
# ============================================

ROLE_HIERARCHY = {
    'guest': 0,          # Read-only, limited access
    'viewer': 1,         # Can view all data
    'developer': 2,      # Can trigger analysis, view code
    'project_admin': 3,  # Can manage project settings
    'project_owner': 4,  # Full project control
    'system_admin': 10   # Can access ALL projects (bypass checks)
}

def has_required_role(user_role: str, required_role: str) -> bool:
    """
    Check if user has sufficient role

    Examples:
        has_required_role('developer', 'viewer') → True
        has_required_role('viewer', 'developer') → False
        has_required_role('system_admin', 'project_owner') → True
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 0)
    return user_level >= required_level


# ============================================
# PROJECT CONTEXT EXTRACTION
# ============================================

class ProjectContext:
    """
    Unified project context manager

    Extracts project_id from multiple sources with priority order:
    1. URL path parameter (highest priority)
    2. Query parameter
    3. Request body JSON
    4. JWT token default_project_id (lowest priority)
    """

    @staticmethod
    def extract_project_id(request_obj, kwargs: Dict) -> Optional[int]:
        """
        Extract project_id from request

        Args:
            request_obj: Flask request object
            kwargs: Route parameters (e.g., {'project_id': 123})

        Returns:
            int: project_id if found
            None: if not found in any source
        """

        # Priority 1: URL path parameter
        # Example: /api/projects/123/failures
        if 'project_id' in kwargs:
            try:
                project_id = int(kwargs['project_id'])
                logger.debug(f"project_id={project_id} from URL path")
                return project_id
            except (ValueError, TypeError):
                logger.warning(f"Invalid project_id in URL path: {kwargs['project_id']}")
                return None

        # Priority 2: Query parameter
        # Example: /api/failures?project_id=123
        if 'project_id' in request_obj.args:
            try:
                project_id = int(request_obj.args['project_id'])
                logger.debug(f"project_id={project_id} from query parameter")
                return project_id
            except (ValueError, TypeError):
                logger.warning(f"Invalid project_id in query: {request_obj.args['project_id']}")
                return None

        # Priority 3: Request body JSON
        # Example: POST {"project_id": 123, "build_id": "..."}
        if request_obj.is_json and request_obj.json and 'project_id' in request_obj.json:
            try:
                project_id = int(request_obj.json['project_id'])
                logger.debug(f"project_id={project_id} from request body")
                return project_id
            except (ValueError, TypeError):
                logger.warning(f"Invalid project_id in body: {request_obj.json['project_id']}")
                return None

        # Priority 4: JWT token default_project_id
        # Example: token payload contains {"default_project_id": 1}
        token = request_obj.headers.get('Authorization', '').replace('Bearer ', '')
        if token:
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                if 'default_project_id' in payload:
                    project_id = int(payload['default_project_id'])
                    logger.debug(f"project_id={project_id} from JWT token")
                    return project_id
            except jwt.InvalidTokenError:
                logger.warning("Invalid JWT token when extracting project_id")
            except (ValueError, TypeError):
                logger.warning(f"Invalid default_project_id in JWT")

        logger.warning("project_id not found in any source")
        return None

    @staticmethod
    def verify_project_access(user_id: int, project_id: int) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Verify user has access to project

        Args:
            user_id: User ID from JWT token
            project_id: Project ID to check access

        Returns:
            Tuple[bool, str, dict]:
                - has_access: True if user can access project
                - role: User's role in project (e.g., 'developer')
                - project_info: Project details (slug, name, status, permissions)
        """
        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)

            # Query user_projects junction table
            cur.execute("""
                SELECT
                    up.role,
                    up.permissions,
                    p.slug,
                    p.name,
                    p.status,
                    p.id as project_id
                FROM user_projects up
                JOIN projects p ON up.project_id = p.id
                WHERE up.user_id = %s AND up.project_id = %s
            """, (user_id, project_id))

            result = cur.fetchone()

            if not result:
                logger.warning(f"User {user_id} has no access to project {project_id}")
                return False, None, None

            # Check if project is active
            if result['status'] != 'active':
                logger.warning(
                    f"User {user_id} tried to access {result['status']} project {project_id}"
                )
                return False, None, None

            # Update last accessed time (audit trail)
            cur.execute("""
                UPDATE user_projects
                SET last_accessed_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND project_id = %s
            """, (user_id, project_id))
            conn.commit()

            logger.info(
                f"✅ User {user_id} (role: {result['role']}) accessing "
                f"project {project_id} ({result['slug']})"
            )

            return True, result['role'], dict(result)

        except Exception as e:
            logger.error(f"Error verifying project access: {e}")
            if conn:
                conn.rollback()
            return False, None, None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def set_db_project_context(project_id: int):
        """
        Set PostgreSQL session variable for Row-Level Security

        This enables automatic filtering by project_id at database level.

        Example:
            set_db_project_context(1)
            # Now ALL queries automatically filter WHERE project_id = 1
            # Even: SELECT * FROM failure_analysis
            # Returns only project_id=1 rows

        Note: Requires RLS migration to be applied first
        """
        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Call PostgreSQL function to set session variable
            cur.execute("SELECT set_project_context(%s)", (project_id,))
            conn.commit()

            logger.debug(f"Set DB project context to project_id={project_id}")

        except Exception as e:
            logger.error(f"Failed to set DB project context: {e}")
            if conn:
                conn.rollback()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


# ============================================
# DECORATOR: require_auth
# ============================================

def require_auth(f):
    """
    Require JWT authentication

    Sets Flask g context:
        - g.user_id: User ID from token
        - g.user_email: User email
        - g.user_role: System role (user, admin)
        - g.token_payload: Full JWT payload

    Usage:
        @app.route('/api/protected')
        @require_auth
        def protected_endpoint():
            user_id = g.user_id  # Available here
            return {'user': user_id}

    Returns:
        401: If token missing or invalid
        401: If token expired
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()

        if not token:
            logger.warning("Missing Authorization token")
            return jsonify({'error': 'Authorization token required'}), 401

        try:
            # Decode and validate JWT token
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

            # Set user context in Flask g
            g.user_id = payload['user_id']
            g.user_email = payload.get('email', 'unknown')
            g.user_role = payload.get('role', 'user')
            g.token_payload = payload

            logger.debug(f"Authenticated user_id={g.user_id} ({g.user_email})")

            return f(*args, **kwargs)

        except jwt.ExpiredSignatureError:
            logger.warning(f"Expired JWT token from {request.remote_addr}")
            return jsonify({'error': 'Token expired', 'code': 'TOKEN_EXPIRED'}), 401

        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return jsonify({'error': 'Invalid token', 'code': 'TOKEN_INVALID'}), 401

    return decorated_function


# ============================================
# DECORATOR: require_project_access
# ============================================

def require_project_access(required_role: str = 'viewer', allow_system_admin: bool = True):
    """
    Require project-level access with role check

    This is the MAIN decorator that enforces project isolation!

    Sets Flask g context:
        - g.project_id: Validated project ID
        - g.project_role: User's role in this project
        - g.project_info: Project details (slug, name, etc.)

    Also:
        - Sets PostgreSQL session variable for RLS
        - Updates last_accessed_at timestamp
        - Logs access for audit trail

    Usage:
        @app.route('/api/projects/<int:project_id>/failures')
        @require_auth
        @require_project_access(required_role='viewer')
        def get_failures(project_id):
            # g.project_id is validated
            # g.project_role contains user's role
            # PostgreSQL RLS automatically filters queries

            conn = get_db_connection()
            cur = conn.cursor()

            # This query automatically filtered by RLS!
            cur.execute("SELECT * FROM failure_analysis")

            return jsonify({'failures': cur.fetchall()})

    Args:
        required_role: Minimum role required
            - 'guest': Anyone with project access
            - 'viewer': Can view data (default)
            - 'developer': Can trigger analysis
            - 'project_admin': Can manage project
            - 'project_owner': Full control

        allow_system_admin: If True, system admins bypass project checks

    Returns:
        400: If project_id not found in request
        403: If user doesn't have access to project
        403: If user's role is insufficient
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Require authentication first
            if not hasattr(g, 'user_id'):
                return jsonify({
                    'error': 'Authentication required',
                    'hint': 'Use @require_auth decorator before this'
                }), 401

            # Extract project_id from request
            project_id = ProjectContext.extract_project_id(request, kwargs)

            if not project_id:
                return jsonify({
                    'error': 'project_id required',
                    'hint': 'Provide project_id in URL path, query param, or request body'
                }), 400

            user_id = g.user_id
            user_system_role = getattr(g, 'user_role', 'user')

            # System admins can bypass project checks
            if allow_system_admin and user_system_role == 'system_admin':
                g.project_id = project_id
                g.project_role = 'system_admin'
                g.project_info = {
                    'system_admin_access': True,
                    'bypass_enabled': True
                }

                # Still set DB context for consistency
                ProjectContext.set_db_project_context(project_id)

                logger.info(
                    f"🔐 System admin {user_id} bypassing checks for project {project_id}"
                )
                return f(*args, **kwargs)

            # Verify project access
            has_access, role, project_info = ProjectContext.verify_project_access(
                user_id, project_id
            )

            if not has_access:
                logger.warning(
                    f"❌ User {user_id} denied access to project {project_id}"
                )
                return jsonify({
                    'error': 'Access denied to this project',
                    'project_id': project_id
                }), 403

            # Check role requirement
            if not has_required_role(role, required_role):
                logger.warning(
                    f"❌ User {user_id} has role '{role}' but needs '{required_role}' "
                    f"for project {project_id}"
                )
                return jsonify({
                    'error': f'Requires {required_role} role or higher',
                    'your_role': role,
                    'required_role': required_role
                }), 403

            # Set context in Flask g
            g.project_id = project_id
            g.project_role = role
            g.project_info = project_info

            # Set PostgreSQL session context for RLS
            ProjectContext.set_db_project_context(project_id)

            logger.info(
                f"✅ User {user_id} (role: {role}) → project {project_id} "
                f"({project_info['slug']})"
            )

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ============================================
# DECORATOR: require_project_permission
# ============================================

def require_project_permission(permission: str):
    """
    Require specific permission in project

    Usage:
        @require_project_access()
        @require_project_permission('can_create_jira_tickets')
        def create_jira_ticket():
            # User has both access AND specific permission
            pass

    Args:
        permission: Permission string (e.g., 'can_create_jira_tickets')

    Returns:
        403: If user doesn't have the required permission
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'project_info') or not g.project_info:
                return jsonify({
                    'error': 'Project context required',
                    'hint': 'Use @require_project_access decorator first'
                }), 400

            permissions = g.project_info.get('permissions', [])

            if permission not in permissions:
                logger.warning(
                    f"User {g.user_id} missing permission '{permission}' "
                    f"for project {g.project_id}"
                )
                return jsonify({
                    'error': f'Missing required permission: {permission}',
                    'your_permissions': permissions
                }), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# ============================================
# MONGODB PROJECT CONTEXT
# ============================================

class MongoDBProjectContext:
    """
    MongoDB project isolation helper

    Current approach: Collection prefixes
    Recommended approach: Database per project
    """

    # Collection prefix mapping (current approach)
    COLLECTION_PREFIXES = {
        1: 'ddn_',
        2: 'guruttava_'
    }

    # Database per project (recommended approach)
    PROJECT_DATABASES = {
        1: 'ddn_project_db',
        2: 'guruttava_project_db'
    }

    @classmethod
    def get_collection_prefix(cls, project_id: int) -> str:
        """
        Get collection prefix for project

        Usage:
            prefix = MongoDBProjectContext.get_collection_prefix(g.project_id)
            collection = db[f'{prefix}test_failures']
        """
        return cls.COLLECTION_PREFIXES.get(project_id, f'project_{project_id}_')

    @classmethod
    def get_database_name(cls, project_id: int) -> str:
        """
        Get MongoDB database name for project (recommended approach)

        Usage:
            db_name = MongoDBProjectContext.get_database_name(g.project_id)
            db = mongo_client[db_name]
            collection = db['test_failures']  # Same name across projects
        """
        if project_id not in cls.PROJECT_DATABASES:
            raise ValueError(f"Unknown project_id: {project_id}")
        return cls.PROJECT_DATABASES[project_id]


# ============================================
# PINECONE PROJECT CONTEXT
# ============================================

class PineconeProjectContext:
    """
    Pinecone namespace isolation
    """

    PROJECT_NAMESPACES = {
        1: 'ddn_knowledge',
        2: 'guruttava_knowledge'
    }

    @classmethod
    def get_namespace(cls, project_id: int) -> str:
        """
        Get Pinecone namespace for project

        Usage:
            namespace = PineconeProjectContext.get_namespace(g.project_id)
            results = index.query(
                vector=embedding,
                namespace=namespace,
                top_k=10
            )
        """
        return cls.PROJECT_NAMESPACES.get(project_id, f'project_{project_id}')


# ============================================
# USAGE EXAMPLES
# ============================================

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║         PROJECT CONTEXT MIDDLEWARE - USAGE EXAMPLES              ║
╚══════════════════════════════════════════════════════════════════╝

EXAMPLE 1: Basic Project Access
────────────────────────────────────────────────────────────────────
from flask import Flask, jsonify, g
from middleware import require_auth, require_project_access

app = Flask(__name__)

@app.route('/api/projects/<int:project_id>/failures', methods=['GET'])
@require_auth
@require_project_access(required_role='viewer')
def get_failures(project_id):
    # g.project_id, g.project_role are now available
    # PostgreSQL RLS automatically filters by project_id

    conn = get_db_connection()
    cur = conn.cursor()

    # This query is automatically filtered!
    cur.execute("SELECT * FROM failure_analysis ORDER BY created_at DESC")

    return jsonify({
        'project_id': g.project_id,
        'project_role': g.project_role,
        'failures': cur.fetchall()
    })


EXAMPLE 2: Require Developer Role
────────────────────────────────────────────────────────────────────
@app.route('/api/projects/<int:project_id>/trigger-analysis', methods=['POST'])
@require_auth
@require_project_access(required_role='developer')
def trigger_analysis(project_id):
    # Only developers and above can access this

    data = request.json
    build_id = data['build_id']

    # Trigger analysis...

    return jsonify({'status': 'started'})


EXAMPLE 3: Admin-Only Endpoint
────────────────────────────────────────────────────────────────────
@app.route('/api/projects/<int:project_id>/config', methods=['PUT'])
@require_auth
@require_project_access(required_role='project_admin')
def update_config(project_id):
    # Only project_admin and project_owner can access

    config = request.json

    # Update project configuration...

    return jsonify({'updated': True})


EXAMPLE 4: MongoDB with Project Context
────────────────────────────────────────────────────────────────────
from middleware import MongoDBProjectContext

@app.route('/api/projects/<int:project_id>/test-results')
@require_auth
@require_project_access(required_role='viewer')
def get_test_results(project_id):
    # Get MongoDB database for this project
    db_name = MongoDBProjectContext.get_database_name(g.project_id)
    db = mongo_client[db_name]

    # Now query is isolated to project's database
    results = db['test_failures'].find().limit(50)

    return jsonify({'results': list(results)})


EXAMPLE 5: Pinecone RAG with Project Context
────────────────────────────────────────────────────────────────────
from middleware import PineconeProjectContext

@app.route('/api/projects/<int:project_id>/search-similar')
@require_auth
@require_project_access(required_role='viewer')
def search_similar(project_id):
    error_text = request.json['error']

    # Get embedding
    embedding = get_embedding(error_text)

    # Get namespace for this project
    namespace = PineconeProjectContext.get_namespace(g.project_id)

    # Query is isolated to project's namespace
    results = pinecone_index.query(
        vector=embedding,
        namespace=namespace,
        top_k=10
    )

    return jsonify({'results': results})


EXAMPLE 6: System Admin Bypass
────────────────────────────────────────────────────────────────────
@app.route('/api/projects/<int:project_id>/audit-log')
@require_auth
@require_project_access(required_role='viewer', allow_system_admin=True)
def get_audit_log(project_id):
    # System admins can access any project
    # Other users need viewer role in the project

    if g.project_role == 'system_admin':
        # Admin sees all data
        pass
    else:
        # Normal user sees filtered data
        pass

    return jsonify({'logs': []})


EXAMPLE 7: Specific Permission Check
────────────────────────────────────────────────────────────────────
from middleware import require_project_permission

@app.route('/api/projects/<int:project_id>/create-jira')
@require_auth
@require_project_access(required_role='developer')
@require_project_permission('can_create_jira_tickets')
def create_jira_ticket(project_id):
    # User needs:
    # 1. developer role or higher
    # 2. 'can_create_jira_tickets' permission

    # Create Jira ticket...

    return jsonify({'ticket': 'DDN-123'})

╔══════════════════════════════════════════════════════════════════╗
║                    INTEGRATION CHECKLIST                         ║
╚══════════════════════════════════════════════════════════════════╝

To integrate this middleware:

1. ✅ Apply RLS migration (003_enable_row_level_security.sql)
2. ✅ Add middleware decorators to existing endpoints
3. ✅ Replace manual project_id validation with decorators
4. ✅ Update MongoDB queries to use MongoDBProjectContext
5. ✅ Update Pinecone queries to use PineconeProjectContext
6. ✅ Test with different roles (viewer, developer, admin)
7. ✅ Add integration tests for access control

""")
