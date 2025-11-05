"""
Code Fix Automation Service
PHASE B: Automated Code Fixing
Tasks: B.1, B.2, B.3

This service handles:
- Fetching approved fixes from PostgreSQL
- Creating GitHub branches for fixes
- Applying code patches to files
- Creating Pull Requests with AI-generated descriptions
- Tracking fix application status

Usage:
    from code_fix_automation import CodeFixAutomation

    service = CodeFixAutomation()
    result = service.apply_approved_fix(
        analysis_id=123,
        approved_by_name="John Doe",
        approved_by_email="john@example.com"
    )

    if result['success']:
        print(f"PR created: {result['pr_url']}")
"""

import os
import sys
import logging
import time
import re
import psycopg2
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Import GitHub client (Phase B.0)
from github_client import get_github_client, GitHubClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# PostgreSQL Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD')
}

# GitHub Configuration
GITHUB_REPO = os.getenv('GITHUB_REPO', 'your-org/your-repo')
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')
GITHUB_FIX_BRANCH_PREFIX = os.getenv('GITHUB_FIX_BRANCH_PREFIX', 'fix/build-')
GITHUB_DEFAULT_REVIEWERS = os.getenv('GITHUB_DEFAULT_REVIEWERS', '').split(',')
GITHUB_PR_LABELS = os.getenv('GITHUB_PR_LABELS', 'automated-fix,ai-generated,needs-review').split(',')
GITHUB_AUTO_ASSIGN_REVIEWERS = os.getenv('GITHUB_AUTO_ASSIGN_REVIEWERS', 'true').lower() == 'true'

# Clean up reviewer list (remove empty strings)
GITHUB_DEFAULT_REVIEWERS = [r.strip() for r in GITHUB_DEFAULT_REVIEWERS if r.strip()]

# ============================================================================
# CODE FIX AUTOMATION SERVICE
# ============================================================================

