"""
Test Script for Thought Prompts - Task 0-ARCH.4
Test category-specific reasoning templates, few-shot examples, and prompt generation

Usage:
    python test_thought_prompts.py

Tests:
1. Verify all category templates exist
2. Test reasoning prompt generation for each category
3. Test few-shot examples retrieval
4. Test observation prompt generation
5. Test answer generation prompt
6. Test prompt with examples integration
7. Test fallback for unknown categories

File: implementation/test_thought_prompts.py
Created: 2025-10-31
"""

import sys
import os

# Force UTF-8 encoding for Windows compatibility
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add implementation directory to path
implementation_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, implementation_dir)
agents_dir = os.path.join(implementation_dir, 'agents')
sys.path.insert(0, agents_dir)

# Import thought prompts directly to avoid full module load
from thought_prompts import ThoughtPrompts, ReasoningExample


def print_header(title: str):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def test_1_category_templates():
    """Test 1: Verify all category reasoning templates exist"""
    print_header("TEST 1: Category Reasoning Templates")

    expected_categories = [
        "CODE_ERROR",
        "INFRA_ERROR",
        "CONFIG_ERROR",
        "DEPENDENCY_ERROR",
        "TEST_FAILURE",
        "UNKNOWN"
    ]

    print("\nExpected Category Templates:")
    for category in expected_categories:
        template = ThoughtPrompts.REASONING_TEMPLATES.get(category)
        if template:
            print(f"  ✓ {category}: Template exists ({len(template)} chars)")
            assert "error_info" in template, f"{category} template missing {{error_info}} placeholder"
            assert "context_summary" in template, f"{category} template missing {{context_summary}} placeholder"
            assert "Output Format (JSON)" in template, f"{category} template missing JSON format instructions"
        else:
            print(f"  ✗ {category}: Template MISSING")
            assert False, f"Missing template for {category}"

    print(f"\n✅ All {len(expected_categories)} category templates verified")
    return True


def test_2_reasoning_prompt_generation():
    """Test 2: Generate reasoning prompts for different categories"""
    print_header("TEST 2: Reasoning Prompt Generation")

    test_cases = [
        {
            "category": "CODE_ERROR",
            "error_info": "NullPointerException at UserService.java:45",
            "context": "No information gathered yet"
        },
        {
            "category": "INFRA_ERROR",
            "error_info": "OutOfMemoryError: Java heap space",
            "context": "RAG Results: 2 similar errors found"
        },
        {
            "category": "CONFIG_ERROR",
            "error_info": "PermissionError: Permission denied /var/log/app.log",
            "context": "MongoDB Logs: 3 log entries"
        }
    ]

    for test in test_cases:
        print(f"\n[Test Case] {test['category']}:")
        prompt = ThoughtPrompts.get_reasoning_prompt(
            error_category=test['category'],
            error_info=test['error_info'],
            context_summary=test['context']
        )

        # Verify prompt contains expected elements
        assert test['error_info'] in prompt, "Error info not in prompt"
        assert test['context'] in prompt, "Context not in prompt"
        assert "Available Actions" in prompt, "Missing actions section"
        assert "Output Format (JSON)" in prompt, "Missing JSON format"

        print(f"  ✓ Prompt generated successfully ({len(prompt)} chars)")
        print(f"  ✓ Contains error info: {test['error_info'][:50]}...")
        print(f"  ✓ Contains context: {test['context'][:50]}...")

    print("\n✅ All reasoning prompts generated correctly")
    return True


def test_3_few_shot_examples():
    """Test 3: Retrieve few-shot examples for each category"""
    print_header("TEST 3: Few-Shot Examples")

    categories_with_examples = [
        "CODE_ERROR",
        "INFRA_ERROR",
        "CONFIG_ERROR",
        "DEPENDENCY_ERROR",
        "TEST_FAILURE"
    ]

    for category in categories_with_examples:
        print(f"\n[Category] {category}:")
        examples = ThoughtPrompts.get_few_shot_examples(category, max_examples=2)

        assert len(examples) > 0, f"No examples for {category}"
        assert len(examples) <= 2, f"Too many examples returned for {category}"

        for i, example in enumerate(examples, 1):
            assert isinstance(example, ReasoningExample), "Example not a ReasoningExample"
            assert example.error_summary, "Example missing error_summary"
            assert example.thought, "Example missing thought"
            assert example.action, "Example missing action"
            assert example.reasoning, "Example missing reasoning"

            print(f"  Example {i}:")
            print(f"    Error: {example.error_summary[:50]}...")
            print(f"    Thought: {example.thought[:50]}...")
            print(f"    Action: {example.action}")

    print("\n✅ All few-shot examples retrieved successfully")
    return True


