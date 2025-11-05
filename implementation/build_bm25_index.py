"""
Build BM25 Index - Phase 3
Builds BM25 keyword search index from PostgreSQL data

Author: AI System
Phase: 3 (Task 3.2)
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
import pickle
from rank_bm25 import BM25Okapi
from typing import List, Dict
import re

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'ddn_ai_analysis')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

OUTPUT_DIR = os.path.dirname(__file__)
BM25_INDEX_PATH = os.path.join(OUTPUT_DIR, 'bm25_index.pkl')
BM25_DOCUMENTS_PATH = os.path.join(OUTPUT_DIR, 'bm25_documents.pkl')

def connect_to_postgres():
    """Connect to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST, port=POSTGRES_PORT, database=POSTGRES_DB,
            user=POSTGRES_USER, password=POSTGRES_PASSWORD
        )
        logger.info(f"Connected to PostgreSQL: {POSTGRES_DB}")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect: {e}")
        return None

def fetch_records(conn) -> List[Dict]:
    """Fetch failure analysis records"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id, build_id, error_category, root_cause,
                   fix_recommendation, confidence_score, consecutive_failures
            FROM failure_analysis ORDER BY created_at DESC
        """)
        records = cursor.fetchall()
        cursor.close()
        logger.info(f"Fetched {len(records)} records")
        return records
    except Exception as e:
        logger.error(f"Error fetching records: {e}")
        return []

def tokenize(text: str) -> List[str]:
    """Tokenize text preserving error codes"""
    if not text:
        return []
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s_-]', ' ', text)
    tokens = [t for t in text.split() if len(t) >= 2]
    return tokens

def create_document(record: Dict) -> Dict:
    """Create searchable document"""
    parts = []
    for field in ['error_category', 'root_cause', 'fix_recommendation', 'build_id']:
        if record.get(field):
            parts.append(str(record[field]))

    searchable_text = ' '.join(parts)
    tokens = tokenize(searchable_text)

    return {
        'id': record.get('id'),
        'build_id': record.get('build_id'),
        'error_category': record.get('error_category'),
        'root_cause': record.get('root_cause'),
        'fix_recommendation': record.get('fix_recommendation'),
        'confidence_score': record.get('confidence_score'),
        'tokens': tokens
    }

def build_index(documents: List[Dict]):
    """Build BM25 index"""
    logger.info(f"Building BM25 index from {len(documents)} documents")
    tokenized_corpus = [doc['tokens'] for doc in documents]
    bm25_index = BM25Okapi(tokenized_corpus)
    logger.info("BM25 index built successfully")
    return bm25_index

def save_index(bm25_index, documents):
    """Save index to disk"""
    with open(BM25_INDEX_PATH, 'wb') as f:
        pickle.dump(bm25_index, f)
    with open(BM25_DOCUMENTS_PATH, 'wb') as f:
        pickle.dump(documents, f)
    logger.info(f"Index saved to {BM25_INDEX_PATH}")
    logger.info(f"Documents saved to {BM25_DOCUMENTS_PATH}")

def main():
    logger.info("=" * 60)
    logger.info("BM25 Index Builder - Phase 3")
    logger.info("=" * 60)

    conn = connect_to_postgres()
    if not conn:
        return False

    try:
        records = fetch_records(conn)
        if not records:
            logger.warning("No records found")
            return False

        documents = [create_document(r) for r in records]
        logger.info(f"Created {len(documents)} searchable documents")

        bm25_index = build_index(documents)
        save_index(bm25_index, documents)

        logger.info("=" * 60)
        logger.info("BM25 INDEX BUILD COMPLETE")
        logger.info(f"Total documents: {len(documents)}")
        logger.info("=" * 60)
        return True
    finally:
        conn.close()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
