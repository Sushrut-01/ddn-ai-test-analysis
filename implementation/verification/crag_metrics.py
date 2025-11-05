"""
CRAG Evaluation Metrics (Task 0-ARCH.19)

Tracks performance and effectiveness of CRAG verification system.

Metrics tracked:
- Confidence distribution (HIGH/MEDIUM/LOW/VERY_LOW)
- Routing decisions (pass-through/HITL/self-correct/web-search)
- Self-correction success rates
- HITL queue statistics
- Web search success rates
- Component score averages
- Time-based trends

Author: AI Analysis System
Date: 2025-11-02
"""

import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json


class CRAGMetrics:
    """
    Metrics tracker for CRAG verification system

    Thread-safe metrics collection and reporting for monitoring
    CRAG performance and effectiveness.
    """

    def __init__(self):
        """Initialize metrics tracker"""
        # Thread lock for thread-safe operations
        self._lock = threading.Lock()

        # Reset all metrics
        self.reset()

    def reset(self):
        """Reset all metrics to zero"""
        with self._lock:
            # Overall statistics
            self.total_verifications = 0
            self.start_time = datetime.now()

            # Confidence level distribution
            self.confidence_counts = {
                'HIGH': 0,      # >= 0.85
                'MEDIUM': 0,    # 0.65 - 0.85
                'LOW': 0,       # 0.40 - 0.65
                'VERY_LOW': 0   # < 0.40
            }

            # Routing decisions
            self.routing_counts = {
                'PASS': 0,           # High confidence pass-through
                'HITL': 0,           # Medium confidence → human review
                'CORRECTED': 0,      # Low confidence → self-corrected
                'WEB_SEARCH': 0,     # Very low → web search
                'ERROR': 0           # Verification errors
            }

            # Confidence scores (for averaging)
            self.confidence_scores = []

            # Component scores (for averaging)
            self.component_scores = {
                'relevance': [],
                'consistency': [],
                'grounding': [],
                'completeness': [],
                'classification': []
            }

            # Self-correction metrics
            self.self_correction_attempts = 0
            self.self_correction_successes = 0
            self.self_correction_failures = 0
            self.confidence_improvements = []  # Delta values

            # HITL metrics
            self.hitl_queued = 0
            self.hitl_pending = 0
            self.hitl_approved = 0
            self.hitl_rejected = 0
            self.hitl_priorities = {
                'high': 0,
                'medium': 0,
                'low': 0
            }

            # Web search metrics
            self.web_search_attempts = 0
            self.web_search_successes = 0
            self.web_search_failures = 0
            self.web_search_improvements = []  # Delta values

            # Time-based tracking
            self.hourly_counts = defaultdict(int)  # Hour -> count
            self.daily_counts = defaultdict(int)   # Date -> count

            # Recent verifications (last 100)
            self.recent_verifications = []
            self.max_recent = 100

    def record_verification(self, verification_result: Dict[str, Any]):
        """
        Record a CRAG verification result

        Args:
            verification_result: Result from CRAGVerifier.verify()
        """
        with self._lock:
            self.total_verifications += 1

            # Extract data
            status = verification_result.get('status', 'UNKNOWN')
            confidence = verification_result.get('confidence', 0.0)
            confidence_level = verification_result.get('confidence_level', 'UNKNOWN')
            action = verification_result.get('action_taken', 'none')
            metadata = verification_result.get('verification_metadata', {})

            # Update confidence distribution
            if confidence_level in self.confidence_counts:
                self.confidence_counts[confidence_level] += 1

            # Update routing counts
            if status in self.routing_counts:
                self.routing_counts[status] += 1
            else:
                self.routing_counts['ERROR'] += 1

            # Store confidence score
            self.confidence_scores.append(confidence)

            # Store component scores
            confidence_scores = metadata.get('confidence_scores', {})
            components = confidence_scores.get('components', {})
            for component_name in self.component_scores.keys():
                score = components.get(component_name)
                if score is not None:
                    self.component_scores[component_name].append(score)

            # Time-based tracking
            now = datetime.now()
            hour_key = now.strftime('%Y-%m-%d %H:00')
            day_key = now.strftime('%Y-%m-%d')
            self.hourly_counts[hour_key] += 1
            self.daily_counts[day_key] += 1

            # Store recent verification
            recent_entry = {
                'timestamp': now.isoformat(),
                'status': status,
                'confidence': confidence,
                'confidence_level': confidence_level,
                'action': action
            }
            self.recent_verifications.append(recent_entry)
            if len(self.recent_verifications) > self.max_recent:
                self.recent_verifications.pop(0)

    def record_self_correction(self, success: bool, original_confidence: float,
                               new_confidence: Optional[float] = None):
        """
        Record a self-correction attempt

        Args:
            success: Whether correction succeeded
            original_confidence: Original confidence before correction
            new_confidence: New confidence after correction (if successful)
        """
        with self._lock:
            self.self_correction_attempts += 1

            if success:
                self.self_correction_successes += 1
                if new_confidence is not None:
                    improvement = new_confidence - original_confidence
                    self.confidence_improvements.append(improvement)
            else:
                self.self_correction_failures += 1

    def record_hitl_queue(self, priority: str = 'medium'):
        """
        Record an item queued for HITL

        Args:
            priority: Priority level (high/medium/low)
        """
        with self._lock:
            self.hitl_queued += 1
            self.hitl_pending += 1  # Initially pending
            if priority in self.hitl_priorities:
                self.hitl_priorities[priority] += 1

    def record_hitl_approval(self):
        """Record a HITL item being approved"""
        with self._lock:
            self.hitl_approved += 1
            if self.hitl_pending > 0:
                self.hitl_pending -= 1

    def record_hitl_rejection(self):
        """Record a HITL item being rejected"""
        with self._lock:
            self.hitl_rejected += 1
            if self.hitl_pending > 0:
                self.hitl_pending -= 1

    def record_web_search(self, success: bool, original_confidence: float,
                         new_confidence: Optional[float] = None):
        """
        Record a web search attempt

        Args:
            success: Whether search succeeded
            original_confidence: Original confidence before search
            new_confidence: New confidence after search (if successful)
        """
        with self._lock:
            self.web_search_attempts += 1

            if success:
                self.web_search_successes += 1
                if new_confidence is not None:
                    improvement = new_confidence - original_confidence
                    self.web_search_improvements.append(improvement)
            else:
                self.web_search_failures += 1

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive CRAG metrics

        Returns:
            dict: All collected metrics and calculated statistics
        """
        with self._lock:
            # Calculate uptime
            uptime = datetime.now() - self.start_time
            uptime_hours = uptime.total_seconds() / 3600

            # Calculate percentages
            total = self.total_verifications if self.total_verifications > 0 else 1

            confidence_distribution = {
                level: {
                    'count': count,
                    'percentage': round((count / total) * 100, 1)
                }
                for level, count in self.confidence_counts.items()
            }

            routing_distribution = {
                status: {
                    'count': count,
                    'percentage': round((count / total) * 100, 1)
                }
                for status, count in self.routing_counts.items()
            }

            # Average confidence
            avg_confidence = (
                sum(self.confidence_scores) / len(self.confidence_scores)
                if self.confidence_scores else 0.0
            )

            # Average component scores
            avg_components = {}
            for component_name, scores in self.component_scores.items():
                avg_components[component_name] = (
                    sum(scores) / len(scores) if scores else 0.0
                )

            # Self-correction statistics
            self_correction_rate = (
                (self.self_correction_successes / self.self_correction_attempts * 100)
                if self.self_correction_attempts > 0
                else 0.0
            )

            avg_improvement = (
                sum(self.confidence_improvements) / len(self.confidence_improvements)
                if self.confidence_improvements
                else 0.0
            )

            # HITL statistics
            hitl_total_processed = self.hitl_approved + self.hitl_rejected
            hitl_approval_rate = (
                (self.hitl_approved / hitl_total_processed * 100)
                if hitl_total_processed > 0
                else 0.0
            )

            # Web search statistics
            web_search_rate = (
                (self.web_search_successes / self.web_search_attempts * 100)
                if self.web_search_attempts > 0
                else 0.0
            )

            avg_web_improvement = (
                sum(self.web_search_improvements) / len(self.web_search_improvements)
                if self.web_search_improvements
                else 0.0
            )

            # Throughput
            verifications_per_hour = (
                self.total_verifications / uptime_hours
                if uptime_hours > 0
                else 0.0
            )

            return {
                'summary': {
                    'total_verifications': self.total_verifications,
                    'uptime_hours': round(uptime_hours, 2),
                    'verifications_per_hour': round(verifications_per_hour, 2),
                    'start_time': self.start_time.isoformat(),
                    'average_confidence': round(avg_confidence, 3)
                },
                'confidence_distribution': confidence_distribution,
                'routing_distribution': routing_distribution,
                'component_scores': {
                    component: round(score, 3)
                    for component, score in avg_components.items()
                },
                'self_correction': {
                    'total_attempts': self.self_correction_attempts,
                    'successes': self.self_correction_successes,
                    'failures': self.self_correction_failures,
                    'success_rate': round(self_correction_rate, 1),
                    'average_improvement': round(avg_improvement, 3),
                    'target_success_rate': 60.0  # From design doc
                },
                'hitl_queue': {
                    'total_queued': self.hitl_queued,
                    'pending': self.hitl_pending,
                    'approved': self.hitl_approved,
                    'rejected': self.hitl_rejected,
                    'approval_rate': round(hitl_approval_rate, 1),
                    'priorities': dict(self.hitl_priorities)
                },
                'web_search': {
                    'total_attempts': self.web_search_attempts,
                    'successes': self.web_search_successes,
                    'failures': self.web_search_failures,
                    'success_rate': round(web_search_rate, 1),
                    'average_improvement': round(avg_web_improvement, 3),
                    'target_success_rate': 50.0  # From design doc
                },
                'recent_verifications': self.recent_verifications[-10:]  # Last 10
            }

    def get_time_series(self, period: str = 'hourly') -> Dict[str, int]:
        """
        Get time-series data for verifications

        Args:
            period: 'hourly' or 'daily'

        Returns:
            dict: Time period -> count
        """
        with self._lock:
            if period == 'hourly':
                return dict(self.hourly_counts)
            elif period == 'daily':
                return dict(self.daily_counts)
            else:
                return {}

    def export_metrics(self) -> str:
        """
        Export metrics as JSON string

        Returns:
            str: JSON-formatted metrics
        """
        stats = self.get_statistics()
        return json.dumps(stats, indent=2)

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status based on metrics

        Returns:
            dict: Health status with warnings
        """
        with self._lock:
            stats = self.get_statistics()
            warnings = []
            health = 'healthy'

            # Check if HITL queue is growing
            if self.hitl_pending > 50:
                warnings.append(f"HITL queue large ({self.hitl_pending} pending)")
                health = 'warning'

            # Check self-correction success rate
            self_correction_rate = stats['self_correction']['success_rate']
            if self.self_correction_attempts >= 10 and self_correction_rate < 40:
                warnings.append(f"Low self-correction rate ({self_correction_rate:.1f}%)")
                health = 'warning'

            # Check web search success rate
            web_search_rate = stats['web_search']['success_rate']
            if self.web_search_attempts >= 10 and web_search_rate < 30:
                warnings.append(f"Low web search success rate ({web_search_rate:.1f}%)")
                health = 'warning'

            # Check confidence distribution (should have some HIGH confidence)
            high_percentage = stats['confidence_distribution']['HIGH']['percentage']
            if self.total_verifications >= 20 and high_percentage < 30:
                warnings.append(f"Low high-confidence rate ({high_percentage:.1f}%)")
                health = 'warning'

            return {
                'status': health,
                'warnings': warnings,
                'metrics_summary': {
                    'total_verifications': self.total_verifications,
                    'hitl_pending': self.hitl_pending,
                    'high_confidence_rate': high_percentage,
                    'self_correction_rate': self_correction_rate,
                    'web_search_rate': web_search_rate
                }
            }


# Global metrics instance
_global_metrics = None
_global_metrics_lock = threading.Lock()


def get_metrics() -> CRAGMetrics:
    """
    Get global CRAG metrics instance (singleton)

    Returns:
        CRAGMetrics: Global metrics tracker
    """
    global _global_metrics

    if _global_metrics is None:
        with _global_metrics_lock:
            if _global_metrics is None:  # Double-check locking
                _global_metrics = CRAGMetrics()

    return _global_metrics


def reset_metrics():
    """Reset global metrics"""
    metrics = get_metrics()
    metrics.reset()
