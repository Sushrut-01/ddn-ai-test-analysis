"""
Context Engineering Module - Phase 0D Task 0D.1
Created: 2025-11-02

Purpose: Optimize context for AI analysis through:
1. Entity Extraction - Extract key entities (error codes, file paths, line numbers, variables)
2. Token Optimization - Stay within Gemini 4000 token limit
3. Metadata Enrichment - Add contextual metadata for better analysis

Usage:
    from context_engineering import ContextEngineer

    engineer = ContextEngineer()
    optimized = engineer.optimize_context(
        error_log="...",
        error_message="...",
        stack_trace="...",
        error_category="CODE_ERROR"
    )
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class ExtractedEntity:
    """Represents an extracted entity from error logs"""
    entity_type: str  # error_code, file_path, line_number, variable, exception_type
    value: str
    confidence: float = 1.0
    context: Optional[str] = None  # Surrounding text for context


@dataclass
class TokenBudget:
    """Token budget allocation for different context components"""
    max_total: int = 4000  # Gemini limit
    error_message: int = 500
    stack_trace: int = 800
    error_log: int = 1000
    similar_errors: int = 700
    github_code: int = 800
    metadata: int = 200

    def validate(self) -> bool:
        """Ensure budget doesn't exceed max_total"""
        allocated = (self.error_message + self.stack_trace + self.error_log +
                    self.similar_errors + self.github_code + self.metadata)
        return allocated <= self.max_total


@dataclass
class OptimizedContext:
    """Optimized context ready for AI analysis"""
    # Core error information
    error_message: str
    error_category: str
    stack_trace: Optional[str] = None
    error_log: Optional[str] = None

    # Extracted entities
    entities: List[ExtractedEntity] = field(default_factory=list)

    # Enriched metadata
    metadata: Dict = field(default_factory=dict)

    # Token statistics
    total_tokens: int = 0
    token_breakdown: Dict[str, int] = field(default_factory=dict)

    # Optimization stats
    truncated_sections: List[str] = field(default_factory=list)
    optimization_applied: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "error_message": self.error_message,
            "error_category": self.error_category,
            "stack_trace": self.stack_trace,
            "error_log": self.error_log,
            "entities": [
                {
                    "type": e.entity_type,
                    "value": e.value,
                    "confidence": e.confidence,
                    "context": e.context
                }
                for e in self.entities
            ],
            "metadata": self.metadata,
            "total_tokens": self.total_tokens,
            "token_breakdown": self.token_breakdown,
            "truncated_sections": self.truncated_sections,
            "optimization_applied": self.optimization_applied
        }


# ============================================================================
# CONTEXT ENGINEER CLASS
# ============================================================================

