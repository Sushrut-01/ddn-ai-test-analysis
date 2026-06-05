"""
Verify API v2 can start without errors
Quick validation before full deployment
"""

import sys
import os

def verify_imports():
    """Verify all imports work"""
    print("\n[*] Verifying imports...")

    try:
        from flask import Flask
        print("  [OK] Flask")

        from flask_cors import CORS
        print("  [OK] Flask-CORS")

        import psycopg2
        print("  [OK] psycopg2")

        from middleware import require_auth, require_project_access
        print("  [OK] Middleware")

        from api_refactored_with_middleware import register_refactored_endpoints
        print("  [OK] Refactored API")

        print("\n[SUCCESS] All imports verified")
        return True

    except ImportError as e:
        print(f"\n[FAIL] Import error: {e}")
        return False

def verify_database():
    """Verify database connection"""
    print("\n[*] Verifying database connection...")

    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', 5434)),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )

        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()

        print("  [OK] Database connection successful")
        return True

    except Exception as e:
        print(f"  [FAIL] Database connection failed: {e}")
        return False

def verify_rls_functions():
    """Verify RLS functions exist"""
    print("\n[*] Verifying RLS functions...")

    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
            port=int(os.getenv('POSTGRES_PORT', 5434)),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )

        cur = conn.cursor()

        # Test set_project_context function
        cur.execute("SELECT set_project_context(1)")
        print("  [OK] set_project_context() function exists")

        # Test get_current_project_id function
        cur.execute("SELECT get_current_project_id()")
        result = cur.fetchone()[0]
        print(f"  [OK] get_current_project_id() returned: {result}")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"  [FAIL] RLS functions error: {e}")
        return False

def verify_flask_app():
    """Verify Flask app can be created"""
    print("\n[*] Verifying Flask app creation...")

    try:
        from flask import Flask
        from flask_cors import CORS
        from api_refactored_with_middleware import register_refactored_endpoints

        app = Flask(__name__)
        CORS(app)

        register_refactored_endpoints(app)

        print("  [OK] Flask app created")
        print(f"  [OK] {len(app.url_map._rules)} routes registered")

        # List registered v2 routes
        v2_routes = [rule.rule for rule in app.url_map.iter_rules() if '/api/v2/' in rule.rule]
        print(f"\n  Registered v2 endpoints:")
        for route in sorted(v2_routes):
            print(f"    - {route}")

        return True

    except Exception as e:
        print(f"  [FAIL] Flask app creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all verifications"""

    print("=" * 70)
    print("API V2 STARTUP VERIFICATION")
    print("=" * 70)

    results = {
        'imports': verify_imports(),
        'database': verify_database(),
        'rls_functions': verify_rls_functions(),
        'flask_app': verify_flask_app()
    }

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for check, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n[SUCCESS] API v2 is ready to start!")
        print("\nStart with:")
        print("  python api_middleware_server.py")
        print("\nThen test:")
        print("  curl http://localhost:5020/api/v2/health")
        return True
    else:
        print("\n[FAIL] Some verifications failed")
        print("Fix the issues above before starting the API")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
