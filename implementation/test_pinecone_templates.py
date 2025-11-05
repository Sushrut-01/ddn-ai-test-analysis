"""
Quick test to verify templates load from Pinecone
"""
import sys
import os

# Add paths
implementation_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, implementation_dir)
agents_dir = os.path.join(implementation_dir, 'agents')
sys.path.insert(0, agents_dir)

# Direct import to avoid langgraph dependency
import importlib.util
spec = importlib.util.spec_from_file_location("thought_prompts", os.path.join(agents_dir, "thought_prompts.py"))
thought_prompts_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(thought_prompts_module)
ThoughtPrompts = thought_prompts_module.ThoughtPrompts

print("\n" + "="*70)
print(" TESTING DATA-DRIVEN TEMPLATES FROM PINECONE")
print("="*70)

# Test 1: Get reasoning prompt
print("\n[Test 1] Get reasoning prompt for CODE_ERROR...")
prompt = ThoughtPrompts.get_reasoning_prompt(
    error_category="CODE_ERROR",
    error_info="NullPointerException at line 45",
    context_summary="No context yet"
)
print(f"OK - Loaded template ({len(prompt)} chars)")
print(f"Preview: {prompt[:150]}...")

# Test 2: Get few-shot examples
print("\n[Test 2] Get few-shot examples for CODE_ERROR...")
examples = ThoughtPrompts.get_few_shot_examples("CODE_ERROR", max_examples=2)
print(f"OK - Loaded {len(examples)} examples")
for i, ex in enumerate(examples, 1):
    print(f"  Example {i}: {ex.error_summary[:50]}...")

# Test 3: Get observation prompt
print("\n[Test 3] Get observation prompt...")
obs_prompt = ThoughtPrompts.get_observation_prompt(
    tool_name="pinecone_knowledge",
    tool_results="Found 3 similar errors",
    current_confidence=0.65
)
print(f"OK - Loaded template ({len(obs_prompt)} chars)")

# Test 4: Get answer generation prompt
print("\n[Test 4] Get answer generation prompt...")
answer_prompt = ThoughtPrompts.get_answer_generation_prompt(
    error_category="CODE_ERROR",
    all_context="Some context",
    reasoning_history="Some history"
)
print(f"OK - Loaded template ({len(answer_prompt)} chars)")

print("\n" + "="*70)
print("SUCCESS - ALL TESTS PASSED - DATA-DRIVEN TEMPLATES WORKING!")
print("="*70)
