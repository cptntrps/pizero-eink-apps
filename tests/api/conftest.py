"""
Pytest Configuration and Fixtures for API Testing
Phase 1.4 - API Test Suite

This module provides:
- Test database fixtures
- Flask test client fixtures
- Sample data fixtures
- Cleanup utilities
"""

import os
import sys
import json
import tempfile
import shutil
import sqlite3
from datetime import datetime, date, timedelta
from contextlib import contextmanager

import pytest

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from api import create_app
from db.medicine_db import MedicineDatabase


# ============================================================================
# Test Configuration
# ============================================================================

@pytest.fixture(scope='session')
def test_dir():
    """Create and cleanup temporary test directory"""
    temp_dir = tempfile.mkdtemp(prefix='pizero_test_')
    yield temp_dir
    # Cleanup after all tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope='session')
def test_db_path(test_dir):
    """Path to test database"""
    return os.path.join(test_dir, 'test_medicine.db')


@pytest.fixture(scope='session')
def test_config_path(test_dir):
    """Path to test config file"""
    config_path = os.path.join(test_dir, 'test_config.json')

    # Create minimal test config
    test_config = {
        "medicine": {
            "enabled": True,
            "reminder_window": 30
        },
        "weather": {"enabled": False},
        "mbta": {"enabled": False},
        "disney": {"enabled": False},
        "flights": {"enabled": False},
        "pomodoro": {"enabled": False},
        "forbidden": {"enabled": False},
        "menu": {"default_app": "medicine"},
        "system": {"debug": True},
        "display": {"brightness": 100}
    }

    with open(config_path, 'w') as f:
        json.dump(test_config, f, indent=2)

    return config_path


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope='function')
def db(test_db_path):
    """
    Create fresh test database for each test function

    Yields:
        MedicineDatabase instance with clean database
    """
    # Remove existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Create new database instance
    db_instance = MedicineDatabase(db_path=test_db_path)

    yield db_instance

    # Cleanup
    db_instance.close()
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest.fixture(scope='function')
def db_with_data(db, sample_medicines):
    """
    Database pre-populated with sample medicines

    Args:
        db: MedicineDatabase fixture
        sample_medicines: Sample medicine data fixture

    Yields:
        MedicineDatabase instance with sample data
    """
    # Add sample medicines
    for medicine in sample_medicines:
        db.add_medicine(medicine)

    yield db


# ============================================================================
# Flask App Fixtures
# ============================================================================

@pytest.fixture(scope='function')
def app(test_db_path, test_config_path):
    """
    Create Flask test application

    Yields:
        Flask app configured for testing
    """
    # Set environment variables for testing
    os.environ['PIZERO_MEDICINE_DB'] = test_db_path
    os.environ['FLASK_ENV'] = 'testing'

    # Create app
    flask_app = create_app('testing')
    flask_app.config['TESTING'] = True
    flask_app.config['DATABASE_PATH'] = test_db_path

    yield flask_app

    # Cleanup
    if 'PIZERO_MEDICINE_DB' in os.environ:
        del os.environ['PIZERO_MEDICINE_DB']


@pytest.fixture(scope='function')
def client(app):
    """
    Flask test client for making API requests

    Args:
        app: Flask app fixture

    Yields:
        Flask test client
    """
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope='function')
def client_with_data(app, test_db_path, sample_medicines):
    """
    Flask test client with pre-populated database

    Args:
        app: Flask app fixture
        test_db_path: Test database path
        sample_medicines: Sample medicine data

    Yields:
        Flask test client with database containing sample data
    """
    # Remove and recreate database for clean state
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    # Populate database
    db = MedicineDatabase(db_path=test_db_path)
    for medicine in sample_medicines:
        db.add_medicine(medicine)
    db.close()

    with app.test_client() as test_client:
        yield test_client

    # Cleanup after test
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture(scope='session')
def sample_medicine():
    """Single sample medicine for testing"""
    return {
        "id": "med_test_001",
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
    }


