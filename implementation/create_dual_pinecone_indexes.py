"""
Create Two Pinecone Indexes for Dual-Index RAG Architecture
=============================================================

Creates two separate indexes:
1. ddn-knowledge-docs - For curated error documentation (Source A)
2. ddn-test-failures - For operational test failure data (Source B)
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Initialize Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'aped-4627-b74a')

pc = Pinecone(api_key=PINECONE_API_KEY)

# Index configurations
INDEXES = [
    {
        'name': 'ddn-knowledge-docs',
        'purpose': 'Curated error documentation (Source A)',
        'description': 'Static knowledge base with proven solutions'
    },
    {
        'name': 'ddn-test-failures',
        'purpose': 'Operational test failure data (Source B)',
        'description': 'Dynamic library of past test failures'
    }
]

def create_index(index_config):
    """Create a Pinecone index if it doesn't exist"""
    index_name = index_config['name']

    logger.info(f"\n{'='*70}")
    logger.info(f"Creating Index: {index_name}")
    logger.info(f"Purpose: {index_config['purpose']}")
    logger.info(f"{'='*70}")

    # Check if index already exists
    existing_indexes = pc.list_indexes()
    index_names = [idx.name for idx in existing_indexes.indexes]

    if index_name in index_names:
        logger.info(f"✓ Index '{index_name}' already exists")

        # Get index info
        index_info = pc.describe_index(index_name)
        logger.info(f"  Dimension: {index_info.dimension}")
        logger.info(f"  Metric: {index_info.metric}")
        logger.info(f"  Host: {index_info.host}")
        return True

    # Create new index
    try:
        logger.info(f"Creating new index '{index_name}'...")

        pc.create_index(
            name=index_name,
            dimension=1536,  # OpenAI text-embedding-3-small
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )

        # Wait for index to be ready
        logger.info("Waiting for index to be ready...")
        timeout = 120  # 2 minutes
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                index_info = pc.describe_index(index_name)
                if index_info.status.ready:
                    logger.info(f"✅ Index '{index_name}' created successfully!")
                    logger.info(f"  Dimension: {index_info.dimension}")
                    logger.info(f"  Metric: {index_info.metric}")
                    logger.info(f"  Host: {index_info.host}")
                    logger.info(f"  Status: {index_info.status.state}")
                    return True
            except Exception as e:
                pass

            time.sleep(5)

        logger.error(f"Timeout waiting for index '{index_name}' to be ready")
        return False

    except Exception as e:
        logger.error(f"Error creating index '{index_name}': {str(e)}")
        return False

def main():
    """Create both Pinecone indexes"""
    logger.info("="*70)
    logger.info("TWO-INDEX RAG ARCHITECTURE - INDEX CREATION")
    logger.info("="*70)
    logger.info("\nThis script creates two separate Pinecone indexes:")
    logger.info("  1. ddn-knowledge-docs  - Curated error documentation")
    logger.info("  2. ddn-test-failures   - Operational test failures")
    logger.info("")

    # Verify API key
    if not PINECONE_API_KEY:
        logger.error("❌ PINECONE_API_KEY not set in environment")
        return False

    logger.info(f"✓ Pinecone API Key: {PINECONE_API_KEY[:10]}...")
    logger.info(f"✓ Environment: {PINECONE_ENVIRONMENT}")
    logger.info("")

    # Create both indexes
    results = []
    for index_config in INDEXES:
        success = create_index(index_config)
        results.append(success)

    # Summary
    logger.info("\n" + "="*70)
    logger.info("INDEX CREATION SUMMARY")
    logger.info("="*70)

    for idx, index_config in enumerate(INDEXES):
        status = "✅ SUCCESS" if results[idx] else "❌ FAILED"
        logger.info(f"{status}: {index_config['name']}")

    all_success = all(results)

    if all_success:
        logger.info("\n✅ Both indexes created successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Update .env.MASTER with new index names")
        logger.info("  2. Migrate error documentation to ddn-knowledge-docs")
        logger.info("  3. Migrate test failures to ddn-test-failures")
        logger.info("  4. Update services to query both indexes")
    else:
        logger.error("\n❌ Some indexes failed to create. Check errors above.")

    return all_success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
