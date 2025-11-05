"""
Test Self-Correction Mechanism - Task 0-ARCH.5
==============================================

Tests for the SelfCorrectionStrategy including:
1. Retry logic for transient errors
2. Exponential backoff timing
3. Max retries limit (3)
4. Alternative tool suggestions
5. Retry history tracking
6. Reset functionality

File: implementation/test_self_correction.py
Created: 2025-11-02
Task: 0-ARCH.5
"""

import sys
import os
import time

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths
implementation_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, implementation_dir)
agents_dir = os.path.join(implementation_dir, 'agents')
sys.path.insert(0, agents_dir)

# Direct import to avoid langgraph dependency
import importlib.util
spec = importlib.util.spec_from_file_location("correction_strategy", os.path.join(agents_dir, "correction_strategy.py"))
correction_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(correction_module)
SelfCorrectionStrategy = correction_module.SelfCorrectionStrategy


def print_header(title: str):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_test(test_num: int, description: str):
    """Print test header"""
    print(f"\n[Test {test_num}] {description}")


def print_result(passed: bool, message: str = ""):
    """Print test result"""
    status = "PASS" if passed else "FAIL"
    print(f"   [{status}] {message}")


# ============================================================================
# TEST SUITE
# ============================================================================

def test_1_transient_error_retry():
    """Test 1: Transient errors trigger retry"""
    print_test(1, "Transient errors trigger retry")

    corrector = SelfCorrectionStrategy()

    # Test various transient error types
    transient_errors = [
        Exception("Connection timeout"),
        Exception("Connection refused"),
        Exception("503 Service Unavailable"),
        Exception("Rate limit exceeded"),
        Exception("Temporary failure")
    ]

    all_passed = True
    for i, error in enumerate(transient_errors, 1):
        should_retry = corrector.should_retry(f"test_tool_{i}", error)
        print_result(should_retry, f"{str(error)[:40]} -> Retry: {should_retry}")
        if not should_retry:
            all_passed = False

    return all_passed


def test_2_permanent_error_no_retry():
    """Test 2: Permanent errors don't trigger retry"""
    print_test(2, "Permanent errors don't trigger retry")

    corrector = SelfCorrectionStrategy()

    # Test permanent error types
    permanent_errors = [
        Exception("File not found"),
        ValueError("Invalid parameter"),
        KeyError("Missing key"),
        AttributeError("No such attribute")
    ]

    all_passed = True
    for i, error in enumerate(permanent_errors, 1):
        should_retry = corrector.should_retry(f"test_tool_{i}", error)
        print_result(not should_retry, f"{str(error)[:40]} -> No Retry: {not should_retry}")
        if should_retry:
            all_passed = False

    return all_passed


def test_3_max_retries_limit():
    """Test 3: Max retries limit (3) is enforced"""
    print_test(3, "Max retries limit enforced (max 3)")

    corrector = SelfCorrectionStrategy()
    tool_name = "pinecone_knowledge"
    error = Exception("Connection timeout")

    retry_results = []
    for i in range(5):  # Try 5 times
        should_retry = corrector.should_retry(tool_name, error)
        retry_results.append(should_retry)
        print_result(True, f"Attempt {i+1}: Retry={should_retry} (Count: {corrector.retry_history.get(tool_name, 0)})")

    # First 3 should retry, last 2 should not
    expected = [True, True, True, False, False]
    passed = retry_results == expected

    print_result(passed, f"Expected: {expected}")
    print_result(passed, f"Got:      {retry_results}")

    return passed


def test_4_exponential_backoff():
    """Test 4: Exponential backoff timing (1s, 2s, 4s)"""
    print_test(4, "Exponential backoff timing")

    corrector = SelfCorrectionStrategy()
    tool_name = "github_get_file"
    error = Exception("Connection timeout")

    expected_backoffs = [1.0, 2.0, 4.0]
    actual_backoffs = []

    for i in range(3):
        corrector.should_retry(tool_name, error)  # Register retry
        backoff = corrector.get_backoff_time(tool_name)
        actual_backoffs.append(backoff)
        print_result(True, f"Retry {i+1}: Backoff = {backoff}s")

    passed = actual_backoffs == expected_backoffs
    print_result(passed, f"Expected: {expected_backoffs}")
    print_result(passed, f"Got:      {actual_backoffs}")

    return passed


def test_5_alternative_tool_suggestions():
    """Test 5: Alternative tool suggestions"""
    print_test(5, "Alternative tool suggestions")

    corrector = SelfCorrectionStrategy()

    test_cases = [
        ("github_get_file", "github_search_code"),
        ("pinecone_knowledge_search", "web_search_error"),
        ("mongodb_get_logs", "postgres_get_failure_history"),
        ("web_search_error", None),  # No alternative
        ("unknown_tool", None)  # Unknown tool
    ]

    all_passed = True
    for failed_tool, expected_alt in test_cases:
        actual_alt = corrector.suggest_alternative_tool(failed_tool)
        passed = actual_alt == expected_alt
        print_result(passed, f"{failed_tool} -> {actual_alt} (expected: {expected_alt})")
        if not passed:
            all_passed = False

    return all_passed


