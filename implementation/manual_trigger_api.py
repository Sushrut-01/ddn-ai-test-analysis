"""
Manual Trigger & Feedback API for DDN AI Test Failure Analysis
Phase 2 Implementation: Manual triggers and feedback loop

Endpoints:
- POST /api/trigger-analysis - Manual trigger for specific build
- POST /api/feedback - Submit feedback on AI recommendation
- GET /api/feedback/:build_id - Get feedback for a build
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
import json

# MongoDB Atlas for build context
from pymongo import MongoClient

# Claude SDK for deep analysis
import anthropic

# Google Gemini SDK for AI analysis
import google.generativeai as genai

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for dashboard access

# Configuration
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:password@postgres:5432/ddn_ai_analysis")  # Docker network

# ============================================================================
# AGENTIC WORKFLOW CONFIGURATION (Pure Python - no n8n dependency)
# ============================================================================
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://sushrutnistane097_db_user:Sharu%40051220@ddn-cluster.wudcfln.mongodb.net/ddn_tests")
MONGODB_DB = os.getenv("MONGODB_DB", "ddn_tests")
LANGGRAPH_URL = os.getenv("LANGGRAPH_URL", "http://ddn-langgraph:5000")
DASHBOARD_API_URL = os.getenv("DASHBOARD_API_URL", "http://ddn-dashboard-api:5006")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# Configure Gemini if API key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
AUTO_FIX_CONFIDENCE_THRESHOLD = float(os.getenv("AUTO_FIX_CONFIDENCE_THRESHOLD", "0.70"))

# PostgreSQL connection
def get_db_connection():
    """Get PostgreSQL database connection"""
    try:
        conn = psycopg2.connect(POSTGRES_URI)
        return conn
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        raise


# ============================================================================
# AGENTIC TRIGGER HELPER FUNCTIONS (DDN AgenticTrigger - Python Implementation)
# ============================================================================

def get_mongodb_client():
    """Get MongoDB Atlas connection for build context"""
    try:
        client = MongoClient(MONGODB_URI)
        return client[MONGODB_DB]
    except Exception as e:
        logger.error(f"❌ MongoDB Atlas connection failed: {e}")
        raise


def route_by_classification(classification: dict) -> str:
    """
    OPTION C Routing Logic:
    - CODE_ERROR or needs_code_analysis=True → 'claude_mcp' (deep analysis)
    - All other categories → 'rag' (fast path, 80% of cases)
    """
    error_category = classification.get('error_category', '')
    needs_code = classification.get('needs_code_analysis', False)

    if error_category == 'CODE_ERROR' or needs_code:
        logger.info(f"🔀 Routing to Claude MCP (CODE_ERROR or needs_code_analysis)")
        return 'claude_mcp'
    else:
        logger.info(f"🔀 Routing to RAG fast path (category: {error_category})")
        return 'rag'


def analyze_with_claude_mcp(build_data: dict, classification: dict) -> dict:
    """
    Deep analysis using Claude for CODE_ERROR category
    Used when code inspection is needed for precise root cause analysis.
    """
    if not ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEY not set - cannot use Claude analysis")
        return {
            "root_cause": "Claude analysis unavailable - API key not configured",
            "fix_recommendation": "Please configure ANTHROPIC_API_KEY",
            "confidence_score": 0.0,
            "analysis_type": "CLAUDE_ANALYSIS_UNAVAILABLE"
        }

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""**CODE ERROR ANALYSIS REQUEST**

**Build Information:**
- Build ID: {build_data.get('build_id')}
- Job: {build_data.get('job_name')}
- Repository: {build_data.get('repository', 'N/A')}
- Branch: {build_data.get('branch', 'N/A')}

**Error Log:**
```
{str(build_data.get('error_log', ''))[:2000]}
```

**Stack Trace:**
```
{str(build_data.get('stack_trace', ''))[:1500]}
```

**Similar Past Issues (from RAG):**
{json.dumps(classification.get('similar_solutions', [])[:3], indent=2, default=str)}

**YOUR TASK:**
1. Analyze the error deeply
2. Identify root cause with technical precision
3. Provide specific fix recommendation with code examples
4. Include prevention strategy

**OUTPUT FORMAT (strict JSON):**
```json
{{
  "root_cause": "Technical explanation of why this error occurred",
  "fix_recommendation": "Step-by-step instructions to fix the issue",
  "code_fix": "Actual code fix or configuration change",
  "prevention_strategy": "How to prevent this in the future",
  "confidence_score": 0.90,
  "files_to_modify": ["file1.py", "file2.py"]
}}
```"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Extract JSON from response
        json_match = text.find('```json')
        if json_match != -1:
            json_end = text.find('```', json_match + 7)
            json_str = text[json_match + 7:json_end].strip()
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                result = {
                    "root_cause": text[:500],
                    "fix_recommendation": text[:1000],
                    "confidence_score": 0.85
                }
        else:
            result = {
                "root_cause": text[:500],
                "fix_recommendation": text[:1000],
                "confidence_score": 0.85
            }

        # Add cost tracking
        result['token_usage'] = response.usage.input_tokens + response.usage.output_tokens
        result['analysis_type'] = 'CLAUDE_DEEP_ANALYSIS'
        result['estimated_cost_usd'] = round(
            (response.usage.input_tokens / 1000000 * 3.00) +
            (response.usage.output_tokens / 1000000 * 15.00), 4
        )

        logger.info(f"✅ Claude analysis complete - tokens: {result['token_usage']}, cost: ${result['estimated_cost_usd']}")
        return result

    except Exception as e:
        logger.error(f"❌ Claude analysis failed: {e}")
        return {
            "root_cause": f"Analysis failed: {str(e)}",
            "fix_recommendation": "Please retry or use RAG fallback",
            "confidence_score": 0.0,
            "analysis_type": "CLAUDE_ANALYSIS_FAILED",
            "token_usage": 0,
            "estimated_cost_usd": 0
        }


def analyze_with_gemini(build_data: dict, classification: dict) -> dict:
    """
    Deep analysis using Google Gemini for CODE_ERROR category.
    Used when Claude is not available or as primary AI.
    """
    if not GEMINI_API_KEY:
        logger.error("❌ GEMINI_API_KEY not set - cannot use Gemini analysis")
        return {
            "root_cause": "Gemini analysis unavailable - API key not configured",
            "fix_recommendation": "Please configure GEMINI_API_KEY",
            "confidence_score": 0.0,
            "analysis_type": "GEMINI_ANALYSIS_UNAVAILABLE"
        }

    prompt = f"""**CODE ERROR ANALYSIS REQUEST**

**Build Information:**
- Build ID: {build_data.get('build_id')}
- Job: {build_data.get('job_name')}
- Test Name: {build_data.get('test_name', 'N/A')}
- Repository: {build_data.get('repository', 'N/A')}
- Branch: {build_data.get('branch', 'N/A')}

**Error Message:**
```
{str(build_data.get('error_message', build_data.get('error_log', '')))[:2000]}
```

**Stack Trace:**
```
{str(build_data.get('stack_trace', ''))[:1500]}
```

