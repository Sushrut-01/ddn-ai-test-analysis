"""
Test RAG Query for Error Documentation
=======================================

This script tests querying Pinecone for similar errors

Usage:
    python test_rag_query.py
"""

import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize clients
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME', 'ddn-error-solutions')

openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def create_embedding(text):
    """Create embedding for query text"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def query_similar_errors(error_message, top_k=3):
    """
    Query Pinecone for similar error documentation

    Args:
        error_message: Error message from test failure
        top_k: Number of similar errors to return

    Returns:
        List of similar error documents
    """
    logger.info(f"Querying for: {error_message[:100]}...")

    # Create embedding for query
    query_embedding = create_embedding(error_message)

    # Query Pinecone (only error documentation, not past failures)
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={
            "doc_type": {"$eq": "error_documentation"}
        }
    )

    similar_errors = []
    for match in results.matches:
        similar_errors.append({
            'score': match.score,
            'error_id': match.metadata.get('error_id'),
            'error_type': match.metadata.get('error_type'),
            'category': match.metadata.get('category'),
            'error_message': match.metadata.get('error_message'),
            'root_cause': match.metadata.get('root_cause'),
            'severity': match.metadata.get('severity'),
            'component': match.metadata.get('component'),
            'tags': match.metadata.get('tags', '').split(',')
        })

    return similar_errors


def test_queries():
    """
    Test various error queries
    """
    logger.info("=" * 70)
    logger.info("Testing RAG Queries for Error Documentation")
    logger.info("=" * 70)

    # Test cases
    test_cases = [
        {
            "name": "NullPointerException Test",
            "query": "NullPointerException: Cannot invoke method because object is null"
        },
        {
            "name": "Connection Refused Test",
            "query": "Connection refused: connect to http://exascaler.ddn.local:8080"
        },
        {
            "name": "Authentication Failure Test",
            "query": "401 Unauthorized: Invalid API key"
        },
        {
            "name": "DNS Resolution Test",
            "query": "UnknownHostException: exascaler.ddn.local cannot be resolved"
        },
        {
            "name": "S3 Access Denied Test",
            "query": "Access Denied error when trying to create S3 bucket"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Test {i}: {test_case['name']}")
        logger.info(f"{'=' * 70}")
        logger.info(f"Query: {test_case['query']}")

        # Query for similar errors
        similar_errors = query_similar_errors(test_case['query'], top_k=3)

        logger.info(f"\nFound {len(similar_errors)} similar errors:\n")

        for j, error in enumerate(similar_errors, 1):
            logger.info(f"--- Match {j} (Similarity: {error['score']:.4f}) ---")
            logger.info(f"Error ID: {error['error_id']}")
            logger.info(f"Type: {error['error_type']}")
            logger.info(f"Category: {error['category']}")
            logger.info(f"Component: {error['component']}")
            logger.info(f"Severity: {error['severity']}")
            logger.info(f"Root Cause: {error['root_cause'][:200]}...")
            logger.info(f"Tags: {', '.join(error['tags'][:5])}")
            logger.info("")

    logger.info("=" * 70)
    logger.info("✅ RAG Query Test Complete!")
    logger.info("=" * 70)


def main():
    """Main test function"""
    try:
        # Check index stats
        logger.info("\nChecking Pinecone index stats...")
        stats = index.describe_index_stats()
        logger.info(f"Total vectors in index: {stats.total_vector_count}")
        logger.info(f"Dimension: {stats.dimension}")

        # Count error documentation vectors
        # Query with very generic text to count docs
        test_embedding = create_embedding("error documentation")
        results = index.query(
            vector=test_embedding,
            top_k=1000,
            include_metadata=True,
            filter={"doc_type": {"$eq": "error_documentation"}}
        )
        error_doc_count = len(results.matches)
        logger.info(f"Error documentation vectors: {error_doc_count}")

        if error_doc_count == 0:
            logger.warning("\n⚠️  No error documentation found in Pinecone!")
            logger.warning("Run: python load_error_docs_to_pinecone.py first")
            return

        # Run test queries
        test_queries()

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set")
        exit(1)
    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set")
        exit(1)

    main()
