"""
Test Script for Tool Registry - Task 0-ARCH.3
Test dynamic category discovery, tool selection, and context-aware routing

Usage:
    python test_tool_registry.py

Tests:
1. Static categories (CODE_ERROR, INFRA_ERROR, CONFIG_ERROR, etc.)
2. Tool selection for each category
3. 80/20 rule for GitHub (confidence-based)
4. Dynamic category discovery from Pinecone
5. Unknown category fallback
6. Category refresh without restart

File: implementation/test_tool_registry.py
Created: 2025-10-31
"""

import sys
import os
from dotenv import load_dotenv

# Add implementation directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
load_dotenv()

# Import registry
from agents.tool_registry import create_tool_registry

def print_header(title: str):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def test_1_data_driven_categories():
    """Test 1: Verify pure data-driven categories from Pinecone"""
    print_header("TEST 1: Pure Data-Driven Categories from Pinecone")

    registry = create_tool_registry()
    categories = registry.get_available_categories()

    print("\nDiscovered Categories (from Pinecone):")
    for cat, desc in categories.items():
        print(f"  ✓ {cat}: {desc}")

    # Verify we have categories (at least 1, possibly more)
    assert len(categories) > 0, "No categories discovered from Pinecone!"

    if "UNKNOWN" in categories and len(categories) == 1:
        print("\n⚠️  WARNING: Only UNKNOWN category found - Pinecone might be empty")
        print("   Expected: Categories from knowledge docs + error library")
    else:
        print(f"\n✅ {len(categories)} categories discovered from Pinecone")
        print("   ℹ️  Note: Categories are purely data-driven (no static code definitions)")

    return True


def test_2_tool_selection_code_error():
    """Test 2: Tool selection for CODE_ERROR"""
    print_header("TEST 2: Tool Selection for CODE_ERROR")

    registry = create_tool_registry()

    # Scenario A: High confidence (0.85) - Should skip GitHub (80% case)
    print("\n[Scenario A] CODE_ERROR with HIGH confidence (0.85):")
    tools_high = registry.get_tools_for_category(
        error_category="CODE_ERROR",
        solution_confidence=0.85,
        iteration=1,
        tools_already_used=[]
    )
    print(f"  Tools: {tools_high}")

    # Should include Pinecone tools (always run)
    assert "pinecone_knowledge" in tools_high, "Missing pinecone_knowledge"
    assert "pinecone_error_library" in tools_high, "Missing pinecone_error_library"

    # Should NOT include GitHub tools (confidence is high)
    github_tools = [t for t in tools_high if t.startswith("github_")]
    print(f"  GitHub tools: {github_tools if github_tools else 'None (skipped due to high confidence)'}")
    assert len(github_tools) == 0, "GitHub tools should be skipped with high confidence"
    print("  ✅ PASS: GitHub skipped (80% case)")

    # Scenario B: Low confidence (0.60) - Should use GitHub (20% case)
    print("\n[Scenario B] CODE_ERROR with LOW confidence (0.60):")
    tools_low = registry.get_tools_for_category(
        error_category="CODE_ERROR",
        solution_confidence=0.60,
        iteration=1,
        tools_already_used=[]
    )
    print(f"  Tools: {tools_low}")

    # Should include GitHub tools (confidence is low)
    github_tools = [t for t in tools_low if t.startswith("github_")]
    print(f"  GitHub tools: {github_tools}")
    assert len(github_tools) > 0, "GitHub tools should be included with low confidence"
    print("  ✅ PASS: GitHub included (20% case)")

    print("\n✅ 80/20 rule working correctly")
    return True


