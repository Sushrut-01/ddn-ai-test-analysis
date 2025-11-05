"""
Self-Correction Strategy for ReAct Agent
=========================================

Implements retry logic and alternative tool selection when tools fail.
Part of Task 0-ARCH.5: Self-Correction Mechanism.

Features:
1. Retry logic for transient errors (timeout, connection, rate limit)
2. Max 3 retries per tool with exponential backoff
3. Alternative tool suggestion when retries exhausted
4. Retry history tracking per tool

Usage:
    corrector = SelfCorrectionStrategy()

    # When tool fails
    if corrector.should_retry(tool_name, error):
        wait_time = corrector.get_backoff_time(tool_name)
        time.sleep(wait_time)
        # Retry tool execution
    else:
        alt_tool = corrector.suggest_alternative_tool(tool_name, error_category)
        # Try alternative tool

File: implementation/agents/correction_strategy.py
Created: 2025-11-02
Task: 0-ARCH.5
"""

import logging
import time
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfCorrectionStrategy:
    """
    Self-correction mechanism for handling tool failures and suggesting alternatives.

    Implements:
    - Retry logic for transient errors (max 3 retries)
    - Exponential backoff (1s, 2s, 4s)
    - Alternative tool suggestions
    - Retry history tracking
    """

    MAX_RETRIES = 3
    BASE_BACKOFF_SECONDS = 1  # Start with 1 second, then 2, 4, etc.

    def __init__(self):
        """Initialize self-correction strategy with empty retry history"""
        self.retry_history: Dict[str, int] = {}  # tool_name -> retry_count
        self.last_retry_time: Dict[str, datetime] = {}  # tool_name -> last_retry_timestamp

    def should_retry(self, tool_name: str, error: Exception) -> bool:
        """
        Decide if we should retry a failed tool execution.

        Retries up to MAX_RETRIES times for transient errors like:
        - Timeout errors
        - Connection errors
        - Rate limit errors

        Args:
            tool_name: Name of the tool that failed
            error: The exception that was raised

        Returns:
            True if we should retry, False otherwise
        """
        # Check current retry count
        retries = self.retry_history.get(tool_name, 0)

        # Max retries reached?
        if retries >= self.MAX_RETRIES:
            logger.warning(f"❌ Max retries ({self.MAX_RETRIES}) reached for {tool_name}")
            return False

        # Check if this is a transient error worth retrying
        error_str = str(error).lower()
        transient_errors = [
            "timeout",
            "timed out",
            "connection",
            "connection reset",
            "connection refused",
            "rate limit",
            "too many requests",
            "503",  # Service unavailable
            "502",  # Bad gateway
            "504",  # Gateway timeout
            "temporary failure",
            "try again"
        ]

        is_transient = any(err in error_str for err in transient_errors)

        if is_transient:
            self.retry_history[tool_name] = retries + 1
            self.last_retry_time[tool_name] = datetime.now()
            logger.info(f"🔄 Retry {retries + 1}/{self.MAX_RETRIES} for {tool_name} (transient error: {type(error).__name__})")
            return True

        # Not a transient error - don't retry
        logger.info(f"❌ Not retrying {tool_name} - permanent error: {type(error).__name__}")
        return False

    def get_backoff_time(self, tool_name: str) -> float:
        """
        Calculate exponential backoff wait time for retry.

        Formula: BASE_BACKOFF * (2 ^ (retry_count - 1))
        - Retry 1: 1 second
        - Retry 2: 2 seconds
        - Retry 3: 4 seconds

        Args:
            tool_name: Name of the tool to get backoff time for

        Returns:
            Number of seconds to wait before retry
        """
        retries = self.retry_history.get(tool_name, 1)
        backoff = self.BASE_BACKOFF_SECONDS * (2 ** (retries - 1))
        logger.debug(f"⏱️ Backoff time for {tool_name}: {backoff}s")
        return backoff

    def suggest_alternative_tool(self, failed_tool: str, error_category: str = None) -> Optional[str]:
        """
        Suggest an alternative tool when the primary tool fails.

        Mapping logic:
        - If file retrieval fails → Try code search
        - If knowledge search fails → Try web search
        - If log retrieval fails → Try failure history

        Args:
            failed_tool: Name of the tool that failed
            error_category: Optional error category for context

        Returns:
            Name of alternative tool, or None if no alternative exists
        """
        # Tool alternatives mapping
        alternatives = {
            # GitHub tools
            "github_get_file": "github_search_code",  # If file not found, try search
            "github_get_pr": "github_list_prs",  # If specific PR fails, list all

            # Knowledge/Search tools
            "pinecone_knowledge_search": "web_search_error",  # If no docs, try web
            "pinecone_error_docs": "web_search_error",  # Fallback to web search

            # Database/Logging tools
            "mongodb_get_logs": "postgres_get_failure_history",  # If logs missing, try history
            "postgres_get_failure_history": "mongodb_get_logs",  # Try reverse too

            # Web search (no alternative - it's the last resort)
            "web_search_error": None
        }

        alternative = alternatives.get(failed_tool)

        if alternative:
            logger.info(f"💡 Suggesting alternative tool: {failed_tool} → {alternative}")
        else:
            logger.warning(f"⚠️ No alternative tool available for {failed_tool}")

        return alternative

    def reset_tool_history(self, tool_name: str):
        """
        Reset retry history for a specific tool.
        Useful when starting a new error analysis or after successful execution.

        Args:
            tool_name: Name of tool to reset history for
        """
        if tool_name in self.retry_history:
            del self.retry_history[tool_name]
        if tool_name in self.last_retry_time:
            del self.last_retry_time[tool_name]
        logger.debug(f"🔄 Reset retry history for {tool_name}")

    def reset_all_history(self):
        """
        Reset all retry history.
        Call this at the start of each new error analysis.
        """
        self.retry_history.clear()
        self.last_retry_time.clear()
        logger.debug("🔄 Reset all retry history")

    def get_retry_stats(self) -> Dict[str, int]:
        """
        Get retry statistics for debugging/monitoring.

        Returns:
            Dictionary of tool_name -> retry_count
        """
        return self.retry_history.copy()

    def has_exhausted_retries(self, tool_name: str) -> bool:
        """
        Check if a tool has exhausted all retries.

        Args:
            tool_name: Name of tool to check

        Returns:
            True if tool has reached MAX_RETRIES, False otherwise
        """
        return self.retry_history.get(tool_name, 0) >= self.MAX_RETRIES


# Singleton instance for easy access
_correction_strategy_instance = None

def get_correction_strategy() -> SelfCorrectionStrategy:
    """
    Get singleton instance of SelfCorrectionStrategy.

    Returns:
        Global SelfCorrectionStrategy instance
    """
    global _correction_strategy_instance
    if _correction_strategy_instance is None:
        _correction_strategy_instance = SelfCorrectionStrategy()
    return _correction_strategy_instance
