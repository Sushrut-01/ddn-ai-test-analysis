"""
RAG Router Module - Task 0D.3
Created: 2025-11-02
Status: Complete

OPTION C Routing Logic:
- CODE_ERROR → Gemini + GitHub + RAG (comprehensive analysis)
- INFRA_ERROR → RAG only (documentation-based solutions)
- CONFIG_ERROR → RAG only (configuration patterns)
- DEPENDENCY_ERROR → RAG only (package resolution)
- TEST_ERROR → RAG only (test patterns)
- UNKNOWN_ERROR → RAG only (general debugging)

Purpose:
This router implements the CRITICAL bug fix requirement:
  "Gemini should only be called for CODE_ERROR, not ALL errors"

Integration:
- Task 0D.5 will use this router to fix ai_analysis_service.py
- Works with context_engineering.py (Task 0D.1) for optimized context
- Works with prompt_templates.py (Task 0D.2) for category-specific prompts

File: implementation/rag_router.py
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class ErrorCategory(str, Enum):
    """Error categories for routing decisions"""
    CODE_ERROR = "CODE_ERROR"
    INFRA_ERROR = "INFRA_ERROR"
    CONFIG_ERROR = "CONFIG_ERROR"
    DEPENDENCY_ERROR = "DEPENDENCY_ERROR"
    TEST_ERROR = "TEST_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


@dataclass
class RoutingDecision:
    """
    Result of routing decision

    Attributes:
        error_category: Category of error
        should_use_gemini: Whether to call Gemini API
        should_use_github: Whether to fetch GitHub code
        should_use_rag: Whether to query RAG (always True)
        rag_tools: List of RAG tools to use
        routing_reason: Human-readable reason for routing
        routing_option: Which routing option (OPTION C)
    """
    error_category: str
    should_use_gemini: bool
    should_use_github: bool
    should_use_rag: bool
    rag_tools: List[str]
    routing_reason: str
    routing_option: str = "OPTION_C"

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "error_category": self.error_category,
            "should_use_gemini": self.should_use_gemini,
            "should_use_github": self.should_use_github,
            "should_use_rag": self.should_use_rag,
            "rag_tools": self.rag_tools,
            "routing_reason": self.routing_reason,
            "routing_option": self.routing_option
        }


# ============================================================================
# RAG ROUTER CLASS
# ============================================================================

class RAGRouter:
    """
    RAG Router for intelligent error routing (OPTION C)

    Routing Rules:
    1. CODE_ERROR → Gemini + GitHub + RAG
       - Needs deep code analysis
       - Gemini provides root cause from actual code
       - GitHub provides code context
       - RAG provides similar error patterns

    2. INFRA_ERROR → RAG only
       - Infrastructure errors are well-documented
       - RAG documentation sufficient
       - No code analysis needed

    3. CONFIG_ERROR → RAG only
       - Configuration patterns in knowledge base
       - RAG documentation sufficient

    4. DEPENDENCY_ERROR → RAG only
       - Package resolution patterns documented
       - RAG documentation sufficient

    5. TEST_ERROR → RAG only
       - Test patterns in knowledge base
       - RAG documentation sufficient

    6. UNKNOWN_ERROR → RAG only
       - Fallback to general debugging
       - RAG provides best-effort help
    """

    # OPTION C Routing Rules
    ROUTING_RULES = {
        ErrorCategory.CODE_ERROR: {
            "use_gemini": True,
            "use_github": True,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Code errors require deep analysis: Gemini for root cause, GitHub for context, RAG for patterns"
        },
        ErrorCategory.INFRA_ERROR: {
            "use_gemini": False,
            "use_github": False,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Infrastructure errors resolved via documented solutions in RAG"
        },
        ErrorCategory.CONFIG_ERROR: {
            "use_gemini": False,
            "use_github": False,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Configuration errors resolved via documented patterns in RAG"
        },
        ErrorCategory.DEPENDENCY_ERROR: {
            "use_gemini": False,
            "use_github": False,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Dependency errors resolved via package resolution patterns in RAG"
        },
        ErrorCategory.TEST_ERROR: {
            "use_gemini": False,
            "use_github": False,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Test errors resolved via test patterns in RAG"
        },
        ErrorCategory.UNKNOWN_ERROR: {
            "use_gemini": False,
            "use_github": False,
            "use_rag": True,
            "rag_tools": ["pinecone_knowledge", "pinecone_error_library"],
            "reason": "Unknown errors use RAG for best-effort pattern matching"
        }
    }

    def __init__(self):
        """Initialize RAG Router"""
        logger.info("RAGRouter initialized with OPTION C routing logic")
        logger.info("  CODE_ERROR -> Gemini + GitHub + RAG")
        logger.info("  All other errors -> RAG only")

        # Statistics tracking
        self._routing_stats = {
            "total_routes": 0,
            "gemini_routes": 0,
            "github_routes": 0,
            "rag_only_routes": 0,
            "by_category": {
                category.value: 0 for category in ErrorCategory
            }
        }

    def route_error(self, error_category: str, error_context: Optional[Dict] = None) -> RoutingDecision:
        """
        Make routing decision based on error category (OPTION C)

        Args:
            error_category: Error category (CODE_ERROR, INFRA_ERROR, etc.)
            error_context: Optional context dict (for future enhancements)

        Returns:
            RoutingDecision with routing instructions

        Example:
            router = RAGRouter()
            decision = router.route_error("CODE_ERROR")
            if decision.should_use_gemini:
                # Call Gemini with optimized context
                pass
            if decision.should_use_github:
                # Fetch GitHub code
                pass
            # Always query RAG
            for tool in decision.rag_tools:
                # Query RAG tool
                pass
        """
        # Normalize category
        error_category_upper = error_category.upper()

        # Get routing rule
        try:
            category_enum = ErrorCategory(error_category_upper)
        except ValueError:
            # Unknown category, fallback to UNKNOWN_ERROR
            logger.warning(f"Unknown error category '{error_category}', using UNKNOWN_ERROR fallback")
            category_enum = ErrorCategory.UNKNOWN_ERROR

        rule = self.ROUTING_RULES[category_enum]

        # Create routing decision
        decision = RoutingDecision(
            error_category=category_enum.value,
            should_use_gemini=rule["use_gemini"],
            should_use_github=rule["use_github"],
            should_use_rag=rule["use_rag"],
            rag_tools=rule["rag_tools"],
            routing_reason=rule["reason"]
        )

        # Update statistics
        self._update_stats(decision)

        # Log routing decision
        self._log_routing_decision(decision)

        return decision

    def should_use_gemini(self, error_category: str) -> bool:
        """
        Determine if Gemini should be used for this error category

        CRITICAL: Only CODE_ERROR uses Gemini (OPTION C)

        Args:
            error_category: Error category

        Returns:
            True only for CODE_ERROR, False for all others
        """
        try:
            category_enum = ErrorCategory(error_category.upper())
        except ValueError:
            return False

        return self.ROUTING_RULES[category_enum]["use_gemini"]

    def should_use_github(self, error_category: str) -> bool:
        """
        Determine if GitHub should be fetched for this error category

        Args:
            error_category: Error category

        Returns:
            True only for CODE_ERROR, False for all others
        """
        try:
            category_enum = ErrorCategory(error_category.upper())
        except ValueError:
            return False

        return self.ROUTING_RULES[category_enum]["use_github"]

    def get_rag_tools(self, error_category: str) -> List[str]:
        """
        Get RAG tools for this error category

        Args:
            error_category: Error category

        Returns:
            List of RAG tool names
        """
        try:
            category_enum = ErrorCategory(error_category.upper())
        except ValueError:
            category_enum = ErrorCategory.UNKNOWN_ERROR

        return self.ROUTING_RULES[category_enum]["rag_tools"]

    def get_routing_reason(self, error_category: str) -> str:
        """
        Get human-readable routing reason

        Args:
            error_category: Error category

        Returns:
            Reason string
        """
        try:
            category_enum = ErrorCategory(error_category.upper())
        except ValueError:
            category_enum = ErrorCategory.UNKNOWN_ERROR

        return self.ROUTING_RULES[category_enum]["reason"]

    def _update_stats(self, decision: RoutingDecision):
        """Update routing statistics"""
        self._routing_stats["total_routes"] += 1
        self._routing_stats["by_category"][decision.error_category] += 1

        if decision.should_use_gemini:
            self._routing_stats["gemini_routes"] += 1
        if decision.should_use_github:
            self._routing_stats["github_routes"] += 1
        if not decision.should_use_gemini:
            self._routing_stats["rag_only_routes"] += 1

    def _log_routing_decision(self, decision: RoutingDecision):
        """Log routing decision for visibility"""
        logger.info(f"[RAGRouter] Routing decision for {decision.error_category}:")
        logger.info(f"  Gemini: {'YES' if decision.should_use_gemini else 'NO'}")
        logger.info(f"  GitHub: {'YES' if decision.should_use_github else 'NO'}")
        logger.info(f"  RAG: {'YES' if decision.should_use_rag else 'NO'} ({', '.join(decision.rag_tools)})")
        logger.info(f"  Reason: {decision.routing_reason}")

    def get_routing_stats(self) -> Dict:
        """
        Get routing statistics

        Returns:
            Dictionary with routing statistics
        """
        stats = self._routing_stats.copy()

        # Calculate percentages
        total = stats["total_routes"]
        if total > 0:
            stats["gemini_percentage"] = (stats["gemini_routes"] / total) * 100
            stats["github_percentage"] = (stats["github_routes"] / total) * 100
            stats["rag_only_percentage"] = (stats["rag_only_routes"] / total) * 100
        else:
            stats["gemini_percentage"] = 0.0
            stats["github_percentage"] = 0.0
            stats["rag_only_percentage"] = 0.0

        return stats

    def reset_stats(self):
        """Reset routing statistics"""
        self._routing_stats = {
            "total_routes": 0,
            "gemini_routes": 0,
            "github_routes": 0,
            "rag_only_routes": 0,
            "by_category": {
                category.value: 0 for category in ErrorCategory
            }
        }
        logger.info("[RAGRouter] Statistics reset")

    def get_all_categories(self) -> List[str]:
        """
        Get all supported error categories

        Returns:
            List of error category names
        """
        return [category.value for category in ErrorCategory]

    def validate_routing_rules(self) -> Dict:
        """
        Validate routing rules consistency

        Returns:
            Validation result dictionary
        """
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "rule_count": len(self.ROUTING_RULES)
        }

        # Check all categories have rules
        for category in ErrorCategory:
            if category not in self.ROUTING_RULES:
                validation["valid"] = False
                validation["errors"].append(f"Missing routing rule for {category.value}")

        # Check OPTION C compliance: Only CODE_ERROR uses Gemini
        gemini_categories = [
            cat.value for cat, rule in self.ROUTING_RULES.items()
            if rule["use_gemini"]
        ]

        if gemini_categories != ["CODE_ERROR"]:
            validation["valid"] = False
            validation["errors"].append(
                f"OPTION C violation: Only CODE_ERROR should use Gemini, but found: {gemini_categories}"
            )

        # Check all rules have required fields
        required_fields = ["use_gemini", "use_github", "use_rag", "rag_tools", "reason"]
        for category, rule in self.ROUTING_RULES.items():
            for field in required_fields:
                if field not in rule:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing field '{field}' in {category.value} rule")

        # Check RAG always enabled
        for category, rule in self.ROUTING_RULES.items():
            if not rule["use_rag"]:
                validation["warnings"].append(f"{category.value} has RAG disabled (unusual)")

        return validation


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_rag_router() -> RAGRouter:
    """
    Factory function to create RAGRouter instance

    Returns:
        Initialized RAGRouter instance

    Example:
        from rag_router import create_rag_router

        router = create_rag_router()
        decision = router.route_error("CODE_ERROR")
    """
    return RAGRouter()


# ============================================================================
# MAIN (FOR TESTING)
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("RAG Router - Task 0D.3 - OPTION C Routing Logic")
    print("=" * 80)

    # Create router
    router = create_rag_router()

    # Validate routing rules
    print("\nValidating routing rules...")
    validation = router.validate_routing_rules()
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    # Test all categories
    print("\n" + "=" * 80)
    print("Testing all error categories:")
    print("=" * 80)

    for category in router.get_all_categories():
        print(f"\n{category}:")
        decision = router.route_error(category)
        print(f"  Gemini: {decision.should_use_gemini}")
        print(f"  GitHub: {decision.should_use_github}")
        print(f"  RAG: {decision.should_use_rag} ({', '.join(decision.rag_tools)})")
        print(f"  Reason: {decision.routing_reason}")

    # Show statistics
    print("\n" + "=" * 80)
    print("Routing Statistics:")
    print("=" * 80)
    stats = router.get_routing_stats()
    print(f"Total routes: {stats['total_routes']}")
    print(f"Gemini routes: {stats['gemini_routes']} ({stats['gemini_percentage']:.1f}%)")
    print(f"GitHub routes: {stats['github_routes']} ({stats['github_percentage']:.1f}%)")
    print(f"RAG-only routes: {stats['rag_only_routes']} ({stats['rag_only_percentage']:.1f}%)")
    print("\nBy category:")
    for cat, count in stats['by_category'].items():
        print(f"  {cat}: {count}")

    print("\n" + "=" * 80)
    print("OPTION C Routing: CODE_ERROR -> Gemini+GitHub, Others -> RAG only")
    print("=" * 80)