**Similar Past Issues (from RAG):**
{json.dumps(classification.get('similar_solutions', [])[:3], indent=2, default=str)}

**YOUR TASK:**
1. Analyze the error deeply and understand the root cause
2. Identify root cause with technical precision
3. Provide specific fix recommendation with code examples if applicable
4. Include prevention strategy

**OUTPUT FORMAT (strict JSON only, no markdown):**
{{
  "error_category": "CODE_ERROR|ENV_CONFIG|NETWORK_ERROR|INFRA_ERROR",
  "root_cause": "Technical explanation of why this error occurred",
  "fix_recommendation": "Step-by-step instructions to fix the issue",
  "code_fix": "Actual code fix or configuration change if applicable",
  "prevention_strategy": "How to prevent this in the future",
  "confidence_score": 0.90,
  "files_to_modify": ["file1.py", "file2.py"]
}}"""

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                max_output_tokens=4000,
            )
        )

        text = response.text
        logger.info(f"📝 Gemini raw response: {text[:500]}...")

        # Extract JSON from response
        result = None

        # Try to find JSON in response
        json_match = text.find('{')
        if json_match != -1:
            json_end = text.rfind('}') + 1
            json_str = text[json_match:json_end]
            try:
                result = json.loads(json_str)
                logger.info(f"✅ Parsed JSON from Gemini response")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parse failed: {e}")

        # Fallback: extract from markdown code block
        if not result and '```json' in text:
            json_start = text.find('```json') + 7
            json_end = text.find('```', json_start)
            json_str = text[json_start:json_end].strip()
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Final fallback
        if not result:
            result = {
                "root_cause": text[:500],
                "fix_recommendation": text[:1000],
                "confidence_score": 0.80,
                "error_category": classification.get('error_category', 'UNKNOWN')
            }

        # Add metadata
        result['analysis_type'] = 'GEMINI_DEEP_ANALYSIS'
        result['ai_model'] = 'gemini-1.5-pro'
        result['token_usage'] = 0  # Gemini doesn't expose token count easily
        result['estimated_cost_usd'] = 0.005  # Gemini is cheaper

        logger.info(f"✅ Gemini analysis complete - category: {result.get('error_category')}")
        return result

    except Exception as e:
        logger.error(f"❌ Gemini analysis failed: {e}")
        return {
            "root_cause": f"Analysis failed: {str(e)}",
            "fix_recommendation": "Please retry or use RAG fallback",
            "confidence_score": 0.0,
            "analysis_type": "GEMINI_ANALYSIS_FAILED",
            "error_category": "UNKNOWN",
            "token_usage": 0,
            "estimated_cost_usd": 0
        }


def get_rag_solution(classification: dict, build_data: dict) -> dict:
    """
    Fast path using RAG retrieval for non-CODE_ERROR categories.
    Uses similar solutions from LangGraph classification (80% of cases).
    """
    solutions = classification.get('similar_solutions', [])
    best_solution = solutions[0] if solutions else {}

    return {
        "build_id": build_data.get('build_id'),
        "analysis_type": "RAG_RETRIEVAL",
        "error_category": classification.get('error_category'),
        "root_cause": best_solution.get('root_cause', 'Based on historical pattern analysis'),
        "fix_recommendation": best_solution.get('solution') or best_solution.get('fix_recommendation', 'Review similar past cases'),
        "prevention_strategy": best_solution.get('prevention', 'Monitor for recurrence'),
        "confidence_score": best_solution.get('confidence', 0.75),
        "similar_cases_found": len(solutions),
        "similar_solutions": solutions[:5],
        "token_usage": 0,
        "estimated_cost_usd": 0.01
    }


def run_agentic_trigger(build_id: str, triggered_by: str) -> dict:
    """
    DDN AgenticTrigger - Complete Python implementation (no n8n)

    Flow:
    1. Get build context from MongoDB Atlas
    2. Call LangGraph /classify-error
    3. OPTION C routing: CODE_ERROR → Claude, others → RAG
    4. Store result via Dashboard API
    5. Return result
    """
    logger.info(f"🎯 AgenticTrigger: Starting analysis for build {build_id}")

    # Step 1: Get build context from MongoDB Atlas
    try:
        mongo_db = get_mongodb_client()
        build_data = mongo_db.builds.find_one({"build_id": build_id})

        if not build_data:
            build_data = mongo_db.test_failures.find_one({"build_id": build_id})

        if not build_data:
            return {
                "status": "error",
                "message": "Build not found in MongoDB",
                "build_id": build_id
            }

        # Convert ObjectId to string for JSON serialization
        if '_id' in build_data:
            build_data['_id'] = str(build_data['_id'])

        # Add console logs if available
        console_log = mongo_db.console_logs.find_one({"build_id": build_id})
        if console_log:
            build_data['stack_trace'] = console_log.get('stack_trace', '')
            build_data['full_console'] = console_log.get('full_log', '')

        logger.info(f"📦 Got build context from MongoDB Atlas")
    except Exception as e:
        logger.error(f"❌ MongoDB error: {e}")
        return {
            "status": "error",
            "message": f"MongoDB error: {str(e)}",
            "build_id": build_id
        }

    # Step 2: Call LangGraph /classify-error
    classification = {}
    try:
        langgraph_response = requests.post(
            f"{LANGGRAPH_URL}/classify-error",
            json={
                "build_id": build_id,
                "error_log": build_data.get('error_log', ''),
                "stack_trace": build_data.get('stack_trace', ''),
                "job_name": build_data.get('job_name', ''),
                "trigger_type": "MANUAL"
            },
            timeout=30
        )
        langgraph_response.raise_for_status()
        classification = langgraph_response.json()
        logger.info(f"🏷️ Classification: {classification.get('error_category')} (confidence: {classification.get('confidence', 0)})")
    except Exception as e:
        logger.warning(f"⚠️ LangGraph classification failed: {e}")
        classification = {
            "error_category": "UNKNOWN",
            "confidence": 0.5,
            "similar_solutions": [],
            "needs_code_analysis": False
        }

    # Step 3: RUN AI ANALYSIS using Gemini (PRIMARY) or Claude (FALLBACK)
    # Now we actually analyze the error with real AI
    error_category = classification.get('error_category', 'UNKNOWN')
    similar_solutions = classification.get('similar_solutions', [])

    logger.info(f"🤖 Starting AI analysis with Gemini for build {build_id}")

    # Use Gemini for AI analysis (primary)
    if GEMINI_API_KEY:
        analysis_result = analyze_with_gemini(build_data, classification)
        logger.info(f"✅ Gemini analysis complete - category: {analysis_result.get('error_category')}")
    # Fallback to Claude if Gemini not available
    elif ANTHROPIC_API_KEY and ANTHROPIC_API_KEY != 'your-anthropic-api-key-here':
        analysis_result = analyze_with_claude_mcp(build_data, classification)
        logger.info(f"✅ Claude analysis complete")
    # Final fallback to RAG solution
    else:
        logger.warning("⚠️ No AI API keys configured - using RAG fallback")
        analysis_result = get_rag_solution(classification, build_data)

    # Update error_category from AI analysis if available
    if analysis_result.get('error_category') and analysis_result.get('error_category') != 'UNKNOWN':
        error_category = analysis_result.get('error_category')

    # Step 4: STORE ANALYSIS RESULT via Dashboard API
    storage_id = None
    try:
        store_response = requests.post(
            f"{DASHBOARD_API_URL}/api/analysis/store",
            json={
                "build_id": build_id,
                "job_name": build_data.get('job_name', ''),
                "test_suite": build_data.get('test_suite', build_data.get('suite_name', '')),
                "error_category": error_category,
                "root_cause": analysis_result.get('root_cause', ''),
                "fix_recommendation": analysis_result.get('fix_recommendation', ''),
                "code_fix": analysis_result.get('code_fix', ''),
                "prevention_strategy": analysis_result.get('prevention_strategy', ''),
                "confidence_score": analysis_result.get('confidence_score', 0.75),
                "analysis_type": analysis_result.get('analysis_type', 'GEMINI_ANALYSIS'),
                "trigger_type": "MANUAL",
                "triggered_by": triggered_by,
                "token_usage": analysis_result.get('token_usage', 0),
                "estimated_cost_usd": analysis_result.get('estimated_cost_usd', 0)
            },
            timeout=30
        )
        store_response.raise_for_status()
        store_result = store_response.json()
        storage_id = store_result.get('analysis_id')
        logger.info(f"✅ Stored analysis via Dashboard API (ID: {storage_id})")
    except Exception as e:
        logger.error(f"❌ Failed to store analysis: {e}")

    # Step 5: ADD TO RAG APPROVAL QUEUE for human validation
    approval_id = None
    rag_suggestion = f"{analysis_result.get('root_cause', '')} - {analysis_result.get('fix_recommendation', '')}"
    try:
        rag_queue_response = requests.post(
            f"{DASHBOARD_API_URL}/api/rag/add",
            json={
                "build_id": build_id,
                "job_name": build_data.get('job_name', ''),
                "error_category": error_category,
                "rag_suggestion": rag_suggestion[:500],
                "rag_confidence": analysis_result.get('confidence_score', 0.75),
                "similar_cases_count": len(similar_solutions),
                "triggered_by": triggered_by,
                "trigger_type": "MANUAL",
                "ai_analysis_id": storage_id
            },
            timeout=10
        )
        rag_queue_response.raise_for_status()
        rag_result = rag_queue_response.json()
        approval_id = rag_result.get('approval_id')
        logger.info(f"📋 Added to RAG approval queue (ID: {approval_id})")
    except Exception as e:
        logger.warning(f"⚠️ Failed to add to RAG queue: {e}")

    # Build final result with AI analysis
    result = {
        "build_id": build_id,
        "job_name": build_data.get('job_name'),
        "test_name": build_data.get('test_name', build_data.get('test_suite')),
        "error_category": error_category,
        "classification": error_category,
        "root_cause": analysis_result.get('root_cause'),
        "fix_recommendation": analysis_result.get('fix_recommendation'),
        "code_fix": analysis_result.get('code_fix'),
        "prevention_strategy": analysis_result.get('prevention_strategy'),
        "confidence_score": analysis_result.get('confidence_score', 0.75),
        "analysis_type": analysis_result.get('analysis_type'),
        "storage_id": storage_id,
        "approval_id": approval_id,
        "similar_cases_count": len(similar_solutions),
        "triggered_by": triggered_by,
        "trigger_type": "MANUAL",
        "timestamp": datetime.now().isoformat(),
        "token_usage": analysis_result.get('token_usage', 0),
        "estimated_cost_usd": analysis_result.get('estimated_cost_usd', 0)
    }

    logger.info(f"✅ AgenticTrigger complete for build {build_id} - AI analysis done")
    return result

# ============================================================================
# WORKFLOW 1: DDN AGENTIC ANALYZER (Auto Analysis from Aging Service)
# ============================================================================

# Teams webhook for notifications
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")


def send_teams_notification(analysis_result: dict) -> bool:
    """
    Send Teams notification for completed analysis.
    Returns True if notification sent successfully.
    """
    if not TEAMS_WEBHOOK_URL:
        logger.info("📭 Teams notification skipped - webhook not configured")
        return False

    try:
        # Build adaptive card payload
        payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [
                            {
                                "type": "TextBlock",
                                "size": "Large",
                                "weight": "Bolder",
                                "text": f"🤖 AI Analysis Complete: {analysis_result.get('build_id')}"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {"title": "Job Name", "value": analysis_result.get('job_name', 'N/A')},
                                    {"title": "Category", "value": analysis_result.get('error_category', 'UNKNOWN')},
                                    {"title": "Confidence", "value": f"{analysis_result.get('confidence_score', 0) * 100:.0f}%"},
                                    {"title": "Analysis Type", "value": analysis_result.get('analysis_type', 'N/A')},
                                    {"title": "Trigger", "value": analysis_result.get('trigger_type', 'AUTOMATIC')}
                                ]
                            },
                            {
                                "type": "TextBlock",
                                "text": f"**Root Cause:** {str(analysis_result.get('root_cause', ''))[:200]}...",
                                "wrap": True
                            }
                        ],
                        "actions": [
                            {
                                "type": "Action.OpenUrl",
                                "title": "View in Dashboard",
                                "url": f"http://localhost:5173/failures/{analysis_result.get('build_id')}"
                            }
                        ]
                    }
                }
            ]
        }

        response = requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Teams notification sent for {analysis_result.get('build_id')}")
            return True
        else:
            logger.warning(f"⚠️ Teams notification failed: {response.status_code}")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Teams notification error: {e}")
        return False


def run_agentic_analyzer(build_id: str, aging_days: int = 0, consecutive_failures: int = 0) -> dict:
    """
    DDN AgenticAnalyzer - Automatic analysis triggered by aging service

    Flow:
    1. Get build context from MongoDB Atlas
    2. Call LangGraph /classify-error
    3. OPTION C routing: CODE_ERROR → Claude, others → RAG
    4. Store result via Dashboard API
    5. Send Teams notification
    6. Return result

    This reuses the same logic as AgenticTrigger but with AUTOMATIC trigger type.
    """
    logger.info(f"🤖 AgenticAnalyzer: Auto analysis for build {build_id} (age: {aging_days}d, failures: {consecutive_failures})")

    # Reuse the core analysis logic from AgenticTrigger
    result = run_agentic_trigger(build_id, "aging_service")

    # Override trigger type for automatic analysis
    result['trigger_type'] = 'AUTOMATIC'
    result['aging_days'] = aging_days
    result['consecutive_failures'] = consecutive_failures

    # Send Teams notification for automatic analysis
    send_teams_notification(result)

    return result


@app.route('/api/auto-analyze', methods=['POST'])
def trigger_auto_analysis():
    """
    DDN AgenticAnalyzer - Automatic analysis endpoint for aging service

    Called by aging_service.py when:
    - Build age > 3 days OR
    - Consecutive failures > 3

    Request:
    {
        "build_id": "DDN-Basic-Tests-85",
        "aging_days": 5,
        "consecutive_failures": 4,
        "triggered_by": "aging_service"
    }

    Response:
    {
        "success": true,
        "message": "Auto analysis completed",
        "data": {...analysis result...}
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data:
            return jsonify({
                "error": "Missing required field: build_id"
            }), 400

        build_id = data['build_id']
        aging_days = data.get('aging_days', 0)
        consecutive_failures = data.get('consecutive_failures', 0)

        logger.info(f"🤖 Auto-analysis requested for build: {build_id}")

        # Pure Python AgenticAnalyzer path (no n8n)
        result = run_agentic_analyzer(build_id, aging_days, consecutive_failures)

        if result.get('status') == 'error':
            return jsonify({
                "success": False,
                "message": result.get('message', 'Analysis failed'),
                "build_id": build_id
            }), 500

        logger.info(f"✅ Auto-analysis complete for build: {build_id}")

        return jsonify({
            "success": True,
            "message": "Auto analysis completed successfully (AgenticAnalyzer)",
            "build_id": build_id,
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"❌ Auto-analysis failed: {e}")
        return jsonify({
            "error": "Auto analysis failed",
            "details": str(e)
        }), 500


# ============================================================================
# MANUAL TRIGGER ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        postgres_connected = True
    except:
        postgres_connected = False

    return jsonify({
        "status": "healthy" if postgres_connected else "degraded",
        "service": "Manual Trigger & Feedback API",
        "version": "2.0.0",
        "postgres_connected": postgres_connected
    }), 200


@app.route('/api/trigger-analysis', methods=['POST'])
def trigger_manual_analysis():
    """
    Manually trigger AI analysis for a specific build

    Request:
    {
        "build_id": "12345",
        "triggered_by_user": "john.doe@company.com",
        "reason": "Critical production issue"
    }

    Response:
    {
        "success": true,
        "message": "Analysis triggered successfully",
        "trigger_id": 123,
        "build_id": "12345",
        "webhook_response": {...}
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data:
            return jsonify({
                "error": "Missing required field: build_id"
            }), 400

        build_id = data['build_id']
        triggered_by_user = data.get('triggered_by_user', 'anonymous')
        reason = data.get('reason', 'Manual trigger from dashboard')
        trigger_source = data.get('trigger_source', 'dashboard')

        logger.info(f"🎯 Manual trigger requested for build: {build_id} by {triggered_by_user}")

        # Get current consecutive failures count from PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT consecutive_failures
            FROM failure_analysis
            WHERE build_id = %s
            ORDER BY timestamp DESC
            LIMIT 1
        """, (build_id,))

        result = cursor.fetchone()
        consecutive_failures = result['consecutive_failures'] if result else 1

        # Log manual trigger in database
        cursor.execute("""
            INSERT INTO manual_trigger_log (
                build_id,
                triggered_by_user,
                trigger_source,
                consecutive_failures_at_trigger,
                reason,
                triggered_at
            ) VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (build_id, triggered_by_user, trigger_source, consecutive_failures, reason))

        trigger_id = cursor.fetchone()['id']
        conn.commit()

        logger.info(f"📝 Manual trigger logged with ID: {trigger_id}")

        # =====================================================================
        # Pure Python AgenticTrigger (no n8n dependency)
        # =====================================================================
        logger.info(f"🐍 Using Python AgenticTrigger")

        try:
            analysis_result = run_agentic_trigger(build_id, triggered_by_user)

            # Get analysis_id from the stored result
            analysis_id = analysis_result.get('storage_id')

            # Update trigger log with success AND link to analysis
            if analysis_id:
                cursor.execute("""
                    UPDATE manual_trigger_log
                    SET trigger_successful = TRUE, analysis_id = %s
                    WHERE id = %s
                """, (analysis_id, trigger_id))
                logger.info(f"📝 Linked trigger {trigger_id} to analysis {analysis_id}")
            else:
                cursor.execute("""
                    UPDATE manual_trigger_log
                    SET trigger_successful = TRUE
                    WHERE id = %s
                """, (trigger_id,))
            conn.commit()

            cursor.close()
            conn.close()

            logger.info(f"✅ AgenticTrigger successful for build: {build_id}")

            return jsonify({
                "success": True,
                "message": "Analysis triggered successfully (AgenticTrigger)",
                "trigger_id": trigger_id,
                "build_id": build_id,
                "consecutive_failures": consecutive_failures,
                "analysis_result": analysis_result
            }), 200

        except Exception as e:
            logger.error(f"❌ AgenticTrigger failed: {e}")
            # Update trigger log with failure
            cursor.execute("""
                UPDATE manual_trigger_log
                SET trigger_successful = FALSE
                WHERE id = %s
            """, (trigger_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({
                "error": "AgenticTrigger failed",
                "details": str(e)
            }), 500

    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {e}")
        return jsonify({
            "error": "Manual trigger failed",
            "details": str(e)
        }), 500


# ============================================================================
# FEEDBACK ENDPOINTS
# ============================================================================

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback on AI recommendation (Enhanced with HITL validation tracking)

    Request (Legacy format):
    {
        "build_id": "12345",
        "feedback_type": "success",  // success, failed, partial, incorrect_classification
        "feedback_text": "Fix worked perfectly!",
        "user_id": "john.doe@company.com",
        "alternative_root_cause": "...",  // if feedback_type = incorrect_classification
        "alternative_fix": "..."
    }

    Request (New HITL format - Task 0-HITL.14):
    {
        "build_id": "12345",
        "validation_status": "accepted",  // accepted, rejected, refining
        "validator_name": "John Doe",
        "validator_email": "john.doe@company.com",
        "feedback_comment": "Analysis is accurate",
        "refinement_suggestions": "..."  // for refining status
    }

    Response:
    {
        "success": true,
        "feedback_id": 456,
        "acceptance_tracking_id": 789,
        "message": "Feedback recorded successfully",
        "pinecone_updated": true
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data:
            return jsonify({
                "error": "Missing required field: build_id"
            }), 400

        build_id = data['build_id']

        # Support both legacy and new HITL formats
        validation_status = data.get('validation_status')

        if validation_status:
            # New HITL format (Task 0-HITL.14)
            feedback_type = validation_status  # Map to legacy field
            feedback_text = data.get('feedback_comment', '')
            user_id = data.get('validator_email', 'anonymous')
            validator_name = data.get('validator_name')
            validator_email = data.get('validator_email')
            refinement_suggestions = data.get('refinement_suggestions')
            alternative_root_cause = None
            alternative_fix = refinement_suggestions if validation_status == 'refining' else None
        else:
            # Legacy format
            if 'feedback_type' not in data:
                return jsonify({
                    "error": "Missing required field: feedback_type or validation_status"
                }), 400
            feedback_type = data['feedback_type']
            feedback_text = data.get('feedback_text', '')
            user_id = data.get('user_id', 'anonymous')
            validator_name = None
            validator_email = user_id if '@' in user_id else None
            refinement_suggestions = None
            alternative_root_cause = data.get('alternative_root_cause')
            alternative_fix = data.get('alternative_fix')

        logger.info(f"📊 Feedback received for build: {build_id} - Type: {feedback_type}")

        # Record feedback in PostgreSQL using stored procedure
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT record_feedback(%s, %s, %s, %s)
        """, (build_id, feedback_type, feedback_text, user_id))

        feedback_id = cursor.fetchone()['record_feedback']

        # If alternative solution provided, store it
        if alternative_root_cause or alternative_fix:
            cursor.execute("""
                UPDATE user_feedback
                SET
                    alternative_root_cause = %s,
                    alternative_fix = %s
                WHERE id = %s
            """, (alternative_root_cause, alternative_fix, feedback_id))

        conn.commit()

        logger.info(f"✅ Feedback recorded with ID: {feedback_id}")

        # Task 0-HITL.14: Insert/Update acceptance_tracking table
        acceptance_tracking_id = None
        if validation_status:
            try:
                # Get analysis_id for this build
                cursor.execute("""
                    SELECT id
                    FROM failure_analysis
                    WHERE build_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (build_id,))

                analysis_result = cursor.fetchone()
                if analysis_result:
                    analysis_id = analysis_result['id']

                    # Check if acceptance_tracking record already exists
                    cursor.execute("""
                        SELECT id, refinement_count
                        FROM acceptance_tracking
                        WHERE analysis_id = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                    """, (analysis_id,))

                    existing_tracking = cursor.fetchone()

                    if existing_tracking:
                        # Update existing record
                        refinement_count = existing_tracking['refinement_count']
                        if validation_status == 'refining':
                            refinement_count += 1

                        cursor.execute("""
                            UPDATE acceptance_tracking
                            SET
                                validation_status = %s,
                                refinement_count = %s,
                                final_acceptance = %s,
                                validator_name = %s,
                                validator_email = %s,
                                feedback_comment = %s,
                                validated_at = CASE WHEN %s IN ('accepted', 'rejected') THEN NOW() ELSE validated_at END,
                                updated_at = NOW()
                            WHERE id = %s
                            RETURNING id
                        """, (
                            validation_status,
                            refinement_count,
                            True if validation_status == 'accepted' else (False if validation_status == 'rejected' else None),
                            validator_name,
                            validator_email,
                            feedback_text,
                            validation_status,
                            existing_tracking['id']
                        ))

                        acceptance_tracking_id = cursor.fetchone()['id']
                        logger.info(f"✅ Updated acceptance_tracking ID: {acceptance_tracking_id}, refinement_count: {refinement_count}")
                    else:
                        # Insert new record
                        cursor.execute("""
                            INSERT INTO acceptance_tracking (
                                analysis_id,
                                build_id,
                                validation_status,
                                refinement_count,
                                final_acceptance,
                                validator_name,
                                validator_email,
                                feedback_comment,
                                validated_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            analysis_id,
                            build_id,
                            validation_status,
                            1 if validation_status == 'refining' else 0,
                            True if validation_status == 'accepted' else (False if validation_status == 'rejected' else None),
                            validator_name,
                            validator_email,
                            feedback_text,
                            datetime.now() if validation_status in ['accepted', 'rejected'] else None
                        ))

                        acceptance_tracking_id = cursor.fetchone()['id']
                        logger.info(f"✅ Created acceptance_tracking ID: {acceptance_tracking_id}")

                    conn.commit()

            except Exception as e:
                logger.error(f"❌ Acceptance tracking failed: {e}")
                # Don't fail the entire request if acceptance tracking fails

        # Update Pinecone vector database with feedback
        pinecone_updated = False
        try:
            # Get the vector ID for this build
            cursor.execute("""
                SELECT build_id
                FROM failure_analysis
                WHERE build_id = %s
                ORDER BY timestamp DESC
                LIMIT 1
            """, (build_id,))

            result = cursor.fetchone()
            if result:
                # Update success rate in Pinecone
                feedback_successful = feedback_type in ['success', 'partial']

                pinecone_response = requests.post(
                    f"{PINECONE_SERVICE_URL}/api/update-feedback",
                    json={
                        "vector_id": f"{build_id}_{int(datetime.now().timestamp())}",
                        "success": feedback_successful,
                        "increment_usage": True
                    },
                    timeout=10
                )

                if pinecone_response.status_code == 200:
                    pinecone_updated = True
                    logger.info(f"✅ Pinecone updated with feedback for build: {build_id}")

        except Exception as e:
            logger.warning(f"⚠️  Pinecone update failed: {e}")

        cursor.close()
        conn.close()

        response_data = {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback recorded successfully",
            "pinecone_updated": pinecone_updated
        }

        # Include acceptance_tracking_id in response if available (Task 0-HITL.14)
        if acceptance_tracking_id:
            response_data["acceptance_tracking_id"] = acceptance_tracking_id

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"❌ Feedback submission failed: {e}")
        return jsonify({
            "error": "Feedback submission failed",
            "details": str(e)
        }), 500


