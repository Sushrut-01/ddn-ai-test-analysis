"""
Workflow Executions API - n8n-style execution viewer

Provides endpoints to view and debug workflow executions:
- List all executions
- Get execution details with node data
- Filter and search executions
- Download execution logs

Port: 5016
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from workflow_execution_tracker import get_workflow_tracker
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize tracker
tracker = get_workflow_tracker()

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'service': 'workflow_executions_api',
        'status': 'healthy',
        'port': 5016,
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# EXECUTION LIST ENDPOINTS
# ============================================================================

@app.route('/api/executions', methods=['GET'])
def get_executions():
    """
    Get list of workflow executions (like n8n's executions page)

    Query parameters:
    - limit: Number of executions to return (default: 50, max: 200)
    - workflow: Filter by workflow name
    - status: Filter by status (running, completed, failed)
    - build_id: Filter by build ID
    - from_date: Filter executions after this date (ISO format)
    - to_date: Filter executions before this date (ISO format)

    Returns:
        List of executions with summary data
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 200)
        workflow_name = request.args.get('workflow')
        status = request.args.get('status')
        build_id = request.args.get('build_id')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')

        # Get executions
        executions = tracker.get_recent_executions(
            limit=limit,
            workflow_name=workflow_name
        )

        # Apply additional filters
        if status:
            executions = [e for e in executions if e['status'] == status]

        if build_id:
            executions = [e for e in executions if e['build_id'] == build_id]

        if from_date:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            executions = [
                e for e in executions
                if e['started_at'] and datetime.fromisoformat(e['started_at']) >= from_dt
            ]

        if to_date:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            executions = [
                e for e in executions
                if e['started_at'] and datetime.fromisoformat(e['started_at']) <= to_dt
            ]

        return jsonify({
            'status': 'success',
            'data': {
                'executions': executions,
                'count': len(executions),
                'filters': {
                    'workflow': workflow_name,
                    'status': status,
                    'build_id': build_id,
                    'from_date': from_date,
                    'to_date': to_date
                }
            }
        })

    except Exception as e:
        logger.error(f"Error getting executions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# EXECUTION DETAILS ENDPOINTS
# ============================================================================

@app.route('/api/executions/<execution_id>', methods=['GET'])
def get_execution_details(execution_id: str):
    """
    Get detailed execution data for a specific execution (like clicking on execution in n8n)

    Returns:
    - Execution metadata
    - All node executions with input/output
    - Execution flow visualization data

    Args:
        execution_id: Execution ID

    Returns:
        Complete execution details with node data
    """
    try:
        execution = tracker.get_execution_details(execution_id)

        if not execution:
            return jsonify({
                'status': 'error',
                'message': f'Execution not found: {execution_id}'
            }), 404

        return jsonify({
            'status': 'success',
            'data': execution
        })

    except Exception as e:
        logger.error(f"Error getting execution details: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/executions/<execution_id>/nodes/<int:sequence_number>', methods=['GET'])
def get_node_execution(execution_id: str, sequence_number: int):
    """
    Get detailed data for a specific node execution

    Args:
        execution_id: Execution ID
        sequence_number: Node sequence number

    Returns:
        Node execution details with full input/output
    """
    try:
        execution = tracker.get_execution_details(execution_id)

        if not execution:
            return jsonify({
                'status': 'error',
                'message': f'Execution not found: {execution_id}'
            }), 404

        # Find the node
        node = next(
            (n for n in execution['nodes'] if n['sequence_number'] == sequence_number),
            None
        )

        if not node:
            return jsonify({
                'status': 'error',
                'message': f'Node not found: {sequence_number}'
            }), 404

        return jsonify({
            'status': 'success',
            'data': node
        })

    except Exception as e:
        logger.error(f"Error getting node execution: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# STATISTICS ENDPOINTS
# ============================================================================

@app.route('/api/executions/stats', methods=['GET'])
def get_execution_stats():
    """
    Get execution statistics

    Query parameters:
    - workflow: Filter by workflow name
    - days: Number of days to analyze (default: 7)

    Returns:
        Statistics about executions
    """
    try:
        workflow_name = request.args.get('workflow')
        days = int(request.args.get('days', 7))

        # Get recent executions
        executions = tracker.get_recent_executions(
            limit=1000,
            workflow_name=workflow_name
        )

        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        executions = [
            e for e in executions
            if e['started_at'] and datetime.fromisoformat(e['started_at']) >= cutoff_date
        ]

        # Calculate statistics
        total = len(executions)
        completed = len([e for e in executions if e['status'] == 'completed'])
        failed = len([e for e in executions if e['status'] == 'failed'])
        running = len([e for e in executions if e['status'] == 'running'])

        # Calculate average duration (completed only)
        durations = [e['duration_ms'] for e in executions if e['duration_ms']]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Group by trigger type
        trigger_counts = {}
        for e in executions:
            trigger = e.get('trigger_type', 'unknown')
            trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1

        # Get recent failures
        recent_failures = [
            {
                'execution_id': e['execution_id'],
                'build_id': e['build_id'],
                'error_message': e['error_message'],
                'error_node': e['error_node'],
                'started_at': e['started_at']
            }
            for e in executions
            if e['status'] == 'failed'
        ][:10]  # Last 10 failures

        return jsonify({
            'status': 'success',
            'data': {
                'period': {
                    'days': days,
                    'from_date': cutoff_date.isoformat(),
                    'to_date': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_executions': total,
                    'completed': completed,
                    'failed': failed,
                    'running': running,
                    'success_rate': round((completed / total * 100) if total > 0 else 0, 2),
                    'failure_rate': round((failed / total * 100) if total > 0 else 0, 2),
                    'avg_duration_ms': round(avg_duration),
                    'avg_duration_sec': round(avg_duration / 1000, 2)
                },
                'by_trigger': trigger_counts,
                'recent_failures': recent_failures
            }
        })

    except Exception as e:
        logger.error(f"Error getting execution stats: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# SEARCH AND FILTER ENDPOINTS
# ============================================================================

@app.route('/api/executions/search', methods=['POST'])
def search_executions():
    """
    Advanced search for executions

    Request body:
    {
        "workflow_name": "react_agent",
        "status": ["completed", "failed"],
        "build_id": "BUILD-123",
        "error_contains": "timeout",
        "date_range": {
            "from": "2025-01-01T00:00:00Z",
            "to": "2025-12-31T23:59:59Z"
        },
        "limit": 100
    }

    Returns:
        Matching executions
    """
    try:
        search_params = request.get_json()

        # Get base executions
        limit = search_params.get('limit', 100)
        workflow = search_params.get('workflow_name')

        executions = tracker.get_recent_executions(
            limit=limit,
            workflow_name=workflow
        )

        # Apply filters
        if 'status' in search_params:
            statuses = search_params['status']
            if not isinstance(statuses, list):
                statuses = [statuses]
            executions = [e for e in executions if e['status'] in statuses]

        if 'build_id' in search_params:
            executions = [e for e in executions if e['build_id'] == search_params['build_id']]

        if 'error_contains' in search_params:
            search_term = search_params['error_contains'].lower()
            executions = [
                e for e in executions
                if e['error_message'] and search_term in e['error_message'].lower()
            ]

        if 'date_range' in search_params:
            date_range = search_params['date_range']
            if 'from' in date_range:
                from_dt = datetime.fromisoformat(date_range['from'].replace('Z', '+00:00'))
                executions = [
                    e for e in executions
                    if e['started_at'] and datetime.fromisoformat(e['started_at']) >= from_dt
                ]
            if 'to' in date_range:
                to_dt = datetime.fromisoformat(date_range['to'].replace('Z', '+00:00'))
                executions = [
                    e for e in executions
                    if e['started_at'] and datetime.fromisoformat(e['started_at']) <= to_dt
                ]

        return jsonify({
            'status': 'success',
            'data': {
                'executions': executions,
                'count': len(executions),
                'search_params': search_params
            }
        })

    except Exception as e:
        logger.error(f"Error searching executions: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("="*70)
    print("🔍 WORKFLOW EXECUTIONS API - Starting")
    print("="*70)
    print(f"📍 Port: 5016")
    print(f"🔗 Health: http://localhost:5016/health")
    print(f"📋 Executions: http://localhost:5016/api/executions")
    print(f"📊 Stats: http://localhost:5016/api/executions/stats")
    print("="*70)

    app.run(
        host='0.0.0.0',
        port=5016,
        debug=True
    )
