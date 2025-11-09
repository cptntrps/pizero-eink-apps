"""
Memory Usage Profiling
======================

Memory profiling and analysis for Flask API and database operations.
Identifies memory leaks, excessive allocations, and optimization opportunities.
"""

import tracemalloc
import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple
import psutil
import gc

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


class MemoryProfiler:
    """Memory usage profiling for API and database operations"""

    def __init__(self):
        """Initialize memory profiler"""
        self.results = {}
        self.process = psutil.Process()

    def get_memory_usage(self) -> Dict:
        """Get current memory usage

        Returns:
            Dictionary with memory statistics
        """
        gc.collect()  # Force garbage collection
        memory_info = self.process.memory_info()

        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }

    def profile_operation(self, operation_name: str, operation_func,
                        *args, **kwargs) -> Dict:
        """Profile a single operation

        Args:
            operation_name: Name of operation
            operation_func: Function to profile
            *args: Arguments to function
            **kwargs: Keyword arguments to function

        Returns:
            Dictionary with memory profiling results
        """
        logger.info(f"Profiling: {operation_name}")

        # Start tracing
        tracemalloc.start()
        gc.collect()

        # Get baseline memory
        baseline = self.get_memory_usage()

        # Run operation
        result = operation_func(*args, **kwargs)

        # Take snapshot
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Get current memory
        after = self.get_memory_usage()

        return {
            'operation': operation_name,
            'baseline_rss_mb': baseline['rss_mb'],
            'after_rss_mb': after['rss_mb'],
            'rss_delta_mb': after['rss_mb'] - baseline['rss_mb'],
            'current_traced_mb': current / 1024 / 1024,
            'peak_traced_mb': peak / 1024 / 1024,
            'result': result
        }

    def test_api_startup(self) -> Dict:
        """Profile: API application startup"""
        def operation():
            app = create_app('testing')
            return app

        return self.profile_operation(
            'api_startup',
            operation
        )

    def test_database_initialization(self) -> Dict:
        """Profile: Database initialization"""
        def operation():
            db = MedicineDatabase(':memory:')
            return db

        return self.profile_operation(
            'database_initialization',
            operation
        )

    def test_create_medicines(self) -> Dict:
        """Profile: Creating 100 medicines"""
        def operation():
            db = MedicineDatabase(':memory:')

            for i in range(100):
                medicine = {
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
                db.add_medicine(medicine)

            return db

        return self.profile_operation(
            'create_100_medicines',
            operation
        )

    def test_get_all_medicines(self) -> Dict:
        """Profile: Retrieving all medicines"""
        db = MedicineDatabase(':memory:')

        # Create medicines first
        for i in range(100):
            medicine = {
                'id': f'med_{i:04d}',
                'name': f'Medicine {i}',
                'dosage': f'{50 + i % 50}mg',
                'time_window': 'morning',
                'window_start': '08:00',
                'window_end': '10:00',
                'days': ['mon', 'wed', 'fri'],
                'pills_per_dose': 1,
                'pills_remaining': 90,
                'low_stock_threshold': 15,
                'active': True
            }
            db.add_medicine(medicine)

        def operation():
            return db.get_all_medicines()

        return self.profile_operation(
            'get_all_medicines',
            operation
        )

    def test_api_request_handling(self) -> Dict:
        """Profile: Handling 50 API requests"""
        app = create_app('testing')
        app.config['DB_PATH'] = ':memory:'

        # Setup database
        db = MedicineDatabase(':memory:')
        for i in range(20):
            medicine = {
                'id': f'med_{i:04d}',
                'name': f'Medicine {i}',
                'dosage': f'{50 + i % 50}mg',
                'time_window': 'morning',
                'window_start': '08:00',
                'window_end': '10:00',
                'days': ['mon', 'wed', 'fri'],
                'pills_per_dose': 1,
                'pills_remaining': 90,
                'low_stock_threshold': 15,
                'active': True
            }
            db.add_medicine(medicine)

        client = app.test_client()

        def operation():
            for i in range(50):
                client.get('/api/v1/medicines')
                client.get('/api/v1/medicines/med_0000')
                client.get('/api/v1/medicines/pending')

        return self.profile_operation(
            'api_request_handling_50_requests',
            operation
        )

    def test_concurrent_database_access(self) -> Dict:
        """Profile: Concurrent database access"""
        import threading

        db = MedicineDatabase(':memory:')

        # Create medicines
        for i in range(50):
            medicine = {
                'id': f'med_{i:04d}',
                'name': f'Medicine {i}',
                'dosage': f'{50 + i % 50}mg',
                'time_window': 'morning',
                'window_start': '08:00',
                'window_end': '10:00',
                'days': ['mon', 'wed', 'fri'],
                'pills_per_dose': 1,
                'pills_remaining': 90,
                'low_stock_threshold': 15,
                'active': True
            }
            db.add_medicine(medicine)

        def worker():
            for _ in range(10):
                db.get_all_medicines()
                db.get_medicine_by_id('med_0000')

        def operation():
            threads = []
            for _ in range(5):
                t = threading.Thread(target=worker)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

        return self.profile_operation(
            'concurrent_database_access',
            operation
        )

    def test_large_response_serialization(self) -> Dict:
        """Profile: Large response serialization"""
        import json as json_lib

        def operation():
            # Create large response-like data
            data = {
                'success': True,
                'data': [
                    {
                        'id': f'med_{i:04d}',
                        'name': f'Medicine {i}',
                        'dosage': f'{50 + i % 50}mg',
                        'frequency': ['morning', 'evening'],
                        'pills_remaining': 90,
                        'active': True,
                        'metadata': {
                            'created': '2025-01-01T00:00:00',
                            'updated': '2025-01-01T00:00:00'
                        }
                    }
                    for i in range(500)
                ]
            }

            # Serialize
            json_str = json_lib.dumps(data)
            return len(json_str)

        return self.profile_operation(
            'large_response_serialization',
            operation
        )

    def run_all_profiles(self) -> Dict:
        """Run all memory profiles"""
        logger.info("=" * 80)
        logger.info("MEMORY PROFILING")
        logger.info("=" * 80)

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'profiles': []
        }

        profiles = [
            self.test_api_startup,
            self.test_database_initialization,
            self.test_create_medicines,
            self.test_get_all_medicines,
            self.test_api_request_handling,
            self.test_concurrent_database_access,
            self.test_large_response_serialization,
        ]

        for profile in profiles:
            try:
                result = profile()
                self.results['profiles'].append(result)
                logger.info(f"  RSS Delta: {result['rss_delta_mb']:.2f}MB, "
                           f"Peak Traced: {result['peak_traced_mb']:.2f}MB")
            except Exception as e:
                logger.error(f"Profile {profile.__name__} failed: {e}")

        self._calculate_summary()

        return self.results

    def _calculate_summary(self):
        """Calculate summary statistics"""
        profiles = self.results['profiles']

        if profiles:
            self.results['summary'] = {
                'total_profiles': len(profiles),
                'average_rss_delta_mb': sum(p['rss_delta_mb'] for p in profiles) / len(profiles),
                'max_rss_delta_mb': max(p['rss_delta_mb'] for p in profiles),
                'average_peak_traced_mb': sum(p['peak_traced_mb'] for p in profiles) / len(profiles),
                'max_peak_traced_mb': max(p['peak_traced_mb'] for p in profiles),
            }

    def print_summary(self):
        """Print memory profile summary"""
        if not self.results:
            logger.warning("No results to display")
            return

        summary = self.results.get('summary', {})

        print("\n" + "=" * 100)
        print("MEMORY PROFILING SUMMARY")
        print("=" * 100)
        print(f"Total Profiles: {summary.get('total_profiles', 0)}")
        print(f"Average RSS Delta: {summary.get('average_rss_delta_mb', 0):.2f}MB")
        print(f"Max RSS Delta: {summary.get('max_rss_delta_mb', 0):.2f}MB")
        print(f"Average Peak Traced: {summary.get('average_peak_traced_mb', 0):.2f}MB")
        print(f"Max Peak Traced: {summary.get('max_peak_traced_mb', 0):.2f}MB")
        print("=" * 100 + "\n")

        print("DETAILED RESULTS:")
        print("-" * 100)
        print(f"{'Operation':<40} {'RSS Delta(MB)':<20} {'Peak Traced(MB)':<20}")
        print("-" * 100)

        for profile in self.results['profiles']:
            print(f"{profile['operation']:<40} "
                  f"{profile['rss_delta_mb']:<20.2f} "
                  f"{profile['peak_traced_mb']:<20.2f}")

        print("-" * 100 + "\n")


