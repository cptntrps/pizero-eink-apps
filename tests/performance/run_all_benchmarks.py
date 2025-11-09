#!/usr/bin/env python3
"""
Master Performance Benchmark Runner
====================================

Runs all performance tests and generates comprehensive report.

Usage:
    python tests/performance/run_all_benchmarks.py
"""

import sys
import os
import logging
import json
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def run_all_benchmarks():
    """Run all performance benchmarks and generate report"""

    print("\n" + "=" * 80)
    print("PI ZERO 2W MEDICINE TRACKER - PERFORMANCE BENCHMARKING SUITE")
    print("=" * 80 + "\n")

    start_time = time.time()
    results = {
        'timestamp': datetime.now().isoformat(),
        'benchmarks': {}
    }

    # Ensure benchmarks directory exists
    benchmarks_dir = '/home/user/pizerowgpio/.benchmarks'
    os.makedirs(benchmarks_dir, exist_ok=True)

    # 1. Database Benchmarks
    print("\n" + "-" * 80)
    print("1. RUNNING DATABASE PERFORMANCE BENCHMARKS")
    print("-" * 80)
    try:
        from tests.performance.benchmark_database import run_benchmarks as db_bench
        db_results = db_bench()
        results['benchmarks']['database'] = db_results
        print("✓ Database benchmarks completed")
    except Exception as e:
        logger.error(f"Database benchmarks failed: {e}")
        results['benchmarks']['database'] = {'error': str(e)}

    # 2. API Benchmarks
    print("\n" + "-" * 80)
    print("2. RUNNING API RESPONSE TIME BENCHMARKS")
    print("-" * 80)
    try:
        from tests.performance.benchmark_api import run_benchmarks as api_bench
        api_results = api_bench()
        results['benchmarks']['api'] = api_results
        print("✓ API benchmarks completed")
    except Exception as e:
        logger.error(f"API benchmarks failed: {e}")
        results['benchmarks']['api'] = {'error': str(e)}

    # 3. Load Tests
    print("\n" + "-" * 80)
    print("3. RUNNING LOAD TESTS (50+ CONCURRENT USERS)")
    print("-" * 80)
    try:
        from tests.performance.load_test import run_load_tests
        load_results = run_load_tests()
        results['benchmarks']['load_test'] = load_results
        print("✓ Load tests completed")
    except Exception as e:
        logger.error(f"Load tests failed: {e}")
        results['benchmarks']['load_test'] = {'error': str(e)}

    # 4. Memory Profiling
    print("\n" + "-" * 80)
    print("4. RUNNING MEMORY USAGE PROFILING")
    print("-" * 80)
    try:
        from tests.performance.memory_profile import run_memory_profiling
        memory_results = run_memory_profiling()
        results['benchmarks']['memory'] = memory_results
        print("✓ Memory profiling completed")
    except Exception as e:
        logger.error(f"Memory profiling failed: {e}")
        results['benchmarks']['memory'] = {'error': str(e)}

    # Calculate total duration
    total_duration = time.time() - start_time
    results['total_duration_seconds'] = total_duration

    # Save comprehensive results
    print("\n" + "-" * 80)
    print("5. SAVING RESULTS")
    print("-" * 80)

    output_file = os.path.join(benchmarks_dir, 'complete_benchmark_results.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"✓ Results saved to: {output_file}")

    # Print summary
    print_summary(results, total_duration)

    return results


def print_summary(results: dict, total_duration: float):
    """Print comprehensive benchmark summary"""

    print("\n" + "=" * 80)
    print("BENCHMARK EXECUTION SUMMARY")
    print("=" * 80)

    print(f"\nTotal Execution Time: {total_duration:.2f} seconds ({total_duration/60:.2f} minutes)")
    print(f"Timestamp: {results['timestamp']}")

    print("\nTest Suite Status:")
    print("-" * 80)

    benchmarks = results.get('benchmarks', {})

    # Database summary
    if 'database' in benchmarks:
        db = benchmarks['database']
        if 'error' in db:
            print("✗ Database Benchmarks: FAILED")
        else:
            summary = db.get('summary', {})
            passed = summary.get('passed_target', 0)
            failed = summary.get('failed_target', 0)
            status = "PASS" if failed == 0 else "PARTIAL"
            print(f"✓ Database Benchmarks: {status} ({passed}/{passed+failed} targets met)")

    # API summary
    if 'api' in benchmarks:
        api = benchmarks['api']
        if 'error' in api:
            print("✗ API Benchmarks: FAILED")
        else:
            summary = api.get('summary', {})
            passed = summary.get('passed_target', 0)
            failed = summary.get('failed_target', 0)
            status = "PASS" if failed == 0 else "PARTIAL"
            print(f"✓ API Benchmarks: {status} ({passed}/{passed+failed} targets met)")

    # Load test summary
    if 'load_test' in benchmarks:
        lt = benchmarks['load_test']
        if 'error' in lt:
            print("✗ Load Tests: FAILED")
        else:
            concurrent = lt.get('concurrent', {})
            target = concurrent.get('load_test_target', {})
            status = "PASS" if target.get('met', False) else "FAIL"
            print(f"✓ Load Tests (50 users): {status}")

    # Memory summary
    if 'memory' in benchmarks:
        mem = benchmarks['memory']
        if 'error' in mem:
            print("✗ Memory Profiling: FAILED")
        else:
            print("✓ Memory Profiling: COMPLETE")

    print("\n" + "=" * 80)
    print("OUTPUT FILES")
    print("=" * 80)

    benchmarks_dir = '/home/user/pizerowgpio/.benchmarks'
    benchmark_files = [
        'complete_benchmark_results.json',
        'database_benchmark.json',
        'api_benchmark.json',
        'load_test.json',
        'memory_profile.json'
    ]

    for file in benchmark_files:
        filepath = os.path.join(benchmarks_dir, file)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {file:<40} ({size:>8} bytes)")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    print("""
1. Review the complete results:
   cat .benchmarks/complete_benchmark_results.json

2. Check performance targets:
   - Database queries: <50ms
   - API responses: <100ms
   - Display renders: <500ms
   - 50+ concurrent users: Handle successfully

3. Identify bottlenecks and optimize:
   - Run individual benchmark files for detailed analysis
   - Profile slow operations with tracemalloc
   - Implement recommended optimizations

4. Document findings:
   - Update docs/PERFORMANCE_REPORT.md with actual results
   - Create optimization plan
   - Track improvements over time

5. Setup continuous monitoring:
   - Add performance checks to CI/CD pipeline
   - Monitor production metrics
   - Alert on performance degradation
""")

    print("=" * 80 + "\n")


if __name__ == '__main__':
    try:
        results = run_all_benchmarks()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nBenchmarking interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Benchmark suite failed: {e}", exc_info=True)
        sys.exit(1)
