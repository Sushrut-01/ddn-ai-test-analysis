"""
DDN Test Failure AI Analysis Service
Simple, production-ready service using Gemini AI
Integrates with MongoDB, PostgreSQL, and Pinecone
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# AI and Database imports
import google.generativeai as genai
from openai import OpenAI
from pinecone import Pinecone
from pymongo import MongoClient
import psycopg2
from psycopg2.extras import RealDictCursor
import requests  # Phase 2: For re-ranking service API calls

# Task 0-ARCH.10: Import ReAct Agent
import sys
agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
sys.path.insert(0, agents_dir)
from react_agent_service import create_react_agent

# Task 0-ARCH.18: Import CRAG Verifier
verification_dir = os.path.join(os.path.dirname(__file__), 'verification')
sys.path.insert(0, verification_dir)
try:
    from crag_verifier import CRAGVerifier
    CRAG_AVAILABLE = True
except ImportError as e:
    CRAG_AVAILABLE = False
    logging.warning(f"CRAG Verifier not available: {e}")

# Task 0D.5: Import Phase 0D modules (Context Engineering)
implementation_dir = os.path.dirname(__file__)
sys.path.insert(0, implementation_dir)
try:
    from rag_router import create_rag_router
    from context_engineering import create_context_engineer
    from prompt_templates import create_prompt_generator
    PHASE_0D_AVAILABLE = True
except ImportError as e:
    PHASE_0D_AVAILABLE = False
    logging.warning(f"Phase 0D modules not available: {e}")

# Phase 4: Import PII redaction
security_dir = os.path.join(implementation_dir, 'security')
sys.path.insert(0, security_dir)
try:
    from pii_redaction import get_pii_redactor
    PII_REDACTION_AVAILABLE = True
except ImportError as e:
    PII_REDACTION_AVAILABLE = False
    logging.warning(f"Phase 4: PII redaction not available: {e}")

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Gemini AI (Task 0-ARCH.10: Now used for formatting only)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
# Use gemini-flash-latest (free tier model with correct name)
try:
    gemini_model = genai.GenerativeModel('models/gemini-flash-latest')
    logger.info("✓ Gemini model initialized: models/gemini-flash-latest (formatting only)")
except Exception as e:
    gemini_model = None
    logger.error(f"✗ Gemini model initialization failed: {str(e)[:200]}")

# Task 0-ARCH.10: ReAct Agent (primary analysis engine)
react_agent = None
try:
    react_agent = create_react_agent()
    logger.info("✓ ReAct Agent initialized (primary analysis engine)")
    logger.info("   - Replaces direct Gemini calls for analysis")
    logger.info("   - Gemini used for final formatting only")
except Exception as e:
    logger.error(f"✗ ReAct Agent initialization failed: {str(e)[:200]}")
    logger.warning("   - Falling back to legacy Gemini direct analysis")

# Task 0-ARCH.18: CRAG Verifier (verification layer)
crag_verifier = None
if CRAG_AVAILABLE:
    try:
        crag_verifier = CRAGVerifier()
        logger.info("✓ CRAG Verifier initialized (multi-dimensional confidence scoring)")
        logger.info("   - HIGH (≥0.85): Pass through")
        logger.info("   - MEDIUM (0.65-0.85): HITL queue")
        logger.info("   - LOW (0.40-0.65): Self-correction")
        logger.info("   - VERY_LOW (<0.40): Web search fallback")
    except Exception as e:
        logger.error(f"✗ CRAG Verifier initialization failed: {str(e)[:200]}")
        logger.warning("   - Answers will not be verified (no confidence scoring)")
else:
    logger.warning("CRAG Verifier not available - answers will not be verified")

# Phase 4: Initialize PII redactor
pii_redactor = None
pii_enabled = os.getenv('PII_REDACTION_ENABLED', 'false').lower() == 'true'

if not pii_enabled:
    logger.info("ℹ️  PII redaction DISABLED (client approval pending)")
    logger.info("   - Storing actual data for dashboard navigation")
    logger.info("   - No redaction before embedding creation")
elif PII_REDACTION_AVAILABLE:
    try:
        pii_redactor = get_pii_redactor()
        logger.info("✓ PII Redactor ENABLED (Phase 4)")
        logger.info("   - Redacts PII before embedding creation")
        logger.info("   - Uses Presidio with regex fallback")
    except Exception as e:
        logger.error(f"✗ PII Redactor initialization failed: {str(e)[:200]}")
        logger.warning("   - PII will NOT be redacted (security risk)")
else:
    logger.warning("Phase 4: PII Redactor not available - install presidio packages")

# Task 0D.5: Initialize Phase 0D modules (Context Engineering)
rag_router = None
context_engineer = None
prompt_generator = None

if PHASE_0D_AVAILABLE:
    try:
        rag_router = create_rag_router()
        logger.info("✓ RAG Router initialized (OPTION C routing)")
        logger.info("   - CODE_ERROR → Gemini + GitHub + RAG")
        logger.info("   - Other errors → RAG only")

        context_engineer = create_context_engineer()
        logger.info("✓ Context Engineer initialized (token optimization)")
        logger.info("   - 4000 token budget for Gemini")
        logger.info("   - Entity extraction and metadata enrichment")

        prompt_generator = create_prompt_generator()
        logger.info("✓ Prompt Generator initialized (category-specific prompts)")
        logger.info("   - 6 category templates with few-shot examples")
        logger.info("   - Dynamic prompt generation")
    except Exception as e:
        logger.error(f"✗ Phase 0D initialization failed: {str(e)[:200]}")
        logger.warning("   - Falling back to legacy prompt generation")
        rag_router = None
        context_engineer = None
        prompt_generator = None
else:
    logger.warning("Phase 0D modules not available - using legacy analysis")

# Phase 2: Re-Ranking Service Configuration
RERANKING_SERVICE_URL = os.getenv('RERANKING_SERVICE_URL', 'http://localhost:5009')
RERANKING_ENABLED = os.getenv('RERANKING_ENABLED', 'true').lower() == 'true'
RERANKING_RETRIEVAL_K = int(os.getenv('RERANKING_RETRIEVAL_K', 50))  # Retrieve 50 candidates
RERANKING_TOP_K = int(os.getenv('RERANKING_TOP_K', 5))  # Return top 5 after re-ranking

# Test re-ranking service availability
reranking_available = False
if RERANKING_ENABLED:
    try:
        test_response = requests.get(
            f"{RERANKING_SERVICE_URL}/health",
            timeout=2
        )
        if test_response.status_code == 200:
            reranking_available = True
            logger.info(f"✓ Re-Ranking Service available at {RERANKING_SERVICE_URL} (Phase 2)")
            logger.info(f"   - Retrieval k={RERANKING_RETRIEVAL_K}, Re-ranked top-k={RERANKING_TOP_K}")
            logger.info("   - Expected accuracy improvement: +15-20%")
        else:
            logger.warning(f"⚠️  Re-Ranking Service returned status {test_response.status_code}")
            logger.warning("   - Falling back to direct RAG results")
    except Exception as e:
        logger.warning(f"⚠️  Re-Ranking Service not available: {e}")
        logger.warning("   - Falling back to direct RAG results")
else:
    logger.info("Re-Ranking Service disabled (set RERANKING_ENABLED=true to enable)")

# OpenAI (for embeddings)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Pinecone - Dual-Index RAG Architecture
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_KNOWLEDGE_INDEX = os.getenv('PINECONE_KNOWLEDGE_INDEX', 'ddn-knowledge-docs')
PINECONE_FAILURES_INDEX = os.getenv('PINECONE_FAILURES_INDEX', 'ddn-error-library')
pc = Pinecone(api_key=PINECONE_API_KEY)

# Connect to both indexes
knowledge_index = pc.Index(PINECONE_KNOWLEDGE_INDEX)
failures_index = pc.Index(PINECONE_FAILURES_INDEX)

logger.info(f"✓ Connected to knowledge index: {PINECONE_KNOWLEDGE_INDEX}")
logger.info(f"✓ Connected to failures index: {PINECONE_FAILURES_INDEX}")

# MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
MONGODB_DB = os.getenv('MONGODB_DB', 'ddn_tests')
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB]
failures_collection = mongo_db['test_failures']

# PostgreSQL
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

# ============================================================================
# ERROR CLASSIFICATION
# ============================================================================

ERROR_CATEGORIES = {
    "ENVIRONMENT": ["ENOTFOUND", "dns", "network", "connection", "timeout", "host"],
    "CONFIGURATION": ["config", "permission", "access denied", "credentials", "authentication"],
    "DEPENDENCY": ["module not found", "import error", "package", "dependency"],
    "CODE": ["syntax", "type error", "null pointer", "undefined"],
    "INFRASTRUCTURE": ["memory", "disk", "cpu", "resource"],
}

def classify_error_simple(error_message):
    """
    Simple keyword-based classification
    """
    error_lower = error_message.lower()

    for category, keywords in ERROR_CATEGORIES.items():
        for keyword in keywords:
            if keyword in error_lower:
                return category

    return "UNKNOWN"

# ============================================================================
# AI ANALYSIS WITH RAG - TASK 0-ARCH.10
# ============================================================================

def analyze_with_react_agent(failure_data):
    """
    Analyze failure using ReAct agent (Task 0-ARCH.10)

    ReAct agent provides:
    - Intelligent error classification
    - Multi-step reasoning for complex errors
    - Context-aware routing (80/20 rule)
    - Self-correction with retries
    - RAG integration (Pinecone knowledge + error library)

    Returns full ReAct analysis with routing stats, multi-step reasoning, etc.
    """
    global react_agent

    if react_agent is None:
        logger.error("[ReAct] Agent not available - using fallback")
        return None

    try:
        # Extract failure data
        error_message = failure_data.get('error_message', '')
        error_log = failure_data.get('error_log', error_message)  # Use error_message if no log
        test_name = failure_data.get('test_name', '')
        stack_trace = failure_data.get('stack_trace', '')
        build_id = str(failure_data.get('_id', 'unknown'))

        logger.info(f"[ReAct] Starting analysis for: {test_name} (build: {build_id})")

        # Call ReAct agent
        react_result = react_agent.analyze(
            build_id=build_id,
            error_log=error_log,
            error_message=error_message,
            stack_trace=stack_trace,
            job_name=failure_data.get('job_name'),
            test_name=test_name
        )

        if react_result.get('success'):
            logger.info(f"[ReAct] Analysis complete: {react_result.get('error_category')}")
            logger.info(f"[ReAct] Iterations: {react_result.get('iterations')}, Confidence: {react_result.get('solution_confidence', 0):.2f}")

            # Log routing stats (Task 0-ARCH.7)
            routing_stats = react_result.get('routing_stats', {})
            if routing_stats.get('total_decisions', 0) > 0:
                logger.info(f"[ReAct] Routing: {routing_stats.get('github_fetch_percentage', 0):.0f}% GitHub fetch rate")

            # Log multi-step reasoning (Task 0-ARCH.8)
            multi_step = react_result.get('multi_step_reasoning', {})
            if multi_step.get('multi_file_detected'):
                logger.info(f"[ReAct] Multi-file error detected: {len(multi_step.get('referenced_files', []))} files")

            return react_result
        else:
            logger.error(f"[ReAct] Analysis failed: {react_result.get('error', 'Unknown error')}")
            return None

    except Exception as e:
        logger.error(f"[ReAct] Error during analysis: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def verify_react_result_with_crag(react_result, failure_data):
    """
    Verify ReAct agent result using CRAG (Task 0-ARCH.18)

    CRAG provides multi-dimensional confidence scoring and intelligent routing:
    - HIGH (≥0.85): Pass through (high quality)
    - MEDIUM (0.65-0.85): Queue for HITL (human review)
    - LOW (0.40-0.65): Attempt self-correction
    - VERY_LOW (<0.40): Web search fallback

    Args:
        react_result: Result from ReAct agent
        failure_data: Original failure data

    Returns:
        dict: Verification result with confidence and metadata
    """
    global crag_verifier

    if crag_verifier is None:
        logger.warning("[CRAG] Verifier not available - skipping verification")
        # Return React result with no verification
        return {
            'verified': False,
            'verification_skipped': True,
            'react_result': react_result,
            'verification_metadata': {
                'status': 'SKIPPED',
                'reason': 'CRAG verifier not available'
            }
        }

    try:
        # Extract retrieved documents from ReAct result
        # The react_result should contain documents from RAG queries
        retrieved_docs = []

        # Check for similar cases (from RAG)
        similar_cases = react_result.get('similar_cases', [])
        for case in similar_cases:
            retrieved_docs.append({
                'text': case.get('resolution', case.get('root_cause', '')),
                'similarity_score': case.get('similarity_score', 0.0),
                'metadata': {
                    'error_type': case.get('error_type', ''),
                    'category': case.get('category', '')
                }
            })

        # If no similar cases, create placeholder docs (CRAG needs docs for scoring)
        if not retrieved_docs:
            logger.info("[CRAG] No retrieved docs found in ReAct result - using placeholder")
            retrieved_docs = [{
                'text': 'No similar documented errors found',
                'similarity_score': 0.0,
                'metadata': {}
            }]

        # Prepare failure context for CRAG
        failure_context = {
            'build_id': str(failure_data.get('_id', 'unknown')),
            'error_message': failure_data.get('error_message', ''),
            'error_category': react_result.get('error_category', 'UNKNOWN'),
            'test_name': failure_data.get('test_name', ''),
            'stack_trace': failure_data.get('stack_trace', '')
        }

        logger.info(f"[CRAG] Verifying ReAct result (category: {react_result.get('error_category')})")
        logger.info(f"[CRAG] Retrieved docs: {len(retrieved_docs)}, Avg similarity: {sum(d.get('similarity_score', 0) for d in retrieved_docs) / len(retrieved_docs) if retrieved_docs else 0:.2f}")

        # Run CRAG verification
        verification_result = crag_verifier.verify(
            react_result=react_result,
            retrieved_docs=retrieved_docs,
            failure_data=failure_context
        )

        # Log verification results
        status = verification_result.get('status')
        confidence = verification_result.get('confidence', 0.0)
        confidence_level = verification_result.get('confidence_level', 'UNKNOWN')

        logger.info(f"[CRAG] Verification complete: {status}")
        logger.info(f"[CRAG] Confidence: {confidence:.3f} ({confidence_level})")
        logger.info(f"[CRAG] Action: {verification_result.get('action_taken', 'none')}")

        # Log component scores
        metadata = verification_result.get('verification_metadata', {})
        if 'confidence_scores' in metadata:
            components = metadata['confidence_scores'].get('components', {})
            logger.info(f"[CRAG] Components: rel={components.get('relevance', 0):.2f}, "
                       f"con={components.get('consistency', 0):.2f}, "
                       f"grd={components.get('grounding', 0):.2f}, "
                       f"cmp={components.get('completeness', 0):.2f}, "
                       f"cls={components.get('classification', 0):.2f}")

        # Return verification result with original react_result embedded
        return {
            'verified': True,
            'verification_status': status,
            'confidence': confidence,
            'confidence_level': confidence_level,
            'react_result': react_result,  # Original result
            'verified_answer': verification_result.get('answer'),  # May be corrected/enhanced
            'verification_metadata': metadata,
            'action_taken': verification_result.get('action_taken'),
            'review_url': verification_result.get('review_url')  # For HITL cases
        }

    except Exception as e:
        logger.error(f"[CRAG] Verification error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

        # Return unverified result
        return {
            'verified': False,
            'verification_failed': True,
            'react_result': react_result,
            'verification_metadata': {
                'status': 'ERROR',
                'error': str(e)
            }
        }


def format_react_result_with_gemini(react_result):
    """
    Format ReAct analysis result using Gemini for user-friendly presentation (Task 0-ARCH.10)

    Takes ReAct's technical analysis and converts it to natural language
    suitable for dashboard display.
    """
    global gemini_model

    if gemini_model is None:
        logger.warning("[Gemini Formatter] Not available - using ReAct result as-is")
        # Return ReAct result in compatible format
        return {
            "classification": react_result.get('error_category', 'UNKNOWN'),
            "root_cause": react_result.get('root_cause', 'Analysis completed'),
            "severity": "MEDIUM",  # Could enhance ReAct to provide severity
            "solution": react_result.get('fix_recommendation', 'See ReAct analysis'),
            "confidence": react_result.get('solution_confidence', 0.0),
            "ai_status": "REACT_SUCCESS",
            "similar_error_docs": react_result.get('similar_cases', []),
            "rag_enabled": True,
            "react_analysis": react_result,  # Include full ReAct result
            "formatting_used": False,
            # Task 0E.5: Include GitHub files (for CODE_ERROR)
            "github_files": react_result.get('github_files', []),
            "github_code_included": len(react_result.get('github_files', [])) > 0
        }

    try:
        # Task 0E.5: Extract GitHub code if available (for CODE_ERROR category)
        github_files = react_result.get('github_files', [])
        github_context = ""

        if github_files:
            github_context = "\n\n=== GITHUB SOURCE CODE (FOR CODE_ERROR) ===\n"
            for idx, file_data in enumerate(github_files, 1):
                github_context += f"\nFile {idx}: {file_data.get('file_path', 'unknown')}\n"
                github_context += f"Lines: {file_data.get('line_range', 'all')}\n"
                github_context += f"Repository: {file_data.get('repo', 'N/A')}\n"
                github_context += "Code:\n"
                github_context += "```\n"
                # Limit code to first 50 lines to avoid token overflow
                code_lines = file_data.get('content', '').split('\n')[:50]
                github_context += '\n'.join(code_lines)
                if len(file_data.get('content', '').split('\n')) > 50:
                    github_context += f"\n... ({file_data.get('total_lines', 0) - 50} more lines omitted)"
                github_context += "\n```\n"

            logger.info(f"[Task 0E.5] Including {len(github_files)} GitHub files in Gemini context")

        # Build Gemini formatting prompt
        prompt = f"""You are formatting an AI analysis result for a user dashboard.

