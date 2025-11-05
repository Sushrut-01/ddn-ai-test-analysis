"""
Test Suite for RAG Router Module - Task 0D.3
Created: 2025-11-02

Tests:
1. Routing decisions for all error categories
2. OPTION C validation (CODE_ERROR only uses Gemini)
3. Helper methods (should_use_gemini, should_use_github, get_rag_tools)
4. Statistics tracking
5. Edge cases (invalid categories, fallback to UNKNOWN_ERROR)
6. Routing rule validation
7. Integration scenarios
"""

import sys
import os

# Add implementation directory to path
sys.path.insert(0, os.path.dirname(__file__))

from rag_router import (
    RAGRouter,
    RoutingDecision,
    ErrorCategory,
    create_rag_router
)


def test_router_initialization():
    """Test 1: Router initialization"""
    print("\n" + "="*80)
    print("TEST 1: Router Initialization")
    print("="*80)

    router = create_rag_router()

    # Check initialization
    assert router is not None, "Router should be initialized"
    assert hasattr(router, 'ROUTING_RULES'), "Router should have ROUTING_RULES"
    assert hasattr(router, '_routing_stats'), "Router should have _routing_stats"

    # Check all categories have routing rules
    for category in ErrorCategory:
        assert category in router.ROUTING_RULES, f"Missing rule for {category.value}"

    print(f"[PASS] Router initialized successfully")
    print(f"  Categories: {len(router.ROUTING_RULES)}")
    print(f"  Statistics tracking: enabled")


def test_code_error_routing():
    """Test 2: CODE_ERROR routing (OPTION C - should use Gemini+GitHub)"""
    print("\n" + "="*80)
    print("TEST 2: CODE_ERROR Routing (OPTION C)")
    print("="*80)

    router = create_rag_router()
    decision = router.route_error("CODE_ERROR")

    # Assertions for CODE_ERROR (OPTION C)
    assert decision.error_category == "CODE_ERROR", "Should be CODE_ERROR"
    assert decision.should_use_gemini == True, "CODE_ERROR should use Gemini (OPTION C)"
    assert decision.should_use_github == True, "CODE_ERROR should use GitHub"
    assert decision.should_use_rag == True, "CODE_ERROR should use RAG"
    assert len(decision.rag_tools) > 0, "CODE_ERROR should have RAG tools"
    assert "pinecone_knowledge" in decision.rag_tools, "Should include pinecone_knowledge"
    assert "pinecone_error_library" in decision.rag_tools, "Should include pinecone_error_library"
    assert decision.routing_option == "OPTION_C", "Should be OPTION_C"

    print(f"[PASS] CODE_ERROR routing correct:")
    print(f"  Gemini: {decision.should_use_gemini}")
    print(f"  GitHub: {decision.should_use_github}")
    print(f"  RAG: {decision.should_use_rag}")
    print(f"  Tools: {decision.rag_tools}")


def test_infra_error_routing():
    """Test 3: INFRA_ERROR routing (OPTION C - should NOT use Gemini)"""
    print("\n" + "="*80)
    print("TEST 3: INFRA_ERROR Routing (OPTION C)")
    print("="*80)

    router = create_rag_router()
    decision = router.route_error("INFRA_ERROR")

    # Assertions for INFRA_ERROR (OPTION C)
    assert decision.error_category == "INFRA_ERROR", "Should be INFRA_ERROR"
    assert decision.should_use_gemini == False, "INFRA_ERROR should NOT use Gemini (OPTION C)"
    assert decision.should_use_github == False, "INFRA_ERROR should NOT use GitHub"
    assert decision.should_use_rag == True, "INFRA_ERROR should use RAG"
    assert len(decision.rag_tools) > 0, "INFRA_ERROR should have RAG tools"

    print(f"[PASS] INFRA_ERROR routing correct:")
    print(f"  Gemini: {decision.should_use_gemini}")
    print(f"  GitHub: {decision.should_use_github}")
    print(f"  RAG: {decision.should_use_rag}")
    print(f"  Tools: {decision.rag_tools}")


