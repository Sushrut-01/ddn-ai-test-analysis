"""
HITL (Human-in-the-Loop) Manager for CRAG Verification (Task 0-ARCH.16)

Implements queue management for medium-confidence answers requiring human review.

Features:
1. PostgreSQL-based queue (hitl_queue table)
2. Priority-based queueing (high/medium/low)
3. SLA tracking (target: <2 hours)
4. Notification integration (Teams/Slack stubs)
5. Review workflow (pending → in_review → approved/rejected)

Author: AI Analysis System
Date: 2025-11-02
"""

import logging
import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

# Notification service configuration
SLACK_SERVICE_URL = os.getenv('SLACK_SERVICE_URL', 'http://localhost:5012')
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL', '')
SLACK_NOTIFICATIONS_ENABLED = os.getenv('SLACK_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'
TEAMS_NOTIFICATIONS_ENABLED = os.getenv('TEAMS_NOTIFICATIONS_ENABLED', 'false').lower() == 'true'
DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:5173')

# PostgreSQL connection
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor, Json
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logger.warning("psycopg2 not available - HITL queue will be in-memory only")


class HITLPriority(Enum):
    """Priority levels for HITL queue"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class HITLStatus(Enum):
    """Status values for HITL queue items"""
    PENDING = "pending"           # Awaiting human review
    IN_REVIEW = "in_review"       # Currently being reviewed
    APPROVED = "approved"         # Human approved the answer
    REJECTED = "rejected"         # Human rejected, needs correction
    CORRECTED = "corrected"       # Corrected after rejection


class HITLManager:
    """
    Human-in-the-Loop queue manager for CRAG verification

    Manages review queue for medium-confidence answers (0.65-0.85).
    Stores items in PostgreSQL for persistence and collaboration.
    """

    # SLA targets
    SLA_TARGET_HOURS = 2  # Target: review within 2 hours

    # SQL schema for hitl_queue table
    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS hitl_queue (
        id SERIAL PRIMARY KEY,
        failure_id VARCHAR(255) NOT NULL,
        build_id VARCHAR(255),
        error_category VARCHAR(50),
        error_message TEXT,

        -- Original ReAct result
        react_result JSONB NOT NULL,

        -- CRAG confidence scores
        confidence FLOAT NOT NULL,
        confidence_scores JSONB NOT NULL,
        concerns JSONB,

        -- Queue metadata
        priority VARCHAR(10) NOT NULL,  -- high, medium, low
        status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending, in_review, approved, rejected, corrected

        -- Timestamps
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        assigned_at TIMESTAMP,
        reviewed_at TIMESTAMP,

        -- Review data
        reviewer VARCHAR(255),
        review_notes TEXT,
        corrected_answer JSONB,
        feedback_rating INT,  -- 1-5 stars

        -- SLA tracking
        sla_deadline TIMESTAMP,
        sla_met BOOLEAN,

        -- Notification tracking
        notification_sent BOOLEAN DEFAULT FALSE,
        notification_sent_at TIMESTAMP,

        -- Indexes
        CONSTRAINT unique_failure_id UNIQUE(failure_id)
    );

    CREATE INDEX IF NOT EXISTS idx_hitl_status ON hitl_queue(status);
    CREATE INDEX IF NOT EXISTS idx_hitl_priority ON hitl_queue(priority, created_at);
    CREATE INDEX IF NOT EXISTS idx_hitl_sla ON hitl_queue(sla_deadline) WHERE status = 'pending';
    """

    def __init__(self):
        """Initialize HITL manager with PostgreSQL connection"""
        self.postgres_conn = None
        self.in_memory_queue: List[Dict] = []  # Fallback if PostgreSQL unavailable

        # Statistics
        self.total_queued = 0
        self.total_approved = 0
        self.total_rejected = 0

        # Initialize PostgreSQL connection
        if PSYCOPG2_AVAILABLE:
            self._initialize_postgres()
        else:
            logger.warning("[HITL] Running in memory-only mode (no PostgreSQL)")

    def _initialize_postgres(self):
        """Initialize PostgreSQL connection and create table if needed"""
        try:
            self.postgres_conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432"),
                database=os.getenv("POSTGRES_DATABASE", "ddn_ai"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD")
            )

            # Create table if it doesn't exist
            with self.postgres_conn.cursor() as cursor:
                cursor.execute(self.CREATE_TABLE_SQL)
                self.postgres_conn.commit()

            logger.info("[HITL] ✓ PostgreSQL connected, hitl_queue table ready")

        except Exception as e:
            logger.error(f"[HITL] ✗ PostgreSQL connection failed: {e}")
            logger.warning("[HITL] Falling back to in-memory queue")
            self.postgres_conn = None

    def queue(self, react_result: Dict, confidence: float, confidence_scores: Dict,
             failure_data: Dict, priority: str = "medium") -> Dict[str, Any]:
        """
        Add item to HITL queue for human review

        Args:
            react_result: ReAct agent result
            confidence: Overall confidence score
            confidence_scores: Component confidence scores
            failure_data: Original failure context
            priority: Queue priority (high/medium/low)

        Returns:
            dict: Queue item with ID and metadata
        """
        self.total_queued += 1

        # Calculate SLA deadline
        sla_deadline = datetime.now() + timedelta(hours=self.SLA_TARGET_HOURS)

        # Identify concerns (low-scoring components)
        concerns = self._identify_concerns(confidence_scores['components'])

        # Create queue item
        queue_item = {
            'failure_id': failure_data.get('build_id', f"unknown-{self.total_queued}"),
            'build_id': failure_data.get('build_id'),
            'error_category': react_result.get('error_category', 'UNKNOWN'),
            'error_message': failure_data.get('error_message', ''),
            'react_result': react_result,
            'confidence': confidence,
            'confidence_scores': confidence_scores,
            'concerns': concerns,
            'priority': priority,
            'status': HITLStatus.PENDING.value,
            'created_at': datetime.now().isoformat(),
            'sla_deadline': sla_deadline.isoformat(),
            'notification_sent': False
        }

        # Store in PostgreSQL or in-memory
        if self.postgres_conn:
            queue_item = self._queue_to_postgres(queue_item)
        else:
            queue_item['id'] = len(self.in_memory_queue) + 1
            self.in_memory_queue.append(queue_item)

        logger.info(f"[HITL] Queued failure {queue_item['failure_id']} "
                   f"(confidence={confidence:.3f}, priority={priority})")

        # Send notification
        self._send_notification(queue_item)

        return queue_item

    def _queue_to_postgres(self, item: Dict) -> Dict:
        """Store queue item in PostgreSQL"""
        try:
            with self.postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    INSERT INTO hitl_queue (
                        failure_id, build_id, error_category, error_message,
                        react_result, confidence, confidence_scores, concerns,
                        priority, status, sla_deadline
                    ) VALUES (
                        %(failure_id)s, %(build_id)s, %(error_category)s, %(error_message)s,
                        %(react_result)s, %(confidence)s, %(confidence_scores)s, %(concerns)s,
                        %(priority)s, %(status)s, %(sla_deadline)s
                    )
                    ON CONFLICT (failure_id) DO UPDATE SET
                        confidence = EXCLUDED.confidence,
                        confidence_scores = EXCLUDED.confidence_scores,
                        concerns = EXCLUDED.concerns,
                        priority = EXCLUDED.priority
                    RETURNING id, created_at
                """, {
                    **item,
                    'react_result': Json(item['react_result']),
                    'confidence_scores': Json(item['confidence_scores']),
                    'concerns': Json(item['concerns'])
                })

                result = cursor.fetchone()
                self.postgres_conn.commit()

                item['id'] = result['id']
                item['created_at'] = result['created_at'].isoformat()

                logger.debug(f"[HITL] Stored in PostgreSQL (id={item['id']})")

        except Exception as e:
            logger.error(f"[HITL] Failed to store in PostgreSQL: {e}")
            self.postgres_conn.rollback()
            # Fallback to in-memory
            item['id'] = len(self.in_memory_queue) + 1
            self.in_memory_queue.append(item)

        return item

    def _identify_concerns(self, components: Dict[str, float]) -> List[str]:
        """Identify low-scoring confidence components as concerns"""
        CONCERN_THRESHOLD = 0.70
        concerns = []

        for component, score in components.items():
            if score < CONCERN_THRESHOLD:
                concerns.append(f"{component}={score:.2f} (below {CONCERN_THRESHOLD})")

        return concerns

    def _send_notification(self, item: Dict):
        """
        Send notification about new HITL item via Slack and/or Teams

        Integrates with:
        - Slack Integration Service (via REST API)
        - Microsoft Teams webhook (direct)
        """
        # Check if already notified
        if item.get('notification_sent'):
            return

        notification_sent = False
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }

        # Send Slack notification via integration service
        if SLACK_NOTIFICATIONS_ENABLED:
            try:
                slack_payload = {
                    'build_id': item['failure_id'],
                    'job_name': f"HITL Review Required - {item['error_category']}",
                    'error_category': 'HITL_REVIEW',
                    'root_cause': (
                        f"A medium-confidence analysis requires human review.\n\n"
                        f"Confidence: {item['confidence']:.2%}\n"
                        f"Priority: {item['priority'].upper()}\n"
                        f"Concerns: {', '.join(item['concerns']) if item['concerns'] else 'None'}\n"
                        f"SLA Deadline: {item['sla_deadline']}"
                    ),
                    'fix_recommendation': (
                        f"Please review the AI analysis and either approve or provide corrections.\n"
                        f"Review URL: {DASHBOARD_URL}/review/{item['failure_id']}"
                    ),
                    'confidence_score': item['confidence'],
                    'consecutive_failures': 1 if item['priority'] == 'low' else (3 if item['priority'] == 'medium' else 5),
                    'build_url': f"{DASHBOARD_URL}/review/{item['failure_id']}"
                }

                response = requests.post(
                    f'{SLACK_SERVICE_URL}/api/slack/send-notification',
                    json=slack_payload,
                    timeout=10
                )

                if response.status_code == 200:
                    logger.info(f"[HITL] Slack notification sent for {item['failure_id']}")
                    notification_sent = True
                else:
                    logger.warning(f"[HITL] Slack notification failed: {response.status_code}")

            except requests.exceptions.ConnectionError:
                logger.warning("[HITL] Could not connect to Slack service")
            except Exception as e:
                logger.warning(f"[HITL] Slack notification error: {e}")

        # Send Teams notification via webhook
        if TEAMS_NOTIFICATIONS_ENABLED and TEAMS_WEBHOOK_URL:
            try:
                teams_message = {
                    "@type": "MessageCard",
                    "@context": "http://schema.org/extensions",
                    "themeColor": "FF0000" if item['priority'] == 'high' else ("FFA500" if item['priority'] == 'medium' else "00FF00"),
                    "summary": f"HITL Review Required - {item['failure_id']}",
                    "sections": [{
                        "activityTitle": f"{priority_emoji.get(item['priority'], '⚪')} New HITL Review Request",
                        "facts": [
                            {"name": "Failure ID", "value": item['failure_id']},
                            {"name": "Category", "value": item['error_category']},
                            {"name": "Confidence", "value": f"{item['confidence']:.2%}"},
                            {"name": "Priority", "value": item['priority'].upper()},
                            {"name": "Concerns", "value": ', '.join(item['concerns']) if item['concerns'] else 'None'},
                            {"name": "SLA Deadline", "value": item['sla_deadline']}
                        ],
                        "markdown": True
                    }],
                    "potentialAction": [{
                        "@type": "OpenUri",
                        "name": "Review Now",
                        "targets": [{"os": "default", "uri": f"{DASHBOARD_URL}/review/{item['failure_id']}"}]
                    }]
                }

                response = requests.post(TEAMS_WEBHOOK_URL, json=teams_message, timeout=10)

                if response.status_code in [200, 202]:
                    logger.info(f"[HITL] Teams notification sent for {item['failure_id']}")
                    notification_sent = True
                else:
                    logger.warning(f"[HITL] Teams notification failed: {response.status_code}")

            except requests.exceptions.ConnectionError:
                logger.warning("[HITL] Could not connect to Teams webhook")
            except Exception as e:
                logger.warning(f"[HITL] Teams notification error: {e}")

        if not notification_sent:
            # Log message for debugging when no notifications are configured
            message = (
                f"{priority_emoji.get(item['priority'], '⚪')} **New HITL Review Request**\n"
                f"Failure ID: {item['failure_id']}\n"
                f"Category: {item['error_category']}\n"
                f"Confidence: {item['confidence']:.2%}\n"
                f"Priority: {item['priority'].upper()}\n"
                f"SLA Deadline: {item['sla_deadline']}"
            )
            logger.info(f"[HITL] Notification (no service configured): {message.replace(chr(10), ' | ')}")

        # Mark as notified
        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE hitl_queue
                        SET notification_sent = TRUE, notification_sent_at = NOW()
                        WHERE failure_id = %s
                    """, (item['failure_id'],))
                    self.postgres_conn.commit()
            except Exception as e:
                logger.error(f"[HITL] Failed to update notification status: {e}")

    def get_pending_items(self, limit: int = 100, priority: Optional[str] = None) -> List[Dict]:
        """
        Get pending HITL items, ordered by priority and age

        Args:
            limit: Maximum number of items to return
            priority: Filter by priority (optional)

        Returns:
            list: Pending queue items
        """
        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = """
                        SELECT id, failure_id, build_id, error_category, error_message,
                               react_result, confidence, confidence_scores, concerns,
                               priority, status, created_at, sla_deadline
                        FROM hitl_queue
                        WHERE status = 'pending'
                    """
                    params = []

                    if priority:
                        query += " AND priority = %s"
                        params.append(priority)

                    query += """
                        ORDER BY
                            CASE priority
                                WHEN 'high' THEN 1
                                WHEN 'medium' THEN 2
                                WHEN 'low' THEN 3
                            END,
                            created_at ASC
                        LIMIT %s
                    """
                    params.append(limit)

                    cursor.execute(query, params)
                    items = cursor.fetchall()

                    return [dict(item) for item in items]

            except Exception as e:
                logger.error(f"[HITL] Failed to get pending items: {e}")
                return []
        else:
            # In-memory fallback
            filtered = [item for item in self.in_memory_queue if item['status'] == 'pending']
            if priority:
                filtered = [item for item in filtered if item['priority'] == priority]

            # Sort by priority then age
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            filtered.sort(key=lambda x: (priority_order.get(x['priority'], 4), x['created_at']))

            return filtered[:limit]

    def approve(self, failure_id: str, reviewer: str, notes: Optional[str] = None,
               rating: Optional[int] = None) -> bool:
        """
        Mark HITL item as approved by human reviewer

        Args:
            failure_id: Failure ID
            reviewer: Reviewer name/email
            notes: Optional review notes
            rating: Optional 1-5 star rating

        Returns:
            bool: Success status
        """
        self.total_approved += 1

        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE hitl_queue
                        SET status = 'approved',
                            reviewer = %s,
                            review_notes = %s,
                            feedback_rating = %s,
                            reviewed_at = NOW(),
                            sla_met = (NOW() <= sla_deadline)
                        WHERE failure_id = %s
                    """, (reviewer, notes, rating, failure_id))

                    self.postgres_conn.commit()
                    logger.info(f"[HITL] Approved: {failure_id} by {reviewer}")
                    return True

            except Exception as e:
                logger.error(f"[HITL] Failed to approve {failure_id}: {e}")
                return False
        else:
            # In-memory fallback
            for item in self.in_memory_queue:
                if item['failure_id'] == failure_id:
                    item['status'] = 'approved'
                    item['reviewer'] = reviewer
                    item['review_notes'] = notes
                    item['feedback_rating'] = rating
                    item['reviewed_at'] = datetime.now().isoformat()
                    return True

            return False

    def reject(self, failure_id: str, reviewer: str, notes: str,
              corrected_answer: Optional[Dict] = None) -> bool:
        """
        Mark HITL item as rejected, with optional correction

        Args:
            failure_id: Failure ID
            reviewer: Reviewer name/email
            notes: Rejection reason
            corrected_answer: Optional corrected answer

        Returns:
            bool: Success status
        """
        self.total_rejected += 1
        new_status = 'corrected' if corrected_answer else 'rejected'

        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE hitl_queue
                        SET status = %s,
                            reviewer = %s,
                            review_notes = %s,
                            corrected_answer = %s,
                            reviewed_at = NOW(),
                            sla_met = (NOW() <= sla_deadline)
                        WHERE failure_id = %s
                    """, (new_status, reviewer, notes,
                         Json(corrected_answer) if corrected_answer else None,
                         failure_id))

                    self.postgres_conn.commit()
                    logger.info(f"[HITL] Rejected: {failure_id} by {reviewer}")
                    return True

            except Exception as e:
                logger.error(f"[HITL] Failed to reject {failure_id}: {e}")
                return False
        else:
            # In-memory fallback
            for item in self.in_memory_queue:
                if item['failure_id'] == failure_id:
                    item['status'] = new_status
                    item['reviewer'] = reviewer
                    item['review_notes'] = notes
                    item['corrected_answer'] = corrected_answer
                    item['reviewed_at'] = datetime.now().isoformat()
                    return True

            return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get HITL queue statistics

        Returns:
            dict: Queue statistics and metrics
        """
        stats = {
            'total_queued': self.total_queued,
            'total_approved': self.total_approved,
            'total_rejected': self.total_rejected,
            'approval_rate': (self.total_approved / self.total_queued * 100)
                if self.total_queued > 0 else 0.0
        }

        if self.postgres_conn:
            try:
                with self.postgres_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get queue size by status
                    cursor.execute("""
                        SELECT status, COUNT(*) as count
                        FROM hitl_queue
                        GROUP BY status
                    """)
                    status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

                    # Get SLA metrics
                    cursor.execute("""
                        SELECT
                            COUNT(*) FILTER (WHERE sla_met = TRUE) as sla_met_count,
                            COUNT(*) FILTER (WHERE sla_met = FALSE) as sla_missed_count,
                            AVG(EXTRACT(EPOCH FROM (reviewed_at - created_at)) / 3600)
                                FILTER (WHERE reviewed_at IS NOT NULL) as avg_review_hours
                        FROM hitl_queue
                        WHERE status IN ('approved', 'rejected', 'corrected')
                    """)
                    sla_metrics = cursor.fetchone()

                    stats.update({
                        'pending_count': status_counts.get('pending', 0),
                        'in_review_count': status_counts.get('in_review', 0),
                        'approved_count': status_counts.get('approved', 0),
                        'rejected_count': status_counts.get('rejected', 0),
                        'sla_met_count': sla_metrics['sla_met_count'] or 0,
                        'sla_missed_count': sla_metrics['sla_missed_count'] or 0,
                        'avg_review_hours': round(float(sla_metrics['avg_review_hours'] or 0), 2),
                        'sla_compliance_rate': (
                            (sla_metrics['sla_met_count'] /
                             (sla_metrics['sla_met_count'] + sla_metrics['sla_missed_count']) * 100)
                            if (sla_metrics['sla_met_count'] + sla_metrics['sla_missed_count']) > 0
                            else 0.0
                        )
                    })

            except Exception as e:
                logger.error(f"[HITL] Failed to get statistics: {e}")

        else:
            # In-memory statistics
            stats.update({
                'pending_count': len([i for i in self.in_memory_queue if i['status'] == 'pending']),
                'in_review_count': len([i for i in self.in_memory_queue if i['status'] == 'in_review']),
                'approved_count': len([i for i in self.in_memory_queue if i['status'] == 'approved']),
                'rejected_count': len([i for i in self.in_memory_queue if i['status'] == 'rejected'])
            })

        return stats

    def __del__(self):
        """Close PostgreSQL connection on cleanup"""
        if self.postgres_conn:
            try:
                self.postgres_conn.close()
                logger.debug("[HITL] PostgreSQL connection closed")
            except:
                pass
