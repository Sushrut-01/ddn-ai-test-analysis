"""
Knowledge Management API - Phase 0-HITL-KM
===========================================
Task 0-HITL-KM.1: Create knowledge management backend API

This API provides full CRUD operations for managing error documentation
in the Pinecone knowledge base, with automatic category discovery refresh.

Features:
- List all knowledge documents with filtering and search
- Get specific knowledge document by ID
- Add new knowledge documentation
- Update existing knowledge documentation
- Delete knowledge documentation
- Trigger category refresh in ReAct agent (no restart needed)
- Get available categories list
- Audit trail integration

Endpoints:
- GET  /api/knowledge/docs          - List all knowledge docs (with filters)
- GET  /api/knowledge/docs/:id      - Get specific doc by ID
- POST /api/knowledge/docs          - Add new doc
- PUT  /api/knowledge/docs/:id      - Update doc
- DELETE /api/knowledge/docs/:id    - Delete doc
- GET  /api/knowledge/categories    - Get all categories
- POST /api/knowledge/refresh       - Trigger category refresh
- GET  /api/knowledge/stats         - Get knowledge base statistics

File: implementation/knowledge_management_api.py
Created: 2025-11-02
Status: ✅ COMPLETE
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from pinecone import Pinecone
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Pinecone Configuration
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_KNOWLEDGE_INDEX = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')

# PostgreSQL Configuration (for audit trail)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_postgres_connection():
    """Get PostgreSQL connection for audit trail"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {str(e)}")
        return None


