"""
Celery Tasks for DDN AI Analysis System
Async task queue for handling test failure analysis

PHASE 7: Task Queue System
- Handles concurrent analysis requests
- Prevents webhook timeouts
- Provides task status tracking
- Supports retry mechanisms
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any
from celery import Celery, Task
from celery.exceptions import SoftTimeLimitExceeded
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# CELERY CONFIGURATION
# ============================================================================

# Redis broker URL
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', REDIS_URL)

# Create Celery app
app = Celery(
    'ddn_ai_tasks',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

# Celery configuration
app.conf.update(
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,  # Acknowledge after task completes
    worker_prefetch_multiplier=1,  # Get one task at a time
    task_track_started=True,  # Track when task starts

    # Retry settings
    task_default_retry_delay=10,  # Retry after 10 seconds
    task_max_retries=3,  # Maximum 3 retries

    # Time limits (in seconds)
    task_soft_time_limit=180,  # 3 minutes soft limit
    task_time_limit=240,  # 4 minutes hard limit

    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    result_backend_transport_options={'master_name': 'mymaster'},

    # Worker settings
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=False,

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True
)

logger.info(f"✓ Celery app configured")
logger.info(f"  - Broker: {CELERY_BROKER_URL}")
logger.info(f"  - Backend: {CELERY_RESULT_BACKEND}")

# ============================================================================
# CUSTOM TASK BASE CLASS
# ============================================================================

class CallbackTask(Task):
    """
    Custom task with callbacks for success/failure

    Features:
    - Success callback
    - Failure callback
    - Retry with exponential backoff
    - Progress tracking
    """

    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        logger.info(f"✓ Task {task_id} succeeded")
        return super().on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        logger.error(f"✗ Task {task_id} failed: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when task is retried"""
        logger.warning(f"↻ Task {task_id} retry: {exc}")
        return super().on_retry(exc, task_id, args, kwargs, einfo)


# ============================================================================
# TASK: ANALYZE TEST FAILURE
# ============================================================================

