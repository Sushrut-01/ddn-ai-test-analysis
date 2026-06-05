"""
MongoDB MCP Server for DDN AI Test Failure Analysis
Provides tools for Claude to query MongoDB database autonomously

MCP Protocol: Model Context Protocol
Allows AI models to call tools/functions to retrieve data on-demand
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
from dotenv import load_dotenv
import time

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI")
mongo_client = None
db = None

def get_mongo_connection():
    """Get or create MongoDB connection"""
    global mongo_client, db

    if mongo_client is None:
        if not MONGODB_URI:
            logger.error("❌ MONGODB_URI is not set. Configure MongoDB Atlas connection string in the environment as MONGODB_URI.")
            raise RuntimeError("MONGODB_URI not configured")
        try:
            mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            mongo_client.admin.command('ping')
            db = mongo_client.get_database()
            logger.info(f"✅ Connected to MongoDB: {db.name}")
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            raise

    return db

# ============================================================================
# MCP TOOL DEFINITIONS
# ============================================================================

MCP_TOOLS = [
    {
        "name": "mongodb_get_full_error_details",
        "description": "Get complete error details including full stack trace, error type, and context for a specific build",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_get_console_log",
        "description": "Get the complete console output/log for a build",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of last lines to return (default: all)",
                    "default": -1
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_get_test_results",
        "description": "Get detailed test execution results including passed/failed tests",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_get_system_info",
        "description": "Get system information including OS, memory, CPU, environment variables",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_get_environment_details",
        "description": "Get environment variables and configuration for the build",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_get_dependency_info",
        "description": "Get dependency versions and package information",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    },
    {
        "name": "mongodb_search_similar_errors",
        "description": "Search for similar errors across all builds",
        "input_schema": {
            "type": "object",
            "properties": {
                "error_pattern": {
                    "type": "string",
                    "description": "Error pattern or keyword to search for"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
                }
            },
            "required": ["error_pattern"]
        }
    },
    {
        "name": "mongodb_get_debug_logs",
        "description": "Get detailed debug logs for the build",
        "input_schema": {
            "type": "object",
            "properties": {
                "build_id": {
                    "type": "string",
                    "description": "The build ID to query"
                }
            },
            "required": ["build_id"]
        }
    }
]

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def mongodb_get_full_error_details(build_id: str) -> Dict[str, Any]:
    """Get complete error details for a build"""
    try:
        db = get_mongo_connection()

        # Query error_details collection
        error_doc = db.error_details.find_one({"build_id": build_id})

        if not error_doc:
            return {
                "success": False,
                "error": f"No error details found for build {build_id}"
            }

        # Also get main build doc
        build_doc = db.builds.find_one({"build_id": build_id})

        result = {
            "success": True,
            "build_id": build_id,
            "error_type": error_doc.get("error_type", "Unknown"),
            "error_message": error_doc.get("error_message", ""),
            "full_stack_trace": error_doc.get("stack_trace", ""),
            "error_code": error_doc.get("error_code"),
            "failing_line": error_doc.get("failing_line"),
            "failing_file": error_doc.get("failing_file"),
            "error_context": error_doc.get("context", ""),
            "full_error_log": build_doc.get("error_log", "") if build_doc else "",
            "timestamp": error_doc.get("timestamp"),
            "severity": error_doc.get("severity", "UNKNOWN")
        }

        logger.info(f"✅ Retrieved full error details for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting error details: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_console_log(build_id: str, lines: int = -1) -> Dict[str, Any]:
    """Get console log for a build"""
    try:
        db = get_mongo_connection()

        console_doc = db.console_logs.find_one({"build_id": build_id})

        if not console_doc:
            return {
                "success": False,
                "error": f"No console log found for build {build_id}"
            }

        full_log = console_doc.get("full_log", "")

        # Return last N lines if specified
        if lines > 0:
            log_lines = full_log.split('\n')
            full_log = '\n'.join(log_lines[-lines:])

        result = {
            "success": True,
            "build_id": build_id,
            "console_output": full_log,
            "log_size": len(full_log),
            "lines_returned": len(full_log.split('\n')) if full_log else 0,
            "timestamp": console_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved console log for {build_id} ({result['log_size']} bytes)")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting console log: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_test_results(build_id: str) -> Dict[str, Any]:
    """Get test execution results"""
    try:
        db = get_mongo_connection()

        test_doc = db.test_results.find_one({"build_id": build_id})

        if not test_doc:
            return {
                "success": False,
                "error": f"No test results found for build {build_id}"
            }

        result = {
            "success": True,
            "build_id": build_id,
            "total_tests": test_doc.get("total_tests", 0),
            "passed": test_doc.get("passed", 0),
            "failed": test_doc.get("failed", 0),
            "skipped": test_doc.get("skipped", 0),
            "failing_tests": test_doc.get("failing_tests", []),
            "test_output": test_doc.get("test_output", ""),
            "test_duration_ms": test_doc.get("duration_ms", 0),
            "test_suite": test_doc.get("test_suite", ""),
            "timestamp": test_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved test results for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting test results: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_system_info(build_id: str) -> Dict[str, Any]:
    """Get system information"""
    try:
        db = get_mongo_connection()

        system_doc = db.system_info.find_one({"build_id": build_id})

        if not system_doc:
            return {
                "success": False,
                "error": f"No system info found for build {build_id}"
            }

        result = {
            "success": True,
            "build_id": build_id,
            "os": system_doc.get("os", ""),
            "os_version": system_doc.get("os_version", ""),
            "architecture": system_doc.get("architecture", ""),
            "cpu_count": system_doc.get("cpu_count", 0),
            "memory_total_mb": system_doc.get("memory_total_mb", 0),
            "memory_available_mb": system_doc.get("memory_available_mb", 0),
            "disk_total_gb": system_doc.get("disk_total_gb", 0),
            "disk_free_gb": system_doc.get("disk_free_gb", 0),
            "hostname": system_doc.get("hostname", ""),
            "python_version": system_doc.get("python_version", ""),
            "java_version": system_doc.get("java_version", ""),
            "timestamp": system_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved system info for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting system info: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_environment_details(build_id: str) -> Dict[str, Any]:
    """Get environment variables and configuration"""
    try:
        db = get_mongo_connection()

        build_doc = db.builds.find_one({"build_id": build_id})

        if not build_doc:
            return {
                "success": False,
                "error": f"No build found for {build_id}"
            }

        result = {
            "success": True,
            "build_id": build_id,
            "environment_vars": build_doc.get("environment", {}),
            "config": build_doc.get("config", {}),
            "build_parameters": build_doc.get("parameters", {}),
            "jenkins_url": build_doc.get("jenkins_url", ""),
            "git_branch": build_doc.get("git_branch", ""),
            "git_commit": build_doc.get("git_commit", ""),
            "timestamp": build_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved environment details for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting environment details: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_dependency_info(build_id: str) -> Dict[str, Any]:
    """Get dependency information"""
    try:
        db = get_mongo_connection()

        build_doc = db.builds.find_one({"build_id": build_id})

        if not build_doc:
            return {
                "success": False,
                "error": f"No build found for {build_id}"
            }

        dependencies = build_doc.get("dependencies", {})

        result = {
            "success": True,
            "build_id": build_id,
            "dependencies": dependencies,
            "pip_packages": dependencies.get("pip", []),
            "npm_packages": dependencies.get("npm", []),
            "maven_dependencies": dependencies.get("maven", []),
            "total_dependencies": sum(len(v) if isinstance(v, list) else 0 for v in dependencies.values()),
            "timestamp": build_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved dependency info for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting dependency info: {e}")
        return {"success": False, "error": str(e)}


def mongodb_search_similar_errors(error_pattern: str, limit: int = 10) -> Dict[str, Any]:
    """Search for similar errors"""
    try:
        db = get_mongo_connection()

        # Search in error_details collection
        cursor = db.error_details.find(
            {
                "$or": [
                    {"error_message": {"$regex": error_pattern, "$options": "i"}},
                    {"stack_trace": {"$regex": error_pattern, "$options": "i"}},
                    {"error_type": {"$regex": error_pattern, "$options": "i"}}
                ]
            }
        ).sort("timestamp", -1).limit(limit)

        results = []
        for doc in cursor:
            results.append({
                "build_id": doc.get("build_id"),
                "error_type": doc.get("error_type"),
                "error_message": doc.get("error_message", "")[:200],
                "timestamp": doc.get("timestamp"),
                "severity": doc.get("severity")
            })

        result = {
            "success": True,
            "search_pattern": error_pattern,
            "matches_found": len(results),
            "results": results
        }

        logger.info(f"✅ Found {len(results)} similar errors for pattern: {error_pattern}")
        return result

    except Exception as e:
        logger.error(f"❌ Error searching similar errors: {e}")
        return {"success": False, "error": str(e)}


def mongodb_get_debug_logs(build_id: str) -> Dict[str, Any]:
    """Get debug logs"""
    try:
        db = get_mongo_connection()

        debug_doc = db.debug_logs.find_one({"build_id": build_id})

        if not debug_doc:
            return {
                "success": False,
                "error": f"No debug logs found for build {build_id}"
            }

        result = {
            "success": True,
            "build_id": build_id,
            "debug_log": debug_doc.get("log", ""),
            "log_level": debug_doc.get("log_level", "INFO"),
            "log_size": len(debug_doc.get("log", "")),
            "timestamp": debug_doc.get("timestamp")
        }

        logger.info(f"✅ Retrieved debug logs for {build_id}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting debug logs: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# MCP PROTOCOL ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db = get_mongo_connection()
        db.command('ping')
        return jsonify({
            "status": "healthy",
            "service": "MongoDB MCP Server",
            "version": "1.0.0",
            "mongodb_connected": True
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "service": "MongoDB MCP Server",
            "error": str(e),
            "mongodb_connected": False
        }), 500


@app.route('/mcp/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools"""
    return jsonify({
        "tools": MCP_TOOLS,
        "total_tools": len(MCP_TOOLS)
    }), 200


