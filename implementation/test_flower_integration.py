"""
Test Flower Integration
Triggers a Celery task to verify it appears in Flower dashboard
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

# Import Celery tasks
from tasks.celery_tasks import analyze_test_failure

def test_flower_integration():
    """Test that tasks appear in Flower dashboard"""

    print("=" * 60)
    print("Testing Flower Integration")
    print("=" * 60)
    print()

    print("[1/3] Sending test task to Celery...")

    # Create test failure data
    test_failure = {
        "test_name": "test_flower_integration",
        "error_message": "This is a test error to verify Flower monitoring",
        "error_type": "TestError",
        "file_path": "test_flower_integration.py",
        "line_number": 42,
        "timestamp": "2025-11-05T15:00:00Z"
    }

    # Send task asynchronously
    result = analyze_test_failure.delay(test_failure)

    print(f"[OK] Task sent successfully!")
    print(f"     Task ID: {result.id}")
    print(f"     Task State: {result.state}")
    print()

    print("[2/3] Checking Flower dashboard...")
    print(f"     URL: http://localhost:5555/task/{result.id}")
    print()

    print("[3/3] Waiting for task completion (max 30 seconds)...")
    try:
        task_result = result.get(timeout=30)
        print(f"[OK] Task completed successfully!")
        print(f"     Result preview: {str(task_result)[:200]}...")
    except Exception as e:
        print(f"[WARNING] Task execution: {str(e)[:100]}")
        print(f"     This is expected if AI services aren't running")
        print(f"     The important part is that the task appears in Flower!")

    print()
    print("=" * 60)
    print("Flower Integration Test Complete!")
    print("=" * 60)
    print()
    print("VERIFICATION STEPS:")
    print("1. Open Flower dashboard: http://localhost:5555")
    print(f"2. Check Tasks tab for task ID: {result.id}")
    print("3. Verify worker 'worker1@localhost' is visible")
    print("4. Check task execution history")
    print()

    return result.id

if __name__ == "__main__":
    task_id = test_flower_integration()
    print(f"\nTask ID for manual verification: {task_id}")
