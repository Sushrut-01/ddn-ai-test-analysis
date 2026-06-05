"""
Jira Integration Service
Port: Configurable via JIRA_SERVICE_PORT env var (default: 5009)
Purpose: Automatically create Jira tickets for test failures with AI-generated insights
Features:
- Auto-create issues for failures
- Update existing issues with new analysis
- Link to Jenkins builds and GitHub commits
- Track issue resolution status
- Sync feedback back to system
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime

# ============================================================================
# RLS CONTEXT HELPER (Added by add_rls_context_to_existing_services.py)
# ============================================================================

def set_rls_context(cursor, project_id):
    """
    Set PostgreSQL Row-Level Security context for project

    Call this after creating a cursor to enable automatic project filtering.

    Args:
        cursor: PostgreSQL cursor
        project_id: Project ID to set context for

    Example:
        conn = get_db_connection()
        cur = conn.cursor()
        set_rls_context(cur, project_id)  # Enable RLS for this project
        cur.execute("SELECT * FROM failure_analysis")  # Automatically filtered
    """
    if project_id:
        try:
            cursor.execute("SELECT set_project_context(%s)", (project_id,))
        except Exception as e:
            # Graceful fallback if RLS function doesn't exist
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not set RLS context: {e}")

# ============================================================================


app = Flask(__name__)
CORS(app)

# Configuration
JIRA_URL = os.getenv('JIRA_URL', 'https://your-company.atlassian.net')
JIRA_EMAIL = os.getenv('JIRA_EMAIL', 'your-email@company.com')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', 'your-api-token')
JIRA_PROJECT_KEY = os.getenv('JIRA_PROJECT_KEY', 'DDN')
JIRA_SERVICE_PORT = int(os.getenv('JIRA_SERVICE_PORT', 5009))

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

# Jira API headers
JIRA_AUTH = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
JIRA_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)


def get_priority_from_failures(consecutive_failures):
    """Determine Jira priority based on consecutive failures"""
    if consecutive_failures >= 5:
        return 'Highest'
    elif consecutive_failures >= 3:
        return 'High'
    else:
        return 'Medium'


def get_labels_from_category(error_category):
    """Get Jira labels based on error category"""
    labels = ['ai-detected', 'test-failure']

    category_map = {
        'CODE_ERROR': ['code-error', 'requires-dev'],
        'TEST_FAILURE': ['test-failure', 'qa-attention'],
        'INFRA_ERROR': ['infrastructure', 'devops'],
        'DEPENDENCY_ERROR': ['dependencies', 'build-system'],
        'CONFIG_ERROR': ['configuration', 'devops']
    }

    labels.extend(category_map.get(error_category, []))
    return labels


@app.route('/api/jira/create-issue', methods=['POST'])
def create_jira_issue():
    """
    Create a Jira issue for a test failure (MULTI-PROJECT SUPPORT)

    Request body:
    {
        "build_id": "123",
        "project_id": 1,              // REQUIRED for multi-project support
        "job_name": "DDN-Tests",
        "error_category": "CODE_ERROR",
        "error_message": "...",
        "root_cause": "...",
        "fix_recommendation": "...",
        "confidence_score": 0.85,
        "consecutive_failures": 3,
        "build_url": "...",
        "github_commit": "..."
    }
    """
    try:
        data = request.get_json()

        build_id = data.get('build_id')
        project_id = data.get('project_id', 1)  # Default to DDN for backward compatibility
        job_name = data.get('job_name', 'Unknown Job')
        error_category = data.get('error_category', 'UNKNOWN')
        error_message = data.get('error_message', data.get('ai_analysis', 'Test failure'))
        root_cause = data.get('root_cause', data.get('ai_analysis', ''))
        fix_recommendation = data.get('fix_recommendation', '')
        confidence_score = data.get('confidence_score', 0.8)
        consecutive_failures = data.get('consecutive_failures', 1)
        build_url = data.get('build_url', '')
        github_commit = data.get('github_commit', '')

        # Get project-specific Jira configuration from database
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                p.slug,
                p.name,
                pc.jira_project_key,
                pc.jira_url,
                pc.jira_email,
                pc.jira_api_token_encrypted
            FROM projects p
            LEFT JOIN project_configurations pc ON p.id = pc.project_id
            WHERE p.id = %s
        """, (project_id,))

        project_config = cursor.fetchone()

        if not project_config or not project_config['jira_project_key']:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': f'Jira not configured for project_id={project_id}'
            }), 400

        # Use project-specific Jira configuration
        project_jira_key = project_config['jira_project_key']
        project_jira_url = project_config['jira_url'] or JIRA_URL
        project_jira_email = project_config['jira_email'] or JIRA_EMAIL
        # Note: In production, decrypt the jira_api_token_encrypted
        project_jira_token = JIRA_API_TOKEN  # TODO: Decrypt from project_config['jira_api_token_encrypted']

        project_jira_auth = HTTPBasicAuth(project_jira_email, project_jira_token)

        # Check if issue already exists for this build and project
        cursor.execute("""
            SELECT jira_issue_key FROM failure_analysis
            WHERE build_id = %s AND project_id = %s AND jira_issue_key IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1
        """, (build_id, project_id))

        existing = cursor.fetchone()

        if existing:
            jira_key = existing['jira_issue_key']
            update_result = update_jira_issue(jira_key, data, project_jira_auth, project_jira_url)

            cursor.close()
            conn.close()

            return jsonify({
                'status': 'success',
                'action': 'updated',
                'jira_issue_key': jira_key,
                'jira_url': f"{project_jira_url}/browse/{jira_key}",
                'project_id': project_id,
                'project_slug': project_config['slug']
            })

        # Create new Jira issue
        priority = get_priority_from_failures(consecutive_failures)
        labels = get_labels_from_category(error_category)

        description = f"""
h2. AI-Detected Test Failure

*Build ID:* {build_id}
*Job Name:* {job_name}
*Error Category:* {error_category}
*Consecutive Failures:* {consecutive_failures}
*AI Confidence:* {int(confidence_score * 100)}%

h3. Root Cause Analysis

{root_cause}

h3. Recommended Fix

{fix_recommendation}

h3. Links

* [Jenkins Build|{build_url}]
* [Dashboard Analysis|http://localhost:3000/failures/{build_id}]
"""

        if github_commit:
            description += f"* [GitHub Commit|https://github.com/your-org/your-repo/commit/{github_commit}]\n"

        description += f"""
h3. Next Steps

# Review the root cause analysis
# Apply the recommended fix
# Re-run the test suite
# Provide feedback in the dashboard

---
_This issue was automatically created by DDN AI Test Failure Analysis System_
_Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_
"""

        issue_payload = {
            'fields': {
                'project': {
                    'key': project_jira_key  # Use project-specific Jira key (DDN or GURU)
                },
                'summary': f'[{error_category}] {error_message[:80]}{"..." if len(error_message) > 80 else ""}',
                'description': {
                    'type': 'doc',
                    'version': 1,
                    'content': [
                        {
                            'type': 'heading',
                            'attrs': {'level': 2},
                            'content': [{'type': 'text', 'text': 'Test Failure Details'}]
                        },
                        {
                            'type': 'paragraph',
                            'content': [
                                {'type': 'text', 'text': 'Build: ', 'marks': [{'type': 'strong'}]},
                                {'type': 'text', 'text': f'{build_id}\n'},
                                {'type': 'text', 'text': 'Job: ', 'marks': [{'type': 'strong'}]},
                                {'type': 'text', 'text': f'{job_name}\n'},
                                {'type': 'text', 'text': 'Category: ', 'marks': [{'type': 'strong'}]},
                                {'type': 'text', 'text': f'{error_category}\n'},
                                {'type': 'text', 'text': 'Consecutive Failures: ', 'marks': [{'type': 'strong'}]},
                                {'type': 'text', 'text': f'{consecutive_failures}\n'},
                                {'type': 'text', 'text': 'AI Confidence: ', 'marks': [{'type': 'strong'}]},
                                {'type': 'text', 'text': f'{int(confidence_score * 100)}%'}
                            ]
                        },
                        {
                            'type': 'heading',
                            'attrs': {'level': 3},
                            'content': [{'type': 'text', 'text': 'Error Message'}]
                        },
                        {
                            'type': 'codeBlock',
                            'attrs': {'language': 'text'},
                            'content': [{'type': 'text', 'text': error_message or 'No error message available'}]
                        },
                        {
                            'type': 'heading',
                            'attrs': {'level': 3},
                            'content': [{'type': 'text', 'text': 'AI Root Cause Analysis'}]
                        },
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': root_cause or 'Analysis pending'}]
                        },
                        {
                            'type': 'heading',
                            'attrs': {'level': 3},
                            'content': [{'type': 'text', 'text': 'Recommended Fix'}]
                        },
                        {
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': fix_recommendation or 'Review the error details and apply appropriate fix'}]
                        },
                        {
                            'type': 'rule'
                        },
                        {
                            'type': 'paragraph',
                            'content': [
                                {'type': 'text', 'text': 'Generated by DDN AI Test Failure Analysis System', 'marks': [{'type': 'em'}]}
                            ]
                        }
                    ]
                },
                'issuetype': {
                    'name': 'Bug'
                }
            }
        }

        response = requests.post(
            f'{project_jira_url}/rest/api/3/issue',
            headers=JIRA_HEADERS,
            auth=project_jira_auth,  # Use project-specific auth
            data=json.dumps(issue_payload)
        )

        if response.status_code not in [200, 201]:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': f'Failed to create Jira issue: {response.text}'
            }), response.status_code

        jira_response = response.json()
        jira_key = jira_response['key']
        jira_url = f"{project_jira_url}/browse/{jira_key}"  # Use project-specific URL

        # Update failure_analysis with Jira link (project-scoped)
        cursor.execute("""
            UPDATE failure_analysis
            SET jira_issue_key = %s, jira_issue_url = %s
            WHERE build_id = %s AND project_id = %s
        """, (jira_key, jira_url, build_id, project_id))

        # Also save to jira_bugs table for dashboard display (with project_id)
        cursor.execute("""
            INSERT INTO jira_bugs (
                project_id, jira_key, jira_url, summary, description, priority, status,
                build_id, error_category, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (jira_key) DO UPDATE SET
                summary = EXCLUDED.summary,
                description = EXCLUDED.description,
                priority = EXCLUDED.priority
        """, (
            project_id,  # CRITICAL: project_id for data isolation
            jira_key,
            jira_url,
            f'[{error_category}] {error_message[:100]}',
            f'Build: {build_id}\nJob: {job_name}\nCategory: {error_category}\n\nRoot Cause: {root_cause}\n\nRecommendation: {fix_recommendation}',
            'High' if error_category in ['CODE_ERROR', 'CRITICAL'] else 'Medium',
            'Open',
            build_id,
            error_category
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'action': 'created',
            'jira_issue_key': jira_key,
            'jira_url': f"{project_jira_url}/browse/{jira_key}",  # Use project-specific URL
            'project_id': project_id,
            'project_slug': project_config['slug']
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def update_jira_issue(jira_key, data, jira_auth, jira_url):
    """
    Update existing Jira issue with new analysis (multi-project support)

    Args:
        jira_key: The Jira issue key (e.g., DDN-123, GURU-456)
        data: Request data with analysis details
        jira_auth: HTTPBasicAuth object with project-specific credentials
        jira_url: Project-specific Jira base URL
    """
    try:
        comment = f"""
*New AI Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

*Build ID:* {data.get('build_id')}
*Consecutive Failures:* {data.get('consecutive_failures', 1)}
*AI Confidence:* {int(data.get('confidence_score', 0) * 100)}%

h4. Updated Root Cause

{data.get('root_cause')}

h4. Updated Fix Recommendation

{data.get('fix_recommendation')}
"""

        comment_payload = {
            'body': comment
        }

        response = requests.post(
            f'{jira_url}/rest/api/3/issue/{jira_key}/comment',
            headers=JIRA_HEADERS,
            auth=jira_auth,  # Use project-specific auth
            data=json.dumps(comment_payload)
        )

        return response.status_code in [200, 201]

    except Exception as e:
        print(f"Error updating Jira issue: {e}")
        return False


@app.route('/api/jira/update-from-feedback', methods=['POST'])
def update_jira_from_feedback():
    """Update Jira issue when feedback is received"""
    try:
        data = request.get_json()
        build_id = data.get('build_id')
        feedback_type = data.get('feedback_type')
        feedback_text = data.get('feedback_text', '')

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT jira_issue_key FROM failure_analysis
            WHERE build_id = %s AND jira_issue_key IS NOT NULL
            LIMIT 1
        """, (build_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({
                'status': 'error',
                'message': 'No Jira issue found for this build'
            }), 404

        jira_key = result['jira_issue_key']

        if feedback_type == 'success':
            comment = f"*Fix Verified as Successful*\n\n{feedback_text}"
            transition_payload = {'transition': {'id': '31'}}
            requests.post(
                f'{jira_url}/rest/api/3/issue/{jira_key}/transitions',
                headers=JIRA_HEADERS,
                auth=jira_auth,  # Use project-specific auth
                data=json.dumps(transition_payload)
            )
        else:
            comment = f"*Fix Did Not Work*\n\nAdditional investigation needed.\n\n{feedback_text}"

        comment_payload = {'body': comment}

        response = requests.post(
            f'{jira_url}/rest/api/3/issue/{jira_key}/comment',
            headers=JIRA_HEADERS,
            auth=jira_auth,  # Use project-specific auth
            data=json.dumps(comment_payload)
        )

        if response.status_code not in [200, 201]:
            return jsonify({
                'status': 'error',
                'message': f'Failed to update Jira: {response.text}'
            }), response.status_code

        return jsonify({
            'status': 'success',
            'jira_issue_key': jira_key,
            'jira_url': f"{JIRA_URL}/browse/{jira_key}"
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/jira/get-issue/<build_id>', methods=['GET'])
def get_jira_issue(build_id):
    """Get Jira issue details for a build"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT jira_issue_key, jira_issue_url
            FROM failure_analysis
            WHERE build_id = %s AND jira_issue_key IS NOT NULL
            LIMIT 1
        """, (build_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({
                'status': 'error',
                'message': 'No Jira issue found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': dict(result)
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bugs', methods=['GET'])
def get_bugs():
    """
    Get list of Jira bugs created by DDN AI system
    Query parameters: status, priority, assignee, limit, offset
    """
    try:
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        assignee_filter = request.args.get('assignee')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        jql_parts = [f'project = {JIRA_PROJECT_KEY}', 'labels = ai-detected']

        if status_filter:
            jql_parts.append(f'status = "{status_filter}"')
        if priority_filter:
            jql_parts.append(f'priority = "{priority_filter}"')
        if assignee_filter:
            jql_parts.append(f'assignee = "{assignee_filter}"')

        jql = ' AND '.join(jql_parts)
        jql += ' ORDER BY created DESC'

        response = requests.get(
            f'{JIRA_URL}/rest/api/3/search',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH,
            params={
                'jql': jql,
                'maxResults': limit,
                'startAt': offset,
                'fields': 'summary,status,priority,assignee,created,updated,labels,description'
            }
        )

        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'Failed to fetch Jira issues: {response.text}'
            }), response.status_code

        jira_data = response.json()
        issues = []

        for issue in jira_data.get('issues', []):
            fields = issue.get('fields', {})
            issues.append({
                'key': issue.get('key'),
                'summary': fields.get('summary'),
                'status': fields.get('status', {}).get('name'),
                'priority': fields.get('priority', {}).get('name'),
                'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else 'Unassigned',
                'created': fields.get('created'),
                'updated': fields.get('updated'),
                'labels': fields.get('labels', []),
                'url': f"{JIRA_URL}/browse/{issue.get('key')}"
            })

        return jsonify({
            'status': 'success',
            'data': {
                'issues': issues,
                'total': jira_data.get('total', 0),
                'limit': limit,
                'offset': offset
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/bugs/<issue_key>', methods=['GET'])
def get_bug_details(issue_key):
    """
    Get full Jira issue details including comments and attachments
    """
    try:
        response = requests.get(
            f'{JIRA_URL}/rest/api/3/issue/{issue_key}',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH,
            params={
                'expand': 'renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations,customfield_10000'
            }
        )

        if response.status_code != 200:
            return jsonify({
                'status': 'error',
                'message': f'Failed to fetch issue details: {response.text}'
            }), response.status_code

        issue_data = response.json()
        fields = issue_data.get('fields', {})

        comments_response = requests.get(
            f'{JIRA_URL}/rest/api/3/issue/{issue_key}/comment',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH
        )

        comments = []
        if comments_response.status_code == 200:
            comments_data = comments_response.json()
            for comment in comments_data.get('comments', []):
                comments.append({
                    'id': comment.get('id'),
                    'author': comment.get('author', {}).get('displayName'),
                    'body': comment.get('body'),
                    'created': comment.get('created'),
                    'updated': comment.get('updated')
                })

        issue_details = {
            'key': issue_data.get('key'),
            'summary': fields.get('summary'),
            'description': fields.get('description'),
            'status': fields.get('status', {}).get('name'),
            'priority': fields.get('priority', {}).get('name'),
            'assignee': fields.get('assignee', {}).get('displayName') if fields.get('assignee') else 'Unassigned',
            'reporter': fields.get('reporter', {}).get('displayName'),
            'created': fields.get('created'),
            'updated': fields.get('updated'),
            'labels': fields.get('labels', []),
            'url': f"{JIRA_URL}/browse/{issue_key}",
            'comments': comments,
            'attachments': [
                {
                    'filename': att.get('filename'),
                    'size': att.get('size'),
                    'created': att.get('created'),
                    'url': att.get('content')
                }
                for att in fields.get('attachment', [])
            ]
        }

        return jsonify({
            'status': 'success',
            'data': issue_details
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        response = requests.get(
            f'{JIRA_URL}/rest/api/3/myself',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH
        )

        jira_status = 'connected' if response.status_code == 200 else 'disconnected'

        return jsonify({
            'status': 'healthy',
            'service': 'jira-integration',
            'port': JIRA_SERVICE_PORT,
            'jira_status': jira_status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


if __name__ == '__main__':
    print("=" * 60)
    print("Jira Integration Service")
    print("=" * 60)
    print(f"Port: {JIRA_SERVICE_PORT}")
    print(f"Jira URL: {JIRA_URL}")
    print(f"Project Key: {JIRA_PROJECT_KEY}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                         - Health check")
    print("  POST /api/jira/create-issue          - Create Jira issue")
    print("  POST /api/jira/update-from-feedback  - Update from feedback")
    print("  GET  /api/jira/get-issue/<build_id>  - Get issue details")
    print("  GET  /api/bugs                       - List all AI-detected bugs")
    print("  GET  /api/bugs/<issue_key>           - Get bug details with comments")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=JIRA_SERVICE_PORT, debug=True)
