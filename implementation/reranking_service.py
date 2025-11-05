"""
Re-Ranking Service (Phase 2)

Standalone Flask service for re-ranking RAG retrieval results using CrossEncoder.

Architecture:
    Query + Candidates (k=50) → CrossEncoder → Top Results (k=5)

Purpose:
    - Improve retrieval precision by re-ranking initial candidates
    - Uses ms-marco-MiniLM-L-6-v2 cross-encoder model
    - Assigns rerank_score to each candidate
    - Returns top-k most relevant results

Endpoints:
    - POST /rerank - Re-rank candidates
    - GET /health - Health check
    - GET /model-info - Get model information

Author: DDN AI Analysis System
Date: 2025-11-03
Version: 1.0.0
Phase: 2 (Tasks 2.1-2.3)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import time

# Import CrossEncoder for re-ranking
try:
    from sentence_transformers import CrossEncoder
    CROSSENCODER_AVAILABLE = True
except ImportError:
    CROSSENCODER_AVAILABLE = False
    logging.error("❌ sentence-transformers not installed")
    logging.error("   Install with: pip install sentence-transformers")

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
CORS(app)  # Enable CORS for cross-origin requests

# Configuration
PORT = int(os.getenv('RERANKING_SERVICE_PORT', 5009))  # Using 5009 to avoid conflict
MODEL_NAME = os.getenv('RERANKING_MODEL', 'cross-encoder/ms-marco-MiniLM-L-6-v2')
MAX_TEXT_LENGTH = int(os.getenv('RERANKING_MAX_TEXT_LENGTH', 512))

# Global model instance
cross_encoder = None


# ============================================================================
# MODEL INITIALIZATION
# ============================================================================

def initialize_model():
    """
    Initialize CrossEncoder model for re-ranking

    Loads the ms-marco-MiniLM-L-6-v2 model which is trained on MS MARCO
    passage ranking dataset. This model is optimized for re-ranking tasks.

    Returns:
        CrossEncoder instance or None if initialization fails
    """
    global cross_encoder

    if not CROSSENCODER_AVAILABLE:
        logger.error("❌ CrossEncoder not available - sentence-transformers not installed")
        return None

    try:
        logger.info(f"🚀 Loading CrossEncoder model: {MODEL_NAME}")
        start_time = time.time()

        cross_encoder = CrossEncoder(MODEL_NAME)

        elapsed = time.time() - start_time
        logger.info(f"✅ CrossEncoder model loaded successfully in {elapsed:.2f}s")
        logger.info(f"   Model: {MODEL_NAME}")
        logger.info(f"   Max text length: {MAX_TEXT_LENGTH} chars")

        return cross_encoder

    except Exception as e:
        logger.error(f"❌ Failed to load CrossEncoder model: {e}")
        return None


# ============================================================================
# RE-RANKING LOGIC
# ============================================================================

def rerank_candidates(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Re-rank candidates using CrossEncoder

    Args:
        query: User query string (error message)
        candidates: List of candidate documents from RAG retrieval
                   Each candidate should have 'text' or 'content' field
        top_k: Number of top documents to return (default: 5)

    Returns:
        Top-k candidates sorted by rerank_score (descending)
        Each candidate will have 'rerank_score' field added

    Example:
        >>> candidates = [
        ...     {'text': 'TimeoutError in HA tests', 'score': 0.85},
        ...     {'text': 'Connection refused', 'score': 0.82}
        ... ]
        >>> results = rerank_candidates("timeout error", candidates, top_k=1)
        >>> results[0]['rerank_score']  # Higher score for better match
        0.94
    """
    if cross_encoder is None:
        logger.error("❌ CrossEncoder not initialized - returning original candidates")
        return candidates[:top_k]

    if not candidates:
        logger.warning("⚠️  No candidates provided for re-ranking")
        return []

    try:
        start_time = time.time()

        # Prepare query-document pairs
        pairs = []
        for candidate in candidates:
            # Extract text from candidate
            text = candidate.get('text', '')
            if not text:
                # Try alternative fields
                text = candidate.get('content', '')
            if not text:
                # Try metadata fields
                metadata = candidate.get('metadata', {})
                text = metadata.get('error_message', '') or metadata.get('root_cause', '')

            # Limit text length for efficiency
            text = text[:MAX_TEXT_LENGTH]
            pairs.append((query, text))

        # Score all pairs with CrossEncoder
        logger.info(f"🔄 Re-ranking {len(candidates)} candidates...")
        scores = cross_encoder.predict(pairs)

        # Combine candidates with scores
        candidates_with_scores = []
        for i, candidate in enumerate(candidates):
            candidate_copy = candidate.copy()
            candidate_copy['rerank_score'] = float(scores[i])
            candidates_with_scores.append(candidate_copy)

        # Sort by rerank score (descending)
        ranked_candidates = sorted(
            candidates_with_scores,
            key=lambda x: x['rerank_score'],
            reverse=True
        )

        # Take top-k
        top_candidates = ranked_candidates[:top_k]

        elapsed = time.time() - start_time
        logger.info(f"✅ Re-ranked {len(candidates)} candidates → top {len(top_candidates)} in {elapsed:.3f}s")

        # Log score distribution
        if top_candidates:
            top_score = top_candidates[0]['rerank_score']
            bottom_score = top_candidates[-1]['rerank_score']
            logger.info(f"   Score range: {bottom_score:.4f} - {top_score:.4f}")

        return top_candidates

    except Exception as e:
        logger.error(f"❌ Re-ranking failed: {e}")
        # Fall back to original candidates
        return candidates[:top_k]


# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint

    Returns:
        {
            "status": "healthy" | "degraded",
            "service": "Re-Ranking Service",
            "version": "1.0.0",
            "model_loaded": true | false,
            "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2"
        }
    """
    status = "healthy" if cross_encoder is not None else "degraded"

    return jsonify({
        "status": status,
        "service": "Re-Ranking Service",
        "version": "1.0.0",
        "model_loaded": cross_encoder is not None,
        "model_name": MODEL_NAME
    }), 200 if status == "healthy" else 503


@app.route('/model-info', methods=['GET'])
def model_info():
    """
    Get model information

    Returns:
        {
            "model_name": "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "model_loaded": true,
            "max_text_length": 512,
            "description": "MS MARCO passage ranking model"
        }
    """
    return jsonify({
        "model_name": MODEL_NAME,
        "model_loaded": cross_encoder is not None,
        "max_text_length": MAX_TEXT_LENGTH,
        "description": "MS MARCO passage ranking model for re-ranking retrieval results"
    })


@app.route('/rerank', methods=['POST'])
def rerank_endpoint():
    """
    Re-rank candidates endpoint (Task 2.1)

    Request:
        POST /rerank
        {
            "query": "TimeoutError in HA tests",
            "candidates": [
                {
                    "text": "Error message text",
                    "score": 0.85,
                    "metadata": {...}
                },
                ...
            ],
            "top_k": 5  // optional, default: 5
        }

    Response:
        {
            "success": true,
            "query": "TimeoutError in HA tests",
            "total_candidates": 50,
            "reranked_count": 5,
            "results": [
                {
                    "text": "...",
                    "score": 0.85,  // original score
                    "rerank_score": 0.94,  // new score
                    "metadata": {...}
                },
                ...
            ],
            "processing_time_ms": 123.45
        }

    Error Response:
        {
            "success": false,
            "error": "Error message",
            "details": "Detailed error description"
        }
    """
    try:
        start_time = time.time()

        # Validate request
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 400

        data = request.json

        # Extract parameters
        query = data.get('query', '')
        candidates = data.get('candidates', [])
        top_k = data.get('top_k', 5)

        # Validate parameters
        if not query:
            return jsonify({
                "success": False,
                "error": "Missing required field: query"
            }), 400

        if not candidates:
            return jsonify({
                "success": False,
                "error": "Missing required field: candidates"
            }), 400

        if not isinstance(candidates, list):
            return jsonify({
                "success": False,
                "error": "candidates must be a list"
            }), 400

        if not isinstance(top_k, int) or top_k < 1:
            return jsonify({
                "success": False,
                "error": "top_k must be a positive integer"
            }), 400

        # Check if model is loaded
        if cross_encoder is None:
            return jsonify({
                "success": False,
                "error": "CrossEncoder model not loaded",
                "details": "Re-ranking service is not available"
            }), 503

        # Perform re-ranking
        logger.info(f"📥 Re-rank request: query='{query[:50]}...', candidates={len(candidates)}, top_k={top_k}")

        reranked_results = rerank_candidates(query, candidates, top_k)

        elapsed_ms = (time.time() - start_time) * 1000

        return jsonify({
            "success": True,
            "query": query,
            "total_candidates": len(candidates),
            "reranked_count": len(reranked_results),
            "results": reranked_results,
            "processing_time_ms": round(elapsed_ms, 2)
        }), 200

    except Exception as e:
        logger.error(f"❌ Re-ranking endpoint error: {e}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "details": str(e)
        }), 500


# ============================================================================
# STARTUP & MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("🚀 Starting Re-Ranking Service")
    logger.info("=" * 80)
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Model: {MODEL_NAME}")
    logger.info(f"   Max text length: {MAX_TEXT_LENGTH}")
    logger.info("")

    # Initialize model
    model = initialize_model()

    if model is None:
        logger.error("=" * 80)
        logger.error("❌ FAILED TO START: Model initialization failed")
        logger.error("=" * 80)
        logger.error("")
        logger.error("Troubleshooting:")
        logger.error("1. Install sentence-transformers: pip install sentence-transformers")
        logger.error("2. Verify internet connection (model downloads on first run)")
        logger.error("3. Check disk space (~200MB needed for model)")
        logger.error("")
        sys.exit(1)

    logger.info("=" * 80)
    logger.info("✅ Re-Ranking Service is ready!")
    logger.info("=" * 80)
    logger.info("")
    logger.info("Endpoints:")
    logger.info(f"   POST http://localhost:{PORT}/rerank       - Re-rank candidates")
    logger.info(f"   GET  http://localhost:{PORT}/health       - Health check")
    logger.info(f"   GET  http://localhost:{PORT}/model-info   - Model information")
    logger.info("")

    # Start Flask server
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=False  # Set to False for production
    )
