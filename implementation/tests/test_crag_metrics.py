"""
Unit Tests for CRAG Metrics (Task 0-ARCH.19)

Tests the CRAGMetrics class that tracks CRAG verification performance
and effectiveness.

Author: AI Analysis System
Date: 2025-11-02
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, timedelta
import json

# Add verification module to path
verification_dir = os.path.join(os.path.dirname(__file__), '..', 'verification')
sys.path.insert(0, verification_dir)

from crag_metrics import CRAGMetrics, get_metrics, reset_metrics


class TestCRAGMetrics(unittest.TestCase):
    """Test CRAGMetrics class"""

    def setUp(self):
        """Set up test fixtures"""
        self.metrics = CRAGMetrics()

    def test_initialization(self):
        """Test CRAGMetrics initialization"""
        self.assertIsNotNone(self.metrics)
        self.assertEqual(self.metrics.total_verifications, 0)
        self.assertEqual(self.metrics.confidence_counts['HIGH'], 0)
        self.assertEqual(self.metrics.routing_counts['PASS'], 0)
        self.assertEqual(self.metrics.self_correction_attempts, 0)
        self.assertEqual(self.metrics.hitl_queued, 0)
        self.assertEqual(self.metrics.web_search_attempts, 0)

    def test_reset(self):
        """Test metrics reset"""
        # Add some data
        self.metrics.total_verifications = 10
        self.metrics.confidence_counts['HIGH'] = 5
        self.metrics.routing_counts['PASS'] = 3

        # Reset
        self.metrics.reset()

        # Verify reset
        self.assertEqual(self.metrics.total_verifications, 0)
        self.assertEqual(self.metrics.confidence_counts['HIGH'], 0)
        self.assertEqual(self.metrics.routing_counts['PASS'], 0)

    def test_record_verification_high_confidence(self):
        """Test recording HIGH confidence verification"""
        verification_result = {
            'status': 'PASS',
            'confidence': 0.92,
            'confidence_level': 'HIGH',
            'action_taken': 'pass_through',
            'verification_metadata': {
                'confidence_scores': {
                    'components': {
                        'relevance': 0.95,
                        'consistency': 0.90,
                        'grounding': 0.92,
                        'completeness': 0.88,
                        'classification': 0.94
                    }
                }
            }
        }

        self.metrics.record_verification(verification_result)

        # Verify counts
        self.assertEqual(self.metrics.total_verifications, 1)
        self.assertEqual(self.metrics.confidence_counts['HIGH'], 1)
        self.assertEqual(self.metrics.routing_counts['PASS'], 1)
        self.assertEqual(len(self.metrics.confidence_scores), 1)
        self.assertEqual(self.metrics.confidence_scores[0], 0.92)

        # Verify component scores
        self.assertEqual(len(self.metrics.component_scores['relevance']), 1)
        self.assertEqual(self.metrics.component_scores['relevance'][0], 0.95)

    def test_record_verification_medium_confidence(self):
        """Test recording MEDIUM confidence verification"""
        verification_result = {
            'status': 'HITL',
            'confidence': 0.72,
            'confidence_level': 'MEDIUM',
            'action_taken': 'queued_for_hitl',
            'verification_metadata': {
                'confidence_scores': {
                    'components': {
                        'relevance': 0.75,
                        'consistency': 0.70,
                        'grounding': 0.72,
                        'completeness': 0.68,
                        'classification': 0.74
                    }
                }
            }
        }

        self.metrics.record_verification(verification_result)

        # Verify counts
        self.assertEqual(self.metrics.confidence_counts['MEDIUM'], 1)
        self.assertEqual(self.metrics.routing_counts['HITL'], 1)

    def test_record_verification_low_confidence(self):
        """Test recording LOW confidence verification"""
        verification_result = {
            'status': 'CORRECTED',
            'confidence': 0.68,
            'confidence_level': 'CORRECTED',
            'action_taken': 'self_correction',
            'verification_metadata': {
                'confidence_scores': {
                    'components': {
                        'relevance': 0.65,
                        'consistency': 0.60,
                        'grounding': 0.62,
                        'completeness': 0.58,
                        'classification': 0.64
                    }
                }
            }
        }

        self.metrics.record_verification(verification_result)

        # LOW confidence would be in the CORRECTED routing
        self.assertEqual(self.metrics.routing_counts['CORRECTED'], 1)

    def test_record_verification_very_low_confidence(self):
        """Test recording VERY LOW confidence verification"""
        verification_result = {
            'status': 'WEB_SEARCH',
            'confidence': 0.62,
            'confidence_level': 'WEB_ENHANCED',
            'action_taken': 'web_search_fallback',
            'verification_metadata': {
                'confidence_scores': {
                    'components': {
                        'relevance': 0.55,
                        'consistency': 0.50,
                        'grounding': 0.52,
                        'completeness': 0.48,
                        'classification': 0.54
                    }
                }
            }
        }

        self.metrics.record_verification(verification_result)

        # VERY LOW confidence would be in the WEB_SEARCH routing
        self.assertEqual(self.metrics.routing_counts['WEB_SEARCH'], 1)

    def test_record_self_correction_success(self):
        """Test recording successful self-correction"""
        self.metrics.record_self_correction(
            success=True,
            original_confidence=0.55,
            new_confidence=0.68
        )

        self.assertEqual(self.metrics.self_correction_attempts, 1)
        self.assertEqual(self.metrics.self_correction_successes, 1)
        self.assertEqual(self.metrics.self_correction_failures, 0)
        self.assertEqual(len(self.metrics.confidence_improvements), 1)
        self.assertAlmostEqual(self.metrics.confidence_improvements[0], 0.13, places=2)

    def test_record_self_correction_failure(self):
        """Test recording failed self-correction"""
        self.metrics.record_self_correction(
            success=False,
            original_confidence=0.52
        )

        self.assertEqual(self.metrics.self_correction_attempts, 1)
        self.assertEqual(self.metrics.self_correction_successes, 0)
        self.assertEqual(self.metrics.self_correction_failures, 1)
        self.assertEqual(len(self.metrics.confidence_improvements), 0)

    def test_record_hitl_queue(self):
        """Test recording HITL queue operations"""
        # Queue with high priority
        self.metrics.record_hitl_queue(priority='high')
        self.assertEqual(self.metrics.hitl_queued, 1)
        self.assertEqual(self.metrics.hitl_pending, 1)
        self.assertEqual(self.metrics.hitl_priorities['high'], 1)

        # Queue with medium priority
        self.metrics.record_hitl_queue(priority='medium')
        self.assertEqual(self.metrics.hitl_queued, 2)
        self.assertEqual(self.metrics.hitl_pending, 2)
        self.assertEqual(self.metrics.hitl_priorities['medium'], 1)

    def test_record_hitl_approval(self):
        """Test recording HITL approval"""
        # Queue an item first
        self.metrics.record_hitl_queue()
        self.assertEqual(self.metrics.hitl_pending, 1)

        # Approve it
        self.metrics.record_hitl_approval()
        self.assertEqual(self.metrics.hitl_approved, 1)
        self.assertEqual(self.metrics.hitl_pending, 0)

    def test_record_hitl_rejection(self):
        """Test recording HITL rejection"""
        # Queue an item first
        self.metrics.record_hitl_queue()
        self.assertEqual(self.metrics.hitl_pending, 1)

        # Reject it
        self.metrics.record_hitl_rejection()
        self.assertEqual(self.metrics.hitl_rejected, 1)
        self.assertEqual(self.metrics.hitl_pending, 0)

    def test_record_web_search_success(self):
        """Test recording successful web search"""
        self.metrics.record_web_search(
            success=True,
            original_confidence=0.35,
            new_confidence=0.58
        )

        self.assertEqual(self.metrics.web_search_attempts, 1)
        self.assertEqual(self.metrics.web_search_successes, 1)
        self.assertEqual(self.metrics.web_search_failures, 0)
        self.assertEqual(len(self.metrics.web_search_improvements), 1)
        self.assertAlmostEqual(self.metrics.web_search_improvements[0], 0.23, places=2)

    def test_record_web_search_failure(self):
        """Test recording failed web search"""
        self.metrics.record_web_search(
            success=False,
            original_confidence=0.32
        )

        self.assertEqual(self.metrics.web_search_attempts, 1)
        self.assertEqual(self.metrics.web_search_successes, 0)
        self.assertEqual(self.metrics.web_search_failures, 1)
        self.assertEqual(len(self.metrics.web_search_improvements), 0)

    def test_get_statistics_empty(self):
        """Test get_statistics with no data"""
        stats = self.metrics.get_statistics()

        self.assertIn('summary', stats)
        self.assertEqual(stats['summary']['total_verifications'], 0)
        self.assertEqual(stats['summary']['average_confidence'], 0.0)

        self.assertIn('confidence_distribution', stats)
        self.assertIn('routing_distribution', stats)
        self.assertIn('component_scores', stats)
        self.assertIn('self_correction', stats)
        self.assertIn('hitl_queue', stats)
        self.assertIn('web_search', stats)

    def test_get_statistics_with_data(self):
        """Test get_statistics with actual data"""
        # Add multiple verifications
        for i in range(10):
            if i < 7:  # 70% HIGH confidence
                result = {
                    'status': 'PASS',
                    'confidence': 0.90,
                    'confidence_level': 'HIGH',
                    'action_taken': 'pass_through',
                    'verification_metadata': {'confidence_scores': {'components': {}}}
                }
            elif i < 9:  # 20% MEDIUM confidence
                result = {
                    'status': 'HITL',
                    'confidence': 0.72,
                    'confidence_level': 'MEDIUM',
                    'action_taken': 'queued_for_hitl',
                    'verification_metadata': {'confidence_scores': {'components': {}}}
                }
            else:  # 10% LOW confidence
                result = {
                    'status': 'CORRECTED',
                    'confidence': 0.55,
                    'confidence_level': 'LOW',
                    'action_taken': 'self_correction',
                    'verification_metadata': {'confidence_scores': {'components': {}}}
                }
            self.metrics.record_verification(result)

        stats = self.metrics.get_statistics()

        # Verify summary
        self.assertEqual(stats['summary']['total_verifications'], 10)
        self.assertGreater(stats['summary']['average_confidence'], 0.0)

        # Verify confidence distribution
        self.assertEqual(stats['confidence_distribution']['HIGH']['count'], 7)
        self.assertEqual(stats['confidence_distribution']['HIGH']['percentage'], 70.0)
        self.assertEqual(stats['confidence_distribution']['MEDIUM']['count'], 2)
        self.assertEqual(stats['confidence_distribution']['MEDIUM']['percentage'], 20.0)

        # Verify routing distribution
        self.assertEqual(stats['routing_distribution']['PASS']['count'], 7)
        self.assertEqual(stats['routing_distribution']['HITL']['count'], 2)
        self.assertEqual(stats['routing_distribution']['CORRECTED']['count'], 1)

    def test_get_time_series_hourly(self):
        """Test hourly time series data"""
        # Add some verifications
        for _ in range(5):
            result = {
                'status': 'PASS',
                'confidence': 0.90,
                'confidence_level': 'HIGH',
                'action_taken': 'pass_through',
                'verification_metadata': {'confidence_scores': {'components': {}}}
            }
            self.metrics.record_verification(result)

        hourly = self.metrics.get_time_series('hourly')
        self.assertIsInstance(hourly, dict)
        # Should have at least one entry for current hour
        self.assertGreater(len(hourly), 0)

    def test_get_time_series_daily(self):
        """Test daily time series data"""
        # Add some verifications
        for _ in range(3):
            result = {
                'status': 'PASS',
                'confidence': 0.90,
                'confidence_level': 'HIGH',
                'action_taken': 'pass_through',
                'verification_metadata': {'confidence_scores': {'components': {}}}
            }
            self.metrics.record_verification(result)

        daily = self.metrics.get_time_series('daily')
        self.assertIsInstance(daily, dict)
        # Should have at least one entry for today
        self.assertGreater(len(daily), 0)

    def test_export_metrics(self):
        """Test metrics export as JSON"""
        # Add some data
        result = {
            'status': 'PASS',
            'confidence': 0.92,
            'confidence_level': 'HIGH',
            'action_taken': 'pass_through',
            'verification_metadata': {'confidence_scores': {'components': {}}}
        }
        self.metrics.record_verification(result)

        # Export
        exported = self.metrics.export_metrics()

        # Should be valid JSON
        self.assertIsInstance(exported, str)
        parsed = json.loads(exported)
        self.assertIn('summary', parsed)
        self.assertIn('confidence_distribution', parsed)

    def test_get_health_status_healthy(self):
        """Test health status when system is healthy"""
        # Add mostly HIGH confidence verifications
        for _ in range(20):
            result = {
                'status': 'PASS',
                'confidence': 0.90,
                'confidence_level': 'HIGH',
                'action_taken': 'pass_through',
                'verification_metadata': {'confidence_scores': {'components': {}}}
            }
            self.metrics.record_verification(result)

        health = self.metrics.get_health_status()

        self.assertEqual(health['status'], 'healthy')
        self.assertEqual(len(health['warnings']), 0)

    def test_get_health_status_hitl_warning(self):
        """Test health warning for large HITL queue"""
        # Queue many items
        for _ in range(60):
            self.metrics.record_hitl_queue()

        health = self.metrics.get_health_status()

        self.assertEqual(health['status'], 'warning')
        self.assertGreater(len(health['warnings']), 0)
        # Should warn about HITL queue
        self.assertTrue(any('HITL queue' in w for w in health['warnings']))

    def test_get_health_status_low_high_confidence_rate(self):
        """Test health warning for low high-confidence rate"""
        # Add mostly LOW confidence verifications
        for _ in range(25):
            result = {
                'status': 'CORRECTED',
                'confidence': 0.55,
                'confidence_level': 'LOW',
                'action_taken': 'self_correction',
                'verification_metadata': {'confidence_scores': {'components': {}}}
            }
            self.metrics.record_verification(result)

        health = self.metrics.get_health_status()

        self.assertEqual(health['status'], 'warning')
        # Should warn about low high-confidence rate
        self.assertTrue(any('high-confidence' in w for w in health['warnings']))

    def test_recent_verifications_limit(self):
        """Test that recent verifications are limited to max_recent"""
        # Add more than max_recent verifications
        for i in range(150):
            result = {
                'status': 'PASS',
                'confidence': 0.90,
                'confidence_level': 'HIGH',
                'action_taken': 'pass_through',
                'verification_metadata': {'confidence_scores': {'components': {}}}
            }
            self.metrics.record_verification(result)

        # Should only keep max_recent (100)
        self.assertEqual(len(self.metrics.recent_verifications), 100)


class TestGlobalMetrics(unittest.TestCase):
    """Test global metrics functions"""

    def test_get_metrics_singleton(self):
        """Test that get_metrics returns singleton instance"""
        metrics1 = get_metrics()
        metrics2 = get_metrics()

        # Should be the same instance
        self.assertIs(metrics1, metrics2)

    def test_reset_metrics(self):
        """Test global reset_metrics function"""
        metrics = get_metrics()

        # Add some data
        result = {
            'status': 'PASS',
            'confidence': 0.90,
            'confidence_level': 'HIGH',
            'action_taken': 'pass_through',
            'verification_metadata': {'confidence_scores': {'components': {}}}
        }
        metrics.record_verification(result)
        self.assertEqual(metrics.total_verifications, 1)

        # Reset
        reset_metrics()

        # Should be reset
        self.assertEqual(metrics.total_verifications, 0)


def main():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCRAGMetrics))
    suite.addTests(loader.loadTestsFromTestCase(TestGlobalMetrics))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
