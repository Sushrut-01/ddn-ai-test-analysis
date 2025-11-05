"""
Unit Tests for Self-Correction Module (Task 0-ARCH.15)

Tests the SelfCorrector class that improves low-confidence answers
through query expansion and re-retrieval.

Test Categories:
1. Query expansion tests
2. Component identification tests
3. Correction workflow tests
4. Integration tests with CRAGVerifier

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

from self_correction import SelfCorrector


class TestSelfCorrector(unittest.TestCase):
    """Test SelfCorrector class"""

    def setUp(self):
        self.corrector = SelfCorrector()

    def test_identify_low_components(self):
        """Test identification of low-scoring components"""
        components = {
            'relevance': 0.88,
            'consistency': 0.65,  # LOW
            'grounding': 0.55,    # LOW
            'completeness': 0.45,  # LOW
            'classification': 0.85
        }

        low = self.corrector._identify_low_components(components)

        # Should identify 3 low components
        self.assertEqual(len(low), 3)
        self.assertIn('consistency', low)
        self.assertIn('grounding', low)
        self.assertIn('completeness', low)

    def test_identify_no_low_components(self):
        """Test when all components are high"""
        components = {
            'relevance': 0.88,
            'consistency': 0.85,
            'grounding': 0.90,
            'completeness': 0.75,
            'classification': 0.85
        }

        low = self.corrector._identify_low_components(components)

        # Should find no low components
        self.assertEqual(len(low), 0)

    def test_expand_query_code_error(self):
        """Test query expansion for CODE_ERROR"""
        error_message = "AssertionError: Expected 200, got 401"
        error_category = "CODE_ERROR"
        low_components = ['relevance', 'grounding']

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should contain original error
        self.assertIn("AssertionError", expanded)
        self.assertIn("Expected 200, got 401", expanded)

        # Should contain category terms
        self.assertTrue(
            'code error' in expanded.lower() or
            'programming bug' in expanded.lower()
        )

    def test_expand_query_infra_error(self):
        """Test query expansion for INFRA_ERROR"""
        error_message = "Connection refused to PostgreSQL"
        error_category = "INFRA_ERROR"
        low_components = ['completeness']

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should contain original error
        self.assertIn("Connection refused", expanded)

        # Should contain infrastructure terms
        self.assertTrue(
            'infrastructure' in expanded.lower() or
            'deployment' in expanded.lower()
        )

    def test_expand_query_low_relevance(self):
        """Test query expansion when relevance is low"""
        error_message = "Test failed with error XYZ"
        error_category = "TEST_ERROR"
        low_components = ['relevance']  # Low relevance specifically

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should add "how to fix" phrasing
        self.assertIn("how to fix", expanded.lower())

    def test_expand_query_low_grounding(self):
        """Test query expansion when grounding is low"""
        error_message = "Module not found"
        error_category = "DEPENDENCY_ERROR"
        low_components = ['grounding']  # Low grounding specifically

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should add documentation terms
        self.assertTrue(
            'documentation' in expanded.lower() or
            'examples' in expanded.lower()
        )

    def test_expand_query_low_completeness(self):
        """Test query expansion when completeness is low"""
        error_message = "Configuration error"
        error_category = "CONFIG_ERROR"
        low_components = ['completeness']  # Low completeness specifically

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should add completeness terms
        self.assertTrue(
            'root cause' in expanded.lower() or
            'step by step' in expanded.lower() or
            'verification' in expanded.lower()
        )

    def test_expand_query_attempt_2_adds_more_terms(self):
        """Test that attempt 2 adds more expansion terms than attempt 1"""
        error_message = "Error occurred"
        error_category = "CODE_ERROR"
        low_components = ['relevance']

        expanded_1 = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        expanded_2 = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=2
        )

        # Attempt 2 should be longer (more terms)
        self.assertGreater(len(expanded_2), len(expanded_1))

    def test_expand_query_extracts_technical_terms(self):
        """Test extraction of technical exception names"""
        error_message = "ValueError: invalid literal for int() with base 10"
        error_category = "CODE_ERROR"
        low_components = []

        expanded = self.corrector._expand_query(
            error_message, error_category, low_components, attempt=1
        )

        # Should extract "ValueError"
        self.assertIn("ValueError", expanded)

    def test_estimate_new_confidence_high_similarity(self):
        """Test confidence estimation with high similarity docs"""
        original_confidence = 0.55
        new_docs = [
            {'similarity_score': 0.85},
            {'similarity_score': 0.82},
            {'similarity_score': 0.88}
        ]

        new_conf = self.corrector._estimate_new_confidence(
            original_confidence, new_docs, len(new_docs)
        )

        # Should boost confidence significantly (avg similarity > 0.80)
        self.assertGreater(new_conf, original_confidence + 0.10)
        self.assertLessEqual(new_conf, 1.0)

    def test_estimate_new_confidence_moderate_similarity(self):
        """Test confidence estimation with moderate similarity docs"""
        original_confidence = 0.50
        new_docs = [
            {'similarity_score': 0.75},
            {'similarity_score': 0.72}
        ]

        new_conf = self.corrector._estimate_new_confidence(
            original_confidence, new_docs, len(new_docs)
        )

        # Should boost moderately (avg similarity 0.70-0.80)
        self.assertGreater(new_conf, original_confidence)
        self.assertGreater(new_conf, original_confidence + 0.05)

    def test_estimate_new_confidence_low_similarity(self):
        """Test confidence estimation with low similarity docs"""
        original_confidence = 0.50
        new_docs = [
            {'similarity_score': 0.60},
            {'similarity_score': 0.55}
        ]

        new_conf = self.corrector._estimate_new_confidence(
            original_confidence, new_docs, len(new_docs)
        )

        # Should boost slightly (avg similarity < 0.70)
        self.assertGreater(new_conf, original_confidence)
        self.assertLess(new_conf, original_confidence + 0.10)

    def test_estimate_new_confidence_no_docs(self):
        """Test confidence estimation with no new documents"""
        original_confidence = 0.50
        new_docs = []

        new_conf = self.corrector._estimate_new_confidence(
            original_confidence, new_docs, 0
        )

        # Should return original confidence
        self.assertEqual(new_conf, original_confidence)

    def test_estimate_new_confidence_capped_at_1(self):
        """Test that confidence is capped at 1.0"""
        original_confidence = 0.90  # Already high
        new_docs = [
            {'similarity_score': 0.95},
            {'similarity_score': 0.92},
            {'similarity_score': 0.90}
        ]

        new_conf = self.corrector._estimate_new_confidence(
            original_confidence, new_docs, len(new_docs)
        )

        # Should cap at 1.0
        self.assertLessEqual(new_conf, 1.0)

    @patch('self_correction.PineconeVectorStore')
    def test_retrieve_additional_docs_mock(self, mock_vectorstore):
        """Test document retrieval with mocked Pinecone"""
        # Skip if embeddings not available
        if not self.corrector.embeddings:
            self.skipTest("OpenAI embeddings not available")

        # Mock the vectorstore
        mock_store = MagicMock()
        mock_vectorstore.return_value = mock_store

        # Mock similarity_search_with_score to return docs
        mock_doc1 = MagicMock()
        mock_doc1.page_content = "Document 1 content"
        mock_doc1.metadata = {'source': 'test'}

        mock_doc2 = MagicMock()
        mock_doc2.page_content = "Document 2 content"
        mock_doc2.metadata = {'source': 'test'}

        mock_store.similarity_search_with_score.return_value = [
            (mock_doc1, 0.85),
            (mock_doc2, 0.78)
        ]

        # Test retrieval
        docs = self.corrector._retrieve_additional_docs(
            query="test query",
            error_category="CODE_ERROR",
            top_k=10
        )

        # Should have retrieved docs
        self.assertGreater(len(docs), 0)

    def test_create_improved_result(self):
        """Test creation of improved result"""
        original_result = {
            'root_cause': 'Original root cause',
            'fix_recommendation': 'Original fix',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.70
        }

        new_docs = [
            {'text': 'New doc 1', 'similarity_score': 0.85},
            {'text': 'New doc 2', 'similarity_score': 0.80}
        ]

        improved = self.corrector._create_improved_result(
            original_result, new_docs, "expanded query"
        )

        # Should be marked as self-corrected
        self.assertTrue(improved['self_corrected'])
        self.assertIn('correction_metadata', improved)

        # Should have metadata
        metadata = improved['correction_metadata']
        self.assertIn('expanded_query', metadata)
        self.assertIn('additional_docs_count', metadata)
        self.assertEqual(metadata['additional_docs_count'], 2)

    def test_get_statistics(self):
        """Test statistics tracking"""
        # Simulate some correction attempts
        self.corrector.correction_attempts = 10
        self.corrector.successful_corrections = 7
        self.corrector.failed_corrections = 3

        stats = self.corrector.get_statistics()

        # Verify statistics
        self.assertEqual(stats['total_attempts'], 10)
        self.assertEqual(stats['successful'], 7)
        self.assertEqual(stats['failed'], 3)
        self.assertEqual(stats['success_rate'], 70.0)
        self.assertEqual(stats['target_success_rate'], 60.0)

    def test_get_statistics_no_attempts(self):
        """Test statistics with no attempts"""
        stats = self.corrector.get_statistics()

        # Success rate should be 0
        self.assertEqual(stats['total_attempts'], 0)
        self.assertEqual(stats['success_rate'], 0.0)


class TestSelfCorrectionIntegration(unittest.TestCase):
    """Integration tests for self-correction with CRAGVerifier"""

    def test_corrector_initialization_in_verifier(self):
        """Test that CRAGVerifier can initialize SelfCorrector"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Should have self_corrector (may be None if dependencies missing)
        self.assertTrue(hasattr(verifier, 'self_corrector'))

    @patch('self_correction.SelfCorrector.correct')
    def test_verifier_calls_self_correction_on_low_confidence(self, mock_correct):
        """Test that CRAGVerifier calls self-correction for low confidence"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Skip if self-corrector not available
        if not verifier.self_corrector:
            self.skipTest("SelfCorrector not available")

        # Mock correction to return improvement
        mock_correct.return_value = {
            'improved': True,
            'corrected_answer': {'root_cause': 'Improved', 'fix_recommendation': 'Better'},
            'new_confidence': 0.72,
            'method': 'query_expansion',
            'attempts': 2,
            'improvement_delta': 0.17
        }

        react_result = {
            'root_cause': 'Vague error description',
            'fix_recommendation': 'Try fixing it',
            'error_category': 'CODE_ERROR',
            'classification_confidence': 0.50
        }

        docs = [
            {'similarity_score': 0.55, 'text': 'Some content'}
        ]

        failure_data = {'build_id': 'test-001', 'error_message': 'Error XYZ'}

        result = verifier.verify(react_result, docs, failure_data)

        # Should have attempted self-correction
        mock_correct.assert_called_once()

        # If correction succeeded, should return CORRECTED status
        if result['status'] == 'CORRECTED':
            self.assertEqual(result['confidence_level'], 'CORRECTED')
            self.assertGreater(result['confidence'], 0.65)


def main():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSelfCorrector))
    suite.addTests(loader.loadTestsFromTestCase(TestSelfCorrectionIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
