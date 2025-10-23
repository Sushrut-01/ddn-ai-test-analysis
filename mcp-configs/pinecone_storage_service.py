"""
Pinecone Storage Service for DDN AI Test Failure Analysis
Stores error solutions as vector embeddings for RAG (Retrieval-Augmented Generation)

This service enables:
1. Storing new error solutions with vector embeddings
2. Searching for similar past errors
3. Updating success rates based on usage feedback
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import os
from dotenv import load_dotenv
import hashlib

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX", "ddn-error-solutions")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"  # OpenAI's latest embedding model
EMBEDDING_DIMENSIONS = 1536  # Dimensions for text-embedding-3-small

# Global clients
pinecone_client = None
openai_client = None
index = None

def initialize_pinecone():
    """Initialize Pinecone connection and index"""
    global pinecone_client, index

    try:
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

        # Check if index exists
        existing_indexes = pinecone_client.list_indexes()

        if PINECONE_INDEX_NAME not in [idx.name for idx in existing_indexes]:
            logger.info(f"📊 Creating new Pinecone index: {PINECONE_INDEX_NAME}")

            pinecone_client.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=EMBEDDING_DIMENSIONS,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )
            logger.info("✅ Pinecone index created")
        else:
            logger.info(f"✅ Pinecone index '{PINECONE_INDEX_NAME}' already exists")

        # Connect to index
        index = pinecone_client.Index(PINECONE_INDEX_NAME)
        logger.info(f"✅ Connected to Pinecone index")

        return True

    except Exception as e:
        logger.error(f"❌ Pinecone initialization failed: {e}")
        return False


def initialize_openai():
    """Initialize OpenAI client"""
    global openai_client

    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI client initialized")
        return True
    except Exception as e:
        logger.error(f"❌ OpenAI initialization failed: {e}")
        return False


def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector for text using OpenAI"""
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    except Exception as e:
        logger.error(f"❌ Error generating embedding: {e}")
        raise


def generate_vector_id(text: str, build_id: str = None) -> str:
    """Generate unique ID for vector"""
    if build_id:
        return f"{build_id}_{int(datetime.utcnow().timestamp())}"

    # Generate from text hash
    text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
    timestamp = int(datetime.utcnow().timestamp())
    return f"error_{text_hash}_{timestamp}"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    pinecone_status = index is not None
    openai_status = openai_client is not None

    return jsonify({
        "status": "healthy" if (pinecone_status and openai_status) else "degraded",
        "service": "Pinecone Storage Service",
        "version": "1.0.0",
        "pinecone_connected": pinecone_status,
        "openai_connected": openai_status,
        "index_name": PINECONE_INDEX_NAME
    }), 200


@app.route('/api/store-vector', methods=['POST'])
def store_vector():
    """
    Store error solution as vector embedding

    Request:
    {
        "id": "optional_custom_id",
        "text": "Error log or description",
        "metadata": {
            "build_id": "12345",
            "error_category": "CODE_ERROR",
            "root_cause": "...",
            "solution": "...",
            "confidence": 0.95,
            "success_rate": 0.0,
            "times_used": 0,
            "timestamp": "2025-01-15T10:00:00Z",
            "analysis_type": "CLAUDE_MCP",
            "priority": "HIGH"
        }
    }
    """
    try:
        data = request.get_json()

        if not data or 'text' not in data:
            return jsonify({
                "error": "Missing required field: text"
            }), 400

        text = data['text']
        metadata = data.get('metadata', {})
        vector_id = data.get('id') or generate_vector_id(text, metadata.get('build_id'))

        logger.info(f"📝 Storing vector: {vector_id}")

        # Generate embedding
        embedding = generate_embedding(text)

        # Prepare metadata (Pinecone requires all metadata to be simple types)
        pinecone_metadata = {
            "build_id": metadata.get("build_id", "unknown"),
            "error_category": metadata.get("error_category", "UNKNOWN"),
            "root_cause": metadata.get("root_cause", "")[:1000],  # Limit length
            "solution": metadata.get("solution", "")[:1000],
            "confidence": float(metadata.get("confidence", 0.0)),
            "success_rate": float(metadata.get("success_rate", 0.0)),
            "times_used": int(metadata.get("times_used", 0)),
            "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
            "analysis_type": metadata.get("analysis_type", ""),
            "priority": metadata.get("priority", "MEDIUM"),
            "text_preview": text[:200]  # Store preview for debugging
        }

        # Upsert to Pinecone
        index.upsert(
            vectors=[{
                "id": vector_id,
                "values": embedding,
                "metadata": pinecone_metadata
            }]
        )

        logger.info(f"✅ Vector stored successfully: {vector_id}")

        return jsonify({
            "success": True,
            "vector_id": vector_id,
            "dimensions": len(embedding),
            "metadata": pinecone_metadata
        }), 200

    except Exception as e:
        logger.error(f"❌ Error storing vector: {e}")
        return jsonify({
            "error": "Failed to store vector",
            "details": str(e)
        }), 500


