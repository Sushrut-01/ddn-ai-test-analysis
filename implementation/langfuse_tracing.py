"""
Langfuse Tracing Module
Centralized LLM observability and tracing for DDN AI Analysis System
Task 8.19 - Phase 8: Monitoring and Observability
"""
import os
import functools
import logging
from typing import Optional, Callable, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)

# Langfuse client instance (initialized lazily)
_langfuse_client: Optional[Any] = None


def get_langfuse_client():
    """
    Get or create Langfuse client instance
    Lazy initialization with fallback if disabled
    """
    global _langfuse_client

    # Check if Langfuse is enabled
    langfuse_enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"

    if not langfuse_enabled:
        logger.info("Langfuse tracing is disabled (LANGFUSE_ENABLED=false)")
        return None

    # Return existing client if already initialized
    if _langfuse_client is not None:
        return _langfuse_client

    try:
        from langfuse import Langfuse

        # Get configuration from environment
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

        # Validate keys
        if not public_key or not secret_key:
            logger.warning(
                "Langfuse keys not configured. Set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY"
            )
            return None

        # Initialize client
        _langfuse_client = Langfuse(
            public_key=public_key, secret_key=secret_key, host=host
        )

        logger.info(f"✓ Langfuse client initialized successfully (host: {host})")
        return _langfuse_client

    except ImportError:
        logger.error(
            "Langfuse package not installed. Install with: pip install langfuse>=2.0.0"
        )
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Langfuse client: {str(e)}")
        return None


def trace(name: Optional[str] = None, **trace_kwargs):
    """
    Decorator for tracing function execution with Langfuse

    Usage:
        @trace(name="analyze_error")
        def my_function(arg1, arg2):
            # function code
            return result

    Args:
        name: Custom trace name (defaults to function name)
        **trace_kwargs: Additional trace metadata

    Returns:
        Decorated function with Langfuse tracing
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            client = get_langfuse_client()

            # If Langfuse is disabled or failed to initialize, run function without tracing
            if client is None:
                return func(*args, **kwargs)

            # Determine trace name
            trace_name = name or func.__name__

            # Create trace
            trace = client.trace(name=trace_name, **trace_kwargs)

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Update trace with success
                trace.update(
                    output=str(result)[:500],  # Limit output size
                    status_message="Success",
                )

                return result

            except Exception as e:
                # Update trace with error
                trace.update(
                    level="ERROR", status_message=f"Error: {str(e)}", output=str(e)
                )
                raise

        return wrapper

    return decorator


def trace_llm_call(
    name: str, model: str, input_text: str, output_text: str, metadata: dict = None
):
    """
    Manually log an LLM API call to Langfuse

    Args:
        name: Name of the LLM call (e.g., "gemini_analysis")
        model: Model name (e.g., "gemini-1.5-flash")
        input_text: Input prompt sent to LLM
        output_text: Response from LLM
        metadata: Additional metadata (tokens, cost, etc.)
    """
    client = get_langfuse_client()

    if client is None:
        return

    try:
        # Create a trace with generation
        trace = client.trace(name=name)

        # Add generation/span to the trace
        trace.generation(
            name=name,
            model=model,
            input=input_text,
            output=output_text,
            metadata=metadata or {}
        )

        logger.debug(f"Logged LLM call to Langfuse: {name} ({model})")

    except Exception as e:
        logger.error(f"Failed to log LLM call to Langfuse: {str(e)}")


def flush_langfuse():
    """
    Flush Langfuse traces to server
    Call this before application shutdown
    """
    client = get_langfuse_client()

    if client is not None:
        try:
            client.flush()
            logger.info("✓ Langfuse traces flushed successfully")
        except Exception as e:
            logger.error(f"Failed to flush Langfuse traces: {str(e)}")


# Export main functions
__all__ = ["trace", "trace_llm_call", "get_langfuse_client", "flush_langfuse"]
