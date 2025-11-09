"""
Integration Test Configuration and Shared Fixtures
Provides utilities for end-to-end testing across app and API layers
"""

import os
import sys
import json
import tempfile
import shutil
import sqlite3
import threading
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from api import create_app
from db.medicine_db import MedicineDatabase


# ============================================================================
# Test Database Setup
# ============================================================================

@pytest.fixture(scope='function')
def integration_test_db():
    """Create isolated test database for integration tests"""
    temp_dir = tempfile.mkdtemp(prefix='pizero_integration_')
    db_path = os.path.join(temp_dir, 'integration_test.db')

    # Set environment variable
    os.environ['PIZERO_MEDICINE_DB'] = db_path

    db = MedicineDatabase(db_path=db_path)

    yield db, db_path, temp_dir

    # Cleanup
    db.close()
    shutil.rmtree(temp_dir, ignore_errors=True)
    if 'PIZERO_MEDICINE_DB' in os.environ:
        del os.environ['PIZERO_MEDICINE_DB']


@pytest.fixture(scope='function')
def integration_app(integration_test_db):
    """Create Flask app for integration testing"""
    db, db_path, temp_dir = integration_test_db

    os.environ['PIZERO_MEDICINE_DB'] = db_path
    os.environ['FLASK_ENV'] = 'testing'

    flask_app = create_app('testing')
    flask_app.config['TESTING'] = True
    flask_app.config['DATABASE_PATH'] = db_path

    yield flask_app

    # Cleanup
    if 'PIZERO_MEDICINE_DB' in os.environ:
        del os.environ['PIZERO_MEDICINE_DB']
    if 'FLASK_ENV' in os.environ:
        del os.environ['FLASK_ENV']


@pytest.fixture(scope='function')
def integration_client(integration_app, integration_test_db):
    """Create Flask test client for integration testing"""
    db, db_path, temp_dir = integration_test_db

    with integration_app.test_client() as test_client:
        yield test_client, db


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def comprehensive_medicine_set():
    """Comprehensive set of medicines for thorough testing"""
    return [
        {
            "id": "med_aspirin_001",
            "name": "Aspirin",
            "dosage": "81mg",
            "time_window": "morning",
            "window_start": "08:00",
            "window_end": "09:00",
            "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            "with_food": True,
            "notes": "Take with breakfast",
            "pills_remaining": 100,
            "pills_per_dose": 1,
            "low_stock_threshold": 10,
            "active": True
        },
        {
            "id": "med_vitamin_d_002",
            "name": "Vitamin D",
            "dosage": "1000 IU",
            "time_window": "morning",
            "window_start": "08:00",
            "window_end": "09:00",
            "days": ["mon", "wed", "fri"],
            "with_food": False,
            "notes": "Mon-Wed-Fri only",
            "pills_remaining": 50,
            "pills_per_dose": 1,
            "low_stock_threshold": 15,
            "active": True
        },
        {
            "id": "med_bp_med_003",
            "name": "Blood Pressure Med",
            "dosage": "10mg",
            "time_window": "evening",
            "window_start": "18:00",
            "window_end": "19:00",
            "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            "with_food": False,
            "notes": "Evening dose - critical",
            "pills_remaining": 5,
            "pills_per_dose": 1,
            "low_stock_threshold": 10,
            "active": True
        },
        {
            "id": "med_thyroid_004",
            "name": "Thyroid Medication",
            "dosage": "75mcg",
            "time_window": "morning",
            "window_start": "07:00",
            "window_end": "08:00",
            "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            "with_food": False,
            "notes": "Take 30 mins before food",
            "pills_remaining": 200,
            "pills_per_dose": 1,
            "low_stock_threshold": 20,
            "active": True
        },
        {
            "id": "med_multivitamin_005",
            "name": "Multivitamin",
            "dosage": "1 tablet",
            "time_window": "afternoon",
            "window_start": "12:00",
            "window_end": "14:00",
            "days": ["tue", "thu", "sat"],
            "with_food": True,
            "notes": "With lunch",
            "pills_remaining": 80,
            "pills_per_dose": 1,
            "low_stock_threshold": 25,
            "active": True
        },
        {
            "id": "med_antihistamine_006",
            "name": "Antihistamine",
            "dosage": "10mg",
            "time_window": "night",
            "window_start": "21:00",
            "window_end": "22:00",
            "days": ["mon", "tue", "wed", "thu", "fri"],
            "with_food": False,
            "notes": "As needed for allergies",
            "pills_remaining": 30,
            "pills_per_dose": 1,
            "low_stock_threshold": 5,
            "active": True
        },
        {
            "id": "med_inactive_007",
            "name": "Inactive Medicine",
            "dosage": "50mg",
            "time_window": "morning",
            "window_start": "08:00",
            "window_end": "09:00",
            "days": ["mon", "tue", "wed"],
            "with_food": False,
            "notes": "No longer taking this",
            "pills_remaining": 30,
            "pills_per_dose": 1,
            "low_stock_threshold": 10,
            "active": False
        }
    ]


@pytest.fixture(scope='session')
def stress_test_medicines():
    """Generate large set of medicines for stress testing"""
    medicines = []
    for i in range(50):
        medicines.append({
            "id": f"med_stress_{i:03d}",
            "name": f"Stress Test Medicine {i}",
            "dosage": f"{(i % 5 + 1) * 10}mg",
            "time_window": ["morning", "afternoon", "evening", "night"][i % 4],
            "window_start": ["08:00", "12:00", "18:00", "21:00"][i % 4],
            "window_end": ["09:00", "13:00", "19:00", "22:00"][i % 4],
            "days": ["mon", "wed", "fri"] if i % 2 == 0 else ["tue", "thu", "sat"],
            "with_food": i % 3 == 0,
            "notes": f"Stress test medicine {i}",
            "pills_remaining": 100 - (i * 2),
            "pills_per_dose": (i % 3) + 1,
            "low_stock_threshold": 20,
            "active": True if i < 40 else False
        })
    return medicines


# ============================================================================
# Helper Fixtures for Data Operations
# ============================================================================

@pytest.fixture
def seed_database():
    """Helper to populate database with test data"""
    def _seed(db, medicines):
        for medicine in medicines:
            db.add_medicine(medicine)
        return len(medicines)

    return _seed


@pytest.fixture
def concurrent_operations():
    """Helper for concurrent database operations"""
    def _run_concurrent(operations, max_workers=10):
        """
        Execute operations concurrently

        Args:
            operations: List of tuples (operation_func, args)
            max_workers: Max concurrent threads

        Returns:
            List of results
        """
        results = []
        exceptions = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(op[0], *op[1]): i
                for i, op in enumerate(operations)
            }

            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    exceptions.append((futures[future], e))

        return results, exceptions

    return _run_concurrent


# ============================================================================
# Database State Verification Helpers
# ============================================================================

@pytest.fixture
def verify_db_consistency():
    """Helper to verify database consistency"""
    def _verify(db_path):
        """
        Verify database integrity and consistency

        Returns:
            Dict with consistency checks
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            checks = {
                'foreign_keys_enabled': True,
                'integrity_check': None,
                'foreign_key_check': None,
                'tables': {},
                'indexes': {}
            }

            # Check foreign keys
            cursor.execute("PRAGMA foreign_keys")
            checks['foreign_keys_enabled'] = cursor.fetchone()[0] == 1

            # Integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            checks['integrity_check'] = result[0] if result else None

            # Foreign key check
            cursor.execute("PRAGMA foreign_key_check")
            checks['foreign_key_check'] = cursor.fetchall()

            # Count records in each table
            tables = ['medicines', 'medicine_days', 'tracking', 'metadata']
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    checks['tables'][table] = cursor.fetchone()[0]
                except:
                    checks['tables'][table] = None

            conn.close()
            return checks
        except Exception as e:
            return {'error': str(e)}

    return _verify


@pytest.fixture
def assert_data_consistency():
    """Helper to assert data consistency"""
    def _assert(consistency_result):
        """Assert database is consistent"""
        assert consistency_result.get('integrity_check') == 'ok', \
            "Database integrity check failed"
        # Foreign keys should be enabled in the main connection (MedicineDatabase enables them)
        # Note: The check itself enables them, so they may not be enabled in the check connection
        assert len(consistency_result.get('foreign_key_check', [])) == 0, \
            "Foreign key violations detected"

    return _assert


# ============================================================================
# API Response Validation Helpers
# ============================================================================

@pytest.fixture
def assert_api_success():
    """Helper to assert successful API responses"""
    def _assert(response, expected_status=200):
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}: {response.data}"

        data = response.get_json()
        assert data is not None, "Response is not JSON"
        assert data.get('success') is True, \
            f"API returned success=False: {data.get('error')}"
        assert 'data' in data, "Response missing 'data' field"

        return data

    return _assert


@pytest.fixture
def assert_api_error():
    """Helper to assert error API responses"""
    def _assert(response, expected_status, expected_code=None):
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"

        data = response.get_json()
        assert data is not None, "Response is not JSON"
        assert data.get('success') is False, "API returned success=True"
        assert 'error' in data, "Response missing 'error' field"

        if expected_code:
            assert data['error'].get('code') == expected_code, \
                f"Expected error code {expected_code}, got {data['error'].get('code')}"

        return data

    return _assert


# ============================================================================
# Cleanup and Utility Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def integration_test_cleanup():
    """Auto cleanup after each integration test"""
    yield

    # Cleanup environment variables
    env_vars = ['PIZERO_MEDICINE_DB', 'FLASK_ENV']
    for var in env_vars:
        if var in os.environ:
            del os.environ[var]
