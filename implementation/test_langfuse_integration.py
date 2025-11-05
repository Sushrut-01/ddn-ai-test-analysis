"""
Test Langfuse Integration
Verifies that traces appear in Langfuse dashboard
"""
import os
import time
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

# Import tracing module
from langfuse_tracing import trace, trace_llm_call, get_langfuse_client, flush_langfuse


@trace(name="test_function_with_decorator")
def test_traced_function(test_name: str, test_value: int):
    """Test function with @trace decorator"""
    print(f"   Executing {test_name} with value {test_value}")
    time.sleep(0.5)  # Simulate some work
    result = {"status": "success", "value": test_value * 2}
    return result


def test_manual_llm_logging():
    """Test manual LLM call logging"""
    print("[Test 2] Manual LLM Call Logging")

    # Simulate an LLM API call
    model_name = "gemini-1.5-flash"
    prompt = "Analyze this test failure: TimeoutError in test_database_connection"
    response = "This error suggests the database connection timed out. Check network connectivity and database server status."

    # Log to Langfuse
    trace_llm_call(
        name="test_gemini_analysis",
        model=model_name,
        input_text=prompt,
        output_text=response,
        metadata={
            "input_tokens": 15,
            "output_tokens": 25,
            "latency_ms": 450,
            "cost_usd": 0.0001,
        },
    )

    print("   ✓ LLM call logged to Langfuse")
    print(f"     Model: {model_name}")
    print(f"     Prompt length: {len(prompt)} chars")
    print(f"     Response length: {len(response)} chars")


def main():
    """Run all Langfuse integration tests"""
    print("=" * 70)
    print("Testing Langfuse Integration")
    print("=" * 70)
    print()

    # Check if Langfuse is enabled
    enabled = os.getenv("LANGFUSE_ENABLED", "false").lower() == "true"
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    host = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

    print(f"Configuration:")
    print(f"  - Langfuse Enabled: {enabled}")
    print(f"  - Langfuse Host: {host}")
    print(f"  - Public Key: {public_key[:20]}..." if public_key else "  - Public Key: NOT SET")
    print()

    if not enabled:
        print("⚠️  WARNING: Langfuse is DISABLED")
        print("   Set LANGFUSE_ENABLED=true in .env to enable tracing")
        print()
        return

    # Initialize client
    print("[Initialization] Creating Langfuse client...")
    client = get_langfuse_client()

    if client is None:
        print("✗ Failed to initialize Langfuse client")
        print("  Check your .env configuration")
        return

    print("✓ Langfuse client initialized successfully")
    print()

    # Test 1: Decorated function
    print("[Test 1] Function with @trace Decorator")
    try:
        result = test_traced_function("integration_test", 42)
        print(f"   ✓ Function executed successfully")
        print(f"     Result: {result}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    print()

    # Test 2: Manual LLM logging
    try:
        test_manual_llm_logging()
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")

    print()

    # Flush traces to server
    print("[Finalization] Flushing traces to Langfuse...")
    flush_langfuse()
    print("✓ Traces flushed")

    print()
    print("=" * 70)
    print("Langfuse Integration Test Complete!")
    print("=" * 70)
    print()
    print("VERIFICATION STEPS:")
    print(f"1. Open Langfuse dashboard: {host}")
    print("2. Navigate to 'Traces' tab")
    print("3. Look for traces:")
    print("   - test_function_with_decorator")
    print("   - test_gemini_analysis")
    print("4. Check trace details, metadata, and timing")
    print()
    print("If traces don't appear immediately, wait 10-15 seconds and refresh")
    print()


if __name__ == "__main__":
    main()