@app.task(
    base=CallbackTask,
    bind=True,
    name='tasks.analyze_test_failure',
    max_retries=3,
    default_retry_delay=10
)
def analyze_test_failure(
    self,
    failure_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze test failure using AI system (async)

    Args:
        failure_data: Dict with test failure information
            - suite_name: Test suite name
            - test_name: Test case name
            - error_message: Error message
            - error_type: Error type/exception
            - stack_trace: Full stack trace
            - build_number: Build ID
            - timestamp: Failure timestamp

    Returns:
        Dict with analysis results:
            - task_id: Celery task ID
            - status: 'SUCCESS' or 'FAILURE'
            - analysis: AI analysis results
            - execution_time_ms: Processing time
            - timestamp: Completion timestamp
    """
    task_id = self.request.id
    start_time = datetime.now()

    logger.info(f"[Task {task_id}] Starting analysis for build {failure_data.get('build_number', 'unknown')}")

    try:
        # Import AI service functions (inside task to avoid circular imports)
        from ai_analysis_service import analyze_with_react_agent, format_react_result_with_gemini, verify_react_result_with_crag

        # Update task state to PROCESSING
        self.update_state(
            state='PROCESSING',
            meta={
                'current': 0,
                'total': 3,
                'status': 'Running ReAct agent analysis...'
            }
        )

        # Step 1: ReAct Agent Analysis
        logger.info(f"[Task {task_id}] Step 1/3: ReAct agent analysis")
        react_result = analyze_with_react_agent(failure_data)

        self.update_state(
            state='PROCESSING',
            meta={
                'current': 1,
                'total': 3,
                'status': 'Verifying with CRAG...'
            }
        )

        # Step 2: CRAG Verification
        logger.info(f"[Task {task_id}] Step 2/3: CRAG verification")
        verified_result = verify_react_result_with_crag(react_result, failure_data)

        self.update_state(
            state='PROCESSING',
            meta={
                'current': 2,
                'total': 3,
                'status': 'Formatting with Gemini...'
            }
        )

        # Step 3: Gemini Formatting
        logger.info(f"[Task {task_id}] Step 3/3: Gemini formatting")
        final_result = format_react_result_with_gemini(verified_result, failure_data)

        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds() * 1000

        # Prepare result
        result = {
            'task_id': task_id,
            'status': 'SUCCESS',
            'analysis': final_result,
            'execution_time_ms': execution_time,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"[Task {task_id}] ✓ Analysis complete in {execution_time:.0f}ms")
        return result

    except SoftTimeLimitExceeded:
        # Soft time limit exceeded - try to save partial results
        logger.error(f"[Task {task_id}] ⏱ Soft time limit exceeded")

        return {
            'task_id': task_id,
            'status': 'TIMEOUT',
            'error': 'Analysis exceeded time limit',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as exc:
        # Log error
        logger.error(f"[Task {task_id}] ✗ Analysis failed: {exc}")

        # Retry if retries left
        if self.request.retries < self.max_retries:
            logger.info(f"[Task {task_id}] ↻ Retrying ({self.request.retries + 1}/{self.max_retries})")

            # Exponential backoff
            retry_delay = 10 * (2 ** self.request.retries)

            raise self.retry(exc=exc, countdown=retry_delay)

        # Max retries reached - return error
        return {
            'task_id': task_id,
            'status': 'FAILURE',
            'error': str(exc),
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# TASK: BATCH ANALYZE FAILURES
# ============================================================================

@app.task(
    name='tasks.batch_analyze_failures',
    bind=True
)
def batch_analyze_failures(
    self,
    failure_list: list[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze multiple test failures in batch

    Args:
        failure_list: List of failure_data dicts

    Returns:
        Dict with batch results:
            - total: Total number of failures
            - queued: Number of tasks queued
            - task_ids: List of Celery task IDs
    """
    task_id = self.request.id
    logger.info(f"[Batch {task_id}] Queuing {len(failure_list)} analyses")

    task_ids = []

    for i, failure_data in enumerate(failure_list, 1):
        # Queue individual analysis task
        result = analyze_test_failure.delay(failure_data)
        task_ids.append(result.id)

        logger.info(f"[Batch {task_id}] Queued {i}/{len(failure_list)}: {result.id}")

    return {
        'batch_id': task_id,
        'total': len(failure_list),
        'queued': len(task_ids),
        'task_ids': task_ids,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# TASK: GET TASK STATUS
# ============================================================================

def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of Celery task

    Args:
        task_id: Celery task ID

    Returns:
        Dict with task status:
            - task_id: Task ID
            - state: Task state (PENDING/PROCESSING/SUCCESS/FAILURE)
            - info: Task info/result
    """
    task = app.AsyncResult(task_id)

    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'info': 'Task is queued'
        }
    elif task.state == 'PROCESSING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'info': task.info
        }
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': task.state,
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'state': task.state,
            'error': str(task.info)
        }
    else:
        response = {
            'task_id': task_id,
            'state': task.state,
            'info': str(task.info)
        }

    return response


# ============================================================================
# TASK: CLEANUP OLD RESULTS
# ============================================================================

@app.task(name='tasks.cleanup_old_results')
def cleanup_old_results(hours: int = 24):
    """
    Clean up old task results from Redis

    Args:
        hours: Delete results older than this many hours
    """
    logger.info(f"Cleaning up results older than {hours} hours")

    # This would be implemented with Redis commands
    # For now, results auto-expire after result_expires config

    return {
        'status': 'completed',
        'hours': hours,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# TASK: ASYNC AUDIT LOGGING
# ============================================================================

@app.task(name='tasks.log_audit_async')
def log_audit_async(
    action: str,
    resource_type: str,
    resource_id: str,
    user_email: str = 'system',
    details: str = None,
    status: str = 'success',
    ip_address: str = None
) -> Dict[str, Any]:
    """
    Asynchronous audit logging task

    Args:
        action: Action performed (create, update, delete, etc.)
        resource_type: Type of resource (failure, analysis, config, etc.)
        resource_id: ID of the resource
        user_email: User performing the action
        details: JSON string with additional details
        status: Status of the action
        ip_address: IP address of the request

    Returns:
        Dict with logging result
    """
    try:
        import psycopg2
        import json

        # Database connection
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )

        cursor = conn.cursor()

        # Insert audit log entry
        cursor.execute("""
            INSERT INTO audit_log
            (timestamp, user_email, action, resource_type, resource_id, details, status, ip_address)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
        """, (user_email, action, resource_type, resource_id, details, status, ip_address))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✓ Audit log: {user_email} {action} {resource_type}/{resource_id}")

        return {
            'status': 'success',
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"✗ Audit log failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


@app.task(name='tasks.log_audit_batch_async')
def log_audit_batch_async(audit_entries: list) -> Dict[str, Any]:
    """
    Batch asynchronous audit logging task

    Args:
        audit_entries: List of audit log entry dicts
            Each entry should have: action, resource_type, resource_id, user_email, etc.

    Returns:
        Dict with batch logging result
    """
    try:
        import psycopg2

        # Database connection
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )

        cursor = conn.cursor()

        # Batch insert audit log entries
        for entry in audit_entries:
            cursor.execute("""
                INSERT INTO audit_log
                (timestamp, user_email, action, resource_type, resource_id, details, status, ip_address)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
            """, (
                entry.get('user_email', 'system'),
                entry.get('action'),
                entry.get('resource_type'),
                entry.get('resource_id'),
                entry.get('details'),
                entry.get('status', 'success'),
                entry.get('ip_address')
            ))

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"✓ Batch audit log: {len(audit_entries)} entries")

        return {
            'status': 'success',
            'entries_logged': len(audit_entries),
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"✗ Batch audit log failed: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# TEST HARNESS
# ============================================================================

def main():
    """Test harness for Celery tasks"""
    print("=" * 80)
    print("Celery Tasks - Test Harness")
    print("=" * 80)

    print(f"\n✓ Celery app configured")
    print(f"  Broker: {CELERY_BROKER_URL}")
    print(f"  Backend: {CELERY_RESULT_BACKEND}")

    print(f"\n📋 Available tasks:")
    for task_name in app.tasks.keys():
        if not task_name.startswith('celery'):
            print(f"  - {task_name}")

    print(f"\n⚠️  To start workers, run:")
    print(f"  celery -A tasks.celery_tasks worker --loglevel=info --concurrency=4 --pool=solo")

    print(f"\n⚠️  To monitor with Flower, run:")
    print(f"  celery -A tasks.celery_tasks flower --port=5555")

    print(f"\n✅ Celery tasks module ready!")


if __name__ == '__main__':
    main()
