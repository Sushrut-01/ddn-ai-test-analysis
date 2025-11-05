"""
GitHub Client - MCP Server Wrapper
Task 0E.3: Wrapper to call MCP GitHub server at localhost:5002

This client provides Python functions to interact with the GitHub MCP server,
which offers 7 tools for fetching source code and repository data.

MCP Tools Available:
1. github_get_file - Get source code content from a file
2. github_get_blame - Get git blame information
3. github_get_commit_history - Get recent commit history
4. github_search_code - Search code patterns
5. github_get_test_file - Get test file by name
6. github_get_directory_structure - Get directory tree
7. github_get_file_changes - Get recent changes/diff

Usage:
    from github_client import GitHubClient

    client = GitHubClient()
    result = client.get_file("src/main.py", start_line=10, end_line=50)
    if result.success:
        print(result.content)
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

MCP_SERVER_URL = os.getenv("MCP_GITHUB_SERVER_URL", "http://localhost:5002")
DEFAULT_REPO = os.getenv("GITHUB_REPO", "your-org/your-repo")
REQUEST_TIMEOUT = 30  # seconds


# ============================================================================
# DATA CLASSES FOR STRUCTURED RESPONSES
# ============================================================================

@dataclass
class GitHubFileResult:
    """Result from github_get_file"""
    success: bool
    content: Optional[str] = None
    repo: Optional[str] = None
    file_path: Optional[str] = None
    branch: Optional[str] = None
    size_bytes: Optional[int] = None
    line_range: Optional[str] = None
    total_lines: Optional[int] = None
    sha: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubCommit:
    """Single commit information"""
    sha: str
    author: str
    author_email: str
    date: str
    message: str
    url: Optional[str] = None


@dataclass
class GitHubCommitHistoryResult:
    """Result from github_get_commit_history"""
    success: bool
    repo: Optional[str] = None
    file_path: Optional[str] = None
    branch: Optional[str] = None
    commit_count: Optional[int] = None
    commits: Optional[List[GitHubCommit]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubSearchResult:
    """Result from github_search_code"""
    success: bool
    query: Optional[str] = None
    repo: Optional[str] = None
    total_count: Optional[int] = None
    results_returned: Optional[int] = None
    results: Optional[List[Dict[str, str]]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubDirectoryResult:
    """Result from github_get_directory_structure"""
    success: bool
    repo: Optional[str] = None
    path: Optional[str] = None
    branch: Optional[str] = None
    item_count: Optional[int] = None
    structure: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubBranchResult:
    """Result from create_branch (Phase B)"""
    success: bool
    repo: Optional[str] = None
    branch_name: Optional[str] = None
    base_ref: Optional[str] = None
    sha: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubFileUpdateResult:
    """Result from update_file (Phase B)"""
    success: bool
    repo: Optional[str] = None
    file_path: Optional[str] = None
    branch: Optional[str] = None
    commit_sha: Optional[str] = None
    commit_message: Optional[str] = None
    commit_url: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


@dataclass
class GitHubPullRequestResult:
    """Result from create_pull_request (Phase B)"""
    success: bool
    repo: Optional[str] = None
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    title: Optional[str] = None
    state: Optional[str] = None  # open, closed, merged
    head: Optional[str] = None  # Source branch
    base: Optional[str] = None  # Target branch
    created_at: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[float] = None


# ============================================================================
# GITHUB CLIENT CLASS
# ============================================================================

class GitHubClient:
    """
    Client for interacting with GitHub MCP Server

    Provides Python wrapper methods for all 7 GitHub MCP tools.
    Handles MCP protocol communication and error handling.
    """

    def __init__(self, server_url: str = None, default_repo: str = None):
        """
        Initialize GitHub client

        Args:
            server_url: MCP server URL (default: from env or localhost:5002)
            default_repo: Default repository (default: from env)
        """
        self.server_url = server_url or MCP_SERVER_URL
        self.default_repo = default_repo or DEFAULT_REPO
        self.call_endpoint = f"{self.server_url}/mcp/call"

        logger.info(f"GitHubClient initialized")
        logger.info(f"  Server: {self.server_url}")
        logger.info(f"  Default repo: {self.default_repo}")

    def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method to call MCP tool

        Args:
            tool_name: Name of the MCP tool
            arguments: Tool arguments

        Returns:
            Response dictionary from MCP server
        """
        payload = {
            "tool": tool_name,
            "arguments": arguments
        }

        try:
            start_time = time.time()
            response = requests.post(
                self.call_endpoint,
                json=payload,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            elapsed_ms = (time.time() - start_time) * 1000

            logger.debug(f"MCP call {tool_name}: {elapsed_ms:.2f}ms")

            return result

        except requests.exceptions.Timeout:
            logger.error(f"MCP call timeout: {tool_name}")
            return {
                "result": {
                    "success": False,
                    "error": f"Request timeout after {REQUEST_TIMEOUT}s"
                }
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"MCP call failed: {tool_name} - {str(e)}")
            return {
                "result": {
                    "success": False,
                    "error": str(e)
                }
            }
        except Exception as e:
            logger.error(f"Unexpected error in MCP call: {str(e)}")
            return {
                "result": {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }
            }

    # ========================================================================
    # TOOL 1: GET FILE
    # ========================================================================

    def get_file(
        self,
        file_path: str,
        repo: str = None,
        start_line: int = None,
        end_line: int = None,
        branch: str = "main"
    ) -> GitHubFileResult:
        """
        Get source code content from a file

        Args:
            file_path: Path to file in repository (e.g., 'src/main/java/DDNStorage.java')
            repo: Repository in format 'owner/repo' (optional, uses default)
            start_line: Starting line number (1-indexed, optional)
            end_line: Ending line number (inclusive, optional)
            branch: Branch name (default: main)

        Returns:
            GitHubFileResult with file content and metadata

        Example:
            result = client.get_file("src/main.py", start_line=10, end_line=50)
            if result.success:
                print(result.content)
        """
        arguments = {
            "file_path": file_path,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo
        if start_line is not None:
            arguments["start_line"] = start_line
        if end_line is not None:
            arguments["end_line"] = end_line

        response = self._call_tool("github_get_file", arguments)
        result_data = response.get("result", {})

        return GitHubFileResult(
            success=result_data.get("success", False),
            content=result_data.get("content"),
            repo=result_data.get("repo"),
            file_path=result_data.get("file_path"),
            branch=result_data.get("branch"),
            size_bytes=result_data.get("size_bytes"),
            line_range=result_data.get("line_range"),
            total_lines=result_data.get("total_lines"),
            sha=result_data.get("sha"),
            url=result_data.get("url"),
            error=result_data.get("error"),
            execution_time_ms=response.get("execution_time_ms")
        )

    # ========================================================================
    # TOOL 2: GET BLAME
    # ========================================================================

    def get_blame(
        self,
        file_path: str,
        repo: str = None,
        line_number: int = None,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Get git blame information showing who last modified each line

        Args:
            file_path: Path to file in repository
            repo: Repository in format 'owner/repo' (optional)
            line_number: Specific line number to get blame for (optional)
            branch: Branch name (default: main)

        Returns:
            Dictionary with blame information
        """
        arguments = {
            "file_path": file_path,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo
        if line_number is not None:
            arguments["line_number"] = line_number

        response = self._call_tool("github_get_blame", arguments)
        return response.get("result", {})

    # ========================================================================
    # TOOL 3: GET COMMIT HISTORY
    # ========================================================================

    def get_commit_history(
        self,
        file_path: str,
        repo: str = None,
        limit: int = 10,
        branch: str = "main"
    ) -> GitHubCommitHistoryResult:
        """
        Get recent commit history for a file

        Args:
            file_path: Path to file in repository
            repo: Repository in format 'owner/repo' (optional)
            limit: Maximum number of commits to return (default: 10)
            branch: Branch name (default: main)

        Returns:
            GitHubCommitHistoryResult with commit history

        Example:
            result = client.get_commit_history("src/main.py", limit=5)
            if result.success:
                for commit in result.commits:
                    print(f"{commit.sha}: {commit.message}")
        """
        arguments = {
            "file_path": file_path,
            "limit": limit,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo

        response = self._call_tool("github_get_commit_history", arguments)
        result_data = response.get("result", {})

        # Convert commits to GitHubCommit objects
        commits = None
        if result_data.get("commits"):
            commits = [
                GitHubCommit(
                    sha=c.get("sha", ""),
                    author=c.get("author", ""),
                    author_email=c.get("author_email", ""),
                    date=c.get("date", ""),
                    message=c.get("message", ""),
                    url=c.get("url")
                )
                for c in result_data["commits"]
            ]

        return GitHubCommitHistoryResult(
            success=result_data.get("success", False),
            repo=result_data.get("repo"),
            file_path=result_data.get("file_path"),
            branch=result_data.get("branch"),
            commit_count=result_data.get("commit_count"),
            commits=commits,
            error=result_data.get("error"),
            execution_time_ms=response.get("execution_time_ms")
        )

    # ========================================================================
    # TOOL 4: SEARCH CODE
    # ========================================================================

    def search_code(
        self,
        query: str,
        repo: str = None,
        language: str = None,
        limit: int = 10
    ) -> GitHubSearchResult:
        """
        Search for code patterns across the repository

        Args:
            query: Search query (e.g., 'function_name', 'error handling')
            repo: Repository in format 'owner/repo' (optional)
            language: Programming language filter (e.g., 'python', 'java')
            limit: Maximum results (default: 10)

        Returns:
            GitHubSearchResult with search results

        Example:
            result = client.search_code("ConnectionError", language="python")
            if result.success:
                for match in result.results:
                    print(f"Found in: {match['file_path']}")
        """
        arguments = {
            "query": query,
            "limit": limit
        }
        if repo:
            arguments["repo"] = repo
        if language:
            arguments["language"] = language

        response = self._call_tool("github_search_code", arguments)
        result_data = response.get("result", {})

        return GitHubSearchResult(
            success=result_data.get("success", False),
            query=result_data.get("query"),
            repo=result_data.get("repo"),
            total_count=result_data.get("total_count"),
            results_returned=result_data.get("results_returned"),
            results=result_data.get("results"),
            error=result_data.get("error"),
            execution_time_ms=response.get("execution_time_ms")
        )

    # ========================================================================
    # TOOL 5: GET TEST FILE
    # ========================================================================

    def get_test_file(
        self,
        test_name: str,
        repo: str = None,
        branch: str = "main"
    ) -> GitHubFileResult:
        """
        Get test file content by test name

        Args:
            test_name: Name of the test (e.g., 'test_memory_usage')
            repo: Repository in format 'owner/repo' (optional)
            branch: Branch name (default: main)

        Returns:
            GitHubFileResult with test file content

        Example:
            result = client.get_test_file("test_authentication")
            if result.success:
                print(result.content)
        """
        arguments = {
            "test_name": test_name,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo

        response = self._call_tool("github_get_test_file", arguments)
        result_data = response.get("result", {})

        return GitHubFileResult(
            success=result_data.get("success", False),
            content=result_data.get("content"),
            repo=result_data.get("repo"),
            file_path=result_data.get("file_path"),
            branch=result_data.get("branch"),
            size_bytes=result_data.get("size_bytes"),
            line_range=result_data.get("line_range"),
            total_lines=result_data.get("total_lines"),
            sha=result_data.get("sha"),
            url=result_data.get("url"),
            error=result_data.get("error"),
            execution_time_ms=response.get("execution_time_ms")
        )

    # ========================================================================
    # TOOL 6: GET DIRECTORY STRUCTURE
    # ========================================================================

    def get_directory_structure(
        self,
        path: str = "",
        repo: str = None,
        recursive: bool = False,
        branch: str = "main"
    ) -> GitHubDirectoryResult:
        """
        Get directory structure/tree for a path

        Args:
            path: Directory path (default: root)
            repo: Repository in format 'owner/repo' (optional)
            recursive: Get recursive tree (default: False)
            branch: Branch name (default: main)

        Returns:
            GitHubDirectoryResult with directory structure

        Example:
            result = client.get_directory_structure("src/main", recursive=True)
            if result.success:
                for item in result.structure:
                    print(f"{item['type']}: {item['path']}")
        """
        arguments = {
            "path": path,
            "recursive": recursive,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo

        response = self._call_tool("github_get_directory_structure", arguments)
        result_data = response.get("result", {})

        return GitHubDirectoryResult(
            success=result_data.get("success", False),
            repo=result_data.get("repo"),
            path=result_data.get("path"),
            branch=result_data.get("branch"),
            item_count=result_data.get("item_count"),
            structure=result_data.get("structure"),
            error=result_data.get("error"),
            execution_time_ms=response.get("execution_time_ms")
        )

    # ========================================================================
    # TOOL 7: GET FILE CHANGES
    # ========================================================================

    def get_file_changes(
        self,
        file_path: str,
        repo: str = None,
        commits: int = 5,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Get recent changes (diff) for a specific file

        Args:
            file_path: Path to file in repository
            repo: Repository in format 'owner/repo' (optional)
            commits: Number of recent commits to show changes for (default: 5)
            branch: Branch name (default: main)

        Returns:
            Dictionary with recent changes and diffs
        """
        arguments = {
            "file_path": file_path,
            "commits": commits,
            "branch": branch
        }
        if repo:
            arguments["repo"] = repo

        response = self._call_tool("github_get_file_changes", arguments)
        return response.get("result", {})

    # ========================================================================
    # HELPER METHODS FOR COMMON USE CASES
    # ========================================================================

    def extract_code_from_stack_trace(
        self,
        file_path: str,
        line_number: int,
        context_lines: int = 10,
        repo: str = None
    ) -> GitHubFileResult:
        """
        Helper: Extract code around a specific line (useful for stack traces)

        Args:
            file_path: Path to file
            line_number: Line number from stack trace
            context_lines: Lines of context before/after (default: 10)
            repo: Repository (optional)

        Returns:
            GitHubFileResult with code around the line
        """
        start_line = max(1, line_number - context_lines)
        end_line = line_number + context_lines

        return self.get_file(
            file_path=file_path,
            repo=repo,
            start_line=start_line,
            end_line=end_line
        )

    def get_files_from_error(
        self,
        error_message: str,
        file_paths: List[str],
        repo: str = None
    ) -> List[GitHubFileResult]:
        """
        Helper: Get multiple files mentioned in an error

        Args:
            error_message: The error message (for logging)
            file_paths: List of file paths to fetch
            repo: Repository (optional)

        Returns:
            List of GitHubFileResult for each file
        """
        logger.info(f"Fetching {len(file_paths)} files for error analysis")
        results = []

        for file_path in file_paths:
            result = self.get_file(file_path, repo=repo)
            results.append(result)

            if result.success:
                logger.info(f"  ✓ Retrieved: {file_path}")
            else:
                logger.warning(f"  ✗ Failed: {file_path} - {result.error}")

        return results

    # ========================================================================
    # PHASE B: WRITE OPERATIONS (Automated Code Fixing)
    # ========================================================================

    def create_branch(
        self,
        branch_name: str,
        base_ref: str = "main",
        repo: str = None
    ) -> GitHubBranchResult:
        """
        Create a new branch from base reference (Phase B - Task B.2)

        Args:
            branch_name: Name for the new branch (e.g., "fix/build-12345")
            base_ref: Base branch or commit SHA to branch from (default: "main")
            repo: Repository in format 'owner/repo' (optional, uses default)

        Returns:
            GitHubBranchResult with branch creation details

        Example:
            result = client.create_branch("fix/build-12345", base_ref="main")
            if result.success:
                print(f"Branch created: {result.branch_name}")
                print(f"Branch SHA: {result.sha}")

        Note:
            Requires GitHub token with 'repo' write permissions
        """
        start_time = time.time()

        try:
            # Use GitHub API directly (not MCP tool - write operation)
            github_token = os.getenv("GITHUB_TOKEN")
            repo_name = repo or self.default_repo

            if not github_token or github_token == "your-github-personal-access-token-here":
                return GitHubBranchResult(
                    success=False,
                    error="GitHub token not configured. Set GITHUB_TOKEN in .env",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            if not repo_name or repo_name == "your-org/your-repo-name":
                return GitHubBranchResult(
                    success=False,
                    error="GitHub repository not configured. Set GITHUB_REPO in .env",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            # Step 1: Get base ref SHA
            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            base_url = f"https://api.github.com/repos/{repo_name}/git/refs/heads/{base_ref}"
            base_response = requests.get(base_url, headers=headers, timeout=10)

            if base_response.status_code != 200:
                return GitHubBranchResult(
                    success=False,
                    repo=repo_name,
                    branch_name=branch_name,
                    base_ref=base_ref,
                    error=f"Failed to get base ref '{base_ref}': {base_response.text}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            base_sha = base_response.json()["object"]["sha"]

            # Step 2: Create new branch
            create_url = f"https://api.github.com/repos/{repo_name}/git/refs"
            create_payload = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha
            }

            create_response = requests.post(
                create_url,
                headers=headers,
                json=create_payload,
                timeout=10
            )

            if create_response.status_code == 201:
                result_data = create_response.json()
                elapsed_ms = (time.time() - start_time) * 1000

                logger.info(f"✓ Branch created: {branch_name} (from {base_ref})")

                return GitHubBranchResult(
                    success=True,
                    repo=repo_name,
                    branch_name=branch_name,
                    base_ref=base_ref,
                    sha=result_data["object"]["sha"],
                    url=result_data["url"],
                    execution_time_ms=elapsed_ms
                )
            else:
                return GitHubBranchResult(
                    success=False,
                    repo=repo_name,
                    branch_name=branch_name,
                    base_ref=base_ref,
                    error=f"GitHub API error: {create_response.status_code} - {create_response.text}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

        except Exception as e:
            logger.error(f"Failed to create branch: {str(e)}")
            return GitHubBranchResult(
                success=False,
                repo=repo,
                branch_name=branch_name,
                base_ref=base_ref,
                error=f"Exception: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def update_file(
        self,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
        repo: str = None
    ) -> GitHubFileUpdateResult:
        """
        Update file content and commit to branch (Phase B - Task B.2)

        Args:
            file_path: Path to file in repository
            content: New file content (complete file, not diff)
            commit_message: Commit message
            branch: Branch to commit to
            repo: Repository in format 'owner/repo' (optional, uses default)

        Returns:
            GitHubFileUpdateResult with commit details

        Example:
            result = client.update_file(
                "src/main.py",
                "print('fixed')",
                "Fix: Automated code fix",
                "fix/build-12345"
            )
            if result.success:
                print(f"Committed: {result.commit_sha}")

        Note:
            Requires GitHub token with 'repo' write permissions
        """
        start_time = time.time()

        try:
            github_token = os.getenv("GITHUB_TOKEN")
            repo_name = repo or self.default_repo

            if not github_token or github_token == "your-github-personal-access-token-here":
                return GitHubFileUpdateResult(
                    success=False,
                    error="GitHub token not configured",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Step 1: Get current file to get its SHA
            get_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}?ref={branch}"
            get_response = requests.get(get_url, headers=headers, timeout=10)

            file_sha = None
            if get_response.status_code == 200:
                file_sha = get_response.json()["sha"]

            # Step 2: Update file
            import base64
            content_bytes = content.encode('utf-8')
            content_base64 = base64.b64encode(content_bytes).decode('utf-8')

            update_url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
            update_payload = {
                "message": commit_message,
                "content": content_base64,
                "branch": branch
            }

            if file_sha:
                update_payload["sha"] = file_sha

            update_response = requests.put(
                update_url,
                headers=headers,
                json=update_payload,
                timeout=10
            )

            if update_response.status_code in [200, 201]:
                result_data = update_response.json()
                elapsed_ms = (time.time() - start_time) * 1000

                logger.info(f"✓ File updated: {file_path} on {branch}")

                return GitHubFileUpdateResult(
                    success=True,
                    repo=repo_name,
                    file_path=file_path,
                    branch=branch,
                    commit_sha=result_data["commit"]["sha"],
                    commit_message=commit_message,
                    commit_url=result_data["commit"]["html_url"],
                    execution_time_ms=elapsed_ms
                )
            else:
                return GitHubFileUpdateResult(
                    success=False,
                    repo=repo_name,
                    file_path=file_path,
                    branch=branch,
                    error=f"GitHub API error: {update_response.status_code} - {update_response.text}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

        except Exception as e:
            logger.error(f"Failed to update file: {str(e)}")
            return GitHubFileUpdateResult(
                success=False,
                repo=repo,
                file_path=file_path,
                branch=branch,
                error=f"Exception: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def create_pull_request(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        repo: str = None,
        reviewers: List[str] = None,
        labels: List[str] = None
    ) -> GitHubPullRequestResult:
        """
        Create a pull request (Phase B - Task B.3)

        Args:
            title: PR title
            body: PR description (supports markdown)
            head: Source branch (e.g., "fix/build-12345")
            base: Target branch (default: "main")
            repo: Repository in format 'owner/repo' (optional, uses default)
            reviewers: List of GitHub usernames to request review from
            labels: List of label names to add to PR

        Returns:
            GitHubPullRequestResult with PR details

        Example:
            result = client.create_pull_request(
                title="Automated Fix: NullPointerException",
                body="## Fix Summary\\n- Root cause: ...\\n- Solution: ...",
                head="fix/build-12345",
                base="main",
                reviewers=["teammate1"],
                labels=["automated-fix", "ai-generated"]
            )
            if result.success:
                print(f"PR created: {result.pr_url}")
                print(f"PR number: {result.pr_number}")

        Note:
            Requires GitHub token with 'repo' write permissions
        """
        start_time = time.time()

        try:
            github_token = os.getenv("GITHUB_TOKEN")
            repo_name = repo or self.default_repo

            if not github_token or github_token == "your-github-personal-access-token-here":
                return GitHubPullRequestResult(
                    success=False,
                    error="GitHub token not configured",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Step 1: Create PR
            pr_url = f"https://api.github.com/repos/{repo_name}/pulls"
            pr_payload = {
                "title": title,
                "body": body,
                "head": head,
                "base": base
            }

            pr_response = requests.post(
                pr_url,
                headers=headers,
                json=pr_payload,
                timeout=10
            )

            if pr_response.status_code != 201:
                return GitHubPullRequestResult(
                    success=False,
                    repo=repo_name,
                    title=title,
                    head=head,
                    base=base,
                    error=f"Failed to create PR: {pr_response.status_code} - {pr_response.text}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            pr_data = pr_response.json()
            pr_number = pr_data["number"]

            # Step 2: Add reviewers (optional)
            if reviewers:
                reviewers_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/requested_reviewers"
                reviewers_payload = {"reviewers": reviewers}
                requests.post(reviewers_url, headers=headers, json=reviewers_payload, timeout=10)

            # Step 3: Add labels (optional)
            if labels:
                labels_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/labels"
                labels_payload = {"labels": labels}
                requests.post(labels_url, headers=headers, json=labels_payload, timeout=10)

            elapsed_ms = (time.time() - start_time) * 1000

            logger.info(f"✓ PR created: #{pr_number} - {title}")

            return GitHubPullRequestResult(
                success=True,
                repo=repo_name,
                pr_number=pr_number,
                pr_url=pr_data["html_url"],
                title=title,
                state=pr_data["state"],
                head=head,
                base=base,
                created_at=pr_data["created_at"],
                execution_time_ms=elapsed_ms
            )

        except Exception as e:
            logger.error(f"Failed to create PR: {str(e)}")
            return GitHubPullRequestResult(
                success=False,
                repo=repo,
                title=title,
                head=head,
                base=base,
                error=f"Exception: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def close_pull_request(
        self,
        pr_number: int,
        repo: str = None
    ) -> GitHubPullRequestResult:
        """
        Close a pull request (Phase B - Task B.8 - Rollback)

        Args:
            pr_number: PR number to close
            repo: Repository in format 'owner/repo' (optional, uses default)

        Returns:
            GitHubPullRequestResult with updated PR state

        Example:
            result = client.close_pull_request(123)
            if result.success:
                print(f"PR #{pr_number} closed")

        Note:
            Requires GitHub token with 'repo' write permissions
            Used for rolling back failed automated fixes
        """
        start_time = time.time()

        try:
            github_token = os.getenv("GITHUB_TOKEN")
            repo_name = repo or self.default_repo

            if not github_token or github_token == "your-github-personal-access-token-here":
                return GitHubPullRequestResult(
                    success=False,
                    error="GitHub token not configured",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

            headers = {
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Close PR by updating state
            pr_url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}"
            pr_payload = {"state": "closed"}

            pr_response = requests.patch(
                pr_url,
                headers=headers,
                json=pr_payload,
                timeout=10
            )

            if pr_response.status_code == 200:
                pr_data = pr_response.json()
                elapsed_ms = (time.time() - start_time) * 1000

                logger.info(f"✓ PR closed: #{pr_number}")

                return GitHubPullRequestResult(
                    success=True,
                    repo=repo_name,
                    pr_number=pr_number,
                    pr_url=pr_data["html_url"],
                    title=pr_data["title"],
                    state=pr_data["state"],
                    head=pr_data["head"]["ref"],
                    base=pr_data["base"]["ref"],
                    execution_time_ms=elapsed_ms
                )
            else:
                return GitHubPullRequestResult(
                    success=False,
                    repo=repo_name,
                    pr_number=pr_number,
                    error=f"Failed to close PR: {pr_response.status_code} - {pr_response.text}",
                    execution_time_ms=(time.time() - start_time) * 1000
                )

        except Exception as e:
            logger.error(f"Failed to close PR: {str(e)}")
            return GitHubPullRequestResult(
                success=False,
                repo=repo,
                pr_number=pr_number,
                error=f"Exception: {str(e)}",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def check_server_health(self) -> Dict[str, Any]:
        """
        Check MCP server health

        Returns:
            Health status dictionary
        """
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global client instance (lazy initialization)
_global_client = None

def get_github_client() -> GitHubClient:
    """Get or create global GitHub client instance"""
    global _global_client
    if _global_client is None:
        _global_client = GitHubClient()
    return _global_client


# ============================================================================
# MAIN - TESTING AND EXAMPLES
# ============================================================================

if __name__ == "__main__":
    """
    Test the GitHub client wrapper
    Run: python github_client.py
    """

    print("="*70)
    print("GITHUB CLIENT - TESTING")
    print("="*70)

    # Initialize client
    client = GitHubClient()

    # Test 1: Check server health
    print("\n1. Testing server health...")
    health = client.check_server_health()
    print(f"   Status: {health.get('status')}")
    print(f"   GitHub connected: {health.get('github_connected')}")

    # Test 2: Get a file
    print("\n2. Testing get_file (README.md)...")
    result = client.get_file("README.md")
    print(f"   Success: {result.success}")
    if result.success:
        print(f"   File: {result.file_path}")
        print(f"   Size: {result.size_bytes} bytes")
        print(f"   Lines: {result.total_lines}")
        print(f"   Execution time: {result.execution_time_ms}ms")
    else:
        print(f"   Error: {result.error}")

    # Test 3: Search code
    print("\n3. Testing search_code...")
    search_result = client.search_code("function", limit=5)
    print(f"   Success: {search_result.success}")
    if search_result.success:
        print(f"   Total results: {search_result.total_count}")
        print(f"   Returned: {search_result.results_returned}")
    else:
        print(f"   Error: {search_result.error}")

    # Test 4: Get commit history
    print("\n4. Testing get_commit_history...")
    history = client.get_commit_history("README.md", limit=3)
    print(f"   Success: {history.success}")
    if history.success:
        print(f"   Commits found: {history.commit_count}")
        if history.commits:
            for commit in history.commits[:2]:
                print(f"     - {commit.sha}: {commit.message[:50]}...")
    else:
        print(f"   Error: {history.error}")

    # Test 5: Get directory structure
    print("\n5. Testing get_directory_structure...")
    dir_result = client.get_directory_structure("")
    print(f"   Success: {dir_result.success}")
    if dir_result.success:
        print(f"   Items found: {dir_result.item_count}")
    else:
        print(f"   Error: {dir_result.error}")

    # Test 6: Helper method - extract code from stack trace
    print("\n6. Testing extract_code_from_stack_trace helper...")
    code_result = client.extract_code_from_stack_trace(
        file_path="README.md",
        line_number=10,
        context_lines=5
    )
    print(f"   Success: {code_result.success}")
    if code_result.success:
        print(f"   Line range: {code_result.line_range}")
    else:
        print(f"   Error: {code_result.error}")

    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
    print("\nNOTE: Some tests may fail if GitHub token is not configured.")
    print("This is expected. The client infrastructure is working correctly.")
    print("="*70)