@pytest.fixture(scope='session')
def sample_medicines():
    """List of sample medicines for testing"""
    return [
        {
            "id": "med_test_001",
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
            "id": "med_test_002",
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
            "id": "med_test_003",
            "name": "Blood Pressure Med",
            "dosage": "10mg",
            "time_window": "evening",
            "window_start": "18:00",
            "window_end": "19:00",
            "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
            "with_food": False,
            "notes": "Evening dose",
            "pills_remaining": 5,
            "pills_per_dose": 1,
            "low_stock_threshold": 10,
            "active": True
        },
        {
            "id": "med_test_004",
            "name": "Inactive Medicine",
            "dosage": "50mg",
            "time_window": "morning",
            "window_start": "08:00",
            "window_end": "09:00",
            "days": ["mon", "tue", "wed"],
            "with_food": False,
            "notes": "This is inactive",
            "pills_remaining": 30,
            "pills_per_dose": 1,
            "low_stock_threshold": 10,
            "active": False
        }
    ]


@pytest.fixture(scope='session')
def invalid_medicine_missing_field():
    """Invalid medicine data - missing required field"""
    return {
        "id": "med_invalid_001",
        "name": "Missing Dosage Medicine",
        # Missing "dosage" field
        "time_window": "morning",
        "window_start": "08:00",
        "window_end": "09:00",
        "days": ["mon", "tue", "wed"],
        "pills_remaining": 30,
        "pills_per_dose": 1,
        "low_stock_threshold": 10
    }


@pytest.fixture(scope='session')
def invalid_medicine_bad_time():
    """Invalid medicine data - bad time format"""
    return {
        "id": "med_invalid_002",
        "name": "Bad Time Medicine",
        "dosage": "10mg",
        "time_window": "morning",
        "window_start": "25:00",  # Invalid hour
        "window_end": "09:00",
        "days": ["mon", "tue", "wed"],
        "pills_remaining": 30,
        "pills_per_dose": 1,
        "low_stock_threshold": 10
    }


@pytest.fixture(scope='session')
def sample_tracking_record():
    """Sample tracking record for testing"""
    return {
        "medicine_id": "med_test_001",
        "date": date.today().strftime('%Y-%m-%d'),
        "time_window": "morning",
        "taken": True,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "pills_taken": 1
    }


# ============================================================================
# Helper Functions
# ============================================================================

@pytest.fixture
def assert_valid_response():
    """Helper to assert valid API response structure"""
    def _assert(response_json, expected_success=True):
        assert 'success' in response_json
        assert response_json['success'] == expected_success

        if expected_success:
            assert 'data' in response_json
        else:
            assert 'error' in response_json
            assert 'code' in response_json['error']
            assert 'message' in response_json['error']

        # Check for meta timestamp
        if 'meta' in response_json:
            assert 'timestamp' in response_json['meta']

    return _assert


@pytest.fixture
def assert_valid_paginated_response():
    """Helper to assert valid paginated response structure"""
    def _assert(response_json):
        assert 'success' in response_json
        assert response_json['success'] is True
        assert 'data' in response_json
        assert 'pagination' in response_json

        pagination = response_json['pagination']
        assert 'page' in pagination
        assert 'per_page' in pagination
        assert 'total' in pagination
        assert 'pages' in pagination

    return _assert


@pytest.fixture
def create_test_medicines():
    """Helper to create multiple test medicines with custom data"""
    def _create(count=5, prefix="test_med"):
        medicines = []
        for i in range(count):
            medicines.append({
                "id": f"{prefix}_{i:03d}",
                "name": f"Medicine {i}",
                "dosage": f"{10 * (i + 1)}mg",
                "time_window": "morning" if i % 2 == 0 else "evening",
                "window_start": "08:00" if i % 2 == 0 else "18:00",
                "window_end": "09:00" if i % 2 == 0 else "19:00",
                "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                "with_food": i % 2 == 0,
                "notes": f"Test medicine {i}",
                "pills_remaining": 100 - (i * 10),
                "pills_per_dose": 1,
                "low_stock_threshold": 10,
                "active": True
            })
        return medicines

    return _create


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_env():
    """Automatically cleanup environment after each test"""
    yield
    # Cleanup environment variables
    env_vars_to_clean = ['PIZERO_MEDICINE_DB', 'FLASK_ENV']
    for var in env_vars_to_clean:
        if var in os.environ:
            del os.environ[var]


# ============================================================================
# Database Verification Helpers
# ============================================================================

@pytest.fixture
def verify_database_state():
    """Helper to verify database state directly"""
    def _verify(db_path, expected_count=None, table='medicines'):
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        conn.close()

        if expected_count is not None:
            assert count == expected_count, f"Expected {expected_count} records in {table}, found {count}"

        return count

    return _verify