def test_6_retry_history_tracking():
    """Test 6: Retry history tracking"""
    print_test(6, "Retry history tracking")

    corrector = SelfCorrectionStrategy()
    error = Exception("Timeout")

    # Simulate retries for multiple tools
    corrector.should_retry("tool_a", error)
    corrector.should_retry("tool_a", error)
    corrector.should_retry("tool_b", error)

    stats = corrector.get_retry_stats()

    passed = (
        stats.get("tool_a") == 2 and
        stats.get("tool_b") == 1
    )

    print_result(passed, f"tool_a retries: {stats.get('tool_a')} (expected: 2)")
    print_result(passed, f"tool_b retries: {stats.get('tool_b')} (expected: 1)")

    return passed


def test_7_reset_tool_history():
    """Test 7: Reset tool history"""
    print_test(7, "Reset tool history")

    corrector = SelfCorrectionStrategy()
    tool_name = "test_tool"
    error = Exception("Timeout")

    # Add some retries
    corrector.should_retry(tool_name, error)
    corrector.should_retry(tool_name, error)

    before_reset = corrector.retry_history.get(tool_name, 0)

    # Reset
    corrector.reset_tool_history(tool_name)

    after_reset = corrector.retry_history.get(tool_name, 0)

    passed = before_reset == 2 and after_reset == 0

    print_result(passed, f"Before reset: {before_reset} retries")
    print_result(passed, f"After reset:  {after_reset} retries")

    return passed


def test_8_reset_all_history():
    """Test 8: Reset all history"""
    print_test(8, "Reset all history")

    corrector = SelfCorrectionStrategy()
    error = Exception("Timeout")

    # Add retries for multiple tools
    corrector.should_retry("tool_a", error)
    corrector.should_retry("tool_b", error)
    corrector.should_retry("tool_c", error)

    before_reset = len(corrector.retry_history)

    # Reset all
    corrector.reset_all_history()

    after_reset = len(corrector.retry_history)

    passed = before_reset == 3 and after_reset == 0

    print_result(passed, f"Before reset: {before_reset} tools tracked")
    print_result(passed, f"After reset:  {after_reset} tools tracked")

    return passed


def test_9_has_exhausted_retries():
    """Test 9: Check if retries exhausted"""
    print_test(9, "Check if retries exhausted")

    corrector = SelfCorrectionStrategy()
    tool_name = "test_tool"
    error = Exception("Timeout")

    # Do 3 retries (max)
    for _ in range(3):
        corrector.should_retry(tool_name, error)

    exhausted = corrector.has_exhausted_retries(tool_name)
    not_exhausted = corrector.has_exhausted_retries("other_tool")

    passed = exhausted and not not_exhausted

    print_result(passed, f"test_tool exhausted: {exhausted} (expected: True)")
    print_result(passed, f"other_tool exhausted: {not_exhausted} (expected: False)")

    return passed


def test_10_singleton_instance():
    """Test 10: Singleton instance works"""
    print_test(10, "Singleton instance")

    from correction_strategy import get_correction_strategy

    instance1 = get_correction_strategy()
    instance2 = get_correction_strategy()

    passed = instance1 is instance2

    print_result(passed, f"Same instance: {instance1 is instance2}")

    return passed


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all tests and report results"""
    print_header("TESTING SELF-CORRECTION MECHANISM (Task 0-ARCH.5)")

    tests = [
        test_1_transient_error_retry,
        test_2_permanent_error_no_retry,
        test_3_max_retries_limit,
        test_4_exponential_backoff,
        test_5_alternative_tool_suggestions,
        test_6_retry_history_tracking,
        test_7_reset_tool_history,
        test_8_reset_all_history,
        test_9_has_exhausted_retries,
        test_10_singleton_instance
    ]

    results = []
    for test_func in tests:
        try:
            passed = test_func()
            results.append((test_func.__name__, passed))
        except Exception as e:
            print_result(False, f"Test failed with exception: {e}")
            results.append((test_func.__name__, False))

    # Summary
    print_header("TEST RESULTS SUMMARY")
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {test_name}")

    print("\n" + "=" * 70)
    print(f" TOTAL: {passed_count}/{total_count} tests passed")
    print("=" * 70)

    if passed_count == total_count:
        print("\nSUCCESS - ALL TESTS PASSED!")
        print("Self-correction mechanism is working correctly.")
        return 0
    else:
        print(f"\nFAILURE - {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
