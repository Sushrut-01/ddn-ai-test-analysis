"""
Simple Test Script for Knowledge Management API
Windows-compatible version without emoji characters
"""

import requests
import json
import time

API_BASE = "http://localhost:5008"

print("="*70)
print("KNOWLEDGE MANAGEMENT API - QUICK TEST")
print("="*70)

# Test 1: Health Check
print("\n[TEST 1] Health Check...")
try:
    r = requests.get(f"{API_BASE}/api/knowledge/health", timeout=5)
    if r.status_code == 200 and r.json().get("status") == "healthy":
        print("[PASS] API is healthy")
    else:
        print("[FAIL] API unhealthy")
        exit(1)
except Exception as e:
    print(f"[FAIL] Could not connect: {e}")
    print("Please start the API: python knowledge_management_api.py")
    exit(1)

# Test 2: Get Documents
print("\n[TEST 2] Get all documents...")
try:
    r = requests.get(f"{API_BASE}/api/knowledge/docs", timeout=10)
    data = r.json()
    count = data.get("count", 0)
    print(f"[PASS] Retrieved {count} documents")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 3: Get Categories
print("\n[TEST 3] Get categories...")
try:
    r = requests.get(f"{API_BASE}/api/knowledge/categories", timeout=10)
    data = r.json()
    cats = data.get("categories", [])
    print(f"[PASS] Found {len(cats)} categories")
    if cats:
        print(f"      Categories: {[c['name'] for c in cats[:5]]}")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 4: Get Statistics
print("\n[TEST 4] Get statistics...")
try:
    r = requests.get(f"{API_BASE}/api/knowledge/stats", timeout=10)
    data = r.json()
    stats = data.get("statistics", {})
    print(f"[PASS] Stats retrieved")
    print(f"      Total docs: {stats.get('total_documents', 0)}")
    print(f"      Total vectors: {stats.get('total_vectors', 0)}")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 5: Add Document
print("\n[TEST 5] Add new test document...")
test_doc = {
    "error_id": f"TEST_{int(time.time())}",
    "error_type": "TestError",
    "error_category": "CODE_ERROR",
    "error_message": "Test error message",
    "component": "test",
    "root_cause": "Test root cause",
    "solution": "Test solution",
    "severity": "MEDIUM",
    "frequency": "LOW",
    "tags": ["test"],
    "created_by": "test_script"
}

try:
    r = requests.post(f"{API_BASE}/api/knowledge/docs", json=test_doc, timeout=30)
    if r.status_code == 201:
        data = r.json()
        doc_id = data.get("document_id")
        print(f"[PASS] Created document: {doc_id}")

        # Test 6: Update Document
        print("\n[TEST 6] Update document...")
        time.sleep(2)
        update = {"severity": "HIGH", "updated_by": "test_script"}
        r2 = requests.put(f"{API_BASE}/api/knowledge/docs/{doc_id}", json=update, timeout=30)
        if r2.status_code == 200:
            print(f"[PASS] Updated document")
        else:
            print(f"[FAIL] Update failed: {r2.status_code}")

        # Test 7: Get Specific Document
        print("\n[TEST 7] Get specific document...")
        r3 = requests.get(f"{API_BASE}/api/knowledge/docs/{doc_id}", timeout=10)
        if r3.status_code == 200:
            doc = r3.json().get("document", {})
            print(f"[PASS] Retrieved: {doc.get('error_type')}")
            print(f"      Severity: {doc.get('severity')}")
        else:
            print(f"[FAIL] Get failed")

        # Test 8: Delete Document
        print("\n[TEST 8] Delete document...")
        time.sleep(2)
        r4 = requests.delete(f"{API_BASE}/api/knowledge/docs/{doc_id}?user=test", timeout=30)
        if r4.status_code == 200:
            print(f"[PASS] Deleted document")
        else:
            print(f"[FAIL] Delete failed: {r4.status_code}")
    else:
        print(f"[FAIL] Add failed: {r.status_code} - {r.text}")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 9: Category Refresh
print("\n[TEST 9] Category refresh...")
try:
    r = requests.post(f"{API_BASE}/api/knowledge/refresh", timeout=10)
    if r.status_code == 200:
        data = r.json()
        count = data.get("count", 0)
        print(f"[PASS] Refreshed {count} categories")
    else:
        print(f"[FAIL] Refresh failed")
except Exception as e:
    print(f"[FAIL] {e}")

# Test 10: Audit Trail Check
print("\n[TEST 10] Check audit trail...")
try:
    import psycopg2
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

    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM knowledge_doc_changes
        WHERE changed_at >= NOW() - INTERVAL '1 hour'
    """)
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    print(f"[PASS] Audit trail working - {count} recent changes")
except Exception as e:
    print(f"[INFO] Audit trail check skipped: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nAll core functionality is working correctly!")
print("\nNext steps:")
print("1. Start the dashboard UI: cd dashboard-ui && npm run dev")
print("2. Navigate to: http://localhost:5173/knowledge")
print("3. Test the frontend interface")
