"""
Prompt Templates Module - Phase 0D Task 0D.2
Created: 2025-11-02

Purpose: Category-specific prompt templates for Gemini AI analysis
- Integrates with context_engineering.py (uses OptimizedContext)
- Provides few-shot examples for each error category
- Generates dynamic prompts based on error context
- Optimized for Gemini API token limits

Usage:
    from prompt_templates import PromptTemplateGenerator
    from context_engineering import ContextEngineer

    engineer = ContextEngineer()
    optimized_ctx = engineer.optimize_context(...)

    generator = PromptTemplateGenerator()
    prompt = generator.generate_analysis_prompt(optimized_ctx)
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# Import context engineering (Task 0D.1)
try:
    from context_engineering import OptimizedContext, ExtractedEntity
    CONTEXT_ENG_AVAILABLE = True
except ImportError:
    CONTEXT_ENG_AVAILABLE = False
    logging.warning("context_engineering not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class FewShotExample:
    """A few-shot example for a specific error category"""
    error_category: str
    error_summary: str
    error_message: str
    key_entities: List[str]  # Extracted entities
    analysis: str  # Expected AI output
    root_cause: str
    fix_recommendation: str


@dataclass
class PromptTemplate:
    """A prompt template for a specific error category"""
    category: str
    system_instruction: str
    analysis_guidelines: List[str]
    few_shot_examples: List[FewShotExample] = field(default_factory=list)
    output_format: str = ""


# ============================================================================
# FEW-SHOT EXAMPLES DATABASE
# ============================================================================

# CODE_ERROR Examples
CODE_ERROR_EXAMPLES = [
    FewShotExample(
        error_category="CODE_ERROR",
        error_summary="NullPointerException in user authentication service",
        error_message="java.lang.NullPointerException at UserService.authenticate(UserService.java:142)",
        key_entities=["NullPointerException", "UserService.java", "line 142", "authenticate()"],
        analysis="""The error occurs in the authenticate method when attempting to access a null User object.

The stack trace points to line 142 in UserService.java where the code likely tries to call a method
on a User object that hasn't been properly initialized or retrieved from the database.""",
        root_cause="Null User object not properly validated before method invocation",
        fix_recommendation="""Add null check before accessing User object:

```java
if (user == null) {
    throw new AuthenticationException("User not found");
}
```

Also verify database query is returning expected results."""
    ),
    FewShotExample(
        error_category="CODE_ERROR",
        error_summary="Array index out of bounds in data processor",
        error_message="IndexError: list index out of range at process_data.py:87",
        key_entities=["IndexError", "process_data.py", "line 87", "list index"],
        analysis="""The code is attempting to access a list element at an index that doesn't exist.

This typically happens when:
1. Loop counter exceeds list length
2. Hardcoded index assumes list size
3. Empty list not handled""",
        root_cause="Accessing list index without bounds checking",
        fix_recommendation="""Add bounds checking:

```python
if len(data_list) > index:
    value = data_list[index]
else:
    # Handle error case
```

Or use safer iteration methods like enumerate() or for-each loops."""
    ),
]

# INFRA_ERROR Examples
INFRA_ERROR_EXAMPLES = [
    FewShotExample(
        error_category="INFRA_ERROR",
        error_summary="OutOfMemoryError during batch processing",
        error_message="java.lang.OutOfMemoryError: Java heap space",
        key_entities=["OutOfMemoryError", "heap space", "batch processing"],
        analysis="""The JVM ran out of heap memory during batch processing operations.

Common causes:
1. Processing too many records in memory at once
2. Memory leak from unclosed resources
3. Insufficient heap size configuration""",
        root_cause="Heap size too small for batch processing workload OR memory leak",
        fix_recommendation="""1. Increase JVM heap size: -Xmx4096m
2. Process data in smaller batches
3. Use streaming/pagination for large datasets
4. Check for unclosed database connections or file handles
5. Profile with jmap/jvisualvm to identify memory leaks"""
    ),
    FewShotExample(
        error_category="INFRA_ERROR",
        error_summary="Connection timeout to database",
        error_message="java.sql.SQLException: Connection timeout after 30 seconds",
        key_entities=["SQLException", "Connection timeout", "30 seconds"],
        analysis="""Database connection timed out after 30 seconds.

Possible causes:
1. Database server is down or unreachable
2. Network issues
3. Connection pool exhausted
4. Firewall blocking connection""",
        root_cause="Unable to establish database connection within timeout period",
        fix_recommendation="""1. Verify database server is running: pg_isready -h hostname
2. Check network connectivity: ping hostname
3. Review connection pool settings (max connections)
4. Increase timeout if needed: connection.timeout=60
5. Check database server logs for errors"""
    ),
]

