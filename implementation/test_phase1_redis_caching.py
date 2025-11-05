"""
Phase 1 Redis Caching - Integration Test
Tests Tasks 1.1-1.5 without requiring Redis to be installed

This test verifies:
1. Service starts with graceful Redis fallback
2. /health endpoint shows redis_available status
3. /cache-stats endpoint returns 503 when Redis unavailable
4. /analyze-error endpoint works with cache_hit: false
5. All Redis code paths handle unavailability gracefully
"""

import requests
import time
import json
from typing import Dict, Optional

# Test configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 5  # seconds

class Phase1RedisTest:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def log(self, test_name: str, passed: bool, message: str, details: Optional[Dict] = None):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2)}")
        print()

        self.results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "details": details
        })

        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def test_service_running(self) -> bool:
        """Test 1: Check if langgraph service is running"""
        test_name = "Test 1: Service Running"
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                self.log(test_name, True, "Service is running and healthy", data)
                return True
            else:
                self.log(test_name, False, f"Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log(test_name, False, "Service is not running. Please start langgraph_agent.py first")
            return False
        except Exception as e:
            self.log(test_name, False, f"Error: {e}")
            return False

    def test_health_redis_status(self) -> bool:
        """Test 2: /health endpoint shows redis_available field"""
        test_name = "Test 2: Health Endpoint Redis Status"
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            data = response.json()

            if 'redis_available' in data:
                redis_status = data['redis_available']
                if redis_status == False:
                    self.log(test_name, True,
                            "Health endpoint correctly shows redis_available: false (graceful degradation)",
                            {"redis_available": redis_status})
                    return True
                else:
                    self.log(test_name, True,
                            "Health endpoint shows redis_available: true (Redis is running)",
                            {"redis_available": redis_status})
                    return True
            else:
                self.log(test_name, False,
                        "Health endpoint missing redis_available field",
                        data)
                return False
        except Exception as e:
            self.log(test_name, False, f"Error: {e}")
            return False

    def test_cache_stats_without_redis(self) -> bool:
        """Test 3: /cache-stats returns 503 when Redis unavailable"""
        test_name = "Test 3: Cache Stats Without Redis"
        try:
            response = requests.get(f"{BASE_URL}/cache-stats", timeout=TIMEOUT)

            # Check if Redis is available from health endpoint first
            health_response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            redis_available = health_response.json().get('redis_available', False)

            if not redis_available:
                # Redis not available - should return 503
                if response.status_code == 503:
                    data = response.json()
                    if data.get('redis_available') == False:
                        self.log(test_name, True,
                                "Cache stats correctly returns 503 with redis_available: false",
                                data)
                        return True
                    else:
                        self.log(test_name, False,
                                "Response missing redis_available: false field",
                                data)
                        return False
                else:
                    self.log(test_name, False,
                            f"Expected 503, got {response.status_code}",
                            response.json())
                    return False
            else:
                # Redis is available - should return 200
                if response.status_code == 200:
                    data = response.json()
                    self.log(test_name, True,
                            "Cache stats returns 200 with Redis statistics",
                            {
                                "total_keys": data.get('total_keys'),
                                "memory_used_mb": data.get('memory_used_mb')
                            })
                    return True
                else:
                    self.log(test_name, False,
                            f"Expected 200, got {response.status_code}")
                    return False
        except Exception as e:
            self.log(test_name, False, f"Error: {e}")
            return False

    def test_analyze_error_cache_metadata(self) -> bool:
        """Test 4: /analyze-error includes cache_hit and cache_key metadata"""
        test_name = "Test 4: Analyze Error Cache Metadata"

        # Sample error for testing (simple error)
        payload = {
            "build_id": "test-phase1-001",
            "error_log": "Test error log for Phase 1 caching test",
            "error_message": "Sample error message for cache key generation"
        }

        try:
            print(f"   Sending analysis request (this may take 5-10 seconds)...")
            response = requests.post(
                f"{BASE_URL}/analyze-error",
                json=payload,
                timeout=30  # Analysis can take longer
            )

            if response.status_code != 200:
                self.log(test_name, False,
                        f"Expected 200, got {response.status_code}",
                        response.json() if response.text else None)
                return False

            data = response.json()

            # Check for required cache fields
            has_cache_hit = 'cache_hit' in data
            has_cache_key = 'cache_key' in data

            if has_cache_hit and has_cache_key:
                cache_hit = data['cache_hit']
                cache_key = data['cache_key']

                # First call should be cache MISS
                if cache_hit == False:
                    self.log(test_name, True,
                            "Analyze endpoint includes cache metadata (cache_hit: false as expected for first call)",
                            {
                                "cache_hit": cache_hit,
                                "cache_key": cache_key,
                                "build_id": data.get('build_id'),
                                "success": data.get('success')
                            })
                    return True
                else:
                    # If cache_hit is True, Redis must be running and we hit cached result
                    self.log(test_name, True,
                            "Analyze endpoint includes cache metadata (cache_hit: true - Redis is running with cached data)",
                            {
                                "cache_hit": cache_hit,
                                "cache_key": cache_key,
                                "build_id": data.get('build_id')
                            })
                    return True
            else:
                missing_fields = []
                if not has_cache_hit:
                    missing_fields.append('cache_hit')
                if not has_cache_key:
                    missing_fields.append('cache_key')

                self.log(test_name, False,
                        f"Response missing cache fields: {', '.join(missing_fields)}",
                        data)
                return False
        except requests.exceptions.Timeout:
            self.log(test_name, False,
                    "Request timed out (analysis may take longer than 30 seconds)")
            return False
        except Exception as e:
            self.log(test_name, False, f"Error: {e}")
            return False

    def test_cache_hit_if_redis_available(self) -> bool:
        """Test 5 (Optional): Test cache HIT if Redis is running"""
        test_name = "Test 5: Cache HIT (Optional)"

        # Check if Redis is available
        try:
            health_response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
            redis_available = health_response.json().get('redis_available', False)

            if not redis_available:
                self.log(test_name, True,
                        "Skipped - Redis not available (install Redis to test cache HIT)",
                        {"redis_available": False})
                return True

            # Same payload as Test 4 to hit cache
            payload = {
                "build_id": "test-phase1-001",
                "error_log": "Test error log for Phase 1 caching test",
                "error_message": "Sample error message for cache key generation"
            }

            print(f"   Sending second analysis request (should be cache HIT)...")
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/analyze-error",
                json=payload,
                timeout=30
            )
            elapsed_ms = (time.time() - start_time) * 1000

            if response.status_code != 200:
                self.log(test_name, False,
                        f"Expected 200, got {response.status_code}")
                return False

            data = response.json()
            cache_hit = data.get('cache_hit')

            if cache_hit == True:
                if elapsed_ms < 1000:  # Less than 1 second (expected < 100ms)
                    self.log(test_name, True,
                            f"Cache HIT successful with fast response ({elapsed_ms:.0f}ms)",
                            {
                                "cache_hit": cache_hit,
                                "response_time_ms": round(elapsed_ms),
                                "cache_key": data.get('cache_key')
                            })
                    return True
                else:
                    self.log(test_name, False,
                            f"Cache HIT but response took {elapsed_ms:.0f}ms (expected < 1000ms)",
                            {"response_time_ms": round(elapsed_ms)})
                    return False
            else:
                self.log(test_name, False,
                        "Expected cache_hit: true for repeated request, got false",
                        data)
                return False
        except Exception as e:
            self.log(test_name, False, f"Error: {e}")
            return False

    def run_all_tests(self):
        """Run all Phase 1 tests"""
        print("=" * 70)
        print("PHASE 1 REDIS CACHING - INTEGRATION TEST")
        print("=" * 70)
        print()
        print("Testing Tasks 1.1-1.5 without requiring Redis installation")
        print("Tests graceful degradation and cache metadata in responses")
        print()
        print("=" * 70)
        print()

        # Test 1: Service running
        if not self.test_service_running():
            print("\n[ERROR] Cannot proceed - langgraph service is not running")
            print("   Please start the service first:")
            print("   > cd implementation")
            print("   > python langgraph_agent.py")
            print()
            return False

        # Test 2: Health endpoint Redis status
        self.test_health_redis_status()

        # Test 3: Cache stats without Redis
        self.test_cache_stats_without_redis()

        # Test 4: Analyze error cache metadata
        # Note: This test may take 5-10 seconds as it runs a full analysis
        self.test_analyze_error_cache_metadata()

        # Test 5: Cache HIT (optional, only if Redis is running)
        self.test_cache_hit_if_redis_available()

        # Print summary
        print("=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"  Passed: {self.passed}")
        print(f"  Failed: {self.failed}")
        print()

        if self.failed == 0:
            print("[OK] ALL TESTS PASSED")
            print()
            print("Phase 1 Redis caching implementation is working correctly!")
            print("Install Redis to enable caching and run Task 1.5 for cache HIT test.")
        else:
            print("[ERROR] SOME TESTS FAILED")
            print()
            print("Please review the failures above and fix the issues.")

        print("=" * 70)

        # Save results to file
        results_file = "test_results/phase1_redis_test_results.json"
        import os
        os.makedirs("test_results", exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump({
                "total_tests": self.passed + self.failed,
                "passed": self.passed,
                "failed": self.failed,
                "results": self.results
            }, f, indent=2)

        print(f"\n[OK] Results saved to: {results_file}")
        print()

        return self.failed == 0


if __name__ == "__main__":
    tester = Phase1RedisTest()
    success = tester.run_all_tests()

    exit(0 if success else 1)