@app.route('/api/feedback/<build_id>', methods=['GET'])
def get_feedback(build_id):
    """
    Get feedback for a specific build

    Response:
    {
        "build_id": "12345",
        "has_feedback": true,
        "feedback": [
            {
                "id": 456,
                "feedback_type": "success",
                "feedback_text": "...",
                "user_id": "...",
                "submitted_at": "..."
            }
        ]
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                uf.id,
                uf.feedback_type,
                uf.feedback_text,
                uf.user_id,
                uf.alternative_root_cause,
                uf.alternative_fix,
                uf.submitted_at
            FROM user_feedback uf
            WHERE uf.build_id = %s
            ORDER BY uf.submitted_at DESC
        """, (build_id,))

        feedback_records = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "build_id": build_id,
            "has_feedback": len(feedback_records) > 0,
            "feedback_count": len(feedback_records),
            "feedback": [dict(record) for record in feedback_records]
        }), 200

    except Exception as e:
        logger.error(f"❌ Get feedback failed: {e}")
        return jsonify({
            "error": "Failed to retrieve feedback",
            "details": str(e)
        }), 500


@app.route('/api/feedback/recent', methods=['GET'])
def get_recent_feedback():
    """
    Get recent feedback across all builds

    Query params:
    - limit: Number of records (default: 50)
    - feedback_type: Filter by type (optional)

    Response:
    {
        "total": 123,
        "feedback": [...]
    }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        feedback_type = request.args.get('feedback_type')

        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = """
            SELECT
                uf.id,
                uf.build_id,
                uf.feedback_type,
                uf.feedback_text,
                uf.user_id,
                uf.submitted_at,
                fa.job_name,
                fa.error_category,
                fa.confidence_score
            FROM user_feedback uf
            JOIN failure_analysis fa ON uf.analysis_id = fa.id
        """

        if feedback_type:
            query += " WHERE uf.feedback_type = %s"
            cursor.execute(query + " ORDER BY uf.submitted_at DESC LIMIT %s", (feedback_type, limit))
        else:
            cursor.execute(query + " ORDER BY uf.submitted_at DESC LIMIT %s", (limit,))

        feedback_records = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            "total": len(feedback_records),
            "feedback": [dict(record) for record in feedback_records]
        }), 200

    except Exception as e:
        logger.error(f"❌ Get recent feedback failed: {e}")
        return jsonify({
            "error": "Failed to retrieve feedback",
            "details": str(e)
        }), 500


# ============================================================================
# WORKFLOW 3: DDN AGENTIC REFINER (HITL Feedback Refinement)
# ============================================================================

def refine_with_claude(original_analysis: dict, build_data: dict, user_feedback: str, user_email: str) -> dict:
    """
    Use Claude to refine analysis based on user feedback.
    This is the core of AgenticRefiner.
    """
    if not ANTHROPIC_API_KEY:
        logger.error("❌ ANTHROPIC_API_KEY not set - cannot use Claude refinement")
        return {
            "root_cause": "Refinement unavailable - API key not configured",
            "fix_recommendation": "Please configure ANTHROPIC_API_KEY",
            "confidence_score": 0.0,
            "refinement_summary": "Failed - no API key"
        }

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = f"""**REFINEMENT REQUEST - USER FEEDBACK PROVIDED**

