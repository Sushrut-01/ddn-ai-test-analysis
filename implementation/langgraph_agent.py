"""
DDN Test Failure Classification Agent - ReAct Implementation
Production-ready error analysis service with Agentic RAG

Task 0-ARCH.6: Refactored to use ReAct agent workflow
- Replaced linear workflow with iterative reasoning loops
- Added dynamic tool selection based on error category
- Integrated self-correction mechanism (Task 0-ARCH.5)
- Context-aware routing (80/20 rule for GitHub)

Previous: classify → rag_search → extract_files (LINEAR)
Current: ReAct loop with think/act/observe iterations (AGENTIC)
"""

from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
import logging
from typing import Dict, Optional
import redis
import hashlib
import json

# Add agents directory to path
agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
sys.path.insert(0, agents_dir)

# Import ReAct Agent (Task 0-ARCH.2, 0-ARCH.3, 0-ARCH.4, 0-ARCH.5)
from react_agent_service import ReActAgent, create_react_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Redis client (Task 1.2 - Phase 1)
redis_client = None
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    redis_db = int(os.getenv('REDIS_DB', 0))
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )
    # Test connection
    redis_client.ping()
    logger.info(f"✅ Redis client initialized: {redis_host}:{redis_port}/{redis_db}")
except Exception as e:
    logger.warning(f"⚠️  Redis not available: {e}")
    logger.warning("   Caching will be disabled")
    redis_client = None

# Initialize ReAct Agent (Task 0-ARCH.6)
react_agent = None

# ============================================================================
# REACT AGENT INITIALIZATION
# ============================================================================

def initialize_react_agent():
    """
    Initialize ReAct agent on startup

    The ReAct agent includes:
    - Task 0-ARCH.2: Core ReAct workflow (7 nodes)
    - Task 0-ARCH.3: Data-driven tool registry
    - Task 0-ARCH.4: Category-specific thought prompts
    - Task 0-ARCH.5: Self-correction mechanism with retry logic

    Returns:
        ReActAgent instance or None if initialization fails
    """
    try:
        logger.info("🚀 Initializing ReAct Agent...")
        agent = create_react_agent()
        logger.info("✅ ReAct Agent initialized successfully")
        logger.info("   - 7 workflow nodes: classify → reasoning → select_tool → execute_tool → observe → answer → verify")
        logger.info("   - Data-driven categories from Pinecone")
        logger.info("   - Self-correction with 3 retries per tool")
        logger.info("   - Context-aware routing (80/20 rule)")
        return agent
    except Exception as e:
        logger.error(f"❌ Failed to initialize ReAct Agent: {e}")
        return None

# ============================================================================
# REDIS CACHING HELPER FUNCTIONS (Task 1.3 - Phase 1)
# ============================================================================

def get_cache_key(error_log: str, error_message: str) -> str:
    """
    Generate a cache key from error log and message

    Uses SHA256 hash of concatenated error_log + error_message

    Args:
        error_log: Full error log text
        error_message: Error message summary

    Returns:
        str: Cache key in format "ddn:analysis:{hash}"
    """
    # Concatenate and normalize
    combined = f"{error_log}|{error_message}".strip().lower()

    # Generate SHA256 hash
    hash_obj = hashlib.sha256(combined.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()

    # Return prefixed key
    return f"ddn:analysis:{hash_hex}"


def get_from_cache(cache_key: str) -> Optional[Dict]:
    """
    Retrieve analysis result from Redis cache

    Args:
        cache_key: Cache key to retrieve

    Returns:
        Dict or None: Cached analysis result or None if not found/error
    """
    if redis_client is None:
        return None

    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            logger.info(f"✅ Cache HIT: {cache_key[:20]}...")
            return json.loads(cached_data)
        else:
            logger.info(f"❌ Cache MISS: {cache_key[:20]}...")
            return None
    except Exception as e:
        logger.warning(f"⚠️  Cache retrieval error: {e}")
        return None


def save_to_cache(cache_key: str, result: Dict, ttl_seconds: int = 3600) -> bool:
    """
    Save analysis result to Redis cache

    Args:
        cache_key: Cache key
        result: Analysis result dictionary
        ttl_seconds: Time to live in seconds (default: 1 hour)

    Returns:
        bool: True if saved successfully, False otherwise
    """
    if redis_client is None:
        return False

    try:
        # Serialize to JSON
        json_data = json.dumps(result)

        # Save with TTL
        redis_client.setex(cache_key, ttl_seconds, json_data)

        logger.info(f"💾 Cached result: {cache_key[:20]}... (TTL: {ttl_seconds}s)")
        return True
    except Exception as e:
        logger.warning(f"⚠️  Cache save error: {e}")
        return False


# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DDN LangGraph Classification Agent",
        "version": "1.0.0",
        "redis_available": redis_client is not None
    })


