"""
Hybrid Search Service - Phase 3
Combines BM25 (keyword matching) with Semantic Search (Pinecone)

This service provides:
- BM25 keyword search for exact error codes (E500, TimeoutError, etc.)
- Semantic search via Pinecone for descriptive queries
- Hybrid ranking that combines both scores with configurable weights

Author: AI System
Phase: 3 (Tasks 3.1-3.9)
Port: 5005
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv
import logging
import pickle
from rank_bm25 import BM25Okapi
from typing import List, Dict, Optional, Tuple
import numpy as np
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================

# BM25 Index Configuration
BM25_INDEX_PATH = os.path.join(os.path.dirname(__file__), 'bm25_index.pkl')
BM25_DOCUMENTS_PATH = os.path.join(os.path.dirname(__file__), 'bm25_documents.pkl')

# Hybrid Search Weights
# These weights determine how much each method contributes to final score
BM25_WEIGHT = 0.4  # 40% weight to keyword matching
SEMANTIC_WEIGHT = 0.6  # 60% weight to semantic similarity

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_KNOWLEDGE_INDEX = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')
PINECONE_FAILURES_INDEX = os.getenv('PINECONE_FAILURES_INDEX', 'ddn-error-library')

# OpenAI Configuration for embeddings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

bm25_index = None
bm25_documents = None
pinecone_client = None
knowledge_index = None
failures_index = None
openai_client = None

# ============================================================================
# INITIALIZATION
# ============================================================================

def initialize_bm25():
    """Load BM25 index and documents from disk"""
    global bm25_index, bm25_documents

    try:
        if not os.path.exists(BM25_INDEX_PATH) or not os.path.exists(BM25_DOCUMENTS_PATH):
            logger.warning(f"⚠️  BM25 index not found at {BM25_INDEX_PATH}")
            logger.warning("   Run build_bm25_index.py first to create the index")
            return False

        with open(BM25_INDEX_PATH, 'rb') as f:
            bm25_index = pickle.load(f)

        with open(BM25_DOCUMENTS_PATH, 'rb') as f:
            bm25_documents = pickle.load(f)

        logger.info(f"✅ BM25 index loaded successfully")
        logger.info(f"   Total documents: {len(bm25_documents)}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load BM25 index: {e}")
        return False

def initialize_pinecone():
    """Initialize Pinecone client and indexes"""
    global pinecone_client, knowledge_index, failures_index

    try:
        if not PINECONE_API_KEY:
            logger.error("❌ PINECONE_API_KEY not found in .env")
            return False

        # Initialize Pinecone
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

        # Connect to indexes
        knowledge_index = pinecone_client.Index(PINECONE_KNOWLEDGE_INDEX)
        failures_index = pinecone_client.Index(PINECONE_FAILURES_INDEX)

        logger.info(f"✅ Pinecone initialized successfully")
        logger.info(f"   Knowledge Index: {PINECONE_KNOWLEDGE_INDEX}")
        logger.info(f"   Failures Index: {PINECONE_FAILURES_INDEX}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Pinecone: {e}")
        return False

def initialize_openai():
    """Initialize OpenAI client for embeddings"""
    global openai_client

    try:
        if not OPENAI_API_KEY:
            logger.error("❌ OPENAI_API_KEY not found in .env")
            return False

        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info(f"✅ OpenAI client initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI: {e}")
        return False

def startup_checks():
    """Run all initialization checks on startup"""
    logger.info("🚀 Starting Hybrid Search Service...")
    logger.info(f"   Port: 5005")
    logger.info(f"   BM25 Weight: {BM25_WEIGHT}")
    logger.info(f"   Semantic Weight: {SEMANTIC_WEIGHT}")

    success = True
    success &= initialize_bm25()
    success &= initialize_pinecone()
    success &= initialize_openai()

    if success:
        logger.info("✅ All services initialized successfully")
    else:
        logger.warning("⚠️  Some services failed to initialize")
        logger.warning("   Service will start with limited functionality")

    return success

# ============================================================================
# BM25 SEARCH
# ============================================================================

def bm25_search(query: str, top_k: int = 50) -> List[Dict]:
    """
    Perform BM25 keyword search

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        List of documents with BM25 scores
    """
    if bm25_index is None or bm25_documents is None:
        logger.warning("BM25 index not loaded, returning empty results")
        return []

    try:
        # Tokenize query (simple split - you can use more sophisticated tokenization)
        query_tokens = query.lower().split()

        # Get BM25 scores
        scores = bm25_index.get_scores(query_tokens)

        # Get top-k results
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include results with positive scores
                results.append({
                    'document': bm25_documents[idx],
                    'bm25_score': float(scores[idx]),
                    'source': 'bm25'
                })

        logger.info(f"   BM25 found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in BM25 search: {e}")
        return []

# ============================================================================
# SEMANTIC SEARCH
# ============================================================================

def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI"""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        return None