class ContextEngineer:
    """
    Main class for context engineering operations

    Responsibilities:
    1. Extract entities from error logs
    2. Optimize token usage
    3. Enrich metadata
    4. Validate context quality
    """

    def __init__(self, token_budget: Optional[TokenBudget] = None):
        """
        Initialize ContextEngineer

        Args:
            token_budget: Custom token budget (uses default if None)
        """
        self.budget = token_budget or TokenBudget()
        if not self.budget.validate():
            logger.warning("Token budget exceeds max_total, using defaults")
            self.budget = TokenBudget()

        # Regex patterns for entity extraction
        self._compile_patterns()

        logger.info("ContextEngineer initialized")
        logger.info(f"  Token budget: {self.budget.max_total} total")

    def _compile_patterns(self):
        """Compile regex patterns for entity extraction"""
        self.patterns = {
            # Error codes: ERR001, E500, ERROR-123, etc.
            'error_code': re.compile(r'\b(?:ERR|ERROR|E)[-_]?\d{3,5}\b', re.IGNORECASE),

            # Exception types: NullPointerException, TypeError, etc.
            'exception_type': re.compile(
                r'\b(?:' +
                '|'.join([
                    r'(?:\w+)?Exception',
                    r'(?:\w+)?Error',
                    r'AssertionFailed',
                    r'Timeout',
                    r'ConnectionRefused'
                ]) +
                r')\b'
            ),

            # File paths: /path/to/file.py, C:\Users\file.java, src/main.js
            'file_path': re.compile(
                r'(?:'
                r'(?:[A-Za-z]:[\\/][\w\\/.-]+)|'  # Windows: C:\path\file.ext
                r'(?:/[\w/.-]+)|'  # Unix: /path/file.ext
                r'(?:[\w]+(?:/[\w.-]+)+)'  # Relative: src/main.js
                r')'
                r'\.(?:py|java|js|jsx|ts|tsx|c|cpp|h|go|rb|php|cs|scala|kt|rs)\b'
            ),

            # Line numbers: at line 42, :123, (line 456)
            'line_number': re.compile(r'(?:line|:|\()\s*(\d{1,5})(?:\)|,|$|\s)', re.IGNORECASE),

            # Variables: variable='value', x=123, name: "test"
            'variable': re.compile(r'\b([a-zA-Z_]\w+)\s*[=:]\s*[\'""]?([^\'"";\n]+)[\'""]?'),

            # Test names: test_login_success, TestUserAuthentication
            'test_name': re.compile(r'\b(?:test_\w+|Test\w+)\b'),

            # HTTP status codes: 404, 500, etc.
            'http_status': re.compile(r'\b(4\d{2}|5\d{2})\b'),

            # IP addresses
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),

            # Timestamps: 2025-11-02 14:30:45, [14:30:45]
            'timestamp': re.compile(
                r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}|'
                r'\[\d{2}:\d{2}:\d{2}\]'
            )
        }

    # ========================================================================
    # ENTITY EXTRACTION
    # ========================================================================

    def extract_entities(self, text: str) -> List[ExtractedEntity]:
        """
        Extract all entities from text

        Args:
            text: Input text (error log, stack trace, etc.)

        Returns:
            List of ExtractedEntity objects
        """
        entities = []

        for entity_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                # Get the matched value (full match or first group)
                value = match.group(1) if match.groups() else match.group(0)

                # Get context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()

                entities.append(ExtractedEntity(
                    entity_type=entity_type,
                    value=value.strip(),
                    confidence=1.0,
                    context=context
                ))

        # Deduplicate entities
        entities = self._deduplicate_entities(entities)

        logger.info(f"Extracted {len(entities)} entities from text")
        return entities

    def _deduplicate_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """Remove duplicate entities, keeping highest confidence"""
        seen = {}
        for entity in entities:
            key = (entity.entity_type, entity.value)
            if key not in seen or entity.confidence > seen[key].confidence:
                seen[key] = entity
        return list(seen.values())

    def extract_critical_entities(self, entities: List[ExtractedEntity]) -> List[ExtractedEntity]:
        """
        Filter to most critical entities for analysis

        Priority order:
        1. Exception types
        2. Error codes
        3. File paths
        4. Line numbers
        5. Test names
        """
        priority_order = [
            'exception_type',
            'error_code',
            'file_path',
            'line_number',
            'test_name',
            'http_status',
            'variable'
        ]

        critical = []
        for entity_type in priority_order:
            matching = [e for e in entities if e.entity_type == entity_type]
            critical.extend(matching[:3])  # Max 3 of each type

        return critical

    # ========================================================================
    # TOKEN OPTIMIZATION
    # ========================================================================

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation: 1 token ≈ 4 chars)

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        # More accurate: split on whitespace and punctuation
        words = re.split(r'\s+|[,.;:()\[\]{}]', text)
        return max(len(text) // 4, len(words))

    def truncate_to_budget(self, text: str, budget: int) -> Tuple[str, bool]:
        """
        Truncate text to fit within token budget

        Strategy:
        1. If under budget, return as-is
        2. Keep first and last portions (error context is often at start/end)
        3. Indicate truncation with marker

        Args:
            text: Input text
            budget: Token budget

        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        if not text:
            return "", False

        current_tokens = self.estimate_tokens(text)
        if current_tokens <= budget:
            return text, False

        # Calculate character budget (tokens * 4)
        char_budget = budget * 4

        # Keep 60% from start, 40% from end (errors often at beginning/end)
        start_chars = int(char_budget * 0.6)
        end_chars = int(char_budget * 0.4)

        # Find good split points (end of line)
        lines = text.split('\n')

        # Get start portion
        start_text = []
        char_count = 0
        for line in lines:
            if char_count + len(line) > start_chars:
                break
            start_text.append(line)
            char_count += len(line) + 1  # +1 for newline

        # Get end portion
        end_text = []
        char_count = 0
        for line in reversed(lines):
            if char_count + len(line) > end_chars:
                break
            end_text.insert(0, line)
            char_count += len(line) + 1

        truncated = (
            '\n'.join(start_text) +
            f"\n\n... [TRUNCATED {len(lines) - len(start_text) - len(end_text)} lines] ...\n\n" +
            '\n'.join(end_text)
        )

        return truncated, True

    def optimize_error_log(self, error_log: str) -> Tuple[str, int]:
        """
        Optimize error log for token efficiency

        Strategy:
        1. Remove timestamps (keep relative timing if needed)
        2. Deduplicate repeated lines
        3. Keep critical error lines
        4. Truncate to budget

        Args:
            error_log: Full error log

        Returns:
            Tuple of (optimized_log, token_count)
        """
        if not error_log:
            return "", 0

        lines = error_log.split('\n')

        # Remove timestamps but keep the content
        cleaned_lines = []
        for line in lines:
            # Remove timestamp patterns
            cleaned = self.patterns['timestamp'].sub('', line).strip()
            if cleaned:  # Only keep non-empty lines
                cleaned_lines.append(cleaned)

        # Deduplicate consecutive identical lines
        deduplicated = []
        prev_line = None
        repeat_count = 0

        for line in cleaned_lines:
            if line == prev_line:
                repeat_count += 1
            else:
                if repeat_count > 1:
                    deduplicated.append(f"... [repeated {repeat_count} times] ...")
                elif prev_line:
                    deduplicated.append(prev_line)
                prev_line = line
                repeat_count = 1

        # Add last line
        if prev_line:
            if repeat_count > 1:
                deduplicated.append(f"... [repeated {repeat_count} times] ...")
            else:
                deduplicated.append(prev_line)

        optimized = '\n'.join(deduplicated)

        # Truncate to budget
        optimized, truncated = self.truncate_to_budget(optimized, self.budget.error_log)

        tokens = self.estimate_tokens(optimized)
        return optimized, tokens

    # ========================================================================
    # METADATA ENRICHMENT
    # ========================================================================

    def enrich_metadata(
        self,
        error_category: str,
        entities: List[ExtractedEntity],
        error_message: str,
        stack_trace: Optional[str] = None
    ) -> Dict:
        """
        Enrich context with metadata for better analysis

        Args:
            error_category: Error category (CODE_ERROR, INFRA_ERROR, etc.)
            entities: Extracted entities
            error_message: Error message
            stack_trace: Stack trace (optional)

        Returns:
            Dictionary of enriched metadata
        """
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'error_category': error_category,
            'entity_counts': {},
            'key_indicators': [],
            'severity_hints': [],
            'analysis_hints': []
        }

        # Count entities by type
        for entity in entities:
            entity_type = entity.entity_type
            metadata['entity_counts'][entity_type] = \
                metadata['entity_counts'].get(entity_type, 0) + 1

        # Extract key indicators
        exception_types = [e.value for e in entities if e.entity_type == 'exception_type']
        if exception_types:
            metadata['key_indicators'].append(f"Exception: {', '.join(set(exception_types[:3]))}")

        file_paths = [e.value for e in entities if e.entity_type == 'file_path']
        if file_paths:
            metadata['key_indicators'].append(f"Files: {len(file_paths)} referenced")

        # Add severity hints based on error patterns
        if 'NullPointerException' in error_message or 'NPE' in error_message:
            metadata['severity_hints'].append("High: Null reference - likely to cause test failures")

        if 'OutOfMemoryError' in error_message or 'OOM' in error_message:
            metadata['severity_hints'].append("Critical: Memory exhaustion - system stability risk")

        if 'timeout' in error_message.lower():
            metadata['severity_hints'].append("Medium: Timeout - may be transient")

        # Add analysis hints based on category
        if error_category == 'CODE_ERROR':
            metadata['analysis_hints'].append("Check source code and recent changes")
            metadata['analysis_hints'].append("Review GitHub commit history")
        elif error_category == 'INFRA_ERROR':
            metadata['analysis_hints'].append("Check system resources (CPU, memory, disk)")
            metadata['analysis_hints'].append("Review infrastructure logs")
        elif error_category == 'CONFIG_ERROR':
            metadata['analysis_hints'].append("Verify configuration files and environment variables")

        # Add stack depth if available
        if stack_trace:
            stack_lines = stack_trace.split('\n')
            metadata['stack_depth'] = len([l for l in stack_lines if l.strip().startswith('at ')])

        return metadata

    # ========================================================================
    # MAIN OPTIMIZATION FUNCTION
    # ========================================================================

    def optimize_context(
        self,
        error_log: str,
        error_message: str,
        error_category: str,
        stack_trace: Optional[str] = None,
        similar_errors: Optional[List[Dict]] = None,
        github_code: Optional[str] = None
    ) -> OptimizedContext:
        """
        Main function to optimize entire context for AI analysis

        Args:
            error_log: Full error log
            error_message: Error message
            error_category: Error category
            stack_trace: Stack trace (optional)
            similar_errors: Similar errors from RAG (optional)
            github_code: GitHub code context (optional)

        Returns:
            OptimizedContext object with all optimizations applied
        """
        logger.info(f"Optimizing context for category: {error_category}")

        context = OptimizedContext(
            error_message=error_message,
            error_category=error_category
        )

        # 1. Extract entities from all sources
        all_text = f"{error_message}\n{error_log or ''}\n{stack_trace or ''}"
        entities = self.extract_entities(all_text)
        context.entities = self.extract_critical_entities(entities)

        # 2. Optimize each component to fit token budget
        token_breakdown = {}

        # Error message (always keep, but truncate if needed)
        error_msg_optimized, truncated = self.truncate_to_budget(
            error_message,
            self.budget.error_message
        )
        context.error_message = error_msg_optimized
        token_breakdown['error_message'] = self.estimate_tokens(error_msg_optimized)
        if truncated:
            context.truncated_sections.append('error_message')

        # Stack trace
        if stack_trace:
            stack_optimized, truncated = self.truncate_to_budget(
                stack_trace,
                self.budget.stack_trace
            )
            context.stack_trace = stack_optimized
            token_breakdown['stack_trace'] = self.estimate_tokens(stack_optimized)
            if truncated:
                context.truncated_sections.append('stack_trace')

        # Error log (most aggressive optimization)
        if error_log:
            log_optimized, tokens = self.optimize_error_log(error_log)
            context.error_log = log_optimized
            token_breakdown['error_log'] = tokens
            if self.estimate_tokens(error_log) != tokens:
                context.truncated_sections.append('error_log')

        # Similar errors (if provided)
        if similar_errors:
            similar_text = json.dumps(similar_errors, indent=2)
            similar_optimized, truncated = self.truncate_to_budget(
                similar_text,
                self.budget.similar_errors
            )
            token_breakdown['similar_errors'] = self.estimate_tokens(similar_optimized)
            if truncated:
                context.truncated_sections.append('similar_errors')

        # GitHub code (if provided)
        if github_code:
            code_optimized, truncated = self.truncate_to_budget(
                github_code,
                self.budget.github_code
            )
            token_breakdown['github_code'] = self.estimate_tokens(code_optimized)
            if truncated:
                context.truncated_sections.append('github_code')

        # 3. Enrich metadata
        context.metadata = self.enrich_metadata(
            error_category,
            context.entities,
            error_message,
            stack_trace
        )
        token_breakdown['metadata'] = self.estimate_tokens(json.dumps(context.metadata))

        # 4. Calculate total tokens
        context.total_tokens = sum(token_breakdown.values())
        context.token_breakdown = token_breakdown
        context.optimization_applied = len(context.truncated_sections) > 0

        # 5. Log optimization results
        logger.info(f"Context optimization complete:")
        logger.info(f"  Total tokens: {context.total_tokens}/{self.budget.max_total}")
        logger.info(f"  Entities extracted: {len(context.entities)}")
        logger.info(f"  Truncated sections: {context.truncated_sections or 'None'}")
        logger.info(f"  Token breakdown: {token_breakdown}")

        return context

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def validate_context(self, context: OptimizedContext) -> Tuple[bool, List[str]]:
        """
        Validate optimized context quality

        Returns:
            Tuple of (is_valid, warnings)
        """
        warnings = []

        # Check token budget
        if context.total_tokens > self.budget.max_total:
            warnings.append(f"Token count ({context.total_tokens}) exceeds budget ({self.budget.max_total})")

        # Check for critical entities
        if not context.entities:
            warnings.append("No entities extracted - context may lack specificity")

        # Check for excessive truncation
        if len(context.truncated_sections) > 3:
            warnings.append(f"Many sections truncated ({len(context.truncated_sections)}) - information loss possible")

        # Validate error message exists
        if not context.error_message or len(context.error_message.strip()) < 10:
            warnings.append("Error message too short or missing")

        is_valid = len(warnings) == 0
        return is_valid, warnings

    def format_for_gemini(self, context: OptimizedContext) -> str:
        """
        Format optimized context for Gemini prompt

        Returns:
            Formatted string ready for AI analysis
        """
        sections = []

        # Header
        sections.append(f"# Error Analysis Context (Category: {context.error_category})")
        sections.append(f"# Total Tokens: {context.total_tokens}")
        sections.append("")

        # Error Message
        sections.append("## Error Message")
        sections.append(context.error_message)
        sections.append("")

        # Key Entities
        if context.entities:
            sections.append("## Extracted Entities")
            for entity in context.entities[:10]:  # Top 10
                sections.append(f"- {entity.entity_type}: {entity.value}")
            sections.append("")

        # Stack Trace
        if context.stack_trace:
            sections.append("## Stack Trace")
            sections.append(context.stack_trace)
            sections.append("")

        # Error Log
        if context.error_log:
            sections.append("## Error Log")
            sections.append(context.error_log)
            sections.append("")

        # Metadata
        if context.metadata.get('key_indicators'):
            sections.append("## Key Indicators")
            for indicator in context.metadata['key_indicators']:
                sections.append(f"- {indicator}")
            sections.append("")

        if context.metadata.get('analysis_hints'):
            sections.append("## Analysis Hints")
            for hint in context.metadata['analysis_hints']:
                sections.append(f"- {hint}")
            sections.append("")

        return '\n'.join(sections)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_context_engineer(token_budget: Optional[TokenBudget] = None) -> ContextEngineer:
    """
    Factory function to create ContextEngineer instance

    Args:
        token_budget: Optional custom token budget

    Returns:
        ContextEngineer instance
    """
    return ContextEngineer(token_budget)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ContextEngineer',
    'OptimizedContext',
    'ExtractedEntity',
    'TokenBudget',
    'create_context_engineer'
]


if __name__ == '__main__':
    # Example usage
    engineer = create_context_engineer()

    # Test with sample error
    sample_error_log = """
2025-11-02 14:30:45 ERROR: Test failed at line 123 in src/main/java/TestRunner.java
java.lang.NullPointerException: Cannot invoke method on null object
    at com.example.TestRunner.executeTest(TestRunner.java:123)
    at com.example.TestSuite.run(TestSuite.java:45)
2025-11-02 14:30:46 ERROR: Previous error at ERR-500
2025-11-02 14:30:47 ERROR: Connection timeout after 30 seconds
    """

    sample_message = "NullPointerException at TestRunner.java:123"

    optimized = engineer.optimize_context(
        error_log=sample_error_log,
        error_message=sample_message,
        error_category="CODE_ERROR",
        stack_trace="at TestRunner.java:123\nat TestSuite.java:45"
    )

    print("\n=== OPTIMIZATION RESULTS ===")
    print(f"Total tokens: {optimized.total_tokens}")
    print(f"Entities: {len(optimized.entities)}")
    print(f"Truncated: {optimized.truncated_sections}")
    print("\n=== FORMATTED FOR GEMINI ===")
    print(engineer.format_for_gemini(optimized))

    # Validate
    is_valid, warnings = engineer.validate_context(optimized)
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