@app.route('/cache-stats', methods=['GET'])
def cache_stats():
    """
    Get Redis cache statistics (Task 1.5 - Phase 1)

    Returns:
    {
        "redis_available": true,
        "total_keys": 42,
        "keys_sample": ["ddn:analysis:abc123...", ...],
        "memory_used_mb": 12.5,
        "cache_info": {...}
    }
    """
    if redis_client is None:
        return jsonify({
            "redis_available": False,
            "message": "Redis is not configured or not available"
        }), 503

    try:
        # Get cache keys
        cache_keys = redis_client.keys("ddn:analysis:*")
        total_keys = len(cache_keys)

        # Get Redis info
        redis_info = redis_client.info('memory')
        memory_used_mb = redis_info.get('used_memory', 0) / (1024 * 1024)

        # Sample of keys (first 10)
        keys_sample = cache_keys[:10] if cache_keys else []

        return jsonify({
            "redis_available": True,
            "total_keys": total_keys,
            "keys_sample": keys_sample,
            "memory_used_mb": round(memory_used_mb, 2),
            "cache_info": {
                "host": os.getenv('REDIS_HOST', 'localhost'),
                "port": int(os.getenv('REDIS_PORT', 6379)),
                "db": int(os.getenv('REDIS_DB', 0)),
                "ttl_seconds": 3600
            }
        }), 200

    except Exception as e:
        logger.error(f"❌ Failed to get cache stats: {e}")
        return jsonify({
            "error": "Failed to retrieve cache statistics",
            "details": str(e)
        }), 500


@app.route('/analyze-error', methods=['POST'])
def analyze_error_endpoint():
    """
    Main endpoint for error analysis using ReAct agent (Task 0-ARCH.6)

    Request body:
    {
        "build_id": "12345",
        "error_log": "Full error log...",
        "error_message": "NullPointerException at line 45",
        "stack_trace": "Stack trace...",  # Optional
        "job_name": "EXAScaler-Tests",    # Optional
        "test_name": "test_storage"       # Optional
    }

    Response:
    {
        "success": true,
        "build_id": "12345",
        "error_category": "CODE_ERROR",
        "classification_confidence": 0.95,
        "root_cause": "Null pointer exception in...",
        "fix_recommendation": "Add null check before...",
        "solution_confidence": 0.92,
        "crag_confidence": 0.88,
        "crag_action": "auto_notify",
        "iterations": 3,
        "tools_used": ["pinecone_knowledge", "pinecone_error_library", "github_get_file"],
        "reasoning_history": [...],
        "similar_cases": [...]
    }
    """
    global react_agent

    try:
        # Check if agent is initialized
        if react_agent is None:
            return jsonify({
                "error": "ReAct agent not initialized",
                "details": "Agent initialization failed at startup"
            }), 503

        # Parse request
        data = request.get_json()

        if not data or 'build_id' not in data or 'error_log' not in data:
            return jsonify({
                "error": "Missing required fields: build_id, error_log"
            }), 400

        # Extract error_message if not provided
        error_message = data.get('error_message', data['error_log'][:500])

        logger.info(f"📥 Received ReAct analysis request for build {data['build_id']}")
        logger.info(f"   Error message: {error_message[:100]}...")

        # Task 1.4 - Phase 1: Check cache first
        cache_key = get_cache_key(data['error_log'], error_message)
        cached_result = get_from_cache(cache_key)

        if cached_result:
            # Cache hit - return cached result
            cached_result['cache_hit'] = True
            cached_result['cache_key'] = cache_key[:20] + "..."
            logger.info(f"⚡ Returning cached result for build {data['build_id']}")
            return jsonify(cached_result), 200

        # Cache miss - run ReAct agent analysis
        logger.info(f"🔄 Running fresh analysis for build {data['build_id']}")
        result = react_agent.analyze(
            build_id=data['build_id'],
            error_log=data['error_log'],
            error_message=error_message,
            stack_trace=data.get('stack_trace'),
            job_name=data.get('job_name'),
            test_name=data.get('test_name')
        )

        # Add request metadata
        result['request_metadata'] = {
            "job_name": data.get('job_name'),
            "test_suite": data.get('test_suite')
        }

        # Add cache metadata
        result['cache_hit'] = False
        result['cache_key'] = cache_key[:20] + "..."

        # Save to cache (TTL: 1 hour)
        save_to_cache(cache_key, result, ttl_seconds=3600)

        logger.info(f"📤 ReAct analysis complete: {result.get('error_category')} ({result.get('iterations')} iterations)")

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"❌ Error during ReAct analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "ReAct analysis failed",
            "details": str(e)
        }), 500


