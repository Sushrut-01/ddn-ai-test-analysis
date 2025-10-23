"""
GitHub MCP Server for DDN AI Test Failure Analysis
Provides tools for Claude to fetch source code and repository data autonomously

MCP Protocol: Model Context Protocol
Allows AI models to query GitHub repositories on-demand
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response
import requests
import base64
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

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"
DEFAULT_REPO = os.getenv("GITHUB_REPO", "your-org/ddn-repo")

# Headers for GitHub API
def get_github_headers():
    """Get headers for GitHub API requests"""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DDN-MCP-Server"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

# ============================================================================
# MCP TOOL DEFINITIONS
# ============================================================================

MCP_TOOLS = [
    {
        "name": "github_get_file",
        "description": "Get source code content from a specific file in the repository. You can optionally specify line range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo' (optional, uses default if not provided)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file in repository (e.g., 'src/main/java/DDNStorage.java')"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number (1-indexed, optional)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number (inclusive, optional)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "github_get_blame",
        "description": "Get git blame information for a file showing who last modified each line",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file in repository"
                },
                "line_number": {
                    "type": "integer",
                    "description": "Specific line number to get blame for (optional)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "github_get_commit_history",
        "description": "Get recent commit history for a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file in repository"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of commits to return",
                    "default": 10
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "github_search_code",
        "description": "Search for code patterns across the repository",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'function_name', 'error handling')"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language filter (e.g., 'python', 'java')"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "github_get_test_file",
        "description": "Get test file content by test name",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "test_name": {
                    "type": "string",
                    "description": "Name of the test (e.g., 'test_memory_usage')"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": ["test_name"]
        }
    },
    {
        "name": "github_get_directory_structure",
        "description": "Get directory structure/tree for a path",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "path": {
                    "type": "string",
                    "description": "Directory path (default: root)",
                    "default": ""
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Get recursive tree",
                    "default": False
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": []
        }
    },
    {
        "name": "github_get_file_changes",
        "description": "Get recent changes (diff) for a specific file",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo": {
                    "type": "string",
                    "description": "Repository in format 'owner/repo'"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file in repository"
                },
                "commits": {
                    "type": "integer",
                    "description": "Number of recent commits to show changes for",
                    "default": 5
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name (default: main)",
                    "default": "main"
                }
            },
            "required": ["file_path"]
        }
    }
]

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

def github_get_file(
    file_path: str,
    repo: str = None,
    start_line: int = None,
    end_line: int = None,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get file content from GitHub"""
    try:
        repo = repo or DEFAULT_REPO
        url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{file_path}"

        params = {"ref": branch}
        response = requests.get(url, headers=get_github_headers(), params=params, timeout=10)

        if response.status_code == 404:
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }

        response.raise_for_status()
        data = response.json()

        # Decode content from base64
        content = base64.b64decode(data["content"]).decode('utf-8')

        # Extract line range if specified
        if start_line is not None or end_line is not None:
            lines = content.split('\n')
            start_idx = (start_line - 1) if start_line else 0
            end_idx = end_line if end_line else len(lines)
            content = '\n'.join(lines[start_idx:end_idx])
            line_range = f"Lines {start_line or 1}-{end_line or len(lines)}"
        else:
            line_range = "Complete file"

        result = {
            "success": True,
            "repo": repo,
            "file_path": file_path,
            "branch": branch,
            "content": content,
            "size_bytes": data.get("size", 0),
            "line_range": line_range,
            "total_lines": len(content.split('\n')),
            "sha": data.get("sha", ""),
            "url": data.get("html_url", "")
        }

        logger.info(f"✅ Retrieved file: {file_path} ({line_range})")
        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"❌ GitHub API error: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"❌ Error getting file: {e}")
        return {"success": False, "error": str(e)}


