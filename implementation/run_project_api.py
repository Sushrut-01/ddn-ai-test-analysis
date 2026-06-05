"""
Standalone Project API Server
Run this to start the multi-project API server

Usage:
    python run_project_api.py

Then test with:
    http://localhost:5006/api/projects
"""

from flask import Flask
from flask_cors import CORS
from project_api import project_bp
from project_scoped_endpoints import scoped_bp
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Project-ID"]
    }
})

# Root endpoint (register before blueprints)
@app.route('/', methods=['GET'])
def root():
    return {
        'service': 'DDN AI Multi-Project API',
        'version': '1.0.0',
        'endpoints': {
            'projects': '/api/projects',
            'project_details': '/api/projects/<id>',
            'project_config': '/api/projects/<id>/config',
            'project_failures': '/api/projects/<id>/failures',
            'project_stats': '/api/projects/<id>/stats',
            'project_jira': '/api/projects/<id>/jira/*',
            'project_analytics': '/api/projects/<id>/analytics/*'
        }
    }

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy', 'service': 'multi-project-api'}

# Register blueprints
app.register_blueprint(project_bp)
app.register_blueprint(scoped_bp)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5006))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'

    print("=" * 60)
    print("DDN AI Multi-Project API Server")
    print("=" * 60)
    print(f"Starting server on http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print("")
    print("Available endpoints:")
    print("  - GET  /api/projects")
    print("  - POST /api/projects")
    print("  - GET  /api/projects/<id>")
    print("  - PUT  /api/projects/<id>")
    print("  - GET  /api/projects/<id>/config")
    print("  - PUT  /api/projects/<id>/config")
    print("  - GET  /api/projects/<id>/stats")
    print("  - GET  /api/projects/<id>/failures")
    print("  - GET  /api/projects/<id>/jira/bugs")
    print("  - POST /api/projects/<id>/jira/create-issue")
    print("")
    print("Database Configuration:")
    print(f"  - Host: {os.getenv('POSTGRES_HOST', 'localhost')}")
    print(f"  - Port: {os.getenv('POSTGRES_PORT', '5432')}")
    print(f"  - Database: {os.getenv('POSTGRES_DB', 'ddn_ai_analysis')}")
    print("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=debug)
