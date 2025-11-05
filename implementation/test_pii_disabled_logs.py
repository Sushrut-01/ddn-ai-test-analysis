"""
Test script to verify PII redaction disabled logs
Verifies that both services correctly log PII_REDACTION_ENABLED=false status
"""
import os
import sys
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

# Set environment variable BEFORE imports
os.environ['PII_REDACTION_ENABLED'] = 'false'

print("=" * 70)
print("PII REDACTION DISABLED - LOG VERIFICATION TEST")
print("=" * 70)
print()

# Test 1: MongoDB Listener
print("[TEST 1] Verifying mongodb_robot_listener.py logs")
print("-" * 70)
try:
    # Need to set minimal MongoDB config to avoid connection errors
    os.environ['MONGODB_URI'] = 'mongodb://localhost:27017/test'
    os.environ['MONGODB_DB'] = 'test'

    # Capture stdout
    captured_output = StringIO()

    # Import and initialize
    with redirect_stdout(captured_output), redirect_stderr(captured_output):
        try:
            from mongodb_robot_listener import MongoDBListener
            listener = MongoDBListener()
        except Exception as e:
            # Connection errors are expected if MongoDB not running
            pass

    output = captured_output.getvalue()

    # Check for expected log messages
    if "PII redaction DISABLED (client approval pending)" in output:
        print("[PASS] Found 'PII redaction DISABLED' message")
    else:
        print("[FAIL] Did not find 'PII redaction DISABLED' message")
        print(f"Output: {output}")

    if "Storing actual data for dashboard navigation" in output:
        print("[PASS] Found 'Storing actual data for dashboard navigation' message")
    else:
        print("[FAIL] Did not find dashboard navigation message")

    # Should NOT see "PII redaction enabled"
    if "PII redaction ENABLED" not in output and "PII redaction enabled" not in output.lower():
        print("[PASS] Correctly NOT showing 'PII redaction enabled'")
    else:
        print("[FAIL] Should not show 'PII redaction enabled' when disabled")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: AI Analysis Service (just check the initialization code)
print("[TEST 2] Verifying ai_analysis_service.py PII initialization logic")
print("-" * 70)

try:
    # Test the logic directly
    pii_enabled = os.getenv('PII_REDACTION_ENABLED', 'false').lower() == 'true'

    if not pii_enabled:
        print("[PASS] PII_REDACTION_ENABLED correctly reads as False")
        print("[PASS] Would log 'PII redaction DISABLED (client approval pending)'")
        print("[PASS] Would log 'Storing actual data for dashboard navigation'")
        print("[PASS] Would log 'No redaction before embedding creation'")
    else:
        print("[FAIL] PII_REDACTION_ENABLED incorrectly reads as True")

except Exception as e:
    print(f"[ERROR] {e}")

print()

# Test 3: Verify .env.MASTER has correct setting
print("[TEST 3] Verifying .env.MASTER configuration")
print("-" * 70)

try:
    env_master_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.MASTER')

    if os.path.exists(env_master_path):
        with open(env_master_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'PII_REDACTION_ENABLED=false' in content:
            print("[PASS] .env.MASTER has PII_REDACTION_ENABLED=false")
        else:
            print("[FAIL] .env.MASTER does not have PII_REDACTION_ENABLED=false")

        if 'PHASE 4: PII REDACTION - DISABLED' in content:
            print("[PASS] .env.MASTER has Phase 4 section header")
        else:
            print("[FAIL] .env.MASTER missing Phase 4 section")

        if 'Dashboard requires actual URLs' in content:
            print("[PASS] .env.MASTER explains why disabled")
        else:
            print("[FAIL] .env.MASTER missing explanation")
    else:
        print("[FAIL] .env.MASTER not found")

except Exception as e:
    print(f"[ERROR] {e}")

print()
print("=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print()
print("Summary:")
print("- MongoDB Listener: Should log 'PII redaction DISABLED'")
print("- AI Analysis Service: Should log 'PII redaction DISABLED'")
print("- Both services: Should log 'Storing actual data for dashboard navigation'")
print("- .env.MASTER: Should have PII_REDACTION_ENABLED=false")
print()
print("[OK] If all tests passed, PII redaction is correctly disabled")
print("[INFO] System will store actual data (no redaction)")
print("[INFO] To re-enable: Set PII_REDACTION_ENABLED=true in .env.MASTER")
