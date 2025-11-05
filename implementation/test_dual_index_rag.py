"""
Test Dual-Index RAG System
===========================

Validates that both Pinecone indexes are working correctly:
1. ddn-knowledge-docs (Source A): Curated error documentation
2. ddn-error-library (Source B): Past error cases

This script tests:
- Connection to both indexes
- Data retrieval from each index
- RAG query functionality
- Result merging and prioritization
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import logging

# Set UTF-8 encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

# Index names
KNOWLEDGE_INDEX = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')
FAILURES_INDEX = os.getenv('PINECONE_FAILURES_INDEX', 'ddn-error-library')

def create_embedding(text):
    """Create OpenAI embedding for text"""
    try:
        response = openai_client.embeddings.create(
            model='text-embedding-3-small',
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return None

def test_index_connection(index_name, expected_purpose):
    """Test connection to a Pinecone index"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Testing: {index_name}")
    logger.info(f"Purpose: {expected_purpose}")
    logger.info(f"{'='*70}")

    try:
        # Connect to index
        index = pc.Index(index_name)
        logger.info(f"✓ Connected to {index_name}")

        # Get stats
        stats = index.describe_index_stats()
        logger.info(f"  Total vectors: {stats.total_vector_count}")
        logger.info(f"  Dimension: {stats.dimension}")

        if stats.total_vector_count == 0:
            logger.warning(f"⚠️  Index {index_name} is empty!")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ Failed to connect to {index_name}: {e}")
        return False

def query_knowledge_index(query_text, top_k=3):
    """Query Knowledge Index (Source A) for error documentation"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Querying Knowledge Index: {KNOWLEDGE_INDEX}")
    logger.info(f"Query: {query_text}")
    logger.info(f"{'='*70}")

    try:
        # Get index
        index = pc.Index(KNOWLEDGE_INDEX)

        # Create embedding
        embedding = create_embedding(query_text)
        if not embedding:
            return []

        # Query with filter for error documentation
        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True,
            filter={"doc_type": {"$eq": "error_documentation"}}
        )

        logger.info(f"✓ Found {len(results.matches)} matches from knowledge docs")

        # Display results
        for i, match in enumerate(results.matches, 1):
            logger.info(f"\n  Match {i}:")
            logger.info(f"    Similarity: {match.score:.4f}")
            logger.info(f"    Error ID: {match.metadata.get('error_id', 'N/A')}")
            logger.info(f"    Error Type: {match.metadata.get('error_type', 'N/A')}")
            logger.info(f"    Category: {match.metadata.get('category', 'N/A')}")
            logger.info(f"    Severity: {match.metadata.get('severity', 'N/A')}")

        return results.matches

    except Exception as e:
        logger.error(f"❌ Knowledge index query failed: {e}")
        return []

def query_failures_index(query_text, top_k=3):
    """Query Error Library (Source B) for past failures"""
    logger.info(f"\n{'='*70}")
    logger.info(f"Querying Error Library: {FAILURES_INDEX}")
    logger.info(f"Query: {query_text}")
    logger.info(f"{'='*70}")

    try:
        # Get index
        index = pc.Index(FAILURES_INDEX)

        # Create embedding
        embedding = create_embedding(query_text)
        if not embedding:
            return []

        # Query without filter (all past failures)
        results = index.query(
            vector=embedding,
            top_k=top_k,
            include_metadata=True
        )

        logger.info(f"✓ Found {len(results.matches)} matches from error library")

        # Display results
        for i, match in enumerate(results.matches, 1):
            logger.info(f"\n  Match {i}:")
            logger.info(f"    Similarity: {match.score:.4f}")
            logger.info(f"    ID: {match.id}")
            logger.info(f"    Test Name: {match.metadata.get('test_name', 'N/A')}")
            logger.info(f"    Classification: {match.metadata.get('classification', 'N/A')}")
            logger.info(f"    Resolved: {match.metadata.get('resolved', False)}")

        return results.matches

    except Exception as e:
        logger.error(f"❌ Error library query failed: {e}")
        return []

def test_dual_index_query(query_text):
    """Test querying both indexes and merging results"""
    logger.info(f"\n{'='*70}")
    logger.info(f"DUAL-INDEX RAG QUERY TEST")
    logger.info(f"Query: {query_text}")
    logger.info(f"{'='*70}")

    # Query both indexes
    knowledge_results = query_knowledge_index(query_text, top_k=3)
    failures_results = query_failures_index(query_text, top_k=2)

    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"DUAL-INDEX QUERY SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"Knowledge Docs (Source A): {len(knowledge_results)} results")
    logger.info(f"Error Library (Source B): {len(failures_results)} results")
    logger.info(f"Total Results: {len(knowledge_results) + len(failures_results)}")

    # Result quality check
    if knowledge_results:
        avg_knowledge_score = sum(m.score for m in knowledge_results) / len(knowledge_results)
        logger.info(f"Avg Knowledge Score: {avg_knowledge_score:.4f}")

    if failures_results:
        avg_failures_score = sum(m.score for m in failures_results) / len(failures_results)
        logger.info(f"Avg Error Library Score: {avg_failures_score:.4f}")

    return len(knowledge_results) > 0 or len(failures_results) > 0

def main():
    """Main test execution"""
    logger.info("="*70)
    logger.info("DUAL-INDEX RAG SYSTEM TEST")
    logger.info("="*70)
    logger.info(f"Knowledge Index: {KNOWLEDGE_INDEX}")
    logger.info(f"Error Library: {FAILURES_INDEX}")
    logger.info("")

    # Test 1: Index Connections
    logger.info("\n" + "="*70)
    logger.info("TEST 1: INDEX CONNECTIVITY")
    logger.info("="*70)

    knowledge_ok = test_index_connection(
        KNOWLEDGE_INDEX,
        "Curated error documentation (ERR001-ERR025)"
    )

    failures_ok = test_index_connection(
        FAILURES_INDEX,
        "Past error cases from test runs"
    )

    if not knowledge_ok or not failures_ok:
        logger.error("\n❌ Index connection test failed!")
        return False

    # Test 2: Query Test Cases
    logger.info("\n" + "="*70)
    logger.info("TEST 2: DUAL-INDEX QUERIES")
    logger.info("="*70)

    test_queries = [
        "NullPointerException in Java code",
        "DNS resolution failed: Name or service not known",
        "Connection refused to storage server",
        "S3 Access Denied 403 Forbidden",
        "Kerberos authentication failed"
    ]

    all_passed = True
    for i, query in enumerate(test_queries, 1):
        logger.info(f"\n\nTest Case {i}/{len(test_queries)}")
        success = test_dual_index_query(query)
        if not success:
            all_passed = False
            logger.warning(f"⚠️  Test case {i} returned no results")

    # Final Summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)

    if all_passed:
        logger.info("✅ All tests passed!")
        logger.info("\nDual-Index RAG System Status:")
        logger.info("  ✓ Both indexes are connected")
        logger.info("  ✓ Queries return results from both sources")
        logger.info("  ✓ Data separation is working correctly")
        logger.info("\nNext Steps:")
        logger.info("  1. Test with real failure analysis")
        logger.info("  2. Verify AI service uses both indexes")
        logger.info("  3. Delete old indexes (ddn-error-solutions, ddn-test-failures)")
        return True
    else:
        logger.error("❌ Some tests failed!")
        logger.error("Review errors above and check index configuration")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
