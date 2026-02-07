"""
Standalone Middleware API Server
Runs independently on port 5020

Start with: python api_middleware_server.py

This provides:
- Middleware-protected endpoints
- RLS enforcement
- Role-based access control
- Project context isolation

Can run alongside existing API for testing
"""

from flask import Flask
from flask_cors import CORS
import logging
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Register refactored endpoints
try:
    from api_refactored_with_middleware import register_refactored_endpoints
    register_refactored_endpoints(app)
    logger.info("Middleware endpoints registered successfully")
except ImportError as e:
    logger.error(f"Failed to import refactored endpoints: {e}")
    sys.exit(1)

if __name__ == '__main__':
    port = int(os.getenv('MIDDLEWARE_API_PORT', 5020))

    print("=" * 70)
    print("MIDDLEWARE API SERVER (v2)")
    print("=" * 70)
    print(f"Starting on port {port}")
    print("")
    print("Endpoints available:")
    print(f"  GET  http://localhost:{port}/api/v2/health")
    print(f"  GET  http://localhost:{port}/api/v2/projects/<id>/failures")
    print(f"  POST http://localhost:{port}/api/v2/projects/<id>/trigger-analysis")
    print(f"  GET  http://localhost:{port}/api/v2/projects/<id>/analytics")
    print(f"  GET  http://localhost:{port}/api/v2/projects/<id>/config")
    print(f"  PUT  http://localhost:{port}/api/v2/projects/<id>/config")
    print("")
    print("Features:")
    print("  - JWT authentication required")
    print("  - Role-based access control")
    print("  - PostgreSQL RLS enforcement")
    print("  - Project context isolation")
    print("=" * 70)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
