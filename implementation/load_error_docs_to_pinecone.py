"""
Load Error Documentation into Pinecone for RAG Integration
===========================================================

This script:
1. Reads error-documentation.json
2. Creates embeddings for each error using OpenAI
3. Uploads to Pinecone with metadata
4. Enables similarity search for AI analysis

Usage:
    python load_error_docs_to_pinecone.py
"""

import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize Pinecone
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT', 'us-east-1')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX', 'ddn-error-solutions')  # Use existing index

pc = Pinecone(api_key=PINECONE_API_KEY)

# Constants
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
ERROR_DOC_FILE = "../error-documentation.json"


def create_embedding(text):
    """
    Create OpenAI embedding for text

    Args:
        text: Text to embed

    Returns:
        List of floats (1536 dimensions)
    """
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error creating embedding: {str(e)}")
        return None


def prepare_error_text(error):
    """
    Prepare comprehensive text for embedding

    Combines all relevant fields for semantic search

    Args:
        error: Error dictionary

    Returns:
        Combined text string
    """
    parts = [
        f"Error Type: {error['error_type']}",
        f"Category: {error['error_category']} - {error['subcategory']}",
        f"Message: {error['error_message']}",
        f"Component: {error['component']}",
        f"Root Cause: {error['root_cause']}",
        f"Solution: {' '.join(error['solution_steps'])}",
        f"Prevention: {error['prevention']}",
        f"Code Before: {error.get('code_before', '')}",
        f"Code After: {error.get('code_after', '')}",
    ]

    return "\n".join(parts)


def load_error_documentation():
    """
    Load error documentation from JSON file

    Returns:
        List of error dictionaries
    """
    try:
        doc_path = os.path.join(os.path.dirname(__file__), ERROR_DOC_FILE)
        logger.info(f"Loading error documentation from: {doc_path}")

        with open(doc_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        errors = data.get('errors', [])
        logger.info(f"✓ Loaded {len(errors)} error documents")
        return errors

    except FileNotFoundError:
        logger.error(f"Error documentation file not found: {doc_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in error documentation: {str(e)}")
        return []


def ensure_pinecone_index():
    """
    Connect to existing Pinecone index

    Returns:
        Pinecone index object
    """
    try:
        logger.info(f"Connecting to Pinecone index: {PINECONE_INDEX_NAME}")

        # Connect to existing index
        index = pc.Index(PINECONE_INDEX_NAME)

        # Get index stats to verify connection
        stats = index.describe_index_stats()
        logger.info(f"✓ Connected to index: {PINECONE_INDEX_NAME}")
        logger.info(f"  Total vectors: {stats.total_vector_count}")
        logger.info(f"  Dimension: {stats.dimension}")

        return index

    except Exception as e:
        logger.error(f"Error connecting to Pinecone index: {str(e)}")
        logger.error(f"Make sure index '{PINECONE_INDEX_NAME}' exists in your Pinecone account")
        return None


def upload_error_to_pinecone(index, error, embedding):
    """
    Upload single error document to Pinecone

    Args:
        index: Pinecone index
        error: Error dictionary
        embedding: Vector embedding

    Returns:
        Boolean success status
    """
    try:
        # Create unique ID
        vector_id = f"error_doc_{error['error_id']}"

        # Prepare metadata (Pinecone has size limits)
        metadata = {
            'error_id': error['error_id'],
            'error_type': error['error_type'],
            'category': error['error_category'],
            'subcategory': error['subcategory'],
            'error_message': error['error_message'][:500],  # Truncate if too long
            'component': error['component'],
            'file_path': error.get('file_path', ''),
            'line_range': error.get('line_range', ''),
            'root_cause': error['root_cause'][:500],
            'severity': error['severity'],
            'frequency': error['frequency'],
            'tags': ','.join(error.get('tags', [])),
            'test_scenarios': ','.join(error.get('test_scenarios', [])),
            'doc_type': 'error_documentation',
            'uploaded_at': datetime.utcnow().isoformat()
        }

        # Upload to Pinecone
        index.upsert(
            vectors=[{
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            }]
        )

        logger.info(f"✓ Uploaded {error['error_id']}: {error['error_type']}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to upload {error['error_id']}: {str(e)}")
        return False


def main():
    """
    Main function to load error docs into Pinecone
    """
    logger.info("=" * 60)
    logger.info("DDN Error Documentation -> Pinecone Loader")
    logger.info("=" * 60)

    # Step 1: Load error documentation
    logger.info("\n[1/4] Loading error documentation...")
    errors = load_error_documentation()

    if not errors:
        logger.error("No error documentation found. Exiting.")
        sys.exit(1)

    # Step 2: Ensure Pinecone index exists
    logger.info("\n[2/4] Setting up Pinecone index...")
    index = ensure_pinecone_index()

    if not index:
        logger.error("Failed to setup Pinecone index. Exiting.")
        sys.exit(1)

    # Step 3: Create embeddings and upload
    logger.info(f"\n[3/4] Creating embeddings and uploading to Pinecone...")
    logger.info(f"Processing {len(errors)} error documents...")

    successful_uploads = 0
    failed_uploads = 0

    for i, error in enumerate(errors, 1):
        logger.info(f"\n--- Processing {i}/{len(errors)} ---")

        # Prepare text for embedding
        error_text = prepare_error_text(error)
        logger.info(f"Text length: {len(error_text)} characters")

        # Create embedding
        logger.info("Creating embedding with OpenAI...")
        embedding = create_embedding(error_text)

        if embedding is None:
            logger.error(f"Failed to create embedding for {error['error_id']}")
            failed_uploads += 1
            continue

        logger.info(f"✓ Embedding created ({len(embedding)} dimensions)")

        # Upload to Pinecone
        logger.info("Uploading to Pinecone...")
        if upload_error_to_pinecone(index, error, embedding):
            successful_uploads += 1
        else:
            failed_uploads += 1

    # Step 4: Summary
    logger.info("\n" + "=" * 60)
    logger.info("[4/4] Upload Summary")
    logger.info("=" * 60)
    logger.info(f"Total errors: {len(errors)}")
    logger.info(f"✓ Successful uploads: {successful_uploads}")
    logger.info(f"✗ Failed uploads: {failed_uploads}")

    # Get index stats
    try:
        stats = index.describe_index_stats()
        logger.info(f"\nPinecone Index Stats:")
        logger.info(f"  Total vectors: {stats.total_vector_count}")
        logger.info(f"  Dimension: {stats.dimension}")
        logger.info(f"  Index fullness: {stats.index_fullness}")
    except Exception as e:
        logger.warning(f"Could not retrieve index stats: {str(e)}")

    logger.info("\n✅ Error documentation loaded into Pinecone successfully!")
    logger.info("AI analysis service can now use RAG for better suggestions.")
    logger.info("\nNext steps:")
    logger.info("1. Test RAG query: python test_rag_query.py")
    logger.info("2. Update ai_analysis_service.py to use error docs")
    logger.info("3. Verify dashboard shows similar error suggestions")


if __name__ == "__main__":
    # Check environment variables
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set in environment")
        sys.exit(1)

    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set in environment")
        sys.exit(1)

    main()