@app.route('/mcp/call', methods=['POST'])
def call_tool():
    """
    Call an MCP tool

    Request:
    {
        "tool": "mongodb_get_full_error_details",
        "arguments": {
            "build_id": "12345"
        }
    }
    """
    try:
        data = request.get_json()
        tool_name = data.get('tool')
        arguments = data.get('arguments', {})

        logger.info(f"🔧 MCP Tool Call: {tool_name} with {arguments}")

        # Route to appropriate function
        tool_functions = {
            "mongodb_get_full_error_details": mongodb_get_full_error_details,
            "mongodb_get_console_log": mongodb_get_console_log,
            "mongodb_get_test_results": mongodb_get_test_results,
            "mongodb_get_system_info": mongodb_get_system_info,
            "mongodb_get_environment_details": mongodb_get_environment_details,
            "mongodb_get_dependency_info": mongodb_get_dependency_info,
            "mongodb_search_similar_errors": mongodb_search_similar_errors,
            "mongodb_get_debug_logs": mongodb_get_debug_logs
        }

        if tool_name not in tool_functions:
            return jsonify({
                "error": f"Unknown tool: {tool_name}",
                "available_tools": list(tool_functions.keys())
            }), 400

        # Call the tool function
        start_time = time.time()
        result = tool_functions[tool_name](**arguments)
        execution_time = (time.time() - start_time) * 1000

        response = {
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "execution_time_ms": round(execution_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

        logger.info(f"✅ Tool executed in {execution_time:.2f}ms")

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"❌ Tool execution error: {e}")
        return jsonify({
            "error": "Tool execution failed",
            "details": str(e)
        }), 500


@app.route('/sse', methods=['GET', 'POST'])
def sse_endpoint():
    """
    Server-Sent Events endpoint for MCP protocol
    This is what Claude connects to
    """
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'server': 'mongodb-mcp'})}\n\n"

        # Send tools list
        yield f"data: {json.dumps({'type': 'tools', 'tools': MCP_TOOLS})}\n\n"

        # Keep connection alive
        while True:
            time.sleep(30)
            yield f"data: {json.dumps({'type': 'ping'})}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 Starting MongoDB MCP Server...")
    logger.info(f"📍 Server will run on: http://localhost:5001")
    logger.info(f"📍 SSE Endpoint: http://localhost:5001/sse")
    logger.info(f"📍 Health Check: http://localhost:5001/health")

    # Test MongoDB connection
    try:
        db = get_mongo_connection()
        logger.info(f"✅ MongoDB connected successfully")
        logger.info(f"📊 Available tools: {len(MCP_TOOLS)}")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        logger.warning("⚠️  Server will start but tools may not work!")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        threaded=True
    )