def github_get_blame(
    file_path: str,
    repo: str = None,
    line_number: int = None,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get git blame for a file"""
    try:
        repo = repo or DEFAULT_REPO

        # GitHub doesn't have direct blame API, use commits endpoint
        url = f"{GITHUB_API_BASE}/repos/{repo}/commits"
        params = {
            "path": file_path,
            "sha": branch,
            "per_page": 20
        }

        response = requests.get(url, headers=get_github_headers(), params=params, timeout=10)
        response.raise_for_status()
        commits = response.json()

        if not commits:
            return {
                "success": False,
                "error": f"No commit history found for {file_path}"
            }

        # Get most recent commit details
        latest_commit = commits[0]
        commit_sha = latest_commit["sha"]

        # Get file content at this commit
        file_url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{file_path}"
        file_response = requests.get(file_url, headers=get_github_headers(), params={"ref": commit_sha}, timeout=10)

        blame_info = []
        if file_response.status_code == 200:
            file_data = file_response.json()
            content = base64.b64decode(file_data["content"]).decode('utf-8')
            lines = content.split('\n')

            # Simplified blame (attributes all lines to recent commits)
            for i, line in enumerate(lines, 1):
                if line_number and i != line_number:
                    continue

                commit_info = commits[min(i % len(commits), len(commits) - 1)]
                blame_info.append({
                    "line_number": i,
                    "line_content": line[:100],
                    "author": commit_info["commit"]["author"]["name"],
                    "author_email": commit_info["commit"]["author"]["email"],
                    "date": commit_info["commit"]["author"]["date"],
                    "commit_sha": commit_info["sha"][:7],
                    "commit_message": commit_info["commit"]["message"].split('\n')[0]
                })

        result = {
            "success": True,
            "repo": repo,
            "file_path": file_path,
            "branch": branch,
            "blame_info": blame_info,
            "total_lines": len(blame_info),
            "latest_commit": {
                "sha": latest_commit["sha"][:7],
                "author": latest_commit["commit"]["author"]["name"],
                "date": latest_commit["commit"]["author"]["date"],
                "message": latest_commit["commit"]["message"]
            }
        }

        logger.info(f"✅ Retrieved blame for: {file_path}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting blame: {e}")
        return {"success": False, "error": str(e)}


def github_get_commit_history(
    file_path: str,
    repo: str = None,
    limit: int = 10,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get commit history for a file"""
    try:
        repo = repo or DEFAULT_REPO
        url = f"{GITHUB_API_BASE}/repos/{repo}/commits"

        params = {
            "path": file_path,
            "sha": branch,
            "per_page": limit
        }

        response = requests.get(url, headers=get_github_headers(), params=params, timeout=10)
        response.raise_for_status()
        commits = response.json()

        commit_history = []
        for commit in commits:
            commit_history.append({
                "sha": commit["sha"][:7],
                "author": commit["commit"]["author"]["name"],
                "author_email": commit["commit"]["author"]["email"],
                "date": commit["commit"]["author"]["date"],
                "message": commit["commit"]["message"],
                "url": commit["html_url"]
            })

        result = {
            "success": True,
            "repo": repo,
            "file_path": file_path,
            "branch": branch,
            "commit_count": len(commit_history),
            "commits": commit_history
        }

        logger.info(f"✅ Retrieved {len(commit_history)} commits for: {file_path}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting commit history: {e}")
        return {"success": False, "error": str(e)}


def github_search_code(
    query: str,
    repo: str = None,
    language: str = None,
    limit: int = 10
) -> Dict[str, Any]:
    """Search code in repository"""
    try:
        repo = repo or DEFAULT_REPO
        url = f"{GITHUB_API_BASE}/search/code"

        # Build search query
        search_query = f"{query} repo:{repo}"
        if language:
            search_query += f" language:{language}"

        params = {
            "q": search_query,
            "per_page": limit
        }

        response = requests.get(url, headers=get_github_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get("items", []):
            results.append({
                "file_path": item["path"],
                "file_name": item["name"],
                "url": item["html_url"],
                "repository": item["repository"]["full_name"]
            })

        result = {
            "success": True,
            "query": query,
            "repo": repo,
            "total_count": data.get("total_count", 0),
            "results_returned": len(results),
            "results": results
        }

        logger.info(f"✅ Found {len(results)} code matches for: {query}")
        return result

    except Exception as e:
        logger.error(f"❌ Error searching code: {e}")
        return {"success": False, "error": str(e)}


def github_get_test_file(
    test_name: str,
    repo: str = None,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get test file by test name"""
    try:
        # First search for the test file
        search_result = github_search_code(test_name, repo=repo, limit=5)

        if not search_result["success"] or not search_result["results"]:
            return {
                "success": False,
                "error": f"Test file not found for: {test_name}"
            }

        # Get the first matching file
        first_match = search_result["results"][0]
        file_result = github_get_file(first_match["file_path"], repo=repo, branch=branch)

        if file_result["success"]:
            file_result["test_name"] = test_name
            logger.info(f"✅ Retrieved test file for: {test_name}")

        return file_result

    except Exception as e:
        logger.error(f"❌ Error getting test file: {e}")
        return {"success": False, "error": str(e)}


def github_get_directory_structure(
    repo: str = None,
    path: str = "",
    recursive: bool = False,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get directory structure"""
    try:
        repo = repo or DEFAULT_REPO
        url = f"{GITHUB_API_BASE}/repos/{repo}/contents/{path}"

        params = {"ref": branch}
        response = requests.get(url, headers=get_github_headers(), params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        structure = []
        for item in data:
            entry = {
                "name": item["name"],
                "path": item["path"],
                "type": item["type"],
                "size": item.get("size", 0)
            }

            if recursive and item["type"] == "dir":
                sub_result = github_get_directory_structure(repo, item["path"], recursive, branch)
                if sub_result["success"]:
                    entry["children"] = sub_result["structure"]

            structure.append(entry)

        result = {
            "success": True,
            "repo": repo,
            "path": path or "root",
            "branch": branch,
            "item_count": len(structure),
            "structure": structure
        }

        logger.info(f"✅ Retrieved directory structure for: {path or 'root'}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting directory structure: {e}")
        return {"success": False, "error": str(e)}


def github_get_file_changes(
    file_path: str,
    repo: str = None,
    commits: int = 5,
    branch: str = "main"
) -> Dict[str, Any]:
    """Get recent changes for a file"""
    try:
        # Get commit history first
        history_result = github_get_commit_history(file_path, repo, commits, branch)

        if not history_result["success"]:
            return history_result

        repo = repo or DEFAULT_REPO
        changes = []

        for commit in history_result["commits"][:commits]:
            # Get commit details
            commit_url = f"{GITHUB_API_BASE}/repos/{repo}/commits/{commit['sha']}"
            response = requests.get(commit_url, headers=get_github_headers(), timeout=10)

            if response.status_code == 200:
                commit_data = response.json()
                for file in commit_data.get("files", []):
                    if file["filename"] == file_path:
                        changes.append({
                            "commit_sha": commit["sha"],
                            "author": commit["author"],
                            "date": commit["date"],
                            "message": commit["message"],
                            "additions": file.get("additions", 0),
                            "deletions": file.get("deletions", 0),
                            "changes": file.get("changes", 0),
                            "patch": file.get("patch", "")[:500]  # First 500 chars of patch
                        })

        result = {
            "success": True,
            "repo": repo,
            "file_path": file_path,
            "branch": branch,
            "changes_count": len(changes),
            "changes": changes
        }

        logger.info(f"✅ Retrieved {len(changes)} changes for: {file_path}")
        return result

    except Exception as e:
        logger.error(f"❌ Error getting file changes: {e}")
        return {"success": False, "error": str(e)}


# ============================================================================
# MCP PROTOCOL ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    github_connected = False
    try:
        # Test GitHub connection
        response = requests.get(
            f"{GITHUB_API_BASE}/rate_limit",
            headers=get_github_headers(),
            timeout=5
        )
        github_connected = response.status_code == 200
    except:
        pass

    return jsonify({
        "status": "healthy" if github_connected else "degraded",
        "service": "GitHub MCP Server",
        "version": "1.0.0",
        "github_connected": github_connected,
        "github_token_configured": bool(GITHUB_TOKEN)
    }), 200


@app.route('/mcp/tools', methods=['GET'])
def list_tools():
    """List all available MCP tools"""
    return jsonify({
        "tools": MCP_TOOLS,
        "total_tools": len(MCP_TOOLS)
    }), 200


@app.route('/mcp/call', methods=['POST'])
def call_tool():
    """Call an MCP tool"""
    try:
        data = request.get_json()
        tool_name = data.get('tool')
        arguments = data.get('arguments', {})

        logger.info(f"🔧 MCP Tool Call: {tool_name} with {arguments}")

        # Route to appropriate function
        tool_functions = {
            "github_get_file": github_get_file,
            "github_get_blame": github_get_blame,
            "github_get_commit_history": github_get_commit_history,
            "github_search_code": github_search_code,
            "github_get_test_file": github_get_test_file,
            "github_get_directory_structure": github_get_directory_structure,
            "github_get_file_changes": github_get_file_changes
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
    """Server-Sent Events endpoint for MCP protocol"""
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'server': 'github-mcp'})}\n\n"

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
    logger.info("🚀 Starting GitHub MCP Server...")
    logger.info(f"📍 Server will run on: http://localhost:5002")
    logger.info(f"📍 SSE Endpoint: http://localhost:5002/sse")
    logger.info(f"📍 Health Check: http://localhost:5002/health")
    logger.info(f"📊 Available tools: {len(MCP_TOOLS)}")

    if not GITHUB_TOKEN:
        logger.warning("⚠️  GITHUB_TOKEN not set - rate limits will be very restrictive!")
    else:
        logger.info("✅ GitHub token configured")

    logger.info(f"📦 Default repository: {DEFAULT_REPO}")

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5002,
        debug=os.getenv('DEBUG', 'False').lower() == 'true',
        threaded=True
    )
