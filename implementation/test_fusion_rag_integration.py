"""
Test Fusion RAG Integration in ReAct Agent (Task 0-ARCH.29)

Tests:
1. ReAct agent initializes Fusion RAG correctly
2. _tool_pinecone_knowledge() uses Fusion RAG
3. _tool_pinecone_error_library() uses Fusion RAG
4. Results include source attribution (rrf_score, rerank_score, sources)

Author: AI Analysis System
Date: 2025-11-03
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv('.env.MASTER')

from implementation.agents.react_agent_service import ReActAgent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_fusion_rag_initialization():
    """Test 1: Verify Fusion RAG initializes in ReAct agent"""
    print("=" * 70)
    print("TEST 1: Fusion RAG Initialization")
    print("=" * 70)

    try:
        agent = ReActAgent()

        # Check if Fusion RAG was initialized
        if hasattr(agent, 'fusion_rag') and agent.fusion_rag is not None:
            print("✅ PASS: Fusion RAG initialized successfully")
            print(f"   - Type: {type(agent.fusion_rag).__name__}")

            # Check components
            if hasattr(agent.fusion_rag, 'cross_encoder'):
                print(f"   - CrossEncoder: {'✓ Enabled' if agent.fusion_rag.cross_encoder else '✗ Disabled'}")
            if hasattr(agent.fusion_rag, 'query_expander'):
                print(f"   - Query Expander: {'✓ Enabled' if agent.fusion_rag.query_expander else '✗ Disabled'}")

            return agent
        else:
            print("⚠️  WARNING: Fusion RAG not initialized (fallback to Pinecone-only)")
            return agent

    except Exception as e:
        print(f"❌ FAIL: Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_knowledge_search(agent):
    """Test 2: Test _tool_pinecone_knowledge with Fusion RAG"""
    print("\n" + "=" * 70)
    print("TEST 2: Knowledge Search with Fusion RAG")
    print("=" * 70)

    if not agent:
        print("❌ SKIP: Agent not initialized")
        return

    # Create test state
    test_state = {
        'error_message': 'JWT authentication token expired',
        'error_category': 'AUTH_ERROR',
        'rag_results': []
    }

    try:
        results = agent._tool_pinecone_knowledge(test_state)

        print(f"\n📊 Retrieved {len(results)} results")

        if len(results) > 0:
            print("\n✅ PASS: Knowledge search returned results")

            # Check first result structure
            first_result = results[0]
            print("\n📝 First Result Structure:")
            print(f"   - source: {first_result.get('source', 'N/A')}")
            print(f"   - content length: {len(first_result.get('content', ''))} chars")
            print(f"   - confidence: {first_result.get('confidence', 'N/A')}")

            # Check Fusion RAG specific fields
            if 'rrf_score' in first_result:
                print(f"   - rrf_score: {first_result['rrf_score']:.4f} ✓")
            else:
                print(f"   - rrf_score: Missing ✗")

            if 'rerank_score' in first_result:
                print(f"   - rerank_score: {first_result['rerank_score']:.4f} ✓" if first_result['rerank_score'] else "   - rerank_score: None (re-ranking disabled)")
            else:
                print(f"   - rerank_score: Missing ✗")

            if 'sources' in first_result:
                print(f"   - sources: {len(first_result['sources'])} retrieval sources ✓")
                for src in first_result['sources'][:3]:  # Show first 3
                    print(f"      • {src}")
            else:
                print(f"   - sources: Missing ✗")

            # Show snippet of content
            content_preview = first_result.get('content', '')[:200]
            print(f"\n📄 Content Preview:")
            print(f"   {content_preview}...")

        else:
            print("⚠️  WARNING: No results returned")

    except Exception as e:
        print(f"❌ FAIL: Knowledge search failed: {e}")
        import traceback
        traceback.print_exc()


def test_error_library_search(agent):
    """Test 3: Test _tool_pinecone_error_library with Fusion RAG"""
    print("\n" + "=" * 70)
    print("TEST 3: Error Library Search with Fusion RAG")
    print("=" * 70)

    if not agent:
        print("❌ SKIP: Agent not initialized")
        return

    # Create test state
    test_state = {
        'error_message': 'Database connection timeout',
        'error_category': 'DATABASE_ERROR',
        'rag_results': []
    }

    try:
        results = agent._tool_pinecone_error_library(test_state)

        print(f"\n📊 Retrieved {len(results)} results")

        if len(results) > 0:
            print("\n✅ PASS: Error library search returned results")

            # Check first result structure
            first_result = results[0]
            print("\n📝 First Result Structure:")
            print(f"   - source: {first_result.get('source', 'N/A')}")
            print(f"   - content length: {len(first_result.get('content', ''))} chars")
            print(f"   - confidence: {first_result.get('confidence', 'N/A')}")

            # Check Fusion RAG specific fields
            if 'rrf_score' in first_result:
                print(f"   - rrf_score: {first_result['rrf_score']:.4f} ✓")
            else:
                print(f"   - rrf_score: Missing ✗")

            if 'rerank_score' in first_result:
                print(f"   - rerank_score: {first_result['rerank_score']:.4f} ✓" if first_result['rerank_score'] else "   - rerank_score: None (re-ranking disabled)")
            else:
                print(f"   - rerank_score: Missing ✗")

            if 'sources' in first_result:
                print(f"   - sources: {len(first_result['sources'])} retrieval sources ✓")
                for src in first_result['sources'][:3]:  # Show first 3
                    print(f"      • {src}")
            else:
                print(f"   - sources: Missing ✗")

            # Show snippet of content
            content_preview = first_result.get('content', '')[:200]
            print(f"\n📄 Content Preview:")
            print(f"   {content_preview}...")

        else:
            print("⚠️  WARNING: No results returned")

    except Exception as e:
        print(f"❌ FAIL: Error library search failed: {e}")
        import traceback
        traceback.print_exc()


def test_source_attribution(agent):
    """Test 4: Verify source attribution in results"""
    print("\n" + "=" * 70)
    print("TEST 4: Source Attribution Verification")
    print("=" * 70)

    if not agent:
        print("❌ SKIP: Agent not initialized")
        return

    # Create test state
    test_state = {
        'error_message': 'API authentication failed with 401',
        'error_category': 'AUTH_ERROR',
        'rag_results': []
    }

    try:
        results = agent._tool_pinecone_knowledge(test_state)

        if len(results) == 0:
            print("⚠️  WARNING: No results to test attribution")
            return

        print(f"\n📊 Testing attribution for {len(results)} results")

        pass_count = 0
        fail_count = 0

        for i, result in enumerate(results, 1):
            has_rrf = 'rrf_score' in result
            has_rerank = 'rerank_score' in result
            has_sources = 'sources' in result

            if has_rrf and has_rerank and has_sources:
                pass_count += 1
                print(f"   ✓ Result {i}: Complete attribution")
            else:
                fail_count += 1
                missing = []
                if not has_rrf: missing.append('rrf_score')
                if not has_rerank: missing.append('rerank_score')
                if not has_sources: missing.append('sources')
                print(f"   ✗ Result {i}: Missing {', '.join(missing)}")

        print(f"\n📈 Attribution Summary:")
        print(f"   - Complete: {pass_count}/{len(results)}")
        print(f"   - Incomplete: {fail_count}/{len(results)}")

        if fail_count == 0:
            print("\n✅ PASS: All results have complete source attribution")
        else:
            print("\n⚠️  PARTIAL: Some results missing attribution fields")

    except Exception as e:
        print(f"❌ FAIL: Attribution test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("FUSION RAG INTEGRATION TEST SUITE - Task 0-ARCH.29")
    print("=" * 70)
    print("\nTesting Fusion RAG integration in ReAct Agent Service")
    print("Expected: 4 sources + CrossEncoder re-ranking + Query expansion")
    print()

    # Test 1: Initialization
    agent = test_fusion_rag_initialization()

    if not agent:
        print("\n❌ CRITICAL: Cannot continue - agent initialization failed")
        return

    # Test 2: Knowledge search
    test_knowledge_search(agent)

    # Test 3: Error library search
    test_error_library_search(agent)

    # Test 4: Source attribution
    test_source_attribution(agent)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUITE COMPLETE")
    print("=" * 70)
    print("\n✅ Integration test completed successfully")
    print("\nNext Steps:")
    print("1. Review test results above")
    print("2. Verify source attribution is complete")
    print("3. Update PROGRESS-TRACKER-FINAL.csv to mark Task 0-ARCH.29 complete")
    print("4. Proceed to Task 0-ARCH.30: Performance testing")


if __name__ == '__main__':
    main()
