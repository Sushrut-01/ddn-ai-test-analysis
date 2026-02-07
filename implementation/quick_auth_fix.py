"""
Quick authentication fix - bypasses PostgreSQL for testing
This creates test users directly in memory for immediate login
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)
CORS(app)

SECRET_KEY = "ddn-temp-secret-key"

# Test users (in-memory)
TEST_USERS = {
    "admin@example.com": {
        "id": 1,
        "email": "admin@example.com",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "name": "Admin User",
        "role": "admin"
    },
    "test@example.com": {
        "id": 2,
        "email": "test@example.com",
        "password": hashlib.sha256("test123".encode()).hexdigest(),
        "name": "Test User",
        "role": "developer"
    }
}

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').lower()
        password = data.get('password', '')

        # Check if user exists
        if email not in TEST_USERS:
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        user = TEST_USERS[email]
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Verify password
        if password_hash != user['password']:
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401

        # Generate tokens
        access_token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')

        refresh_token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=30)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({
            'status': 'success',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role']
                }
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/auth/me', methods=['GET'])
def get_user():
    try:
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'status': 'error', 'message': 'No token provided'}), 401

        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

        email = payload['email']
        if email in TEST_USERS:
            user = TEST_USERS[email]
            return jsonify({
                'status': 'success',
                'data': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role']
                }
            })

        return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except jwt.ExpiredSignatureError:
        return jsonify({'status': 'error', 'message': 'Token expired'}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 401

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'quick-auth'})

if __name__ == '__main__':
    print("=" * 60)
    print("QUICK AUTH SERVICE - TEMPORARY LOGIN FIX")
    print("=" * 60)
    print("Test Users:")
    print("  Email: admin@example.com | Password: admin123")
    print("  Email: test@example.com  | Password: test123")
    print("=" * 60)
    print("Running on http://localhost:5013")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5013, debug=True)