def create_embedding(text: str) -> Optional[List[float]]:
    """
    Create OpenAI embedding for text

    Args:
        text: Text to embed

    Returns:
        List of floats (1536 dimensions) or None on error
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


def prepare_document_text(doc: Dict) -> str:
    """
    Prepare comprehensive text for embedding from knowledge document

    Args:
        doc: Knowledge document dictionary

    Returns:
        Combined text string for embedding
    """
    parts = [
        f"Error Type: {doc.get('error_type', '')}",
        f"Category: {doc.get('error_category', '')} - {doc.get('subcategory', '')}",
        f"Message: {doc.get('error_message', '')}",
        f"Component: {doc.get('component', '')}",
        f"Root Cause: {doc.get('root_cause', '')}",
        f"Solution: {doc.get('solution', '')}",
        f"Prevention: {doc.get('prevention', '')}",
    ]

    # Add solution steps if available
    if 'solution_steps' in doc and isinstance(doc['solution_steps'], list):
        parts.append(f"Solution Steps: {' '.join(doc['solution_steps'])}")

    # Add code examples if available
    if 'code_before' in doc:
        parts.append(f"Code Before: {doc.get('code_before', '')}")
    if 'code_after' in doc:
        parts.append(f"Code After: {doc.get('code_after', '')}")

    return "\n".join(filter(None, parts))


def prepare_metadata(doc: Dict) -> Dict:
    """
    Prepare Pinecone metadata from document

    Args:
        doc: Knowledge document dictionary

    Returns:
        Metadata dictionary for Pinecone
    """
    # Convert lists to comma-separated strings for Pinecone
    tags = doc.get('tags', [])
    if isinstance(tags, list):
        tags = ','.join(tags)

    test_scenarios = doc.get('test_scenarios', [])
    if isinstance(test_scenarios, list):
        test_scenarios = ','.join(test_scenarios)

    metadata = {
        'error_id': doc.get('error_id', ''),
        'error_type': doc.get('error_type', ''),
        'error_category': doc.get('error_category', ''),
        'category_description': doc.get('category_description', ''),
        'subcategory': doc.get('subcategory', ''),
        'error_message': doc.get('error_message', '')[:500],  # Truncate if too long
        'component': doc.get('component', ''),
        'file_path': doc.get('file_path', ''),
        'line_range': doc.get('line_range', ''),
        'root_cause': doc.get('root_cause', '')[:500],
        'severity': doc.get('severity', ''),
        'frequency': doc.get('frequency', ''),
        'tags': tags,
        'test_scenarios': test_scenarios,
        'doc_type': 'error_documentation',
        'updated_at': datetime.utcnow().isoformat(),
        'created_by': doc.get('created_by', 'system'),
        'updated_by': doc.get('updated_by', 'system')
    }

    return metadata


def log_audit_trail(action: str, doc_id: str, user: str, details: Dict):
    """
    Log knowledge document changes to audit trail

    Args:
        action: Action performed (add, update, delete)
        doc_id: Document ID
        user: User who performed action
        details: Additional details
    """
    try:
        conn = get_postgres_connection()
        if not conn:
            logger.warning("Could not log audit trail - PostgreSQL unavailable")
            return

        cursor = conn.cursor()

        # Check if knowledge_doc_changes table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'knowledge_doc_changes'
            )
        """)

        table_exists = cursor.fetchone()[0]

        if table_exists:
            cursor.execute("""
                INSERT INTO knowledge_doc_changes
                (doc_id, action, user_email, details, changed_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (doc_id, action, user, json.dumps(details)))

            conn.commit()
            logger.info(f"Audit trail logged: {action} on {doc_id} by {user}")
        else:
            logger.warning("knowledge_doc_changes table does not exist - skipping audit trail")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Error logging audit trail: {str(e)}")


def trigger_category_refresh():
    """
    Trigger category refresh in ReAct agent (Task 0-HITL-KM.4)

    This allows new categories to be discovered without restarting the agent.
    Connects to the agent's tool registry and forces a category refresh.

    Returns:
        Boolean indicating success
    """
    try:
        # Import the tool registry
        from agents.tool_registry import create_tool_registry

        # Create registry and refresh categories
        registry = create_tool_registry()
        categories = registry.refresh_categories()

        logger.info(f"✅ Category refresh triggered successfully")
        logger.info(f"   Available categories: {list(categories.keys())}")

        return True, categories

    except Exception as e:
        logger.error(f"Failed to trigger category refresh: {str(e)}")
        return False, {}


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/knowledge/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'knowledge-management-api',
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/knowledge/docs', methods=['GET'])
def list_knowledge_docs():
    """
    List all knowledge documents with optional filtering

    Query parameters:
    - category: Filter by error category
    - severity: Filter by severity
    - search: Search in error_type and error_message
    - limit: Maximum number of results (default 100)
    """
    try:
        # Get query parameters
        category = request.args.get('category')
        severity = request.args.get('severity')
        search_query = request.args.get('search')
        limit = int(request.args.get('limit', 100))

        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Build filter
        filter_dict = {'doc_type': 'error_documentation'}
        if category:
            filter_dict['error_category'] = category
        if severity:
            filter_dict['severity'] = severity

        # Get all vectors with metadata
        # Note: Pinecone requires a query vector, so we use a generic search
        search_text = search_query if search_query else "error documentation knowledge base"
        query_embedding = create_embedding(search_text)

        if not query_embedding:
            return jsonify({'error': 'Failed to create search embedding'}), 500

        # Query Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=limit,
            include_metadata=True,
            filter=filter_dict
        )

        # Format results
        docs = []
        for match in results.matches:
            doc = {
                'id': match.id,
                'score': match.score,
                **match.metadata
            }

            # Convert comma-separated strings back to lists
            if 'tags' in doc and isinstance(doc['tags'], str):
                doc['tags'] = doc['tags'].split(',') if doc['tags'] else []
            if 'test_scenarios' in doc and isinstance(doc['test_scenarios'], str):
                doc['test_scenarios'] = doc['test_scenarios'].split(',') if doc['test_scenarios'] else []

            docs.append(doc)

        return jsonify({
            'success': True,
            'count': len(docs),
            'documents': docs,
            'query': {
                'category': category,
                'severity': severity,
                'search': search_query,
                'limit': limit
            }
        })

    except Exception as e:
        logger.error(f"Error listing knowledge docs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/docs/<doc_id>', methods=['GET'])
def get_knowledge_doc(doc_id):
    """
    Get specific knowledge document by ID

    Args:
        doc_id: Document ID (vector ID in Pinecone)
    """
    try:
        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Fetch vector by ID
        result = index.fetch(ids=[doc_id])

        if doc_id not in result.vectors:
            return jsonify({'error': 'Document not found'}), 404

        vector = result.vectors[doc_id]
        doc = {
            'id': doc_id,
            **vector.metadata
        }

        # Convert comma-separated strings back to lists
        if 'tags' in doc and isinstance(doc['tags'], str):
            doc['tags'] = doc['tags'].split(',') if doc['tags'] else []
        if 'test_scenarios' in doc and isinstance(doc['test_scenarios'], str):
            doc['test_scenarios'] = doc['test_scenarios'].split(',') if doc['test_scenarios'] else []

        return jsonify({
            'success': True,
            'document': doc
        })

    except Exception as e:
        logger.error(f"Error getting knowledge doc: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/docs', methods=['POST'])
def add_knowledge_doc():
    """
    Add new knowledge document

    Request body: Knowledge document JSON with all required fields
    """
    try:
        # Get document from request
        doc = request.json

        if not doc:
            return jsonify({'error': 'No document provided'}), 400

        # Validate required fields
        required_fields = ['error_id', 'error_type', 'error_category', 'error_message', 'root_cause']
        missing_fields = [field for field in required_fields if field not in doc]

        if missing_fields:
            return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400

        # Create embedding
        doc_text = prepare_document_text(doc)
        embedding = create_embedding(doc_text)

        if not embedding:
            return jsonify({'error': 'Failed to create embedding'}), 500

        # Prepare metadata
        metadata = prepare_metadata(doc)
        metadata['created_at'] = datetime.utcnow().isoformat()

        # Create vector ID
        vector_id = f"error_doc_{doc['error_id']}"

        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Check if document already exists
        existing = index.fetch(ids=[vector_id])
        if vector_id in existing.vectors:
            return jsonify({'error': 'Document with this error_id already exists'}), 409

        # Upload to Pinecone
        index.upsert(
            vectors=[{
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            }]
        )

        # Log audit trail
        log_audit_trail(
            action='add',
            doc_id=vector_id,
            user=doc.get('created_by', 'system'),
            details={'error_type': doc['error_type'], 'category': doc['error_category']}
        )

        # Trigger category refresh (Task 0-HITL-KM.4)
        refresh_success, categories = trigger_category_refresh()

        logger.info(f"✅ Added knowledge doc: {vector_id}")

        return jsonify({
            'success': True,
            'document_id': vector_id,
            'message': 'Knowledge document added successfully',
            'category_refresh': refresh_success,
            'available_categories': list(categories.keys()) if refresh_success else []
        }), 201

    except Exception as e:
        logger.error(f"Error adding knowledge doc: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/docs/<doc_id>', methods=['PUT'])
def update_knowledge_doc(doc_id):
    """
    Update existing knowledge document

    Args:
        doc_id: Document ID (vector ID in Pinecone)

    Request body: Updated document fields
    """
    try:
        # Get updates from request
        updates = request.json

        if not updates:
            return jsonify({'error': 'No updates provided'}), 400

        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Fetch existing document
        existing = index.fetch(ids=[doc_id])
        if doc_id not in existing.vectors:
            return jsonify({'error': 'Document not found'}), 404

        # Merge existing metadata with updates
        existing_metadata = existing.vectors[doc_id].metadata
        updated_doc = {**existing_metadata, **updates}

        # Create new embedding
        doc_text = prepare_document_text(updated_doc)
        embedding = create_embedding(doc_text)

        if not embedding:
            return jsonify({'error': 'Failed to create embedding'}), 500

        # Prepare updated metadata
        metadata = prepare_metadata(updated_doc)
        metadata['updated_at'] = datetime.utcnow().isoformat()

        # Update in Pinecone
        index.upsert(
            vectors=[{
                'id': doc_id,
                'values': embedding,
                'metadata': metadata
            }]
        )

        # Log audit trail
        log_audit_trail(
            action='update',
            doc_id=doc_id,
            user=updates.get('updated_by', 'system'),
            details={'updated_fields': list(updates.keys())}
        )

        # Trigger category refresh if category changed
        if 'error_category' in updates:
            refresh_success, categories = trigger_category_refresh()
            logger.info(f"Category changed - triggered refresh")
        else:
            refresh_success = False
            categories = {}

        logger.info(f"✅ Updated knowledge doc: {doc_id}")

        return jsonify({
            'success': True,
            'document_id': doc_id,
            'message': 'Knowledge document updated successfully',
            'category_refresh': refresh_success,
            'available_categories': list(categories.keys()) if refresh_success else []
        })

    except Exception as e:
        logger.error(f"Error updating knowledge doc: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/docs/<doc_id>', methods=['DELETE'])
def delete_knowledge_doc(doc_id):
    """
    Delete knowledge document

    Args:
        doc_id: Document ID (vector ID in Pinecone)
    """
    try:
        # Get user from query params
        user = request.args.get('user', 'system')

        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Fetch existing document for audit trail
        existing = index.fetch(ids=[doc_id])
        if doc_id not in existing.vectors:
            return jsonify({'error': 'Document not found'}), 404

        existing_metadata = existing.vectors[doc_id].metadata

        # Delete from Pinecone
        index.delete(ids=[doc_id])

        # Log audit trail
        log_audit_trail(
            action='delete',
            doc_id=doc_id,
            user=user,
            details={
                'error_type': existing_metadata.get('error_type', ''),
                'category': existing_metadata.get('error_category', '')
            }
        )

        # Trigger category refresh (category might be removed if last doc)
        refresh_success, categories = trigger_category_refresh()

        logger.info(f"✅ Deleted knowledge doc: {doc_id}")

        return jsonify({
            'success': True,
            'document_id': doc_id,
            'message': 'Knowledge document deleted successfully',
            'category_refresh': refresh_success,
            'available_categories': list(categories.keys()) if refresh_success else []
        })

    except Exception as e:
        logger.error(f"Error deleting knowledge doc: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/categories', methods=['GET'])
def get_categories():
    """
    Get all available error categories from Pinecone

    Returns list of categories with descriptions and document counts
    """
    try:
        # Trigger category discovery
        success, categories = trigger_category_refresh()

        if not success:
            return jsonify({'error': 'Failed to retrieve categories'}), 500

        # Get document counts per category
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        category_stats = []
        for category_name, category_desc in categories.items():
            # Query for documents in this category
            query_embedding = create_embedding(category_name)
            if query_embedding:
                results = index.query(
                    vector=query_embedding,
                    top_k=1000,
                    include_metadata=True,
                    filter={
                        'doc_type': 'error_documentation',
                        'error_category': category_name
                    }
                )

                category_stats.append({
                    'name': category_name,
                    'description': category_desc,
                    'document_count': len(results.matches)
                })

        return jsonify({
            'success': True,
            'count': len(category_stats),
            'categories': category_stats
        })

    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/refresh', methods=['POST'])
def refresh_categories():
    """
    Trigger category refresh in ReAct agent

    Allows new categories to be discovered without restarting the agent.
    This is called automatically after add/update/delete operations,
    but can also be manually triggered.
    """
    try:
        success, categories = trigger_category_refresh()

        if not success:
            return jsonify({'error': 'Failed to refresh categories'}), 500

        return jsonify({
            'success': True,
            'message': 'Categories refreshed successfully',
            'count': len(categories),
            'categories': list(categories.keys())
        })

    except Exception as e:
        logger.error(f"Error refreshing categories: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """
    Get knowledge base statistics

    Returns:
    - Total document count
    - Documents per category
    - Documents per severity
    - Recent additions
    """
    try:
        # Connect to Pinecone
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)

        # Get index stats
        stats = index.describe_index_stats()

        # Get all documents
        query_embedding = create_embedding("knowledge base statistics")
        if not query_embedding:
            return jsonify({'error': 'Failed to create embedding'}), 500

        results = index.query(
            vector=query_embedding,
            top_k=1000,  # Get all docs
            include_metadata=True,
            filter={'doc_type': 'error_documentation'}
        )

        # Aggregate statistics
        total_docs = len(results.matches)

        # Count by category
        category_counts = {}
        severity_counts = {}
        recent_docs = []

        for match in results.matches:
            metadata = match.metadata

            # Category counts
            category = metadata.get('error_category', 'UNKNOWN')
            category_counts[category] = category_counts.get(category, 0) + 1

            # Severity counts
            severity = metadata.get('severity', 'UNKNOWN')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            # Recent docs (last 7 days)
            updated_at = metadata.get('updated_at', '')
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    if (datetime.utcnow() - updated_date).days <= 7:
                        recent_docs.append({
                            'id': match.id,
                            'error_type': metadata.get('error_type', ''),
                            'category': category,
                            'updated_at': updated_at
                        })
                except:
                    pass

        return jsonify({
            'success': True,
            'statistics': {
                'total_documents': total_docs,
                'total_vectors': stats.total_vector_count,
                'index_dimension': stats.dimension,
                'by_category': category_counts,
                'by_severity': severity_counts,
                'recent_additions': len(recent_docs),
                'recent_docs': sorted(recent_docs, key=lambda x: x['updated_at'], reverse=True)[:10]
            }
        })

    except Exception as e:
        logger.error(f"Error getting knowledge stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Verify environment variables
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not set in environment")
        sys.exit(1)

    if not PINECONE_API_KEY:
        logger.error("PINECONE_API_KEY not set in environment")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("Knowledge Management API - Starting")
    logger.info("=" * 60)
    logger.info(f"Pinecone Index: {PINECONE_KNOWLEDGE_INDEX}")
    logger.info(f"Embedding Model: {EMBEDDING_MODEL}")
    logger.info("=" * 60)

    # Test Pinecone connection
    try:
        index = pc.Index(PINECONE_KNOWLEDGE_INDEX)
        stats = index.describe_index_stats()
        logger.info(f"✓ Connected to Pinecone")
        logger.info(f"  Total vectors: {stats.total_vector_count}")
        logger.info(f"  Dimension: {stats.dimension}")
    except Exception as e:
        logger.error(f"✗ Failed to connect to Pinecone: {str(e)}")
        sys.exit(1)

    # Start Flask server
    port = int(os.getenv('KNOWLEDGE_API_PORT', 5008))
    logger.info(f"\n🚀 Starting Knowledge Management API on port {port}")
    logger.info("=" * 60)

    app.run(host='0.0.0.0', port=port, debug=True)
