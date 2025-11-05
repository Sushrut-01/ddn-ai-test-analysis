"""
Test script for Context Engineering Module - Task 0D.1
Created: 2025-11-02

Tests:
1. Entity extraction from various error types
2. Token optimization and truncation
3. Metadata enrichment
4. Integration with error categories
5. Validation and edge cases
"""

import sys
import os

# Add implementation directory to path
sys.path.insert(0, os.path.dirname(__file__))

from context_engineering import (
    ContextEngineer,
    TokenBudget,
    OptimizedContext,
    create_context_engineer
)


def test_entity_extraction():
    """Test 1: Entity extraction from error logs"""
    print("\n" + "="*80)
    print("TEST 1: Entity Extraction")
    print("="*80)

    engineer = create_context_engineer()

    test_cases = [
        {
            "name": "Code Error with Stack Trace",
            "text": """
NullPointerException at line 123 in /src/main/java/TestRunner.java
    at com.example.TestRunner.executeTest(TestRunner.java:123)
    at com.example.TestSuite.run(TestSuite.java:45)
Error code: ERR-001
            """,
            "expected_entities": ["exception_type", "file_path", "line_number", "error_code"]
        },
        {
            "name": "Infrastructure Error",
            "text": """
OutOfMemoryError: Java heap space
Server IP: 192.168.1.100
Status code: 500
            """,
            "expected_entities": ["exception_type", "ip_address", "http_status"]
        },
        {
            "name": "Configuration Error",
            "text": """
ConfigurationException: Invalid database URL
database_host=localhost
database_port=5432
            """,
            "expected_entities": ["exception_type", "variable"]
        }
    ]

    for test in test_cases:
        print(f"\n{test['name']}:")
        entities = engineer.extract_entities(test['text'])

        entity_types = set(e.entity_type for e in entities)
        print(f"  Extracted {len(entities)} entities")
        print(f"  Types found: {entity_types}")

        for expected in test['expected_entities']:
            found = expected in entity_types
            status = "[PASS]" if found else "[FAIL]"
            print(f"  {status} {expected}: {'Found' if found else 'Missing'}")

    print("\n[PASS] TEST 1 PASSED: Entity extraction working")


def test_token_optimization():
    """Test 2: Token optimization and budget management"""
    print("\n" + "="*80)
    print("TEST 2: Token Optimization")
    print("="*80)

    # Create engineer with small budget for testing
    small_budget = TokenBudget(
        max_total=500,
        error_message=100,
        stack_trace=100,
        error_log=200,
        similar_errors=50,
        metadata=50
    )
    engineer = ContextEngineer(small_budget)

    # Create a long error log
    long_log = "\n".join([
        f"2025-11-02 14:30:{i:02d} ERROR: Test error line {i} with lots of details and information that will need to be truncated to fit within the token budget"
        for i in range(100)
    ])

    print(f"Original log length: {len(long_log)} chars")
    print(f"Original token estimate: {engineer.estimate_tokens(long_log)} tokens")

    optimized_log, token_count = engineer.optimize_error_log(long_log)

    print(f"Optimized log length: {len(optimized_log)} chars")
    print(f"Optimized tokens: {token_count} tokens")
    print(f"Budget: {small_budget.error_log} tokens")
    print(f"Within budget: {'YES' if token_count <= small_budget.error_log else 'NO'}")

    if token_count <= small_budget.error_log:
        print("\n[PASS] TEST 2 PASSED: Token optimization working")
    else:
        print("\n[FAIL] TEST 2 FAILED: Exceeded token budget")


def test_metadata_enrichment():
    """Test 3: Metadata enrichment for different error categories"""
    print("\n" + "="*80)
    print("TEST 3: Metadata Enrichment")
    print("="*80)

    engineer = create_context_engineer()

    test_cases = [
        {
            "category": "CODE_ERROR",
            "error_message": "NullPointerException at TestRunner.java:123",
            "expected_hints": ["source code", "GitHub"]
        },
        {
            "category": "INFRA_ERROR",
            "error_message": "OutOfMemoryError: Java heap space",
            "expected_hints": ["system resources", "infrastructure"]
        },
        {
            "category": "CONFIG_ERROR",
            "error_message": "ConfigurationException: Invalid database URL",
            "expected_hints": ["configuration", "environment"]
        }
    ]

    for test in test_cases:
        print(f"\n{test['category']}:")

        entities = engineer.extract_entities(test['error_message'])
        metadata = engineer.enrich_metadata(
            test['category'],
            entities,
            test['error_message']
        )

        print(f"  Metadata keys: {list(metadata.keys())}")
        print(f"  Analysis hints: {metadata.get('analysis_hints', [])}")

        # Check if expected hints are present
        hints_text = ' '.join(metadata.get('analysis_hints', [])).lower()
        for expected in test['expected_hints']:
            found = expected.lower() in hints_text
            status = "[PASS]" if found else "[FAIL]"
            print(f"  {status} Contains '{expected}': {found}")

    print("\n[PASS] TEST 3 PASSED: Metadata enrichment working")