# CONFIG_ERROR Examples
CONFIG_ERROR_EXAMPLES = [
    FewShotExample(
        error_category="CONFIG_ERROR",
        error_summary="Invalid database URL configuration",
        error_message="ConfigurationException: Invalid database URL: jdbc:postgresql://localhost",
        key_entities=["ConfigurationException", "database URL", "jdbc:postgresql"],
        analysis="""The database URL is malformed - missing port and database name.

A valid PostgreSQL JDBC URL should include:
- Protocol: jdbc:postgresql://
- Host: localhost
- Port: 5432
- Database: /dbname""",
        root_cause="Incomplete database URL in configuration file",
        fix_recommendation="""Update database URL in application.properties:

```properties
database.url=jdbc:postgresql://localhost:5432/mydatabase
```

Full format: jdbc:postgresql://[host]:[port]/[database]"""
    ),
]

# DEPENDENCY_ERROR Examples
DEPENDENCY_ERROR_EXAMPLES = [
    FewShotExample(
        error_category="DEPENDENCY_ERROR",
        error_summary="Missing Python module",
        error_message="ModuleNotFoundError: No module named 'requests'",
        key_entities=["ModuleNotFoundError", "requests", "Python"],
        analysis="""The 'requests' module is not installed in the Python environment.

This is a missing dependency issue - the code imports a library that hasn't been installed.""",
        root_cause="Missing Python package 'requests'",
        fix_recommendation="""Install the missing package:

```bash
pip install requests
```

Add to requirements.txt to prevent future issues:
```
requests==2.31.0
```"""
    ),
]

# TEST_ERROR Examples
TEST_ERROR_EXAMPLES = [
    FewShotExample(
        error_category="TEST_ERROR",
        error_summary="Test assertion failed - expected value mismatch",
        error_message="AssertionError: Expected 5 but got 3",
        key_entities=["AssertionError", "Expected 5", "got 3"],
        analysis="""Test assertion failed due to value mismatch.

The test expected a return value of 5 but the actual result was 3.
This indicates either:
1. The function logic is incorrect
2. The test expectations are wrong
3. Test data doesn't match production scenario""",
        root_cause="Function returned 3 instead of expected 5",
        fix_recommendation="""1. Review function logic to understand why it returns 3
2. Verify test expectations are correct
3. Check if test data/mocks are set up properly
4. Add debugging to see intermediate values"""
    ),
]


# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