def semantic_search(query: str, top_k: int = 50) -> List[Dict]:
    """
    Perform semantic search using Pinecone

    Args:
        query: Search query
        top_k: Number of results to return

    Returns:
        List of documents with semantic similarity scores
    """
    if knowledge_index is None or failures_index is None:
        logger.warning("Pinecone not initialized, returning empty results")
        return []

    try:
        # Generate query embedding
        query_embedding = get_embedding(query)
        if query_embedding is None:
            return []

        # Search both indexes
        knowledge_results = knowledge_index.query(
            vector=query_embedding,
            top_k=top_k // 2,
            include_metadata=True
        )

        failures_results = failures_index.query(
            vector=query_embedding,
            top_k=top_k // 2,
            include_metadata=True
        )

        # Combine results
        results = []

        for match in knowledge_results.matches:
            results.append({
                'document': {
                    'id': match.id,
                    'metadata': match.metadata,
                    'source_index': 'knowledge'
                },
                'semantic_score': float(match.score),
                'source': 'semantic'
            })

        for match in failures_results.matches:
            results.append({
                'document': {
                    'id': match.id,
                    'metadata': match.metadata,
                    'source_index': 'failures'
                },
                'semantic_score': float(match.score),
                'source': 'semantic'
            })

        logger.info(f"   Semantic found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return []

# ============================================================================
# HYBRID SEARCH
# ============================================================================

def normalize_scores(scores: List[float]) -> List[float]:
    """Normalize scores to 0-1 range using min-max normalization"""
    if not scores or len(scores) == 0:
        return []

    min_score = min(scores)
    max_score = max(scores)

    if max_score == min_score:
        return [1.0] * len(scores)

    return [(s - min_score) / (max_score - min_score) for s in scores]

def hybrid_search(
    query: str,
    top_k: int = 10,
    bm25_weight: float = BM25_WEIGHT,
    semantic_weight: float = SEMANTIC_WEIGHT
) -> List[Dict]:
    """
    Perform hybrid search combining BM25 and semantic search

    Args:
        query: Search query
        top_k: Number of final results to return
        bm25_weight: Weight for BM25 scores (default 0.4)
        semantic_weight: Weight for semantic scores (default 0.6)

    Returns:
        List of documents ranked by hybrid score
    """
    logger.info(f"🔍 Hybrid search for query: '{query}'")
    logger.info(f"   Requesting top {top_k} results")

    # Get results from both methods (request more to ensure good coverage)
    bm25_results = bm25_search(query, top_k=50)
    semantic_results = semantic_search(query, top_k=50)

    # Create a dictionary to merge results by document ID
    merged_results = {}

    # Process BM25 results
    bm25_scores = [r['bm25_score'] for r in bm25_results]
    normalized_bm25 = normalize_scores(bm25_scores)

    for i, result in enumerate(bm25_results):
        doc_id = result['document'].get('id') or result['document'].get('build_id') or str(i)
        merged_results[doc_id] = {
            'document': result['document'],
            'bm25_score': normalized_bm25[i],
            'semantic_score': 0.0,
            'hybrid_score': 0.0
        }

    # Process semantic results
    semantic_scores = [r['semantic_score'] for r in semantic_results]
    normalized_semantic = normalize_scores(semantic_scores)

    for i, result in enumerate(semantic_results):
        doc_id = result['document'].get('id') or result['document'].get('build_id') or f"semantic_{i}"

        if doc_id in merged_results:
            # Document found in both - update semantic score
            merged_results[doc_id]['semantic_score'] = normalized_semantic[i]
        else:
            # Document only in semantic results
            merged_results[doc_id] = {
                'document': result['document'],
                'bm25_score': 0.0,
                'semantic_score': normalized_semantic[i],
                'hybrid_score': 0.0
            }

    # Calculate hybrid scores
    for doc_id in merged_results:
        merged_results[doc_id]['hybrid_score'] = (
            bm25_weight * merged_results[doc_id]['bm25_score'] +
            semantic_weight * merged_results[doc_id]['semantic_score']
        )

    # Sort by hybrid score and return top-k
    sorted_results = sorted(
        merged_results.values(),
        key=lambda x: x['hybrid_score'],
        reverse=True
    )[:top_k]

    logger.info(f"✅ Hybrid search complete: {len(sorted_results)} results")
    return sorted_results

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        'status': 'running',
        'service': 'Hybrid Search Service',
        'port': 5005,
        'bm25_loaded': bm25_index is not None,
        'pinecone_connected': knowledge_index is not None,
        'openai_connected': openai_client is not None
    }

    if bm25_documents:
        status['bm25_document_count'] = len(bm25_documents)

    return jsonify(status)

