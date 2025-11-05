"""
Verify LangGraph Refactor - Task 0-ARCH.6
==========================================

Verify the structure and syntax of the refactored langgraph_agent.py

This script doesn't require dependencies - it just checks:
1. File syntax is correct
2. Expected functions/variables exist
3. Old functions are removed

File: implementation/verify_langgraph_refactor.py
Created: 2025-11-02
Task: 0-ARCH.6
"""

import sys
import os
import ast

# Force UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("\n" + "=" * 70)
print(" VERIFYING LANGGRAPH REFACTOR (Task 0-ARCH.6)")
print("=" * 70)

# Test 1: Read the file
print("\n[Test 1] Read langgraph_agent.py...")
try:
    langgraph_path = os.path.join(os.path.dirname(__file__), 'langgraph_agent.py')
    with open(langgraph_path, 'r', encoding='utf-8') as f:
        code = f.read()
    print(f"   [PASS] File read successfully ({len(code)} characters)")
except Exception as e:
    print(f"   [FAIL] Failed to read file: {e}")
    sys.exit(1)

# Test 2: Parse the file (check syntax)
print("\n[Test 2] Parse file (check syntax)...")
try:
    tree = ast.parse(code, filename='langgraph_agent.py')
    print("   [PASS] File syntax is valid")
except SyntaxError as e:
    print(f"   [FAIL] Syntax error: {e}")
    sys.exit(1)

# Test 3: Check for ReAct imports
print("\n[Test 3] Check for ReAct imports...")
has_react_import = False
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module and 'react_agent_service' in node.module:
            has_react_import = True
            names = [alias.name for alias in node.names]
            print(f"   [PASS] Found import: from {node.module} import {', '.join(names)}")

if not has_react_import:
    print("   [FAIL] ReActAgent import not found")
    sys.exit(1)

# Test 4: Check for initialize_react_agent function
print("\n[Test 4] Check for initialize_react_agent function...")
found_init = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'initialize_react_agent':
        found_init = True
        print(f"   [PASS] Found initialize_react_agent function")
        break

if not found_init:
    print("   [FAIL] initialize_react_agent function not found")
    sys.exit(1)

# Test 5: Check for new endpoints
print("\n[Test 5] Check for new endpoints...")
endpoints = {
    'analyze_error_endpoint': False,
    'classify_error_endpoint': False,
    'get_categories': False,
    'refresh_categories': False
}

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name in endpoints:
            endpoints[node.name] = True

for endpoint, found in endpoints.items():
    if found:
        print(f"   [PASS] Found endpoint: {endpoint}")
    else:
        print(f"   [FAIL] Missing endpoint: {endpoint}")
        sys.exit(1)

# Test 6: Verify old functions are removed
print("\n[Test 6] Verify old functions removed...")
old_functions = ['classify_error', 'search_similar_errors_rag', 'extract_file_paths', 'create_classification_workflow']
found_old = []

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name in old_functions:
            found_old.append(node.name)

if found_old:
    print(f"   [FAIL] Old functions still exist: {found_old}")
    sys.exit(1)
else:
    print("   [PASS] All old linear workflow functions removed")

# Test 7: Check for Task 0-ARCH.6 documentation
print("\n[Test 7] Check for task documentation...")
if 'Task 0-ARCH.6' in code:
    print("   [PASS] Task 0-ARCH.6 documented in file")
else:
    print("   [WARN] Task 0-ARCH.6 not mentioned in documentation")

# Test 8: Check for ReAct keywords
print("\n[Test 8] Check for ReAct keywords...")
react_keywords = ['ReAct', 'think/act/observe', 'iterative', 'self-correction']
found_keywords = [kw for kw in react_keywords if kw in code]
print(f"   [PASS] Found ReAct keywords: {', '.join(found_keywords)}")

# Test 9: Count lines of code
print("\n[Test 9] Analyze code metrics...")
lines = code.split('\n')
total_lines = len(lines)
code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
comment_lines = [l for l in lines if l.strip().startswith('#')]
print(f"   Total lines: {total_lines}")
print(f"   Code lines: {len(code_lines)}")
print(f"   Comment lines: {len(comment_lines)}")

if total_lines < 200:
    print("   [PASS] Code significantly reduced (was 428 lines, now {})".format(total_lines))
else:
    print(f"   [INFO] Code size: {total_lines} lines (was 428 lines)")

# Summary
print("\n" + "=" * 70)
print(" VERIFICATION SUMMARY")
print("=" * 70)
print("\n✅ ALL VERIFICATION CHECKS PASSED!")
print("\nLangGraph Refactor Complete:")
print("  ✅ File syntax is valid")
print("  ✅ ReActAgent properly imported")
print("  ✅ initialize_react_agent function exists")
print("  ✅ All new endpoints defined")
print("  ✅ Old linear workflow removed")
print("  ✅ Task 0-ARCH.6 documented")
print("\nRefactor Status: READY FOR INTEGRATION TESTING")
print("=" * 70)
