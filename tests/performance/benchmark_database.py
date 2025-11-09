"""
Database Performance Benchmarking
==================================

Comprehensive benchmarks for SQLite database operations used in the Pi Zero 2W
Medicine Tracker. Tests query performance, transaction handling, and index efficiency.

Target: Database queries <50ms
"""

import time
import sqlite3
import statistics
import os
import sys
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
import tempfile
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from db.medicine_db import MedicineDatabase


class DatabaseBenchmark:
    """Database performance benchmarking suite"""

    def __init__(self, db_path: str = None, num_iterations: int = 100):
        """Initialize benchmark suite

        Args:
            db_path: Path to test database
            num_iterations: Number of iterations for each test
        """
        if db_path is None:
            self.temp_dir = tempfile.mkdtemp()
            db_path = os.path.join(self.temp_dir, 'benchmark.db')

        self.db_path = db_path
        self.num_iterations = num_iterations
        self.results = {}
        self.db = None

    def setup(self):
        """Setup test database with sample data"""
        logger.info("Setting up test database...")
        self.db = MedicineDatabase(self.db_path)

        # Create sample medicines
        medicines = [
            {
                'id': f'med_{i:04d}',
                'name': f'Medicine {i}',
                'dosage': f'{50 + i % 50}mg',
                'time_window': 'morning' if i % 2 == 0 else 'evening',
                'window_start': '08:00' if i % 2 == 0 else '20:00',
                'window_end': '10:00' if i % 2 == 0 else '22:00',
                'days': ['mon', 'wed', 'fri'] if i % 2 == 0 else ['tue', 'thu', 'sat'],
                'pills_per_dose': 1,
                'pills_remaining': 90,
                'low_stock_threshold': 15,
                'active': True
            }
            for i in range(50)
        ]

        for med in medicines:
            self.db.add_medicine(med)

        # Add tracking records
        for med_id in [f'med_{i:04d}' for i in range(50)]:
            for days_back in range(30):  # Last 30 days
                taken_date = (datetime.now() - timedelta(days=days_back)).date()
                self.db.mark_medicine_taken(med_id, datetime.now(), taken_date)

        logger.info(f"Created test database with {len(medicines)} medicines")

    def cleanup(self):
        """Clean up test database"""
        if self.db:
            try:
                os.remove(self.db_path)
                logger.info("Cleaned up test database")
            except Exception as e:
                logger.warning(f"Failed to cleanup: {e}")

    def benchmark_operation(self, operation_name: str, operation_func,
                          *args, **kwargs) -> Dict:
        """Benchmark a single operation

        Args:
            operation_name: Name of operation for logging
            operation_func: Function to benchmark
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Returns:
            Dictionary with timing statistics
        """
        logger.info(f"Benchmarking: {operation_name}")
        times = []

        for i in range(self.num_iterations):
            start = time.perf_counter()
            operation_func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            times.append(elapsed)

        stats = {
            'operation': operation_name,
            'iterations': self.num_iterations,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'p95_ms': sorted(times)[int(len(times) * 0.95)],
            'p99_ms': sorted(times)[int(len(times) * 0.99)],
        }

        # Check target
        stats['target_met'] = stats['mean_ms'] < 50

        logger.info(f"  Mean: {stats['mean_ms']:.2f}ms, Median: {stats['median_ms']:.2f}ms, "
                   f"P95: {stats['p95_ms']:.2f}ms")

        return stats

    def test_get_all_medicines(self) -> Dict:
        """Benchmark: Get all medicines"""
        def operation():
            self.db.get_all_medicines()

        return self.benchmark_operation(
            'get_all_medicines',
            operation
        )

    def test_get_medicine_by_id(self) -> Dict:
        """Benchmark: Get single medicine by ID"""
        def operation():
            self.db.get_medicine_by_id('med_0000')

        return self.benchmark_operation(
            'get_medicine_by_id',
            operation
        )

    def test_get_pending_medicines(self) -> Dict:
        """Benchmark: Get pending medicines"""
        def operation():
            self.db.get_pending_medicines(date.today(), datetime.now())

        return self.benchmark_operation(
            'get_pending_medicines',
            operation
        )

    def test_get_low_stock_medicines(self) -> Dict:
        """Benchmark: Get low stock medicines"""
        def operation():
            self.db.get_low_stock_medicines()

        return self.benchmark_operation(
            'get_low_stock_medicines',
            operation
        )

    def test_mark_medicine_taken(self) -> Dict:
        """Benchmark: Mark medicine as taken"""
        counter = [0]

        def operation():
            med_id = f'med_{counter[0] % 50:04d}'
            self.db.mark_medicine_taken(
                med_id,
                datetime.now(),
                date.today()
            )
            counter[0] += 1

        return self.benchmark_operation(
            'mark_medicine_taken',
            operation
        )

    def test_update_medicine(self) -> Dict:
        """Benchmark: Update medicine"""
        def operation():
            med_data = self.db.get_medicine_by_id('med_0000')
            med_data['pills_remaining'] = 50
            self.db.update_medicine('med_0000', med_data)

        return self.benchmark_operation(
            'update_medicine',
            operation
        )

    def test_get_medicine_tracking_history(self) -> Dict:
        """Benchmark: Get tracking history for medicine"""
        def operation():
            self.db.get_tracking_history(medicine_id='med_0000')

        return self.benchmark_operation(
            'get_medicine_tracking_history',
            operation
        )

    def test_get_tracking_by_date_range(self) -> Dict:
        """Benchmark: Get tracking records by date range"""
        def operation():
            start_date = date.today() - timedelta(days=30)
            end_date = date.today()
            self.db.get_tracking_history(start_date=start_date, end_date=end_date)

        return self.benchmark_operation(
            'get_tracking_by_date_range',
            operation
        )

    def test_batch_mark_taken(self) -> Dict:
        """Benchmark: Batch mark multiple medicines as taken"""
        counter = [0]

        def operation():
            med_ids = [f'med_{i:04d}' for i in range(5)]
            for med_id in med_ids:
                self.db.mark_medicine_taken(med_id, datetime.now(), date.today())
            counter[0] += 1

        return self.benchmark_operation(
            'batch_mark_taken',
            operation
        )

    def test_transaction_overhead(self) -> Dict:
        """Benchmark: Transaction overhead"""
        def operation():
            with self.db.transaction():
                self.db.get_medicine_by_id('med_0000')

        return self.benchmark_operation(
            'transaction_overhead',
            operation
        )

    def run_all(self) -> Dict:
        """Run all database benchmarks"""
        logger.info("=" * 80)
        logger.info("DATABASE PERFORMANCE BENCHMARKS")
        logger.info("=" * 80)

        try:
            self.setup()

            self.results = {
                'timestamp': datetime.now().isoformat(),
                'database': self.db_path,
                'iterations': self.num_iterations,
                'benchmarks': []
            }

            # Run benchmarks
            benchmarks = [
                self.test_get_all_medicines,
                self.test_get_medicine_by_id,
                self.test_get_pending_medicines,
                self.test_get_low_stock_medicines,
                self.test_mark_medicine_taken,
                self.test_update_medicine,
                self.test_get_medicine_tracking_history,
                self.test_get_tracking_by_date_range,
                self.test_batch_mark_taken,
                self.test_transaction_overhead,
            ]

            for benchmark in benchmarks:
                result = benchmark()
                self.results['benchmarks'].append(result)

            # Calculate summary
            self._calculate_summary()

            return self.results

        finally:
            self.cleanup()

    def _calculate_summary(self):
        """Calculate summary statistics"""
        benchmarks = self.results['benchmarks']

        self.results['summary'] = {
            'total_benchmarks': len(benchmarks),
            'passed_target': sum(1 for b in benchmarks if b['target_met']),
            'failed_target': sum(1 for b in benchmarks if not b['target_met']),
            'average_mean_ms': statistics.mean(b['mean_ms'] for b in benchmarks),
            'average_p95_ms': statistics.mean(b['p95_ms'] for b in benchmarks),
            'average_p99_ms': statistics.mean(b['p99_ms'] for b in benchmarks),
        }

    def print_summary(self):
        """Print benchmark summary"""
        if not self.results:
            logger.warning("No results to display. Run benchmarks first.")
            return

        summary = self.results.get('summary', {})

        print("\n" + "=" * 80)
        print("DATABASE BENCHMARK SUMMARY")
        print("=" * 80)
        print(f"Total Benchmarks: {summary.get('total_benchmarks', 0)}")
        print(f"Target Met: {summary.get('passed_target', 0)}")
        print(f"Target Failed: {summary.get('failed_target', 0)}")
        print(f"Average Mean Time: {summary.get('average_mean_ms', 0):.2f}ms")
        print(f"Average P95 Time: {summary.get('average_p95_ms', 0):.2f}ms")
        print(f"Average P99 Time: {summary.get('average_p99_ms', 0):.2f}ms")
        print("=" * 80 + "\n")

        print("DETAILED RESULTS:")
        print("-" * 80)
        print(f"{'Operation':<40} {'Mean':<10} {'P95':<10} {'Status':<10}")
        print("-" * 80)

        for bench in self.results['benchmarks']:
            status = "PASS" if bench['target_met'] else "FAIL"
            print(f"{bench['operation']:<40} {bench['mean_ms']:<10.2f} "
                  f"{bench['p95_ms']:<10.2f} {status:<10}")

        print("-" * 80 + "\n")


def run_benchmarks():
    """Run database benchmarks"""
    benchmark = DatabaseBenchmark(num_iterations=100)
    results = benchmark.run_all()
    benchmark.print_summary()

    # Save results to JSON
    output_file = '/home/user/pizerowgpio/.benchmarks/database_benchmark.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {output_file}")

    return results


if __name__ == '__main__':
    run_benchmarks()
