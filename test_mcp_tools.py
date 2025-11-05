"""
Test script for all 7 GitHub MCP tools
Task 0E.2: Verify MCP GitHub server functionality
"""

import requests
import json

MCP_SERVER = "http://localhost:5002"

def test_tool(tool_name, arguments):
    """Test a single MCP tool"""
    print(f"\n{'='*70}")
    print(f"Testing: {tool_name}")
    print(f"{'='*70}")

    payload = {
        "tool": tool_name,
        "arguments": arguments
    }

    print(f"Request: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(
            f"{MCP_SERVER}/mcp/call",
            json=payload,
            timeout=10
        )

        print(f"\nStatus Code: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)[:500]}...")

        return response.status_code, result
    except Exception as e:
        print(f"ERROR: {e}")
        return None, {"error": str(e)}

# Test all 7 tools
print("="*70)
print("MCP GITHUB SERVER - TOOL VERIFICATION TEST")
print("="*70)

# Check server health first
print("\n1. Checking server health...")
health = requests.get(f"{MCP_SERVER}/health").json()
print(f"   Status: {health['status']}")
print(f"   GitHub Token Configured: {health['github_token_configured']}")
print(f"   GitHub Connected: {health['github_connected']}")

# Test all 7 tools
tools_tested = []

# Tool 1: github_get_file
status, result = test_tool("github_get_file", {
    "file_path": "README.md"
})
tools_tested.append(("github_get_file", status == 200 or "error" in result.get("result", {})))

# Tool 2: github_get_blame
status, result = test_tool("github_get_blame", {
    "file_path": "README.md"
})
tools_tested.append(("github_get_blame", status == 200 or "error" in result.get("result", {})))

# Tool 3: github_get_commit_history
status, result = test_tool("github_get_commit_history", {
    "file_path": "README.md",
    "limit": 5
})
tools_tested.append(("github_get_commit_history", status == 200 or "error" in result.get("result", {})))

# Tool 4: github_search_code
status, result = test_tool("github_search_code", {
    "query": "function",
    "limit": 5
})
tools_tested.append(("github_search_code", status == 200 or "error" in result.get("result", {})))

# Tool 5: github_get_test_file
status, result = test_tool("github_get_test_file", {
    "test_name": "test_example"
})
tools_tested.append(("github_get_test_file", status == 200 or "error" in result.get("result", {})))

# Tool 6: github_get_directory_structure
status, result = test_tool("github_get_directory_structure", {
    "path": "",
    "recursive": False
})
tools_tested.append(("github_get_directory_structure", status == 200 or "error" in result.get("result", {})))

# Tool 7: github_get_file_changes
status, result = test_tool("github_get_file_changes", {
    "file_path": "README.md",
    "commits": 3
})
tools_tested.append(("github_get_file_changes", status == 200 or "error" in result.get("result", {})))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
for tool_name, responded in tools_tested:
    status_icon = "✅" if responded else "❌"
    print(f"{status_icon} {tool_name}: {'Responded (tool infrastructure works)' if responded else 'No response'}")

print(f"\nTotal tools tested: {len(tools_tested)}/7")
print(f"Tools responding: {sum(1 for _, r in tools_tested if r)}/7")

print("\n" + "="*70)
print("NOTE: Tools may return errors due to placeholder GitHub token.")
print("This is expected. We're verifying tool routing and error handling work.")
print("="*70)
