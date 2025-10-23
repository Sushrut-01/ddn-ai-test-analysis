"""
DDN Test Failure Classification Agent - LangGraph Implementation
Production-ready error classification service with RAG integration
"""

from flask import Flask, request, jsonify
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# ============================================================================
# ERROR CATEGORIES CONFIGURATION
# ============================================================================

ERROR_CATEGORIES = {
    "CODE_ERROR": {
        "needs_github": True,
        "keywords": [
            "SyntaxError", "CompileError", "NullPointerException",
            "AttributeError", "TypeError", "undefined", "NameError",
            "IndexError", "KeyError", "ValueError"
        ],
        "action": "fetch_code_and_analyze",
        "priority": "HIGH"
    },
    "INFRA_ERROR": {
        "needs_github": False,
        "keywords": [
            "OutOfMemoryError", "DiskSpaceError", "NetworkError",
            "ConnectionTimeout", "SocketException", "heap space",
            "memory", "disk full", "no space"
        ],
        "action": "retrieve_infra_solution",
        "priority": "HIGH"
    },
    "DEPENDENCY_ERROR": {
        "needs_github": False,
        "keywords": [
            "ModuleNotFoundError", "ImportError", "version conflict",
            "ClassNotFoundException", "NoClassDefFoundError",
            "dependency", "package not found", "cannot import"
        ],
        "action": "retrieve_dependency_solution",
        "priority": "MEDIUM"
    },
    "CONFIG_ERROR": {
        "needs_github": False,
        "keywords": [
            "ConfigurationException", "InvalidConfiguration",
            "permission denied", "access denied", "configuration",
            "config", "environment variable"
        ],
        "action": "retrieve_config_solution",
        "priority": "MEDIUM"
    },
    "TEST_FAILURE": {
        "needs_github": True,
        "keywords": [
            "AssertionError", "ExpectationFailed", "test failed",
            "assertion failed", "expected", "actual"
        ],
        "action": "fetch_test_and_analyze",
        "priority": "MEDIUM"
    }
}

# ============================================================================
# STATE DEFINITION
# ============================================================================

class ErrorAnalysisState(BaseModel):
    """State for error analysis workflow"""
    build_id: str
    error_log: str
    status: str = "FAILURE"
    job_name: Optional[str] = None
    test_suite: Optional[str] = None

    # Classification results
    error_category: Optional[str] = None
    confidence: float = 0.0
    similar_solutions: List[Dict] = []
    needs_code_analysis: bool = False

    # File paths (for code errors)
    github_files: List[str] = []

    # Final output
    solution: Optional[Dict] = None

# ============================================================================
# CLASSIFICATION FUNCTIONS
# ============================================================================

def classify_error(state: dict) -> dict:
    """
    Step 1: Classify error type based on keywords
    """
    logger.info(f"🔍 Classifying error for build {state['build_id']}")

    error_log = state.get('error_log', '').lower()

    # Match against known patterns
    best_match = None
    max_matches = 0

    for category, config in ERROR_CATEGORIES.items():
        matches = sum(1 for keyword in config['keywords']
                     if keyword.lower() in error_log)

        if matches > max_matches:
            max_matches = matches
            best_match = category

    # Default to CODE_ERROR if no matches
    if best_match is None:
        best_match = "CODE_ERROR"
        confidence = 0.5
    else:
        confidence = min(0.95, 0.6 + (max_matches * 0.1))

    state['error_category'] = best_match
    state['confidence'] = confidence
    state['needs_code_analysis'] = ERROR_CATEGORIES[best_match]['needs_github']

    logger.info(f"✅ Classified as {best_match} (confidence: {confidence:.2f})")

    return state


def search_similar_errors_rag(state: dict) -> dict:
    """
    Step 2: RAG search in Pinecone for similar past errors
    """
    logger.info(f"🔎 Searching Pinecone for similar errors...")

    try:
        # Initialize Pinecone
        embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        vectorstore = PineconeVectorStore(
            index_name=os.getenv("PINECONE_INDEX", "ddn-error-solutions"),
            embedding=embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY")
        )

        # Search for similar errors
        similar_docs = vectorstore.similarity_search(
            state['error_log'],
            k=5,
            filter={"error_category": state['error_category']}
        )

        # Format results
        state['similar_solutions'] = [
            {
                "error": doc.page_content,
                "solution": doc.metadata.get('solution', ''),
                "root_cause": doc.metadata.get('root_cause', ''),
                "success_rate": doc.metadata.get('success_rate', 0.0),
                "confidence": doc.metadata.get('confidence', 0.0),
                "times_used": doc.metadata.get('times_used', 0)
            }
            for doc in similar_docs
        ]

        logger.info(f"✅ Found {len(state['similar_solutions'])} similar cases")

    except Exception as e:
        logger.error(f"❌ Pinecone search failed: {e}")
        state['similar_solutions'] = []

    return state


