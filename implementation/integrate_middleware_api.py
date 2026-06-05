"""
Integration Script: Add Middleware-Protected Endpoints
Adds v2 endpoints to existing dashboard_api_full.py without breaking old endpoints

Run this to integrate:
    python integrate_middleware_api.py

What it does:
1. Imports the refactored blueprint
2. Registers v2 endpoints alongside old endpoints
3. Keeps everything backward compatible
4. Adds graceful fallbacks
"""

import os
import sys

def integrate_middleware():
    """Integrate middleware endpoints into main API"""

    print("=" * 70)
    print("INTEGRATING MIDDLEWARE API - ZERO DOWNTIME APPROACH")
    print("=" * 70)

    # Check if files exist
    if not os.path.exists('dashboard_api_full.py'):
        print("[ERROR] dashboard_api_full.py not found!")
        print("  Please run this script from implementation/ directory")
        return False

    if not os.path.exists('api_refactored_with_middleware.py'):
        print("[ERROR] api_refactored_with_middleware.py not found!")
        return False

    if not os.path.exists('middleware/project_context.py'):
        print("[ERROR] middleware/project_context.py not found!")
        return False

    print("\n[OK] All required files found")

    # Create integration code snippet
    integration_code = '''
# ============================================================================
# MIDDLEWARE INTEGRATION - Added by integrate_middleware_api.py
# ============================================================================

# Import refactored endpoints with middleware
try:
    from api_refactored_with_middleware import register_refactored_endpoints

    # Register v2 endpoints (with middleware protection)
    register_refactored_endpoints(app)

    print("✅ Middleware-protected v2 endpoints registered")
    print("   New endpoints available:")
    print("   - GET  /api/v2/projects/<id>/failures")
    print("   - POST /api/v2/projects/<id>/trigger-analysis")
    print("   - GET  /api/v2/projects/<id>/analytics")
    print("   - GET  /api/v2/projects/<id>/config")
    print("   - PUT  /api/v2/projects/<id>/config")
    print("   - GET  /api/v2/health")
    print("")
    print("   Old endpoints still work for backward compatibility!")

except ImportError as e:
    print(f"⚠️  WARNING: Could not load middleware endpoints: {e}")
    print("   Old endpoints will continue to work")

# ============================================================================
'''

    print("\n[*] Integration code prepared")
    print("\n[MANUAL STEP REQUIRED]")
    print("-" * 70)
    print("Add this code to dashboard_api_full.py:")
    print("-" * 70)
    print(integration_code)
    print("-" * 70)

    print("\n[*] Creating standalone middleware API server...")

    # Create standalone server that can run independently
    standalone_code = '''"""
Standalone Middleware API Server
Can run independently or alongside existing API

Start with: python api_middleware_server.py
"""

from flask import Flask
from flask_cors import CORS
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register refactored endpoints
from api_refactored_with_middleware import register_refactored_endpoints
register_refactored_endpoints(app)

if __name__ == '__main__':
    port = int(os.getenv('MIDDLEWARE_API_PORT', 5020))

    print("=" * 70)
    print("MIDDLEWARE API SERVER")
    print("=" * 70)
    print(f"Starting on port {port}")
    print("")
    print("Endpoints available:")
    print(f"  - GET  http://localhost:{port}/api/v2/projects/<id>/failures")
    print(f"  - POST http://localhost:{port}/api/v2/projects/<id>/trigger-analysis")
    print(f"  - GET  http://localhost:{port}/api/v2/projects/<id>/analytics")
    print(f"  - GET  http://localhost:{port}/api/v2/projects/<id>/config")
    print(f"  - PUT  http://localhost:{port}/api/v2/projects/<id>/config")
    print(f"  - GET  http://localhost:{port}/api/v2/health")
    print("=" * 70)

    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
'''

    with open('api_middleware_server.py', 'w') as f:
        f.write(standalone_code)

    print("[OK] Created: api_middleware_server.py")

    print("\n" + "=" * 70)
    print("INTEGRATION OPTIONS")
    print("=" * 70)

    print("\n📋 OPTION 1: Add to Existing API (Recommended)")
    print("-" * 70)
    print("1. Open dashboard_api_full.py")
    print("2. Add the integration code shown above (near the end of file)")
    print("3. Restart the API server")
    print("4. Both old and new endpoints will work")

    print("\n📋 OPTION 2: Run as Separate Service (Safer)")
    print("-" * 70)
    print("1. Start standalone server:")
    print("   python api_middleware_server.py")
    print("")
    print("2. Add to docker-compose.yml:")
    print("""
  middleware-api:
    build:
      context: ./implementation
      dockerfile: Dockerfile
    container_name: ddn-middleware-api
    ports:
      - "5020:5020"
    environment:
      - MIDDLEWARE_API_PORT=5020
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=ddn_ai_analysis
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    networks:
      - ddn-network
    depends_on:
      - postgres
    restart: unless-stopped
    command: python api_middleware_server.py
""")

    print("\n📋 OPTION 3: Test First (Safest)")
    print("-" * 70)
    print("1. Run standalone server on port 5020")
    print("2. Test v2 endpoints manually")
    print("3. Once confirmed working, integrate into main API")

    print("\n" + "=" * 70)
    print("TESTING THE NEW ENDPOINTS")
    print("=" * 70)

    test_script = '''
# test_middleware_endpoints.sh

# 1. Health check
curl http://localhost:5020/api/v2/health

# 2. Login and get token
TOKEN=$(curl -X POST http://localhost:5013/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email":"admin@ddn.com","password":"admin123"}' \\
  | jq -r '.token')

# 3. Get failures for project 1
curl -H "Authorization: Bearer $TOKEN" \\
  http://localhost:5020/api/v2/projects/1/failures

# 4. Try to access project 2 (should fail if user doesn't have access)
curl -H "Authorization: Bearer $TOKEN" \\
  http://localhost:5020/api/v2/projects/2/failures

# 5. Get analytics
curl -H "Authorization: Bearer $TOKEN" \\
  http://localhost:5020/api/v2/projects/1/analytics?time_range=30

# 6. Trigger analysis (requires developer role)
curl -X POST -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"build_id":"TEST-123","force_reanalysis":false}' \\
  http://localhost:5020/api/v2/projects/1/trigger-analysis
'''

    with open('test_middleware_endpoints.sh', 'w') as f:
        f.write(test_script)

    print("\n[OK] Created: test_middleware_endpoints.sh")
    print("\nRun with: bash test_middleware_endpoints.sh")

    print("\n" + "=" * 70)
    print("[SUCCESS] INTEGRATION PREPARED")
    print("=" * 70)

    print("\nNext steps:")
    print("1. Choose an integration option above")
    print("2. Start the server")
    print("3. Test using test_middleware_endpoints.sh")
    print("4. Monitor logs for any issues")

    return True

if __name__ == "__main__":
    success = integrate_middleware()
    exit(0 if success else 1)