A user has reviewed the previous analysis and provided feedback. Please re-analyze with this new context.

---

## ORIGINAL ANALYSIS

**Category:** {original_analysis.get('error_category', 'UNKNOWN')}
**Confidence:** {original_analysis.get('confidence_score', 0)}
**Analysis Type:** {original_analysis.get('analysis_type', 'N/A')}

**Original Root Cause:**
{original_analysis.get('root_cause', 'N/A')}

**Original Fix Recommendation:**
{original_analysis.get('fix_recommendation', 'N/A')}

---

## USER FEEDBACK

**Provided by:** {user_email}
**Feedback:**
```
{user_feedback}
```

---

## BUILD INFORMATION

**Build ID:** {build_data.get('build_id')}
**Job:** {build_data.get('job_name', 'N/A')}
**Test Suite:** {build_data.get('test_name', build_data.get('test_suite', 'N/A'))}

**Error Log:**
```
{str(build_data.get('error_log', ''))[:2000]}
```

**Stack Trace:**
```
{str(build_data.get('stack_trace', ''))[:1500]}
```

---

## YOUR TASK (REFINEMENT)

This is a refinement request. The user is not satisfied with the previous analysis.

**Instructions:**
1. **Consider the user's feedback** - They may have domain knowledge you lack
2. **Re-evaluate the error category** - User feedback may indicate wrong classification
3. **Provide SPECIFIC evidence** - Quote exact details from logs
4. **Explain what changed** - Why is this refinement better than original?

