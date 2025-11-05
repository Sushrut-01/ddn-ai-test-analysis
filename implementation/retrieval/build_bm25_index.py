"""
BM25 Index Builder (Task 0-ARCH.25)

Builds a BM25 (Best Match 25) sparse retrieval index from multiple sources:
1. MongoDB error documents
2. Pinecone knowledge docs
3. Error documentation

BM25 provides keyword-based retrieval to complement dense vector search.

Author: AI Analysis System
Date: 2025-11-02
Version: 1.0.0
"""

import os
import sys
import logging
import pickle
import argparse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Database imports
try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("WARNING: pymongo not available. Install with: pip install pymongo")

try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    print("WARNING: pinecone not available. Install with: pip install pinecone-client")

# BM25 import
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print("ERROR: rank_bm25 not available. Install with: pip install rank-bm25")
    sys.exit(1)

# Environment variables
from dotenv import load_dotenv
# Load from .env.MASTER in project root (parent_dir is 'implementation', go up one more level)
project_root = os.path.dirname(parent_dir)
env_path = os.path.join(project_root, '.env.MASTER')
print(f"Loading environment from: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")
load_dotenv(env_path)
print(f"MONGODB_ATLAS_URI after load: {os.getenv('MONGODB_ATLAS_URI', 'NOT SET')[:50] if os.getenv('MONGODB_ATLAS_URI') else 'NOT SET'}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BM25IndexBuilder:
    """
    Builds BM25 index from multiple document sources

    Sources:
        1. MongoDB: Error documents from failures collection
        2. Pinecone: Knowledge documentation
        3. Files: Additional documentation (optional)

    Output:
        Pickle file containing:
            - bm25: BM25Okapi index
            - documents: List of document texts
            - metadata: List of metadata dicts with doc_id, source, etc.
    """

    def __init__(
        self,
        mongodb_uri: Optional[str] = None,
        pinecone_api_key: Optional[str] = None,
        pinecone_index_name: str = "ddn-knowledge-docs"
    ):
        """
        Initialize BM25 index builder

        Args:
            mongodb_uri: MongoDB connection string
            pinecone_api_key: Pinecone API key
            pinecone_index_name: Pinecone index name
        """
        logger.info("[BM25] Initializing BM25 Index Builder...")

        self.documents = []
        self.metadata = []
        self.source_counts = {
            'mongodb': 0,
            'pinecone': 0,
            'files': 0
        }

        # MongoDB setup
        self.mongodb_uri = mongodb_uri or os.getenv('MONGODB_ATLAS_URI')
        logger.info(f"[BM25] MongoDB URI configured: {bool(self.mongodb_uri)}")
        if self.mongodb_uri:
            logger.info(f"[BM25] MongoDB URI: {self.mongodb_uri[:50]}...")
        self.mongo_client = None
        self.mongo_collection = None

        # Pinecone setup
        self.pinecone_api_key = pinecone_api_key or os.getenv('PINECONE_API_KEY')
        self.pinecone_index_name = pinecone_index_name
        self.pinecone_client = None
        self.pinecone_index = None

    def load_from_mongodb(
        self,
        limit: Optional[int] = None,
        date_filter: Optional[datetime] = None
    ) -> int:
        """
        Load error documents from MongoDB

        Args:
            limit: Maximum number of documents to load (None = all)
            date_filter: Only load documents after this date

        Returns:
            Number of documents loaded
        """
        if not MONGODB_AVAILABLE:
            logger.warning("[BM25] MongoDB not available - skipping")
            return 0

        if not self.mongodb_uri:
            logger.warning("[BM25] MONGODB_ATLAS_URI not configured - skipping")
            return 0

        try:
            logger.info("[BM25] Connecting to MongoDB...")
            self.mongo_client = MongoClient(self.mongodb_uri)
            db = self.mongo_client['test_failures']
            self.mongo_collection = db['failures']

            # Build query
            query = {}
            if date_filter:
                query['created_at'] = {'$gte': date_filter}

            # Count total
            total = self.mongo_collection.count_documents(query)
            logger.info(f"[BM25] Found {total} MongoDB documents")

            # Load documents
            cursor = self.mongo_collection.find(query)
            if limit:
                cursor = cursor.limit(limit)

            count = 0
            for doc in cursor:
                # Combine text fields for BM25
                text_parts = []

                if 'error_message' in doc:
                    text_parts.append(doc['error_message'])

                if 'error_stacktrace' in doc:
                    text_parts.append(doc['error_stacktrace'])

                if 'test_name' in doc:
                    text_parts.append(doc['test_name'])

                if 'root_cause' in doc:
                    text_parts.append(doc['root_cause'])

                if 'fix_recommendation' in doc:
                    text_parts.append(doc['fix_recommendation'])

                # Combine all parts
                combined_text = '\n'.join(text_parts)

                if combined_text.strip():
                    self.documents.append(combined_text)
                    self.metadata.append({
                        'doc_id': str(doc['_id']),
                        'source': 'mongodb',
                        'build_id': doc.get('build_id', 'unknown'),
                        'error_category': doc.get('error_category', 'UNKNOWN'),
                        'created_at': doc.get('created_at', '').isoformat() if isinstance(doc.get('created_at'), datetime) else str(doc.get('created_at', ''))
                    })
                    count += 1

                if count % 100 == 0:
                    logger.info(f"[BM25] Loaded {count} MongoDB documents...")

            self.source_counts['mongodb'] = count
            logger.info(f"[BM25] ✓ Loaded {count} documents from MongoDB")
            return count

        except Exception as e:
            logger.error(f"[BM25] Failed to load from MongoDB: {e}")
            return 0

    def load_from_pinecone(
        self,
        namespace: Optional[str] = None,
        limit: Optional[int] = None
    ) -> int:
        """
        Load knowledge documents from Pinecone

        Args:
            namespace: Pinecone namespace (None = default)
            limit: Maximum number of documents to load

        Returns:
            Number of documents loaded
        """
        if not PINECONE_AVAILABLE:
            logger.warning("[BM25] Pinecone not available - skipping")
            return 0

        if not self.pinecone_api_key:
            logger.warning("[BM25] PINECONE_API_KEY not configured - skipping")
            return 0

        try:
            logger.info("[BM25] Connecting to Pinecone...")
            self.pinecone_client = Pinecone(api_key=self.pinecone_api_key)
            self.pinecone_index = self.pinecone_client.Index(self.pinecone_index_name)

            # Get index stats
            stats = self.pinecone_index.describe_index_stats()
            total_vectors = stats.get('total_vector_count', 0)
            logger.info(f"[BM25] Pinecone index has {total_vectors} vectors")

            # Pinecone doesn't have a direct "list all" API
            # We need to query and paginate or use a list of known IDs
            # For now, we'll use a sample query approach

            # Alternative: If you have a list of doc IDs, fetch them
            # For this implementation, we'll query with a broad vector and paginate

            logger.info("[BM25] Loading Pinecone documents via pagination...")

            count = 0
            # Since Pinecone doesn't easily support "list all", we'll use a different approach:
            # Query with dummy vector and get matches, then fetch their full data

            # This is a limitation - in production, you might:
            # 1. Store doc IDs separately and fetch them
            # 2. Use Pinecone's backup/export feature
            # 3. Maintain a separate document store

            # For now, let's implement a fetch-by-ID approach if you have doc IDs
            # Or skip this and rely on MongoDB only

            logger.warning("[BM25] Pinecone bulk export not fully implemented")
            logger.warning("[BM25] To load Pinecone docs, you need to:")
            logger.warning("[BM25]   1. Export doc IDs from Pinecone")
            logger.warning("[BM25]   2. Call fetch() with those IDs")
            logger.warning("[BM25]   3. Or use Pinecone backup feature")
            logger.info("[BM25] Skipping Pinecone for now - using MongoDB only")

            # Placeholder for future implementation
            # If you have a list of IDs:
            # doc_ids = get_all_pinecone_ids()  # You need to implement this
            # for batch in chunks(doc_ids, 100):
            #     response = self.pinecone_index.fetch(batch)
            #     for doc_id, vector_data in response['vectors'].items():
            #         text = vector_data['metadata'].get('text', '')
            #         if text:
            #             self.documents.append(text)
            #             self.metadata.append({
            #                 'doc_id': doc_id,
            #                 'source': 'pinecone',
            #                 'category': vector_data['metadata'].get('category', 'unknown')
            #             })
            #             count += 1

            self.source_counts['pinecone'] = count
            return count

        except Exception as e:
            logger.error(f"[BM25] Failed to load from Pinecone: {e}")
            return 0

    def load_from_files(self, file_paths: List[str]) -> int:
        """
        Load documents from text files

        Args:
            file_paths: List of file paths to load

        Returns:
            Number of documents loaded
        """
        count = 0

        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    logger.warning(f"[BM25] File not found: {file_path}")
                    continue

                logger.info(f"[BM25] Loading from file: {file_path}")

                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

                if text.strip():
                    self.documents.append(text)
                    self.metadata.append({
                        'doc_id': f"file_{count}",
                        'source': 'file',
                        'file_path': file_path
                    })
                    count += 1

            except Exception as e:
                logger.error(f"[BM25] Failed to load {file_path}: {e}")

        self.source_counts['files'] = count
        logger.info(f"[BM25] ✓ Loaded {count} documents from files")
        return count

    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for BM25 indexing

        Args:
            text: Raw text

        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters but keep alphanumeric and spaces
        # Keep underscores for identifiers like TOKEN_EXPIRATION
        text = re.sub(r'[^\w\s]', ' ', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Preprocess
        text = self.preprocess_text(text)

        # Simple whitespace tokenization
        tokens = text.split()

        # Remove very short tokens (length < 2)
        tokens = [t for t in tokens if len(t) >= 2]

        return tokens

    def build_index(self) -> Tuple[BM25Okapi, List[str], List[Dict]]:
        """
        Build BM25 index from loaded documents

        Returns:
            Tuple of (bm25_index, documents, metadata)
        """
        if not self.documents:
            raise ValueError("No documents loaded. Call load_from_* methods first.")

        logger.info(f"[BM25] Building BM25 index from {len(self.documents)} documents...")

        # Tokenize all documents
        tokenized_docs = []
        for i, doc in enumerate(self.documents):
            tokens = self.tokenize(doc)
            tokenized_docs.append(tokens)

            if (i + 1) % 100 == 0:
                logger.info(f"[BM25] Tokenized {i + 1}/{len(self.documents)} documents...")

        # Build BM25 index
        logger.info("[BM25] Creating BM25Okapi index...")
        bm25 = BM25Okapi(tokenized_docs)

        logger.info("[BM25] ✓ BM25 index built successfully")
        logger.info(f"[BM25] Index statistics:")
        logger.info(f"[BM25]   - Total documents: {len(self.documents)}")
        logger.info(f"[BM25]   - MongoDB: {self.source_counts['mongodb']}")
        logger.info(f"[BM25]   - Pinecone: {self.source_counts['pinecone']}")
        logger.info(f"[BM25]   - Files: {self.source_counts['files']}")

        return bm25, self.documents, self.metadata

    def save_index(
        self,
        bm25: BM25Okapi,
        documents: List[str],
        metadata: List[Dict],
        output_path: str
    ):
        """
        Save BM25 index to pickle file

        Args:
            bm25: BM25Okapi index
            documents: List of document texts
            metadata: List of metadata dicts
            output_path: Path to save pickle file
        """
        logger.info(f"[BM25] Saving index to {output_path}...")

        # Create directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Prepare data
        index_data = {
            'bm25': bm25,
            'documents': documents,
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
            'version': '1.0.0',
            'source_counts': self.source_counts
        }

        # Save as pickle
        with open(output_path, 'wb') as f:
            pickle.dump(index_data, f, protocol=pickle.HIGHEST_PROTOCOL)

        # Get file size
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"[BM25] ✓ Index saved successfully ({size_mb:.2f} MB)")

    def load_existing_index(self, index_path: str) -> Tuple[BM25Okapi, List[str], List[Dict]]:
        """
        Load existing BM25 index from pickle file

        Args:
            index_path: Path to pickle file

        Returns:
            Tuple of (bm25_index, documents, metadata)
        """
        logger.info(f"[BM25] Loading existing index from {index_path}...")

        with open(index_path, 'rb') as f:
            index_data = pickle.load(f)

        bm25 = index_data['bm25']
        documents = index_data['documents']
        metadata = index_data['metadata']

        logger.info(f"[BM25] ✓ Loaded index with {len(documents)} documents")
        logger.info(f"[BM25]   Created: {index_data.get('created_at', 'unknown')}")
        logger.info(f"[BM25]   Version: {index_data.get('version', 'unknown')}")

        return bm25, documents, metadata

    def incremental_update(
        self,
        existing_index_path: str,
        output_path: str,
        load_new_docs: bool = True
    ):
        """
        Incrementally update existing BM25 index with new documents

        Args:
            existing_index_path: Path to existing index
            output_path: Path to save updated index
            load_new_docs: Whether to load new documents from sources
        """
        logger.info("[BM25] Starting incremental update...")

        # Load existing index
        old_bm25, old_documents, old_metadata = self.load_existing_index(existing_index_path)

        # Store old documents
        self.documents = old_documents.copy()
        self.metadata = old_metadata.copy()

        old_count = len(old_documents)
        logger.info(f"[BM25] Existing index has {old_count} documents")

        # Load new documents
        if load_new_docs:
            # Get existing doc IDs to avoid duplicates
            existing_ids = set(m['doc_id'] for m in old_metadata)

            # Save current count
            before_count = len(self.documents)

            # Load from MongoDB (only new ones)
            self.load_from_mongodb()

            # Remove duplicates
            new_docs = []
            new_metadata = []
            for i in range(before_count, len(self.documents)):
                doc_id = self.metadata[i]['doc_id']
                if doc_id not in existing_ids:
                    new_docs.append(self.documents[i])
                    new_metadata.append(self.metadata[i])
                    existing_ids.add(doc_id)

            # Update documents with non-duplicates
            self.documents = old_documents + new_docs
            self.metadata = old_metadata + new_metadata

            new_count = len(new_docs)
            logger.info(f"[BM25] Added {new_count} new documents (skipped duplicates)")

        # Rebuild index with all documents
        logger.info("[BM25] Rebuilding index with all documents...")
        bm25, documents, metadata = self.build_index()

        # Save updated index
        self.save_index(bm25, documents, metadata, output_path)

        logger.info(f"[BM25] ✓ Incremental update complete: {old_count} → {len(documents)} documents")


def main():
    """
    Main function for building BM25 index
    """
    parser = argparse.ArgumentParser(description='Build BM25 index for Fusion RAG')
    parser.add_argument(
        '--output',
        default='implementation/data/bm25_index.pkl',
        help='Output path for BM25 index (default: implementation/data/bm25_index.pkl)'
    )
    parser.add_argument(
        '--mongodb-limit',
        type=int,
        default=None,
        help='Limit number of MongoDB documents (default: all)'
    )
    parser.add_argument(
        '--incremental',
        action='store_true',
        help='Perform incremental update of existing index'
    )
    parser.add_argument(
        '--files',
        nargs='*',
        help='Additional text files to include'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("BM25 Index Builder - Task 0-ARCH.25")
    print("=" * 60)
    print()

    # Initialize builder
    builder = BM25IndexBuilder()

    if args.incremental:
        # Incremental update
        if not os.path.exists(args.output):
            logger.error(f"Cannot perform incremental update - index not found: {args.output}")
            sys.exit(1)

        builder.incremental_update(
            existing_index_path=args.output,
            output_path=args.output,
            load_new_docs=True
        )

    else:
        # Full rebuild
        # Load from MongoDB
        mongo_count = builder.load_from_mongodb(limit=args.mongodb_limit)

        # Load from Pinecone (if available)
        pinecone_count = builder.load_from_pinecone()

        # Load from files
        if args.files:
            file_count = builder.load_from_files(args.files)

        # Build index
        if not builder.documents:
            logger.error("[BM25] No documents loaded - nothing to index")
            sys.exit(1)

        bm25, documents, metadata = builder.build_index()

        # Save index
        builder.save_index(bm25, documents, metadata, args.output)

    print()
    print("=" * 60)
    print("BM25 Index Build Complete!")
    print("=" * 60)
    print()
    print(f"Index saved to: {args.output}")
    print(f"Total documents: {len(builder.documents)}")
    print(f"  - MongoDB: {builder.source_counts['mongodb']}")
    print(f"  - Pinecone: {builder.source_counts['pinecone']}")
    print(f"  - Files: {builder.source_counts['files']}")
    print()
    print("You can now use this index with FusionRAG:")
    print(f"  fusion_rag = FusionRAG(bm25_index_path='{args.output}')")
    print()


if __name__ == '__main__':
    main()