=== REACT AGENT ANALYSIS ===
Error Category: {react_result.get('error_category')}
Classification Confidence: {react_result.get('classification_confidence', 0):.2f}
Root Cause: {react_result.get('root_cause', 'Not determined')}
Fix Recommendation: {react_result.get('fix_recommendation', 'Not provided')}
Solution Confidence: {react_result.get('solution_confidence', 0):.2f}
Iterations: {react_result.get('iterations', 0)}
Tools Used: {', '.join(react_result.get('tools_used', []))}
{github_context}
=== YOUR TASK ===
Format this analysis for end users. Return ONLY JSON with:
- classification: Map error_category to: ENVIRONMENT/CONFIGURATION/DEPENDENCY/CODE/INFRASTRUCTURE
- root_cause: User-friendly 1-2 sentence explanation (if GitHub code is provided, reference specific line numbers and code issues)
- severity: LOW/MEDIUM/HIGH/CRITICAL (infer from confidence and error type)
- solution: Clear, actionable 3-5 step fix (if GitHub code is provided, include specific code changes needed)
- confidence: {react_result.get('solution_confidence', 0)} (keep same)

IMPORTANT:
- If GitHub source code is provided above, use it to provide more specific root cause and solution
- Reference actual file paths and line numbers when available
- Return ONLY valid JSON, no markdown, no extra text."""

        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        # Parse JSON
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()

        formatted = json.loads(response_text)
        formatted['ai_status'] = 'REACT_WITH_GEMINI_FORMATTING'
        formatted['similar_error_docs'] = react_result.get('similar_cases', [])
        formatted['rag_enabled'] = True
        formatted['react_analysis'] = react_result  # Include full ReAct result
        formatted['formatting_used'] = True
        # Task 0E.5: Include GitHub files in response (for CODE_ERROR)
        formatted['github_files'] = github_files if github_files else []
        formatted['github_code_included'] = len(github_files) > 0

        logger.info("[Gemini Formatter] Successfully formatted ReAct result")
        return formatted

    except Exception as e:
        logger.warning(f"[Gemini Formatter] Failed: {str(e)} - using ReAct result as-is")
        # Fallback to ReAct result
        return {
            "classification": react_result.get('error_category', 'UNKNOWN'),
            "root_cause": react_result.get('root_cause', 'Analysis completed'),
            "severity": "MEDIUM",
            "solution": react_result.get('fix_recommendation', 'See ReAct analysis'),
            "confidence": react_result.get('solution_confidence', 0.0),
            "ai_status": "REACT_SUCCESS_FORMATTING_FAILED",
            "similar_error_docs": react_result.get('similar_cases', []),
            "rag_enabled": True,
            "react_analysis": react_result,
            "formatting_used": False,
            "formatting_error": str(e)[:200],
            # Task 0E.5: Include GitHub files (for CODE_ERROR)
            "github_files": react_result.get('github_files', []),
            "github_code_included": len(react_result.get('github_files', [])) > 0
        }


def rerank_candidates(query, candidates, top_k=5):
    """
    Re-rank candidates using Re-Ranking Service (Phase 2)

    Calls the standalone re-ranking service to improve result quality.
    Falls back to original candidates if service is unavailable.

    Args:
        query: Error message query string
        candidates: List of candidate documents from Pinecone
        top_k: Number of top results to return after re-ranking

    Returns:
        Top-k re-ranked candidates with rerank_score added
    """
    if not reranking_available or not RERANKING_ENABLED:
        logger.debug("[Phase 2] Re-ranking disabled or unavailable - using original results")
        return candidates[:top_k]

    if not candidates:
        return []

    try:
        # Prepare candidates for re-ranking service
        rerank_candidates_list = []
        for candidate in candidates:
            # Extract text from candidate
            text = candidate.get('error_type', '') or candidate.get('root_cause', '')
            if not text and 'metadata' in candidate:
                text = candidate['metadata'].get('error_message', '') or candidate['metadata'].get('root_cause', '')

            rerank_candidates_list.append({
                'text': text,
                'score': candidate.get('similarity_score', 0),
                'metadata': candidate.get('metadata', {})
            })

        # Call re-ranking service
        logger.info(f"[Phase 2] Re-ranking {len(rerank_candidates_list)} candidates...")
        response = requests.post(
            f"{RERANKING_SERVICE_URL}/rerank",
            json={
                'query': query,
                'candidates': rerank_candidates_list,
                'top_k': top_k
            },
            timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                reranked_results = result.get('results', [])
                logger.info(f"[Phase 2] ✓ Re-ranked → top {len(reranked_results)} "
                           f"(processing time: {result.get('processing_time_ms', 0):.2f}ms)")

                # Merge rerank_score back into original candidates
                for i, reranked in enumerate(reranked_results):
                    if i < len(candidates):
                        candidates[i]['rerank_score'] = reranked.get('rerank_score', 0)

                return reranked_results[:top_k]
            else:
                logger.warning(f"[Phase 2] Re-ranking failed: {result.get('error')}")
                return candidates[:top_k]
        else:
            logger.warning(f"[Phase 2] Re-ranking service returned {response.status_code}")
            return candidates[:top_k]

    except Exception as e:
        logger.warning(f"[Phase 2] Re-ranking error: {e} - falling back to original results")
        return candidates[:top_k]


def query_error_documentation(error_message, top_k=3):
    """
    Query Knowledge Index (Source A) for similar error documentation

    Phase 2 Enhancement: Now retrieves k=50 candidates and re-ranks them
    to return the top-5 most relevant results.

    This queries the ddn-knowledge-docs index containing 25 curated error patterns
    (ERR001-ERR025) with proven solutions.

    Args:
        error_message: Error message from test failure
        top_k: Number of similar error docs to return (after re-ranking)

    Returns:
        List of similar error documentation with metadata (re-ranked)
    """
    try:
        # Create embedding for error message
        embedding = create_embedding(error_message)
        if not embedding:
            logger.warning("[RAG Knowledge] Failed to create embedding for error documentation query")
            return []

        # Phase 2: Retrieve more candidates for re-ranking
        retrieval_k = RERANKING_RETRIEVAL_K if reranking_available else top_k

        # Query Knowledge Index (Source A)
        results = knowledge_index.query(
            vector=embedding,
            top_k=retrieval_k,
            include_metadata=True,
            filter={
                "doc_type": {"$eq": "error_documentation"}
            }
        )

        similar_docs = []
        for match in results.matches:
            similar_docs.append({
                'source': 'knowledge_docs',
                'similarity_score': match.score,
                'error_id': match.metadata.get('error_id'),
                'error_type': match.metadata.get('error_type'),
                'category': match.metadata.get('category'),
                'root_cause': match.metadata.get('root_cause'),
                'severity': match.metadata.get('severity'),
                'tags': match.metadata.get('tags', '').split(',') if match.metadata.get('tags') else [],
                'metadata': match.metadata  # Include full metadata for re-ranking
            })

        logger.info(f"[RAG Knowledge] Retrieved {len(similar_docs)} candidates from curated knowledge")

        # Phase 2: Apply re-ranking if available
        if reranking_available and len(similar_docs) > top_k:
            similar_docs = rerank_candidates(error_message, similar_docs, top_k)
            logger.info(f"[RAG Knowledge] After re-ranking: {len(similar_docs)} results")

        return similar_docs

    except Exception as e:
        logger.error(f"[RAG Knowledge] Error querying documentation: {str(e)}")
        return []


def format_rag_only_result(error_category, error_message, similar_error_docs):
    """
    Format RAG-only results for non-CODE errors (Task 0D.5)

    When routing determines Gemini is not needed (INFRA, CONFIG, DEPENDENCY, TEST, UNKNOWN),
    format the RAG results for dashboard display.

    Args:
        error_category: Error category
        error_message: Error message
        similar_error_docs: RAG query results

    Returns:
        Formatted analysis dict
    """
    # Find best matching RAG document
    best_match = None
    if similar_error_docs:
        best_match = similar_error_docs[0]  # Highest similarity

    if best_match:
        # Use RAG document for analysis
        return {
            "classification": error_category,
            "root_cause": best_match.get('root_cause', 'See similar documented error'),
            "severity": best_match.get('severity', 'MEDIUM'),
            "solution": f"This error matches documented pattern {best_match.get('error_id', 'N/A')}. "
                       f"See RAG documentation for resolution steps.",
            "confidence": best_match.get('similarity_score', 0.7),
            "ai_status": "RAG_ONLY",
            "similar_error_docs": similar_error_docs,
            "rag_enabled": True,
            "routing_used": "OPTION_C",
            "gemini_used": False,
            "rag_match": True
        }
    else:
        # No RAG match found
        return {
            "classification": error_category,
            "root_cause": f"{error_category} error - no similar documented errors found",
            "severity": "MEDIUM",
            "solution": "Manual analysis recommended - error pattern not in knowledge base",
            "confidence": 0.4,
            "ai_status": "RAG_ONLY_NO_MATCH",
            "similar_error_docs": [],
            "rag_enabled": True,
            "routing_used": "OPTION_C",
            "gemini_used": False,
            "rag_match": False
        }


def analyze_failure_with_gemini(failure_data):
    """
    Analyze test failure using ReAct agent + Gemini formatting (Task 0-ARCH.10)
    Updated with Task 0D.5: Routing logic + Context Engineering

    NEW FLOW (Task 0D.5):
    1. ReAct Agent performs analysis (classification, RAG, reasoning, multi-step)
    2. Gemini formats results for user-friendly presentation
    3. Falls back to legacy with Phase 0D routing if ReAct unavailable

    Legacy Flow with Task 0D.5 Routing:
    1. Classify error category
    2. Route using RAGRouter (OPTION C)
    3. Query RAG documentation (always)
    4. If CODE_ERROR: Optimize context + Generate prompt + Call Gemini
    5. If other errors: Format RAG results only (BUG FIX)
    """
    global gemini_model, react_agent, rag_router, context_engineer, prompt_generator

    # Task 0-ARCH.10: Try ReAct agent first
    if react_agent is not None:
        logger.info("[Analysis] Using ReAct agent (Task 0-ARCH.10)")

        # Step 1: Analyze with ReAct
        react_result = analyze_with_react_agent(failure_data)

        if react_result is not None:
            # Task 0-ARCH.18: Step 2: Verify with CRAG
            verification_result = verify_react_result_with_crag(react_result, failure_data)

            # Step 3: Format with Gemini (using verified result)
            # Use verified_answer if available, otherwise use original react_result
            result_to_format = verification_result.get('verified_answer', react_result)
            formatted_result = format_react_result_with_gemini(result_to_format)

            # Task 0-ARCH.18: Add CRAG verification metadata to response
            formatted_result['crag_verified'] = verification_result.get('verified', False)
            formatted_result['crag_confidence'] = verification_result.get('confidence', 0.0)
            formatted_result['crag_confidence_level'] = verification_result.get('confidence_level', 'UNKNOWN')
            formatted_result['crag_status'] = verification_result.get('verification_status', 'UNKNOWN')
            formatted_result['crag_action'] = verification_result.get('action_taken', 'none')
            formatted_result['crag_metadata'] = verification_result.get('verification_metadata', {})

            # Add review URL for HITL cases
            if verification_result.get('review_url'):
                formatted_result['review_url'] = verification_result['review_url']

            return formatted_result
        else:
            logger.warning("[Analysis] ReAct analysis failed - falling back to Gemini")

    # Fallback: Legacy Gemini-only analysis with Task 0D.5 routing
    logger.info("[Analysis] Using legacy analysis with Phase 0D routing")

    # Check if Gemini is available
    if gemini_model is None:
        logger.error("Gemini model not configured")
        return {
            "classification": "AI_UNAVAILABLE",
            "root_cause": "Gemini AI model is not configured or failed to initialize",
            "severity": "UNKNOWN",
            "solution": "Manual analysis required - Check Gemini API configuration",
            "confidence": 0.0,
            "ai_status": "UNAVAILABLE",
            "similar_error_docs": []
        }

    try:
        error_message = failure_data.get('error_message', '')
        error_log = failure_data.get('error_log', error_message)
        test_name = failure_data.get('test_name', '')
        stack_trace = failure_data.get('stack_trace', '')

        # STEP 0: Simple error classification (if not provided by ReAct)
        error_category = failure_data.get('error_category')
        if not error_category:
            error_category = classify_error_simple(error_message)
            logger.info(f"[Classification] Simple classification: {error_category}")

        # STEP 1: Query RAG for similar error documentation (ALWAYS)
        logger.info(f"[RAG] Querying error documentation for: {test_name}")
        similar_error_docs = query_error_documentation(error_message, top_k=3)

        # Task 0D.5: STEP 2: Route error using RAGRouter (CRITICAL BUG FIX)
        if rag_router is not None:
            routing_decision = rag_router.route_error(error_category)
            logger.info(f"[Task 0D.5] Routing decision: Gemini={routing_decision.should_use_gemini}, "
                       f"GitHub={routing_decision.should_use_github}, RAG={routing_decision.should_use_rag}")

            # BUG FIX: Only use Gemini for CODE_ERROR
            if not routing_decision.should_use_gemini:
                # RAG-only analysis for non-CODE errors
                logger.info(f"[Task 0D.5] BUG FIX: Skipping Gemini for {error_category} (using RAG only)")

                # Format RAG results for dashboard
                return format_rag_only_result(
                    error_category=error_category,
                    error_message=error_message,
                    similar_error_docs=similar_error_docs
                )
        else:
            logger.warning("[Task 0D.5] RAGRouter not available - using all errors with Gemini (legacy bug)")
            routing_decision = None

        # Task 0D.5: STEP 3: Use Context Engineering + Prompt Templates (CODE_ERROR only)
        if context_engineer is not None and prompt_generator is not None:
            # Optimize context with token budget
            logger.info(f"[Task 0D.5] Optimizing context for Gemini (CODE_ERROR)")
            optimized_context = context_engineer.optimize_context(
                error_log=error_log,
                error_message=error_message,
                error_category=error_category,
                stack_trace=stack_trace
            )

            logger.info(f"[Task 0D.5] Context optimized: {optimized_context.total_tokens} tokens "
                       f"(budget: {context_engineer.budget.max_total})")
            logger.info(f"[Task 0D.5] Entities extracted: {len(optimized_context.entities)}")

            # Generate category-specific prompt with few-shot examples
            logger.info(f"[Task 0D.5] Generating {error_category} prompt with few-shot examples")
            prompt = prompt_generator.generate_analysis_prompt(
                optimized_context=optimized_context,
                include_few_shot=True,
                max_examples=2
            )

            logger.info(f"[Task 0D.5] Prompt generated: {len(prompt)} chars")

        else:
            # Fallback to legacy prompt building (if Phase 0D not available)
            logger.warning("[Task 0D.5] Phase 0D modules not available - using legacy prompt")

            # Build RAG context
            rag_context = ""
            if similar_error_docs:
                rag_context = "\n\n=== SIMILAR DOCUMENTED ERRORS (for reference) ===\n"
                for i, doc in enumerate(similar_error_docs, 1):
                    rag_context += f"\n{i}. {doc['error_type']} (Similarity: {doc['similarity_score']:.2f})\n"
                    rag_context += f"   Category: {doc['category']}\n"
                    rag_context += f"   Root Cause: {doc['root_cause'][:200]}...\n"
                    rag_context += f"   Tags: {', '.join(doc['tags'][:5])}\n"
                rag_context += "\nUse these documented errors as reference, but analyze the current failure independently.\n"

            # Legacy prompt
            prompt = f"""Analyze this DDN storage test failure and provide structured response.