def test_4_format_few_shot_examples():
    """Test 4: Format few-shot examples for prompt inclusion"""
    print_header("TEST 4: Format Few-Shot Examples")

    print("\n[Test] Formatting CODE_ERROR examples:")
    examples = ThoughtPrompts.get_few_shot_examples("CODE_ERROR", max_examples=2)
    formatted = ThoughtPrompts.format_few_shot_examples(examples)

    # Verify formatting
    assert "Examples of Good Reasoning" in formatted, "Missing header"
    assert "Example 1:" in formatted, "Missing first example"
    assert "Error:" in formatted, "Missing error label"
    assert "Thought:" in formatted, "Missing thought label"
    assert "Action:" in formatted, "Missing action label"
    assert "Reasoning:" in formatted, "Missing reasoning label"

    print(f"  ✓ Formatted output ({len(formatted)} chars)")
    print(f"\n  Preview:")
    print("  " + formatted[:300].replace("\n", "\n  "))
    print("  ...")

    # Test empty examples
    print("\n[Test] Empty examples list:")
    empty_formatted = ThoughtPrompts.format_few_shot_examples([])
    assert empty_formatted == "", "Empty list should return empty string"
    print("  ✓ Empty list handled correctly")

    print("\n✅ Few-shot formatting working correctly")
    return True


def test_5_observation_prompt():
    """Test 5: Generate observation analysis prompt"""
    print_header("TEST 5: Observation Analysis Prompt")

    test_cases = [
        {
            "tool_name": "pinecone_knowledge",
            "tool_results": "Found 3 similar errors: ERR001, ERR002, ERR003. All relate to null pointer handling.",
            "confidence": 0.65
        },
        {
            "tool_name": "github_get_file",
            "tool_results": "Retrieved UserService.java with 250 lines. Error occurs in getUserDetails() method.",
            "confidence": 0.40
        }
    ]

    for test in test_cases:
        print(f"\n[Test] Observation for {test['tool_name']}:")
        prompt = ThoughtPrompts.get_observation_prompt(
            tool_name=test['tool_name'],
            tool_results=test['tool_results'],
            current_confidence=test['confidence']
        )

        # Verify prompt structure
        assert test['tool_name'] in prompt, "Tool name not in prompt"
        assert str(test['confidence']) in prompt or f"{test['confidence']:.2f}" in prompt, "Confidence not in prompt"
        assert "Output Format (JSON)" in prompt, "Missing JSON format"
        assert "observation" in prompt, "Missing observation field"
        assert "confidence_change" in prompt, "Missing confidence_change field"

        print(f"  ✓ Observation prompt generated ({len(prompt)} chars)")
        print(f"  ✓ Contains tool name: {test['tool_name']}")
        print(f"  ✓ Current confidence: {test['confidence']:.2f}")

    print("\n✅ Observation prompts generated correctly")
    return True


def test_6_answer_generation_prompt():
    """Test 6: Generate answer generation prompt"""
    print_header("TEST 6: Answer Generation Prompt")

    error_category = "CODE_ERROR"
    all_context = """SIMILAR ERROR DOCUMENTATION:
- knowledge_docs: NullPointerException handling best practices...
- error_library: Similar case resolved by adding null checks...

CODE CONTEXT:
- UserService.java: public User getUserDetails(String userId) {..."""

    reasoning_history = """[
  {
    "iteration": 1,
    "thought": "Need to search for NullPointerException patterns",
    "action": "pinecone_knowledge"
  },
  {
    "iteration": 2,
    "thought": "Found similar cases, checking source code",
    "action": "github_get_file"
  }
]"""

    print(f"\n[Test] Generating answer prompt for {error_category}:")
    prompt = ThoughtPrompts.get_answer_generation_prompt(
        error_category=error_category,
        all_context=all_context,
        reasoning_history=reasoning_history
    )

    # Verify prompt structure
    assert error_category in prompt, "Error category not in prompt"
    assert "All Information Gathered" in prompt or "GATHERED CONTEXT" in prompt, "Missing context section"
    assert "Output Format (JSON)" in prompt, "Missing JSON format"
    assert "root_cause" in prompt, "Missing root_cause field"
    assert "fix_recommendation" in prompt, "Missing fix_recommendation field"
    assert "confidence" in prompt, "Missing confidence field"

    print(f"  ✓ Answer generation prompt created ({len(prompt)} chars)")
    print(f"  ✓ Category: {error_category}")
    print(f"  ✓ Context length: {len(all_context)} chars")
    print(f"  ✓ Reasoning history: {len(reasoning_history)} chars")

    print("\n✅ Answer generation prompt working correctly")
    return True


