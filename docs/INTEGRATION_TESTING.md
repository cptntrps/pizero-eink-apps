# Integration Testing Guide

## Overview

This document describes the comprehensive end-to-end integration test suite for the Pi Zero 2W Medicine Tracker system. The suite validates interactions between the medicine app and API layer, database concurrency, error recovery, and data consistency.

## Test Suite Structure

### 1. Multi-App Interaction Tests (`test_app_interactions.py`)

Tests interactions between the medicine app and API layer through the database.

#### Key Test Classes

**TestMedicineAppAPIIntegration**
- `test_app_reads_after_api_creates`: Validates app can read data created via API
- `test_app_tracking_visible_to_api`: Ensures API sees tracking data from app
- `test_api_updates_visible_to_app`: Confirms app sees API-initiated changes
- `test_pending_medicines_consistency`: Verifies pending medicine calculations
- `test_low_stock_detection_across_layers`: Validates low stock status consistency
- `test_stats_calculation_consistency`: Ensures stats are correct
- `test_medicine_deletion_cascades`: Tests cascade delete behavior
- `test_concurrent_app_api_reads`: Validates concurrent read safety
- `test_metadata_updates_on_changes`: Confirms metadata tracking
- `test_medicine_days_consistency`: Verifies days-of-week preservation

**TestCrossLayerDataFlow**
- `test_create_read_update_delete_cycle`: Complete CRUD cycle validation
- `test_multiple_medicines_independent_operations`: Independent operation isolation
- `test_state_after_multiple_marks_taken`: Duplicate handling

### 2. Concurrent Access Tests (`test_concurrent_access.py`)

Comprehensive testing of concurrent database operations with 10+ simultaneous accesses.

#### Concurrent Read Operations (15 threads)
- `test_concurrent_get_all_medicines`: 15 concurrent reads
- `test_concurrent_get_medicine_by_id`: 12 concurrent ID lookups
- `test_concurrent_get_tracking_history`: 10 concurrent history queries
- `test_concurrent_get_pending_medicines`: 10 concurrent pending checks

#### Concurrent Write Operations (10 threads)
- `test_concurrent_mark_medicine_taken`: 10 threads marking different medicines
- `test_concurrent_add_medicines`: 10 threads adding different medicines
- `test_concurrent_update_same_medicine`: 5 threads updating same record

#### Mixed Concurrent Operations (15-20 threads)
- `test_concurrent_mixed_operations_15_threads`: Mixed reads/writes
- `test_concurrent_mark_and_read_tracking`: 10 write + 10 read threads
- `test_stress_20_concurrent_diverse_operations`: 20 diverse operations

#### Edge Cases
- `test_concurrent_add_duplicate_ids`: Duplicate constraint enforcement
- `test_concurrent_operations_high_contention`: 15 threads on single medicine

### 3. Error Recovery Tests (`test_error_recovery.py`)

Tests application behavior under error conditions and recovery scenarios.

#### Transaction Rollback
- `test_add_medicine_with_invalid_data_rollback`: Rollback on validation failure
- `test_update_nonexistent_medicine_error`: Error handling for missing records
- `test_delete_nonexistent_medicine_error`: Proper error on delete
- `test_mark_taken_nonexistent_medicine`: Error on invalid operations
- `test_transaction_isolation`: Transaction isolation verification

#### Data Validation
- `test_invalid_time_window_rejected`: Time window constraint
- `test_invalid_day_rejected`: Day-of-week constraint
- `test_negative_pills_prevented`: Negative pill prevention
- `test_zero_pills_per_dose_prevented`: Pills per dose constraint

#### Concurrent Error Handling
- `test_concurrent_adds_duplicate_id`: Duplicate ID handling

#### Database Corruption Recovery
- `test_connection_timeout_recovery`: Recovery from connection issues
- `test_database_cleanup_after_error`: Clean state after errors
- `test_partial_update_rollback`: Update atomicity

#### Recovery Scenarios
- `test_recovery_from_interrupted_tracking`: Tracking persistence
- `test_recovery_after_multiple_errors`: System usability after errors

### 4. Data Consistency Tests (`test_data_consistency.py`)

Validates data relationships, constraints, and consistency.

#### Foreign Key Constraints
- `test_medicine_days_foreign_key`: Foreign key verification
- `test_delete_medicine_cascades_to_days`: Cascade delete to days
- `test_delete_medicine_cascades_to_tracking`: Cascade delete to tracking
- `test_tracking_foreign_key_to_medicines`: Tracking foreign key

#### Unique Constraints
- `test_medicine_id_unique_constraint`: Primary key constraint
- `test_tracking_unique_constraint`: Composite unique constraint
- `test_medicine_days_composite_unique`: Composite key on days

#### Data Integrity
- `test_all_medicines_have_valid_days`: Valid day verification
- `test_tracking_consistency`: Referential integrity
- `test_pill_count_consistency`: Pill count accuracy
- `test_time_window_consistency`: Time window validity

#### Consistency After Operations
- `test_consistency_after_update`: Update data integrity
- `test_consistency_after_mark_taken`: Atomic mark operations
- `test_consistency_across_multiple_operations`: Complex sequences
- `test_database_integrity_after_operations`: Overall integrity

#### Metadata Consistency
- `test_metadata_last_updated_on_add`: Metadata updates on add
- `test_metadata_last_updated_on_mark`: Metadata updates on mark

## Running Tests

### Run All Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Specific Test File
```bash
pytest tests/integration/test_concurrent_access.py -v
```

### Run Specific Test Class
```bash
pytest tests/integration/test_app_interactions.py::TestMedicineAppAPIIntegration -v
```

### Run Specific Test
```bash
pytest tests/integration/test_concurrent_access.py::TestConcurrentReads::test_concurrent_get_all_medicines -v
```