**CRITICAL:**
- Address ALL points in user feedback
- If user mentions specific files or areas, focus on those
- Explain why the original analysis may have been incorrect

**OUTPUT FORMAT (strict JSON):**
```json
{{
  "refinement_summary": "What changed from original analysis",
  "user_feedback_addressed": "How we addressed user's concerns",
  "revised_category": "ERROR_CATEGORY (may differ from original)",
  "root_cause": "NEW technical explanation based on feedback",
  "fix_recommendation": "UPDATED step-by-step fix",
  "code_fix": "Actual code fix or configuration change if applicable",
  "evidence": ["Specific evidence supporting this refined analysis"],
  "why_original_was_wrong": "Explanation (if applicable)",
  "confidence_score": 0.90,
  "confidence_change": "+10% improvement or reason for decrease"
}}
```"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text

        # Extract JSON from response
        json_match = text.find('```json')
        if json_match != -1:
            json_end = text.find('```', json_match + 7)
            json_str = text[json_match + 7:json_end].strip()
            try:
                result = json.loads(json_str)
            except json.JSONDecodeError:
                result = {
                    "root_cause": text[:500],
                    "fix_recommendation": text[:1000],
                    "confidence_score": 0.80,
                    "refinement_summary": "Parsed from unstructured response"
                }
        else:
            result = {
                "root_cause": text[:500],
                "fix_recommendation": text[:1000],
                "confidence_score": 0.80,
                "refinement_summary": "Parsed from unstructured response"
            }

        # Add metadata
        result['token_usage'] = response.usage.input_tokens + response.usage.output_tokens
        result['analysis_type'] = 'CLAUDE_REFINEMENT'
        result['estimated_cost_usd'] = round(
            (response.usage.input_tokens / 1000000 * 3.00) +
            (response.usage.output_tokens / 1000000 * 15.00), 4
        )
        result['refined_by'] = user_email
        result['refinement_timestamp'] = datetime.now().isoformat()

        logger.info(f"✅ Claude refinement complete - tokens: {result['token_usage']}, cost: ${result['estimated_cost_usd']}")
        return result

    except Exception as e:
        logger.error(f"❌ Claude refinement failed: {e}")
        return {
            "root_cause": f"Refinement failed: {str(e)}",
            "fix_recommendation": "Please retry or contact support",
            "confidence_score": 0.0,
            "refinement_summary": "Claude API error",
            "analysis_type": "CLAUDE_REFINEMENT_FAILED"
        }