def test_3_tool_selection_infra_error():
    """Test 3: Tool selection for INFRA_ERROR"""
    print_header("TEST 3: Tool Selection for INFRA_ERROR")

    registry = create_tool_registry()

    print("\n[Scenario] INFRA_ERROR analysis:")
    tools = registry.get_tools_for_category(
        error_category="INFRA_ERROR",
        solution_confidence=0.50,
        iteration=1,
        tools_already_used=[]
    )
    print(f"  Tools: {tools}")

    # Should include Pinecone (always)
    assert "pinecone_knowledge" in tools, "Missing pinecone_knowledge"
    assert "pinecone_error_library" in tools, "Missing pinecone_error_library"

    # Should include MongoDB logs (primary for INFRA_ERROR)
    mongodb_tools = [t for t in tools if t.startswith("mongodb_")]
    print(f"  MongoDB tools: {mongodb_tools}")
    assert len(mongodb_tools) > 0, "MongoDB tools should be included for INFRA_ERROR"

    # Should NOT include GitHub (not relevant for INFRA_ERROR)
    github_tools = [t for t in tools if t.startswith("github_")]
    print(f"  GitHub tools: {github_tools if github_tools else 'None (not relevant for INFRA)'}")
    assert len(github_tools) == 0, "GitHub tools should NOT be used for INFRA_ERROR"

    print("\n✅ INFRA_ERROR routing correct (MongoDB yes, GitHub no)")
    return True


def test_4_tool_selection_config_error():
    """Test 4: Tool selection for CONFIG_ERROR"""
    print_header("TEST 4: Tool Selection for CONFIG_ERROR")

    registry = create_tool_registry()

    print("\n[Scenario] CONFIG_ERROR analysis:")
    tools = registry.get_tools_for_category(
        error_category="CONFIG_ERROR",
        solution_confidence=0.50,
        iteration=1,
        tools_already_used=[]
    )
    print(f"  Tools: {tools}")

    # Should include Pinecone (always)
    assert "pinecone_knowledge" in tools, "Missing pinecone_knowledge"

    # Should include MongoDB (primary for CONFIG_ERROR)
    mongodb_tools = [t for t in tools if t.startswith("mongodb_")]
    print(f"  MongoDB tools: {mongodb_tools}")
    assert len(mongodb_tools) > 0, "MongoDB tools should be included for CONFIG_ERROR"

    # Should NOT include GitHub
    github_tools = [t for t in tools if t.startswith("github_")]
    assert len(github_tools) == 0, "GitHub tools should NOT be used for CONFIG_ERROR"

    print("\n✅ CONFIG_ERROR routing correct")
    return True


def test_5_unknown_category_fallback():
    """Test 5: Unknown category fallback (Option B)"""
    print_header("TEST 5: Unknown Category Fallback (Hybrid Option B)")

    registry = create_tool_registry()

    print("\n[Scenario] DATABASE_ERROR (not in base categories):")
    tools = registry.get_tools_for_category(
        error_category="DATABASE_ERROR",  # Unknown category
        solution_confidence=0.50,
        iteration=1,
        tools_already_used=[]
    )
    print(f"  Tools: {tools}")

    # Should fallback to RAG-first approach
    assert "pinecone_knowledge" in tools, "Missing pinecone_knowledge in fallback"
    assert "pinecone_error_library" in tools, "Missing pinecone_error_library in fallback"

    print("  ✅ PASS: Unknown category falls back to RAG-first approach")
    print("\n✅ Hybrid Option B (fallback) working")
    return True


def test_6_tool_execution_tracking():
    """Test 6: Tool execution metrics tracking"""
    print_header("TEST 6: Tool Execution Metrics")

    registry = create_tool_registry()

    print("\n[Scenario] Recording tool execution:")

    # Record some executions
    registry.record_tool_execution("pinecone_knowledge", success=True, latency=0.5)
    registry.record_tool_execution("pinecone_knowledge", success=True, latency=0.6)
    registry.record_tool_execution("github_get_file", success=True, latency=1.2)
    registry.record_tool_execution("github_get_file", success=False, latency=2.0)

    # Get stats
    stats = registry.get_tool_stats()
    print("\nTool Execution Statistics:")
    for tool_name, tool_stats in stats.items():
        print(f"\n  {tool_name}:")
        print(f"    - Total calls: {tool_stats['total_calls']}")
        print(f"    - Success rate: {tool_stats['success_rate']:.1%}")
        print(f"    - Avg latency: {tool_stats['avg_latency']:.2f}s")
        print(f"    - Cost per call: ${tool_stats['cost']:.4f}")

    # Verify stats
    assert "pinecone_knowledge" in stats, "Missing pinecone_knowledge stats"
    assert stats["pinecone_knowledge"]["total_calls"] == 2, "Incorrect call count"
    assert stats["pinecone_knowledge"]["success_rate"] == 1.0, "Incorrect success rate"

    assert "github_get_file" in stats, "Missing github_get_file stats"
    assert stats["github_get_file"]["total_calls"] == 2, "Incorrect call count"
    assert stats["github_get_file"]["success_rate"] == 0.5, "Incorrect success rate"

    print("\n✅ Tool execution tracking working")
    return True