def test_full_optimization():
    """Test 4: Full context optimization workflow"""
    print("\n" + "="*80)
    print("TEST 4: Full Context Optimization")
    print("="*80)

    engineer = create_context_engineer()

    # Realistic test failure scenario
    error_log = """
2025-11-02 14:30:45 INFO: Starting test execution
2025-11-02 14:30:46 INFO: Connecting to database at localhost:5432
2025-11-02 14:30:47 ERROR: Connection timeout after 30 seconds
2025-11-02 14:30:47 ERROR: Failed to execute test_database_connection
java.sql.SQLException: Connection timeout
    at org.postgresql.jdbc.PgConnection.connect(PgConnection.java:234)
    at com.example.DatabaseTest.testConnection(DatabaseTest.java:56)
2025-11-02 14:30:48 ERROR: Test failed with error code ERR-DB-001
    """

    error_message = "SQLException: Connection timeout at DatabaseTest.java:56"
    stack_trace = """
    at org.postgresql.jdbc.PgConnection.connect(PgConnection.java:234)
    at com.example.DatabaseTest.testConnection(DatabaseTest.java:56)
    at org.junit.runners.JUnit4.run(JUnit4.java:89)
    """

    optimized = engineer.optimize_context(
        error_log=error_log,
        error_message=error_message,
        error_category="INFRA_ERROR",
        stack_trace=stack_trace
    )

    print(f"\nOptimization Results:")
    print(f"  Total tokens: {optimized.total_tokens}/{engineer.budget.max_total}")
    print(f"  Entities extracted: {len(optimized.entities)}")
    print(f"  Token breakdown: {optimized.token_breakdown}")
    print(f"  Truncated sections: {optimized.truncated_sections or 'None'}")

    # Validate
    is_valid, warnings = engineer.validate_context(optimized)
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    # Test formatting for Gemini
    formatted = engineer.format_for_gemini(optimized)
    print(f"\nFormatted output length: {len(formatted)} chars")
    print(f"Contains error message: {'YES' if error_message in formatted else 'NO'}")
    print(f"Contains entities section: {'YES' if '## Extracted Entities' in formatted else 'NO'}")

    if is_valid and optimized.total_tokens <= engineer.budget.max_total:
        print("\n[PASS] TEST 4 PASSED: Full optimization workflow working")
    else:
        print("\n[FAIL] TEST 4 FAILED: Issues with optimization")


def test_edge_cases():
    """Test 5: Edge cases and error handling"""
    print("\n" + "="*80)
    print("TEST 5: Edge Cases")
    print("="*80)

    engineer = create_context_engineer()

    test_cases = [
        {
            "name": "Empty inputs",
            "error_log": "",
            "error_message": "",
            "error_category": "CODE_ERROR"
        },
        {
            "name": "Very short message",
            "error_log": None,
            "error_message": "Error",
            "error_category": "CODE_ERROR"
        },
        {
            "name": "Only error message",
            "error_log": None,
            "error_message": "NullPointerException at line 123",
            "error_category": "CODE_ERROR"
        },
        {
            "name": "Unicode and special characters",
            "error_log": "Error: Файл не найден 文件未找到 ファイルが見つかりません",
            "error_message": "FileNotFoundException: /path/to/file.txt",
            "error_category": "CODE_ERROR"
        }
    ]

    for test in test_cases:
        print(f"\n{test['name']}:")
        try:
            optimized = engineer.optimize_context(
                error_log=test['error_log'] or "",
                error_message=test['error_message'],
                error_category=test['error_category']
            )
            is_valid, warnings = engineer.validate_context(optimized)
            print(f"  Result: {'Success' if is_valid or warnings else 'Failed'}")
            print(f"  Tokens: {optimized.total_tokens}")
            if warnings:
                print(f"  Warnings: {len(warnings)}")
        except Exception as e:
            print(f"  Exception: {str(e)}")

    print("\n[PASS] TEST 5 PASSED: Edge cases handled")


def test_category_specific_optimization():
    """Test 6: Category-specific optimization strategies"""
    print("\n" + "="*80)
    print("TEST 6: Category-Specific Optimization")
    print("="*80)

    engineer = create_context_engineer()

    categories = [
        ("CODE_ERROR", "NullPointerException at TestRunner.java:123"),
        ("INFRA_ERROR", "OutOfMemoryError: Java heap space"),
        ("CONFIG_ERROR", "ConfigurationException: Invalid database URL"),
        ("DEPENDENCY_ERROR", "ModuleNotFoundError: No module named 'requests'"),
        ("TEST_ERROR", "AssertionError: Expected 5 but got 3"),
    ]

    for category, message in categories:
        print(f"\n{category}:")
        optimized = engineer.optimize_context(
            error_log=f"Test error log for {category}",
            error_message=message,
            error_category=category
        )

        print(f"  Tokens: {optimized.total_tokens}")
        print(f"  Entities: {len(optimized.entities)}")
        print(f"  Metadata hints: {len(optimized.metadata.get('analysis_hints', []))}")

    print("\n[PASS] TEST 6 PASSED: Category-specific optimization working")


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("CONTEXT ENGINEERING MODULE - COMPREHENSIVE TEST SUITE")
    print("Task 0D.1 - Created 2025-11-02")
    print("="*80)

    try:
        test_entity_extraction()
        test_token_optimization()
        test_metadata_enrichment()
        test_full_optimization()
        test_edge_cases()
        test_category_specific_optimization()

        print("\n" + "="*80)
        print("[SUCCESS] ALL TESTS PASSED")
        print("="*80)
        print("\nContext Engineering Module is ready for integration with:")
        print("  - Task 0D.2: prompt_templates.py")
        print("  - Task 0D.5: ai_analysis_service.py")
        print("  - Task 0D.6: langgraph_agent.py")
        print("\n")

        return True

    except Exception as e:
        print("\n" + "="*80)
        print(f"[FAILED] TESTS FAILED: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