def extract_file_paths(state: dict) -> dict:
    """
    Step 3: Extract file paths from error log (for code errors)
    """
    if not state.get('needs_code_analysis'):
        return state

    logger.info("📁 Extracting file paths from error log...")

    error_log = state.get('error_log', '')
    file_paths = []

    # Common patterns for file paths in stack traces
    import re

    # Java stack traces: at com.example.Class.method(File.java:123)
    java_pattern = r'at\s+[\w.]+\(([\w/]+\.java):(\d+)\)'
    java_matches = re.findall(java_pattern, error_log)
    file_paths.extend([f"src/main/java/{path}" for path, _ in java_matches])

    # Python stack traces: File "/path/to/file.py", line 123
    python_pattern = r'File\s+"([^"]+\.py)",\s+line\s+(\d+)'
    python_matches = re.findall(python_pattern, error_log)
    file_paths.extend([path for path, _ in python_matches])

    # Generic file paths
    generic_pattern = r'[\w/]+\.(py|java|js|ts|cpp|c|h):\d+'
    generic_matches = re.findall(generic_pattern, error_log)
    file_paths.extend(generic_matches)

    # Remove duplicates
    state['github_files'] = list(set(file_paths))

    logger.info(f"✅ Extracted {len(state['github_files'])} file paths")

    return state


# ============================================================================
# LANGGRAPH WORKFLOW
# ============================================================================

def create_classification_workflow():
    """
    Create the LangGraph workflow for error classification
    """
    workflow = StateGraph(dict)

    # Add nodes
    workflow.add_node("classify", classify_error)
    workflow.add_node("rag_search", search_similar_errors_rag)
    workflow.add_node("extract_files", extract_file_paths)

    # Define edges
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "rag_search")
    workflow.add_edge("rag_search", "extract_files")
    workflow.add_edge("extract_files", END)

    return workflow.compile()


# Initialize workflow
classification_app = create_classification_workflow()

# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DDN LangGraph Classification Agent",
        "version": "1.0.0"
    })


@app.route('/classify-error', methods=['POST'])
def classify_error_endpoint():
    """
    Main endpoint for error classification

    Request body:
    {
        "build_id": "12345",
        "error_log": "NullPointerException at...",
        "status": "FAILURE",
        "job_name": "EXAScaler-Tests",
        "test_suite": "Smoke"
    }

    Response:
    {
        "build_id": "12345",
        "error_category": "CODE_ERROR",
        "confidence": 0.95,
        "needs_code_analysis": true,
        "similar_solutions": [...],
        "github_files": ["src/main/java/DDNStorage.java"],
        "priority": "HIGH"
    }
    """
    try:
        # Parse request
        data = request.get_json()

        if not data or 'build_id' not in data or 'error_log' not in data:
            return jsonify({
                "error": "Missing required fields: build_id, error_log"
            }), 400

        logger.info(f"📥 Received classification request for build {data['build_id']}")

        # Create initial state
        initial_state = {
            "build_id": data['build_id'],
            "error_log": data['error_log'],
            "status": data.get('status', 'FAILURE'),
            "job_name": data.get('job_name'),
            "test_suite": data.get('test_suite')
        }

        # Run workflow
        result = classification_app.invoke(initial_state)

        # Build response
        response = {
            "build_id": result['build_id'],
            "error_category": result['error_category'],
            "confidence": result['confidence'],
            "needs_code_analysis": result['needs_code_analysis'],
            "similar_solutions": result['similar_solutions'],
            "github_files": result.get('github_files', []),
            "priority": ERROR_CATEGORIES[result['error_category']]['priority'],
            "action": ERROR_CATEGORIES[result['error_category']]['action']
        }

        logger.info(f"📤 Classification complete: {result['error_category']}")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"❌ Error during classification: {str(e)}")
        return jsonify({
            "error": "Classification failed",
            "details": str(e)
        }), 500


@app.route('/categories', methods=['GET'])
def get_categories():
    """Get all available error categories"""
    return jsonify({
        "categories": list(ERROR_CATEGORIES.keys()),
        "details": ERROR_CATEGORIES
    })


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting DDN LangGraph Classification Service...")
    logger.info(f"📍 Service will run on: http://localhost:5000")

    # Verify environment variables
    required_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "PINECONE_INDEX"
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        logger.warning("Some features may not work properly!")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )
