"""
DDN AI Analysis System - Baseline Metrics Test
Task 0.2: Document baseline metrics before RAG enhancements

This script:
1. Fetches 10 diverse test failures from MongoDB
2. Runs AI analysis on each
3. Measures performance, retrieval, quality, and cost metrics
4. Generates BASELINE-METRICS.txt report
"""

import requests
import json
import time
from datetime import datetime
import os
import statistics
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
AI_ANALYSIS_API = "http://localhost:5000/api/analyze"
DASHBOARD_API = "http://localhost:5006/api/failures"
OUTPUT_DIR = "../baseline"
RAW_RESULTS_DIR = f"{OUTPUT_DIR}/raw_results"
NUM_TESTS = 10

# Ensure output directories exist
os.makedirs(RAW_RESULTS_DIR, exist_ok=True)

def fetch_diverse_test_failures(limit=100):
    """Fetch diverse test failures from MongoDB"""
    print(f"\n📥 Fetching {limit} test failures from MongoDB...")

    try:
        response = requests.get(f"{DASHBOARD_API}?limit={limit}")
        response.raise_for_status()
        data = response.json()

        failures = data.get('failures', [])
        print(f"✅ Fetched {len(failures)} test failures")

        return failures
    except Exception as e:
        print(f"❌ Error fetching failures: {e}")
        return []

def select_diverse_cases(failures, num_tests=10):
    """Select diverse test cases covering different error types"""
    print(f"\n🎯 Selecting {num_tests} diverse test cases...")

    # Group by error type
    error_types = {}
    for failure in failures:
        error_msg = failure.get('error_message', '').lower()

        # Categorize errors
        if 'enotfound' in error_msg or 'connection' in error_msg:
            category = 'network_error'
        elif 'timeout' in error_msg:
            category = 'timeout_error'
        elif 'null' in error_msg or 'undefined' in error_msg:
            category = 'null_pointer'
        elif 'permission' in error_msg or 'access denied' in error_msg:
            category = 'permission_error'
        elif 'memory' in error_msg or 'heap' in error_msg:
            category = 'memory_error'
        elif 'assertion' in error_msg or 'expected' in error_msg:
            category = 'assertion_error'
        else:
            category = 'other_error'

        if category not in error_types:
            error_types[category] = []
        error_types[category].append(failure)

    # Select diverse cases
    selected = []
    categories = list(error_types.keys())

    print(f"📊 Found {len(categories)} error categories:")
    for cat, cases in error_types.items():
        print(f"   - {cat}: {len(cases)} cases")

    # Round-robin selection for diversity
    idx = 0
    while len(selected) < num_tests and any(error_types.values()):
        category = categories[idx % len(categories)]
        if error_types[category]:
            selected.append(error_types[category].pop(0))
        idx += 1

    print(f"✅ Selected {len(selected)} diverse test cases")
    return selected

def analyze_failure(failure, test_num):
    """Run AI analysis on a test failure and measure metrics"""
    print(f"\n🔍 Test {test_num}/{NUM_TESTS}: Analyzing failure...")
    print(f"   Test: {failure.get('test_name', 'Unknown')[:50]}...")
    print(f"   Error: {failure.get('error_message', 'Unknown')[:60]}...")

    # Prepare request payload - API only requires failure_id
    payload = {
        "failure_id": str(failure.get('_id', ''))
    }

    # Measure latency
    start_time = time.time()

    try:
        response = requests.post(
            AI_ANALYSIS_API,
            json=payload,
            timeout=120  # 2 minute timeout
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # Extract metrics
            metrics = {
                "test_number": test_num,
                "test_name": failure.get('test_name', 'Unknown'),
                "error_type": categorize_error(failure.get('error_message', '')),
                "latency_seconds": round(elapsed_time, 2),
                "status": "success",
                "response": result
            }

            print(f"   ✅ Analysis completed in {elapsed_time:.2f}s")

            # Save raw result
            save_raw_result(test_num, metrics)

            return metrics
        else:
            print(f"   ❌ API error: {response.status_code}")
            return {
                "test_number": test_num,
                "latency_seconds": round(elapsed_time, 2),
                "status": "error",
                "error_code": response.status_code
            }

    except requests.Timeout:
        elapsed_time = time.time() - start_time
        print(f"   ⏱️ Timeout after {elapsed_time:.2f}s")
        return {
            "test_number": test_num,
            "latency_seconds": round(elapsed_time, 2),
            "status": "timeout"
        }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"   ❌ Error: {str(e)[:100]}")
        return {
            "test_number": test_num,
            "latency_seconds": round(elapsed_time, 2),
            "status": "exception",
            "error": str(e)
        }

def categorize_error(error_msg):
    """Categorize error message"""
    error_msg = error_msg.lower()
    if 'enotfound' in error_msg or 'connection' in error_msg:
        return 'network_error'
    elif 'timeout' in error_msg:
        return 'timeout_error'
    elif 'null' in error_msg or 'undefined' in error_msg:
        return 'null_pointer'
    elif 'permission' in error_msg:
        return 'permission_error'
    elif 'memory' in error_msg:
        return 'memory_error'
    elif 'assertion' in error_msg:
        return 'assertion_error'
    else:
        return 'other_error'

def save_raw_result(test_num, metrics):
    """Save raw test result as JSON"""
    filename = f"{RAW_RESULTS_DIR}/test_{test_num:03d}_{metrics['error_type']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f"   💾 Saved: {filename}")

def save_test_cases(test_cases):
    """Save selected test cases"""
    filename = f"{OUTPUT_DIR}/test_cases.json"
    simplified_cases = []

    for i, case in enumerate(test_cases, 1):
        simplified_cases.append({
            "test_number": i,
            "test_name": case.get('test_name', 'Unknown'),
            "error_message": case.get('error_message', ''),
            "job_name": case.get('job_name', ''),
            "build_id": case.get('build_id', '')
        })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(simplified_cases, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved test cases: {filename}")

def generate_baseline_report(all_metrics):
    """Generate BASELINE-METRICS.txt report"""
    print("\n📊 Generating baseline metrics report...")

    # Filter successful tests
    successful_tests = [m for m in all_metrics if m['status'] == 'success']
    failed_tests = [m for m in all_metrics if m['status'] != 'success']

    # Calculate statistics
    if successful_tests:
        latencies = [m['latency_seconds'] for m in successful_tests]
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        median_latency = statistics.median(latencies)
    else:
        avg_latency = min_latency = max_latency = median_latency = 0

    # Generate report
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("DDN AI ANALYSIS SYSTEM - BASELINE METRICS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"System Version: Current (Before RAG Enhancements)")
    report_lines.append(f"Test Count: {len(all_metrics)}")
    report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("PERFORMANCE METRICS")
    report_lines.append("=" * 80)
    report_lines.append(f"Successful Analyses:    {len(successful_tests)}/{len(all_metrics)}")
    report_lines.append(f"Failed Analyses:        {len(failed_tests)}/{len(all_metrics)}")
    report_lines.append("")
    report_lines.append(f"Average Latency:        {avg_latency:.2f} seconds")
    report_lines.append(f"Min Latency:            {min_latency:.2f} seconds")
    report_lines.append(f"Max Latency:            {max_latency:.2f} seconds")
    report_lines.append(f"Median Latency:         {median_latency:.2f} seconds")
    report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("ERROR TYPE DISTRIBUTION")
    report_lines.append("=" * 80)
    error_types = {}
    for m in all_metrics:
        if 'error_type' in m:
            error_type = m['error_type']
            error_types[error_type] = error_types.get(error_type, 0) + 1

    for error_type, count in sorted(error_types.items()):
        report_lines.append(f"{error_type:.<30} {count}")
    report_lines.append("")

    report_lines.append("=" * 80)
    report_lines.append("DETAILED TEST RESULTS")
    report_lines.append("=" * 80)
    for m in all_metrics:
        report_lines.append(f"\nTest {m['test_number']}:")
        report_lines.append(f"  Test Name:     {m.get('test_name', 'Unknown')[:60]}")
        report_lines.append(f"  Error Type:    {m.get('error_type', 'Unknown')}")
        report_lines.append(f"  Latency:       {m['latency_seconds']:.2f}s")
        report_lines.append(f"  Status:        {m['status']}")

    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("NOTES")
    report_lines.append("=" * 80)
    report_lines.append("- This baseline was captured BEFORE implementing RAG enhancements")
    report_lines.append("- Enhancements to be added: Re-ranking, Hybrid Search, Caching, Query Expansion")
    report_lines.append("- Expected improvements: +20-30% accuracy, 31% cost reduction, faster retrieval")
    report_lines.append("- Compare with ENHANCED-METRICS.txt after Phase 2-5 implementation")
    report_lines.append("")
    report_lines.append("=" * 80)

    # Save report
    report_text = "\n".join(report_lines)
    filename = f"{OUTPUT_DIR}/BASELINE-METRICS.txt"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(f"✅ Baseline metrics report saved: {filename}")
    print(f"\n📄 Report Preview:")
    print(report_text)

    return report_text

def main():
    """Main execution"""
    print("=" * 80)
    print("DDN AI ANALYSIS SYSTEM - BASELINE METRICS TEST")
    print("Task 0.2: Document Baseline Metrics")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Fetch test failures
    all_failures = fetch_diverse_test_failures(limit=100)

    if not all_failures:
        print("❌ No test failures found. Cannot proceed.")
        return

    # Step 2: Select diverse test cases
    test_cases = select_diverse_cases(all_failures, NUM_TESTS)
    save_test_cases(test_cases)

    # Step 3: Run analyses
    print("\n" + "=" * 80)
    print("RUNNING BASELINE TESTS")
    print("=" * 80)

    all_metrics = []
    for i, failure in enumerate(test_cases, 1):
        metrics = analyze_failure(failure, i)
        all_metrics.append(metrics)

        # Brief pause between tests
        if i < len(test_cases):
            time.sleep(2)

    # Step 4: Generate report
    print("\n" + "=" * 80)
    print("GENERATING REPORT")
    print("=" * 80)
    generate_baseline_report(all_metrics)

    print("\n" + "=" * 80)
    print("BASELINE METRICS TEST COMPLETED")
    print("=" * 80)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📁 Results saved in: {OUTPUT_DIR}/")
    print(f"   - BASELINE-METRICS.txt")
    print(f"   - test_cases.json")
    print(f"   - raw_results/ (10 JSON files)")

if __name__ == "__main__":
    main()