def test_all_categories_routing():
    """Test 4: All categories routing (OPTION C compliance)"""
    print("\n" + "="*80)
    print("TEST 4: All Categories Routing (OPTION C Compliance)")
    print("="*80)

    router = create_rag_router()

    categories = [
        "CODE_ERROR",
        "INFRA_ERROR",
        "CONFIG_ERROR",
        "DEPENDENCY_ERROR",
        "TEST_ERROR",
        "UNKNOWN_ERROR"
    ]

    gemini_count = 0
    github_count = 0
    rag_count = 0

    print("\nRouting decisions:")
    for category in categories:
        decision = router.route_error(category)

        print(f"\n{category}:")
        print(f"  Gemini: {decision.should_use_gemini}")
        print(f"  GitHub: {decision.should_use_github}")
        print(f"  RAG: {decision.should_use_rag}")

        # Count usage
        if decision.should_use_gemini:
            gemini_count += 1
        if decision.should_use_github:
            github_count += 1
        if decision.should_use_rag:
            rag_count += 1

        # All should have RAG
        assert decision.should_use_rag == True, f"{category} should use RAG"

    # OPTION C validation: Only CODE_ERROR uses Gemini
    print(f"\n[PASS] OPTION C Compliance:")
    print(f"  Gemini used: {gemini_count}/6 categories (should be 1)")
    print(f"  GitHub used: {github_count}/6 categories (should be 1)")
    print(f"  RAG used: {rag_count}/6 categories (should be 6)")

    assert gemini_count == 1, "Only CODE_ERROR should use Gemini (OPTION C)"
    assert github_count == 1, "Only CODE_ERROR should use GitHub"
    assert rag_count == 6, "All categories should use RAG"


def test_helper_methods():
    """Test 5: Helper methods (should_use_gemini, should_use_github, get_rag_tools)"""
    print("\n" + "="*80)
    print("TEST 5: Helper Methods")
    print("="*80)

    router = create_rag_router()

    # Test should_use_gemini
    print("\nshould_use_gemini():")
    assert router.should_use_gemini("CODE_ERROR") == True, "CODE_ERROR should use Gemini"
    assert router.should_use_gemini("INFRA_ERROR") == False, "INFRA_ERROR should not use Gemini"
    assert router.should_use_gemini("CONFIG_ERROR") == False, "CONFIG_ERROR should not use Gemini"
    print("  [PASS] CODE_ERROR: True, Others: False")

    # Test should_use_github
    print("\nshould_use_github():")
    assert router.should_use_github("CODE_ERROR") == True, "CODE_ERROR should use GitHub"
    assert router.should_use_github("INFRA_ERROR") == False, "INFRA_ERROR should not use GitHub"
    print("  [PASS] CODE_ERROR: True, Others: False")

    # Test get_rag_tools
    print("\nget_rag_tools():")
    code_tools = router.get_rag_tools("CODE_ERROR")
    assert len(code_tools) > 0, "CODE_ERROR should have RAG tools"
    assert "pinecone_knowledge" in code_tools, "Should include pinecone_knowledge"
    print(f"  [PASS] CODE_ERROR tools: {code_tools}")

    infra_tools = router.get_rag_tools("INFRA_ERROR")
    assert len(infra_tools) > 0, "INFRA_ERROR should have RAG tools"
    print(f"  [PASS] INFRA_ERROR tools: {infra_tools}")

    # Test get_routing_reason
    print("\nget_routing_reason():")
    code_reason = router.get_routing_reason("CODE_ERROR")
    assert len(code_reason) > 0, "Should have routing reason"
    print(f"  [PASS] CODE_ERROR reason: {code_reason[:60]}...")


def test_statistics_tracking():
    """Test 6: Statistics tracking"""
    print("\n" + "="*80)
    print("TEST 6: Statistics Tracking")
    print("="*80)

    router = create_rag_router()

    # Initial stats
    stats = router.get_routing_stats()
    assert stats['total_routes'] == 0, "Should start with 0 routes"

    # Route some errors
    router.route_error("CODE_ERROR")
    router.route_error("INFRA_ERROR")
    router.route_error("CONFIG_ERROR")
    router.route_error("CODE_ERROR")  # Second CODE_ERROR

    # Check stats
    stats = router.get_routing_stats()
    print(f"\nStatistics after 4 routes:")
    print(f"  Total routes: {stats['total_routes']}")
    print(f"  Gemini routes: {stats['gemini_routes']}")
    print(f"  GitHub routes: {stats['github_routes']}")
    print(f"  RAG-only routes: {stats['rag_only_routes']}")

    assert stats['total_routes'] == 4, "Should have 4 total routes"
    assert stats['gemini_routes'] == 2, "Should have 2 Gemini routes (2x CODE_ERROR)"
    assert stats['github_routes'] == 2, "Should have 2 GitHub routes (2x CODE_ERROR)"
    assert stats['rag_only_routes'] == 2, "Should have 2 RAG-only routes (INFRA+CONFIG)"

    # Check percentages
    assert stats['gemini_percentage'] == 50.0, "Should be 50% Gemini (2/4)"
    assert stats['rag_only_percentage'] == 50.0, "Should be 50% RAG-only (2/4)"

    print(f"  Gemini percentage: {stats['gemini_percentage']:.1f}%")
    print(f"  RAG-only percentage: {stats['rag_only_percentage']:.1f}%")

    # Check by-category stats
    print(f"\nBy category:")
    for cat, count in stats['by_category'].items():
        if count > 0:
            print(f"  {cat}: {count}")

    assert stats['by_category']['CODE_ERROR'] == 2, "Should have 2 CODE_ERROR routes"
    assert stats['by_category']['INFRA_ERROR'] == 1, "Should have 1 INFRA_ERROR route"
    assert stats['by_category']['CONFIG_ERROR'] == 1, "Should have 1 CONFIG_ERROR route"

    # Test reset
    router.reset_stats()
    stats = router.get_routing_stats()
    assert stats['total_routes'] == 0, "Stats should be reset to 0"
    print(f"\n[PASS] Statistics reset successfully")


