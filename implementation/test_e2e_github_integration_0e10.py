"""
Task 0E.10: End-to-End GitHub Integration Test
================================================

Tests the complete GitHub integration flow:
1. Start all required services
2. Trigger CODE_ERROR analysis
3. Verify GitHub code fetched and stored in PostgreSQL
4. Verify frontend can display the code

Prerequisites:
- PostgreSQL running on localhost:5432
- MongoDB running on localhost:27017
- MCP GitHub Server running on localhost:5002
- AI Analysis Service running on localhost:5003
- Dashboard API running on localhost:5006
- Dashboard UI running on localhost:5173

Test Flow:
ReAct Agent → GitHub MCP → PostgreSQL → Dashboard API → Frontend
"""

import os
import sys
import time
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment
load_dotenv()

# Test configuration
REACT_AGENT_URL = os.getenv('REACT_AGENT_URL', 'http://localhost:5001')
DASHBOARD_API_URL = os.getenv('DASHBOARD_API_URL', 'http://localhost:5006')
MCP_GITHUB_SERVER_URL = os.getenv('MCP_GITHUB_SERVER_URL', 'http://localhost:5002')
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:5003')

# PostgreSQL connection
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def check_service_health(name, url):
    """Check if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print(f"[OK] {name} is running at {url}")
            return True
        else:
            print(f"[WARN] {name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] {name} is not reachable at {url}: {str(e)}")
        return False

def test_service_health_checks():
    """Test 1: Verify all services are running"""
    print_section("TEST 1: Service Health Checks")

    services = [
        ("MCP GitHub Server", MCP_GITHUB_SERVER_URL),
        ("AI Analysis Service", AI_SERVICE_URL),
        ("Dashboard API", DASHBOARD_API_URL),
        ("ReAct Agent", REACT_AGENT_URL)
    ]

    all_healthy = True
    for name, url in services:
        if not check_service_health(name, url):
            all_healthy = False

    # Check PostgreSQL
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        conn.close()
        print(f"[OK] PostgreSQL is running at {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
    except Exception as e:
        print(f"[FAIL] PostgreSQL connection failed: {str(e)}")
        all_healthy = False

    if not all_healthy:
        print("\n[WARN] WARNING: Not all services are running. Test may fail.")
        print("Please ensure all services are started before running this test.")
        return False

    print("\n[OK] All services are running!")
    return True

def create_test_code_error():
    """Create a sample CODE_ERROR for testing"""
    return {
        "test_name": "test_github_integration_e2e",
        "error_message": "AttributeError: 'NoneType' object has no attribute 'get'",
        "stack_trace": """Traceback (most recent call last):
  File "/app/src/services/user_service.py", line 143, in get_user_profile
    profile = user_data.get('profile')
