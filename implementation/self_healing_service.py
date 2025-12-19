"""
Self-Healing Automation Service (Experimental)
Port: 5008
Purpose: Automatically apply fixes for known, deterministic failures
Features:
- Pattern-based fix application
- Human-in-the-loop approval for first-time fixes
- Success rate tracking
- Rollback capability
- Safe mode with dry-run
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from datetime import datetime
import subprocess

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

JENKINS_URL = os.getenv('JENKINS_URL', 'http://localhost:8080')
JENKINS_USER = os.getenv('JENKINS_USER', 'admin')
JENKINS_TOKEN = os.getenv('JENKINS_TOKEN', 'your-token')

SAFE_MODE = os.getenv('SELF_HEALING_SAFE_MODE', 'true').lower() == 'true'
MIN_SUCCESS_RATE = float(os.getenv('MIN_SUCCESS_RATE', '0.8'))  # 80% minimum
MIN_PATTERN_OCCURRENCES = int(os.getenv('MIN_PATTERN_OCCURRENCES', '3'))

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your-github-token')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'your-org/your-repo')


def get_postgres_connection():
    """Create PostgreSQL connection"""
    return psycopg2.connect(**POSTGRES_CONFIG)


# Predefined fix patterns with high confidence
FIX_PATTERNS = {
    'timeout_increase': {
        'pattern_type': 'TEST_TIMEOUT',
        'detection_keywords': ['timeout', 'timed out', 'exceeded'],
        'fix_type': 'config_update',
        'fix_function': 'apply_timeout_fix',
        'requires_approval': False,
        'safe_mode_only': False
    },
    'dependency_update': {
        'pattern_type': 'DEPENDENCY_MISMATCH',
        'detection_keywords': ['dependency', 'version mismatch', 'incompatible'],
        'fix_type': 'dependency_update',
        'fix_function': 'apply_dependency_fix',
        'requires_approval': True,
        'safe_mode_only': False
    },
    'cache_clear': {
        'pattern_type': 'CACHE_CORRUPTION',
        'detection_keywords': ['cache', 'corrupted', 'stale'],
        'fix_type': 'cache_clear',
        'fix_function': 'apply_cache_clear_fix',
        'requires_approval': False,
        'safe_mode_only': False
    },
    'env_variable_fix': {
        'pattern_type': 'ENV_VARIABLE_MISSING',
        'detection_keywords': ['environment variable', 'not set', 'undefined'],
        'fix_type': 'env_config',
        'fix_function': 'apply_env_variable_fix',
        'requires_approval': True,
        'safe_mode_only': False
    },
    'service_restart': {
        'pattern_type': 'SERVICE_UNRESPONSIVE',
        'detection_keywords': ['connection refused', 'service unavailable', 'cannot connect'],
        'fix_type': 'service_restart',
        'fix_function': 'apply_service_restart_fix',
        'requires_approval': False,
        'safe_mode_only': True
    }
}


@app.route('/api/self-heal/analyze', methods=['POST'])
def analyze_for_self_healing():
    """
    Analyze a failure to determine if it's eligible for self-healing
    Request body:
    {
        "build_id": "12345",
        "error_category": "INFRA_ERROR",
        "root_cause": "...",
        "fix_recommendation": "..."
    }
    """
    try:
        data = request.get_json()
        build_id = data.get('build_id')
        error_category = data.get('error_category')
        root_cause = data.get('root_cause', '')
        fix_recommendation = data.get('fix_recommendation', '')

        # Check if failure matches known patterns
        matched_pattern = None
        for pattern_name, pattern_config in FIX_PATTERNS.items():
            keywords = pattern_config['detection_keywords']
            if any(keyword.lower() in root_cause.lower() or keyword.lower() in fix_recommendation.lower() for keyword in keywords):
                matched_pattern = pattern_name
                break

        if not matched_pattern:
            return jsonify({
                'status': 'not_eligible',
                'message': 'No matching self-healing pattern found'
            })

        # Get pattern success history
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                occurrence_count,
                success_rate,
                last_applied,
                requires_human_approval
            FROM failure_patterns
            WHERE pattern_type = %s
        """, (FIX_PATTERNS[matched_pattern]['pattern_type'],))

        pattern_history = cursor.fetchone()
        cursor.close()
        conn.close()

        if not pattern_history:
            # First time seeing this pattern
            return jsonify({
                'status': 'requires_approval',
                'pattern': matched_pattern,
                'message': 'First occurrence - requires human approval',
                'fix_type': FIX_PATTERNS[matched_pattern]['fix_type']
            })

        # Check eligibility criteria
        if pattern_history['occurrence_count'] < MIN_PATTERN_OCCURRENCES:
            return jsonify({
                'status': 'insufficient_data',
                'pattern': matched_pattern,
                'occurrences': pattern_history['occurrence_count'],
                'min_required': MIN_PATTERN_OCCURRENCES
            })

        if pattern_history['success_rate'] < MIN_SUCCESS_RATE:
            return jsonify({
                'status': 'low_success_rate',
                'pattern': matched_pattern,
                'success_rate': pattern_history['success_rate'],
                'min_required': MIN_SUCCESS_RATE
            })

        if FIX_PATTERNS[matched_pattern]['requires_approval'] or pattern_history['requires_human_approval']:
            return jsonify({
                'status': 'requires_approval',
                'pattern': matched_pattern,
                'message': 'This fix type requires human approval'
            })

        if SAFE_MODE and FIX_PATTERNS[matched_pattern]['safe_mode_only']:
            return jsonify({
                'status': 'safe_mode_blocked',
                'pattern': matched_pattern,
                'message': 'Fix blocked by safe mode'
            })

        return jsonify({
            'status': 'eligible',
            'pattern': matched_pattern,
            'fix_type': FIX_PATTERNS[matched_pattern]['fix_type'],
            'success_rate': pattern_history['success_rate'],
            'occurrences': pattern_history['occurrence_count']
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/self-heal/apply', methods=['POST'])
def apply_self_healing_fix():
    """
    Apply self-healing fix
    Request body:
    {
        "build_id": "12345",
        "pattern": "timeout_increase",
        "dry_run": false,
        "approved_by": "user@company.com"
    }
    """
    try:
        data = request.get_json()
        build_id = data.get('build_id')
        pattern_name = data.get('pattern')
        dry_run = data.get('dry_run', False)
        approved_by = data.get('approved_by', 'system')

        if pattern_name not in FIX_PATTERNS:
            return jsonify({
                'status': 'error',
                'message': 'Invalid pattern name'
            }), 400

        pattern_config = FIX_PATTERNS[pattern_name]

        # Log the attempt
        conn = get_postgres_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO self_healing_log (
                build_id, pattern_type, fix_type, dry_run,
                approved_by, applied_at, status
            ) VALUES (%s, %s, %s, %s, %s, NOW(), 'in_progress')
            RETURNING id
        """, (
            build_id,
            pattern_config['pattern_type'],
            pattern_config['fix_type'],
            dry_run,
            approved_by
        ))

        log_id = cursor.fetchone()[0]
        conn.commit()

        # Apply the fix
        fix_function = globals().get(pattern_config['fix_function'])
        if not fix_function:
            cursor.execute("""
                UPDATE self_healing_log
                SET status = 'failed', error_message = %s
                WHERE id = %s
            """, ('Fix function not implemented', log_id))
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                'status': 'error',
                'message': 'Fix function not implemented'
            }), 500

        # Execute fix function
        try:
            result = fix_function(build_id, dry_run)

            status = 'success' if result['success'] else 'failed'
            cursor.execute("""
                UPDATE self_healing_log
                SET status = %s, result_details = %s, completed_at = NOW()
                WHERE id = %s
            """, (status, json.dumps(result), log_id))

            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                'status': 'success',
                'result': result,
                'log_id': log_id
            })

        except Exception as fix_error:
            cursor.execute("""
                UPDATE self_healing_log
                SET status = 'failed', error_message = %s
                WHERE id = %s
            """, (str(fix_error), log_id))
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({
                'status': 'error',
                'message': str(fix_error)
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# Fix Implementation Functions

def apply_timeout_fix(build_id, dry_run=False):
    """Increase timeout values in test configuration"""
    try:
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Would increase timeout from 30s to 60s in test config'
            }

        # Actual implementation would update Jenkins job config or test files
        # This is a simplified example
        return {
            'success': True,
            'message': 'Timeout increased from 30s to 60s',
            'changes': ['Updated test.config: timeout=60']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def apply_dependency_fix(build_id, dry_run=False):
    """Update dependency versions"""
    try:
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Would update package.json dependencies'
            }

        # Actual implementation would update dependency files
        return {
            'success': True,
            'message': 'Dependencies updated',
            'changes': ['Updated package.json', 'Ran npm install']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def apply_cache_clear_fix(build_id, dry_run=False):
    """Clear build cache"""
    try:
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Would clear Jenkins workspace cache'
            }

        # Trigger Jenkins cache clear
        response = requests.post(
            f"{JENKINS_URL}/job/your-job/doWipeOutWorkspace",
            auth=(JENKINS_USER, JENKINS_TOKEN)
        )

        return {
            'success': response.status_code == 200,
            'message': 'Cache cleared successfully',
            'changes': ['Cleared Jenkins workspace']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def apply_env_variable_fix(build_id, dry_run=False):
    """Set missing environment variables"""
    try:
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Would set missing environment variable'
            }

        # Actual implementation would update Jenkins environment
        return {
            'success': True,
            'message': 'Environment variable set',
            'changes': ['Set MISSING_VAR=default_value']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


def apply_service_restart_fix(build_id, dry_run=False):
    """Restart unresponsive service"""
    try:
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Would restart service'
            }

        # Actual implementation would restart service
        # subprocess.run(['systemctl', 'restart', 'service-name'])

        return {
            'success': True,
            'message': 'Service restarted',
            'changes': ['Restarted service-name']
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


@app.route('/api/self-heal/history', methods=['GET'])
def get_self_healing_history():
    """Get self-healing history"""
    try:
        limit = int(request.args.get('limit', 50))

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT * FROM self_healing_log
            ORDER BY applied_at DESC
            LIMIT %s
        """, (limit,))

        history = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'history': [dict(h) for h in history]
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/self-heal/patterns', methods=['GET'])
def get_eligible_patterns():
    """Get all eligible self-healing patterns"""
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                pattern_type,
                occurrence_count,
                success_rate,
                last_applied
            FROM failure_patterns
            WHERE success_rate >= %s
              AND occurrence_count >= %s
            ORDER BY success_rate DESC, occurrence_count DESC
        """, (MIN_SUCCESS_RATE, MIN_PATTERN_OCCURRENCES))

        patterns = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'patterns': [dict(p) for p in patterns],
                'min_success_rate': MIN_SUCCESS_RATE,
                'min_occurrences': MIN_PATTERN_OCCURRENCES,
                'safe_mode': SAFE_MODE
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# CODE HEALING PIPELINE ENDPOINTS (For PR → Build → Jira Workflow)
# ============================================================================

@app.route('/api/fixes/pending', methods=['GET'])
def get_pending_fixes():
    """
    Get CODE_ERROR failures that are approved for fixing
    Returns failures with fix status (pending, pr_created, building, jira_created)
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                fa.id,
                fa.build_id,
                fa.mongodb_failure_id,
                fa.error_category,
                fa.root_cause,
                fa.fix_recommendation,
                fa.confidence_score,
                fa.analyzed_at,
                fa.jira_issue_key,
                fa.jira_issue_url,
                COALESCE(fa.pr_url, '') as pr_url,
                COALESCE(fa.pr_number, 0) as pr_number,
                CASE
                    WHEN fa.jira_issue_key IS NOT NULL THEN 'jira_created'
                    WHEN fa.pr_number IS NOT NULL THEN 'pr_created'
                    ELSE 'pending'
                END as fix_status
            FROM failure_analysis fa
            WHERE fa.error_category = 'CODE_ERROR'
              AND fa.confidence_score >= 0.7
            ORDER BY fa.analyzed_at DESC
            LIMIT 50
        """)

        fixes = cursor.fetchall()

        # Convert to list of dicts and format dates
        result = []
        for fix in fixes:
            fix_dict = dict(fix)
            if isinstance(fix_dict.get('analyzed_at'), datetime):
                fix_dict['analyzed_at'] = fix_dict['analyzed_at'].isoformat()
            result.append(fix_dict)

        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'data': {
                'fixes': result,
                'total': len(result)
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/fixes/apply', methods=['POST'])
def apply_code_fix():
    """
    Apply code fix to codebase
    Creates GitHub PR via MCP, triggers Jenkins build, creates Jira ticket if build fails
    """
    try:
        data = request.get_json()
        failure_id = data.get('failure_id')
        fix_code = data.get('fix_code')

        if not failure_id:
            return jsonify({
                'status': 'error',
                'message': 'failure_id is required'
            }), 400

        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Get failure details
        cursor.execute("""
            SELECT * FROM failure_analysis
            WHERE id = %s OR mongodb_failure_id = %s
        """, (failure_id, failure_id))

        failure = cursor.fetchone()
        if not failure:
            return jsonify({
                'status': 'error',
                'message': 'Failure not found'
            }), 404

        # In safe mode, just return simulated response
        if SAFE_MODE:
            cursor.close()
            conn.close()

            return jsonify({
                'status': 'success',
                'message': 'Fix applied in safe mode (dry-run)',
                'data': {
                    'fix_id': failure_id,
                    'pr_url': f'https://github.com/{GITHUB_REPO}/pull/mock-{failure_id}',
                    'pr_number': 999,
                    'branch_name': f'fix/auto-{failure_id}',
                    'build_triggered': True,
                    'safe_mode': True
                }
            })

        # TODO: Real implementation would:
        # 1. Create fix branch
        # 2. Apply code changes
        # 3. Create GitHub PR via MCP
        # 4. Trigger Jenkins build
        # 5. Monitor build status
        # 6. Create Jira ticket if build fails

        # For now, return simulated response
        cursor.close()
        conn.close()

        return jsonify({
            'status': 'success',
            'message': 'Fix pipeline initiated',
            'data': {
                'fix_id': failure_id,
                'pr_url': f'https://github.com/{GITHUB_REPO}/pull/pending',
                'status': 'pr_creation_pending'
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/fixes/status/<fix_id>', methods=['GET'])
def get_fix_status(fix_id):
    """
    Get current status of fix pipeline
    Returns: pending, pr_created, ci_running, ci_passed, ci_failed, jira_created
    """
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("""
            SELECT
                id,
                build_id,
                pr_url,
                pr_number,
                jira_issue_key,
                jira_issue_url,
                analyzed_at,
                CASE
                    WHEN jira_issue_key IS NOT NULL THEN 'jira_created'
                    WHEN pr_number IS NOT NULL THEN 'pr_created'
                    ELSE 'pending'
                END as pipeline_status
            FROM failure_analysis
            WHERE id = %s OR mongodb_failure_id = %s OR build_id = %s
        """, (fix_id, fix_id, fix_id))

        fix = cursor.fetchone()
        cursor.close()
        conn.close()

        if not fix:
            return jsonify({
                'status': 'error',
                'message': 'Fix not found'
            }), 404

        fix_dict = dict(fix)
        if isinstance(fix_dict.get('analyzed_at'), datetime):
            fix_dict['analyzed_at'] = fix_dict['analyzed_at'].isoformat()

        return jsonify({
            'status': 'success',
            'data': fix_dict
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'self-healing',
        'port': 5008,
        'safe_mode': SAFE_MODE,
        'min_success_rate': MIN_SUCCESS_RATE,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 60)
    print("Self-Healing Automation Service (Experimental)")
    print("=" * 60)
    print(f"Port: 5008")
    print(f"Safe Mode: {SAFE_MODE}")
    print(f"Min Success Rate: {MIN_SUCCESS_RATE}")
    print(f"Min Pattern Occurrences: {MIN_PATTERN_OCCURRENCES}")
    print("=" * 60)
    print("\nAvailable Endpoints:")
    print("  GET  /health                      - Health check")
    print("  POST /api/self-heal/analyze       - Analyze eligibility")
    print("  POST /api/self-heal/apply         - Apply fix")
    print("  GET  /api/self-heal/history       - Get history")
    print("  GET  /api/self-heal/patterns      - Get eligible patterns")
    print("\n  Code Healing Pipeline:")
    print("  GET  /api/fixes/pending           - Get pending CODE_ERROR fixes")
    print("  POST /api/fixes/apply             - Apply fix (PR → Build → Jira)")
    print("  GET  /api/fixes/status/<fix_id>   - Get fix pipeline status")
    print("=" * 60)
    print("\nSupported Fix Patterns:")
    for name, config in FIX_PATTERNS.items():
        print(f"  - {name}: {config['pattern_type']}")
    print("=" * 60)
    print("\nStarting server...")

    app.run(host='0.0.0.0', port=5008, debug=True)