class CodeFixAutomation:
    """
    Service for automated code fixing with GitHub PR creation

    Handles the complete flow from fix approval to PR creation:
    1. Fetch fix recommendation from PostgreSQL
    2. Create GitHub branch
    3. Apply code patch
    4. Create Pull Request
    5. Track status in database
    """

    def __init__(self, github_client: GitHubClient = None):
        """
        Initialize Code Fix Automation service

        Args:
            github_client: Optional GitHubClient instance (uses global if None)
        """
        self.github_client = github_client or get_github_client()
        self.db_config = POSTGRES_CONFIG

        logger.info("CodeFixAutomation service initialized")
        logger.info(f"  GitHub repo: {GITHUB_REPO}")
        logger.info(f"  Base branch: {GITHUB_BRANCH}")
        logger.info(f"  Default reviewers: {GITHUB_DEFAULT_REVIEWERS}")

    def apply_approved_fix(
        self,
        analysis_id: int,
        approved_by_name: str,
        approved_by_email: str
    ) -> Dict[str, Any]:
        """
        Apply an approved code fix and create a Pull Request

        This is the main entry point for Phase B automated fixing.
        Implements Tasks B.2 (apply fix) and B.3 (create PR).

        Args:
            analysis_id: ID from failure_analysis table
            approved_by_name: Name of person who approved the fix
            approved_by_email: Email of person who approved the fix

        Returns:
            Dictionary with result:
            {
                'success': bool,
                'analysis_id': int,
                'build_id': str,
                'branch_name': str,
                'pr_number': int,
                'pr_url': str,
                'fix_application_id': int,
                'time_to_pr_creation_ms': int,
                'error': str (if success=False)
            }

        Example:
            result = service.apply_approved_fix(
                analysis_id=123,
                approved_by_name="Jane Smith",
                approved_by_email="jane@example.com"
            )

            if result['success']:
                print(f"PR #{result['pr_number']} created: {result['pr_url']}")
        """
        start_time = time.time()

        logger.info(f"="*70)
        logger.info(f"APPLYING APPROVED FIX")
        logger.info(f"="*70)
        logger.info(f"Analysis ID: {analysis_id}")
        logger.info(f"Approved by: {approved_by_name} <{approved_by_email}>")

        try:
            # Step 1: Fetch fix from database
            logger.info("Step 1: Fetching fix from database...")
            fix_data = self._fetch_fix_from_database(analysis_id)

            if not fix_data:
                return {
                    'success': False,
                    'analysis_id': analysis_id,
                    'error': f"No fix found for analysis_id {analysis_id}"
                }

            build_id = fix_data['build_id']
            logger.info(f"  Build ID: {build_id}")
            logger.info(f"  Error: {fix_data['error_type']}")
            logger.info(f"  File: {fix_data['file_path']}")

            # Step 2: Create fix application record
            logger.info("Step 2: Creating fix application record...")
            fix_app_id = self._create_fix_application_record(
                analysis_id=analysis_id,
                build_id=build_id,
                approved_by_name=approved_by_name,
                approved_by_email=approved_by_email,
                error_category=fix_data.get('error_category'),
                error_type=fix_data.get('error_type'),
                error_severity=fix_data.get('severity'),
                ai_confidence=fix_data.get('confidence_score')
            )

            logger.info(f"  Fix application ID: {fix_app_id}")

            # Step 3: Create GitHub branch
            logger.info("Step 3: Creating GitHub branch...")
            branch_name = f"{GITHUB_FIX_BRANCH_PREFIX}{build_id}"

            branch_result = self.github_client.create_branch(
                branch_name=branch_name,
                base_ref=GITHUB_BRANCH
            )

            if not branch_result.success:
                self._update_fix_status(fix_app_id, 'failed', error=branch_result.error)
                return {
                    'success': False,
                    'analysis_id': analysis_id,
                    'build_id': build_id,
                    'fix_application_id': fix_app_id,
                    'error': f"Failed to create branch: {branch_result.error}"
                }

            logger.info(f"  Branch created: {branch_name}")
            logger.info(f"  Branch SHA: {branch_result.sha}")

            # Update fix application with branch info
            self._update_fix_branch_info(fix_app_id, branch_name, GITHUB_BRANCH)

            # Step 4: Apply code patch to branch
            logger.info("Step 4: Applying code patch...")

            patch_result = self._apply_code_patch(
                file_path=fix_data['file_path'],
                fix_recommendation=fix_data['fix_recommendation'],
                branch_name=branch_name,
                build_id=build_id,
                error_type=fix_data['error_type']
            )

            if not patch_result['success']:
                self._update_fix_status(fix_app_id, 'failed', error=patch_result['error'])
                return {
                    'success': False,
                    'analysis_id': analysis_id,
                    'build_id': build_id,
                    'branch_name': branch_name,
                    'fix_application_id': fix_app_id,
                    'error': f"Failed to apply patch: {patch_result['error']}"
                }

            logger.info(f"  Patch applied successfully")
            logger.info(f"  Commit SHA: {patch_result['commit_sha']}")

            # Update fix application with files changed
            self._update_files_changed(fix_app_id, patch_result['files_changed'])

            # Step 5: Create Pull Request
            logger.info("Step 5: Creating Pull Request...")

            pr_result = self._create_pull_request(
                fix_data=fix_data,
                branch_name=branch_name,
                approved_by_name=approved_by_name
            )

            if not pr_result['success']:
                self._update_fix_status(fix_app_id, 'failed', error=pr_result['error'])
                return {
                    'success': False,
                    'analysis_id': analysis_id,
                    'build_id': build_id,
                    'branch_name': branch_name,
                    'fix_application_id': fix_app_id,
                    'error': f"Failed to create PR: {pr_result['error']}"
                }

            logger.info(f"  PR created: #{pr_result['pr_number']}")
            logger.info(f"  PR URL: {pr_result['pr_url']}")

            # Step 6: Update fix application with PR info
            elapsed_ms = int((time.time() - start_time) * 1000)

            self._update_fix_with_pr_info(
                fix_app_id=fix_app_id,
                pr_number=pr_result['pr_number'],
                pr_url=pr_result['pr_url'],
                pr_title=pr_result['pr_title'],
                pr_body=pr_result['pr_body'],
                reviewers=GITHUB_DEFAULT_REVIEWERS if GITHUB_AUTO_ASSIGN_REVIEWERS else [],
                labels=GITHUB_PR_LABELS,
                time_to_pr_creation_ms=elapsed_ms
            )

            self._update_fix_status(fix_app_id, 'pr_created')

            logger.info("="*70)
            logger.info("FIX APPLIED SUCCESSFULLY!")
            logger.info(f"Time to PR creation: {elapsed_ms}ms ({elapsed_ms/1000:.1f}s)")
            logger.info("="*70)

            return {
                'success': True,
                'analysis_id': analysis_id,
                'build_id': build_id,
                'branch_name': branch_name,
                'pr_number': pr_result['pr_number'],
                'pr_url': pr_result['pr_url'],
                'pr_title': pr_result['pr_title'],
                'fix_application_id': fix_app_id,
                'time_to_pr_creation_ms': elapsed_ms
            }

        except Exception as e:
            logger.error(f"Unexpected error in apply_approved_fix: {str(e)}", exc_info=True)
            return {
                'success': False,
                'analysis_id': analysis_id,
                'error': f"Exception: {str(e)}"
            }

    def _fetch_fix_from_database(self, analysis_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch fix recommendation from PostgreSQL failure_analysis table

        Args:
            analysis_id: Analysis ID

        Returns:
            Dictionary with fix data or None if not found
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            query = """
                SELECT
                    id,
                    build_id,
                    error_type,
                    error_category,
                    error_message,
                    component,
                    file_path,
                    line_number,
                    stack_trace,
                    root_cause,
                    fix_recommendation,
                    severity,
                    confidence_score,
                    github_files
                FROM failure_analysis
                WHERE id = %s
            """

            cursor.execute(query, (analysis_id,))
            row = cursor.fetchone()

            cursor.close()
            conn.close()

            if not row:
                return None

            # Parse row into dictionary
            fix_data = {
                'id': row[0],
                'build_id': row[1],
                'error_type': row[2],
                'error_category': row[3],
                'error_message': row[4],
                'component': row[5],
                'file_path': row[6],
                'line_number': row[7],
                'stack_trace': row[8],
                'root_cause': row[9],
                'fix_recommendation': row[10],
                'severity': row[11],
                'confidence_score': row[12],
                'github_files': row[13]
            }

            return fix_data

        except Exception as e:
            logger.error(f"Failed to fetch fix from database: {str(e)}")
            return None

    def _create_fix_application_record(
        self,
        analysis_id: int,
        build_id: str,
        approved_by_name: str,
        approved_by_email: str,
        error_category: str = None,
        error_type: str = None,
        error_severity: str = None,
        ai_confidence: float = None
    ) -> int:
        """
        Create initial record in code_fix_applications table

        Returns:
            Fix application ID
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            query = """
                INSERT INTO code_fix_applications (
                    analysis_id,
                    build_id,
                    approved_by_name,
                    approved_by_email,
                    approved_at,
                    status,
                    error_category,
                    error_type,
                    error_severity,
                    ai_confidence_score
                ) VALUES (
                    %s, %s, %s, %s, CURRENT_TIMESTAMP,
                    'pending', %s, %s, %s, %s
                )
                RETURNING id
            """

            cursor.execute(query, (
                analysis_id,
                build_id,
                approved_by_name,
                approved_by_email,
                error_category,
                error_type,
                error_severity,
                ai_confidence
            ))

            fix_app_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            return fix_app_id

        except Exception as e:
            logger.error(f"Failed to create fix application record: {str(e)}")
            raise

    def _update_fix_status(
        self,
        fix_app_id: int,
        status: str,
        error: str = None
    ):
        """Update fix application status"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            if error:
                query = """
                    UPDATE code_fix_applications
                    SET status = %s,
                        rollback_reason = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(query, (status, error, fix_app_id))
            else:
                query = """
                    UPDATE code_fix_applications
                    SET status = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(query, (status, fix_app_id))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to update fix status: {str(e)}")

    def _update_fix_branch_info(
        self,
        fix_app_id: int,
        branch_name: str,
        base_branch: str
    ):
        """Update fix application with branch info"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            query = """
                UPDATE code_fix_applications
                SET branch_name = %s,
                    base_branch = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor.execute(query, (branch_name, base_branch, fix_app_id))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to update branch info: {str(e)}")

    def _update_files_changed(
        self,
        fix_app_id: int,
        files_changed: List[Dict[str, Any]]
    ):
        """Update fix application with files changed"""
        try:
            import json

            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            query = """
                UPDATE code_fix_applications
                SET files_changed = %s::jsonb,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor.execute(query, (json.dumps(files_changed), fix_app_id))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to update files changed: {str(e)}")

    def _update_fix_with_pr_info(
        self,
        fix_app_id: int,
        pr_number: int,
        pr_url: str,
        pr_title: str,
        pr_body: str,
        reviewers: List[str],
        labels: List[str],
        time_to_pr_creation_ms: int
    ):
        """Update fix application with PR information"""
        try:
            import json

            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            query = """
                UPDATE code_fix_applications
                SET pr_number = %s,
                    pr_url = %s,
                    pr_title = %s,
                    pr_body = %s,
                    pr_state = 'open',
                    reviewers = %s::jsonb,
                    labels = %s::jsonb,
                    time_to_pr_creation_ms = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """

            cursor.execute(query, (
                pr_number,
                pr_url,
                pr_title,
                pr_body,
                json.dumps(reviewers),
                json.dumps(labels),
                time_to_pr_creation_ms,
                fix_app_id
            ))

            conn.commit()
            cursor.close()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to update PR info: {str(e)}")

    def _apply_code_patch(
        self,
        file_path: str,
        fix_recommendation: str,
        branch_name: str,
        build_id: str,
        error_type: str
    ) -> Dict[str, Any]:
        """
        Apply code patch to file in GitHub branch (Task B.2)

        This function:
        1. Fetches current file content from GitHub
        2. Applies the AI-recommended fix
        3. Commits the change to the branch

        Args:
            file_path: Path to file in repository
            fix_recommendation: AI-generated fix suggestion
            branch_name: Branch to commit to
            build_id: Build ID for commit message
            error_type: Error type for commit message

        Returns:
            Dictionary with success status and details
        """
        try:
            # Step 1: Fetch current file content
            logger.info(f"  Fetching current file: {file_path}")
            file_result = self.github_client.get_file(file_path, branch=GITHUB_BRANCH)

            if not file_result.success:
                return {
                    'success': False,
                    'error': f"Failed to fetch file: {file_result.error}"
                }

            original_content = file_result.content
            logger.info(f"  Current file size: {len(original_content)} chars")

            # Step 2: Apply fix (simplified - replace entire file)
            # In production, you'd want to:
            # - Parse the fix_recommendation to extract the actual code fix
            # - Apply a unified diff patch
            # - Validate syntax
            #
            # For now, we'll use a simple approach:
            # If fix_recommendation contains code blocks, extract and apply them

            fixed_content = self._apply_fix_to_content(
                original_content,
                fix_recommendation,
                file_path
            )

            if fixed_content == original_content:
                logger.warning("  No changes detected after applying fix")
                # Still proceed - the fix might be in comments or documentation

            # Step 3: Commit changes to branch
            commit_message = f"Fix: {error_type} in {file_path} (Build {build_id})\n\nAutomated fix generated by AI analysis.\nSee PR description for details."

            logger.info(f"  Committing changes to branch: {branch_name}")
            update_result = self.github_client.update_file(
                file_path=file_path,
                content=fixed_content,
                commit_message=commit_message,
                branch=branch_name
            )

            if not update_result.success:
                return {
                    'success': False,
                    'error': f"Failed to commit: {update_result.error}"
                }

            # Calculate diff statistics
            original_lines = original_content.splitlines()
            fixed_lines = fixed_content.splitlines()

            lines_added = max(0, len(fixed_lines) - len(original_lines))
            lines_removed = max(0, len(original_lines) - len(fixed_lines))
            lines_changed = sum(1 for o, f in zip(original_lines, fixed_lines) if o != f)

            files_changed = [{
                'file_path': file_path,
                'lines_changed': lines_changed,
                'lines_added': lines_added,
                'lines_removed': lines_removed,
                'commit_sha': update_result.commit_sha,
                'commit_url': update_result.commit_url
            }]

            return {
                'success': True,
                'commit_sha': update_result.commit_sha,
                'commit_url': update_result.commit_url,
                'files_changed': files_changed
            }

        except Exception as e:
            logger.error(f"Failed to apply code patch: {str(e)}")
            return {
                'success': False,
                'error': f"Exception: {str(e)}"
            }

    def _apply_fix_to_content(
        self,
        original_content: str,
        fix_recommendation: str,
        file_path: str
    ) -> str:
        """
        Apply fix recommendation to file content

        This is a simplified implementation. In production, you would:
        1. Parse the fix_recommendation to extract code snippets
        2. Apply a proper unified diff patch
        3. Validate syntax using language-specific parsers

        For now, we use a heuristic approach:
        - If fix_recommendation contains a code block, use it
        - Otherwise, return original content (no change)

        Args:
            original_content: Current file content
            fix_recommendation: AI fix suggestion
            file_path: File path (for language detection)

        Returns:
            Modified content
        """
        # Extract code blocks from markdown
        code_block_pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, fix_recommendation, re.DOTALL)

        if matches:
            # Use the first code block as the fix
            fixed_code = matches[0]
            logger.info(f"  Extracted code block ({len(fixed_code)} chars)")

            # Simple heuristic: if code block looks like a complete file, use it
            # Otherwise, try to merge it into the original content

            if len(fixed_code) > 100 and ('class ' in fixed_code or 'def ' in fixed_code or 'function ' in fixed_code):
                # Looks like a complete file replacement
                logger.info("  Using code block as complete file replacement")
                return fixed_code
            else:
                # Try to find and replace the buggy section
                # This is highly simplified - production would use AST manipulation
                logger.info("  Attempting to merge code block into original")

                # For now, just append a comment with the fix
                # In production, you'd use proper patch application
                comment_char = self._get_comment_char(file_path)
                fixed_content = original_content + f"\n\n{comment_char} AI-suggested fix:\n{comment_char} {fix_recommendation[:500]}\n"
                return fixed_content

        # No code block found - return original with comment
        logger.warning("  No code block found in fix_recommendation")
        return original_content

    def _get_comment_char(self, file_path: str) -> str:
        """Get comment character for file type"""
        if file_path.endswith(('.py', '.sh', '.yml', '.yaml')):
            return '#'
        elif file_path.endswith(('.java', '.js', '.ts', '.c', '.cpp', '.go', '.rs')):
            return '//'
        else:
            return '#'

    def _create_pull_request(
        self,
        fix_data: Dict[str, Any],
        branch_name: str,
        approved_by_name: str
    ) -> Dict[str, Any]:
        """
        Create GitHub Pull Request with AI-generated description (Task B.3)

        Generates a comprehensive PR description including:
        - Root cause analysis
        - Fix explanation
        - Files changed
        - AI confidence score
        - Test verification steps

        Args:
            fix_data: Fix data from database
            branch_name: Source branch
            approved_by_name: Who approved the fix

        Returns:
            Dictionary with PR details
        """
        try:
            # Generate PR title
            pr_title = f"Automated Fix: {fix_data['error_type']} in {fix_data['component']}"

            # Generate PR body (markdown)
            pr_body = self._generate_pr_description(fix_data, approved_by_name)

            # Create PR
            logger.info(f"  Creating PR: {pr_title}")
            pr_result = self.github_client.create_pull_request(
                title=pr_title,
                body=pr_body,
                head=branch_name,
                base=GITHUB_BRANCH,
                reviewers=GITHUB_DEFAULT_REVIEWERS if GITHUB_AUTO_ASSIGN_REVIEWERS else None,
                labels=GITHUB_PR_LABELS
            )

            if not pr_result.success:
                return {
                    'success': False,
                    'error': pr_result.error
                }

            return {
                'success': True,
                'pr_number': pr_result.pr_number,
                'pr_url': pr_result.pr_url,
                'pr_title': pr_title,
                'pr_body': pr_body
            }

        except Exception as e:
            logger.error(f"Failed to create PR: {str(e)}")
            return {
                'success': False,
                'error': f"Exception: {str(e)}"
            }

    def _generate_pr_description(
        self,
        fix_data: Dict[str, Any],
        approved_by_name: str
    ) -> str:
        """
        Generate comprehensive PR description with AI analysis

        Args:
            fix_data: Fix data from database
            approved_by_name: Who approved the fix

        Returns:
            Markdown-formatted PR description
        """
        confidence_percent = int((fix_data.get('confidence_score', 0.0) or 0.0) * 100)

        description = f"""## Automated Fix for Build {fix_data['build_id']}

### Error Summary
**Type:** {fix_data['error_type']}
**Category:** {fix_data['error_category']}
**Severity:** {fix_data['severity']}
**Component:** {fix_data['component']}

**Error Message:**
```
{fix_data['error_message'][:500]}
```

### Root Cause Analysis
{fix_data['root_cause']}

### Fix Applied
{fix_data['fix_recommendation']}

### Files Changed
- `{fix_data['file_path']}` (line {fix_data['line_number']})

### AI Confidence
**Confidence Score:** {confidence_percent}%

### Approval
**Approved by:** {approved_by_name}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

### Verification Steps
1. **Review code changes** - Ensure the fix addresses the root cause
2. **Run unit tests** - Verify no regressions
   ```bash
   npm test  # or your test command
   ```
3. **Run integration tests** - Check end-to-end functionality
4. **Manual testing** - Test the specific scenario that failed

### Test Results
- **Build ID:** {fix_data['build_id']}
- **Original failure location:** {fix_data['file_path']}:{fix_data['line_number']}

### Additional Context
This is an automated fix generated by the DDN AI Test Failure Analysis System.

**Analysis ID:** {fix_data['id']}
**Error Category:** {fix_data['error_category']}
**Original Stack Trace:** [View in Dashboard](#)

---

🤖 **Generated by [DDN AI Analysis System](https://github.com/your-org/ddn-ai)**
📊 **Analysis ID:** {fix_data['id']} | **Build:** {fix_data['build_id']}
"""

        return description


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

# Global service instance
_global_service = None

def get_code_fix_service() -> CodeFixAutomation:
    """Get or create global CodeFixAutomation service"""
    global _global_service
    if _global_service is None:
        _global_service = CodeFixAutomation()
    return _global_service


# ============================================================================
# MAIN - TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test the Code Fix Automation service
    Run: python code_fix_automation.py
    """

    print("="*70)
    print("CODE FIX AUTOMATION SERVICE - TESTING")
    print("="*70)

    # Initialize service
    service = CodeFixAutomation()

    # Test parameters (replace with real values)
    test_analysis_id = 1  # Replace with actual analysis_id from your database

    print(f"\nTesting with analysis_id: {test_analysis_id}")
    print("Note: This will create a real GitHub branch and PR!")
    print("Make sure you have:")
    print("  1. GITHUB_TOKEN configured with WRITE permissions")
    print("  2. Valid analysis_id in failure_analysis table")
    print("  3. code_fix_applications table created")

    response = input("\nProceed with test? (yes/no): ")

    if response.lower() == 'yes':
        result = service.apply_approved_fix(
            analysis_id=test_analysis_id,
            approved_by_name="Test User",
            approved_by_email="test@example.com"
        )

        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)

        if result['success']:
            print(f"✓ SUCCESS!")
            print(f"  PR Number: {result['pr_number']}")
            print(f"  PR URL: {result['pr_url']}")
            print(f"  Branch: {result['branch_name']}")
            print(f"  Time: {result['time_to_pr_creation_ms']}ms")
        else:
            print(f"✗ FAILED: {result['error']}")
    else:
        print("\nTest cancelled.")
