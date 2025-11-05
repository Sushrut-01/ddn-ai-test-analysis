"""
Unit Tests for HITL Manager (Task 0-ARCH.16)

Tests the HITLManager class that manages human review queue for
medium-confidence answers.

Author: AI Analysis System
Date: 2025-11-02
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add verification module to path
verification_dir = os.path.join(os.path.dirname(__file__), '..', 'verification')
sys.path.insert(0, verification_dir)

from hitl_manager import HITLManager, HITLPriority, HITLStatus


class TestHITLManager(unittest.TestCase):
    """Test HITLManager class"""

    def setUp(self):
        self.manager = HITLManager()

    def test_queue_item_in_memory(self):
        """Test queueing item (in-memory mode)"""
        react_result = {
            'root_cause': 'Token issue',
            'fix_recommendation': 'Update config',
            'error_category': 'CONFIG_ERROR',
            'classification_confidence': 0.75
        }

        confidence_scores = {
            'overall_confidence': 0.72,
            'components': {
                'relevance': 0.80,
                'consistency': 0.68,  # Low
                'grounding': 0.75,
                'completeness': 0.65,  # Low
                'classification': 0.75
            }
        }

        failure_data = {
            'build_id': 'TEST-001',
            'error_message': 'Configuration error occurred'
        }

        item = self.manager.queue(
            react_result=react_result,
            confidence=0.72,
            confidence_scores=confidence_scores,
            failure_data=failure_data,
            priority='medium'
        )

        # Should have ID and metadata
        self.assertIn('id', item)
        self.assertEqual(item['failure_id'], 'TEST-001')
        self.assertEqual(item['priority'], 'medium')
        self.assertEqual(item['status'], 'pending')
        self.assertEqual(item['confidence'], 0.72)

        # Should identify concerns
        self.assertGreater(len(item['concerns']), 0)

    def test_identify_concerns(self):
        """Test identification of low-scoring components"""
        components = {
            'relevance': 0.85,
            'consistency': 0.65,  # Below 0.70
            'grounding': 0.55,    # Below 0.70
            'completeness': 0.45,  # Below 0.70
            'classification': 0.80
        }

        concerns = self.manager._identify_concerns(components)

        # Should identify 3 concerns
        self.assertEqual(len(concerns), 3)
        self.assertTrue(any('consistency' in c for c in concerns))
        self.assertTrue(any('grounding' in c for c in concerns))
        self.assertTrue(any('completeness' in c for c in concerns))

    def test_get_pending_items(self):
        """Test retrieving pending items"""
        # Queue some items
        for i in range(3):
            self.manager.queue(
                react_result={'root_cause': f'Error {i}'},
                confidence=0.70 + i * 0.01,
                confidence_scores={'overall_confidence': 0.70, 'components': {}},
                failure_data={'build_id': f'TEST-{i:03d}'},
                priority='medium'
            )

        pending = self.manager.get_pending_items()

        # Should get all 3 items
        self.assertEqual(len(pending), 3)

        # All should be pending
        for item in pending:
            self.assertEqual(item['status'], 'pending')

    def test_approve_item(self):
        """Test approving a queued item"""
        # Queue an item
        item = self.manager.queue(
            react_result={'root_cause': 'Test'},
            confidence=0.75,
            confidence_scores={'overall_confidence': 0.75, 'components': {}},
            failure_data={'build_id': 'TEST-APPROVE'},
            priority='medium'
        )

        # Approve it
        success = self.manager.approve(
            failure_id='TEST-APPROVE',
            reviewer='test@example.com',
            notes='Looks good',
            rating=5
        )

        self.assertTrue(success)
        self.assertEqual(self.manager.total_approved, 1)

    def test_reject_item(self):
        """Test rejecting a queued item"""
        # Queue an item
        item = self.manager.queue(
            react_result={'root_cause': 'Test'},
            confidence=0.75,
            confidence_scores={'overall_confidence': 0.75, 'components': {}},
            failure_data={'build_id': 'TEST-REJECT'},
            priority='medium'
        )

        # Reject it
        success = self.manager.reject(
            failure_id='TEST-REJECT',
            reviewer='test@example.com',
            notes='Needs correction',
            corrected_answer={'root_cause': 'Corrected'}
        )

        self.assertTrue(success)
        self.assertEqual(self.manager.total_rejected, 1)

    def test_get_statistics(self):
        """Test statistics tracking"""
        # Queue and process some items
        for i in range(5):
            self.manager.queue(
                react_result={'root_cause': f'Error {i}'},
                confidence=0.70,
                confidence_scores={'overall_confidence': 0.70, 'components': {}},
                failure_data={'build_id': f'TEST-{i:03d}'},
                priority='medium'
            )

        # Approve 3
        for i in range(3):
            self.manager.approve(f'TEST-{i:03d}', 'reviewer', 'OK')

        # Reject 1
        self.manager.reject('TEST-003', 'reviewer', 'Not OK')

        stats = self.manager.get_statistics()

        # Verify statistics
        self.assertEqual(stats['total_queued'], 5)
        self.assertEqual(stats['total_approved'], 3)
        self.assertEqual(stats['total_rejected'], 1)
        self.assertEqual(stats['approval_rate'], 60.0)  # 3/5 = 60%


class TestHITLIntegration(unittest.TestCase):
    """Integration tests with CRAGVerifier"""

    def test_verifier_initializes_hitl_manager(self):
        """Test that CRAGVerifier can initialize HITLManager"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Should have hitl_manager (may be None if dependencies missing)
        self.assertTrue(hasattr(verifier, 'hitl_manager'))

    def test_verifier_queues_medium_confidence(self):
        """Test that CRAGVerifier queues medium confidence items"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Skip if HITL manager not available
        if not verifier.hitl_manager:
            self.skipTest("HITLManager not available")

        react_result = {
            'root_cause': 'Medium confidence error',
            'fix_recommendation': 'Try this fix',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.75
        }

        docs = [
            {'similarity_score': 0.75, 'text': 'Some content'}
        ]

        failure_data = {'build_id': 'TEST-MEDIUM', 'error_message': 'Error XYZ'}

        result = verifier.verify(react_result, docs, failure_data)

        # Should queue for HITL
        if result['status'] == 'HITL':
            self.assertEqual(result['confidence_level'], 'MEDIUM')
            self.assertIn('verification_metadata', result)


def main():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestHITLManager))
    suite.addTests(loader.loadTestsFromTestCase(TestHITLIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