### Run with Coverage
```bash
pytest tests/integration/ --cov=db --cov=api --cov-report=html
```

### Run with Detailed Output
```bash
pytest tests/integration/ -vv -s
```

### Run with Specific Markers
```bash
pytest tests/integration/ -m "slow" -v
```

## Test Data

### Sample Medicine Set
The test suite uses a comprehensive sample medicine set with:
- Aspirin (daily)
- Vitamin D (MWF)
- Blood Pressure Medication (daily)
- Thyroid Medication (daily)
- Multivitamin (TThSa)
- Antihistamine (weekdays)
- Inactive Medicine (for testing)

### Stress Test Medicines
- 50 medicines with various configurations
- Multiple time windows, schedules, and pill counts
- Mix of active and inactive medicines

## Key Features

### Thread Safety
- WAL mode enabled for better concurrency
- Foreign keys enabled for constraint enforcement
- Transaction isolation with rollback support
- Thread-local database connections

### Data Validation
- Schema-level constraints (CHECK, UNIQUE, FOREIGN KEY)
- Application-level validation
- Cascade delete for referential integrity

### Atomic Operations
- Transactions ensure all-or-nothing semantics
- Tracking and pill counts updated atomically
- Metadata timestamps updated on all changes

### Error Recovery
- Connection timeout recovery
- Transaction rollback on errors
- Partial update prevention
- State cleanup after failures

## Test Fixtures

### Database Fixtures
- `integration_test_db`: Fresh isolated database per test
- `integration_app`: Flask app for API testing
- `integration_client`: Test client with database

### Data Fixtures
- `comprehensive_medicine_set`: 7 realistic medicines
- `stress_test_medicines`: 50 medicines for load testing
- `sample_*`: Individual medicine data

### Helper Fixtures
- `concurrent_operations`: Execute concurrent operations
- `verify_db_consistency`: Check database integrity
- `assert_data_consistency`: Assert consistency checks
- `assert_api_success`: Validate success responses
- `assert_api_error`: Validate error responses

## Performance Metrics

### Expected Performance

| Operation | Threads | Time |
|-----------|---------|------|
| Concurrent reads | 15 | <100ms |
| Concurrent writes | 10 | <200ms |
| Mixed operations | 20 | <500ms |
| Concurrent marks | 10 | <150ms |

### Monitoring

Tests include timing information and can be profiled:
```bash
pytest tests/integration/test_concurrent_access.py -v -s --durations=10
```

## Continuous Integration

Integration tests should run:
1. On every commit (fast suite)
2. Before releases (full suite)
3. In CI/CD pipeline (with coverage)

### CI Configuration Example
```yaml
- name: Run Integration Tests
  run: |
    pytest tests/integration/ --cov=db --cov=api \
      --tb=short --junit-xml=test-results.xml
```

## Debugging Failed Tests

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Run Single Test with Debug
```bash
pytest tests/integration/test_app_interactions.py::TestMedicineAppAPIIntegration::test_app_reads_after_api_creates -vv -s --pdb
```

### Check Database State
```python
def test_my_test(integration_test_db):
    db, db_path, _ = integration_test_db
    # ... test code ...

    # Debug: Check database directly
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM medicines")
    print(f"Medicines: {cursor.fetchone()[0]}")
```

### View Test Isolation
Each test gets a fresh database in a temporary directory:
```
/tmp/pizero_integration_XXXXX/
  └── integration_test.db
```

## Common Issues and Solutions

### Issue: Tests Timeout
**Solution**: Increase timeout in pytest.ini or reduce max_workers in concurrent tests

### Issue: Database Locked
**Solution**: Ensure all connections are closed; check for lingering threads

### Issue: Concurrency Failures
**Solution**: Run with fewer workers; check for race conditions; add explicit synchronization

### Issue: Cleanup Issues
**Solution**: Verify cleanup_env fixture runs; check temp file cleanup

## Future Enhancements

- [ ] Load testing with 100+ concurrent operations
- [ ] Long-running stability tests (hours)
- [ ] Database corruption simulation and recovery
- [ ] Network failure simulation
- [ ] Memory leak detection
- [ ] Performance regression testing
- [ ] API layer integration with real Flask client
- [ ] Cache consistency validation
- [ ] Backup/restore verification
- [ ] Migration testing

## Related Documentation

- [ARCHITECTURE_REVIEW.md](../ARCHITECTURE_REVIEW.md) - System architecture
- [DATABASE_DOCUMENTATION.md](../DATABASE_DOCUMENTATION.md) - Database schema
- [API_ENDPOINT_QUICK_REFERENCE.md](../API_ENDPOINT_QUICK_REFERENCE.md) - API endpoints

## Contributing Tests

When adding new integration tests:

1. **Identify the layer**: App, API, or database
2. **Choose test type**: Read, write, mixed, or error scenario
3. **Use fixtures**: Leverage existing fixtures for consistency
4. **Test isolation**: Each test should be independent
5. **Clean assertions**: Clear error messages
6. **Document intent**: Docstrings explain scenario and validation
7. **Performance aware**: Avoid slow operations in non-perf tests

Example template:
```python
def test_your_feature(integration_test_db, comprehensive_medicine_set):
    """
    Scenario: Clear description of test scenario
    Validates: What behavior is being verified
    """
    db, db_path, _ = integration_test_db

    # Setup
    medicine = comprehensive_medicine_set[0]

    # Action
    result = db.add_medicine(medicine)

    # Assertion
    assert result is True
    assert len(db.get_all_medicines()) == 1
```

## Questions?

Refer to test docstrings and comments for implementation details. Each test includes:
- Scenario description
- Expected behavior
- Key assertions