class DisplayRenderProfiler:
    """Profile display rendering performance"""

    def __init__(self):
        """Initialize display profiler"""
        self.results = {}

    def profile_canvas_creation(self) -> Dict:
        """Profile canvas creation"""
        from display.canvas import create_canvas, DISPLAY_WIDTH, DISPLAY_HEIGHT
        from PIL import Image, ImageDraw

        start = datetime.now()

        # Create canvases multiple times
        for _ in range(100):
            img, draw = create_canvas()
            draw.text((10, 10), "Test", fill=0)

        duration = (datetime.now() - start).total_seconds() * 1000

        return {
            'operation': 'canvas_creation_100x',
            'duration_ms': duration,
            'average_per_canvas_ms': duration / 100,
            'target_met': duration < 50000  # 500ms per canvas * 100
        }

    def profile_text_rendering(self) -> Dict:
        """Profile text rendering"""
        from display.canvas import create_canvas

        start = datetime.now()

        # Render text multiple times
        for i in range(100):
            img, draw = create_canvas()
            for y in range(0, 120, 20):
                draw.text((10, y), f"Line {i}", fill=0)

        duration = (datetime.now() - start).total_seconds() * 1000

        return {
            'operation': 'text_rendering_500_texts',
            'duration_ms': duration,
            'average_per_text_ms': duration / 500,
            'target_met': duration < 50000
        }

    def profile_display_full_update(self) -> Dict:
        """Profile full display update"""
        from display.canvas import create_canvas

        start = datetime.now()

        # Simulate full display updates
        for _ in range(100):
            img, draw = create_canvas()
            # Draw a complex scene
            draw.rectangle((0, 0, 250, 122), outline=0)
            for i in range(12):
                draw.text((10 + i * 20, 10), "Med", fill=0)
                draw.text((10 + i * 20, 30), "Time", fill=0)
                draw.text((10 + i * 20, 50), "Dose", fill=0)
            # Convert to bytes (simulating display buffer)
            buffer = img.tobytes()

        duration = (datetime.now() - start).total_seconds() * 1000

        return {
            'operation': 'display_full_update_100x',
            'duration_ms': duration,
            'average_per_update_ms': duration / 100,
            'target_met': duration < 50000  # 500ms per update * 100
        }

    def run_all_profiles(self) -> Dict:
        """Run all display render profiles"""
        logger.info("=" * 80)
        logger.info("DISPLAY RENDER PROFILING")
        logger.info("=" * 80)

        self.results = {
            'timestamp': datetime.now().isoformat(),
            'profiles': []
        }

        try:
            profiles = [
                self.profile_canvas_creation,
                self.profile_text_rendering,
                self.profile_display_full_update,
            ]

            for profile in profiles:
                try:
                    result = profile()
                    self.results['profiles'].append(result)
                    logger.info(f"  {result['operation']}: {result['duration_ms']:.2f}ms, "
                               f"Target: {'PASS' if result['target_met'] else 'FAIL'}")
                except Exception as e:
                    logger.error(f"Profile {profile.__name__} failed: {e}")

        except Exception as e:
            logger.warning(f"Display profiling not available: {e}")

        return self.results

    def print_summary(self):
        """Print display render summary"""
        if not self.results.get('profiles'):
            logger.warning("No display profiles available")
            return

        print("\n" + "=" * 80)
        print("DISPLAY RENDER PROFILING SUMMARY")
        print("=" * 80)
        print(f"{'Operation':<40} {'Duration(ms)':<20} {'Target':<15}")
        print("-" * 80)

        for profile in self.results['profiles']:
            target = "PASS" if profile['target_met'] else "FAIL"
            print(f"{profile['operation']:<40} "
                  f"{profile['duration_ms']:<20.2f} "
                  f"{target:<15}")

        print("-" * 80 + "\n")


def run_memory_profiling():
    """Run memory profiling"""
    # Memory profiling
    profiler = MemoryProfiler()
    memory_results = profiler.run_all_profiles()
    profiler.print_summary()

    # Display render profiling
    display_profiler = DisplayRenderProfiler()
    display_results = display_profiler.run_all_profiles()
    display_profiler.print_summary()

    # Save results
    all_results = {
        'memory': memory_results,
        'display': display_results
    }

    output_file = '/home/user/pizerowgpio/.benchmarks/memory_profile.json'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"Results saved to {output_file}")

    return all_results


if __name__ == '__main__':
    run_memory_profiling()