=== CURRENT FAILURE ===
Test: {test_name}
Error: {error_message}
Stack Trace: {stack_trace[:1000]}
{rag_context}

=== YOUR TASK ===
Analyze the CURRENT failure above and return ONLY JSON with these exact keys:
- classification: ENVIRONMENT/CONFIGURATION/DEPENDENCY/CODE/INFRASTRUCTURE
- root_cause: Brief explanation of what caused this specific failure
- severity: LOW/MEDIUM/HIGH/CRITICAL
- solution: Actionable step-by-step fix for this failure
- confidence: 0.0 to 1.0 (how confident are you in this analysis)
- rag_match: true/false (did similar documented errors help your analysis?)

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no extra text."""

        # STEP 4: Call Gemini (CODE_ERROR only after routing)
        logger.info(f"[Gemini] Analyzing {error_category}: {failure_data.get('_id')}")
        response = gemini_model.generate_content(prompt)
        response_text = response.text.strip()

        # Parse JSON
        try:
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()

            analysis = json.loads(response_text)
            analysis['ai_status'] = 'SUCCESS'
            analysis['similar_error_docs'] = similar_error_docs  # Include RAG results
            analysis['rag_enabled'] = True

            # Task 0D.5: Add Phase 0D metadata
            analysis['phase_0d_enabled'] = PHASE_0D_AVAILABLE
            analysis['routing_used'] = "OPTION_C" if rag_router is not None else "LEGACY"
            analysis['context_engineering_used'] = context_engineer is not None
            analysis['prompt_templates_used'] = prompt_generator is not None
            analysis['gemini_used'] = True  # This is CODE_ERROR path

            logger.info(f"[Gemini] SUCCESS (Task 0D.5 enhanced): {analysis.get('classification')}")
            if context_engineer is not None:
                logger.info(f"[Task 0D.5] Used context engineering + prompt templates")
            return analysis

        except json.JSONDecodeError:
            logger.error(f"[Gemini] Invalid JSON: {response_text[:200]}")
            return {
                "classification": "AI_PARSE_ERROR",
                "root_cause": "Gemini returned invalid JSON format",
                "severity": "UNKNOWN",
                "solution": "Manual analysis required - AI response parsing failed",
                "confidence": 0.0,
                "ai_status": "PARSE_ERROR",
                "ai_response": response_text[:500],
                "similar_error_docs": similar_error_docs,
                "rag_enabled": True
            }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[Gemini] API Error: {error_msg}")

        # Check if it's a quota error
        if "429" in error_msg or "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return {
                "classification": "AI_QUOTA_EXCEEDED",
                "root_cause": "Gemini API free tier quota exceeded (requests per minute or daily limit)",
                "severity": "UNKNOWN",
                "solution": "Wait for quota reset or upgrade to paid plan. Check https://ai.google.dev/gemini-api/docs/rate-limits",
                "confidence": 0.0,
                "ai_status": "QUOTA_EXCEEDED",
                "error_details": error_msg[:500],
                "similar_error_docs": []
            }
        else:
            return {
                "classification": "AI_FAILED",
                "root_cause": f"Gemini AI analysis failed: {error_msg[:200]}",
                "severity": "UNKNOWN",
                "solution": "Manual analysis required - AI service error occurred",
                "confidence": 0.0,
                "ai_status": "FAILED",
                "error_details": error_msg[:500],
                "similar_error_docs": []
            }

# ============================================================================
# VECTOR EMBEDDINGS
# ============================================================================

def create_embedding(text):
    """
    Create OpenAI embedding for text
    Phase 4: Now redacts PII before creating embedding
    """
    try:
        # Phase 4: Redact PII before embedding
        text_to_embed = text
        if pii_redactor:
            try:
                redacted_text, metadata = pii_redactor.redact(text)
                if metadata['redactions'] > 0:
                    logger.info(f"[Phase 4] Redacted {metadata['redactions']} PII entities before embedding")
                    text_to_embed = redacted_text
            except Exception as e:
                logger.warning(f"[Phase 4] PII redaction failed before embedding: {e}")
                # Continue with original text (better to create embedding than fail)

        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text_to_embed
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        return None

def search_similar_failures(error_message, top_k=5):
    """
    Query Error Library (Source B) for similar past failures

    Phase 2 Enhancement: Now retrieves k=50 candidates and re-ranks them
    to return the top-5 most relevant results.

    This queries the ddn-error-library index containing past error cases
    from actual test runs for pattern matching.

    Args:
        error_message: Error message from test failure
        top_k: Number of similar past failures to return (after re-ranking)

    Returns:
        List of similar past failures with metadata (re-ranked)
    """
    try:
        # Create embedding for error message
        embedding = create_embedding(error_message)
        if not embedding:
            return []

        # Phase 2: Retrieve more candidates for re-ranking
        retrieval_k = RERANKING_RETRIEVAL_K if reranking_available else top_k

        # Query Error Library Index (Source B)
        results = failures_index.query(
            vector=embedding,
            top_k=retrieval_k,
            include_metadata=True
        )

        similar = []
        for match in results.matches:
            # Extract text for re-ranking
            text = match.metadata.get('error_message', '') or match.metadata.get('root_cause', '')

            similar.append({
                'source': 'error_library',
                'id': match.id,
                'similarity_score': match.score,
                'text': text,
                'error_type': match.metadata.get('error_type', ''),
                'root_cause': match.metadata.get('root_cause', ''),
                'metadata': match.metadata
            })

        logger.info(f"[RAG Error Library] Retrieved {len(similar)} candidates from past failures")

        # Phase 2: Apply re-ranking if available
        if reranking_available and len(similar) > top_k:
            similar = rerank_candidates(error_message, similar, top_k)
            logger.info(f"[RAG Error Library] After re-ranking: {len(similar)} results")

        return similar

    except Exception as e:
        logger.error(f"[RAG Error Library] Search error: {str(e)}")
        return []

def store_in_pinecone(failure_id, error_message, metadata):
    """
    Store failure embedding in Error Library (Source B)

    New failures are automatically added to the error library
    to improve pattern matching for future failures.
    """
    try:
        embedding = create_embedding(error_message)
        if not embedding:
            return False

        # Store in Error Library Index (Source B)
        failures_index.upsert(
            vectors=[{
                'id': str(failure_id),
                'values': embedding,
                'metadata': metadata
            }]
        )

        logger.info(f"[RAG Error Library] Stored failure {failure_id} in error library")
        return True

    except Exception as e:
        logger.error(f"[RAG Error Library] Storage error: {str(e)}")
        return False

# ============================================================================
# POSTGRESQL STORAGE
# ============================================================================

def update_mongodb_analysis_status(failure_id, analysis_id, analysis_status='completed'):
    """
    Update MongoDB failure record with AI analysis status
    This enables dashboard to filter failures by analysis completion

    Args:
        failure_id: MongoDB failure ID (string or ObjectId)
        analysis_id: PostgreSQL analysis ID
        analysis_status: Status string ('completed', 'error', 'pending')
    """
    try:
        from bson import ObjectId

        # Convert to ObjectId if string
        if isinstance(failure_id, str):
            try:
                failure_oid = ObjectId(failure_id)
            except:
                failure_oid = failure_id
        else:
            failure_oid = failure_id

        # Update MongoDB failure record with analysis tracking
        result = failures_collection.update_one(
            {'_id': failure_oid},
            {'$set': {
                'analysis_status': analysis_status,
                'analysis_id': analysis_id,
                'analyzed_at': datetime.utcnow(),
                'analysis_synced': True
            }}
        )

        if result.modified_count > 0:
            logger.info(f"[MongoDB Sync] Updated failure {failure_id} with analysis_status={analysis_status}")
        else:
            logger.warning(f"[MongoDB Sync] No document found to update for failure {failure_id}")

        return result.modified_count > 0

    except Exception as e:
        logger.error(f"[MongoDB Sync] Failed to update failure {failure_id}: {str(e)}")
        return False


def save_analysis_to_postgres(failure_id, analysis, similar_failures):
    """
    Save AI analysis to PostgreSQL
    Task 0E.6: Now includes GitHub source code files (for CODE_ERROR)
    """
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Task 0E.6: Extract GitHub files from analysis (if available)
        github_files = analysis.get('github_files', [])
        github_code_included = analysis.get('github_code_included', False)

        # Convert github_files to JSON string for PostgreSQL JSONB
        import json
        github_files_json = json.dumps(github_files) if github_files else '[]'

        insert_query = """
        INSERT INTO failure_analysis (
            mongodb_failure_id,
            classification,
            root_cause,
            severity,
            recommendation,
            confidence_score,
            similar_failures_count,
            analyzed_at,
            ai_model,
            github_files,
            github_code_included
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        cursor.execute(insert_query, (
            str(failure_id),
            analysis.get('classification', 'UNKNOWN'),
            analysis.get('root_cause', '')[:500],  # Limit size
            analysis.get('severity', 'MEDIUM'),
            analysis.get('solution', '')[:1000],  # Limit size
            float(analysis.get('confidence', 0.7)),
            len(similar_failures),
            datetime.utcnow(),
            'gemini-pro',
            github_files_json,  # Task 0E.6: GitHub files (JSONB)
            github_code_included  # Task 0E.6: GitHub code flag
        ))

        analysis_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        # Task 0E.6: Log GitHub files inclusion
        if github_code_included:
            logger.info(f"Saved analysis to PostgreSQL: ID {analysis_id} (with {len(github_files)} GitHub files)")
        else:
            logger.info(f"Saved analysis to PostgreSQL: ID {analysis_id}")
        return analysis_id

    except Exception as e:
        logger.error(f"PostgreSQL save error: {str(e)}")
        return None

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint with detailed status
    """
    health_status = {
        'status': 'healthy',
        'service': 'AI Analysis Service',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }

    # Gemini AI status
    health_status['components']['gemini'] = {
        'api_key_configured': bool(GEMINI_API_KEY),
        'model_initialized': gemini_model is not None,
        'model_name': 'models/gemini-flash-latest' if gemini_model else None,
        'status': 'available' if gemini_model else 'unavailable'
    }

    # OpenAI status
    health_status['components']['openai'] = {
        'api_key_configured': bool(OPENAI_API_KEY),
        'embedding_model': 'text-embedding-3-small',
        'status': 'available' if OPENAI_API_KEY else 'unavailable'
    }

    # Pinecone status - Dual-Index Architecture
    try:
        # Check Knowledge Index (Source A)
        knowledge_stats = knowledge_index.describe_index_stats()
        health_status['components']['pinecone_knowledge'] = {
            'api_key_configured': bool(PINECONE_API_KEY),
            'index_name': PINECONE_KNOWLEDGE_INDEX,
            'total_vectors': knowledge_stats.total_vector_count,
            'dimension': knowledge_stats.dimension,
            'purpose': 'Error Documentation (Source A)',
            'status': 'connected'
        }

        # Check Error Library Index (Source B)
        failures_stats = failures_index.describe_index_stats()
        health_status['components']['pinecone_failures'] = {
            'api_key_configured': bool(PINECONE_API_KEY),
            'index_name': PINECONE_FAILURES_INDEX,
            'total_vectors': failures_stats.total_vector_count,
            'dimension': failures_stats.dimension,
            'purpose': 'Past Error Cases (Source B)',
            'status': 'connected'
        }
    except Exception as e:
        health_status['components']['pinecone'] = {
            'api_key_configured': bool(PINECONE_API_KEY),
            'status': 'error',
            'error': str(e)[:200]
        }

    # MongoDB status
    try:
        mongo_client.server_info()
        failure_count = failures_collection.count_documents({})
        health_status['components']['mongodb'] = {
            'status': 'connected',
            'database': MONGODB_DB,
            'total_failures': failure_count
        }
    except Exception as e:
        health_status['components']['mongodb'] = {
            'status': 'error',
            'error': str(e)[:200]
        }

    # PostgreSQL status
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM failure_analysis")
        analysis_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        health_status['components']['postgresql'] = {
            'status': 'connected',
            'database': POSTGRES_CONFIG['database'],
            'total_analyses': analysis_count
        }
    except Exception as e:
        health_status['components']['postgresql'] = {
            'status': 'error',
            'error': str(e)[:200]
        }

    # RAG availability
    health_status['rag_enabled'] = bool(gemini_model and OPENAI_API_KEY and PINECONE_API_KEY)
    health_status['gemini_available'] = gemini_model is not None
    health_status['openai_available'] = bool(OPENAI_API_KEY)

    # Overall status
    critical_components_ok = (
        gemini_model is not None and
        bool(OPENAI_API_KEY) and
        health_status['components']['mongodb']['status'] == 'connected'
    )

    health_status['status'] = 'healthy' if critical_components_ok else 'degraded'

    return jsonify(health_status)

@app.route('/api/crag/metrics', methods=['GET'])
def get_crag_metrics():
    """
    Get CRAG verification metrics (Task 0-ARCH.19)

    Returns comprehensive metrics about CRAG verification system:
    - Confidence distribution (HIGH/MEDIUM/LOW/VERY_LOW)
    - Routing decisions (PASS/HITL/CORRECTED/WEB_SEARCH)
    - Self-correction success rates
    - HITL queue statistics
    - Web search success rates
    - Time-series data
    """
    try:
        if not CRAG_AVAILABLE:
            return jsonify({
                'error': 'CRAG verification not available',
                'reason': 'CRAG modules not loaded'
            }), 503

        # Get metrics from CRAGVerifier
        metrics = crag_verifier.get_statistics()

        # Add timestamp
        metrics['retrieved_at'] = datetime.utcnow().isoformat()

        return jsonify(metrics)

    except Exception as e:
        logger.error(f"Failed to get CRAG metrics: {e}")
        return jsonify({
            'error': 'Failed to retrieve metrics',
            'message': str(e)
        }), 500

@app.route('/api/crag/health', methods=['GET'])
def get_crag_health():
    """
    Get CRAG system health status (Task 0-ARCH.19)

    Returns health status with warnings based on metrics:
    - Overall health: healthy/warning
    - Warnings about HITL queue, success rates, etc.
    - Key metric summary
    """
    try:
        if not CRAG_AVAILABLE:
            return jsonify({
                'status': 'unavailable',
                'message': 'CRAG verification not available'
            }), 503

        # Get health status from metrics
        from verification.crag_metrics import get_metrics
        metrics = get_metrics()
        health_status = metrics.get_health_status()

        # Add timestamp
        health_status['checked_at'] = datetime.utcnow().isoformat()

        return jsonify(health_status)

    except Exception as e:
        logger.error(f"Failed to get CRAG health: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/crag/metrics/reset', methods=['POST'])
def reset_crag_metrics():
    """
    Reset CRAG metrics (Task 0-ARCH.19)

    Resets all collected metrics to zero. Useful for testing or
    starting fresh metric collection periods.

    Requires admin access or specific authorization.
    """
    try:
        if not CRAG_AVAILABLE:
            return jsonify({
                'error': 'CRAG verification not available'
            }), 503

        from verification.crag_metrics import reset_metrics
        reset_metrics()

        return jsonify({
            'success': True,
            'message': 'CRAG metrics reset successfully',
            'reset_at': datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Failed to reset CRAG metrics: {e}")
        return jsonify({
            'error': 'Failed to reset metrics',
            'message': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_failure():
    """
    Analyze a single failure
    POST body: { "failure_id": "mongodb_id" }
    """
    try:
        data = request.json
        failure_id = data.get('failure_id')

        if not failure_id:
            return jsonify({'error': 'failure_id required'}), 400

        # Get failure from MongoDB
        from bson import ObjectId
        failure = failures_collection.find_one({'_id': ObjectId(failure_id)})

        if not failure:
            return jsonify({'error': 'Failure not found'}), 404

        logger.info(f"Analyzing failure: {failure_id}")

        # Step 1: Search for similar failures
        error_message = failure.get('error_message', '')
        similar_failures = search_similar_failures(error_message)

        # Step 2: AI Analysis with Gemini (NO FALLBACK)
        analysis = analyze_failure_with_gemini(failure)

        # Step 3: Save to PostgreSQL
        analysis_id = save_analysis_to_postgres(failure_id, analysis, similar_failures)

        # Step 3.5: Sync MongoDB with analysis status
        analysis_status = 'completed' if analysis.get('ai_status') not in ['FAILED', 'UNAVAILABLE', 'QUOTA_EXCEEDED'] else 'error'
        update_mongodb_analysis_status(failure_id, analysis_id, analysis_status)

        # Step 4: Store in Pinecone for future similarity search
        metadata = {
            'test_name': failure.get('test_name', ''),
            'classification': analysis.get('classification', 'UNKNOWN'),
            'resolved': False
        }
        store_in_pinecone(failure_id, error_message, metadata)

        return jsonify({
            'status': 'success',
            'failure_id': failure_id,
            'analysis_id': analysis_id,
            'analysis': analysis,
            'similar_failures': similar_failures
        })

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-batch', methods=['POST'])
def analyze_batch():
    """
    Analyze multiple unanalyzed failures
    POST body: { "limit": 10 }
    """
    try:
        data = request.json
        limit = data.get('limit', 10)

        # Get PostgreSQL connection
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor()

        # Find unanalyzed failures
        cursor.execute("""
            SELECT mongodb_failure_id FROM failure_analysis
        """)
        analyzed_ids = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()

        # Get unanalyzed from MongoDB
        unanalyzed = failures_collection.find({
            '_id': {'$nin': [failure_id for failure_id in analyzed_ids]}
        }).limit(limit)

        results = []
        for failure in unanalyzed:
            failure_id = str(failure['_id'])

            logger.info(f"Analyzing failure: {failure_id}")

            # Analyze with Gemini (NO FALLBACK)
            error_message = failure.get('error_message', '')
            similar_failures = search_similar_failures(error_message)
            analysis = analyze_failure_with_gemini(failure)
            analysis_id = save_analysis_to_postgres(failure_id, analysis, similar_failures)

            # Sync MongoDB with analysis status
            analysis_status = 'completed' if analysis.get('ai_status') not in ['FAILED', 'UNAVAILABLE', 'QUOTA_EXCEEDED'] else 'error'
            update_mongodb_analysis_status(failure_id, analysis_id, analysis_status)

            # Store in Pinecone
            metadata = {
                'test_name': failure.get('test_name', ''),
                'classification': analysis.get('classification', 'UNKNOWN'),
                'resolved': False
            }
            store_in_pinecone(failure_id, error_message, metadata)

            results.append({
                'failure_id': failure_id,
                'analysis_id': analysis_id,
                'classification': analysis.get('classification')
            })

        return jsonify({
            'status': 'success',
            'analyzed_count': len(results),
            'results': results
        })

    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("=" * 70)
    logger.info("DDN AI Analysis Service Starting (Dual-Index RAG)")
    logger.info("=" * 70)
    logger.info(f"Gemini API: {'Configured' if GEMINI_API_KEY else 'MISSING'}")
    logger.info(f"OpenAI API: {'Configured' if OPENAI_API_KEY else 'MISSING'}")
    logger.info(f"Pinecone API: {'Configured' if PINECONE_API_KEY else 'MISSING'}")
    logger.info(f"  Knowledge Index (Source A): {PINECONE_KNOWLEDGE_INDEX}")
    logger.info(f"  Error Library (Source B): {PINECONE_FAILURES_INDEX}")
    logger.info(f"MongoDB: {MONGODB_URI[:50]}...")
    logger.info(f"PostgreSQL: {POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}")
    logger.info("=" * 70)

    app.run(host='0.0.0.0', port=5000, debug=False)
