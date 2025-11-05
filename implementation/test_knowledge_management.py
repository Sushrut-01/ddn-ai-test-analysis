"""
Test Script for Knowledge Management API
=========================================
Task 0-HITL-KM: Comprehensive testing of all endpoints

Tests:
1. Health check
2. Get all documents
3. Get categories
4. Get statistics
5. Add new document
6. Update document
7. Delete document
8. Category refresh

Usage:
    python test_knowledge_management.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5008"
HEADERS = {"Content-Type": "application/json"}

# Test counters
tests_passed = 0
tests_failed = 0
test_results = []

def log_test(test_name, passed, message=""):
    """Log test result"""
    global tests_passed, tests_failed
    status = "✅ PASS" if passed else "❌ FAIL"
    result = {
        "test": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)

    if passed:
        tests_passed += 1
        print(f"{status} - {test_name}")
    else:
        tests_failed += 1
        print(f"{status} - {test_name}")
        if message:
            print(f"     Error: {message}")

def test_health_check():
    """Test 1: Health check endpoint"""
    test_name = "Health Check"
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                log_test(test_name, True, f"Service is healthy")
                return True
            else:
                log_test(test_name, False, "Service returned unhealthy status")
                return False
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_test(test_name, False, "Could not connect to API. Is the server running on port 5008?")
        return False
    except Exception as e:
        log_test(test_name, False, str(e))
        return False

def test_get_all_docs():
    """Test 2: Get all knowledge documents"""
    test_name = "Get All Documents"
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/docs", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "documents" in data and "count" in data:
                count = data.get("count", 0)
                log_test(test_name, True, f"Retrieved {count} documents")
                return True, data
            else:
                log_test(test_name, False, "Invalid response format")
                return False, None
        else:
            log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        log_test(test_name, False, str(e))
        return False, None

def test_get_categories():
    """Test 3: Get all categories"""
    test_name = "Get Categories"
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/categories", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "categories" in data:
                categories = data.get("categories", [])
                cat_count = len(categories)
                log_test(test_name, True, f"Found {cat_count} categories")
                return True, data
            else:
                log_test(test_name, False, "Invalid response format")
                return False, None
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False, None
    except Exception as e:
        log_test(test_name, False, str(e))
        return False, None

def test_get_stats():
    """Test 4: Get knowledge base statistics"""
    test_name = "Get Statistics"
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/stats", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "statistics" in data:
                stats = data["statistics"]
                total_docs = stats.get("total_documents", 0)
                total_vectors = stats.get("total_vectors", 0)
                log_test(test_name, True, f"Total docs: {total_docs}, Total vectors: {total_vectors}")
                return True, data
            else:
                log_test(test_name, False, "Invalid response format")
                return False, None
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False, None
    except Exception as e:
        log_test(test_name, False, str(e))
        return False, None

def test_add_document():
    """Test 5: Add new knowledge document"""
    test_name = "Add New Document"

    # Create test document
    test_doc = {
        "error_id": f"TEST_ERR_{int(time.time())}",
        "error_type": "TestTimeoutError",
        "error_category": "CODE_ERROR",
        "category_description": "Code-related errors",
        "subcategory": "Timeout",
        "error_message": "Test: Connection timeout after 30 seconds",
        "component": "test-service",
        "file_path": "src/test/TestService.py",
        "line_range": "100-105",
        "root_cause": "Test: Network timeout due to slow database query",
        "solution": "Test: Optimize database query and add connection pooling",
        "solution_steps": [
            "Add index to database table",
            "Implement connection pooling",
            "Add timeout configuration"
        ],
        "prevention": "Test: Regular performance testing and monitoring",
        "code_before": "result = db.query('SELECT * FROM large_table')",
        "code_after": "result = db.query('SELECT * FROM large_table LIMIT 1000')",
        "severity": "HIGH",
        "frequency": "MEDIUM",
        "tags": ["timeout", "database", "performance"],
        "test_scenarios": ["Load test with 1000 users", "Stress test with slow network"],
        "created_by": "test_script"
    }

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/knowledge/docs",
            json=test_doc,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code == 201:
            data = response.json()
            if data.get("success") and data.get("document_id"):
                doc_id = data["document_id"]
                category_refresh = data.get("category_refresh", False)
                log_test(test_name, True, f"Created document: {doc_id}, Category refresh: {category_refresh}")
                return True, doc_id
            else:
                log_test(test_name, False, "Invalid response format")
                return False, None
        else:
            log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
            return False, None
    except Exception as e:
        log_test(test_name, False, str(e))
        return False, None

def test_get_specific_doc(doc_id):
    """Test 6: Get specific document by ID"""
    test_name = "Get Specific Document"
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge/docs/{doc_id}", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if "document" in data:
                doc = data["document"]
                log_test(test_name, True, f"Retrieved document: {doc.get('error_type')}")
                return True, doc
            else:
                log_test(test_name, False, "Invalid response format")
                return False, None
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False, None
    except Exception as e:
        log_test(test_name, False, str(e))
        return False, None

def test_update_document(doc_id):
    """Test 7: Update existing document"""
    test_name = "Update Document"

    update_data = {
        "severity": "CRITICAL",
        "frequency": "HIGH",
        "prevention": "UPDATED: Enhanced monitoring and alerting system",
        "updated_by": "test_script"
    }

    try:
        response = requests.put(
            f"{API_BASE_URL}/api/knowledge/docs/{doc_id}",
            json=update_data,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                log_test(test_name, True, f"Updated document: {doc_id}")
                return True
            else:
                log_test(test_name, False, "Invalid response format")
                return False
        else:
            log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test(test_name, False, str(e))
        return False

def test_search_filter():
    """Test 8: Search and filter documents"""
    test_name = "Search and Filter"
    try:
        # Test with search query
        response = requests.get(
            f"{API_BASE_URL}/api/knowledge/docs?search=timeout&limit=10",
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            log_test(test_name, True, f"Search found {count} results")
            return True
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test(test_name, False, str(e))
        return False

def test_category_refresh():
    """Test 9: Trigger category refresh"""
    test_name = "Category Refresh"
    try:
        response = requests.post(f"{API_BASE_URL}/api/knowledge/refresh", timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                count = data.get("count", 0)
                categories = data.get("categories", [])
                log_test(test_name, True, f"Refreshed {count} categories: {categories[:3]}...")
                return True
            else:
                log_test(test_name, False, "Invalid response format")
                return False
        else:
            log_test(test_name, False, f"HTTP {response.status_code}")
            return False
    except Exception as e:
        log_test(test_name, False, str(e))
        return False

def test_delete_document(doc_id):
    """Test 10: Delete document"""
    test_name = "Delete Document"
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/knowledge/docs/{doc_id}?user=test_script",
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                log_test(test_name, True, f"Deleted document: {doc_id}")
                return True
            else:
                log_test(test_name, False, "Invalid response format")
                return False
        else:
            log_test(test_name, False, f"HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        log_test(test_name, False, str(e))
        return False

def test_audit_trail():
    """Test 11: Verify audit trail in PostgreSQL"""
    test_name = "Audit Trail"
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import os
        from dotenv import load_dotenv

        load_dotenv()

        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Check if table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'knowledge_doc_changes'
            )
        """)
        table_exists = cursor.fetchone()['exists']

        if not table_exists:
            log_test(test_name, False, "Table knowledge_doc_changes does not exist")
            cursor.close()
            conn.close()
            return False

        # Get recent changes
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM knowledge_doc_changes
            WHERE changed_at >= NOW() - INTERVAL '1 hour'
        """)
        result = cursor.fetchone()
        recent_count = result['count']

        cursor.close()
        conn.close()

        log_test(test_name, True, f"Found {recent_count} recent changes in audit trail")
        return True

    except Exception as e:
        log_test(test_name, False, f"Could not connect to PostgreSQL: {str(e)}")
        return False

def print_summary():
    """Print test summary"""
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {tests_passed + tests_failed}")
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed / (tests_passed + tests_failed) * 100):.1f}%")
    print("=" * 70)

    if tests_failed > 0:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    else:
        print("\n🎉 All tests passed! Knowledge Management API is working correctly.")

def main():
    """Main test execution"""
    print("=" * 70)
    print("KNOWLEDGE MANAGEMENT API - TEST SUITE")
    print("=" * 70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # Test 1: Health Check
    health_ok = test_health_check()
    if not health_ok:
        print("\n❌ API is not running. Please start the Knowledge Management API:")
        print("   python implementation/knowledge_management_api.py")
        return

    print()

    # Test 2: Get All Documents
    docs_ok, docs_data = test_get_all_docs()

    # Test 3: Get Categories
    cat_ok, cat_data = test_get_categories()

    # Test 4: Get Statistics
    stats_ok, stats_data = test_get_stats()

    print()

    # Test 5: Add Document
    add_ok, doc_id = test_add_document()

    if add_ok and doc_id:
        # Wait a moment for processing
        time.sleep(2)

        # Test 6: Get Specific Document
        get_ok, doc_data = test_get_specific_doc(doc_id)

        # Test 7: Update Document
        update_ok = test_update_document(doc_id)

        # Wait a moment for processing
        time.sleep(1)

        # Test 8: Search and Filter
        search_ok = test_search_filter()

        # Test 9: Category Refresh
        refresh_ok = test_category_refresh()

        # Wait a moment before delete
        time.sleep(1)

        # Test 10: Delete Document
        delete_ok = test_delete_document(doc_id)

    print()

    # Test 11: Audit Trail
    audit_ok = test_audit_trail()

    # Print Summary
    print_summary()

    # Save results to file
    try:
        with open("knowledge_management_test_results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_tests": tests_passed + tests_failed,
                "passed": tests_passed,
                "failed": tests_failed,
                "success_rate": (tests_passed / (tests_passed + tests_failed) * 100),
                "test_results": test_results
            }, f, indent=2)
        print(f"\n📝 Detailed results saved to: knowledge_management_test_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results file: {e}")

if __name__ == "__main__":
    main()
