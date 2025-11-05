"""
Query Expansion Module (Task 0-ARCH.28)

Generates query variations to improve recall in Fusion RAG retrieval.

Strategies:
1. Acronym Expansion (JWT → JSON Web Token)
2. Synonym Addition (auth → authentication)
3. Technical Term Variations (TOKEN_EXPIRATION → token expiration)
4. Category Keywords (CODE_ERROR → implementation bug function)

Author: AI Analysis System
Date: 2025-11-02
Version: 1.0.0
"""

import re
from typing import List, Optional, Dict


class QueryExpander:
    """
    Query expansion for improved recall in retrieval

    Generates 2-3 query variations from original query using:
    - Acronym expansion
    - Synonym replacement
    - Technical term normalization
    - Category-specific keywords
    """

    # Common technical acronyms
    ACRONYMS = {
        'JWT': 'JSON Web Token',
        'API': 'Application Programming Interface',
        'SQL': 'Structured Query Language',
        'HTTP': 'Hypertext Transfer Protocol',
        'HTTPS': 'HTTP Secure',
        'SSL': 'Secure Sockets Layer',
        'TLS': 'Transport Layer Security',
        'URL': 'Uniform Resource Locator',
        'URI': 'Uniform Resource Identifier',
        'JSON': 'JavaScript Object Notation',
        'XML': 'Extensible Markup Language',
        'REST': 'Representational State Transfer',
        'CRUD': 'Create Read Update Delete',
        'ORM': 'Object Relational Mapping',
        'TTL': 'Time To Live',
        'CORS': 'Cross-Origin Resource Sharing',
        'CSRF': 'Cross-Site Request Forgery',
        'XSS': 'Cross-Site Scripting',
        'CSS': 'Cascading Style Sheets',
        'HTML': 'HyperText Markup Language',
        'DNS': 'Domain Name System',
        'TCP': 'Transmission Control Protocol',
        'UDP': 'User Datagram Protocol',
        'IP': 'Internet Protocol',
        'VPN': 'Virtual Private Network',
        'SSH': 'Secure Shell',
        'FTP': 'File Transfer Protocol',
        'SMTP': 'Simple Mail Transfer Protocol',
        'POP': 'Post Office Protocol',
        'IMAP': 'Internet Message Access Protocol'
    }

    # Common technical synonyms
    SYNONYMS = {
        'auth': ['authentication', 'login', 'credentials'],
        'authentication': ['auth', 'login', 'credentials'],
        'login': ['authentication', 'signin', 'auth'],
        'error': ['failure', 'issue', 'problem', 'exception'],
        'failure': ['error', 'issue', 'problem'],
        'issue': ['error', 'problem', 'bug'],
        'bug': ['error', 'issue', 'defect'],
        'config': ['configuration', 'settings', 'setup'],
        'configuration': ['config', 'settings', 'setup'],
        'settings': ['configuration', 'config', 'preferences'],
        'timeout': ['time out', 'timed out', 'connection timeout'],
        'database': ['db', 'datastore', 'data store'],
        'db': ['database', 'datastore'],
        'connection': ['connect', 'connectivity', 'link'],
        'middleware': ['middle ware', 'middleware component'],
        'permission': ['permissions', 'access', 'authorization'],
        'permissions': ['permission', 'access rights', 'authorization'],
        'unauthorized': ['401', 'not authorized', 'access denied'],
        'forbidden': ['403', 'access forbidden', 'not allowed'],
        'not found': ['404', 'missing', 'does not exist'],
        'server error': ['500', 'internal error', 'server failure'],
        'service': ['svc', 'microservice', 'daemon'],
        'deployment': ['deploy', 'release', 'rollout'],
        'environment': ['env', 'environment variable', 'runtime'],
        'token': ['access token', 'auth token', 'bearer token'],
        'password': ['pwd', 'passphrase', 'credentials'],
        'user': ['username', 'account', 'profile'],
        'session': ['user session', 'login session', 'web session'],
        'cache': ['cached', 'caching', 'cache memory'],
        'memory': ['mem', 'RAM', 'heap'],
        'network': ['net', 'networking', 'connectivity']
    }

    # Category-specific keywords
    CATEGORY_KEYWORDS = {
        'CODE_ERROR': ['implementation', 'bug', 'function', 'method', 'code'],
        'INFRA_ERROR': ['infrastructure', 'service', 'deployment', 'resource', 'system'],
        'CONFIG_ERROR': ['configuration', 'settings', 'environment', 'variable', 'parameter'],
        'DEPENDENCY_ERROR': ['package', 'library', 'dependency', 'module', 'import'],
        'TEST_ERROR': ['test', 'assertion', 'mock', 'unittest', 'testing'],
        'NETWORK_ERROR': ['network', 'connection', 'timeout', 'connectivity', 'socket'],
        'DATABASE_ERROR': ['database', 'query', 'transaction', 'schema', 'table'],
        'AUTH_ERROR': ['authentication', 'authorization', 'permission', 'access', 'credential'],
        'PERFORMANCE_ERROR': ['performance', 'slow', 'latency', 'timeout', 'bottleneck']
    }

    def __init__(self, max_variations: int = 3):
        """
        Initialize query expander

        Args:
            max_variations: Maximum number of query variations to generate (default: 3)
        """
        self.max_variations = max_variations

    def expand(
        self,
        query: str,
        error_category: Optional[str] = None,
        include_original: bool = True
    ) -> List[str]:
        """
        Expand query into multiple variations

        Args:
            query: Original query string
            error_category: Optional error category for context
            include_original: Whether to include original query (default: True)

        Returns:
            List of query variations (including original if include_original=True)

        Example:
            >>> expander = QueryExpander()
            >>> variations = expander.expand("JWT auth error", error_category="AUTH_ERROR")
            >>> print(variations)
            ['JWT auth error', 'JSON Web Token authentication error', 'JWT authentication failure']
        """
        variations = []

        # Always start with original if requested
        if include_original:
            variations.append(query)

        # Strategy 1: Expand acronyms
        acronym_expanded = self._expand_acronyms(query)
        if acronym_expanded and acronym_expanded != query:
            variations.append(acronym_expanded)

        # Strategy 2: Replace with synonyms
        synonym_replaced = self._replace_synonyms(query)
        if synonym_replaced and synonym_replaced != query:
            variations.append(synonym_replaced)

        # Strategy 3: Add category keywords
        if error_category:
            category_query = self._add_category_keywords(query, error_category)
            if category_query and category_query != query:
                variations.append(category_query)

        # Strategy 4: Normalize technical terms
        normalized = self._normalize_technical_terms(query)
        if normalized and normalized != query and normalized not in variations:
            variations.append(normalized)

        # Deduplicate and limit to max_variations
        unique_variations = list(dict.fromkeys(variations))  # Preserve order
        return unique_variations[:self.max_variations]

    def _expand_acronyms(self, query: str) -> Optional[str]:
        """
        Expand acronyms in query

        Args:
            query: Original query

        Returns:
            Query with expanded acronyms or None
        """
        expanded = query

        # Find and expand acronyms
        for acronym, expansion in self.ACRONYMS.items():
            # Match whole word only (case-insensitive)
            pattern = r'\b' + re.escape(acronym) + r'\b'
            if re.search(pattern, query, re.IGNORECASE):
                expanded = re.sub(pattern, expansion, expanded, count=1, flags=re.IGNORECASE)
                break  # Only expand one acronym to avoid over-expansion

        return expanded if expanded != query else None

    def _replace_synonyms(self, query: str) -> Optional[str]:
        """
        Replace words with synonyms

        Args:
            query: Original query

        Returns:
            Query with synonym replacements or None
        """
        words = query.lower().split()

        # Find first word with synonyms
        for i, word in enumerate(words):
            if word in self.SYNONYMS:
                synonyms = self.SYNONYMS[word]
                # Take first synonym that's different from original
                for syn in synonyms:
                    if syn != word:
                        words[i] = syn
                        return ' '.join(words)
                break

        return None

    def _add_category_keywords(self, query: str, category: str) -> Optional[str]:
        """
        Add category-specific keywords to query

        Args:
            query: Original query
            category: Error category

        Returns:
            Query with category keywords or None
        """
        if category not in self.CATEGORY_KEYWORDS:
            return None

        keywords = self.CATEGORY_KEYWORDS[category]

        # Add first keyword that's not already in query
        query_lower = query.lower()
        for keyword in keywords:
            if keyword not in query_lower:
                return f"{query} {keyword}"

        return None

    def _normalize_technical_terms(self, query: str) -> Optional[str]:
        """
        Normalize technical terms (e.g., TOKEN_EXPIRATION → token expiration)

        Args:
            query: Original query

        Returns:
            Query with normalized terms or None
        """
        # Find SCREAMING_SNAKE_CASE or snake_case identifiers
        pattern = r'\b[A-Z_]{3,}\b|\b[a-z_]+_[a-z_]+\b'
        matches = re.findall(pattern, query)

        if matches:
            normalized = query
            for match in matches:
                # Convert to space-separated lowercase
                replacement = match.lower().replace('_', ' ')
                normalized = normalized.replace(match, replacement, 1)
                break  # Only normalize one term

            return normalized if normalized != query else None

        return None

    def get_acronym_expansions(self, query: str) -> Dict[str, str]:
        """
        Get all acronyms in query and their expansions

        Args:
            query: Query string

        Returns:
            Dict mapping acronyms to expansions
        """
        found = {}
        for acronym, expansion in self.ACRONYMS.items():
            pattern = r'\b' + re.escape(acronym) + r'\b'
            if re.search(pattern, query, re.IGNORECASE):
                found[acronym] = expansion

        return found

    def get_synonyms(self, word: str) -> List[str]:
        """
        Get synonyms for a word

        Args:
            word: Word to find synonyms for

        Returns:
            List of synonyms
        """
        word_lower = word.lower()
        return self.SYNONYMS.get(word_lower, [])

    def add_custom_acronym(self, acronym: str, expansion: str):
        """
        Add custom acronym expansion

        Args:
            acronym: Acronym (e.g., 'DDN')
            expansion: Full expansion (e.g., 'Data Delivery Network')
        """
        self.ACRONYMS[acronym.upper()] = expansion

    def add_custom_synonym(self, word: str, synonyms: List[str]):
        """
        Add custom synonym mapping

        Args:
            word: Word
            synonyms: List of synonyms
        """
        self.SYNONYMS[word.lower()] = synonyms