def test_edge_cases():
    """Test 7: Edge cases (invalid categories, case insensitivity)"""
    print("\n" + "="*80)
    print("TEST 7: Edge Cases")
    print("="*80)

    router = create_rag_router()

    # Test invalid category (should fallback to UNKNOWN_ERROR)
    print("\nInvalid category:")
    decision = router.route_error("INVALID_CATEGORY")
    assert decision.error_category == "UNKNOWN_ERROR", "Should fallback to UNKNOWN_ERROR"
    assert decision.should_use_gemini == False, "UNKNOWN_ERROR should not use Gemini"
    print(f"  [PASS] 'INVALID_CATEGORY' -> {decision.error_category}")

    # Test case insensitivity
    print("\nCase insensitivity:")
    decision_lower = router.route_error("code_error")
    decision_upper = router.route_error("CODE_ERROR")
    assert decision_lower.error_category == decision_upper.error_category, "Should be case-insensitive"
    print(f"  [PASS] 'code_error' == 'CODE_ERROR'")

    # Test empty string (should fallback to UNKNOWN_ERROR)
    print("\nEmpty category:")
    decision = router.route_error("")
    assert decision.error_category == "UNKNOWN_ERROR", "Empty should fallback to UNKNOWN_ERROR"
    print(f"  [PASS] '' -> {decision.error_category}")

    # Test None handling via should_use_gemini
    print("\nNone/empty handling in helper methods:")
    assert router.should_use_gemini("") == False, "Empty should return False"
    assert router.should_use_gemini("invalid") == False, "Invalid should return False"
    print(f"  [PASS] Empty/invalid categories handled gracefully")


