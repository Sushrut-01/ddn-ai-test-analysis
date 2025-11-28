"""
Slack Integration Service
Port: Configurable via SLACK_SERVICE_PORT env var (default: 5012)
Purpose: Send test failure notifications to Slack channels with AI-generated insights
Features:
- Send rich messages with failure details
- Interactive buttons for feedback
- Thread updates for status changes
- Channel routing based on severity
- Slash command support
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN', 'xoxb-your-token')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET', 'your-signing-secret')
SLACK_DEFAULT_CHANNEL = os.getenv('SLACK_DEFAULT_CHANNEL', '#test-failures')
SLACK_SERVICE_PORT = int(os.getenv('SLACK_SERVICE_PORT', 5012))

POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:3000')

# Slack API headers
SLACK_HEADERS = {
    'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
    'Content-Type': 'application/json'
}


def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)


def get_channel_by_category(error_category, consecutive_failures):
    """Route to appropriate Slack channel based on category and severity"""
    if consecutive_failures >= 5:
        return '#critical-failures'

    channel_map = {
        'CODE_ERROR': '#dev-failures',
        'TEST_FAILURE': '#qa-failures',
        'INFRA_ERROR': '#devops-alerts',
        'DEPENDENCY_ERROR': '#build-alerts',
        'CONFIG_ERROR': '#config-alerts'
    }

    return channel_map.get(error_category, SLACK_DEFAULT_CHANNEL)


def get_color_by_confidence(confidence_score):
    """Get color code based on confidence score"""
    if confidence_score >= 0.8:
        return '#4caf50'
    elif confidence_score >= 0.6:
        return '#ff9800'
    else:
        return '#f44336'


@app.route('/api/slack/send-notification', methods=['POST'])
def send_slack_notification():
    """Send test failure notification to Slack"""
    try:
        data = request.get_json()

        build_id = data.get('build_id')
        job_name = data.get('job_name', 'Unknown Job')
        error_category = data.get('error_category')
        root_cause = data.get('root_cause', 'N/A')
        fix_recommendation = data.get('fix_recommendation', 'N/A')
        confidence_score = data.get('confidence_score', 0)
        consecutive_failures = data.get('consecutive_failures', 1)
        build_url = data.get('build_url', '')

        channel = get_channel_by_category(error_category, consecutive_failures)
        color = get_color_by_confidence(confidence_score)

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Test Failure Detected: {job_name}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Build ID:*\n`{build_id}`"},
                    {"type": "mrkdwn", "text": f"*Category:*\n{error_category}"},
                    {"type": "mrkdwn", "text": f"*Consecutive Failures:*\n{consecutive_failures}"},
                    {"type": "mrkdwn", "text": f"*AI Confidence:*\n{int(confidence_score * 100)}%"}
                ]
            },
            {"type": "divider"},
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Root Cause:*\n{root_cause[:500]}{'...' if len(root_cause) > 500 else ''}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recommended Fix:*\n{fix_recommendation[:500]}{'...' if len(fix_recommendation) > 500 else ''}"
                }
            },
            {"type": "divider"},
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Fix Worked", "emoji": True},
                        "style": "primary",
                        "value": json.dumps({"build_id": build_id, "feedback": "success"}),
                        "action_id": "feedback_success"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Fix Failed", "emoji": True},
                        "style": "danger",
                        "value": json.dumps({"build_id": build_id, "feedback": "failed"}),
                        "action_id": "feedback_failed"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Dashboard", "emoji": True},
                        "url": f"{DASHBOARD_URL}/failures/{build_id}",
                        "action_id": "view_dashboard"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Jenkins Build", "emoji": True},
                        "url": build_url,
                        "action_id": "view_jenkins"
                    }
                ]
            }
        ]

        payload = {
            'channel': channel,
            'blocks': blocks,
            'text': f'Test Failure: {job_name} - {error_category}'
        }

        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers=SLACK_HEADERS,
            data=json.dumps(payload)
        )

        slack_response = response.json()

        if not slack_response.get('ok'):
            return jsonify({
                'status': 'error',
                'message': f"Slack API error: {slack_response.get('error')}"
            }), 500

        message_ts = slack_response.get('ts')

        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE failure_analysis
            SET slack_message_ts = %s, slack_channel = %s
            WHERE build_id = %s
        """, (message_ts, channel, build_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'channel': channel,
            'message_ts': message_ts
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/slack/interactions', methods=['POST'])
def handle_slack_interactions():
    """Handle Slack interactive components (button clicks)"""
    try:
        payload = json.loads(request.form.get('payload'))
        action = payload['actions'][0]
        action_id = action['action_id']
        user_id = payload['user']['id']
        user_name = payload['user']['name']

        if action_id in ['feedback_success', 'feedback_failed']:
            value = json.loads(action['value'])
            build_id = value['build_id']
            feedback_type = 'success' if action_id == 'feedback_success' else 'failed'

            conn = get_postgres_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO user_feedback (analysis_id, feedback_type, user_id, created_at)
                SELECT id, %s, %s, NOW()
                FROM failure_analysis
                WHERE build_id = %s
                LIMIT 1
            """, (feedback_type, f"slack:{user_name}", build_id))

            conn.commit()
            cursor.close()
            conn.close()

            channel = payload['channel']['id']
            thread_ts = payload['message']['ts']

            reply_text = f"<@{user_id}> marked this fix as *successful*!" if feedback_type == 'success' else f"<@{user_id}> reported the fix *did not work*. Additional investigation needed."

            requests.post(
                'https://slack.com/api/chat.postMessage',
                headers=SLACK_HEADERS,
                data=json.dumps({
                    'channel': channel,
                    'thread_ts': thread_ts,
                    'text': reply_text
                })
            )

            return jsonify({'status': 'success'})

        return jsonify({'status': 'ignored'})

    except Exception as e:
        print(f"Error handling interaction: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/slack/update-thread', methods=['POST'])
def update_slack_thread():
    """Post update to Slack thread"""
    try:
        data = request.get_json()
        build_id = data.get('build_id')
        message = data.get('message')

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT slack_message_ts, slack_channel
            FROM failure_analysis
            WHERE build_id = %s AND slack_message_ts IS NOT NULL
            LIMIT 1
        """, (build_id,))

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            return jsonify({
                'status': 'error',
                'message': 'No Slack message found for this build'
            }), 404

        payload = {
            'channel': result['slack_channel'],
            'thread_ts': result['slack_message_ts'],
            'text': message
        }

        response = requests.post(
            'https://slack.com/api/chat.postMessage',
            headers=SLACK_HEADERS,
            data=json.dumps(payload)
        )

        if not response.json().get('ok'):
            return jsonify({
                'status': 'error',
                'message': 'Failed to post thread reply'
            }), 500

        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/slack/slash-command', methods=['POST'])