@app.route('/classify-error', methods=['POST'])
def classify_error_endpoint():
    """
    Legacy endpoint for backward compatibility
    Redirects to new ReAct-based analysis endpoint

    DEPRECATED: Use /analyze-error instead
    """
    logger.warning("⚠️  Using deprecated /classify-error endpoint - use /analyze-error instead")

    # Convert legacy request to new format
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Map old format to new format
    new_request = {
        "build_id": data.get('build_id'),
        "error_log": data.get('error_log', ''),
        "error_message": data.get('error_log', '')[:500],  # Extract first 500 chars
        "job_name": data.get('job_name'),
        "test_name": data.get('test_suite')  # Map test_suite to test_name
    }

    # Call new endpoint
    from flask import current_app
    with current_app.test_request_context('/analyze-error', method='POST', json=new_request):
        return analyze_error_endpoint()


@app.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all available error categories (Task 0-ARCH.3: Data-driven)

    Returns dynamically discovered categories from Pinecone + static categories
    """
    global react_agent

    if react_agent is None:
        return jsonify({
            "error": "ReAct agent not initialized"
        }), 503

    try:
        # Get all categories from ReAct agent (data-driven from Pinecone)
        categories = react_agent.get_available_categories()

        return jsonify({
            "categories": list(categories.keys()),
            "details": categories,
            "source": "data_driven_from_pinecone",
            "note": "Categories are dynamically discovered from Pinecone knowledge docs"
        }), 200

    except Exception as e:
        logger.error(f"❌ Failed to get categories: {e}")
        return jsonify({
            "error": "Failed to retrieve categories",
            "details": str(e)
        }), 500


@app.route('/refresh-categories', methods=['POST'])
def refresh_categories():
    """
    Refresh error categories from Pinecone (Task 0-ARCH.3)

    Useful when new error types are added to Pinecone docs
    """
    global react_agent

    if react_agent is None:
        return jsonify({
            "error": "ReAct agent not initialized"
        }), 503

    try:
        logger.info("🔄 Refreshing categories from Pinecone...")
        categories = react_agent.refresh_categories()

        return jsonify({
            "success": True,
            "message": "Categories refreshed from Pinecone",
            "categories": list(categories.keys()),
            "count": len(categories)
        }), 200

    except Exception as e:
        logger.error(f"❌ Failed to refresh categories: {e}")
        return jsonify({
            "error": "Failed to refresh categories",
            "details": str(e)
        }), 500


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("🚀 Starting DDN ReAct Agent Service (Task 0-ARCH.6)")
    logger.info("=" * 70)
    logger.info(f"📍 Service will run on: http://localhost:5000")

    # Verify environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_KNOWLEDGE_INDEX",
        "PINECONE_FAILURES_INDEX"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("⚠️  ReAct agent may not work properly!")
    else:
        knowledge_idx = os.getenv("PINECONE_KNOWLEDGE_INDEX")
        failures_idx = os.getenv("PINECONE_FAILURES_INDEX")
        logger.info(f"✅ Knowledge Index: {knowledge_idx}")
        logger.info(f"✅ Error Library: {failures_idx}")

    # Initialize ReAct agent
    logger.info("\n" + "=" * 70)
    react_agent = initialize_react_agent()
    logger.info("=" * 70)

    if react_agent is None:
        logger.error("❌ Failed to initialize ReAct agent - service may not work properly")
    else:
        logger.info("\n✅ ReAct Agent Service Ready!")
        logger.info("   - POST /analyze-error  - ReAct-based error analysis")
        logger.info("   - POST /classify-error - Legacy endpoint (deprecated)")
        logger.info("   - GET  /categories     - Get available error categories")
        logger.info("   - POST /refresh-categories - Refresh categories from Pinecone")
        logger.info("   - GET  /health         - Health check")

    # Run Flask app
    logger.info("\n" + "=" * 70)
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )
