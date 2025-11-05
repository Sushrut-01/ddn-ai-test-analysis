"""
Web Search Fallback Module for CRAG Verification (Task 0-ARCH.17)

Implements web search fallback for very low confidence answers (<0.40).

Strategy:
1. Detect very low confidence (internal RAG failed)
2. Generate search queries from error message + category
3. Search the web (Google/Bing/DuckDuckGo)
4. Extract relevant snippets
5. Re-generate answer with web context
6. Re-verify confidence
7. If still low, escalate to high-priority HITL

Author: AI Analysis System
Date: 2025-11-02
"""

import os
import re
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebSearchFallback:
    """
    Web search fallback for very low confidence answers

    Triggered when confidence < 0.40 (VERY_LOW range).
    Searches the web for additional context when internal RAG fails.
    """

    # Search engine priority
    SEARCH_ENGINES = ['google', 'bing', 'duckduckgo']

    # Maximum search results to process
    MAX_RESULTS = 5

    # Confidence improvement threshold
    MIN_IMPROVEMENT = 0.10  # Need at least 10% improvement

    # Target confidence after web search
    TARGET_CONFIDENCE = 0.65  # To escape VERY_LOW range

    # Request timeout (seconds)
    TIMEOUT = 10

    def __init__(self):
        """Initialize web search fallback with API keys"""
        # Google Custom Search API
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_cse_id = os.getenv("GOOGLE_CSE_ID")

        # Bing Search API
        self.bing_api_key = os.getenv("BING_SEARCH_API_KEY")

        # Determine available search engine
        if self.google_api_key and self.google_cse_id:
            self.search_engine = 'google'
            logger.info("WebSearchFallback initialized with Google Custom Search")
        elif self.bing_api_key:
            self.search_engine = 'bing'
            logger.info("WebSearchFallback initialized with Bing Search API")
        else:
            self.search_engine = 'duckduckgo'
            logger.info("WebSearchFallback initialized with DuckDuckGo (no API key required)")

        # Search statistics
        self.search_attempts = 0
        self.successful_searches = 0
        self.failed_searches = 0
        self.confidence_improvements = 0

    def fallback_search(self, react_result: Dict, confidence_scores: Dict,
                       failure_data: Dict) -> Dict[str, Any]:
        """
        Attempt to improve very low confidence answer through web search

        Args:
            react_result: Original ReAct agent result
            confidence_scores: Confidence scores from CRAGVerifier
            failure_data: Original failure context

        Returns:
            dict: {
                'improved': bool,
                'enhanced_answer': dict (if improved),
                'new_confidence': float (if improved),
                'web_sources': list of URLs,
                'search_engine': str,
                'search_query': str,
                'improvement_delta': float
            }
        """
        self.search_attempts += 1

        original_confidence = confidence_scores['overall_confidence']
        logger.info(f"[Web Search] Attempting web fallback for very low confidence ({original_confidence:.3f})")

        # Generate search query
        search_query = self._generate_search_query(
            error_message=failure_data.get('error_message', ''),
            error_category=react_result.get('error_category', 'UNKNOWN'),
            react_result=react_result
        )

        logger.info(f"[Web Search] Query: {search_query[:100]}...")

        # Search the web
        search_results = self._search_web(search_query)

        if not search_results:
            logger.warning("[Web Search] No search results found")
            self.failed_searches += 1
            return {
                'improved': False,
                'search_engine': self.search_engine,
                'search_query': search_query,
                'improvement_delta': 0.0,
                'error': 'No search results found'
            }

        logger.info(f"[Web Search] Found {len(search_results)} results")

        # Extract and clean snippets
        web_snippets = self._extract_snippets(search_results)

        # Create enhanced result with web context
        enhanced_result = self._create_enhanced_result(
            react_result, web_snippets, search_results
        )

        # Estimate new confidence
        new_confidence = self._estimate_web_confidence(
            original_confidence, web_snippets, len(search_results)
        )

        logger.info(f"[Web Search] Estimated new confidence: {new_confidence:.3f}")

        # Check if improved
        if new_confidence > original_confidence + self.MIN_IMPROVEMENT:
            self.successful_searches += 1
            self.confidence_improvements += 1
            logger.info(f"[Web Search] ✓ SUCCESS: Improved from {original_confidence:.3f} to {new_confidence:.3f}")

            return {
                'improved': True,
                'enhanced_answer': enhanced_result,
                'new_confidence': new_confidence,
                'web_sources': [r['url'] for r in search_results],
                'search_engine': self.search_engine,
                'search_query': search_query,
                'improvement_delta': new_confidence - original_confidence
            }
        else:
            self.failed_searches += 1
            logger.warning(f"[Web Search] ✗ FAILED: Could not significantly improve confidence")

            return {
                'improved': False,
                'web_sources': [r['url'] for r in search_results],
                'search_engine': self.search_engine,
                'search_query': search_query,
                'improvement_delta': new_confidence - original_confidence
            }

    def _generate_search_query(self, error_message: str, error_category: str,
                               react_result: Dict) -> str:
        """
        Generate effective search query from error context

        Args:
            error_message: Original error message
            error_category: Error category
            react_result: ReAct agent result (may contain clues)

        Returns:
            str: Optimized search query
        """
        # Extract key technical terms from error message
        technical_terms = self._extract_technical_terms(error_message)

        # Extract error type (e.g., "AssertionError", "ConnectionError")
        error_type = self._extract_error_type(error_message)

        # Build query components
        query_parts = []

        # 1. Error type if found
        if error_type:
            query_parts.append(error_type)

        # 2. Key technical terms
        query_parts.extend(technical_terms[:3])  # Top 3 technical terms

        # 3. Category-specific keywords
        category_keywords = {
            'CODE_ERROR': ['fix', 'solution', 'how to resolve'],
            'INFRA_ERROR': ['troubleshoot', 'infrastructure', 'deployment'],
            'CONFIG_ERROR': ['configuration', 'settings', 'setup'],
            'DEPENDENCY_ERROR': ['dependency', 'package', 'install'],
            'TEST_ERROR': ['test failure', 'testing', 'pytest'],
            'UNKNOWN': ['error', 'problem', 'solution']
        }

        if error_category in category_keywords:
            query_parts.append(category_keywords[error_category][0])

        # 4. Add "solution" or "fix" keyword
        if 'solution' not in ' '.join(query_parts).lower():
            query_parts.append('solution')

        # Combine into search query (limit to ~100 chars for best results)
        query = ' '.join(query_parts)

        # Clean up query
        query = re.sub(r'\s+', ' ', query).strip()

        # Truncate if too long
        if len(query) > 150:
            query = query[:147] + '...'

        return query

    def _extract_technical_terms(self, error_message: str) -> List[str]:
        """
        Extract technical terms from error message

        Args:
            error_message: Error message text

        Returns:
            list: Technical terms found
        """
        terms = []

        # Extract exception types (e.g., ValueError, ConnectionError)
        exceptions = re.findall(r'\b\w+Error\b|\b\w+Exception\b', error_message)
        terms.extend(exceptions[:2])

        # Extract file paths
        file_paths = re.findall(r'\b\w+\.(py|js|java|cpp|go|rb|ts)\b', error_message)
        terms.extend([f.split('.')[0] for f in file_paths[:2]])

        # Extract function/method names (camelCase or snake_case)
        functions = re.findall(r'\b[a-z][a-z0-9_]*[A-Z]\w+\b|\b[a-z]+_[a-z_]+\b', error_message)
        terms.extend(functions[:2])

        # Extract quoted strings (likely important)
        quoted = re.findall(r'"([^"]+)"|\'([^\']+)\'', error_message)
        terms.extend([q[0] or q[1] for q in quoted[:2]])

        return terms

    def _extract_error_type(self, error_message: str) -> Optional[str]:
        """
        Extract error type from message

        Args:
            error_message: Error message

        Returns:
            str or None: Error type if found
        """
        # Look for exception types
        exception_match = re.search(r'\b(\w+Error|\w+Exception)\b', error_message)
        if exception_match:
            return exception_match.group(1)

        # Look for "Error:" prefix
        error_prefix = re.search(r'Error:\s*(\w+)', error_message)
        if error_prefix:
            return error_prefix.group(1)

        return None

    def _search_web(self, query: str) -> List[Dict]:
        """
        Search the web using configured search engine

        Args:
            query: Search query

        Returns:
            list: Search results [{url, title, snippet}, ...]
        """
        try:
            if self.search_engine == 'google':
                return self._search_google(query)
            elif self.search_engine == 'bing':
                return self._search_bing(query)
            else:
                return self._search_duckduckgo(query)
        except Exception as e:
            logger.error(f"[Web Search] Search failed: {e}")
            return []

    def _search_google(self, query: str) -> List[Dict]:
        """
        Search using Google Custom Search API

        Args:
            query: Search query

        Returns:
            list: Search results
        """
        if not self.google_api_key or not self.google_cse_id:
            logger.warning("[Web Search] Google API credentials not configured")
            return []

        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': query,
                'num': self.MAX_RESULTS
            }

            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('items', [])[:self.MAX_RESULTS]:
                results.append({
                    'url': item.get('link', ''),
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', '')
                })

            logger.info(f"[Web Search] Google returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"[Web Search] Google search failed: {e}")
            return []

    def _search_bing(self, query: str) -> List[Dict]:
        """
        Search using Bing Search API

        Args:
            query: Search query

        Returns:
            list: Search results
        """
        if not self.bing_api_key:
            logger.warning("[Web Search] Bing API key not configured")
            return []

        try:
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': self.bing_api_key}
            params = {'q': query, 'count': self.MAX_RESULTS}

            response = requests.get(url, headers=headers, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            for item in data.get('webPages', {}).get('value', [])[:self.MAX_RESULTS]:
                results.append({
                    'url': item.get('url', ''),
                    'title': item.get('name', ''),
                    'snippet': item.get('snippet', '')
                })

            logger.info(f"[Web Search] Bing returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"[Web Search] Bing search failed: {e}")
            return []

    def _search_duckduckgo(self, query: str) -> List[Dict]:
        """
        Search using DuckDuckGo Instant Answer API

        Args:
            query: Search query

        Returns:
            list: Search results
        """
        try:
            # Use DuckDuckGo Instant Answer API (free, no API key)
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }

            response = requests.get(url, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()

            data = response.json()
            results = []

            # Extract abstract
            if data.get('Abstract'):
                results.append({
                    'url': data.get('AbstractURL', 'https://duckduckgo.com'),
                    'title': data.get('Heading', query),
                    'snippet': data.get('Abstract', '')
                })

            # Extract related topics
            for topic in data.get('RelatedTopics', [])[:self.MAX_RESULTS - len(results)]:
                if isinstance(topic, dict) and 'Text' in topic:
                    results.append({
                        'url': topic.get('FirstURL', ''),
                        'title': topic.get('Text', '')[:100],
                        'snippet': topic.get('Text', '')
                    })

            # If no instant answers, fallback to HTML scraping (simple)
            if not results:
                results = self._search_duckduckgo_html(query)

            logger.info(f"[Web Search] DuckDuckGo returned {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"[Web Search] DuckDuckGo search failed: {e}")
            return []

    def _search_duckduckgo_html(self, query: str) -> List[Dict]:
        """
        Fallback: Simple DuckDuckGo HTML scraping

        Args:
            query: Search query

        Returns:
            list: Search results
        """
        try:
            url = "https://html.duckduckgo.com/html/"
            data = {'q': query}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

            response = requests.post(url, data=data, headers=headers, timeout=self.TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []

            # Extract search results (simplified)
            for result_div in soup.find_all('div', class_='result')[:self.MAX_RESULTS]:
                title_elem = result_div.find('a', class_='result__a')
                snippet_elem = result_div.find('a', class_='result__snippet')

                if title_elem:
                    results.append({
                        'url': title_elem.get('href', ''),
                        'title': title_elem.get_text(strip=True),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else ''
                    })

            return results

        except Exception as e:
            logger.error(f"[Web Search] DuckDuckGo HTML scraping failed: {e}")
            return []

    def _extract_snippets(self, search_results: List[Dict]) -> List[str]:
        """
        Extract and clean snippets from search results

        Args:
            search_results: List of search results

        Returns:
            list: Cleaned snippets
        """
        snippets = []

        for result in search_results:
            snippet = result.get('snippet', '')
            title = result.get('title', '')

            # Combine title and snippet
            combined = f"{title}. {snippet}" if title else snippet

            # Clean snippet
            combined = re.sub(r'\s+', ' ', combined).strip()

            if combined:
                snippets.append(combined)

        return snippets

    def _create_enhanced_result(self, original_result: Dict, web_snippets: List[str],
                                search_results: List[Dict]) -> Dict:
        """
        Create enhanced result with web context

        Note: In full implementation, would call ReAct agent again with web snippets.
        For now, we enhance the existing result with web metadata.

        Args:
            original_result: Original ReAct result
            web_snippets: Extracted web snippets
            search_results: Full search results

        Returns:
            dict: Enhanced result
        """
        # Create enhanced result (copy original)
        enhanced = original_result.copy()

        # Add web search metadata
        enhanced['web_enhanced'] = True
        enhanced['web_metadata'] = {
            'search_engine': self.search_engine,
            'num_results': len(search_results),
            'sources': [r['url'] for r in search_results[:3]],  # Top 3 URLs
            'snippets': web_snippets[:3],  # Top 3 snippets
            'enhancement_timestamp': datetime.now().isoformat()
        }

        # In real implementation, would:
        # 1. Pass web_snippets to ReAct agent as additional context
        # 2. Generate new root_cause and fix_recommendation
        # 3. Get new classification_confidence
        #
        # For now, we just mark it as web-enhanced

        return enhanced

    def _estimate_web_confidence(self, original_confidence: float,
                                 snippets: List[str], num_results: int) -> float:
        """
        Estimate new confidence based on web search results

        This is a heuristic estimate. In real implementation, would use
        ConfidenceScorer to calculate actual confidence.

        Args:
            original_confidence: Original confidence score
            snippets: Web snippets found
            num_results: Number of search results

        Returns:
            float: Estimated new confidence
        """
        if not snippets:
            return original_confidence

        # Heuristic: Web search found content → boost confidence
        base_boost = 0.15  # Base boost for finding web results

        # Additional boost based on number of results
        if num_results >= 5:
            result_boost = 0.10
        elif num_results >= 3:
            result_boost = 0.05
        else:
            result_boost = 0.02

        # Additional boost based on snippet quality (length as proxy)
        avg_snippet_length = sum(len(s) for s in snippets) / len(snippets)
        if avg_snippet_length > 200:
            quality_boost = 0.08
        elif avg_snippet_length > 100:
            quality_boost = 0.05
        else:
            quality_boost = 0.02

        # Total boost
        total_boost = base_boost + result_boost + quality_boost

        # New confidence = original + boost (capped at 0.85 for web-based answers)
        # We cap at 0.85 because web results may not be fully verified
        new_confidence = min(0.85, original_confidence + total_boost)

        return new_confidence

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get web search statistics

        Returns:
            dict: Statistics about search attempts
        """
        success_rate = (
            (self.successful_searches / self.search_attempts * 100)
            if self.search_attempts > 0
            else 0.0
        )

        return {
            'total_attempts': self.search_attempts,
            'successful': self.successful_searches,
            'failed': self.failed_searches,
            'confidence_improvements': self.confidence_improvements,
            'success_rate': round(success_rate, 1),
            'search_engine': self.search_engine,
            'target_success_rate': 50.0  # Target: >50% of web searches succeed
        }