@app.route('/hybrid-search', methods=['POST'])
def hybrid_search_endpoint():
    """
    Hybrid search endpoint

    Request body:
    {
        "query": "E500 TimeoutError",
        "top_k": 10,
        "bm25_weight": 0.4,
        "semantic_weight": 0.6
    }

    Response:
    {
        "query": "E500 TimeoutError",
        "results": [
            {
                "document": {...},
                "bm25_score": 0.85,
                "semantic_score": 0.75,
                "hybrid_score": 0.79
            }
        ],
        "total_results": 10
    }
    """
    try:
        data = request.json

        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data['query']
        top_k = data.get('top_k', 10)
        bm25_weight = data.get('bm25_weight', BM25_WEIGHT)
        semantic_weight = data.get('semantic_weight', SEMANTIC_WEIGHT)

        # Perform hybrid search
        results = hybrid_search(
            query=query,
            top_k=top_k,
            bm25_weight=bm25_weight,
            semantic_weight=semantic_weight
        )

        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results),
            'weights': {
                'bm25': bm25_weight,
                'semantic': semantic_weight
            }
        })
    except Exception as e:
        logger.error(f"Error in hybrid search endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/bm25-search', methods=['POST'])
def bm25_search_endpoint():
    """BM25-only search endpoint for testing"""
    try:
        data = request.json
        query = data.get('query')
        top_k = data.get('top_k', 10)

        if not query:
            return jsonify({'error': 'Missing query parameter'}), 400

        results = bm25_search(query, top_k)

        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results)
        })
    except Exception as e:
        logger.error(f"Error in BM25 search endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/semantic-search', methods=['POST'])
def semantic_search_endpoint():
    """Semantic-only search endpoint for testing"""
    try:
        data = request.json
        query = data.get('query')
        top_k = data.get('top_k', 10)

        if not query:
            return jsonify({'error': 'Missing query parameter'}), 400

        results = semantic_search(query, top_k)

        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results)
        })
    except Exception as e:
        logger.error(f"Error in semantic search endpoint: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reload-bm25', methods=['POST'])
def reload_bm25_index():
    """Reload BM25 index from disk (useful after rebuilding)"""
    try:
        success = initialize_bm25()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'BM25 index reloaded successfully',
                'document_count': len(bm25_documents) if bm25_documents else 0
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to reload BM25 index'
            }), 500
    except Exception as e:
        logger.error(f"Error reloading BM25 index: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Run startup checks
    startup_checks()

    # Start Flask server
    port = int(os.getenv('HYBRID_SEARCH_PORT', 5005))
    logger.info(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
