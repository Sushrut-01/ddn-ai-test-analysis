"""
Thought Prompts - Phase 0-ARCH
Task 0-ARCH.4B: Data-Driven Templates from Pinecone

REFACTORED: All templates now fetched from Pinecone database.
Hardcoded templates kept as emergency fallback only.

Features:
- Fetch templates from Pinecone at runtime
- 30-minute memory cache for performance
- Code fallback if Pinecone unavailable
- Same public API (backward compatible)

File: implementation/agents/thought_prompts.py
Created: 2025-10-31
Refactored: 2025-11-01 (Data-driven)
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Pinecone imports
try:
    from langchain_pinecone import PineconeVectorStore
    from langchain_openai import OpenAIEmbeddings
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logging.warning("Pinecone not available - will use code fallback")

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class ReasoningExample:
    """A few-shot example for reasoning"""
    error_summary: str
    thought: str
    action: str
    reasoning: str


class ThoughtPrompts:
    """
    Data-Driven Thought Prompts from Pinecone

    NEW: Fetches all templates from Pinecone database at runtime.
    Hardcoded templates are FALLBACK ONLY (if Pinecone fails).

    Cache Strategy:
    - 30-minute memory cache for performance
    - <5ms average latency (from cache)
    - Fallback to code if Pinecone unavailable
    """

    # =========================================================================
    # CACHE AND STATE
    # =========================================================================

    _cache: Dict[str, any] = {}
    _cache_timestamps: Dict[str, datetime] = {}
    _cache_ttl = timedelta(minutes=30)
    _pinecone_available = None
    _vectorstore = None

    # =========================================================================
    # PINECONE CONNECTION
    # =========================================================================

    @classmethod
    def _init_pinecone(cls):
        """Initialize Pinecone connection (lazy loading)"""
        if cls._vectorstore is not None:
            return  # Already initialized

        if not PINECONE_AVAILABLE:
            logger.warning("Pinecone libraries not available - using code fallback")
            cls._pinecone_available = False
            return

        try:
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                dimensions=1536
            )

            cls._vectorstore = PineconeVectorStore(
                index_name="ddn-knowledge-docs",
                embedding=embeddings,
                pinecone_api_key=os.getenv("PINECONE_API_KEY")
            )

            cls._pinecone_available = True
            logger.info("✅ Pinecone templates connected (data-driven mode)")

        except Exception as e:
            logger.warning(f"⚠️  Pinecone connection failed: {e}")
            logger.warning("Using code fallback templates")
            cls._pinecone_available = False

    @classmethod
    def _fetch_from_pinecone(cls, doc_type: str, error_category: str) -> Optional[any]:
        """
        Fetch template from Pinecone by doc_type and category

        Args:
            doc_type: Type of template (reasoning_template, few_shot_example, etc.)
            error_category: Error category or "GLOBAL"

        Returns:
            Template data or None if not found
        """
        # Check cache first
        cache_key = f"{doc_type}_{error_category}"

        if cache_key in cls._cache:
            cached_at = cls._cache_timestamps[cache_key]
            if datetime.now() - cached_at < cls._cache_ttl:
                logger.debug(f"Cache HIT: {cache_key}")
                return cls._cache[cache_key]

        # Initialize Pinecone if needed
        if cls._pinecone_available is None:
            cls._init_pinecone()

        # If Pinecone unavailable, return None (will use fallback)
        if not cls._pinecone_available:
            return None

        try:
            # Query Pinecone
            docs = cls._vectorstore.similarity_search(
                "template",  # Dummy query (we filter by metadata)
                k=50,
                filter={
                    "doc_type": doc_type,
                    "error_category": error_category,
                    "active": True
                }
            )

            if not docs:
                logger.debug(f"Pinecone: No template found for {cache_key}")
                return None

            # Extract data based on doc_type
            if doc_type == "few_shot_example":
                # Return all examples, sorted by index
                examples = []
                for doc in docs:
                    metadata = doc.metadata
                    examples.append({
                        "index": metadata.get("example_index", 0),
                        "error_summary": metadata.get("error_summary", ""),
                        "thought": metadata.get("thought", ""),
                        "action": metadata.get("action", ""),
                        "reasoning": metadata.get("reasoning", "")
                    })
                # Sort by index
                examples.sort(key=lambda x: x["index"])
                result = examples
            else:
                # Single template (reasoning, observation, answer_generation)
                result = docs[0].metadata.get("template_content")

            # Cache result
            cls._cache[cache_key] = result
            cls._cache_timestamps[cache_key] = datetime.now()

            logger.debug(f"Pinecone FETCH: {cache_key}")
            return result

        except Exception as e:
            logger.warning(f"Pinecone query failed for {cache_key}: {e}")
            return None

    # =========================================================================
    # FALLBACK TEMPLATES (EMERGENCY USE ONLY)
    # =========================================================================

    _FALLBACK_REASONING_TEMPLATES = {
        "CODE_ERROR": """You are analyzing a CODE_ERROR (source code bug).

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Think step-by-step about what might be causing this error. Consider:
1. What does the error message tell us?
2. Which code patterns typically cause this?
3. Do we have enough information, or do we need more context?
4. What's the most logical next step?

