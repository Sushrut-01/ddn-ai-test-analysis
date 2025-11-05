"""
Test BM25 Index (Task 0-ARCH.25)

Tests the BM25 index building and retrieval functionality.

Author: AI Analysis System
Date: 2025-11-02
"""

import os
import sys
import logging

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from retrieval.build_bm25_index import BM25IndexBuilder

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_build_index():
    """Test building BM25 index"""
    print("=" * 60)
    print("Test 1: Build BM25 Index")
    print("=" * 60)

    builder = BM25IndexBuilder()

    # Load sample documents
    sample_docs = [
        "Authentication error in middleware.py - TOKEN_EXPIRATION configuration issue",
        "SQL database connection timeout in database.py",
        "JWT token validation failed - invalid signature",
        "API endpoint returns 401 unauthorized - authentication middleware",
        "Python import error - module not found",
        "Test failed with AssertionError in test_auth.py",
        "Configuration error - missing MONGODB_URI environment variable",
        "Network timeout when connecting to external service",
        "Memory leak detected in background worker process",
        "File not found error - config.json missing"
    ]

    # Add documents manually
    for i, text in enumerate(sample_docs):
        builder.documents.append(text)
        builder.metadata.append({
            'doc_id': f'sample_{i}',
            'source': 'test',
            'category': 'SAMPLE'
        })

    print(f"Added {len(builder.documents)} sample documents")

    # Build index
    bm25, documents, metadata = builder.build_index()

    print(f"✓ Index built with {len(documents)} documents")
    return builder, bm25, documents, metadata


def test_search_index(builder, bm25, documents, metadata):
    """Test searching BM25 index"""
    print("\n" + "=" * 60)
    print("Test 2: Search BM25 Index")
    print("=" * 60)

    test_queries = [
        "authentication error",
        "TOKEN_EXPIRATION",
        "database connection",
        "JWT token",
        "test failed"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)

        # Tokenize query
        tokenized_query = builder.tokenize(query)

        # Get BM25 scores
        scores = bm25.get_scores(tokenized_query)

        # Get top 3 results
        top_indices = scores.argsort()[-3:][::-1]

        for rank, idx in enumerate(top_indices, 1):
            if scores[idx] > 0:
                print(f"{rank}. Score: {scores[idx]:.4f}")
                print(f"   Doc: {documents[idx][:80]}...")
                print(f"   ID: {metadata[idx]['doc_id']}")


def test_save_load_index(builder, bm25, documents, metadata):
    """Test saving and loading index"""
    print("\n" + "=" * 60)
    print("Test 3: Save and Load Index")
    print("=" * 60)

    # Save index
    test_path = 'implementation/data/test_bm25_index.pkl'
    builder.save_index(bm25, documents, metadata, test_path)
    print(f"✓ Index saved to {test_path}")

    # Load index
    loaded_bm25, loaded_docs, loaded_meta = builder.load_existing_index(test_path)
    print(f"✓ Index loaded with {len(loaded_docs)} documents")

    # Verify
    assert len(loaded_docs) == len(documents), "Document count mismatch"
    assert len(loaded_meta) == len(metadata), "Metadata count mismatch"
    print("✓ Saved and loaded index match")

    return test_path


def test_with_fusion_rag(index_path):
    """Test BM25 index with FusionRAG"""
    print("\n" + "=" * 60)
    print("Test 4: Integration with FusionRAG")
    print("=" * 60)

    try:
        from retrieval.fusion_rag_service import FusionRAG

        # Initialize FusionRAG with BM25 index
        fusion_rag = FusionRAG(bm25_index_path=index_path)

        # Check BM25 is available
        if fusion_rag.sources_available['bm25']:
            print("✓ BM25 source loaded successfully in FusionRAG")

            # Get statistics
            stats = fusion_rag.get_statistics()
            print(f"✓ BM25 has {stats.get('bm25', {}).get('num_documents', 0)} documents")

            # Test retrieval (only if BM25 is the only available source)
            if sum(fusion_rag.sources_available.values()) == 1:
                print("\nTesting BM25 retrieval through FusionRAG...")
                results = fusion_rag.retrieve(
                    query="authentication error",
                    top_k=3
                )

                print(f"✓ Retrieved {len(results)} results")
                for i, doc in enumerate(results, 1):
                    print(f"\n{i}. RRF Score: {doc['rrf_score']:.4f}")
                    print(f"   Source: {doc['primary_source']}")
                    print(f"   Text: {doc['text'][:80]}...")
            else:
                print("✓ BM25 is one of multiple sources available")
        else:
            print("✗ BM25 source not available in FusionRAG")

    except ImportError:
        print("⚠ FusionRAG not available - skipping integration test")


def main():
    """Run all tests"""
    print("=" * 60)
    print("BM25 Index Test Suite - Task 0-ARCH.25")
    print("=" * 60)
    print()

    # Test 1: Build index
    builder, bm25, documents, metadata = test_build_index()

    # Test 2: Search index
    test_search_index(builder, bm25, documents, metadata)

    # Test 3: Save and load
    index_path = test_save_load_index(builder, bm25, documents, metadata)

    # Test 4: Integration with FusionRAG
    test_with_fusion_rag(index_path)

    print("\n" + "=" * 60)
    print("All Tests Complete!")
    print("=" * 60)
    print()
    print(f"Test index saved to: {index_path}")
    print()
    print("To build production index from MongoDB:")
    print("  python implementation/retrieval/build_bm25_index.py")
    print()


if __name__ == '__main__':
    main()
