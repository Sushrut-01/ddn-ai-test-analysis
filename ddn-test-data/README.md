# DDN Test Data Repository

Test data repository for the DDN AI Test Failure Analysis System - MCP GitHub integration testing.

## Purpose

This repository provides realistic test data for:

1. **GitHub Code Fetching** - Testing MCP GitHub server tools
2. **Error Analysis** - CODE_ERROR category analysis with actual source code context
3. **Stack Trace Parsing** - Extracting file paths and line numbers from error messages
4. **Source Code Context** - Providing relevant code snippets for AI analysis

## Repository Structure

```
ddn-test-data/
├── robot-tests/              # Robot Framework test files
│   ├── ddn_basic_tests.robot      # Basic DDN product tests
│   ├── ddn_advanced_tests.robot   # Advanced multi-tenancy tests
│   └── DDN_Keywords.py            # Python keyword library
│
├── tests/                    # Unit and integration tests
│   ├── python/
│   │   └── test_ha_failover.py   # HA failover tests (ERROR LINE 145)
│   └── java/
│       └── StorageTest.java       # Java storage tests
│
├── src/                      # Sample source code with error patterns
│   ├── storage/
│   │   └── DDNStorage.java        # Storage client (ERROR LINE 142)
│   ├── network/
│   │   └── connection.py          # Network connection (ERROR LINE 87)
│   └── tests/
│       └── ha_test.py             # Integration tests
│
├── test-data/                # Sample error logs and stack traces
│   ├── error-logs/
│   │   └── code-errors.json       # Sample CODE_ERROR logs
│   └── stack-traces/
│       └── sample-traces.txt      # Example stack traces
│
└── docs/                     # Documentation
    └── ERROR-PATTERNS.md          # Common error patterns documentation
```

## Common Error Lines

This repository includes sample files with common error patterns used in testing:

### Python Errors

**File:** `tests/python/test_ha_failover.py`
- **Line 145:** `result = connection.execute_operation()`
  - **Error Type:** TimeoutError
  - **Scenario:** HA failover timeout when backup node unavailable
  - **Stack Trace Pattern:** `File "tests/python/test_ha_failover.py", line 145`

**File:** `src/network/connection.py`
- **Line 87:** `raise TimeoutError(f'Operation timed out after {self.timeout}s')`
  - **Error Type:** TimeoutError
  - **Scenario:** Network operation exceeds configured timeout
  - **Stack Trace Pattern:** `File "src/network/connection.py", line 87`

### Java Errors

**File:** `src/storage/DDNStorage.java`
- **Line 142:** `buffer.allocate(size);`
  - **Error Type:** NullPointerException
  - **Scenario:** Buffer not initialized before allocate() call
  - **Stack Trace Pattern:** `at com.ddn.storage.DDNStorage.allocate(DDNStorage.java:142)`

## Usage with MCP GitHub Server

### Fetching Files

```python
from github_client import get_github_client

client = get_github_client()

# Fetch Python test file with error context
result = client.get_file(
    file_path="tests/python/test_ha_failover.py",
    start_line=140,
    end_line=150
)
print(result.content)  # Shows code around line 145

# Fetch Java source file
result = client.get_file(
    file_path="src/storage/DDNStorage.java",
    start_line=135,
    end_line=145
)
print(result.content)  # Shows code around line 142
```

### Searching Code

```python
# Search for timeout handling
results = client.search_code(query="TimeoutError", language="python")

# Search for null pointer issues
results = client.search_code(query="NullPointerException", language="java")
```

### Getting Directory Structure

```python
# List test directory
structure = client.get_directory_structure("tests")
print(structure)  # Shows python/ and java/ subdirectories
```

## Error Log Format

Sample error logs in `test-data/error-logs/code-errors.json` follow this format:

```json
{
  "id": "error_001",
  "error_type": "CODE_ERROR",
  "category": "timeout",
  "test_name": "test_ha_failover_timeout",
  "error_message": "TimeoutError: Operation timed out after 30s",
  "file": "tests/python/test_ha_failover.py",
  "line": 145,
  "stack_trace": "Traceback...",
  "severity": "high"
}
```

## Testing Scenarios

### 1. CODE_ERROR Analysis

Test the AI system's ability to:
- Extract file paths from stack traces
- Fetch relevant source code from GitHub
- Identify root cause from code context
- Provide fix recommendations

### 2. Stack Trace Parsing

Test patterns like:
```
File "tests/python/test_ha_failover.py", line 145, in test_ha_failover_timeout
at com.ddn.storage.DDNStorage.allocate(DDNStorage.java:142)
File "src/network/connection.py", line 87, in execute_operation
```

### 3. Multi-Language Support

- Python files with pytest tests
- Java files with JUnit tests
- Robot Framework tests for end-to-end scenarios

## Integration with DDN AI System

This repository is used by:

1. **MCP GitHub Server** (`mcp_github_server.py`)
   - Fetches files via GitHub API
   - Returns code snippets with line numbers
   - Provides directory listings

2. **GitHubClient Wrapper** (`github_client.py`)
   - High-level interface for MCP server
   - Code extraction from stack traces
   - Test file discovery

3. **ReAct Agent** (`react_agent_service.py`)
   - Uses GitHub code for CODE_ERROR analysis
   - Enhances AI recommendations with actual code
   - Provides context-aware solutions

4. **Dashboard UI**
   - Displays fetched code with syntax highlighting
   - Shows line numbers from error stack traces
   - Presents GitHub links for detailed exploration

## Development and Testing

### Prerequisites

- GitHub Personal Access Token with `repo` scope
- MCP GitHub Server running on port 5002
- Environment variables configured:
  ```bash
  GITHUB_TOKEN=your_token_here
  GITHUB_REPO=Sushrut-01/ddn-test-data
  MCP_GITHUB_SERVER_URL=http://localhost:5002
  ```

### Running Tests

```bash
# Test GitHub integration
python implementation/test_github_integration_0e4.py

# Test with Gemini AI
python implementation/test_github_gemini_integration_0e5.py

# End-to-end test
python implementation/test_e2e_github_integration_0e10.py
```

## Error Pattern Documentation

### Timeout Errors

**Common Causes:**
- Network latency
- Slow storage backend responses
- Deadlocks in failover logic

**Example Lines:**
- Python: `tests/python/test_ha_failover.py:145`
- Python: `src/network/connection.py:87`

### Null Pointer Errors

**Common Causes:**
- Uninitialized objects
- Missing initialization calls
- Race conditions in multi-threaded code

**Example Lines:**
- Java: `src/storage/DDNStorage.java:142`

### Connection Errors

**Common Causes:**
- Network partitions
- Node failures
- Configuration issues

**Example Lines:**
- Python: `src/network/connection.py:62`

## Contributing

This is a test data repository. To add new error patterns:

1. Create realistic source files with clear error lines
2. Add corresponding error logs to `test-data/error-logs/`
3. Document error patterns in this README
4. Update line number references

## Version History

- **v1.0** (2025-11-03): Initial repository creation
  - Python HA failover tests
  - Java storage client code
  - Sample error logs
  - Robot Framework tests

## License

MIT License - For testing and development purposes

## Contact

Part of the DDN AI Test Failure Analysis System
Project Repository: DDN-AI-Project-Documentation