@app.route('/api/search-similar', methods=['POST'])
def search_similar():
    """
    Search for similar errors using vector similarity

    Request:
    {
        "query": "Error log or description",
        "top_k": 5,
        "filter": {
            "error_category": "CODE_ERROR"
        },
        "min_confidence": 0.7
    }
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({
                "error": "Missing required field: query"
            }), 400

        query = data['query']
        top_k = data.get('top_k', 5)
        filter_dict = data.get('filter', {})
        min_confidence = data.get('min_confidence', 0.0)

        logger.info(f"🔍 Searching for similar errors (top_k={top_k})")

        # Generate query embedding
        query_embedding = generate_embedding(query)

        # Search Pinecone
        search_results = index.query(
            vector=query_embedding,
            top_k=top_k * 2,  # Get more, then filter
            include_metadata=True,
            filter=filter_dict if filter_dict else None
        )

        # Process and filter results
        matches = []
        for match in search_results.matches:
            metadata = match.metadata
            confidence = metadata.get('confidence', 0.0)

            # Filter by minimum confidence
            if confidence < min_confidence:
                continue

            matches.append({
                "id": match.id,
                "similarity_score": round(match.score, 4),
                "build_id": metadata.get("build_id"),
                "error_category": metadata.get("error_category"),
                "root_cause": metadata.get("root_cause"),
                "solution": metadata.get("solution"),
                "confidence": confidence,
                "success_rate": metadata.get("success_rate", 0.0),
                "times_used": metadata.get("times_used", 0),
                "timestamp": metadata.get("timestamp"),
                "analysis_type": metadata.get("analysis_type"),
                "priority": metadata.get("priority")
            })

            if len(matches) >= top_k:
                break

        logger.info(f"✅ Found {len(matches)} similar errors")

        return jsonify({
            "success": True,
            "query_preview": query[:100],
            "matches_found": len(matches),
            "matches": matches
        }), 200

    except Exception as e:
        logger.error(f"❌ Error searching similar: {e}")
        return jsonify({
            "error": "Search failed",
            "details": str(e)
        }), 500


@app.route('/api/update-feedback', methods=['POST'])
def update_feedback():
    """
    Update success rate and usage count for a solution

    Request:
    {
        "vector_id": "12345_1234567890",
        "success": true,
        "increment_usage": true
    }
    """
    try:
        data = request.get_json()

        if not data or 'vector_id' not in data:
            return jsonify({
                "error": "Missing required field: vector_id"
            }), 400

        vector_id = data['vector_id']
        success = data.get('success', True)
        increment_usage = data.get('increment_usage', True)

        logger.info(f"📊 Updating feedback for: {vector_id}")

        # Fetch current vector
        fetch_response = index.fetch(ids=[vector_id])

        if vector_id not in fetch_response.vectors:
            return jsonify({
                "error": f"Vector not found: {vector_id}"
            }), 404

        vector_data = fetch_response.vectors[vector_id]
        metadata = vector_data.metadata

        # Update metrics
        times_used = metadata.get('times_used', 0)
        success_rate = metadata.get('success_rate', 0.0)

        if increment_usage:
            times_used += 1

        if success:
            # Update success rate using moving average
            success_rate = ((success_rate * (times_used - 1)) + 1.0) / times_used
        else:
            success_rate = ((success_rate * (times_used - 1)) + 0.0) / times_used

        # Update metadata
        metadata['times_used'] = times_used
        metadata['success_rate'] = round(success_rate, 3)
        metadata['last_used'] = datetime.utcnow().isoformat()

        # Upsert updated vector
        index.upsert(
            vectors=[{
                "id": vector_id,
                "values": vector_data.values,
                "metadata": metadata
            }]
        )

        logger.info(f"✅ Feedback updated: times_used={times_used}, success_rate={success_rate:.2f}")

        return jsonify({
            "success": True,
            "vector_id": vector_id,
            "times_used": times_used,
            "success_rate": round(success_rate, 3)
        }), 200

    except Exception as e:
        logger.error(f"❌ Error updating feedback: {e}")
        return jsonify({
            "error": "Feedback update failed",
            "details": str(e)
        }), 500


@app.route('/api/get-stats', methods=['GET'])
def get_stats():
    """Get statistics about stored vectors"""
    try:
        # Get index stats
        stats = index.describe_index_stats()

        return jsonify({
            "success": True,
            "index_name": PINECONE_INDEX_NAME,
            "total_vectors": stats.total_vector_count,
            "dimensions": stats.dimension,
            "namespaces": stats.namespaces
        }), 200

    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return jsonify({
            "error": "Failed to get stats",
            "details": str(e)
        }), 500


@app.route('/api/delete-vector', methods=['DELETE'])
def delete_vector():
    """
    Delete a vector

    Request:
    {
        "vector_id": "12345_1234567890"
    }
    """
    try:
        data = request.get_json()

        if not data or 'vector_id' not in data:
            return jsonify({
                "error": "Missing required field: vector_id"
            }), 400

        vector_id = data['vector_id']

        logger.info(f"🗑️ Deleting vector: {vector_id}")

        index.delete(ids=[vector_id])

        logger.info(f"✅ Vector deleted: {vector_id}")

        return jsonify({
            "success": True,
            "vector_id": vector_id,
            "message": "Vector deleted successfully"
        }), 200

    except Exception as e:
        logger.error(f"❌ Error deleting vector: {e}")
        return jsonify({
            "error": "Delete failed",
            "details": str(e)
        }), 500


@app.route('/api/batch-store', methods=['POST'])
def batch_store():
    """
    Store multiple vectors at once

    Request:
    {
        "vectors": [
            {
                "text": "Error description",
                "metadata": {...}
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()

        if not data or 'vectors' not in data:
            return jsonify({
                "error": "Missing required field: vectors"
            }), 400

        vectors_data = data['vectors']

        logger.info(f"📦 Batch storing {len(vectors_data)} vectors")

        # Prepare vectors for upsert
        vectors_to_upsert = []

        for vec_data in vectors_data:
            text = vec_data.get('text')
            metadata = vec_data.get('metadata', {})

            if not text:
                continue

            vector_id = vec_data.get('id') or generate_vector_id(text, metadata.get('build_id'))
            embedding = generate_embedding(text)

            pinecone_metadata = {
                "build_id": metadata.get("build_id", "unknown"),
                "error_category": metadata.get("error_category", "UNKNOWN"),
                "root_cause": metadata.get("root_cause", "")[:1000],
                "solution": metadata.get("solution", "")[:1000],
                "confidence": float(metadata.get("confidence", 0.0)),
                "success_rate": float(metadata.get("success_rate", 0.0)),
                "times_used": int(metadata.get("times_used", 0)),
                "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
                "text_preview": text[:200]
            }

            vectors_to_upsert.append({
                "id": vector_id,
                "values": embedding,
                "metadata": pinecone_metadata
            })

        # Batch upsert
        index.upsert(vectors=vectors_to_upsert)

        logger.info(f"✅ Batch stored {len(vectors_to_upsert)} vectors")

        return jsonify({
            "success": True,
            "vectors_stored": len(vectors_to_upsert),
            "vector_ids": [v["id"] for v in vectors_to_upsert]
        }), 200

    except Exception as e:
        logger.error(f"❌ Error in batch store: {e}")
        return jsonify({
            "error": "Batch store failed",
            "details": str(e)
        }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting Pinecone Storage Service...")
    logger.info(f"📍 Server will run on: http://localhost:5003")
    logger.info(f"📍 Health Check: http://localhost:5003/health")

    # Initialize services
    openai_status = initialize_openai()
    pinecone_status = initialize_pinecone()

    if not openai_status:
        logger.error("❌ OpenAI initialization failed - service will not work!")
        logger.error("   Check OPENAI_API_KEY in .env file")

    if not pinecone_status:
        logger.error("❌ Pinecone initialization failed - service will not work!")
        logger.error("   Check PINECONE_API_KEY and PINECONE_INDEX in .env file")

    if openai_status and pinecone_status:
        logger.info("✅ All services initialized successfully")
        logger.info(f"📊 Index: {PINECONE_INDEX_NAME}")
        logger.info(f"🤖 Embedding Model: {EMBEDDING_MODEL}")
        logger.info(f"📐 Dimensions: {EMBEDDING_DIMENSIONS}")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        threaded=True
    )
