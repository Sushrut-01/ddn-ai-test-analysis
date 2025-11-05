"""
Test script for re-ranking service (Phase 2 - Task 2.2)

Tests:
1. Model initialization
2. Health endpoint
3. Re-ranking with sample data
"""

import requests
import time
import sys

RERANK_SERVICE_URL = "http://localhost:5009"

def test_health():
    """Test health endpoint"""
    print("=" * 60)
    print("TEST 1: Health Check")
    print("=" * 60)

    try:
        response = requests.get(f"{RERANK_SERVICE_URL}/health", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print("\n" + "=" * 60)
    print("TEST 2: Model Info")
    print("=" * 60)

    try:
        response = requests.get(f"{RERANK_SERVICE_URL}/model-info", timeout=5)
        print(f"✅ Status Code: {response.status_code}")
        data = response.json()
        print(f"✅ Model: {data.get('model_name')}")
        print(f"✅ Loaded: {data.get('model_loaded')}")
        print(f"✅ Max Length: {data.get('max_text_length')}")
        return True
    except Exception as e:
        print(f"❌ Model info failed: {e}")
        return False

def test_rerank():
    """Test re-ranking with sample candidates"""
    print("\n" + "=" * 60)
    print("TEST 3: Re-Ranking")
    print("=" * 60)

    # Sample query and candidates
    query = "TimeoutError in HA failover test"
    candidates = [
        {
            "text": "TimeoutError: Connection timed out after 30 seconds in high availability test",
            "score": 0.85,
            "metadata": {"error_category": "TIMEOUT_ERROR"}
        },
        {
            "text": "Network connection refused error",
            "score": 0.82,
            "metadata": {"error_category": "NETWORK_ERROR"}
        },
        {
            "text": "High availability failover timeout during switch",
            "score": 0.80,
            "metadata": {"error_category": "TIMEOUT_ERROR"}
        },
        {
            "text": "Database authentication failed",
            "score": 0.78,
            "metadata": {"error_category": "AUTH_ERROR"}
        },
        {
            "text": "HA test timeout when switching primary node",
            "score": 0.75,
            "metadata": {"error_category": "TIMEOUT_ERROR"}
        }
    ]

    payload = {
        "query": query,
        "candidates": candidates,
        "top_k": 3
    }

    try:
        print(f"Query: {query}")
        print(f"Candidates: {len(candidates)}")
        print(f"Top K: 3")
        print()

        response = requests.post(
            f"{RERANK_SERVICE_URL}/rerank",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            print(f"✅ Total candidates: {data.get('total_candidates')}")
            print(f"✅ Reranked count: {data.get('reranked_count')}")
            print(f"✅ Processing time: {data.get('processing_time_ms')}ms")
            print()

            print("Top 3 Results:")
            for i, result in enumerate(data.get('results', []), 1):
                print(f"\n  {i}. Text: {result.get('text', '')[:60]}...")
                print(f"     Original Score: {result.get('score', 0):.4f}")
                print(f"     Rerank Score: {result.get('rerank_score', 0):.4f}")

            return True
        else:
            print(f"❌ Status Code: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Re-ranking failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("RE-RANKING SERVICE TEST SUITE")
    print("=" * 60)
    print()

    # Wait for service to start
    print("Waiting for service to start...")
    for i in range(5):
        try:
            requests.get(f"{RERANK_SERVICE_URL}/health", timeout=2)
            print("✅ Service is ready!")
            break
        except:
            print(f"   Attempt {i+1}/5: Service not ready, waiting...")
            time.sleep(2)
    else:
        print("❌ Service did not start in time")
        print("\nPlease start the service manually:")
        print("   python reranking_service.py")
        sys.exit(1)

    print()

    # Run tests
    tests = [
        ("Health Check", test_health),
        ("Model Info", test_model_info),
        ("Re-Ranking", test_rerank)
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
