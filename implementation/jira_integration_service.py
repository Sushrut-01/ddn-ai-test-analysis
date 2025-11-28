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
    Create a Jira issue for a test failure
    """
    try:
        data = request.get_json()

        build_id = data.get('build_id')
        job_name = data.get('job_name', 'Unknown Job')
        error_category = data.get('error_category')
        root_cause = data.get('root_cause')
        fix_recommendation = data.get('fix_recommendation')
        confidence_score = data.get('confidence_score', 0)
        consecutive_failures = data.get('consecutive_failures', 1)
        build_url = data.get('build_url', '')
        github_commit = data.get('github_commit', '')

        # Check if issue already exists
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT jira_issue_key FROM failure_analysis
            WHERE build_id = %s AND jira_issue_key IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1
        """, (build_id,))

        existing = cursor.fetchone()

        if existing:
            jira_key = existing['jira_issue_key']
            update_result = update_jira_issue(jira_key, data)

            cursor.close()
            conn.close()

            return jsonify({
                'status': 'success',
                'action': 'updated',
                'jira_issue_key': jira_key,
                'jira_url': f"{JIRA_URL}/browse/{jira_key}"
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
                    'key': JIRA_PROJECT_KEY
                },
                'summary': f'Test Failure: {job_name} - {error_category}',
                'description': description,
                'issuetype': {
                    'name': 'Bug'
                },
                'priority': {
                    'name': priority
                },
                'labels': labels,
                'customfield_10000': build_id
            }
        }

        response = requests.post(
            f'{JIRA_URL}/rest/api/3/issue',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH,
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

        cursor.execute("""
            UPDATE failure_analysis
            SET jira_issue_key = %s, jira_issue_url = %s
            WHERE build_id = %s
        """, (jira_key, f"{JIRA_URL}/browse/{jira_key}", build_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'action': 'created',
            'jira_issue_key': jira_key,
            'jira_url': f"{JIRA_URL}/browse/{jira_key}"
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


def update_jira_issue(jira_key, data):
    """Update existing Jira issue with new analysis"""
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
            f'{JIRA_URL}/rest/api/3/issue/{jira_key}/comment',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH,
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
                f'{JIRA_URL}/rest/api/3/issue/{jira_key}/transitions',
                headers=JIRA_HEADERS,
                auth=JIRA_AUTH,
                data=json.dumps(transition_payload)
            )
        else:
            comment = f"*Fix Did Not Work*\n\nAdditional investigation needed.\n\n{feedback_text}"

        comment_payload = {'body': comment}

        response = requests.post(
            f'{JIRA_URL}/rest/api/3/issue/{jira_key}/comment',
            headers=JIRA_HEADERS,
            auth=JIRA_AUTH,
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
    print("  GET  /health                       - Health check")
    print("  POST /api/jira/create-issue        - Create Jira issue")
    print("  POST /api/jira/update-from-feedback - Update from feedback")
    print("  GET  /api/jira/get-issue/<build_id> - Get issue details")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=JIRA_SERVICE_PORT, debug=True)
