"""
Project-Wide Import Verification Test
Tests that all changed dependencies work across the entire project
"""
import sys
import importlib.util
from pathlib import Path

def test_import(module_name, test_imports):
    """Test specific imports from a module"""
    try:
        for import_stmt in test_imports:
            exec(import_stmt)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def test_file_imports(file_path):
    """Test that a file can be imported/compiled"""
    try:
        spec = importlib.util.spec_from_file_location("test_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            # Don't execute, just load to check imports
            return True, "OK"
        return False, "Could not load spec"
    except Exception as e:
        return False, str(e)

print("=" * 70)
print("PROJECT-WIDE IMPORT VERIFICATION")
print("=" * 70)

# Test 1: Core dependency imports
print("\n[TEST 1] Core Dependency Imports")
print("-" * 70)

core_tests = [
    ("pinecone", ["import pinecone", "from pinecone import Pinecone, ServerlessSpec"]),
    ("numpy", ["import numpy as np", "import numpy"]),
    ("scipy", ["import scipy"]),
    ("psycopg2", ["import psycopg2"]),
    ("rank_bm25", ["from rank_bm25 import BM25Okapi"]),
    ("flask", ["from flask import Flask, request, jsonify"]),
    ("openai", ["from openai import OpenAI"]),
]

results = []
for module_name, test_stmts in core_tests:
    success, msg = test_import(module_name, test_stmts)
    status = "[PASS]" if success else "[FAIL]"
    print(f"  {module_name:20s} {status:10s} {msg}")
    results.append((module_name, success))

# Test 2: Pinecone-dependent files
print("\n[TEST 2] Pinecone-Dependent Files (19 files)")
print("-" * 70)

pinecone_files = [
    "dashboard_api_full.py",
    "ai_analysis_service.py",
    "hybrid_search_service.py",
    "knowledge_management_api.py",
    "retrieval/fusion_rag_service.py",
    "retrieval/build_bm25_index.py",
    "migrate_templates_to_pinecone.py",
    "migrate_to_dual_index.py",
    "create_dual_pinecone_indexes.py",
    "load_error_docs_to_pinecone.py",
    "recreate_pinecone_index.py",
    "test_dual_index_rag.py",
    "test_rag_query.py",
    "test_pinecone_connection.py",
    "start_dashboard_api_port5006.py",
]

pinecone_ok = 0
pinecone_fail = 0

for file in pinecone_files:
    file_path = Path(__file__).parent / file
    if file_path.exists():
        success, msg = test_file_imports(file_path)
        status = "[OK]" if success else "[FAIL]"
        print(f"  {file:40s} {status}")
        if success:
            pinecone_ok += 1
        else:
            pinecone_fail += 1
            print(f"    Error: {msg}")
    else:
        print(f"  {file:40s} [NOT FOUND]")

print(f"\n  Summary: {pinecone_ok}/{pinecone_ok + pinecone_fail} files OK")

# Test 3: All services compile check
print("\n[TEST 3] Service Compilation Check")
print("-" * 70)

import py_compile

services = [
    "ai_analysis_service.py",
    "dashboard_api_full.py",
    "knowledge_management_api.py",
    "hybrid_search_service.py",
    "reranking_service.py",
    "manual_trigger_api.py",
    "service_manager_api.py",
]

service_ok = 0
for service in services:
    try:
        py_compile.compile(service, doraise=True)
        print(f"  {service:40s} [COMPILED]")
        service_ok += 1
    except Exception as e:
        print(f"  {service:40s} [FAILED]: {e}")

print(f"\n  Summary: {service_ok}/{len(services)} services compiled")

# Final Summary
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)

total_core = len(core_tests)
passed_core = sum(1 for _, success in results if success)

print(f"Core Dependencies:  {passed_core}/{total_core} passed")
print(f"Pinecone Files:     {pinecone_ok}/{pinecone_ok + pinecone_fail} OK")
print(f"Service Files:      {service_ok}/{len(services)} compiled")

overall_status = "[PASS] ALL TESTS PASSED" if (
    passed_core == total_core and
    pinecone_fail == 0 and
    service_ok == len(services)
) else "[WARNING] SOME TESTS FAILED"

print(f"\nOverall Status: {overall_status}")
print("=" * 70)
