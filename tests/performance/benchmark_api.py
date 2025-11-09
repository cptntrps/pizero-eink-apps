"""
API Performance Benchmarking
============================

Comprehensive benchmarks for Flask API endpoints. Tests response times for all
major API operations including medicines management, tracking, and configuration.

Target: API responses <100ms
"""

import time
import statistics
import os
import sys
import logging
import json
from datetime import datetime, date, timedelta
from typing import Dict, List
import tempfile

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api import create_app
from db.medicine_db import MedicineDatabase


class APIBenchmark:
    """API performance benchmarking suite"""

    def __init__(self, num_iterations: int = 100, db_path: str = None):
        """Initialize API benchmark suite

        Args:
            num_iterations: Number of iterations per test
            db_path: Path to test database
        """
        self.num_iterations = num_iterations
        self.db_path = db_path or ':memory:'
        self.app = None
        self.client = None
        self.results = {}

    def setup(self):
        """Setup test Flask app and database"""
        logger.info("Setting up test API...")

        # Create Flask test app
        self.app = create_app('testing')
        self.app.config['DB_PATH'] = self.db_path
        self.client = self.app.test_client()

        # Create test database with sample data
        self._setup_test_data()

        logger.info("API test environment ready")

    def _setup_test_data(self):
        """Setup test data in database"""
        db = MedicineDatabase(self.db_path)

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
            for i in range(20)  # Fewer medicines for API tests
        ]

        for med in medicines:
            db.add_medicine(med)

        logger.info(f"Created {len(medicines)} test medicines")

    def benchmark_endpoint(self, endpoint_name: str, method: str, endpoint: str,
                         data: dict = None, expected_status: int = 200) -> Dict:
        """Benchmark a single API endpoint

        Args:
            endpoint_name: Name for logging
            method: HTTP method (GET, POST, etc)
            endpoint: API endpoint path
            data: Request body data
            expected_status: Expected HTTP status code

        Returns:
            Dictionary with timing statistics
        """
        logger.info(f"Benchmarking: {endpoint_name}")
        times = []
        errors = 0

        for i in range(self.num_iterations):
            start = time.perf_counter()

            try:
                if method == 'GET':
                    response = self.client.get(endpoint)
                elif method == 'POST':
                    response = self.client.post(
                        endpoint,
                        json=data,
                        content_type='application/json'
                    )
                elif method == 'PUT':
                    response = self.client.put(
                        endpoint,
                        json=data,
                        content_type='application/json'
                    )
                elif method == 'PATCH':
                    response = self.client.patch(
                        endpoint,
                        json=data,
                        content_type='application/json'
                    )
                elif method == 'DELETE':
                    response = self.client.delete(endpoint)
                else:
                    raise ValueError(f"Unknown method: {method}")

                elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

                if response.status_code != expected_status:
                    errors += 1

                times.append(elapsed)

            except Exception as e:
                logger.error(f"Request failed: {e}")
                errors += 1

        if not times:
            return {
                'endpoint': endpoint_name,
                'method': method,
                'iterations': self.num_iterations,
                'error_rate': 100.0,
                'mean_ms': 0,
                'target_met': False
            }

        stats = {
            'endpoint': endpoint_name,
            'method': method,
            'path': endpoint,
            'iterations': self.num_iterations,
            'errors': errors,
            'error_rate': (errors / self.num_iterations) * 100,
            'min_ms': min(times),
            'max_ms': max(times),
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'stdev_ms': statistics.stdev(times) if len(times) > 1 else 0,
            'p95_ms': sorted(times)[int(len(times) * 0.95)],
            'p99_ms': sorted(times)[int(len(times) * 0.99)],
        }

        # Check target (< 100ms)
        stats['target_met'] = stats['mean_ms'] < 100

        logger.info(f"  Mean: {stats['mean_ms']:.2f}ms, Median: {stats['median_ms']:.2f}ms, "
                   f"P95: {stats['p95_ms']:.2f}ms, Errors: {errors}")

        return stats

    # ========================================================================
    # MEDICINE ENDPOINTS
    # ========================================================================

    def test_get_medicines(self) -> Dict:
        """Benchmark: GET /api/v1/medicines"""
        return self.benchmark_endpoint(
            'GET /api/v1/medicines',
            'GET',
            '/api/v1/medicines'
        )

    def test_get_single_medicine(self) -> Dict:
        """Benchmark: GET /api/v1/medicines/{id}"""
        return self.benchmark_endpoint(
            'GET /api/v1/medicines/{id}',
            'GET',
            '/api/v1/medicines/med_0000'
        )

    def test_create_medicine(self) -> Dict:
        """Benchmark: POST /api/v1/medicines"""
        counter = [0]

        def operation():
            data = {
                'id': f'test_med_{counter[0]:04d}',
                'name': f'Test Medicine {counter[0]}',
                'dosage': '50mg',
                'time_window': 'morning',
                'window_start': '08:00',
                'window_end': '10:00',
                'days': ['mon', 'wed', 'fri'],
                'pills_per_dose': 1,
                'pills_remaining': 90,
                'low_stock_threshold': 15,
                'active': True
            }
            counter[0] += 1
            return data

        times = []
        errors = 0

        for i in range(self.num_iterations):
            start = time.perf_counter()
            try:
                response = self.client.post(
                    '/api/v1/medicines',
                    json=operation(),
                    content_type='application/json'
                )
                elapsed = (time.perf_counter() - start) * 1000
                if response.status_code != 201:
                    errors += 1
                times.append(elapsed)
            except Exception as e:
                logger.error(f"Create medicine failed: {e}")
                errors += 1

        if not times:
            return {
                'endpoint': 'POST /api/v1/medicines',
                'method': 'POST',
                'error_rate': 100.0,
                'target_met': False
            }

        stats = {
            'endpoint': 'POST /api/v1/medicines',
            'method': 'POST',
            'path': '/api/v1/medicines',
            'iterations': self.num_iterations,
            'errors': errors,
            'error_rate': (errors / self.num_iterations) * 100,
            'mean_ms': statistics.mean(times),
            'median_ms': statistics.median(times),
            'p95_ms': sorted(times)[int(len(times) * 0.95)],
            'p99_ms': sorted(times)[int(len(times) * 0.99)],
            'target_met': statistics.mean(times) < 100
        }

        logger.info(f"  Mean: {stats['mean_ms']:.2f}ms, P95: {stats['p95_ms']:.2f}ms")

        return stats

    def test_update_medicine(self) -> Dict:
        """Benchmark: PUT /api/v1/medicines/{id}"""
        data = {
            'id': 'med_0000',
            'name': 'Updated Medicine',
            'dosage': '75mg',
            'time_window': 'morning',
            'window_start': '08:00',
            'window_end': '10:00',
            'days': ['mon', 'wed', 'fri'],
            'pills_per_dose': 1,
            'pills_remaining': 80,
            'low_stock_threshold': 15,
            'active': True
        }

        return self.benchmark_endpoint(
            'PUT /api/v1/medicines/{id}',
            'PUT',
            '/api/v1/medicines/med_0000',
            data=data,
            expected_status=200
        )

    def test_patch_medicine(self) -> Dict:
        """Benchmark: PATCH /api/v1/medicines/{id}"""
        data = {'pills_remaining': 75}

        return self.benchmark_endpoint(
            'PATCH /api/v1/medicines/{id}',
            'PATCH',
            '/api/v1/medicines/med_0000',
            data=data,
            expected_status=200
        )

    def test_get_pending_medicines(self) -> Dict:
        """Benchmark: GET /api/v1/medicines/pending"""
        return self.benchmark_endpoint(
            'GET /api/v1/medicines/pending',
            'GET',
            '/api/v1/medicines/pending'
        )

    def test_get_low_stock(self) -> Dict:
        """Benchmark: GET /api/v1/medicines/low-stock"""
        return self.benchmark_endpoint(
            'GET /api/v1/medicines/low-stock',
            'GET',
            '/api/v1/medicines/low-stock'
        )

    # ========================================================================
    # TRACKING ENDPOINTS
    # ========================================================================

    def test_mark_medicine_taken(self) -> Dict:
        """Benchmark: POST /api/v1/medicines/{id}/take"""
        data = {'timestamp': datetime.now().isoformat()}

        return self.benchmark_endpoint(
            'POST /api/v1/medicines/{id}/take',
            'POST',
            '/api/v1/medicines/med_0000/take',
            data=data,
            expected_status=201
        )

    def test_batch_mark_taken(self) -> Dict:
        """Benchmark: POST /api/v1/medicines/batch-take"""
        data = {
            'medicine_ids': ['med_0000', 'med_0001', 'med_0002'],
            'timestamp': datetime.now().isoformat()
        }

        return self.benchmark_endpoint(
            'POST /api/v1/medicines/batch-take',
            'POST',
            '/api/v1/medicines/batch-take',
            data=data,
            expected_status=200
        )

    # ========================================================================
    # HEALTH & INFO ENDPOINTS
    # ========================================================================

    def test_health_check(self) -> Dict:
        """Benchmark: GET /api/v1/health"""
        return self.benchmark_endpoint(
            'GET /api/v1/health',
            'GET',
            '/api/v1/health'
        )

    def test_api_root(self) -> Dict:
        """Benchmark: GET /api/v1/"""
        return self.benchmark_endpoint(
            'GET /api/v1/',
            'GET',
            '/api/v1/'
        )

    def run_all(self) -> Dict:
        """Run all API benchmarks"""
        logger.info("=" * 80)
        logger.info("API PERFORMANCE BENCHMARKS")
        logger.info("=" * 80)

        try:
            self.setup()

            self.results = {
                'timestamp': datetime.now().isoformat(),
                'iterations': self.num_iterations,
                'benchmarks': []
            }

            # Run benchmarks
            benchmarks = [
                self.test_api_root,
                self.test_health_check,
                self.test_get_medicines,
                self.test_get_single_medicine,
                self.test_get_pending_medicines,
                self.test_get_low_stock,
                self.test_create_medicine,
                self.test_update_medicine,
                self.test_patch_medicine,
                self.test_mark_medicine_taken,
                self.test_batch_mark_taken,
            ]

            for benchmark in benchmarks:
                try:
                    result = benchmark()
                    self.results['benchmarks'].append(result)
                except Exception as e:
                    logger.error(f"Benchmark {benchmark.__name__} failed: {e}")

            # Calculate summary
            self._calculate_summary()

            return self.results

        finally:
            pass  # No cleanup needed for in-memory database

    def _calculate_summary(self):
        """Calculate summary statistics"""
        benchmarks = self.results['benchmarks']

        self.results['summary'] = {
            'total_benchmarks': len(benchmarks),
            'passed_target': sum(1 for b in benchmarks if b.get('target_met', False)),
            'failed_target': sum(1 for b in benchmarks if not b.get('target_met', True)),
            'average_mean_ms': statistics.mean(b['mean_ms'] for b in benchmarks if 'mean_ms' in b),
            'average_p95_ms': statistics.mean(b['p95_ms'] for b in benchmarks if 'p95_ms' in b),
        }

    def print_summary(self):
        """Print benchmark summary"""
        if not self.results:
            logger.warning("No results to display. Run benchmarks first.")
            return

        summary = self.results.get('summary', {})

        print("\n" + "=" * 80)
        print("API BENCHMARK SUMMARY")
        print("=" * 80)
        print(f"Total Endpoints: {summary.get('total_benchmarks', 0)}")
        print(f"Target Met: {summary.get('passed_target', 0)}")
        print(f"Target Failed: {summary.get('failed_target', 0)}")
        print(f"Average Response Time: {summary.get('average_mean_ms', 0):.2f}ms")
        print(f"Average P95 Time: {summary.get('average_p95_ms', 0):.2f}ms")
        print("=" * 80 + "\n")

        print("DETAILED RESULTS:")
        print("-" * 100)
        print(f"{'Endpoint':<40} {'Method':<6} {'Mean(ms)':<12} {'P95(ms)':<12} {'Status':<10}")
        print("-" * 100)

        for bench in self.results['benchmarks']:
            status = "PASS" if bench.get('target_met', False) else "FAIL"
            endpoint = bench.get('endpoint', 'Unknown')
            method = bench.get('method', 'N/A')
            mean_ms = bench.get('mean_ms', 0)
            p95_ms = bench.get('p95_ms', 0)

            print(f"{endpoint:<40} {method:<6} {mean_ms:<12.2f} {p95_ms:<12.2f} {status:<10}")

        print("-" * 100 + "\n")


def run_benchmarks():
    """Run API benchmarks"""
    benchmark = APIBenchmark(num_iterations=100)
    results = benchmark.run_all()
    benchmark.print_summary()

    # Save results to JSON
    output_file = '/home/user/pizerowgpio/.benchmarks/api_benchmark.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results saved to {output_file}")

    return results


if __name__ == '__main__':
    run_benchmarks()
