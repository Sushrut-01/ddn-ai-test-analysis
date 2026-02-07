"""
Test API Routes
Verifies that Flask routes are registered correctly
"""

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from project_api import project_bp
from project_scoped_endpoints import scoped_bp

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(project_bp)
app.register_blueprint(scoped_bp)

# Add test root route
@app.route('/')
def root():
    return {'status': 'ok', 'message': 'Multi-Project API is running'}

@app.route('/health')
def health():
    return {'status': 'healthy'}

# Test with app context
with app.test_client() as client:
    print("Testing routes...")
    print("=" * 70)

    # Test root
    response = client.get('/')
    print(f"\n1. GET / => {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.get_json()}")

    # Test health
    response = client.get('/health')
    print(f"\n2. GET /health => {response.status_code}")
    if response.status_code == 200:
        print(f"   Response: {response.get_json()}")

    # Test projects endpoint (should fail without auth, but route should exist)
    response = client.get('/api/projects')
    print(f"\n3. GET /api/projects => {response.status_code}")
    if response.status_code != 404:
        print(f"   Route exists! (Got {response.status_code} - expected without auth)")
    else:
        print(f"   ERROR: Route not found!")

    # List all routes
    print("\n" + "=" * 70)
    print("All registered routes:")
    print("=" * 70)
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'OPTIONS', 'HEAD'})
        print(f"  {methods:10} {rule.rule}")