class PromptTemplateGenerator:
    """
    Generates category-specific prompts for Gemini AI analysis

    Integrates with:
    - context_engineering.py (OptimizedContext)
    - Few-shot examples for each category
    - Dynamic prompt generation based on error context
    """

    def __init__(self):
        """Initialize prompt template generator"""
        self.templates = self._initialize_templates()
        logger.info("PromptTemplateGenerator initialized")
        logger.info(f"  {len(self.templates)} category templates loaded")

    def _initialize_templates(self) -> Dict[str, PromptTemplate]:
        """Initialize all category templates with few-shot examples"""
        return {
            "CODE_ERROR": PromptTemplate(
                category="CODE_ERROR",
                system_instruction="""You are an expert software engineer analyzing a CODE_ERROR (source code bug).

Your task is to provide a detailed root cause analysis and actionable fix recommendations.""",
                analysis_guidelines=[
                    "Identify the exact line/file where the error occurs",
                    "Explain what the error message means in plain terms",
                    "Determine the root cause (not just the symptom)",
                    "Consider common code patterns that cause this error type",
                    "Look for related code in the GitHub context if provided",
                    "Provide specific, actionable fix recommendations with code examples",
                ],
                few_shot_examples=CODE_ERROR_EXAMPLES,
                output_format="""Provide analysis in this structure:
1. **Error Summary**: Brief description of what went wrong
2. **Root Cause**: Underlying issue causing the error
3. **Fix Recommendation**: Specific steps to fix, with code examples
4. **Related Files**: Other files that may need changes
5. **Testing Notes**: How to verify the fix works"""
            ),

            "INFRA_ERROR": PromptTemplate(
                category="INFRA_ERROR",
                system_instruction="""You are an expert DevOps engineer analyzing an INFRA_ERROR (infrastructure/system issue).

Your task is to diagnose system-level problems and provide operational recommendations.""",
                analysis_guidelines=[
                    "Identify which system resource is failing (memory, disk, network, CPU)",
                    "Determine if this is transient or persistent",
                    "Consider system capacity and scaling issues",
                    "Look for resource exhaustion patterns",
                    "Check for environmental differences (dev vs prod)",
                    "Provide both immediate fixes and long-term solutions",
                ],
                few_shot_examples=INFRA_ERROR_EXAMPLES,
                output_format="""Provide analysis in this structure:
1. **System Impact**: What system resources are affected
2. **Root Cause**: Why the system is failing
3. **Immediate Fix**: Quick mitigation steps
4. **Long-term Solution**: Permanent fix (scaling, configuration)
5. **Monitoring**: What to monitor to prevent recurrence"""
            ),

            "CONFIG_ERROR": PromptTemplate(
                category="CONFIG_ERROR",
                system_instruction="""You are an expert system administrator analyzing a CONFIG_ERROR (configuration issue).

Your task is to identify configuration problems and provide correct settings.""",
                analysis_guidelines=[
                    "Identify which configuration file/setting is wrong",
                    "Explain what the correct format/value should be",
                    "Consider environment-specific configuration",
                    "Check for missing required settings",
                    "Look for conflicting configuration values",
                    "Provide exact configuration snippets",
                ],
                few_shot_examples=CONFIG_ERROR_EXAMPLES,
                output_format="""Provide analysis in this structure:
1. **Configuration Issue**: What setting is wrong or missing
2. **Correct Configuration**: Exact correct value/format
3. **Configuration File**: Which file to update
4. **Verification Steps**: How to verify the fix
5. **Related Settings**: Other settings that may need updating"""
            ),

            "DEPENDENCY_ERROR": PromptTemplate(
                category="DEPENDENCY_ERROR",
                system_instruction="""You are an expert dependency manager analyzing a DEPENDENCY_ERROR (missing/conflicting dependency).

Your task is to resolve dependency issues and version conflicts.""",
                analysis_guidelines=[
                    "Identify which dependency is missing or conflicting",
                    "Determine the correct version needed",
                    "Check for transitive dependency conflicts",
                    "Consider compatibility with other dependencies",
                    "Provide exact installation commands",
                    "Update dependency manifest files",
                ],
                few_shot_examples=DEPENDENCY_ERROR_EXAMPLES,
                output_format="""Provide analysis in this structure:
1. **Missing Dependency**: What package/library is needed
2. **Installation Command**: Exact command to install
3. **Version Compatibility**: Recommended version and why
4. **Dependency File Update**: Changes to requirements.txt/pom.xml/package.json
5. **Verification**: How to verify dependency is working"""
            ),

            "TEST_ERROR": PromptTemplate(
                category="TEST_ERROR",
                system_instruction="""You are an expert QA engineer analyzing a TEST_ERROR (test failure/assertion issue).

Your task is to determine why tests are failing and how to fix them.""",
                analysis_guidelines=[
                    "Determine if test expectations are correct",
                    "Check if production code logic is wrong",
                    "Look for test data/mock setup issues",
                    "Consider timing/race conditions in tests",
                    "Identify flaky vs consistent failures",
                    "Provide fixes for both test and production code",
                ],
                few_shot_examples=TEST_ERROR_EXAMPLES,
                output_format="""Provide analysis in this structure:
1. **Test Failure**: What assertion/expectation failed
2. **Actual vs Expected**: What happened vs what should happen
3. **Root Cause**: Is the test wrong or the code wrong?
4. **Fix Recommendation**: How to fix (test or code)
5. **Test Improvements**: How to make test more robust"""
            ),

            "UNKNOWN_ERROR": PromptTemplate(
                category="UNKNOWN_ERROR",
                system_instruction="""You are an expert debugger analyzing an error that doesn't fit standard categories.

Your task is to classify the error and provide general troubleshooting guidance.""",
                analysis_guidelines=[
                    "Attempt to categorize the error (code/infra/config/dependency/test)",
                    "Focus on the error message and stack trace",
                    "Provide general debugging steps",
                    "Suggest what additional information would help",
                    "Consider multiple possible root causes",
                ],
                few_shot_examples=[],
                output_format="""Provide analysis in this structure:
1. **Error Classification**: Best guess at error type
2. **Possible Causes**: Multiple theories about the root cause
3. **Debugging Steps**: What to check next
4. **Additional Info Needed**: What data would help diagnose
5. **General Recommendations**: Safe steps to try"""
            ),
        }

    def generate_analysis_prompt(
        self,
        optimized_context: 'OptimizedContext',
        include_few_shot: bool = True,
        max_examples: int = 2
    ) -> str:
        """
        Generate complete analysis prompt for Gemini

        Args:
            optimized_context: OptimizedContext from context_engineering.py
            include_few_shot: Whether to include few-shot examples
            max_examples: Maximum number of examples to include

        Returns:
            Complete prompt string ready for Gemini
        """
        if not CONTEXT_ENG_AVAILABLE:
            raise ImportError("context_engineering module not available")

        category = optimized_context.error_category
        template = self.templates.get(category, self.templates["UNKNOWN_ERROR"])

        logger.info(f"Generating prompt for category: {category}")

        # Build prompt sections
        sections = []

        # 1. System Instruction
        sections.append(template.system_instruction)
        sections.append("")

        # 2. Few-Shot Examples (if requested)
        if include_few_shot and template.few_shot_examples:
            sections.append("# Examples of Similar Error Analysis\n")
            for i, example in enumerate(template.few_shot_examples[:max_examples], 1):
                sections.append(f"## Example {i}")
                sections.append(f"**Error:** {example.error_message}")
                sections.append(f"**Key Entities:** {', '.join(example.key_entities)}")
                sections.append(f"\n**Analysis:**\n{example.analysis}")
                sections.append(f"\n**Root Cause:** {example.root_cause}")
                sections.append(f"\n**Fix:** {example.fix_recommendation}")
                sections.append("\n" + "-" * 80 + "\n")

        # 3. Analysis Guidelines
        sections.append("# Analysis Guidelines\n")
        for guideline in template.analysis_guidelines:
            sections.append(f"- {guideline}")
        sections.append("")

        # 4. Error Context (from OptimizedContext)
        sections.append("# Error Context to Analyze\n")

        # Error message
        sections.append("## Error Message")
        sections.append(optimized_context.error_message)
        sections.append("")

        # Extracted Entities
        if optimized_context.entities:
            sections.append("## Extracted Key Entities")
            entity_groups = {}
            for entity in optimized_context.entities[:15]:  # Top 15
                if entity.entity_type not in entity_groups:
                    entity_groups[entity.entity_type] = []
                entity_groups[entity.entity_type].append(entity.value)

            for entity_type, values in entity_groups.items():
                sections.append(f"- **{entity_type}**: {', '.join(values[:5])}")  # Max 5 per type
            sections.append("")

        # Stack Trace
        if optimized_context.stack_trace:
            sections.append("## Stack Trace")
            sections.append("```")
            sections.append(optimized_context.stack_trace)
            sections.append("```")
            sections.append("")

        # Error Log
        if optimized_context.error_log:
            sections.append("## Error Log (Optimized)")
            sections.append("```")
            sections.append(optimized_context.error_log)
            sections.append("```")
            sections.append("")

        # Metadata Hints
        if optimized_context.metadata.get('analysis_hints'):
            sections.append("## Analysis Hints")
            for hint in optimized_context.metadata['analysis_hints']:
                sections.append(f"- {hint}")
            sections.append("")

        if optimized_context.metadata.get('severity_hints'):
            sections.append("## Severity Indicators")
            for hint in optimized_context.metadata['severity_hints']:
                sections.append(f"- {hint}")
            sections.append("")

        # 5. Output Format
        sections.append("# Required Output Format\n")
        sections.append(template.output_format)
        sections.append("")

        # 6. Additional Instructions
        sections.append("# Final Instructions\n")
        sections.append(f"- Total context tokens: {optimized_context.total_tokens}")
        if optimized_context.truncated_sections:
            sections.append(f"- Note: Following sections were truncated: {', '.join(optimized_context.truncated_sections)}")
        sections.append("- Provide specific, actionable recommendations")
        sections.append("- Use code examples where helpful")
        sections.append("- Be concise but thorough")

        prompt = '\n'.join(sections)

        logger.info(f"Prompt generated: {len(prompt)} chars")
        return prompt

    def generate_simple_prompt(
        self,
        error_message: str,
        error_category: str,
        stack_trace: Optional[str] = None
    ) -> str:
        """
        Generate simple prompt without OptimizedContext (fallback)

        Args:
            error_message: Error message
            error_category: Error category
            stack_trace: Stack trace (optional)

        Returns:
            Simple prompt string
        """
        template = self.templates.get(error_category, self.templates["UNKNOWN_ERROR"])

        sections = []
        sections.append(template.system_instruction)
        sections.append("")
        sections.append("# Error to Analyze\n")
        sections.append(f"**Error Message:** {error_message}")

        if stack_trace:
            sections.append("\n**Stack Trace:**")
            sections.append("```")
            sections.append(stack_trace)
            sections.append("```")

        sections.append("\n" + template.output_format)

        return '\n'.join(sections)

    def get_template(self, category: str) -> PromptTemplate:
        """Get template for specific category"""
        return self.templates.get(category, self.templates["UNKNOWN_ERROR"])

    def list_categories(self) -> List[str]:
        """List all available categories"""
        return list(self.templates.keys())


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_prompt_generator() -> PromptTemplateGenerator:
    """Factory function to create PromptTemplateGenerator"""
    return PromptTemplateGenerator()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'PromptTemplateGenerator',
    'PromptTemplate',
    'FewShotExample',
    'create_prompt_generator'
]


if __name__ == '__main__':
    # Example usage
    generator = create_prompt_generator()

    print("\n=== AVAILABLE CATEGORIES ===")
    for category in generator.list_categories():
        template = generator.get_template(category)
        example_count = len(template.few_shot_examples)
        print(f"{category}: {example_count} few-shot examples")

    # Test simple prompt generation
    print("\n=== SAMPLE SIMPLE PROMPT ===")
    simple_prompt = generator.generate_simple_prompt(
        error_message="NullPointerException at TestRunner.java:123",
        error_category="CODE_ERROR",
        stack_trace="at TestRunner.java:123\nat TestSuite.java:45"
    )
    print(simple_prompt[:500] + "...\n")

    print("Prompt template generator ready!")