def handle_slash_command():
    """Handle Slack slash commands"""
    try:
        command_text = request.form.get('text', '').strip()
        user_id = request.form.get('user_id')
        user_name = request.form.get('user_name')

        if command_text == 'status':
            conn = get_postgres_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute("""
                SELECT
                    COUNT(*) as total_failures,
                    COUNT(CASE WHEN feedback_result = 'success' THEN 1 END) as successful_fixes,
                    AVG(confidence_score) as avg_confidence
                FROM failure_analysis
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """)

            stats = cursor.fetchone()
            cursor.close()
            conn.close()

            response_text = f"""*DDN AI System Status (Last 7 days)*
Total Failures: {stats['total_failures']}
Successful Fixes: {stats['successful_fixes']}
Success Rate: {int(stats['successful_fixes'] / stats['total_failures'] * 100) if stats['total_failures'] > 0 else 0}%
Avg Confidence: {int(stats['avg_confidence'] * 100) if stats['avg_confidence'] else 0}%
"""

            return jsonify({
                'response_type': 'ephemeral',
                'text': response_text
            })

        elif command_text.startswith('trigger '):
            build_id = command_text.split(' ')[1]

            trigger_response = requests.post(
                'http://manual-trigger-api:5004/api/trigger-analysis',
                json={
                    'build_id': build_id,
                    'triggered_by_user': f'slack:{user_name}',
                    'trigger_source': 'slack_slash_command',
                    'reason': 'Manual trigger via Slack slash command'
                }
            )

            if trigger_response.status_code == 200:
                response_text = f"AI analysis triggered for build `{build_id}`. Results will be posted here shortly."
            else:
                response_text = f"Failed to trigger analysis for build `{build_id}`. Please check the build ID and try again."

            return jsonify({
                'response_type': 'ephemeral',
                'text': response_text
            })

        else:
            return jsonify({
                'response_type': 'ephemeral',
                'text': """*DDN AI Slash Commands:*
`/ddn-ai status` - Get system status
`/ddn-ai trigger <build_id>` - Manually trigger AI analysis
"""
            })

    except Exception as e:
        return jsonify({
            'response_type': 'ephemeral',
            'text': f'Error: {str(e)}'
        })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        response = requests.post(
            'https://slack.com/api/auth.test',
            headers=SLACK_HEADERS
        )

        slack_status = 'connected' if response.json().get('ok') else 'disconnected'

        return jsonify({
            'status': 'healthy',
            'service': 'slack-integration',
            'port': SLACK_SERVICE_PORT,
            'slack_status': slack_status,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


if __name__ == '__main__':
    print("=" * 60)
    print("Slack Integration Service")
    print("=" * 60)
    print(f"Port: {SLACK_SERVICE_PORT}")
    print(f"Default Channel: {SLACK_DEFAULT_CHANNEL}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                      - Health check")
    print("  POST /api/slack/send-notification - Send notification")
    print("  POST /api/slack/interactions      - Handle button clicks")
    print("  POST /api/slack/update-thread     - Update message thread")
    print("  POST /api/slack/slash-command     - Handle slash commands")
    print("=" * 60)
    print("\nSlash Commands:")
    print("  /ddn-ai status              - Get system status")
    print("  /ddn-ai trigger <build_id>  - Manually trigger analysis")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=SLACK_SERVICE_PORT, debug=True)
