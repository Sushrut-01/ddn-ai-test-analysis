"""
Unit Tests for CRAG Verifier (Task 0-ARCH.14)

Tests the ConfidenceScorer and CRAGVerifier classes

Test Categories:
1. ConfidenceScorer tests (5 components)
2. CRAGVerifier routing tests (4 thresholds)
3. Integration tests
4. Edge case tests

Author: AI Analysis System
Date: 2025-11-02
"""

import unittest
from datetime import datetime
import sys
import os

# Add verification module to path
verification_dir = os.path.join(os.path.dirname(__file__), '..', 'verification')
sys.path.insert(0, verification_dir)

from crag_verifier import ConfidenceScorer, CRAGVerifier


class TestConfidenceScorer(unittest.TestCase):
    """Test ConfidenceScorer class"""

    def setUp(self):
        self.scorer = ConfidenceScorer()

    def test_relevance_score_high(self):
        """Test relevance score with high similarity docs"""
        docs = [
            {'similarity_score': 0.92},
            {'similarity_score': 0.87},
            {'similarity_score': 0.85}
        ]

        score = self.scorer.calculate_relevance_score(docs)

        # Average should be (0.92 + 0.87 + 0.85) / 3 = 0.88
        self.assertAlmostEqual(score, 0.88, places=2)
        self.assertGreaterEqual(score, 0.80)  # High relevance

    def test_relevance_score_low(self):
        """Test relevance score with low similarity docs"""
        docs = [
            {'similarity_score': 0.45},
            {'similarity_score': 0.38},
            {'similarity_score': 0.42}
        ]

        score = self.scorer.calculate_relevance_score(docs)

        # Average should be ~0.42
        self.assertLess(score, 0.50)  # Low relevance

    def test_relevance_score_empty_docs(self):
        """Test relevance score with no documents"""
        docs = []

        score = self.scorer.calculate_relevance_score(docs)

        self.assertEqual(score, 0.0)  # No docs = 0 relevance

    def test_consistency_score_single_doc(self):
        """Test consistency with only one document"""
        docs = [
            {'text': 'Fix authentication by updating token expiration to 1 hour'}
        ]

        score = self.scorer.calculate_consistency_score(docs, "Some answer")

        # Single doc assumed consistent
        self.assertEqual(score, 1.0)

    def test_consistency_score_similar_docs(self):
        """Test consistency with similar documents"""
        docs = [
            {'text': 'Update token expiration to 1 hour in auth middleware'},
            {'text': 'Fix token validation - set expiration to 3600 seconds'},
            {'text': 'Increase auth token TTL to one hour'}
        ]

        answer = "Update token expiration"
        score = self.scorer.calculate_consistency_score(docs, answer)

        # Should have moderate consistency (heuristic-based scoring)
        self.assertGreater(score, 0.10)  # Not zero
        self.assertLess(score, 1.0)  # Not perfect

    def test_consistency_score_conflicting_docs(self):
        """Test consistency with conflicting documents"""
        docs = [
            {'text': 'Update token expiration to 1 hour'},
            {'text': 'Fix database connection timeout issue'},
            {'text': 'Install missing Python package requests'}
        ]

        answer = "Update token"
        score = self.scorer.calculate_consistency_score(docs, answer)

        # Should be low consistency (docs talk about different things)
        self.assertLess(score, 0.60)

    def test_grounding_score_well_grounded(self):
        """Test grounding score with well-grounded answer"""
        docs = [
            {'text': 'The authentication token expiration is set in auth/middleware.py line 45. '
                    'Current value is 30 minutes. Should be updated to 1 hour for better UX.'}
        ]

        answer = "The token expiration is set in auth/middleware.py. Update from 30 minutes to 1 hour."

        score = self.scorer.calculate_grounding_score(answer, docs)

        # Should be well-grounded (facts match docs)
        self.assertGreater(score, 0.70)

    def test_grounding_score_hallucination(self):
        """Test grounding score with hallucinated facts"""
        docs = [
            {'text': 'The authentication error occurs in the login function.'}
        ]

        answer = ("The error is in auth/middleware.py line 45. "
                 "The database connection pool size is set to 5 connections. "
                 "Update the Redis cache timeout to 300 seconds.")

        score = self.scorer.calculate_grounding_score(answer, docs)

        # Should be low (lots of facts not in docs)
        self.assertLess(score, 0.60)

    def test_grounding_score_no_docs(self):
        """Test grounding with no retrieved documents"""
        docs = []
        answer = "Update the configuration file"

        score = self.scorer.calculate_grounding_score(answer, docs)

        self.assertEqual(score, 0.0)  # No docs = no grounding

    def test_completeness_score_code_error_complete(self):
        """Test completeness for complete CODE_ERROR answer"""
        react_result = {
            'root_cause': 'The authentication fails because token expiration is set too short in auth/token.py line 45',
            'fix_recommendation': 'Update TOKEN_EXPIRATION from 1800 to 3600 seconds. Test by running pytest tests/test_auth.py',
            'error_category': 'CODE_ERROR'
        }

        score = self.scorer.calculate_completeness_score(react_result, 'CODE_ERROR')

        # Has: root_cause ✓, fix_steps ✓, code_location ✓, verification ✓
        # Should be 4/4 = 1.0
        self.assertGreaterEqual(score, 0.75)

    def test_completeness_score_code_error_incomplete(self):
        """Test completeness for incomplete CODE_ERROR answer"""
        react_result = {
            'root_cause': 'Authentication fails',
            'fix_recommendation': 'Update the token expiration',
            'error_category': 'CODE_ERROR'
        }

        score = self.scorer.calculate_completeness_score(react_result, 'CODE_ERROR')

        # Has: root_cause ✗ (too short), fix_steps ✗ (too short), code_location ✗, verification ✗
        # Should be low
        self.assertLess(score, 0.50)

    def test_completeness_score_infra_error(self):
        """Test completeness for INFRA_ERROR (doesn't need code_location)"""
        react_result = {
            'root_cause': 'PostgreSQL server is not running on localhost:5432. Connection refused.',
            'fix_recommendation': 'Start PostgreSQL service: sudo systemctl start postgresql. Verify with pg_isready.',
            'error_category': 'INFRA_ERROR'
        }

        score = self.scorer.calculate_completeness_score(react_result, 'INFRA_ERROR')

        # INFRA_ERROR needs: root_cause ✓, fix_steps ✓, verification ✓ (3/3)
        self.assertGreaterEqual(score, 0.90)

    def test_calculate_all_scores(self):
        """Test combined score calculation"""
        react_result = {
            'root_cause': 'Token expiration too short in auth/middleware.py',
            'fix_recommendation': 'Update TOKEN_EXPIRATION to 3600. Test with pytest.',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.85
        }

        docs = [
            {'similarity_score': 0.88, 'text': 'Token expiration in auth middleware'},
            {'similarity_score': 0.82, 'text': 'Update token expiration to one hour'},
        ]

        result = self.scorer.calculate_all_scores(react_result, docs)

        # Check structure
        self.assertIn('overall_confidence', result)
        self.assertIn('components', result)
        self.assertIn('weights', result)

        # Check components
        components = result['components']
        self.assertIn('relevance', components)
        self.assertIn('consistency', components)
        self.assertIn('grounding', components)
        self.assertIn('completeness', components)
        self.assertIn('classification', components)

        # All scores should be [0, 1]
        for score in components.values():
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)

        # Overall should be weighted average
        overall = result['overall_confidence']
        self.assertGreaterEqual(overall, 0.0)
        self.assertLessEqual(overall, 1.0)


