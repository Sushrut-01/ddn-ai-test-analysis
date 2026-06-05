"""
Authentication Service
Port: 5013
Purpose: JWT-based authentication and user management
Features:
- User registration and login
- JWT token generation and validation
- Session management
- Password hashing with bcrypt
- User CRUD operations
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
import secrets

app = Flask(__name__)
CORS(app)

# Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
TOKEN_EXPIRE_MINUTES = int(os.getenv('TOKEN_EXPIRE_MINUTES', 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))

# Team notification emails
TEAM_EMAILS = ['sushrut.nistane@rysun.com', 'amit.manjesh@rysun.com']

def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)


def verify_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'status': 'error', 'message': 'No authorization header'}), 401

        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({'status': 'error', 'message': 'Invalid authorization header'}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401

        # Add user info to request context
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        request.user_role = payload.get('role')

        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.user_role != 'admin':
            return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400

        if len(password) < 8:
            return jsonify({
                'status': 'error',
                'message': 'Password must be at least 8 characters'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Email already registered'
            }), 400

        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Determine role (first team member is admin)
        cursor.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        role = 'admin' if user_count == 0 else 'user'

        # Insert user
        cursor.execute("""
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, true, NOW())
            RETURNING id, email, first_name, last_name, role, created_at
        """, (email, password_hash, first_name, last_name, role))

        user = cursor.fetchone()
        user_id = user['id']

        # Generate JWT tokens for auto-login
        access_token_payload = {
            'user_id': user_id,
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }

        refresh_token_payload = {
            'user_id': user_id,
            'email': user['email'],
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.utcnow()
        }

        access_token = jwt.encode(access_token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Create session for the new user (auto-login)
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        cursor.execute("""
            INSERT INTO user_sessions (user_id, token, refresh_token, expires_at, ip_address, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            user_id,
            access_token,
            refresh_token,
            datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            ip_address,
            user_agent
        ))

        conn.commit()
        cursor.close()
        conn.close()

        # Convert datetime to ISO format
        user_data = dict(user)
        if isinstance(user_data.get('created_at'), datetime):
            user_data['created_at'] = user_data['created_at'].isoformat()

        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'data': {
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': 3600  # 1 hour
            }
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Email and password are required'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get user
        cursor.execute("""
            SELECT id, email, password_hash, first_name, last_name, role, is_active
            FROM users
            WHERE email = %s
        """, (email,))

        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        if not user['is_active']:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Account is disabled'
            }), 401

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        # Generate tokens
        access_token_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }

        refresh_token_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            'iat': datetime.utcnow()
        }

        access_token = jwt.encode(access_token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Create session
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        cursor.execute("""
            INSERT INTO user_sessions (user_id, token, refresh_token, expires_at, ip_address, user_agent, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            user['id'],
            access_token,
            refresh_token,
            datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            ip_address,
            user_agent
        ))

        # Update last login
        cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))

        conn.commit()
        cursor.close()
        conn.close()

        # Prepare user data (exclude password)
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'role': user['role']
        }

        return jsonify({
            'status': 'success',
            'data': {
                'user': user_data,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_in': TOKEN_EXPIRE_MINUTES * 60  # seconds
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """User logout"""
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]

        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Delete session
        cursor.execute("DELETE FROM user_sessions WHERE token = %s", (token,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Logged out successfully'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """Get current user info"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, email, first_name, last_name, role, is_active, created_at, last_login
            FROM users
            WHERE id = %s
        """, (request.user_id,))

        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        user_data = dict(user)
        if isinstance(user_data.get('created_at'), datetime):
            user_data['created_at'] = user_data['created_at'].isoformat()
        if isinstance(user_data.get('last_login'), datetime):
            user_data['last_login'] = user_data['last_login'].isoformat()

        return jsonify({
            'status': 'success',
            'data': {'user': user_data}
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/auth/refresh', methods=['POST'])
def refresh_token():
    """Refresh access token"""
    try:
        data = request.get_json()
        refresh_token_str = data.get('refresh_token')

        if not refresh_token_str:
            return jsonify({
                'status': 'error',
                'message': 'Refresh token is required'
            }), 400

        payload = verify_token(refresh_token_str)
        if not payload or payload.get('type') != 'refresh':
            return jsonify({
                'status': 'error',
                'message': 'Invalid refresh token'
            }), 401

        # Generate new access token
        access_token_payload = {
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload.get('role', 'user'),
            'exp': datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
            'iat': datetime.utcnow()
        }

        access_token = jwt.encode(access_token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return jsonify({
            'status': 'success',
            'data': {
                'access_token': access_token,
                'expires_in': TOKEN_EXPIRE_MINUTES * 60
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# USER MANAGEMENT ENDPOINTS
# ============================================================================

@app.route('/api/users', methods=['GET'])
@require_admin
def get_users():
    """Get all users (admin only)"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total = cursor.fetchone()['count']

        # Get users
        cursor.execute("""
            SELECT id, email, first_name, last_name, role, is_active, created_at, last_login
            FROM users
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))

        users = cursor.fetchall()
        cursor.close()
        conn.close()

        # Format dates
        users_data = []
        for user in users:
            user_dict = dict(user)
            if isinstance(user_dict.get('created_at'), datetime):
                user_dict['created_at'] = user_dict['created_at'].isoformat()
            if isinstance(user_dict.get('last_login'), datetime):
                user_dict['last_login'] = user_dict['last_login'].isoformat()
            users_data.append(user_dict)

        return jsonify({
            'status': 'success',
            'data': {
                'users': users_data,
                'total': total,
                'page': page,
                'limit': limit
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    """Update user (admin only)"""
    try:
        data = request.get_json()

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build update query
        updates = []
        params = []

        if 'first_name' in data:
            updates.append("first_name = %s")
            params.append(data['first_name'])

        if 'last_name' in data:
            updates.append("last_name = %s")
            params.append(data['last_name'])

        if 'role' in data:
            updates.append("role = %s")
            params.append(data['role'])

        if 'is_active' in data:
            updates.append("is_active = %s")
            params.append(data['is_active'])

        if not updates:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'No fields to update'
            }), 400

        updates.append("updated_at = NOW()")
        params.append(user_id)

        query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s RETURNING id, email, first_name, last_name, role, is_active"
        cursor.execute(query, params)

        user = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': {'user': dict(user)}
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Soft delete user (admin only)"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET is_active = false WHERE id = %s", (user_id,))

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'User deactivated successfully'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
@require_auth
def get_user_stats(user_id):
    """Get user activity stats"""
    try:
        # Only allow users to see their own stats, or admins to see anyone's
        if request.user_id != user_id and request.user_role != 'admin':
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get audit log stats
        cursor.execute("""
            SELECT
                COUNT(*) as total_actions,
                COUNT(CASE WHEN action LIKE 'approve%' THEN 1 END) as approvals,
                COUNT(CASE WHEN action LIKE 'reject%' THEN 1 END) as rejections,
                MAX(timestamp) as last_action
            FROM audit_log
            WHERE user_email = (SELECT email FROM users WHERE id = %s)
        """, (user_id,))

        stats = cursor.fetchone()
        cursor.close()
        conn.close()

        stats_data = dict(stats) if stats else {}
        if isinstance(stats_data.get('last_action'), datetime):
            stats_data['last_action'] = stats_data['last_action'].isoformat()

        return jsonify({
            'status': 'success',
            'data': {'stats': stats_data}
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'authentication',
        'port': 5013,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Authentication Service")
    print("=" * 60)
    print(f"Port: 5013")
    print(f"JWT Algorithm: {JWT_ALGORITHM}")
    print(f"Access Token Expiry: {TOKEN_EXPIRE_MINUTES} minutes")
    print(f"Refresh Token Expiry: {REFRESH_TOKEN_EXPIRE_DAYS} days")
    print("=" * 60)
    print("\nTeam Notification Emails:")
    for email in TEAM_EMAILS:
        print(f"  - {email}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                    - Health check")
    print("\n  Authentication:")
    print("  POST /api/auth/register         - Register new user")
    print("  POST /api/auth/login            - User login")
    print("  POST /api/auth/logout           - User logout (requires auth)")
    print("  GET  /api/auth/me               - Get current user (requires auth)")
    print("  POST /api/auth/refresh          - Refresh access token")
    print("\n  User Management:")
    print("  GET  /api/users                 - Get all users (admin only)")
    print("  PUT  /api/users/<user_id>       - Update user (admin only)")
    print("  DELETE /api/users/<user_id>     - Deactivate user (admin only)")
    print("  GET  /api/users/<user_id>/stats - Get user stats")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=5013, debug=True)
