"""
Centralized Audit Logging Utility
Provides async audit logging for all services
"""

import json
from typing import Optional, Dict, Any


def log_audit(
    action: str,
    resource_type: str,
    resource_id: str,
    user_email: str = 'system',
    details: Optional[Dict[str, Any]] = None,
    status: str = 'success',
    ip_address: Optional[str] = None
) -> None:
    """
    Log an audit event asynchronously using Celery.

    Args:
        action: Action performed (create, update, delete, view, approve, reject, etc.)
        resource_type: Type of resource (failure, analysis, config, user, etc.)
        resource_id: ID of the resource
        user_email: Email of user performing action (default: 'system')
        details: Additional details as dictionary
        status: Status of action (success, failed, pending)
        ip_address: IP address of the requester

    Example:
        log_audit(
            action='update',
            resource_type='config',
            resource_id='ai.confidence_threshold',
            user_email='admin@example.com',
            details={'old_value': '0.7', 'new_value': '0.8'},
            status='success'
        )
    """
    try:
        # Import Celery task here to avoid circular imports
        from tasks.celery_tasks import log_audit_async

        # Convert details to JSON string if provided
        details_json = json.dumps(details) if details else None

        # Queue the audit log task asynchronously
        log_audit_async.delay(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_email=user_email,
            details=details_json,
            status=status,
            ip_address=ip_address
        )
    except Exception as e:
        # Fallback to synchronous logging if Celery is not available
        print(f"[WARNING] Async audit logging failed, using fallback: {str(e)}")
        try:
            _log_audit_sync(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_email=user_email,
                details=details,
                status=status,
                ip_address=ip_address
            )
        except Exception as sync_error:
            print(f"[ERROR] Audit logging failed: {str(sync_error)}")


def _log_audit_sync(
    action: str,
    resource_type: str,
    resource_id: str,
    user_email: str = 'system',
    details: Optional[Dict[str, Any]] = None,
    status: str = 'success',
    ip_address: Optional[str] = None
) -> None:
    """
    Fallback synchronous audit logging (direct database write).
    Used when Celery is not available.
    """
    import psycopg2
    import os

    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB', 'ddn_ai_analysis'),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'password')
        )

        cursor = conn.cursor()

        details_json = json.dumps(details) if details else None

        cursor.execute("""
            INSERT INTO audit_log
            (timestamp, user_email, action, resource_type, resource_id, details, status, ip_address)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s)
        """, (user_email, action, resource_type, resource_id, details_json, status, ip_address))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"[ERROR] Synchronous audit logging failed: {str(e)}")


def log_audit_batch(audit_entries: list) -> None:
    """
    Log multiple audit events at once.

    Args:
        audit_entries: List of dictionaries with audit log fields

    Example:
        log_audit_batch([
            {
                'action': 'approve',
                'resource_type': 'failure',
                'resource_id': '123',
                'user_email': 'admin@example.com'
            },
            {
                'action': 'approve',
                'resource_type': 'failure',
                'resource_id': '124',
                'user_email': 'admin@example.com'
            }
        ])
    """
    try:
        from tasks.celery_tasks import log_audit_batch_async

        # Process entries to convert details to JSON
        processed_entries = []
        for entry in audit_entries:
            processed = entry.copy()
            if 'details' in processed and isinstance(processed['details'], dict):
                processed['details'] = json.dumps(processed['details'])
            processed_entries.append(processed)

        # Queue the batch audit log task
        log_audit_batch_async.delay(processed_entries)

    except Exception as e:
        print(f"[WARNING] Async batch audit logging failed: {str(e)}")
        # Fallback: log each entry individually
        for entry in audit_entries:
            log_audit(**entry)


# Convenience functions for common audit actions

def log_create(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log resource creation"""
    log_audit('create', resource_type, resource_id, user_email, details)


def log_update(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log resource update"""
    log_audit('update', resource_type, resource_id, user_email, details)


def log_delete(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log resource deletion"""
    log_audit('delete', resource_type, resource_id, user_email, details)


def log_view(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log resource view/access"""
    log_audit('view', resource_type, resource_id, user_email, details)


def log_approve(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log approval action"""
    log_audit('approve', resource_type, resource_id, user_email, details)


def log_reject(resource_type: str, resource_id: str, user_email: str = 'system', details: Optional[Dict] = None):
    """Log rejection action"""
    log_audit('reject', resource_type, resource_id, user_email, details)


def log_login(user_email: str, ip_address: Optional[str] = None, status: str = 'success'):
    """Log user login"""
    log_audit('login', 'user', user_email, user_email, status=status, ip_address=ip_address)


def log_logout(user_email: str, ip_address: Optional[str] = None):
    """Log user logout"""
    log_audit('logout', 'user', user_email, user_email, ip_address=ip_address)


def log_config_change(config_key: str, old_value: str, new_value: str, user_email: str = 'system'):
    """Log configuration change"""
    log_audit(
        'update',
        'config',
        config_key,
        user_email,
        details={'old_value': old_value, 'new_value': new_value}
    )