class TestCRAGVerifier(unittest.TestCase):
    """Test CRAGVerifier class"""

    def setUp(self):
        self.verifier = CRAGVerifier()

    def test_high_confidence_pass_through(self):
        """Test HIGH confidence routing (≥0.85)"""
        react_result = {
            'root_cause': (
                'Authentication failure in test suite at test_user_authentication.py line 45. '
                'TOKEN_EXPIRATION constant in auth/middleware.py line 45 is set to 1800 seconds which equals 30 minutes. '
                'Long-running test suites exceed 30 minutes causing authentication tokens to expire during test execution. '
                'This results in authentication failures and test failures.'
            ),
            'fix_recommendation': (
                'Step 1: Open file auth/middleware.py and navigate to line 45\n'
                'Step 2: Update TOKEN_EXPIRATION constant from 1800 to 3600 seconds\n'
                'Step 3: Restart the authentication service to apply the changes\n'
                'Step 4: Run pytest tests/test_auth.py to verify the fix works correctly\n'
                'Step 5: Confirm all authentication tests pass successfully'
            ),
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.97
        }

        # Highly relevant docs with excellent similarity and overlap
        docs = [
            {
                'similarity_score': 0.97,
                'text': (
                    'Authentication failure in test suite at test_user_authentication.py line 45. '
                    'TOKEN_EXPIRATION constant in auth/middleware.py line 45 set to 1800 seconds which equals 30 minutes. '
                    'Long-running test suites exceed 30 minutes causing tokens to expire during test execution. '
                    'Solution: Open file auth/middleware.py navigate to line 45. '
                    'Update TOKEN_EXPIRATION constant from 1800 to 3600 seconds. '
                    'Restart authentication service to apply changes. '
                    'Run pytest tests/test_auth.py to verify fix works correctly. '
                    'Confirm all authentication tests pass successfully.'
                )
            },
            {
                'similarity_score': 0.95,
                'text': (
                    'TOKEN_EXPIRATION in auth/middleware.py line 45 currently 1800 seconds (30 minutes). '
                    'Test suites fail when execution time exceeds 30 minutes. '
                    'Tokens expire during test execution causing authentication failures. '
                    'Update constant to 3600 seconds. Restart service. Run pytest tests/test_auth.py. Verify tests pass.'
                )
            },
            {
                'similarity_score': 0.93,
                'text': (
                    'Fix authentication test failures in test_user_authentication.py. '
                    'TOKEN_EXPIRATION constant auth/middleware.py line 45 needs update from 1800 to 3600 seconds. '
                    'Long-running tests cause token expiration. '
                    'After updating restart authentication service run pytest tests/test_auth.py confirm tests pass successfully.'
                )
            }
        ]

        failure_data = {'build_id': 'test-001'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should be PASS with high confidence
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['confidence_level'], 'HIGH')
        self.assertGreaterEqual(result['confidence'], self.verifier.THRESHOLD_HIGH)
        self.assertEqual(result['action_taken'], 'pass_through')

    def test_medium_confidence_hitl(self):
        """Test HITL routing for moderate-quality inputs"""
        react_result = {
            'root_cause': 'Authentication fails due to token expiration issue in the authentication middleware component',
            'fix_recommendation': 'Update the token configuration settings in the middleware. Run tests to verify the changes work correctly.',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.78
        }

        docs = [
            {'similarity_score': 0.80, 'text': 'Token expiration configuration settings in authentication middleware. Update these values to resolve authentication timeout issues.'},
            {'similarity_score': 0.75, 'text': 'Authentication service settings and token management configuration parameters.'}
        ]

        failure_data = {'build_id': 'test-002'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should route to HITL (not high enough confidence for automatic pass-through)
        self.assertEqual(result['status'], 'HITL')
        self.assertLess(result['confidence'], self.verifier.THRESHOLD_HIGH)
        self.assertEqual(result['action_taken'], 'queued_for_hitl')
        self.assertIn('review_url', result)

    def test_low_confidence_self_correct(self):
        """Test that low-quality inputs route to HITL (would be self-correction with Task 0-ARCH.15)"""
        react_result = {
            'root_cause': 'Authentication error occurs in the system',
            'fix_recommendation': 'Fix the authentication configuration',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.55
        }

        docs = [
            {'similarity_score': 0.60, 'text': 'Authentication configuration and setup'},
            {'similarity_score': 0.52, 'text': 'Login and authentication process details'}
        ]

        failure_data = {'build_id': 'test-003'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should escalate to HITL since self_corrector not yet implemented (Task 0-ARCH.15)
        # When self-corrector is available, this would attempt self-correction first
        self.assertEqual(result['status'], 'HITL')
        # Confidence should be below HIGH threshold
        self.assertLess(result['confidence'], self.verifier.THRESHOLD_HIGH)

    def test_very_low_confidence_web_search(self):
        """Test VERY LOW confidence routing (<0.40) - should trigger web search"""
        react_result = {
            'root_cause': 'Unknown error occurred',
            'fix_recommendation': 'Fix the issue',
            'error_category': 'UNKNOWN',
            'classification_confidence': 0.25
        }

        docs = [
            {'similarity_score': 0.30, 'text': 'Some unrelated content about different topics'},
        ]

        failure_data = {'build_id': 'test-004'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should escalate to high-priority HITL since web_searcher not yet implemented (Task 0-ARCH.17)
        # When web_searcher is available, this would attempt web search first
        self.assertEqual(result['status'], 'HITL')
        self.assertLess(result['confidence'], self.verifier.THRESHOLD_LOW)
        self.assertEqual(result['verification_metadata']['priority'], 'high')

    def test_edge_case_no_docs(self):
        """Test edge case: No retrieved documents"""
        react_result = {
            'root_cause': 'Some error occurred',
            'fix_recommendation': 'Fix the error',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.70
        }

        docs = []  # No documents

        failure_data = {'build_id': 'test-005'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should have very low confidence due to no docs
        # Should route to HITL or web search
        self.assertIn(result['status'], ['HITL', 'WEB_SEARCH'])
        self.assertLess(result['confidence'], 0.60)

    def test_edge_case_empty_answer(self):
        """Test edge case: Empty answer from ReAct"""
        react_result = {
            'root_cause': '',
            'fix_recommendation': '',
            'error_category': 'UNKNOWN',
            'classification_confidence': 0.20
        }

        docs = [
            {'similarity_score': 0.75, 'text': 'Some documentation'}
        ]

        failure_data = {'build_id': 'test-006'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Should have low confidence
        self.assertLess(result['confidence'], self.verifier.THRESHOLD_MEDIUM)

    def test_priority_calculation(self):
        """Test HITL priority calculation"""
        failure_data_infra = {
            'build_id': 'test-007',
            'error_category': 'INFRA_ERROR'
        }

        failure_data_code = {
            'build_id': 'test-008',
            'error_category': 'CODE_ERROR'
        }

        # Low confidence should be high priority
        priority_low_conf = self.verifier._calculate_priority(0.66, failure_data_code)
        self.assertEqual(priority_low_conf, 'high')

        # INFRA_ERROR should be high priority
        priority_infra = self.verifier._calculate_priority(0.75, failure_data_infra)
        self.assertEqual(priority_infra, 'high')

        # Medium confidence CODE_ERROR should be medium priority
        priority_medium = self.verifier._calculate_priority(0.75, failure_data_code)
        self.assertEqual(priority_medium, 'medium')

    def test_verification_metadata(self):
        """Test that verification metadata is properly populated"""
        react_result = {
            'root_cause': 'Token expiration in auth/middleware.py',
            'fix_recommendation': 'Update TOKEN_EXPIRATION',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.85
        }

        docs = [
            {'similarity_score': 0.88, 'text': 'Token config'}
        ]

        failure_data = {'build_id': 'test-009'}

        result = self.verifier.verify(react_result, docs, failure_data)

        # Check metadata structure
        self.assertIn('verification_metadata', result)
        metadata = result['verification_metadata']

        self.assertIn('timestamp', metadata)
        self.assertIn('confidence_scores', metadata)
        self.assertIn('components', metadata['confidence_scores'])

        # Verify timestamp format
        timestamp = metadata['timestamp']
        datetime.fromisoformat(timestamp)  # Should not raise exception


class TestCRAGIntegration(unittest.TestCase):
    """Integration tests for CRAG verifier"""

    def test_end_to_end_high_quality(self):
        """Test end-to-end with high-quality ReAct result"""
        verifier = CRAGVerifier()

        react_result = {
            'root_cause': (
                'AssertionError in test_valid_login function at test_user_authentication.py line 45. '
                'Expected HTTP status code 200 but received 401 Unauthorized. '
                'Root cause identified: TOKEN_EXPIRATION constant in auth/middleware.py line 45 '
                'is set to 1800 seconds which equals 30 minutes. This causes authentication tokens to expire during test execution. '
                'The test suite takes longer than 30 minutes to run causing tokens to become invalid.'
            ),
            'fix_recommendation': (
                'Step 1: Open auth/middleware.py and locate line 45\n'
                'Step 2: Update TOKEN_EXPIRATION constant from 1800 to 3600 seconds\n'
                'Step 3: Restart the authentication service to apply changes\n'
                'Step 4: Run pytest tests/test_auth.py to verify the fix\n'
                'Step 5: Confirm all authentication tests pass successfully'
            ),
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.98
        }

        docs = [
            {
                'similarity_score': 0.98,
                'text': ('AssertionError in test_valid_login function at test_user_authentication.py line 45 occurs when status code is 401 Unauthorized instead of expected 200. '
                        'Root cause: TOKEN_EXPIRATION constant in auth/middleware.py line 45 set to 1800 seconds (30 minutes). '
                        'Tokens expire during test execution because test suite takes longer than 30 minutes. '
                        'Solution: Update TOKEN_EXPIRATION from 1800 to 3600 seconds. Open auth/middleware.py locate line 45 make the change. '
                        'Restart authentication service. Run pytest tests/test_auth.py to verify fix. Confirm all authentication tests pass successfully.')
            },
            {
                'similarity_score': 0.96,
                'text': ('Authentication token expiration configuration in auth/middleware.py line 45. '
                        'TOKEN_EXPIRATION constant currently set to 1800 seconds which equals 30 minutes. '
                        'Test failures occur in test_user_authentication.py when 401 errors received instead of 200. '
                        'Update constant to 3600 seconds. Restart service. Run pytest tests/test_auth.py verify all tests pass.')
            },
            {
                'similarity_score': 0.94,
                'text': ('Fix for authentication timeout issues in test_valid_login. '
                        'TOKEN_EXPIRATION in auth/middleware.py line 45 needs update from 1800 to 3600 seconds. '
                        'Test suite execution time exceeds 30 minutes causing token expiration. '
                        'After updating restart authentication service run pytest tests/test_auth.py confirm tests pass.')
            }
        ]

        failure_data = {
            'build_id': 'BUILD-12345',
            'error_category': 'CODE_ERROR'
        }

        result = verifier.verify(react_result, docs, failure_data)

        # Should pass through with high confidence
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['confidence_level'], 'HIGH')
        self.assertGreaterEqual(result['confidence'], 0.85)

        # Verify key components scored well
        components = result['verification_metadata']['confidence_scores']['components']
        self.assertGreater(components['relevance'], 0.90)  # Very high similarity docs
        self.assertGreater(components['classification'], 0.95)  # High classification confidence


def main():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceScorer))
    suite.addTests(loader.loadTestsFromTestCase(TestCRAGVerifier))
    suite.addTests(loader.loadTestsFromTestCase(TestCRAGIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)