def test_routing_rule_validation():
    """Test 8: Routing rule validation"""
    print("\n" + "="*80)
    print("TEST 8: Routing Rule Validation")
    print("="*80)

    router = create_rag_router()

    # Validate routing rules
    validation = router.validate_routing_rules()

    print(f"\nValidation result:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Rule count: {validation['rule_count']}")
    print(f"  Errors: {len(validation['errors'])}")
    print(f"  Warnings: {len(validation['warnings'])}")

    if validation['errors']:
        print(f"\nErrors:")
        for error in validation['errors']:
            print(f"  - {error}")

    if validation['warnings']:
        print(f"\nWarnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    assert validation['valid'] == True, "Routing rules should be valid"
    assert validation['rule_count'] == 6, "Should have 6 routing rules"
    assert len(validation['errors']) == 0, "Should have no errors"

    print(f"\n[PASS] All routing rules valid (OPTION C compliant)")


def test_routing_decision_to_dict():
    """Test 9: RoutingDecision to_dict() serialization"""
    print("\n" + "="*80)
    print("TEST 9: RoutingDecision Serialization")
    print("="*80)

    router = create_rag_router()
    decision = router.route_error("CODE_ERROR")

    # Convert to dict
    decision_dict = decision.to_dict()

    print(f"\nSerialized decision:")
    print(f"  error_category: {decision_dict['error_category']}")
    print(f"  should_use_gemini: {decision_dict['should_use_gemini']}")
    print(f"  should_use_github: {decision_dict['should_use_github']}")
    print(f"  should_use_rag: {decision_dict['should_use_rag']}")
    print(f"  rag_tools: {decision_dict['rag_tools']}")
    print(f"  routing_option: {decision_dict['routing_option']}")

    # Assertions
    assert isinstance(decision_dict, dict), "Should be a dictionary"
    assert decision_dict['error_category'] == "CODE_ERROR", "Should have error_category"
    assert 'should_use_gemini' in decision_dict, "Should have should_use_gemini"
    assert 'rag_tools' in decision_dict, "Should have rag_tools"
    assert decision_dict['routing_option'] == "OPTION_C", "Should have routing_option"

    print(f"\n[PASS] RoutingDecision serialization working")


def test_integration_scenario():
    """Test 10: Integration scenario (typical usage flow)"""
    print("\n" + "="*80)
    print("TEST 10: Integration Scenario")
    print("="*80)

    router = create_rag_router()

    print("\nScenario: Processing batch of errors")

    # Simulate processing errors
    errors = [
        ("build-1", "CODE_ERROR", "NullPointerException at line 45"),
        ("build-2", "INFRA_ERROR", "OutOfMemoryError: heap space"),
        ("build-3", "CONFIG_ERROR", "Invalid database URL"),
        ("build-4", "CODE_ERROR", "TypeError: undefined variable"),
        ("build-5", "DEPENDENCY_ERROR", "ModuleNotFoundError: requests")
    ]

    results = []

    for build_id, category, message in errors:
        decision = router.route_error(category)

        result = {
            "build_id": build_id,
            "category": category,
            "gemini_used": decision.should_use_gemini,
            "github_used": decision.should_use_github,
            "rag_used": decision.should_use_rag
        }

        results.append(result)

        print(f"\n{build_id} ({category}):")
        print(f"  Gemini: {'YES' if decision.should_use_gemini else 'NO'}")
        print(f"  GitHub: {'YES' if decision.should_use_github else 'NO'}")
        print(f"  RAG: {'YES' if decision.should_use_rag else 'NO'}")

    # Verify only CODE_ERROR used Gemini
    gemini_builds = [r['build_id'] for r in results if r['gemini_used']]
    print(f"\n[PASS] Gemini used for: {gemini_builds} (CODE_ERROR builds only)")

    assert len(gemini_builds) == 2, "Only 2 CODE_ERROR builds should use Gemini"
    assert all(r['rag_used'] for r in results), "All builds should use RAG"

    # Show final stats
    stats = router.get_routing_stats()
    print(f"\nFinal statistics:")
    print(f"  Total: {stats['total_routes']}")
    print(f"  Gemini: {stats['gemini_routes']} ({stats['gemini_percentage']:.0f}%)")
    print(f"  RAG-only: {stats['rag_only_routes']} ({stats['rag_only_percentage']:.0f}%)")


def test_all_categories_list():
    """Test 11: Get all categories"""
    print("\n" + "="*80)
    print("TEST 11: Get All Categories")
    print("="*80)

    router = create_rag_router()
    categories = router.get_all_categories()

    print(f"\nAvailable categories: {len(categories)}")
    for cat in categories:
        print(f"  - {cat}")

    assert len(categories) == 6, "Should have 6 categories"
    assert "CODE_ERROR" in categories, "Should include CODE_ERROR"
    assert "INFRA_ERROR" in categories, "Should include INFRA_ERROR"
    assert "CONFIG_ERROR" in categories, "Should include CONFIG_ERROR"
    assert "DEPENDENCY_ERROR" in categories, "Should include DEPENDENCY_ERROR"
    assert "TEST_ERROR" in categories, "Should include TEST_ERROR"
    assert "UNKNOWN_ERROR" in categories, "Should include UNKNOWN_ERROR"

    print(f"\n[PASS] All categories available")


def run_all_tests():
    """Run all test suites"""
    print("="*80)
    print("RAG ROUTER - COMPREHENSIVE TEST SUITE")
    print("Task 0D.3 - Created 2025-11-02")
    print("="*80)

    try:
        test_router_initialization()
        test_code_error_routing()
        test_infra_error_routing()
        test_all_categories_routing()
        test_helper_methods()
        test_statistics_tracking()
        test_edge_cases()
        test_routing_rule_validation()
        test_routing_decision_to_dict()
        test_integration_scenario()
        test_all_categories_list()

        print("\n" + "="*80)
        print("[SUCCESS] ALL TESTS PASSED")
        print("="*80)
        print("\nRAG Router is ready for integration with:")
        print("  - Task 0D.5: ai_analysis_service.py (BUG FIX - Gemini only for CODE_ERROR)")
        print("  - Task 0D.6: langgraph_agent.py (routing integration)")
        print("  - OPTION C routing: CODE_ERROR -> Gemini+GitHub, Others -> RAG only")
        print("\n")

        return True

    except AssertionError as e:
        print("\n" + "="*80)
        print(f"[FAILED] TEST FAILED: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return False

    except Exception as e:
        print("\n" + "="*80)
        print(f"[ERROR] UNEXPECTED ERROR: {str(e)}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