@app.route('/api/refine-analysis', methods=['POST'])
def refine_analysis():
    """
    DDN AgenticRefiner - HITL feedback refinement endpoint

    Request:
    {
        "build_id": "DDN-Basic-Tests-85",
        "user_feedback": "The original analysis missed that this is actually a configuration issue...",
        "user_email": "john.doe@company.com"
    }

    Response:
    {
        "success": true,
        "message": "Analysis refined successfully",
        "data": {...refined analysis...}
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data or 'build_id' not in data:
            return jsonify({"error": "Missing required field: build_id"}), 400

        if 'user_feedback' not in data or len(data.get('user_feedback', '').strip()) < 10:
            return jsonify({"error": "User feedback is required and must be at least 10 characters"}), 400

        build_id = data['build_id']
        user_feedback = data['user_feedback'].strip()
        user_email = data.get('user_email', 'anonymous@user.com')

        logger.info(f"🔄 AgenticRefiner: Refinement requested for build {build_id}")

        # STEP 1: Get original analysis from Dashboard API (GAP #3 FIX - PostgreSQL, not MongoDB)
        original_analysis = None
        try:
            dashboard_response = requests.get(
                f"{DASHBOARD_API_URL}/api/analysis/{build_id}",
                timeout=10
            )
            if dashboard_response.status_code == 200:
                original_analysis = dashboard_response.json()
                logger.info(f"📦 Got original analysis from Dashboard API")
            else:
                logger.warning(f"⚠️ Dashboard API returned {dashboard_response.status_code}, checking PostgreSQL directly")
        except Exception as e:
            logger.warning(f"⚠️ Dashboard API call failed: {e}")

        # Fallback: Direct PostgreSQL query if Dashboard API fails
        if not original_analysis:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""
                    SELECT id, build_id, job_name, test_name, error_category,
                           root_cause, fix_recommendation, confidence_score,
                           analysis_type, timestamp, refinement_count
                    FROM failure_analysis
                    WHERE build_id = %s
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (build_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if result:
                    original_analysis = dict(result)
                    logger.info(f"📦 Got original analysis from PostgreSQL directly")
            except Exception as e:
                logger.error(f"❌ PostgreSQL query failed: {e}")

        if not original_analysis:
            return jsonify({
                "status": "error",
                "message": "No existing analysis found for this build",
                "build_id": build_id,
                "suggestion": "Please run manual analysis first before refinement"
            }), 404

        # STEP 2: Get build context from MongoDB for additional context
        build_data = {"build_id": build_id}
        try:
            mongo_db = get_mongodb_client()
            mongo_build = mongo_db.builds.find_one({"build_id": build_id})
            if not mongo_build:
                mongo_build = mongo_db.test_failures.find_one({"build_id": build_id})

            if mongo_build:
                if '_id' in mongo_build:
                    mongo_build['_id'] = str(mongo_build['_id'])
                build_data.update(mongo_build)

            # Get console log
            console_log = mongo_db.console_logs.find_one({"build_id": build_id})
            if console_log:
                build_data['stack_trace'] = console_log.get('stack_trace', '')
                build_data['full_console'] = console_log.get('full_log', '')

            logger.info(f"📦 Got build context from MongoDB Atlas")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB context retrieval failed: {e}")

        # STEP 3: Call Claude for refinement
        refined_result = refine_with_claude(original_analysis, build_data, user_feedback, user_email)

        if refined_result.get('confidence_score', 0) == 0:
            return jsonify({
                "success": False,
                "message": "Refinement failed",
                "error": refined_result.get('root_cause', 'Unknown error')
            }), 500

        # STEP 4: Build complete refined result
        refinement_count = original_analysis.get('refinement_count', 0) + 1

        final_result = {
            "build_id": build_id,
            "job_name": build_data.get('job_name', original_analysis.get('job_name')),
            "test_name": build_data.get('test_name', original_analysis.get('test_name')),
            "error_category": refined_result.get('revised_category', original_analysis.get('error_category')),
            "root_cause": refined_result.get('root_cause'),
            "fix_recommendation": refined_result.get('fix_recommendation'),
            "code_fix": refined_result.get('code_fix', ''),
            "confidence_score": refined_result.get('confidence_score', 0.80),
            "analysis_type": "CLAUDE_REFINEMENT",
            "trigger_type": "REFINEMENT",
            "refinement_count": refinement_count,
            "refinement_summary": refined_result.get('refinement_summary', ''),
            "user_feedback_addressed": refined_result.get('user_feedback_addressed', ''),
            "original_user_feedback": user_feedback,
            "refined_by": user_email,
            "timestamp": datetime.now().isoformat(),
            "token_usage": refined_result.get('token_usage', 0),
            "estimated_cost_usd": refined_result.get('estimated_cost_usd', 0)
        }

        # STEP 5: Update via Dashboard API
        try:
            update_response = requests.put(
                f"{DASHBOARD_API_URL}/api/analysis/update",
                json=final_result,
                timeout=10
            )
            if update_response.status_code == 200:
                update_result = update_response.json()
                final_result['storage_updated'] = True
                final_result['updated_id'] = update_result.get('id')
                logger.info(f"✅ Updated analysis via Dashboard API")
            else:
                logger.warning(f"⚠️ Dashboard API update returned {update_response.status_code}")
                final_result['storage_updated'] = False
        except Exception as e:
            logger.warning(f"⚠️ Dashboard API update failed: {e}")
            final_result['storage_updated'] = False

        logger.info(f"✅ AgenticRefiner complete for build {build_id} (refinement #{refinement_count})")

        return jsonify({
            "success": True,
            "message": f"Analysis refined successfully (refinement #{refinement_count})",
            "build_id": build_id,
            "data": final_result
        }), 200

    except Exception as e:
        logger.error(f"❌ AgenticRefiner failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Refinement failed",
            "details": str(e)
        }), 500


# ============================================================================
# WORKFLOW 4: DDN AGENTIC FIXER (Auto GitHub PR Creation)
# ============================================================================

# Slack webhook for notifications
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Auto-fix confidence threshold
AUTO_FIX_CONFIDENCE_THRESHOLD = float(os.getenv("AUTO_FIX_CONFIDENCE_THRESHOLD", "0.70"))


def send_slack_notification(fix_result: dict) -> bool:
    """
    Send Slack notification for auto-fix PR creation.
    Returns True if notification sent successfully.
    """
    if not SLACK_WEBHOOK_URL:
        logger.info("📭 Slack notification skipped - webhook not configured")
        return False

    try:
        payload = {
            "text": f"🤖 Auto-Fix PR Created: #{fix_result.get('pr_number')}",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 Automated Code Fix Applied",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*PR Number:*\n<{fix_result.get('pr_url')}|#{fix_result.get('pr_number')}>"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Confidence:*\n{fix_result.get('confidence_score', 0) * 100:.0f}%"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Category:*\n{fix_result.get('error_category', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Build:*\n{fix_result.get('build_id', 'N/A')}"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View PR",
                                "emoji": True
                            },
                            "url": fix_result.get('pr_url', '#'),
                            "style": "primary"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "View Build",
                                "emoji": True
                            },
                            "url": f"http://localhost:5173/failures/{fix_result.get('build_id')}"
                        }
                    ]
                }
            ]
        }

        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Slack notification sent for PR #{fix_result.get('pr_number')}")
            return True
        else:
            logger.warning(f"⚠️ Slack notification failed: {response.status_code}")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Slack notification error: {e}")
        return False


@app.route('/api/auto-fix', methods=['POST'])
def trigger_auto_fix():
    """
    DDN AgenticFixer - Auto-fix endpoint for high-confidence analyses

    Called when AI analysis completes with confidence >= 70%.
    Creates a GitHub PR with the recommended fix.

    Request:
    {
        "analysis_id": 123,
        "build_id": "DDN-Basic-Tests-85",
        "confidence_score": 0.85,
        "error_category": "CODE_ERROR",
        "code_fix": "...",
        "file_path": "path/to/file.py"
    }

    Response:
    {
        "success": true,
        "message": "Auto-fix PR created successfully",
        "data": {
            "pr_number": 456,
            "pr_url": "https://github.com/..."
        }
    }
    """
    try:
        data = request.get_json()

        # Validate request
        if not data:
            return jsonify({"error": "No data provided"}), 400

        build_id = data.get('build_id')
        analysis_id = data.get('analysis_id')
        confidence_score = float(data.get('confidence_score', 0))

        if not build_id and not analysis_id:
            return jsonify({"error": "Missing required field: build_id or analysis_id"}), 400

        logger.info(f"🔧 AgenticFixer: Auto-fix requested for build {build_id} (confidence: {confidence_score})")

        # STEP 1: Validate confidence threshold
        if confidence_score < AUTO_FIX_CONFIDENCE_THRESHOLD:
            logger.info(f"⏸️ Auto-fix skipped - confidence {confidence_score} < threshold {AUTO_FIX_CONFIDENCE_THRESHOLD}")
            return jsonify({
                "status": "skipped",
                "message": "Confidence too low for auto-fix",
                "build_id": build_id,
                "confidence_score": confidence_score,
                "threshold": AUTO_FIX_CONFIDENCE_THRESHOLD,
                "action": "Manual review required"
            }), 200

        # STEP 2: Call Dashboard API to approve fix and create PR
        approve_payload = {
            "analysis_id": analysis_id,
            "build_id": build_id,
            "approved_by_name": "AI Auto-Fix System",
            "approved_by_email": "autofix@system.ai",
            "auto_approved": True,
            "confidence_score": confidence_score
        }

        try:
            approve_response = requests.post(
                f"{DASHBOARD_API_URL}/api/fixes/approve",
                json=approve_payload,
                timeout=60
            )
            approve_response.raise_for_status()
            pr_result = approve_response.json()

            if not pr_result.get('success'):
                logger.error(f"❌ PR creation failed: {pr_result.get('error')}")
                return jsonify({
                    "status": "error",
                    "message": "Failed to create PR",
                    "build_id": build_id,
                    "error": pr_result.get('error', 'Unknown error')
                }), 500

            logger.info(f"✅ PR created: #{pr_result.get('pr_number')}")

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Dashboard API call failed: {e}")
            return jsonify({
                "status": "error",
                "message": "Failed to call Dashboard API",
                "build_id": build_id,
                "error": str(e)
            }), 500

        # STEP 3: Build success result
        fix_result = {
            "analysis_id": analysis_id,
            "build_id": build_id,
            "fix_application_id": pr_result.get('fix_application_id'),
            "pr_number": pr_result.get('pr_number'),
            "pr_url": pr_result.get('pr_url'),
            "pr_created_at": datetime.now().isoformat(),
            "error_category": data.get('error_category'),
            "confidence_score": confidence_score,
            "file_path": data.get('file_path'),
            "status": "pr_created",
            "auto_approved": True,
            "approved_by": "AI Auto-Fix System"
        }

        # STEP 4: Send Slack notification
        send_slack_notification(fix_result)

        # STEP 5: Log to database for analytics
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO auto_fix_history (
                    analysis_id, build_id, pr_number, pr_url,
                    confidence_score, auto_approved, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                analysis_id, build_id, pr_result.get('pr_number'),
                pr_result.get('pr_url'), confidence_score, True
            ))
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"📝 Auto-fix logged to history")
        except Exception as e:
            logger.warning(f"⚠️ Failed to log auto-fix history: {e}")
            # Don't fail the request - PR was created successfully

        logger.info(f"✅ AgenticFixer complete for build {build_id}")

        return jsonify({
            "success": True,
            "message": "Auto-fix PR created successfully",
            "data": fix_result
        }), 200

    except Exception as e:
        logger.error(f"❌ AgenticFixer failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Auto-fix failed",
            "details": str(e)
        }), 500


@app.route('/api/auto-fix/check-eligible', methods=['GET'])
def check_auto_fix_eligible():
    """
    Check if a build is eligible for auto-fix based on confidence threshold.

    Query params:
    - build_id: Build to check
    - confidence: Confidence score to check

    Response:
    {
        "eligible": true,
        "confidence_score": 0.85,
        "threshold": 0.70
    }
    """
    build_id = request.args.get('build_id')
    confidence = request.args.get('confidence', type=float)

    if confidence is None:
        return jsonify({"error": "Missing required param: confidence"}), 400

    eligible = confidence >= AUTO_FIX_CONFIDENCE_THRESHOLD

    return jsonify({
        "eligible": eligible,
        "build_id": build_id,
        "confidence_score": confidence,
        "threshold": AUTO_FIX_CONFIDENCE_THRESHOLD,
        "action": "Auto-fix will proceed" if eligible else "Manual review required"
    }), 200


# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get analytics summary

    Response:
    {
        "total_analyses": 123,
        "analysis_breakdown": {...},
        "feedback_stats": {...},
        "cost_stats": {...}
    }
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get recent metrics
        cursor.execute("""
            SELECT
                COUNT(*) as total_analyses,
                SUM(CASE WHEN analysis_type = 'RAG_BASED' THEN 1 ELSE 0 END) as rag_analyses,
                SUM(CASE WHEN analysis_type = 'CLAUDE_DEEP_ANALYSIS' THEN 1 ELSE 0 END) as claude_analyses,
                SUM(estimated_cost_usd) as total_cost,
                AVG(confidence_score) as avg_confidence,
                AVG(processing_time_ms) as avg_processing_time,
                SUM(CASE WHEN feedback_received THEN 1 ELSE 0 END) as feedback_count,
                SUM(CASE WHEN feedback_result = 'success' THEN 1 ELSE 0 END) as positive_feedback
            FROM failure_analysis
            WHERE timestamp > CURRENT_DATE - INTERVAL '30 days'
        """)

        summary = dict(cursor.fetchone())

        cursor.close()
        conn.close()

        # Calculate success rate
        if summary['feedback_count'] > 0:
            summary['feedback_success_rate'] = round(
                (summary['positive_feedback'] / summary['feedback_count']) * 100,
                2
            )
        else:
            summary['feedback_success_rate'] = None

        return jsonify(summary), 200

    except Exception as e:
        logger.error(f"❌ Get analytics failed: {e}")
        return jsonify({
            "error": "Failed to retrieve analytics",
            "details": str(e)
        }), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting Manual Trigger & Feedback API...")
    logger.info(f"📍 Server will run on: http://localhost:5004")
    logger.info(f"📍 Health Check: http://localhost:5004/health")

    # Show Agentic Workflow configuration
    logger.info("🐍 Pure Python Agentic Workflows (no n8n)")
    logger.info(f"   MongoDB Atlas: {MONGODB_DB}")
    logger.info(f"   LangGraph: {LANGGRAPH_URL}")
    logger.info(f"   Dashboard API: {DASHBOARD_API_URL}")
    logger.info(f"   Anthropic API: {'configured' if ANTHROPIC_API_KEY else 'NOT SET'}")
    logger.info("")
    logger.info("📋 DDN Agentic Workflow Endpoints:")
    logger.info("   POST /api/auto-analyze     - Workflow 1: AgenticAnalyzer (auto from aging)")
    logger.info("   POST /api/trigger-analysis - Workflow 2: AgenticTrigger (manual)")
    logger.info("   POST /api/refine-analysis  - Workflow 3: AgenticRefiner (HITL feedback)")
    logger.info("   POST /api/auto-fix         - Workflow 4: AgenticFixer (auto PR creation)")
    logger.info("")
    logger.info(f"   Teams Webhook: {'configured' if TEAMS_WEBHOOK_URL else 'NOT SET'}")
    logger.info(f"   Slack Webhook: {'configured' if SLACK_WEBHOOK_URL else 'NOT SET'}")
    logger.info(f"   Auto-Fix Threshold: {AUTO_FIX_CONFIDENCE_THRESHOLD * 100:.0f}%")

    # Verify environment
    if not POSTGRES_URI:
        logger.warning("⚠️  POSTGRES_URI not set!")

    # Test PostgreSQL connection
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("✅ PostgreSQL connected successfully")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.warning("⚠️  Server will start but database features may not work!")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5004,
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        threaded=True
    )