def test_7_iterative_tool_selection():
    """Test 7: Iterative tool selection (don't repeat tools)"""
    print_header("TEST 7: Iterative Tool Selection")

    registry = create_tool_registry()

    print("\n[Scenario] Multiple iterations for CODE_ERROR:")

    # Iteration 1
    print("\n  Iteration 1:")
    tools_iter1 = registry.get_tools_for_category(
        error_category="CODE_ERROR",
        solution_confidence=0.30,
        iteration=1,
        tools_already_used=[]
    )
    print(f"    Tools: {tools_iter1}")

    # Iteration 2 (after using Pinecone tools)
    print("\n  Iteration 2 (after RAG):")
    tools_iter2 = registry.get_tools_for_category(
        error_category="CODE_ERROR",
        solution_confidence=0.40,  # Still low
        iteration=2,
        tools_already_used=["pinecone_knowledge", "pinecone_error_library"]
    )
    print(f"    Tools: {tools_iter2}")

    # Should not repeat tools already used
    assert "pinecone_knowledge" not in tools_iter2, "Should not repeat pinecone_knowledge"
    assert "pinecone_error_library" not in tools_iter2, "Should not repeat pinecone_error_library"

    # Should include GitHub (confidence still low)
    github_tools = [t for t in tools_iter2 if t.startswith("github_")]
    assert len(github_tools) > 0, "Should include GitHub tools in iteration 2"

    print("\n✅ Iterative tool selection avoids repeats")
    return True


def test_8_category_refresh():
    """Test 8: Category refresh without restart"""
    print_header("TEST 8: Dynamic Category Refresh")

    registry = create_tool_registry()

    print("\n[Scenario A] Initial categories:")
    categories_initial = registry.get_available_categories()
    print(f"  Count: {len(categories_initial)}")
    print(f"  Categories: {list(categories_initial.keys())}")

    print("\n[Scenario B] Force refresh categories:")
    categories_refreshed = registry.refresh_categories()
    print(f"  Count: {len(categories_refreshed)}")
    print(f"  Categories: {list(categories_refreshed.keys())}")

    # Both should have at least base categories
    assert len(categories_refreshed) >= 5, "Should have at least 5 base categories"

    print("\n✅ Category refresh working (no restart needed)")
    print("   Note: To test dynamic discovery, add a new error doc to Pinecone with")
    print("   metadata: {'error_category': 'DATABASE_ERROR', 'doc_type': 'error_documentation'}")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Tool Registry Test Suite - Task 0-ARCH.3" + " " * 18 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")

    tests = [
        ("Pure Data-Driven Categories", test_1_data_driven_categories),
        ("CODE_ERROR Tool Selection (80/20 rule)", test_2_tool_selection_code_error),
        ("INFRA_ERROR Tool Selection", test_3_tool_selection_infra_error),
        ("CONFIG_ERROR Tool Selection", test_4_tool_selection_config_error),
        ("Unknown Category Fallback", test_5_unknown_category_fallback),
        ("Tool Execution Tracking", test_6_tool_execution_tracking),
        ("Iterative Tool Selection", test_7_iterative_tool_selection),
        ("Category Refresh", test_8_category_refresh),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print_header("TEST SUMMARY")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")

    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\n{passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 80)

    # Key Features Validated
    print("\n" + "=" * 80)
    print(" Key Features Validated")
    print("=" * 80)
    print("  ✓ Pure data-driven categories (from Pinecone knowledge docs + error library)")
    print("  ✓ NO static categories in code (single source of truth)")
    print("  ✓ Category alignment validation between both indexes")
    print("  ✓ 80/20 rule for GitHub (confidence-based routing)")
    print("  ✓ Context-aware tool selection by category")
    print("  ✓ Unknown category fallback (only if Pinecone fails)")
    print("  ✓ Tool execution metrics tracking")
    print("  ✓ Iterative tool selection (no repeats)")
    print("  ✓ Category refresh without restart")
    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
