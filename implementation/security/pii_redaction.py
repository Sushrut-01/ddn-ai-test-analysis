"""
PII Redaction Module (Phase 4, Task 4.1)

Redacts Personally Identifiable Information (PII) from error logs and test failures
using Microsoft Presidio before storing in MongoDB and creating embeddings.

Redacts:
- Email addresses
- IP addresses
- Phone numbers
- Credit card numbers
- Names
- Social Security Numbers
- API keys and tokens

Author: DDN AI Analysis System
Date: 2025-11-03
Version: 1.0.0
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

# Presidio imports
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    from presidio_anonymizer.entities import OperatorConfig
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    logging.warning("Presidio not available - PII redaction will use regex fallback")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PIIRedactor:
    """
    PII Redaction service using Microsoft Presidio with regex fallback

    Redacts sensitive information from text before storage and embedding creation.
    Uses Presidio when available, falls back to regex patterns otherwise.
    """

    # PII entity types to detect and redact
    PII_ENTITIES = [
        "EMAIL_ADDRESS",
        "PHONE_NUMBER",
        "CREDIT_CARD",
        "IP_ADDRESS",
        "PERSON",
        "US_SSN",
        "US_PASSPORT",
        "US_DRIVER_LICENSE",
        "URL",
        "LOCATION",
        "DATE_TIME",
        "IBAN_CODE",
        "CRYPTO",
        "MEDICAL_LICENSE",
        "US_BANK_NUMBER"
    ]

    # Regex patterns for fallback (when Presidio unavailable)
    REGEX_PATTERNS = {
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'IPV4': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'IPV6': r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b',
        'PHONE': r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'CREDIT_CARD': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'API_KEY': r'\b(?:api[_-]?key|token|bearer|secret)[:\s=]+[\'"]?[A-Za-z0-9_\-]{20,}[\'"]?\b',
        'AWS_KEY': r'\b(?:AKIA|ASIA)[0-9A-Z]{16}\b',
        'JWT': r'\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b'
    }

    # Replacement tokens
    REPLACEMENT_TOKENS = {
        'EMAIL': '<EMAIL>',
        'IPV4': '<IP_ADDRESS>',
        'IPV6': '<IP_ADDRESS>',
        'PHONE': '<PHONE_NUMBER>',
        'SSN': '<SSN>',
        'CREDIT_CARD': '<CREDIT_CARD>',
        'API_KEY': '<API_KEY>',
        'AWS_KEY': '<AWS_KEY>',
        'JWT': '<TOKEN>',
        'PERSON': '<PERSON>',
        'LOCATION': '<LOCATION>',
        'URL': '<URL>',
        'US_BANK_NUMBER': '<BANK_ACCOUNT>'
    }

    def __init__(self, use_presidio: bool = True):
        """
        Initialize PII redactor

        Args:
            use_presidio: Whether to use Presidio (True) or regex fallback (False)
        """
        self.use_presidio = use_presidio and PRESIDIO_AVAILABLE
        self.analyzer = None
        self.anonymizer = None

        if self.use_presidio:
            try:
                self.analyzer = AnalyzerEngine()
                self.anonymizer = AnonymizerEngine()
                logger.info("✓ PII Redactor initialized with Presidio")
            except Exception as e:
                logger.warning(f"Failed to initialize Presidio, using regex fallback: {e}")
                self.use_presidio = False
        else:
            logger.info("✓ PII Redactor initialized with regex fallback")

        # Statistics
        self.redaction_stats = {
            'total_redactions': 0,
            'by_type': {}
        }

    def redact(self, text: str, language: str = 'en') -> Tuple[str, Dict]:
        """
        Redact PII from text

        Args:
            text: Text to redact
            language: Language code (default: 'en')

        Returns:
            Tuple of (redacted_text, metadata)
        """
        if not text or not isinstance(text, str):
            return text, {'redactions': 0, 'entities': []}

        if self.use_presidio:
            return self._redact_with_presidio(text, language)
        else:
            return self._redact_with_regex(text)

    def _redact_with_presidio(self, text: str, language: str) -> Tuple[str, Dict]:
        """Redact PII using Presidio"""
        try:
            analyzer_results = self.analyzer.analyze(
                text=text,
                language=language,
                entities=self.PII_ENTITIES
            )

            if not analyzer_results:
                return text, {'redactions': 0, 'entities': []}

            operators = {}
            for entity_type in self.PII_ENTITIES:
                replacement = self.REPLACEMENT_TOKENS.get(entity_type, f'<{entity_type}>')
                operators[entity_type] = OperatorConfig("replace", {"new_value": replacement})

            anonymized_result = self.anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators
            )

            entities_found = [{
                'type': result.entity_type,
                'start': result.start,
                'end': result.end,
                'score': result.score
            } for result in analyzer_results]

            self.redaction_stats['total_redactions'] += len(entities_found)
            for entity in entities_found:
                entity_type = entity['type']
                self.redaction_stats['by_type'][entity_type] = \
                    self.redaction_stats['by_type'].get(entity_type, 0) + 1

            return anonymized_result.text, {
                'redactions': len(entities_found),
                'entities': entities_found,
                'method': 'presidio'
            }

        except Exception as e:
            logger.error(f"Presidio redaction failed: {e}")
            return self._redact_with_regex(text)

    def _redact_with_regex(self, text: str) -> Tuple[str, Dict]:
        """Redact PII using regex patterns (fallback)"""
        redacted = text
        entities_found = []

        for pattern_name, pattern in self.REGEX_PATTERNS.items():
            matches = list(re.finditer(pattern, redacted, re.IGNORECASE))

            for match in matches:
                entities_found.append({
                    'type': pattern_name,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 1.0
                })

                replacement = self.REPLACEMENT_TOKENS.get(pattern_name, f'<{pattern_name}>')
                redacted = redacted[:match.start()] + replacement + redacted[match.end():]

        self.redaction_stats['total_redactions'] += len(entities_found)
        for entity in entities_found:
            entity_type = entity['type']
            self.redaction_stats['by_type'][entity_type] = \
                self.redaction_stats['by_type'].get(entity_type, 0) + 1

        return redacted, {
            'redactions': len(entities_found),
            'entities': entities_found,
            'method': 'regex'
        }

    def redact_failure_data(self, failure_data: Dict) -> Tuple[Dict, Dict]:
        """
        Redact PII from test failure data

        Redacts: error_message, stack_trace, error_log, test_name
        """
        redacted_data = failure_data.copy()
        all_metadata = {
            'total_redactions': 0,
            'fields_redacted': {}
        }

        fields_to_redact = ['error_message', 'stack_trace', 'error_log', 'test_name']

        for field in fields_to_redact:
            if field in redacted_data and redacted_data[field]:
                original_text = str(redacted_data[field])
                redacted_text, metadata = self.redact(original_text)

                if metadata['redactions'] > 0:
                    redacted_data[field] = redacted_text
                    all_metadata['fields_redacted'][field] = metadata
                    all_metadata['total_redactions'] += metadata['redactions']

        redacted_data['pii_redacted'] = all_metadata['total_redactions'] > 0
        redacted_data['pii_redaction_metadata'] = all_metadata

        return redacted_data, all_metadata

    def get_statistics(self) -> Dict:
        """Get redaction statistics"""
        return {
            'total_redactions': self.redaction_stats['total_redactions'],
            'redactions_by_type': self.redaction_stats['by_type'].copy(),
            'method': 'presidio' if self.use_presidio else 'regex',
            'presidio_available': PRESIDIO_AVAILABLE
        }


# Singleton instance
_pii_redactor = None


def get_pii_redactor(use_presidio: bool = True) -> PIIRedactor:
    """Get singleton PIIRedactor instance"""
    global _pii_redactor
    if _pii_redactor is None:
        _pii_redactor = PIIRedactor(use_presidio=use_presidio)
    return _pii_redactor


if __name__ == '__main__':
    print("=" * 70)
    print("PII Redaction Test - Phase 4, Task 4.1")
    print("=" * 70)

    redactor = PIIRedactor()

    test_cases = [
        "Error: Connection failed to 192.168.1.100 for user john.doe@example.com",
        "API Key: sk_test_1234567890abcdefghijklmnop leaked",
        "SSN 123-45-6789 found in error message",
        "Contact support at +1-555-123-4567"
    ]

    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"  Original: {test_text}")
        redacted, metadata = redactor.redact(test_text)
        print(f"  Redacted: {redacted}")
        print(f"  Found {metadata['redactions']} PII entities")
