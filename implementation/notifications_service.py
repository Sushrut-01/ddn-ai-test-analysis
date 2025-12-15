"""
Notifications Service
Port: 5014
Purpose: Email and in-app notifications
Features:
- In-app notifications for users
- Email notifications via SMTP
- Notification queue with retry logic
- Notification preferences per user
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': os.getenv('POSTGRES_PORT', 5432),
    'database': os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'password')
}

# SMTP Configuration
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'from_address': os.getenv('SMTP_FROM_ADDRESS', 'DDN AI <noreply@ddn-ai.com>'),
    'use_tls': os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
}

# Team notification emails
TEAM_EMAILS = ['sushrut.nistane@rysun.com', 'amit.manjesh@rysun.com']

def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)


def send_email(to_email, subject, body_text, body_html=None):
    """Send email via SMTP"""
    try:
        if not SMTP_CONFIG['username'] or not SMTP_CONFIG['password']:
            print(f"[WARNING] SMTP not configured. Email not sent to {to_email}")
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_CONFIG['from_address']
        msg['To'] = to_email

        # Add text and HTML parts
        part1 = MIMEText(body_text, 'plain')
        msg.attach(part1)

        if body_html:
            part2 = MIMEText(body_html, 'html')
            msg.attach(part2)

        # Connect and send
        server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
        if SMTP_CONFIG['use_tls']:
            server.starttls()

        server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
        server.send_message(msg)
        server.quit()

        print(f"[OK] Email sent to {to_email}: {subject}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {str(e)}")
        return False


# ============================================================================
# IN-APP NOTIFICATIONS
# ============================================================================

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get user notifications"""
    try:
        user_email = request.args.get('user_email')
        is_read = request.args.get('is_read')
        category = request.args.get('category')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        if not user_email:
            return jsonify({
                'status': 'error',
                'message': 'user_email parameter is required'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Build query
        conditions = ["user_email = %s", "is_archived = false"]
        params = [user_email]

        if is_read is not None:
            conditions.append("is_read = %s")
            params.append(is_read.lower() == 'true')

        if category:
            conditions.append("category = %s")
            params.append(category)

        where_clause = " AND ".join(conditions)
        params.extend([limit, offset])

        cursor.execute(f"""
            SELECT *
            FROM notifications
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params)

        notifications = cursor.fetchall()

        # Get total count
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM notifications
            WHERE {where_clause}
        """, params[:-2])  # Exclude limit and offset

        total = cursor.fetchone()['count']

        cursor.close()
        conn.close()

        # Format notifications
        notifications_data = []
        for notif in notifications:
            notif_dict = dict(notif)
            if isinstance(notif_dict.get('created_at'), datetime):
                notif_dict['created_at'] = notif_dict['created_at'].isoformat()
            if isinstance(notif_dict.get('read_at'), datetime):
                notif_dict['read_at'] = notif_dict['read_at'].isoformat()
            notifications_data.append(notif_dict)

        return jsonify({
            'status': 'success',
            'data': {
                'notifications': notifications_data,
                'total': total,
                'unread_count': sum(1 for n in notifications_data if not n['is_read'])
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/notifications/mark-read', methods=['POST'])
def mark_notifications_read():
    """Mark one or multiple notifications as read"""
    try:
        data = request.get_json()
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return jsonify({
                'status': 'error',
                'message': 'notification_ids is required'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = true, read_at = NOW()
            WHERE id = ANY(%s)
        """, (notification_ids,))

        updated_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': f'{updated_count} notification(s) marked as read'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all user notifications as read"""
    try:
        data = request.get_json()
        user_email = data.get('user_email')

        if not user_email:
            return jsonify({
                'status': 'error',
                'message': 'user_email is required'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_read = true, read_at = NOW()
            WHERE user_email = %s AND is_read = false
        """, (user_email,))

        updated_count = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': f'{updated_count} notification(s) marked as read'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def archive_notification(notification_id):
    """Archive (soft delete) a notification"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE notifications
            SET is_archived = true
            WHERE id = %s
        """, (notification_id,))

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                'status': 'error',
                'message': 'Notification not found'
            }), 404

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Notification archived'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/notifications/send', methods=['POST'])
def create_notification():
    """Create a new notification (internal use)"""
    try:
        data = request.get_json()

        required_fields = ['user_email', 'title', 'message', 'type', 'category']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO notifications (
                user_email, title, message, type, category,
                related_resource_type, related_resource_id, action_url, created_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id, user_email, title, message, type, category, created_at
        """, (
            data['user_email'],
            data['title'],
            data['message'],
            data['type'],
            data['category'],
            data.get('related_resource_type'),
            data.get('related_resource_id'),
            data.get('action_url')
        ))

        notification = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()

        notif_data = dict(notification)
        if isinstance(notif_data.get('created_at'), datetime):
            notif_data['created_at'] = notif_data['created_at'].isoformat()

        return jsonify({
            'status': 'success',
            'data': {'notification': notif_data}
        }), 201

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# EMAIL NOTIFICATIONS
# ============================================================================

@app.route('/api/email/send', methods=['POST'])
def send_email_notification():
    """Send email notification"""
    try:
        data = request.get_json()

        required_fields = ['to_email', 'subject', 'body_text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400

        to_email = data['to_email']
        subject = data['subject']
        body_text = data['body_text']
        body_html = data.get('body_html')

        # Add to email queue
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            INSERT INTO email_queue (to_email, subject, body_text, body_html, status, created_at)
            VALUES (%s, %s, %s, %s, 'pending', NOW())
            RETURNING id
        """, (to_email, subject, body_text, body_html))

        email_id = cursor.fetchone()['id']
        conn.commit()

        # Try to send immediately
        success = send_email(to_email, subject, body_text, body_html)

        # Update status
        cursor.execute("""
            UPDATE email_queue
            SET status = %s, sent_at = %s, attempts = attempts + 1
            WHERE id = %s
        """, ('sent' if success else 'failed', datetime.now() if success else None, email_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'email_id': email_id,
                'sent': success
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/email/send-team', methods=['POST'])
def send_team_notification():
    """Send email to all team members"""
    try:
        data = request.get_json()

        required_fields = ['subject', 'body_text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} is required'
                }), 400

        subject = data['subject']
        body_text = data['body_text']
        body_html = data.get('body_html')

        results = []
        for email in TEAM_EMAILS:
            success = send_email(email, subject, body_text, body_html)
            results.append({
                'email': email,
                'sent': success
            })

        return jsonify({
            'status': 'success',
            'data': {
                'results': results,
                'total_sent': sum(1 for r in results if r['sent'])
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/email/status/<int:email_id>', methods=['GET'])
def get_email_status(email_id):
    """Get email delivery status"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT id, to_email, subject, status, attempts, created_at, sent_at, last_error
            FROM email_queue
            WHERE id = %s
        """, (email_id,))

        email = cursor.fetchone()
        cursor.close()
        conn.close()

        if not email:
            return jsonify({
                'status': 'error',
                'message': 'Email not found'
            }), 404

        email_data = dict(email)
        if isinstance(email_data.get('created_at'), datetime):
            email_data['created_at'] = email_data['created_at'].isoformat()
        if isinstance(email_data.get('sent_at'), datetime):
            email_data['sent_at'] = email_data['sent_at'].isoformat()

        return jsonify({
            'status': 'success',
            'data': {'email': email_data}
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/email/retry-failed', methods=['POST'])
def retry_failed_emails():
    """Retry sending failed emails"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get failed emails (max 3 attempts)
        cursor.execute("""
            SELECT id, to_email, subject, body_text, body_html
            FROM email_queue
            WHERE status = 'failed' AND attempts < 3
            ORDER BY created_at DESC
            LIMIT 10
        """)

        failed_emails = cursor.fetchall()

        retry_results = []
        for email in failed_emails:
            success = send_email(
                email['to_email'],
                email['subject'],
                email['body_text'],
                email['body_html']
            )

            cursor.execute("""
                UPDATE email_queue
                SET status = %s, sent_at = %s, attempts = attempts + 1
                WHERE id = %s
            """, ('sent' if success else 'failed', datetime.now() if success else None, email['id']))

            retry_results.append({
                'email_id': email['id'],
                'to_email': email['to_email'],
                'success': success
            })

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'retried': len(retry_results),
                'successful': sum(1 for r in retry_results if r['success']),
                'results': retry_results
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    smtp_configured = bool(SMTP_CONFIG['username'] and SMTP_CONFIG['password'])

    return jsonify({
        'status': 'healthy',
        'service': 'notifications',
        'port': 5014,
        'smtp_configured': smtp_configured,
        'team_emails': TEAM_EMAILS,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Notifications Service")
    print("=" * 60)
    print(f"Port: 5014")
    print(f"SMTP Host: {SMTP_CONFIG['host']}:{SMTP_CONFIG['port']}")
    print(f"SMTP Configured: {bool(SMTP_CONFIG['username'])}")
    print("=" * 60)
    print("\nTeam Notification Emails:")
    for email in TEAM_EMAILS:
        print(f"  - {email}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                          - Health check")
    print("\n  In-App Notifications:")
    print("  GET  /api/notifications               - Get user notifications")
    print("  POST /api/notifications/mark-read     - Mark as read")
    print("  POST /api/notifications/mark-all-read - Mark all as read")
    print("  DELETE /api/notifications/<id>        - Archive notification")
    print("  POST /api/notifications/send          - Create notification")
    print("\n  Email Notifications:")
    print("  POST /api/email/send                  - Send email")
    print("  POST /api/email/send-team             - Send to all team members")
    print("  GET  /api/email/status/<id>           - Get email status")
    print("  POST /api/email/retry-failed          - Retry failed emails")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=5014, debug=True)