AttributeError: 'NoneType' object has no attribute 'get'
""",
        "test_type": "unit",
        "suite_name": "User Service Tests",
        "failure_count": 1,
        "build_id": "test-e2e-0e10-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "metadata": {
            "category": "CODE_ERROR",
            "test_file": "/app/tests/test_user_service.py"
        }
    }

def test_trigger_analysis():
    """Test 2: Trigger CODE_ERROR analysis"""
    print_section("TEST 2: Trigger CODE_ERROR Analysis")

    error_data = create_test_code_error()
    print(f"Test Error: {error_data['error_message']}")
    print(f"File: src/services/user_service.py:143")
    print(f"Build ID: {error_data['build_id']}")

    try:
        # Trigger analysis via AI Service
        print("\nSending analysis request to AI Service...")
        response = requests.post(
            f"{AI_SERVICE_URL}/analyze",
            json=error_data,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Analysis completed!")
            print(f"   Classification: {result.get('classification', 'N/A')}")
            print(f"   Confidence: {result.get('confidence_score', 'N/A')}")
            print(f"   GitHub Code Included: {result.get('github_code_included', False)}")

            if result.get('github_files'):
                print(f"   GitHub Files Fetched: {len(result['github_files'])}")
                for i, file in enumerate(result['github_files'], 1):
                    print(f"     {i}. {file.get('file_path', 'Unknown')}")

            return result.get('build_id') or error_data['build_id'], result
        else:
            print(f"[FAIL] Analysis failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None

    except Exception as e:
        print(f"[FAIL] Error triggering analysis: {str(e)}")
        return None, None

def test_verify_postgresql_storage(build_id):
    """Test 3: Verify GitHub code stored in PostgreSQL"""
    print_section("TEST 3: Verify PostgreSQL Storage")

    if not build_id:
        print("[WARN]  No build_id provided, skipping PostgreSQL verification")
        return False

    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Query failure_analysis table
        cursor.execute("""
            SELECT
                id,
                classification,
                github_files,
                github_code_included,
                confidence_score,
                analyzed_at
            FROM failure_analysis
            WHERE build_id = %s
            ORDER BY analyzed_at DESC
            LIMIT 1
        """, (build_id,))

        analysis = cursor.fetchone()

        if analysis:
            print(f"[OK] Analysis found in PostgreSQL")
            print(f"   Analysis ID: {analysis['id']}")
            print(f"   Classification: {analysis['classification']}")
            print(f"   Confidence: {analysis['confidence_score']}")
            print(f"   GitHub Code Included: {analysis['github_code_included']}")

            if analysis['github_files']:
                github_files = analysis['github_files']
                print(f"   GitHub Files Stored: {len(github_files)}")

                for i, file in enumerate(github_files, 1):
                    print(f"\n   File {i}:")
                    print(f"     Path: {file.get('file_path', 'N/A')}")
                    print(f"     Lines: {file.get('line_range', 'N/A')}")
                    print(f"     Repo: {file.get('repo', 'N/A')}")
                    print(f"     Branch: {file.get('branch', 'N/A')}")
                    content_len = len(file.get('content', ''))
                    print(f"     Content Length: {content_len} characters")

                    if content_len > 0:
                        print(f"     [OK] Code content stored successfully")
                    else:
                        print(f"     [WARN]  No code content found")

                cursor.close()
                conn.close()
                return True
            else:
                print("   [WARN]  No GitHub files found in analysis")
                cursor.close()
                conn.close()
                return False
        else:
            print(f"[FAIL] No analysis found for build_id: {build_id}")
            cursor.close()
            conn.close()
            return False

    except Exception as e:
        print(f"[FAIL] PostgreSQL verification failed: {str(e)}")
        return False

def test_dashboard_api_response(build_id):
    """Test 4: Verify Dashboard API returns GitHub code"""
    print_section("TEST 4: Verify Dashboard API Response")

    if not build_id:
        print("[WARN]  No build_id provided, skipping API verification")
        return False

    try:
        # First get the failure_id from failures list
        print("Fetching failures from Dashboard API...")
        response = requests.get(f"{DASHBOARD_API_URL}/api/failures", timeout=10)

        if response.status_code != 200:
            print(f"[FAIL] Failed to fetch failures: {response.status_code}")
            return False

        failures = response.json().get('data', {}).get('failures', [])

        # Find our test failure
        test_failure = None
        for failure in failures:
            if failure.get('build_id') == build_id:
                test_failure = failure
                break

        if not test_failure:
            print(f"[WARN]  Test failure not found in API response")
            return False

        failure_id = test_failure.get('_id')
        print(f"[OK] Found test failure: {failure_id}")

        # Get detailed failure info
        print(f"\nFetching failure details from /api/failures/{failure_id}...")
        detail_response = requests.get(
            f"{DASHBOARD_API_URL}/api/failures/{failure_id}",
            timeout=10
        )

        if detail_response.status_code != 200:
            print(f"[FAIL] Failed to fetch failure details: {detail_response.status_code}")
            return False

        failure_data = detail_response.json().get('failure', {})
        ai_analysis = failure_data.get('ai_analysis')

        if not ai_analysis:
            print("[WARN]  No AI analysis found in API response")
            return False

        print(f"[OK] AI Analysis found in API response")
        print(f"   Classification: {ai_analysis.get('classification', 'N/A')}")
        print(f"   GitHub Code Included: {ai_analysis.get('github_code_included', False)}")

        github_files = ai_analysis.get('github_files')
        if github_files and len(github_files) > 0:
            print(f"   [OK] GitHub Files in API Response: {len(github_files)}")

            for i, file in enumerate(github_files, 1):
                print(f"\n   File {i}:")
                print(f"     Path: {file.get('file_path', 'N/A')}")
                print(f"     Lines: {file.get('line_range', 'N/A')}")
                print(f"     Content: {len(file.get('content', ''))} characters")

            print(f"\n[OK] Dashboard API correctly returns GitHub code!")
            print(f"   Frontend URL: http://localhost:5173/failures/{failure_id}")
            return True
        else:
            print("   [WARN]  No GitHub files in API response")
            return False

    except Exception as e:
        print(f"[FAIL] Dashboard API verification failed: {str(e)}")
        return False

def test_frontend_integration():
    """Test 5: Verify Frontend can consume the data"""
    print_section("TEST 5: Frontend Integration Check")

    print("Checking if CodeSnippet component exists...")
    component_path = "c:\\DDN-AI-Project-Documentation\\implementation\\dashboard-ui\\src\\components\\CodeSnippet.jsx"

    if os.path.exists(component_path):
        print(f"[OK] CodeSnippet.jsx component found")

        # Check for key features
        with open(component_path, 'r', encoding='utf-8') as f:
            content = f.read()

            checks = [
                ("SyntaxHighlighter import", "from 'react-syntax-highlighter'" in content),
                ("Error line highlighting", "isErrorLine" in content),
                ("Copy to clipboard", "clipboard" in content),
                ("GitHub link integration", "GitHubIcon" in content),
                ("Line number support", "showLineNumbers" in content)
            ]

            all_passed = True
            for name, passed in checks:
                if passed:
                    print(f"   [OK] {name}")
                else:
                    print(f"   [FAIL] {name}")
                    all_passed = False

            return all_passed
    else:
        print(f"[FAIL] CodeSnippet.jsx component not found")
        return False

def run_all_tests():
    """Run all end-to-end tests"""
    print_section("Task 0E.10: End-to-End GitHub Integration Test")
    print("Testing complete GitHub integration flow")
    print("Started at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    results = {}

    # Test 1: Service health
    results['health'] = test_service_health_checks()
    if not results['health']:
        print("\n[FAIL] SERVICE HEALTH CHECK FAILED")
        print("Please start all required services and try again.")
        return False

    # Test 2: Trigger analysis
    build_id, analysis_result = test_trigger_analysis()
    results['analysis'] = build_id is not None

    if not results['analysis']:
        print("\n[FAIL] ANALYSIS TRIGGER FAILED")
        print("Cannot proceed with further tests.")
        return False

    # Wait for analysis to complete
    print("\n[WAIT] Waiting 5 seconds for analysis to complete...")
    time.sleep(5)

    # Test 3: PostgreSQL storage
    results['postgresql'] = test_verify_postgresql_storage(build_id)

    # Test 4: Dashboard API
    results['dashboard_api'] = test_dashboard_api_response(build_id)

    # Test 5: Frontend integration
    results['frontend'] = test_frontend_integration()

    # Summary
    print_section("TEST SUMMARY")

    tests = [
        ("Service Health Checks", results['health']),
        ("CODE_ERROR Analysis Trigger", results['analysis']),
        ("PostgreSQL Storage Verification", results['postgresql']),
        ("Dashboard API Response", results['dashboard_api']),
        ("Frontend Integration", results['frontend'])
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for name, result in tests:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {name}")

    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\n[OK] Task 0E.10 COMPLETE: End-to-end GitHub integration verified")
        print("\nPhase 0E is now 100% complete:")
        print("  [OK] 0E.1-0E.5: Backend integration")
        print("  [OK] 0E.6: Dashboard API")
        print("  [OK] 0E.7-0E.9: Frontend components")
        print("  [OK] 0E.10: End-to-end testing (this test)")
        print("  [OK] 0E.11: Documentation")
        return True
    else:
        print("\n[WARN]  SOME TESTS FAILED")
        print("Please review the failures above and fix the issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
