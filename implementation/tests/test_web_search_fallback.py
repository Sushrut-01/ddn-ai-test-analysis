"""
Unit Tests for Web Search Fallback (Task 0-ARCH.17)

Tests the WebSearchFallback class that provides web search fallback
for very low confidence answers (<0.40).

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

from web_search_fallback import WebSearchFallback


class TestWebSearchFallback(unittest.TestCase):
    """Test WebSearchFallback class"""

    def setUp(self):
        self.searcher = WebSearchFallback()

    def test_initialization(self):
        """Test WebSearchFallback initialization"""
        self.assertIsNotNone(self.searcher)
        self.assertIn(self.searcher.search_engine, ['google', 'bing', 'duckduckgo'])
        self.assertEqual(self.searcher.search_attempts, 0)
        self.assertEqual(self.searcher.successful_searches, 0)

    def test_extract_technical_terms(self):
        """Test extraction of technical terms from error message"""
        error_message = 'AssertionError in test_login.py: Expected 200, got 401 "TokenExpired"'

        terms = self.searcher._extract_technical_terms(error_message)

        # Should extract exception types, file names, quoted strings
        self.assertGreater(len(terms), 0)
        # Should find AssertionError
        self.assertTrue(any('AssertionError' in term for term in terms))

    def test_extract_error_type(self):
        """Test extraction of error type"""
        # Test with Exception
        error_message_1 = "ValueError: Invalid input provided"
        error_type_1 = self.searcher._extract_error_type(error_message_1)
        self.assertEqual(error_type_1, "ValueError")

        # Test with Error
        error_message_2 = "ConnectionError occurred during API call"
        error_type_2 = self.searcher._extract_error_type(error_message_2)
        self.assertEqual(error_type_2, "ConnectionError")

        # Test with no error type
        error_message_3 = "Something went wrong"
        error_type_3 = self.searcher._extract_error_type(error_message_3)
        self.assertIsNone(error_type_3)

    def test_generate_search_query_code_error(self):
        """Test search query generation for CODE_ERROR"""
        error_message = "AssertionError in test_auth.py line 45: Expected 200, got 401"
        error_category = "CODE_ERROR"
        react_result = {
            'root_cause': 'Token expiration issue',
            'error_category': 'CODE_ERROR'
        }

        query = self.searcher._generate_search_query(error_message, error_category, react_result)

        # Should include error type and category keywords
        self.assertIn('AssertionError', query)
        self.assertTrue('fix' in query.lower() or 'solution' in query.lower())

    def test_generate_search_query_infra_error(self):
        """Test search query generation for INFRA_ERROR"""
        error_message = "ConnectionError: Failed to connect to database at localhost:5432"
        error_category = "INFRA_ERROR"
        react_result = {'error_category': 'INFRA_ERROR'}

        query = self.searcher._generate_search_query(error_message, error_category, react_result)

        # Should include error type and infra keywords
        self.assertIn('ConnectionError', query)
        self.assertTrue('troubleshoot' in query.lower() or 'infrastructure' in query.lower())

    def test_extract_snippets(self):
        """Test snippet extraction from search results"""
        search_results = [
            {
                'url': 'https://example.com/1',
                'title': 'How to Fix AssertionError',
                'snippet': 'AssertionError occurs when a test assertion fails. Solution: Check your test expectations.'
            },
            {
                'url': 'https://example.com/2',
                'title': 'Debugging Test Failures',
                'snippet': 'Common causes of test failures include incorrect assertions and environment issues.'
            }
        ]

        snippets = self.searcher._extract_snippets(search_results)

        # Should have 2 snippets
        self.assertEqual(len(snippets), 2)
        # Should combine title and snippet
        self.assertIn('How to Fix AssertionError', snippets[0])
        self.assertIn('Check your test expectations', snippets[0])

    def test_estimate_web_confidence_high_results(self):
        """Test confidence estimation with good search results"""
        original_confidence = 0.35
        snippets = [
            'This is a detailed solution to the AssertionError problem. You need to update your token expiration settings to 3600 seconds.',
            'Fix the authentication issue by updating the TOKEN_EXPIRATION constant in auth/middleware.py line 45.',
            'Step-by-step guide: 1. Open middleware.py 2. Change TOKEN_EXPIRATION 3. Restart service'
        ]
        num_results = 5

        new_confidence = self.searcher._estimate_web_confidence(
            original_confidence, snippets, num_results
        )

        # Should improve significantly
        self.assertGreater(new_confidence, original_confidence + 0.10)
        # But should not exceed 0.85 (web results cap)
        self.assertLessEqual(new_confidence, 0.85)

    def test_estimate_web_confidence_poor_results(self):
        """Test confidence estimation with poor search results"""
        original_confidence = 0.38
        snippets = ['Short text']  # Very short snippet
        num_results = 1

        new_confidence = self.searcher._estimate_web_confidence(
            original_confidence, snippets, num_results
        )

        # Should improve (base boost is 0.15)
        self.assertGreater(new_confidence, original_confidence)
        # Poor results should give less boost than high results
        # But will still get base_boost (0.15) + small result_boost + small quality_boost
        self.assertLess(new_confidence, original_confidence + 0.25)

    def test_estimate_web_confidence_no_results(self):
        """Test confidence estimation with no results"""
        original_confidence = 0.32
        snippets = []
        num_results = 0

        new_confidence = self.searcher._estimate_web_confidence(
            original_confidence, snippets, num_results
        )

        # Should not change
        self.assertEqual(new_confidence, original_confidence)

    def test_create_enhanced_result(self):
        """Test creation of enhanced result with web metadata"""
        original_result = {
            'root_cause': 'Token issue',
            'fix_recommendation': 'Update config',
            'error_category': 'CODE_ERROR'
        }

        web_snippets = ['Solution found in documentation', 'Update settings']
        search_results = [
            {'url': 'https://example.com/1', 'title': 'Fix 1', 'snippet': 'Snippet 1'},
            {'url': 'https://example.com/2', 'title': 'Fix 2', 'snippet': 'Snippet 2'}
        ]

        enhanced = self.searcher._create_enhanced_result(
            original_result, web_snippets, search_results
        )

        # Should have web_enhanced flag
        self.assertTrue(enhanced.get('web_enhanced'))
        # Should have web_metadata
        self.assertIn('web_metadata', enhanced)
        # Should include sources
        self.assertIn('sources', enhanced['web_metadata'])
        self.assertEqual(len(enhanced['web_metadata']['sources']), 2)

    @patch('web_search_fallback.requests.get')
    def test_search_duckduckgo_success(self, mock_get):
        """Test DuckDuckGo search (mocked)"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Abstract': 'This is a test abstract about error fixing',
            'AbstractURL': 'https://example.com',
            'Heading': 'Error Fix Guide',
            'RelatedTopics': [
                {
                    'Text': 'Solution 1: Update configuration',
                    'FirstURL': 'https://example.com/solution1'
                },
                {
                    'Text': 'Solution 2: Restart service',
                    'FirstURL': 'https://example.com/solution2'
                }
            ]
        }
        mock_get.return_value = mock_response

        # Force DuckDuckGo
        self.searcher.search_engine = 'duckduckgo'
        results = self.searcher._search_duckduckgo('test query')

        # Should have results
        self.assertGreater(len(results), 0)
        # First result should be abstract
        self.assertEqual(results[0]['url'], 'https://example.com')
        self.assertIn('error fixing', results[0]['snippet'])

    @patch('web_search_fallback.requests.get')
    def test_search_google_success(self, mock_get):
        """Test Google search (mocked)"""
        # Set up Google credentials
        self.searcher.google_api_key = 'test_key'
        self.searcher.google_cse_id = 'test_cse'
        self.searcher.search_engine = 'google'

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'link': 'https://example.com/result1',
                    'title': 'Result 1',
                    'snippet': 'This is result 1 snippet'
                },
                {
                    'link': 'https://example.com/result2',
                    'title': 'Result 2',
                    'snippet': 'This is result 2 snippet'
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = self.searcher._search_google('test query')

        # Should have 2 results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], 'https://example.com/result1')
        self.assertEqual(results[1]['title'], 'Result 2')

    @patch('web_search_fallback.requests.get')
    def test_search_bing_success(self, mock_get):
        """Test Bing search (mocked)"""
        # Set up Bing credentials
        self.searcher.bing_api_key = 'test_key'
        self.searcher.search_engine = 'bing'

        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'webPages': {
                'value': [
                    {
                        'url': 'https://example.com/bing1',
                        'name': 'Bing Result 1',
                        'snippet': 'Bing snippet 1'
                    },
                    {
                        'url': 'https://example.com/bing2',
                        'name': 'Bing Result 2',
                        'snippet': 'Bing snippet 2'
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        results = self.searcher._search_bing('test query')

        # Should have 2 results
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], 'https://example.com/bing1')
        self.assertEqual(results[1]['snippet'], 'Bing snippet 2')

    @patch.object(WebSearchFallback, '_search_web')
    def test_fallback_search_success(self, mock_search):
        """Test full fallback search (mocked)"""
        # Mock search results
        mock_search.return_value = [
            {
                'url': 'https://example.com/solution',
                'title': 'How to Fix AssertionError in Authentication',
                'snippet': 'The solution is to update TOKEN_EXPIRATION from 1800 to 3600 seconds in auth/middleware.py. This fixes the authentication timeout issue.'
            },
            {
                'url': 'https://stackoverflow.com/q/12345',
                'title': 'Token Expiration Issues',
                'snippet': 'Common cause: token TTL too short. Increase to 1 hour (3600 seconds).'
            }
        ]

        react_result = {
            'root_cause': 'Unknown authentication error',
            'fix_recommendation': 'Check configuration',
            'error_category': 'CODE_ERROR'
        }

        confidence_scores = {
            'overall_confidence': 0.35,
            'components': {
                'relevance': 0.40,
                'consistency': 0.30,
                'grounding': 0.35,
                'completeness': 0.30,
                'classification': 0.40
            }
        }

        failure_data = {
            'build_id': 'TEST-WEB-001',
            'error_message': 'AssertionError: Expected 200, got 401'
        }

        result = self.searcher.fallback_search(react_result, confidence_scores, failure_data)

        # Should show improvement
        self.assertTrue(result['improved'])
        self.assertGreater(result['new_confidence'], 0.35)
        self.assertIn('web_sources', result)
        self.assertEqual(len(result['web_sources']), 2)
        self.assertEqual(result['search_engine'], self.searcher.search_engine)

    @patch.object(WebSearchFallback, '_search_web')
    def test_fallback_search_no_results(self, mock_search):
        """Test fallback search with no results"""
        # Mock empty search results
        mock_search.return_value = []

        react_result = {'error_category': 'UNKNOWN'}
        confidence_scores = {'overall_confidence': 0.30, 'components': {}}
        failure_data = {'build_id': 'TEST-NO-RESULTS', 'error_message': 'Unknown error'}

        result = self.searcher.fallback_search(react_result, confidence_scores, failure_data)

        # Should not improve
        self.assertFalse(result['improved'])
        self.assertIn('error', result)

    def test_get_statistics(self):
        """Test statistics tracking"""
        # Simulate some searches
        self.searcher.search_attempts = 10
        self.searcher.successful_searches = 6
        self.searcher.failed_searches = 4
        self.searcher.confidence_improvements = 5

        stats = self.searcher.get_statistics()

        # Verify statistics
        self.assertEqual(stats['total_attempts'], 10)
        self.assertEqual(stats['successful'], 6)
        self.assertEqual(stats['failed'], 4)
        self.assertEqual(stats['success_rate'], 60.0)
        self.assertEqual(stats['confidence_improvements'], 5)


class TestWebSearchIntegration(unittest.TestCase):
    """Integration tests with CRAGVerifier"""

    def test_verifier_initializes_web_searcher(self):
        """Test that CRAGVerifier can initialize WebSearchFallback"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Should have web_searcher (may be None if dependencies missing)
        self.assertTrue(hasattr(verifier, 'web_searcher'))

    @patch.object(WebSearchFallback, '_search_web')
    def test_verifier_triggers_web_search_very_low_confidence(self, mock_search):
        """Test that CRAGVerifier triggers web search for very low confidence"""
        from crag_verifier import CRAGVerifier

        verifier = CRAGVerifier()

        # Skip if web searcher not available
        if not verifier.web_searcher:
            self.skipTest("WebSearchFallback not available")

        # Mock search results
        mock_search.return_value = [
            {
                'url': 'https://example.com/fix',
                'title': 'Solution Found',
                'snippet': 'Detailed solution to your problem with step-by-step instructions.'
            }
        ]

        react_result = {
            'root_cause': 'Unknown error',
            'fix_recommendation': 'Unknown fix',
            'error_category': 'UNKNOWN',
            'classification_confidence': 0.25
        }

        docs = [
            {'similarity_score': 0.30, 'text': 'Unrelated content'}
        ]

        failure_data = {
            'build_id': 'TEST-VERY-LOW',
            'error_message': 'Unknown error occurred'
        }

        result = verifier.verify(react_result, docs, failure_data)

        # Should attempt web search or escalate to HITL
        self.assertIn(result['status'], ['WEB_SEARCH', 'HITL'])

        # If web search worked, should have web sources
        if result['status'] == 'WEB_SEARCH':
            self.assertIn('web_sources', result['verification_metadata'])


def main():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchFallback))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