# Singleton instance
_query_expander = None


def get_query_expander(max_variations: int = 3) -> QueryExpander:
    """
    Get singleton QueryExpander instance

    Args:
        max_variations: Maximum query variations

    Returns:
        QueryExpander instance
    """
    global _query_expander

    if _query_expander is None:
        _query_expander = QueryExpander(max_variations=max_variations)

    return _query_expander


if __name__ == '__main__':
    # Test query expansion
    print("=" * 60)
    print("Query Expansion Test - Task 0-ARCH.28")
    print("=" * 60)
    print()

    expander = QueryExpander(max_variations=3)

    test_queries = [
        ("JWT authentication error", "AUTH_ERROR"),
        ("SQL connection timeout", "DATABASE_ERROR"),
        ("TOKEN_EXPIRATION config issue", "CONFIG_ERROR"),
        ("API endpoint not found", None),
        ("auth middleware failure", "CODE_ERROR")
    ]

    for query, category in test_queries:
        print(f"Original: {query}")
        if category:
            print(f"Category: {category}")

        variations = expander.expand(query, error_category=category)

        print(f"Variations ({len(variations)}):")
        for i, var in enumerate(variations, 1):
            marker = " [original]" if var == query else ""
            print(f"  {i}. {var}{marker}")

        # Show acronyms found
        acronyms = expander.get_acronym_expansions(query)
        if acronyms:
            print(f"Acronyms found: {acronyms}")

        print()