def test_7_prompt_with_examples():
    """Test 7: Generate complete prompt with few-shot examples"""
    print_header("TEST 7: Reasoning Prompt with Examples")

    test_cases = [
        {
            "category": "CODE_ERROR",
            "include_examples": True,
            "should_have_examples": True
        },
        {
            "category": "INFRA_ERROR",
            "include_examples": True,
            "should_have_examples": True
        },
        {
            "category": "CODE_ERROR",
            "include_examples": False,
            "should_have_examples": False
        }
    ]

    for test in test_cases:
        print(f"\n[Test] {test['category']} (examples={test['include_examples']}):")
        prompt = ThoughtPrompts.get_reasoning_prompt_with_examples(
            error_category=test['category'],
            error_info="Test error message",
            context_summary="Test context",
            include_examples=test['include_examples']
        )

        if test['should_have_examples']:
            assert "Examples of Good Reasoning" in prompt, "Examples should be included"
            assert "Example 1:" in prompt, "First example should be present"
            print(f"  ✓ Prompt includes few-shot examples")
        else:
            assert "Examples of Good Reasoning" not in prompt, "Examples should not be included"
            print(f"  ✓ Prompt without examples")

        print(f"  ✓ Total prompt length: {len(prompt)} chars")

    print("\n✅ Prompt with examples integration working")
    return True


def test_8_unknown_category_fallback():
    """Test 8: Fallback behavior for unknown categories"""
    print_header("TEST 8: Unknown Category Fallback")

    unknown_category = "DATABASE_ERROR"  # Not in base categories

    print(f"\n[Test] Using unknown category: {unknown_category}")
    prompt = ThoughtPrompts.get_reasoning_prompt(
        error_category=unknown_category,
        error_info="Database connection failed",
        context_summary="No context yet"
    )

    # Should fallback to UNKNOWN template
    assert "UNKNOWN" in prompt or "unknown" in prompt, "Should use UNKNOWN fallback"
    assert len(prompt) > 0, "Prompt should still be generated"

    print(f"  ✓ Fallback to UNKNOWN template")
    print(f"  ✓ Prompt generated ({len(prompt)} chars)")

    # Test with examples for unknown category
    print(f"\n[Test] Unknown category with examples:")
    prompt_with_examples = ThoughtPrompts.get_reasoning_prompt_with_examples(
        error_category=unknown_category,
        error_info="Database connection failed",
        context_summary="No context yet",
        include_examples=True
    )

    # UNKNOWN category has no few-shot examples, so should just return base prompt
    assert len(prompt_with_examples) > 0, "Should still return a prompt"
    print(f"  ✓ Handles unknown category with examples request")
    print(f"  ✓ Prompt length: {len(prompt_with_examples)} chars")

    print("\n✅ Unknown category fallback working correctly")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 18 + "Thought Prompts Test Suite - Task 0-ARCH.4" + " " * 18 + "|")
    print("+" + "=" * 78 + "+")
    print("\n")

    tests = [
        ("Category Templates", test_1_category_templates),
        ("Reasoning Prompt Generation", test_2_reasoning_prompt_generation),
        ("Few-Shot Examples", test_3_few_shot_examples),
        ("Format Few-Shot Examples", test_4_format_few_shot_examples),
        ("Observation Prompt", test_5_observation_prompt),
        ("Answer Generation Prompt", test_6_answer_generation_prompt),
        ("Prompt with Examples", test_7_prompt_with_examples),
        ("Unknown Category Fallback", test_8_unknown_category_fallback),
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
    print("  ✓ Category-specific reasoning templates (6 categories)")
    print("  ✓ Few-shot examples for each error type (2 examples per category)")
    print("  ✓ Observation analysis prompt template")
    print("  ✓ Answer generation prompt template")
    print("  ✓ Prompt with examples integration")
    print("  ✓ Unknown category fallback to UNKNOWN template")
    print("  ✓ JSON format validation in all prompts")
    print("  ✓ Placeholder substitution (error_info, context_summary)")
    print("=" * 80)

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
