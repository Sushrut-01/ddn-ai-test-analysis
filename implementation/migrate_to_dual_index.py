"""
Migrate Data to Dual-Index RAG Architecture
============================================

Migrates data from single index to dual-index system:
- 25 error docs (ERR001-ERR025) → ddn-knowledge-docs
- Test failures → ddn-test-failures
"""

import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone
import logging
import time

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

# Index references
OLD_INDEX_NAME = 'ddn-error-solutions'
KNOWLEDGE_INDEX_NAME = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')
FAILURES_INDEX_NAME = os.getenv('PINECONE_FAILURES_INDEX', 'ddn-test-failures')

def create_embedding(text):
    """Create OpenAI embedding"""
    response = openai_client.embeddings.create(
        model='text-embedding-3-small',
        input=text
    )
    return response.data[0].embedding

def load_error_documentation():
    """Load all error documentation from JSON files"""
    errors = []

    # Get base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load Phase 1 errors (ERR001-ERR010)
    logger.info("Loading Phase 1 error documentation (ERR001-ERR010)...")
    phase1_path = os.path.join(base_dir, 'error-documentation.json')
    try:
        with open(phase1_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            errors.extend(data['errors'])
            logger.info(f"✓ Loaded {len(data['errors'])} errors from Phase 1")
    except Exception as e:
        logger.error(f"Error loading Phase 1: {e}")

    # Load Phase 2 errors (ERR011-ERR025)
    logger.info("Loading Phase 2 error documentation (ERR011-ERR025)...")
    phase2_path = os.path.join(base_dir, 'error-documentation-phase2.json')
    try:
        with open(phase2_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            errors.extend(data['errors'])
            logger.info(f"✓ Loaded {len(data['errors'])} errors from Phase 2")
    except Exception as e:
        logger.error(f"Error loading Phase 2: {e}")

    logger.info(f"Total error documentation entries: {len(errors)}")
    return errors

def prepare_error_text(error):
    """Prepare comprehensive text for embedding"""
    text_parts = [
        f"Error ID: {error['error_id']}",
        f"Type: {error['error_type']}",
        f"Category: {error['error_category']}",
        f"Subcategory: {error['subcategory']}",
        f"Error Message: {error['error_message']}",
        f"Root Cause: {error['root_cause']}",
        f"Component: {error['component']}",
        f"Solution Steps: {' '.join(error['solution_steps'][:5])}",
        f"Tags: {' '.join(error['tags'])}"
    ]
    return '\n'.join(text_parts)

def migrate_error_documentation():
    """Migrate all error documentation to knowledge index"""
    logger.info("\n" + "="*70)
    logger.info("STEP 1: Migrate Error Documentation to ddn-knowledge-docs")
    logger.info("="*70)

    # Load error docs
    errors = load_error_documentation()

    if not errors:
        logger.error("❌ No error documentation found!")
        return False

    # Connect to knowledge index
    try:
        knowledge_index = pc.Index(KNOWLEDGE_INDEX_NAME)
        logger.info(f"✓ Connected to {KNOWLEDGE_INDEX_NAME}")
    except Exception as e:
        logger.error(f"❌ Failed to connect to knowledge index: {e}")
        return False

    # Migrate each error
    success_count = 0
    fail_count = 0

    for i, error in enumerate(errors, 1):
        error_id = error['error_id']
        logger.info(f"\nProcessing {i}/{len(errors)}: {error_id} - {error['error_type']}")

        try:
            # Create comprehensive text for embedding
            text = prepare_error_text(error)
            logger.info(f"  Text length: {len(text)} characters")

            # Create embedding
            embedding = create_embedding(text)
            logger.info(f"  ✓ Created embedding (1536 dimensions)")

            # Prepare metadata (truncate long fields)
            metadata = {
                'doc_type': 'error_documentation',
                'error_id': error['error_id'],
                'error_type': error['error_type'],
                'category': error['error_category'],
                'subcategory': error['subcategory'],
                'error_message': error['error_message'][:500],
                'root_cause': error['root_cause'][:500],
                'severity': error['severity'],
                'component': error['component'],
                'tags': ','.join(error['tags']),
                'frequency': error['frequency'],
                'file_path': error.get('file_path', ''),
                'line_range': error.get('line_range', ''),
                'uploaded_at': time.strftime('%Y-%m-%dT%H:%M:%S')
            }

            # Upload to Pinecone
            knowledge_index.upsert(vectors=[{
                'id': f"error_doc_{error['error_id']}",
                'values': embedding,
                'metadata': metadata
            }])

            logger.info(f"  ✅ Uploaded to {KNOWLEDGE_INDEX_NAME}")
            success_count += 1

        except Exception as e:
            logger.error(f"  ❌ Failed to migrate {error_id}: {str(e)[:100]}")
            fail_count += 1

    # Summary
    logger.info("\n" + "="*70)
    logger.info("MIGRATION SUMMARY - Error Documentation")
    logger.info("="*70)
    logger.info(f"Total: {len(errors)}")
    logger.info(f"✅ Success: {success_count}")
    logger.info(f"❌ Failed: {fail_count}")

    # Verify final count
    stats = knowledge_index.describe_index_stats()
    logger.info(f"\n📊 Knowledge Index Stats:")
    logger.info(f"  Total vectors: {stats.total_vector_count}")

    return success_count == len(errors)

def migrate_test_failures():
    """Migrate test failures from old index to failures index"""
    logger.info("\n" + "="*70)
    logger.info("STEP 2: Migrate Test Failures to ddn-test-failures")
    logger.info("="*70)

    try:
        # Connect to old index
        old_index = pc.Index(OLD_INDEX_NAME)
        logger.info(f"✓ Connected to old index: {OLD_INDEX_NAME}")

        # Get all vectors from old index
        old_stats = old_index.describe_index_stats()
        logger.info(f"  Old index has {old_stats.total_vector_count} vectors")

        # Query to get all non-documentation vectors
        dummy_vector = [0.0] * 1536
        results = old_index.query(
            vector=dummy_vector,
            top_k=10000,
            include_metadata=True,
            include_values=True
        )

        # Filter for test failures (not error documentation)
        test_failures = [
            match for match in results.matches
            if match.metadata.get('doc_type') != 'error_documentation'
        ]

        logger.info(f"  Found {len(test_failures)} test failure vectors")

        if not test_failures:
            logger.warning("⚠️  No test failures found in old index")
            return True

        # Connect to failures index
        failures_index = pc.Index(FAILURES_INDEX_NAME)
        logger.info(f"✓ Connected to {FAILURES_INDEX_NAME}")

        # Migrate each test failure
        success_count = 0
        for i, match in enumerate(test_failures, 1):
            try:
                logger.info(f"\nMigrating test failure {i}/{len(test_failures)}: {match.id}")

                failures_index.upsert(vectors=[{
                    'id': match.id,
                    'values': match.values,
                    'metadata': match.metadata
                }])

                logger.info(f"  ✅ Migrated to {FAILURES_INDEX_NAME}")
                success_count += 1

            except Exception as e:
                logger.error(f"  ❌ Failed: {str(e)[:100]}")

        # Summary
        logger.info("\n" + "="*70)
        logger.info("MIGRATION SUMMARY - Test Failures")
        logger.info("="*70)
        logger.info(f"Total: {len(test_failures)}")
        logger.info(f"✅ Success: {success_count}")
        logger.info(f"❌ Failed: {len(test_failures) - success_count}")

        # Verify final count
        stats = failures_index.describe_index_stats()
        logger.info(f"\n📊 Failures Index Stats:")
        logger.info(f"  Total vectors: {stats.total_vector_count}")

        return success_count == len(test_failures)

    except Exception as e:
        logger.error(f"❌ Error migrating test failures: {e}")
        return False

def verify_migration():
    """Verify both indexes have correct data"""
    logger.info("\n" + "="*70)
    logger.info("STEP 3: Verify Migration")
    logger.info("="*70)

    try:
        # Check knowledge index
        knowledge_index = pc.Index(KNOWLEDGE_INDEX_NAME)
        knowledge_stats = knowledge_index.describe_index_stats()
        logger.info(f"\n✓ {KNOWLEDGE_INDEX_NAME}:")
        logger.info(f"  Total vectors: {knowledge_stats.total_vector_count}")
        logger.info(f"  Expected: 25 error documentation entries")

        # Check failures index
        failures_index = pc.Index(FAILURES_INDEX_NAME)
        failures_stats = failures_index.describe_index_stats()
        logger.info(f"\n✓ {FAILURES_INDEX_NAME}:")
        logger.info(f"  Total vectors: {failures_stats.total_vector_count}")
        logger.info(f"  Expected: ~10 test failure entries")

        # Verify knowledge index has error docs
        dummy_vector = [0.0] * 1536
        results = knowledge_index.query(
            vector=dummy_vector,
            top_k=5,
            include_metadata=True,
            filter={"doc_type": {"$eq": "error_documentation"}}
        )

        logger.info(f"\n✓ Sample from {KNOWLEDGE_INDEX_NAME}:")
        for match in results.matches[:3]:
            logger.info(f"  - {match.metadata.get('error_id')}: {match.metadata.get('error_type')}")

        return True

    except Exception as e:
        logger.error(f"❌ Verification failed: {e}")
        return False

def main():
    """Main migration process"""
    logger.info("="*70)
    logger.info("DUAL-INDEX RAG MIGRATION")
    logger.info("="*70)
    logger.info(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"\nSource: {OLD_INDEX_NAME}")
    logger.info(f"Target 1: {KNOWLEDGE_INDEX_NAME} (error documentation)")
    logger.info(f"Target 2: {FAILURES_INDEX_NAME} (test failures)")
    logger.info("")

    # Step 1: Migrate error documentation
    success1 = migrate_error_documentation()

    # Step 2: Migrate test failures
    success2 = migrate_test_failures()

    # Step 3: Verify
    success3 = verify_migration()

    # Final summary
    logger.info("\n" + "="*70)
    logger.info("MIGRATION COMPLETE")
    logger.info("="*70)
    logger.info(f"Finished: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if all([success1, success2, success3]):
        logger.info("\n✅ All migration steps completed successfully!")
        logger.info("\nNext steps:")
        logger.info("  1. Update AI services to query both indexes")
        logger.info("  2. Test dual-index RAG system")
        logger.info("  3. Delete old index after verification")
        return True
    else:
        logger.error("\n❌ Some migration steps failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
