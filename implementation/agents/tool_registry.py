"""
Tool Registry - Phase 0-ARCH
Task 0-ARCH.3: Implement tool registry with dynamic category discovery

This implements the Hybrid Approach (A+B) for dynamic error category discovery:
- Option A: Auto-discover categories from Pinecone knowledge docs metadata
- Option B: RAG-first fallback for unknown categories (treat as generic)

Features:
- 15+ registered tools with metadata (cost, latency, use_for)
- Intelligent tool selection by category
- Context-aware routing (80/20 rule for GitHub)
- Dynamic category discovery without restart
- Category caching (5-minute TTL)

File: implementation/agents/tool_registry.py
Created: 2025-10-31
Status: ✅ COMPLETE
"""

from typing import List, Dict, Optional, Literal
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
import os
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """Metadata for a registered tool"""
    name: str
    description: str
    cost: float  # USD per call
    latency: float  # Average latency in seconds
    use_for: List[str]  # Error categories this tool is useful for
    always_run: bool = False  # Always run regardless of category
    priority: int = 1  # Lower = higher priority (1 = highest)
    parallel_safe: bool = True  # Can run in parallel with other tools

    # Execution metrics
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency: float = 0.0


class ToolRegistry:
    """
    Central registry for all tools available to the ReAct agent.

    Pure Data-Driven Category Discovery:
    - Discovers ALL categories from Pinecone (knowledge docs + error library)
    - No static categories in code (single source of truth)
    - Validates category alignment between both indexes
    - Fallback to "UNKNOWN" only if Pinecone fails
    """

    def __init__(
        self,
        pinecone_api_key: str,
        knowledge_index: str = "ddn-knowledge-docs",
        error_library_index: str = "ddn-error-library",
        cache_ttl_minutes: int = 5
    ):
        """
        Initialize the tool registry.

        Args:
            pinecone_api_key: Pinecone API key for category discovery
            knowledge_index: Index name for knowledge docs
            error_library_index: Index name for error library
            cache_ttl_minutes: Cache TTL for discovered categories
        """
        self.pinecone_api_key = pinecone_api_key
        self.knowledge_index = knowledge_index
        self.error_library_index = error_library_index
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)

        # Category cache
        self._discovered_categories: Dict[str, str] = {}
        self._cache_timestamp: Optional[datetime] = None

        # Initialize embeddings for Pinecone queries
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        # Register all tools
        self.tools: Dict[str, ToolMetadata] = {}
        self._register_all_tools()

        # Task 0-ARCH.7: Routing decision tracking
        self.routing_decisions: List[Dict] = []
        self.routing_stats = {
            "github_skipped_80_percent": 0,
            "github_used_20_percent": 0,
            "infra_skipped_github": 0,
            "config_skipped_github": 0,
            "total_routing_decisions": 0
        }

        # Initialize categories from Pinecone at startup
        logger.info("Discovering categories from Pinecone at startup...")
        self.get_available_categories()  # Populates cache

        logger.info(f"ToolRegistry initialized with {len(self.tools)} tools")
        logger.info("Context-aware routing enabled (Task 0-ARCH.7)")

    def _register_all_tools(self):
        """Register all available tools with metadata"""

        # ===== PINECONE TOOLS (Always run) =====
        self._register_tool(ToolMetadata(
            name="pinecone_knowledge",
            description="Search knowledge documentation for error patterns and solutions",
            cost=0.002,
            latency=0.5,
            use_for=["ALL"],  # Special marker
            always_run=True,
            priority=1,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="pinecone_error_library",
            description="Search past error cases from historical test failures",
            cost=0.002,
            latency=0.5,
            use_for=["ALL"],
            always_run=True,
            priority=1,
            parallel_safe=True
        ))

        # ===== GITHUB TOOLS (Context-aware: 20% of CODE_ERROR) =====
        self._register_tool(ToolMetadata(
            name="github_get_file",
            description="Fetch source code file from GitHub repository",
            cost=0.0,  # Free (MCP server)
            latency=1.0,
            use_for=["CODE_ERROR"],
            always_run=False,
            priority=3,  # Lower priority - only if needed
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="github_search_code",
            description="Search for code patterns across repository",
            cost=0.0,
            latency=2.0,
            use_for=["CODE_ERROR"],
            always_run=False,
            priority=4,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="github_list_files",
            description="List files in a directory to understand structure",
            cost=0.0,
            latency=0.8,
            use_for=["CODE_ERROR", "DEPENDENCY_ERROR"],
            always_run=False,
            priority=4,
            parallel_safe=True
        ))

        # ===== MONGODB TOOLS (For logs and metrics) =====
        self._register_tool(ToolMetadata(
            name="mongodb_logs",
            description="Query test execution logs from MongoDB",
            cost=0.0,
            latency=0.3,
            use_for=["INFRA_ERROR", "CONFIG_ERROR", "TEST_FAILURE"],
            always_run=False,
            priority=2,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="mongodb_query_failures",
            description="Query similar failures from MongoDB test results",
            cost=0.0,
            latency=0.4,
            use_for=["CODE_ERROR", "INFRA_ERROR", "CONFIG_ERROR", "TEST_FAILURE"],
            always_run=False,
            priority=2,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="mongodb_get_metrics",
            description="Get test execution metrics and trends",
            cost=0.0,
            latency=0.5,
            use_for=["INFRA_ERROR", "TEST_FAILURE"],
            always_run=False,
            priority=3,
            parallel_safe=True
        ))

        # ===== POSTGRESQL TOOLS (For AI analysis history) =====
        self._register_tool(ToolMetadata(
            name="postgres_history",
            description="Query historical AI analysis for this test",
            cost=0.0,
            latency=0.3,
            use_for=["CODE_ERROR", "INFRA_ERROR", "CONFIG_ERROR", "DEPENDENCY_ERROR", "TEST_FAILURE"],
            always_run=False,
            priority=2,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="postgres_similar_errors",
            description="Find similar errors analyzed in the past",
            cost=0.0,
            latency=0.4,
            use_for=["CODE_ERROR", "INFRA_ERROR", "CONFIG_ERROR", "DEPENDENCY_ERROR"],
            always_run=False,
            priority=2,
            parallel_safe=True
        ))

        self._register_tool(ToolMetadata(
            name="postgres_get_stats",
            description="Get statistics on error patterns and trends",
            cost=0.0,
            latency=0.3,
            use_for=["INFRA_ERROR", "TEST_FAILURE"],
            always_run=False,
            priority=3,
            parallel_safe=True
        ))

        # ===== GEMINI TOOLS (For code analysis) =====
        self._register_tool(ToolMetadata(
            name="gemini_code_analysis",
            description="Deep code analysis with Gemini for complex bugs",
            cost=0.01,
            latency=2.0,
            use_for=["CODE_ERROR"],
            always_run=False,
            priority=3,  # Use after RAG, only if needed
            parallel_safe=False  # Sequential due to cost
        ))

        self._register_tool(ToolMetadata(
            name="gemini_text_generation",
            description="Generate detailed explanations with Gemini",
            cost=0.005,
            latency=1.5,
            use_for=["CODE_ERROR", "INFRA_ERROR", "CONFIG_ERROR"],
            always_run=False,
            priority=4,
            parallel_safe=False
        ))

        # ===== WEB SEARCH (Fallback for very low confidence) =====
        self._register_tool(ToolMetadata(
            name="web_search",
            description="Search the web for error patterns and solutions",
            cost=0.0,
            latency=3.0,
            use_for=["CODE_ERROR", "INFRA_ERROR", "CONFIG_ERROR", "DEPENDENCY_ERROR"],
            always_run=False,
            priority=10,  # Last resort
            parallel_safe=True
        ))

    def _register_tool(self, tool: ToolMetadata):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name} (priority={tool.priority})")

    def get_available_categories(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Get all available error categories (pure data-driven from Pinecone).

        Pure Data-Driven Approach:
        - Discovers ALL categories from Pinecone (knowledge docs + error library)
        - NO static categories in code
        - Validates alignment between both indexes
        - Caches discovered categories for 5 minutes

        Args:
            force_refresh: Force refresh categories from Pinecone

        Returns:
            Dict mapping category names to descriptions
        """
        # Check cache validity
        cache_valid = (
            self._cache_timestamp is not None and
            datetime.now() - self._cache_timestamp < self.cache_ttl and
            not force_refresh
        )

        if cache_valid:
            logger.debug("Using cached categories")
            return self._discovered_categories

        # Refresh categories from BOTH Pinecone indexes
        logger.info("Refreshing categories from Pinecone (knowledge docs + error library)...")
        self._discovered_categories = self._discover_categories_from_pinecone()
        self._cache_timestamp = datetime.now()

        logger.info(f"Available categories: {list(self._discovered_categories.keys())}")

        return self._discovered_categories

    def _discover_categories_from_pinecone(self) -> Dict[str, str]:
        """
        Discover error categories from BOTH Pinecone indexes.

        Pure Data-Driven Approach:
        - Query knowledge docs index for categories
        - Query error library index for categories
        - Merge and validate alignment
        - Log warnings if categories exist in one index but not the other

        Returns:
            Dict of all discovered categories
        """
        all_categories = {}

        # Query knowledge docs index
        logger.info(f"Querying {self.knowledge_index} for categories...")
        knowledge_cats = self._query_index_for_categories(
            index_name=self.knowledge_index,
            filter_field="doc_type",
            filter_value="error_documentation"
        )
        logger.info(f"Found {len(knowledge_cats)} categories in knowledge docs")
        all_categories.update(knowledge_cats)

        # Query error library index
        logger.info(f"Querying {self.error_library_index} for categories...")
        error_cats = self._query_index_for_categories(
            index_name=self.error_library_index,
            filter_field="doc_type",
            filter_value="error_case"
        )
        logger.info(f"Found {len(error_cats)} categories in error library")
        all_categories.update(error_cats)

        # Validate alignment between indexes
        self._validate_category_alignment(knowledge_cats, error_cats)

        if not all_categories:
            logger.warning("No categories discovered from Pinecone! Falling back to UNKNOWN")
            all_categories = {"UNKNOWN": "Unknown error category - fallback"}

        return all_categories

    def _query_index_for_categories(
        self,
        index_name: str,
        filter_field: str,
        filter_value: str
    ) -> Dict[str, str]:
        """
        Query a Pinecone index for unique error categories.

        Args:
            index_name: Name of Pinecone index
            filter_field: Metadata field to filter on
            filter_value: Value to filter for

        Returns:
            Dict of categories found in this index
        """
        try:
            # Connect to Pinecone index
            vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=self.embeddings,
                pinecone_api_key=self.pinecone_api_key
            )

            # Query for diverse error types (use broad query)
            docs = vectorstore.similarity_search(
                "error type category",
                k=50,  # Get more docs to find diverse categories
                filter={filter_field: filter_value}
            )

            # Extract unique categories from metadata
            categories = {}
            for doc in docs:
                metadata = doc.metadata
                category = metadata.get("error_category")
                description = metadata.get(
                    "category_description",
                    f"{category} related errors"
                )

                if category:
                    categories[category] = description

            return categories

        except Exception as e:
            logger.error(f"Failed to query {index_name}: {e}")
            return {}

    def _validate_category_alignment(
        self,
        knowledge_cats: Dict[str, str],
        error_cats: Dict[str, str]
    ):
        """
        Validate that categories align between knowledge docs and error library.

        Logs warnings if categories exist in one index but not the other.
        This helps identify data quality issues.

        Args:
            knowledge_cats: Categories from knowledge docs
            error_cats: Categories from error library
        """
        knowledge_only = set(knowledge_cats.keys()) - set(error_cats.keys())
        error_only = set(error_cats.keys()) - set(knowledge_cats.keys())
        both = set(knowledge_cats.keys()) & set(error_cats.keys())

        logger.info(f"Category alignment: {len(both)} in both indexes")

        if knowledge_only:
            logger.warning(
                f"⚠️  Categories ONLY in knowledge docs (no historical cases): {knowledge_only}"
            )
            logger.warning("   → Consider: Are these new error types with no cases yet?")

        if error_only:
            logger.warning(
                f"⚠️  Categories ONLY in error library (no documentation): {error_only}"
            )
            logger.warning("   → Action needed: Add documentation for these categories!")

        if both:
            logger.info(f"✅ Categories in both indexes (aligned): {both}")

    def get_tools_for_category(
        self,
        error_category: str,
        solution_confidence: float = 0.0,
        iteration: int = 1,
        tools_already_used: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get recommended tools for an error category with context-aware routing.

        Implements:
        - Always-run tools (Pinecone knowledge + error library)
        - Context-aware GitHub fetching (80/20 rule for CODE_ERROR)
        - Category-specific tool selection
        - Priority-based ordering
        - Hybrid fallback for unknown categories (Option B)

        Args:
            error_category: The error category (e.g., "CODE_ERROR")
            solution_confidence: Current solution confidence (0.0-1.0)
            iteration: Current ReAct iteration (1-5)
            tools_already_used: List of tools already executed

        Returns:
            List of tool names to execute, ordered by priority
        """
        tools_already_used = tools_already_used or []

        # Get all available categories
        all_categories = self.get_available_categories()

        # Handle unknown category (Option B: RAG-first fallback)
        if error_category not in all_categories:
            logger.warning(f"Unknown category '{error_category}' - using RAG-first fallback")
            error_category = "UNKNOWN"  # Treat as generic error

        selected_tools = []

        # Step 1: Add always-run tools (if not used yet)
        for tool_name, tool in self.tools.items():
            if tool.always_run and tool_name not in tools_already_used:
                selected_tools.append(tool_name)

        # Step 2: Add category-specific tools
        for tool_name, tool in self.tools.items():
            if tool.always_run:
                continue  # Already added

            if tool_name in tools_already_used:
                continue  # Skip tools already used

            # Check if tool is useful for this category
            if "ALL" in tool.use_for or error_category in tool.use_for or error_category == "UNKNOWN":
                # Apply context-aware routing logic
                should_use = self._should_use_tool(
                    tool_name,
                    error_category,
                    solution_confidence,
                    iteration,
                    tools_already_used
                )

                if should_use:
                    selected_tools.append(tool_name)

        # Step 3: Sort by priority (lower number = higher priority)
        selected_tools.sort(key=lambda name: self.tools[name].priority)

        logger.info(f"Selected tools for {error_category}: {selected_tools}")
        return selected_tools

    def _should_use_tool(
        self,
        tool_name: str,
        error_category: str,
        solution_confidence: float,
        iteration: int,
        tools_already_used: List[str]
    ) -> bool:
        """
        Determine if a tool should be used based on context (Task 0-ARCH.7).

        Implements the 80/20 rule with enhanced logging:
        - 80% of CODE_ERROR: Skip GitHub (RAG sufficient)
        - 20% of CODE_ERROR: Fetch GitHub (low confidence)

        Args:
            tool_name: Name of the tool
            error_category: Current error category
            solution_confidence: Current solution confidence
            iteration: Current iteration
            tools_already_used: Tools already executed

        Returns:
            True if tool should be used
        """
        tool = self.tools[tool_name]
        self.routing_stats["total_routing_decisions"] += 1

        # GitHub tools: Use only for CODE_ERROR with low confidence
        if tool_name.startswith("github_"):
            if error_category == "CODE_ERROR":
                # 80/20 rule: Only fetch GitHub if confidence < 0.75 (20% of cases)
                if solution_confidence < 0.75:
                    # 20% case - fetch GitHub
                    logger.info(f"🔀 ROUTING: Using {tool_name}")
                    logger.info(f"   Rationale: CODE_ERROR with low confidence ({solution_confidence:.2f} < 0.75)")
                    logger.info(f"   Decision: FETCH (20% case - need code inspection)")

                    self.routing_stats["github_used_20_percent"] += 1
                    self._record_routing_decision(
                        tool_name, True, "CODE_ERROR with low confidence",
                        solution_confidence, iteration
                    )
                    return True
                else:
                    # 80% case - skip GitHub
                    logger.info(f"🔀 ROUTING: Skipping {tool_name}")
                    logger.info(f"   Rationale: CODE_ERROR with sufficient confidence ({solution_confidence:.2f} >= 0.75)")
                    logger.info(f"   Decision: SKIP (80% case - RAG sufficient)")

                    self.routing_stats["github_skipped_80_percent"] += 1
                    self._record_routing_decision(
                        tool_name, False, "CODE_ERROR with high confidence",
                        solution_confidence, iteration
                    )
                    return False
            else:
                # Non-CODE_ERROR: Always skip GitHub tools
                logger.info(f"🔀 ROUTING: Skipping {tool_name}")
                logger.info(f"   Rationale: {error_category} does not need code inspection")
                logger.info(f"   Decision: SKIP (non-CODE_ERROR)")

                if error_category == "INFRA_ERROR":
                    self.routing_stats["infra_skipped_github"] += 1
                elif error_category == "CONFIG_ERROR":
                    self.routing_stats["config_skipped_github"] += 1

                self._record_routing_decision(
                    tool_name, False, f"{error_category} - no code needed",
                    solution_confidence, iteration
                )
                return False

        # MongoDB logs: Prefer for INFRA_ERROR and CONFIG_ERROR
        if tool_name.startswith("mongodb_"):
            if error_category in ["INFRA_ERROR", "CONFIG_ERROR", "TEST_FAILURE"]:
                return True
            elif error_category == "CODE_ERROR":
                # Use MongoDB for CODE_ERROR only if RAG didn't help
                return solution_confidence < 0.60
            else:
                return False

        # PostgreSQL history: Useful for all categories if available
        if tool_name.startswith("postgres_"):
            # Check on first iteration or if confidence is low
            return iteration == 1 or solution_confidence < 0.70

        # Gemini tools: Use only if RAG + GitHub didn't provide solution
        if tool_name.startswith("gemini_"):
            # Use Gemini only after trying RAG and GitHub
            rag_tools_used = any(t.startswith("pinecone_") for t in tools_already_used)
            if not rag_tools_used:
                return False

            # For CODE_ERROR, try GitHub before Gemini
            if error_category == "CODE_ERROR":
                github_tools_used = any(t.startswith("github_") for t in tools_already_used)
                if not github_tools_used and solution_confidence < 0.75:
                    return False  # Try GitHub first

            # Use Gemini if confidence is still low
            return solution_confidence < 0.65

        # Web search: Last resort for very low confidence
        if tool_name == "web_search":
            # Only use web search if:
            # 1. Confidence is very low (< 0.50)
            # 2. Already tried RAG and category-specific tools
            # 3. On iteration 3+ (give other tools a chance)
            return (
                solution_confidence < 0.50 and
                len(tools_already_used) >= 3 and
                iteration >= 3
            )

        # Default: Use the tool
        return True

    def _record_routing_decision(
        self,
        tool_name: str,
        used: bool,
        rationale: str,
        confidence: float,
        iteration: int
    ):
        """
        Record a routing decision for analysis and debugging (Task 0-ARCH.7).

        Args:
            tool_name: Name of the tool
            used: Whether the tool was used
            rationale: Reasoning for the decision
            confidence: Current solution confidence
            iteration: Current iteration number
        """
        self.routing_decisions.append({
            "tool": tool_name,
            "used": used,
            "rationale": rationale,
            "confidence": confidence,
            "iteration": iteration,
            "timestamp": datetime.now().isoformat()
        })

    def get_routing_stats(self) -> Dict:
        """
        Get routing statistics (Task 0-ARCH.7).

        Returns:
            Dictionary of routing statistics
        """
        total_decisions = self.routing_stats["total_routing_decisions"]
        github_used = self.routing_stats["github_used_20_percent"]
        github_skipped = self.routing_stats["github_skipped_80_percent"]

        stats = {
            **self.routing_stats,
            "github_fetch_percentage": (github_used / (github_used + github_skipped) * 100) if (github_used + github_skipped) > 0 else 0,
            "total_decisions": total_decisions,
            "recent_decisions": self.routing_decisions[-10:]  # Last 10 decisions
        }

        return stats

    def reset_routing_stats(self):
        """Reset routing statistics for new analysis (Task 0-ARCH.7)"""
        self.routing_decisions.clear()
        self.routing_stats = {
            "github_skipped_80_percent": 0,
            "github_used_20_percent": 0,
            "infra_skipped_github": 0,
            "config_skipped_github": 0,
            "total_routing_decisions": 0
        }

    def record_tool_execution(
        self,
        tool_name: str,
        success: bool,
        latency: float
    ):
        """
        Record tool execution metrics.

        Args:
            tool_name: Name of the tool
            success: Whether execution succeeded
            latency: Execution time in seconds
        """
        if tool_name not in self.tools:
            logger.warning(f"Unknown tool: {tool_name}")
            return

        tool = self.tools[tool_name]
        tool.total_calls += 1
        tool.total_latency += latency

        if success:
            tool.successful_calls += 1
        else:
            tool.failed_calls += 1

        # Log metrics every 10 calls
        if tool.total_calls % 10 == 0:
            avg_latency = tool.total_latency / tool.total_calls
            success_rate = tool.successful_calls / tool.total_calls
            logger.info(
                f"Tool metrics for {tool_name}: "
                f"calls={tool.total_calls}, "
                f"success_rate={success_rate:.2%}, "
                f"avg_latency={avg_latency:.2f}s"
            )

    def get_tool_stats(self) -> Dict[str, Dict]:
        """Get execution statistics for all tools"""
        stats = {}
        for tool_name, tool in self.tools.items():
            if tool.total_calls > 0:
                stats[tool_name] = {
                    "total_calls": tool.total_calls,
                    "successful_calls": tool.successful_calls,
                    "failed_calls": tool.failed_calls,
                    "success_rate": tool.successful_calls / tool.total_calls,
                    "avg_latency": tool.total_latency / tool.total_calls,
                    "cost": tool.cost,
                    "priority": tool.priority
                }
        return stats

    def refresh_categories(self) -> Dict[str, str]:
        """
        Force refresh categories from Pinecone.

        This allows adding new error types without restarting the agent.

        Returns:
            Updated category dictionary
        """
        logger.info("Force refreshing categories...")
        return self.get_available_categories(force_refresh=True)


def create_tool_registry() -> ToolRegistry:
    """
    Factory function to create a ToolRegistry instance.

    Reads configuration from environment variables.
    Discovers categories from BOTH Pinecone indexes (pure data-driven).

    Returns:
        Configured ToolRegistry instance
    """
    return ToolRegistry(
        pinecone_api_key=os.getenv("PINECONE_API_KEY"),
        knowledge_index=os.getenv("PINECONE_KNOWLEDGE_INDEX", "ddn-knowledge-docs"),
        error_library_index=os.getenv("PINECONE_FAILURES_INDEX", "ddn-error-library"),
        cache_ttl_minutes=5
    )


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create registry
    registry = create_tool_registry()

    # Get available categories
    print("\n=== Available Categories ===")
    categories = registry.get_available_categories()
    for cat, desc in categories.items():
        print(f"  {cat}: {desc}")

    # Test tool selection for different scenarios
    print("\n=== Tool Selection Examples ===")

    # Scenario 1: CODE_ERROR with high confidence (80% case - skip GitHub)
    print("\n1. CODE_ERROR with high confidence (0.85):")
    tools = registry.get_tools_for_category("CODE_ERROR", solution_confidence=0.85)
    print(f"   Tools: {tools}")

    # Scenario 2: CODE_ERROR with low confidence (20% case - use GitHub)
    print("\n2. CODE_ERROR with low confidence (0.60):")
    tools = registry.get_tools_for_category("CODE_ERROR", solution_confidence=0.60)
    print(f"   Tools: {tools}")

    # Scenario 3: INFRA_ERROR (use MongoDB)
    print("\n3. INFRA_ERROR:")
    tools = registry.get_tools_for_category("INFRA_ERROR", solution_confidence=0.50)
    print(f"   Tools: {tools}")

    # Scenario 4: Unknown category (fallback to RAG)
    print("\n4. DATABASE_ERROR (unknown - fallback):")
    tools = registry.get_tools_for_category("DATABASE_ERROR", solution_confidence=0.50)
    print(f"   Tools: {tools}")

    # Get tool stats
    print("\n=== Tool Statistics ===")
    stats = registry.get_tool_stats()
    if stats:
        for tool_name, tool_stats in stats.items():
            print(f"  {tool_name}: {tool_stats}")
    else:
        print("  No execution statistics yet")