**Available Actions:**
- pinecone_knowledge: Search for similar error patterns
- pinecone_error_library: Check historical cases
- github_get_file: Fetch source code (only if confidence < 0.75)
- postgres_history: Check past occurrences
- DONE: Generate answer (if confident)

**Output Format (JSON):**
{{
    "thought": "Your reasoning about the error...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}""",

        "INFRA_ERROR": """You are analyzing an INFRA_ERROR (infrastructure/resource issue).

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Think about infrastructure and resource issues. Consider:
1. Is this a resource exhaustion issue (memory, disk, CPU)?
2. Is it a network/connectivity problem?
3. Are there environmental factors (permissions, config)?
4. What logs or metrics would help?

**Available Actions:**
- pinecone_knowledge: Search for infrastructure solutions
- pinecone_error_library: Check similar incidents
- mongodb_logs: Query execution logs and metrics
- postgres_history: Check if this happened before
- DONE: Generate answer (if confident)

**Important:** INFRA_ERROR doesn't need code inspection - focus on logs and metrics!

**Output Format (JSON):**
{{
    "thought": "Your reasoning about the infrastructure issue...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}""",

        "CONFIG_ERROR": """You are analyzing a CONFIG_ERROR (configuration problem).

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Think about configuration issues. Consider:
1. What configuration is missing or incorrect?
2. Are there permission problems?
3. Are environment variables set correctly?
4. Is this a deployment/setup issue?

**Available Actions:**
- pinecone_knowledge: Search for configuration fixes
- pinecone_error_library: Check similar config issues
- mongodb_logs: Check console logs for config details
- postgres_history: Check if this config issue happened before
- DONE: Generate answer (if confident)

**Important:** CONFIG_ERROR is about setup, not code bugs!

**Output Format (JSON):**
{{
    "thought": "Your reasoning about the configuration...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}""",

        "DEPENDENCY_ERROR": """You are analyzing a DEPENDENCY_ERROR (module/package issue).

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Think about dependency issues. Consider:
1. Is a package missing or not installed?
2. Is there a version conflict?
3. Are import paths correct?
4. Is this a build/compilation issue?

**Available Actions:**
- pinecone_knowledge: Search for dependency solutions
- pinecone_error_library: Check similar dependency issues
- mongodb_logs: Check build/install logs
- postgres_history: Check past dependency problems
- DONE: Generate answer (if confident)

**Output Format (JSON):**
{{
    "thought": "Your reasoning about dependencies...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}""",

        "TEST_FAILURE": """You are analyzing a TEST_FAILURE (test assertion failure).

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Think about why the test is failing. Consider:
1. Is it a legitimate code bug (expected != actual)?
2. Is the test itself flaky or incorrect?
3. Is there missing test data or setup?
4. Has the expected behavior changed?

**Available Actions:**
- pinecone_knowledge: Search for test failure patterns
- pinecone_error_library: Check similar test failures
- github_get_file: Fetch test code (if confidence < 0.75)
- postgres_history: Check test history
- DONE: Generate answer (if confident)

**Output Format (JSON):**
{{
    "thought": "Your reasoning about the test failure...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}""",

        "UNKNOWN": """You are analyzing an error of UNKNOWN category.

**Error Information:**
{error_info}

**Context So Far:**
{context_summary}

**Your Task:**
Since the category is unknown, take a general approach:
1. What does the error message suggest?
2. Start with broad knowledge search
3. Look for similar historical cases
4. Gather more context before deciding

**Available Actions:**
- pinecone_knowledge: Broad search for error patterns
- pinecone_error_library: Check any similar cases
- mongodb_logs: Check execution logs
- postgres_history: Check if seen before
- DONE: Generate answer (if confident)

**Output Format (JSON):**
{{
    "thought": "Your reasoning about this error...",
    "confidence": 0.0-1.0,
    "needs_more_info": true/false,
    "next_action": "tool_name or DONE",
    "reasoning": "Why you chose this action..."
}}"""
    }

    _FALLBACK_FEW_SHOT_EXAMPLES = {
        "CODE_ERROR": [
            ReasoningExample(
                error_summary="NullPointerException at line 45 in UserService.java",
                thought="This is a classic null pointer issue. The error says 'user' is null when calling getUserDetails(). I need to understand the context - is this a common pattern we've seen before?",
                action="pinecone_knowledge",
                reasoning="First, search knowledge docs for NullPointerException patterns to see if we have documented solutions."
            ),
            ReasoningExample(
                error_summary="TypeError: Cannot read property 'id' of undefined",
                thought="JavaScript undefined property access. The object is undefined when we try to access 'id'. RAG search found similar patterns - they recommend null checking before access. Confidence is high.",
                action="DONE",
                reasoning="Knowledge search returned clear solution with 0.88 confidence. We have enough to answer."
            )
        ],
        "INFRA_ERROR": [
            ReasoningExample(
                error_summary="OutOfMemoryError: Java heap space",
                thought="Memory exhaustion issue. Heap is full. This is infrastructure-related, not a code bug. I need to check if we have solutions for memory tuning.",
                action="pinecone_knowledge",
                reasoning="Search for OutOfMemoryError solutions and JVM heap configuration recommendations."
            )
        ],
        "CONFIG_ERROR": [
            ReasoningExample(
                error_summary="PermissionError: Permission denied /var/log/app.log",
                thought="Permission issue with log file. Process user doesn't have write access. This is a configuration/deployment problem, not code.",
                action="pinecone_knowledge",
                reasoning="Search for permission issue solutions and file access configuration."
            )
        ],
        "DEPENDENCY_ERROR": [
            ReasoningExample(
                error_summary="ModuleNotFoundError: No module named 'pandas'",
                thought="Missing Python package. Package not installed in environment. Need to check requirements and installation procedure.",
                action="pinecone_knowledge",
                reasoning="Search for dependency installation solutions and package management guidance."
            )
        ],
        "TEST_FAILURE": [
            ReasoningExample(
                error_summary="AssertionError: Expected 200, got 404",
                thought="Test expecting success (200) but getting not found (404). Could be legitimate bug or test data issue. Need context.",
                action="pinecone_knowledge",
                reasoning="Search for API test failure patterns and 404 error handling."
            )
        ]
    }

    _FALLBACK_OBSERVATION_TEMPLATE = """**Observation Analysis**

You just executed: {tool_name}

**Tool Results:**
{tool_results}

**Your Task:**
Analyze what you learned from this tool execution. Consider:
1. Did this give us useful information?
2. Did it increase or decrease our confidence?
3. What does this tell us about the root cause?
4. Should we continue gathering info or are we ready to answer?

**Current Confidence:** {current_confidence}

**Output Format (JSON):**
{{
    "observation": "What you learned from the tool results...",
    "confidence_change": "+0.2 (if info was helpful) or -0.1 (if contradictory) or 0.0 (if unclear)",
    "key_findings": ["finding 1", "finding 2"],
    "ready_to_answer": true/false
}}"""

    _FALLBACK_ANSWER_GENERATION_TEMPLATE = """**Generate Final Answer**

You have completed your ReAct reasoning loop. Now generate a comprehensive answer.

**Error Category:** {error_category}

**All Information Gathered:**
{all_context}

**Reasoning History:**
{reasoning_history}

**Your Task:**
Based on ALL the information gathered, provide:
1. **Root Cause:** Clear explanation of what caused the error
2. **Fix Recommendation:** Specific, actionable steps to fix it
3. **Confidence:** Your confidence level (0.0-1.0)

**Guidelines:**
- Be specific and actionable
- Reference the evidence from your research
- If unsure, be honest about confidence level
- For CODE_ERROR: Include file/line references if available
- For INFRA_ERROR: Include resource metrics and thresholds
- For CONFIG_ERROR: Include specific config changes needed

**Output Format (JSON):**
{{
    "root_cause": "Clear explanation of the root cause...",
    "fix_recommendation": "Specific steps to fix the issue...",
    "confidence": 0.0-1.0,
    "evidence": ["evidence 1", "evidence 2"],
    "additional_notes": "Any caveats or additional context..."
}}"""

    # =========================================================================
    # PUBLIC API (BACKWARD COMPATIBLE)
    # =========================================================================

    @classmethod
    def get_reasoning_prompt(
        cls,
        error_category: str,
        error_info: str,
        context_summary: str
    ) -> str:
        """
        Get reasoning prompt for an error category.

        NEW: Tries Pinecone first, falls back to code templates.

        Args:
            error_category: Error category (CODE_ERROR, INFRA_ERROR, etc.)
            error_info: Information about the error
            context_summary: Summary of context gathered so far

        Returns:
            Formatted reasoning prompt
        """
        # Try Pinecone first
        template = cls._fetch_from_pinecone("reasoning_template", error_category)

        # Fallback to code
        if template is None:
            logger.debug(f"Using code fallback for reasoning template: {error_category}")
            template = cls._FALLBACK_REASONING_TEMPLATES.get(
                error_category,
                cls._FALLBACK_REASONING_TEMPLATES["UNKNOWN"]
            )

        return template.format(
            error_info=error_info,
            context_summary=context_summary
        )

    @classmethod
    def get_few_shot_examples(
        cls,
        error_category: str,
        max_examples: int = 2
    ) -> List[ReasoningExample]:
        """
        Get few-shot examples for an error category.

        NEW: Tries Pinecone first, falls back to code examples.

        Args:
            error_category: Error category
            max_examples: Maximum number of examples to return

        Returns:
            List of reasoning examples
        """
        # Try Pinecone first
        pinecone_examples = cls._fetch_from_pinecone("few_shot_example", error_category)

        if pinecone_examples:
            # Convert to ReasoningExample objects
            examples = [
                ReasoningExample(
                    error_summary=ex["error_summary"],
                    thought=ex["thought"],
                    action=ex["action"],
                    reasoning=ex["reasoning"]
                )
                for ex in pinecone_examples
            ]
            return examples[:max_examples]

        # Fallback to code
        logger.debug(f"Using code fallback for few-shot examples: {error_category}")
        examples = cls._FALLBACK_FEW_SHOT_EXAMPLES.get(error_category, [])
        return examples[:max_examples]

    @classmethod
    def format_few_shot_examples(
        cls,
        examples: List[ReasoningExample]
    ) -> str:
        """Format few-shot examples for inclusion in prompts"""
        if not examples:
            return ""

        formatted = "**Examples of Good Reasoning:**\n\n"
        for i, example in enumerate(examples, 1):
            formatted += f"""Example {i}:
Error: {example.error_summary}
Thought: {example.thought}
Action: {example.action}
Reasoning: {example.reasoning}

"""
        return formatted

    @classmethod
    def get_observation_prompt(
        cls,
        tool_name: str,
        tool_results: str,
        current_confidence: float
    ) -> str:
        """
        Get observation analysis prompt.

        NEW: Tries Pinecone first, falls back to code template.
        """
        # Try Pinecone first
        template = cls._fetch_from_pinecone("observation_template", "GLOBAL")

        # Fallback to code
        if template is None:
            logger.debug("Using code fallback for observation template")
            template = cls._FALLBACK_OBSERVATION_TEMPLATE

        return template.format(
            tool_name=tool_name,
            tool_results=tool_results[:1000],
            current_confidence=f"{current_confidence:.2f}"
        )

    @classmethod
    def get_answer_generation_prompt(
        cls,
        error_category: str,
        all_context: str,
        reasoning_history: str
    ) -> str:
        """
        Get answer generation prompt.

        NEW: Tries Pinecone first, falls back to code template.
        """
        # Try Pinecone first
        template = cls._fetch_from_pinecone("answer_generation_template", "GLOBAL")

        # Fallback to code
        if template is None:
            logger.debug("Using code fallback for answer generation template")
            template = cls._FALLBACK_ANSWER_GENERATION_TEMPLATE

        return template.format(
            error_category=error_category,
            all_context=all_context,
            reasoning_history=reasoning_history
        )

    @classmethod
    def get_reasoning_prompt_with_examples(
        cls,
        error_category: str,
        error_info: str,
        context_summary: str,
        include_examples: bool = True
    ) -> str:
        """Get reasoning prompt with optional few-shot examples"""
        base_prompt = cls.get_reasoning_prompt(
            error_category,
            error_info,
            context_summary
        )

        if include_examples:
            examples = cls.get_few_shot_examples(error_category, max_examples=2)
            if examples:
                examples_text = cls.format_few_shot_examples(examples)
                base_prompt = examples_text + "\n" + base_prompt

        return base_prompt

    @classmethod
    def clear_cache(cls):
        """Clear template cache (for testing or manual refresh)"""
        cls._cache.clear()
        cls._cache_timestamps.clear()
        logger.info("Template cache cleared")
