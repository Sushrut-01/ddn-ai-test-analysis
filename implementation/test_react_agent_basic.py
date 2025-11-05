"""
Test Script for ReAct Agent - Task 0-ARCH.2
Quick validation that the agent works with real integrations

Usage:
    python test_react_agent_basic.py
"""

import sys
import os
import json
from dotenv import load_dotenv

# Add implementation directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

# Import agent
from agents.react_agent_service import create_react_agent

def test_code_error():
    """Test CODE_ERROR analysis"""
    print("=" * 80)
    print("TEST 1: CODE_ERROR - NullPointerException")
    print("=" * 80)

    agent = create_react_agent()

    result = agent.analyze(
        build_id="test-code-001",
        error_message="NullPointerException: Cannot invoke method on null object at line 45",
        error_log="""
        Test: test_user_authentication
        Status: FAILED

        java.lang.NullPointerException: Cannot invoke "getUserDetails" because "user" is null
            at com.example.UserService.authenticate(UserService.java:45)
            at com.example.AuthController.login(AuthController.java:23)

        Expected: User authentication to succeed
        Actual: NullPointerException thrown
        """,
        stack_trace="at com.example.UserService.authenticate(UserService.java:45)",
        test_name="test_user_authentication",
        job_name="auth-service-tests"
    )

    print("\nRESULT:")
    print(json.dumps(result, indent=2))
    print("\n")

    return result


def test_infra_error():
    """Test INFRA_ERROR analysis"""
    print("=" * 80)
    print("TEST 2: INFRA_ERROR - OutOfMemoryError")
    print("=" * 80)

    agent = create_react_agent()

    result = agent.analyze(
        build_id="test-infra-001",
        error_message="OutOfMemoryError: Java heap space",
        error_log="""
        Test: test_large_dataset_processing
        Status: FAILED

        java.lang.OutOfMemoryError: Java heap space
            at java.util.Arrays.copyOf(Arrays.java:3332)
            at java.util.ArrayList.grow(ArrayList.java:275)

        Heap Memory Usage:
        - Initial: 256MB
        - Max: 512MB
        - Used: 512MB (100%)
        """,
        test_name="test_large_dataset_processing",
        job_name="data-processor-tests"
    )

    print("\nRESULT:")
    print(json.dumps(result, indent=2))
    print("\n")

    return result


def test_config_error():
    """Test CONFIG_ERROR analysis"""
    print("=" * 80)
    print("TEST 3: CONFIG_ERROR - Permission Denied")
    print("=" * 80)

    agent = create_react_agent()

    result = agent.analyze(
        build_id="test-config-001",
        error_message="Permission denied: /var/log/app.log",
        error_log="""
        Test: test_log_file_creation
        Status: FAILED

        PermissionError: [Errno 13] Permission denied: '/var/log/app.log'
            at logging.FileHandler.__init__(FileHandler.py:55)
            at app.setup_logging(app.py:12)

        File permissions: /var/log/app.log (read-only)
        Process user: appuser (uid: 1000)
        File owner: root (uid: 0)
        """,
        test_name="test_log_file_creation",
        job_name="logging-tests"
    )

    print("\nRESULT:")
    print(json.dumps(result, indent=2))
    print("\n")

    return result


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ReAct Agent Test Suite - Task 0-ARCH.2" + " " * 19 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    results = []

    # Test 1: CODE_ERROR
    try:
        result1 = test_code_error()
        results.append(("CODE_ERROR", result1['success']))
    except Exception as e:
        print(f"❌ CODE_ERROR test failed: {e}\n")
        results.append(("CODE_ERROR", False))

    # Test 2: INFRA_ERROR
    try:
        result2 = test_infra_error()
        results.append(("INFRA_ERROR", result2['success']))
    except Exception as e:
        print(f"❌ INFRA_ERROR test failed: {e}\n")
        results.append(("INFRA_ERROR", False))

    # Test 3: CONFIG_ERROR
    try:
        result3 = test_config_error()
        results.append(("CONFIG_ERROR", result3['success']))
    except Exception as e:
        print(f"❌ CONFIG_ERROR test failed: {e}\n")
        results.append(("CONFIG_ERROR", False))

    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    print("=" * 80)


if __name__ == "__main__":
    main()
