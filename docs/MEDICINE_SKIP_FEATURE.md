# Medicine Skip Feature Documentation

## Overview

The Medicine Skip Feature allows users to track when they intentionally skip or forget to take a medicine dose. This provides more accurate adherence tracking by distinguishing between doses that were taken, skipped, or simply missed.

**Version:** 1.1.0
**Date Added:** 2025-11-08
**Database Migration:** 002_add_skip_tracking.sql

---

## Feature Capabilities

### Core Functionality

1. **Skip Tracking**: Mark medicine doses as skipped with optional reasons
2. **Skip History**: View complete history of skipped doses with filters
3. **Enhanced Adherence Stats**: Get detailed adherence metrics including skip rates
4. **No Pill Decrement**: Skipped doses don't reduce pill inventory (only taken doses do)

### Skip Reasons

Users can categorize skips with the following reasons:

- **Forgot**: User forgot to take the medicine
- **Side effects**: Experiencing adverse reactions
- **Out of stock**: Medicine not available
- **Doctor advised**: Healthcare provider recommendation
- **Other**: Any other reason

---

## Database Schema Changes

### Migration 002: Add Skip Tracking

The skip feature adds three new columns to the `tracking` table:

```sql
ALTER TABLE tracking ADD COLUMN skipped INTEGER DEFAULT 0;
ALTER TABLE tracking ADD COLUMN skip_reason TEXT DEFAULT NULL;
ALTER TABLE tracking ADD COLUMN skip_timestamp TEXT DEFAULT NULL;
```

### New Indexes

```sql
CREATE INDEX idx_tracking_skipped ON tracking(skipped);
CREATE INDEX idx_tracking_skip_timestamp ON tracking(skip_timestamp);
```

### New View: adherence_detailed

```sql
CREATE VIEW adherence_detailed AS
SELECT
    m.id as medicine_id,
    m.name,
    m.dosage,
    t.date,
    t.time_window,
    t.taken,
    t.skipped,
    t.timestamp as taken_timestamp,
    t.skip_timestamp,
    t.skip_reason,
    CASE
        WHEN t.taken = 1 THEN 'taken'
        WHEN t.skipped = 1 THEN 'skipped'
        ELSE 'pending'
    END as status
FROM medicines m
LEFT JOIN tracking t ON m.id = t.medicine_id
ORDER BY t.date DESC, m.name;
```

---

## API Endpoints

### 1. Skip a Medicine Dose

**Endpoint:** `POST /api/v1/tracking/skip`

**Request Body:**
```json
{
    "medicine_id": "med_1234567890",
    "time_window": "morning",
    "skip_reason": "Forgot",
    "skip_date": "2025-11-08",
    "notes": "Overslept this morning"
}
```

**Required Fields:**
- `medicine_id` (string): Medicine ID in format `med_TIMESTAMP`

**Optional Fields:**
- `time_window` (string): One of: morning, afternoon, evening, night (defaults to medicine's default)
- `skip_reason` (string): One of: Forgot, Side effects, Out of stock, Doctor advised, Other
- `skip_date` (string): Date in YYYY-MM-DD format (defaults to today)
- `notes` (string): Additional notes (max 500 characters)

**Response (201 Created):**
```json
{
    "success": true,
    "message": "Medicine marked as skipped",
    "data": {
        "medicine_id": "med_1234567890",
        "medicine_name": "Vitamin D",
        "skip_date": "2025-11-08",
        "skip_timestamp": "2025-11-08 09:30:00",
        "skip_reason": "Forgot",
        "time_window": "morning"
    }
}
```

**Error Responses:**
- `400`: Validation error (invalid input)
- `404`: Medicine not found
- `500`: Database error

---

### 2. Get Skip History

**Endpoint:** `GET /api/v1/tracking/skip-history`

**Query Parameters:**
- `medicine_id` (optional): Filter by specific medicine
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Example Request:**
```
GET /api/v1/tracking/skip-history?medicine_id=med_1234567890&start_date=2025-11-01
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": [
        {
            "id": 123,
            "medicine_id": "med_1234567890",
            "name": "Vitamin D",
            "dosage": "1000 IU",
            "date": "2025-11-08",
            "time_window": "morning",
            "skipped": 1,
            "skip_timestamp": "2025-11-08 09:30:00",
            "skip_reason": "Forgot",
            "notes": null
        }
    ],
    "meta": {
        "total": 1,
        "page": 1,
        "per_page": 20,
        "total_pages": 1
    }
}
```

---

### 3. Get Detailed Adherence Statistics

**Endpoint:** `GET /api/v1/tracking/adherence-detailed`

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format (defaults to 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (defaults to today)

**Example Request:**
```
GET /api/v1/tracking/adherence-detailed?start_date=2025-10-01&end_date=2025-11-08
```

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "taken": 45,
        "skipped": 3,
        "missed": 2,
        "total": 50,
        "adherence_rate": 90.0,
        "skip_rate": 6.0
    }
}
```

**Metrics Explained:**
- `taken`: Number of doses marked as taken
- `skipped`: Number of doses marked as skipped
- `missed`: Number of doses neither taken nor skipped
- `total`: Total expected doses in the period
- `adherence_rate`: Percentage of doses taken (taken/total * 100)
- `skip_rate`: Percentage of doses skipped (skipped/total * 100)

---

### 4. Updated: Today's Statistics

**Endpoint:** `GET /api/v1/tracking/today`

**Changes:** Now includes `medicines_skipped` in response

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "date": "2025-11-08",
        "total_medicines": 5,
        "medicines_taken": 3,
        "medicines_skipped": 1,
        "medicines_pending": 1,
        "adherence_rate": 0.60,
        "low_stock_count": 2
    }
}
```

---

## Python API Usage

### Database Methods

```python
from db.medicine_db import MedicineDatabase
from datetime import date, datetime

db = MedicineDatabase()

# Skip a medicine
result = db.skip_medicine(
    medicine_id='med_1234567890',
    time_window='morning',
    skip_date=date.today(),
    skip_timestamp=datetime.now(),
    skip_reason='Forgot'
)

# Get skip history
skip_history = db.get_skip_history(
    medicine_id='med_1234567890',
    start_date=date(2025, 11, 1),
    end_date=date.today()
)

# Get detailed adherence stats
stats = db.get_adherence_detailed(
    start_date=date(2025, 10, 1),
    end_date=date.today()
)

# Get today's stats (now returns 3 values)
taken, skipped, total = db.get_today_stats(check_date=date.today())
```

---

## Example Workflows

### Workflow 1: User Forgets Morning Dose

1. User realizes they forgot their morning Vitamin D
2. User opens medicine tracker app
3. User selects "Skip" instead of "Taken"
4. User selects skip reason: "Forgot"
5. System records skip without decrementing pill count
6. Adherence stats updated to reflect skip

### Workflow 2: Doctor Advises Temporary Stop

1. Doctor advises patient to skip medicine for a few days
2. User marks medicine as skipped each day
3. User selects skip reason: "Doctor advised"
4. Pills remain in inventory
5. User can view skip history to track duration

### Workflow 3: Reviewing Adherence Patterns

1. User wants to understand adherence over past month
2. User requests detailed adherence stats
3. System shows:
   - 42 doses taken (84%)
   - 5 doses skipped (10%)
   - 3 doses missed (6%)
4. User can drill down into skip history to see reasons
5. User identifies pattern: mostly "Forgot" on weekends

---

## Skip Reasons Explained

### Forgot
- User unintentionally missed the dose
- Most common skip reason
- Helps identify patterns (e.g., always forget weekend doses)

### Side Effects
- User experiencing adverse reactions
- Important for medical review
- May indicate need to consult healthcare provider

### Out of Stock
- Medicine not available when needed
- Helps track inventory management issues
- Alerts user to refill earlier next time

### Doctor Advised
- Healthcare provider recommended skipping
- Temporary or permanent change in regimen
- Important for medical record keeping

### Other
- Any reason not covered above
- Can include notes for clarification
- Catch-all category

---

## Technical Implementation Details

### ACID Compliance

All skip operations use database transactions to ensure:
- **Atomicity**: Skip operation fully completes or fully fails
- **Consistency**: Database constraints maintained
- **Isolation**: Concurrent skip operations don't interfere
- **Durability**: Skip records persist after commit

### Thread Safety

The MedicineDatabase class uses thread-local connections to ensure safe concurrent access:
```python
self._local = threading.local()
```

### Conflict Resolution

When skipping a medicine that was already tracked for the same date/time window:
```sql
ON CONFLICT(medicine_id, date, time_window)
DO UPDATE SET skipped=1, skip_timestamp=excluded.skip_timestamp, skip_reason=excluded.skip_reason
```

This means:
- If previously marked as taken, it becomes skipped
- If previously skipped, the skip reason/timestamp updates
- Unique constraint prevents duplicate tracking entries

### Pill Count Protection

**Critical:** Skipped doses DO NOT decrement pill count
- Only `mark_medicine_taken()` decrements pills
- `skip_medicine()` leaves `pills_remaining` unchanged
- This ensures accurate inventory tracking

---

## Validation Rules

### Input Validation (Marshmallow)

```python
class SkipMedicineSchema(Schema):
    medicine_id = fields.Str(required=True, validate=Regexp(r'^med_\d+$'))
    time_window = fields.Str(validate=OneOf(['morning', 'afternoon', 'evening', 'night']))
    skip_date = fields.Date(format='%Y-%m-%d')
    skip_reason = fields.Str(validate=OneOf([
        'Forgot', 'Side effects', 'Out of stock', 'Doctor advised', 'Other'
    ]))
    notes = fields.Str(validate=Length(max=500))
```

### Business Rules

1. Medicine must exist (ValueError raised if not found)
2. Skip reason must be from predefined list
3. Notes limited to 500 characters
4. Date must be valid YYYY-MM-DD format
5. Time window must be valid option

---

## Error Handling

### Common Errors

**Medicine Not Found:**
```json
{
    "success": false,
    "error": {
        "code": "RESOURCE_NOT_FOUND",
        "message": "Medicine not found: med_invalid"
    }
}
```

**Invalid Skip Reason:**
```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Validation failed",
        "details": {
            "skip_reason": ["Skip reason must be one of: Forgot, Side effects, Out of stock, Doctor advised, Other"]
        }
    }
}
```

**Database Error:**
```json
{
    "success": false,
    "error": {
        "code": "DATABASE_ERROR",
        "message": "Failed to skip medicine",
        "details": "Error message here"
    }
}
```

---

## Testing

### Test Coverage

The skip functionality includes comprehensive tests in:
- `/tests/api/test_skip_functionality.py`

**Test Classes:**
1. `TestSkipMedicine` - Skip endpoint tests
2. `TestGetSkipHistory` - Skip history retrieval
3. `TestGetAdherenceDetailed` - Detailed stats
4. `TestTodayStatsWithSkip` - Updated today stats
5. `TestSkipEdgeCases` - Edge case scenarios

**Key Test Scenarios:**
- Skip with all fields vs required only
- All skip reasons tested
- Medicine not found handling
- Invalid input validation
- Pill count not decremented
- Skip then take (state transition)
- Take then skip (state transition)
- Pagination and filtering
- Date range queries
- Empty result sets

### Running Tests

```bash
# Run all skip tests
pytest tests/api/test_skip_functionality.py -v

# Run specific test class
pytest tests/api/test_skip_functionality.py::TestSkipMedicine -v

# Run with coverage
pytest tests/api/test_skip_functionality.py --cov=api.v1.routes.tracking --cov=db.medicine_db
```

---

## Migration Guide

### Applying the Migration

1. **Backup your database:**
   ```bash
   cp /path/to/medicine.db /path/to/medicine.db.backup
   ```

2. **Run the migration:**
   ```bash
   sqlite3 /path/to/medicine.db < db/migrations/002_add_skip_tracking.sql
   ```

3. **Verify migration:**
   ```bash
   sqlite3 /path/to/medicine.db "SELECT value FROM metadata WHERE key = 'schema_version';"
   # Should output: 1.1.0
   ```

### Rolling Back

If you need to rollback:
```sql
BEGIN TRANSACTION;

-- Drop new columns
ALTER TABLE tracking DROP COLUMN skipped;
ALTER TABLE tracking DROP COLUMN skip_reason;
ALTER TABLE tracking DROP COLUMN skip_timestamp;

-- Drop indexes
DROP INDEX IF EXISTS idx_tracking_skipped;
DROP INDEX IF EXISTS idx_tracking_skip_timestamp;

-- Drop view
DROP VIEW IF EXISTS adherence_detailed;

-- Restore schema version
UPDATE metadata SET value = '2.0.0' WHERE key = 'schema_version';

COMMIT;
```

**Note:** SQLite doesn't support `ALTER TABLE DROP COLUMN` in older versions. You may need to recreate the table.

---

## Performance Considerations

### Indexes

The migration creates two new indexes:
- `idx_tracking_skipped` - Fast filtering of skipped records
- `idx_tracking_skip_timestamp` - Efficient date range queries

### Query Optimization

**Skip History Query:**
- Uses index on `skipped = 1`
- Joins with medicines table for names
- Supports filtering by medicine_id, date range
- Ordered by skip_timestamp

**Adherence Stats Query:**
- Aggregates using COUNT and SUM
- Uses CASE statements for categorization
- Efficient for large datasets

### Best Practices

1. **Use date ranges** when querying skip history to limit result sets
2. **Paginate** large result sets (default 20 items per page)
3. **Index usage** verified with `EXPLAIN QUERY PLAN`
4. **Transaction isolation** prevents concurrent modification issues

---

## Security Considerations

### Input Validation

- All inputs validated using Marshmallow schemas
- SQL injection prevented by parameterized queries
- Medicine ID format enforced (med_TIMESTAMP)
- Notes length limited to 500 characters

### Access Control

- Skip functionality respects same access controls as other tracking endpoints
- No additional permissions required
- User can only skip medicines they have access to

### Data Integrity

- Foreign key constraints ensure medicine exists
- Unique constraints prevent duplicate tracking
- Transactions ensure atomic operations
- Triggers update metadata on changes

---

## Future Enhancements

Potential improvements to consider:

1. **Skip Notifications:**
   - Alert user if skipping too frequently
   - Weekly skip summary

2. **Pattern Analysis:**
   - Identify skip patterns (weekends, holidays)
   - Suggest reminders based on skip history

3. **Export Functionality:**
   - Export skip history to CSV
   - Include in adherence reports

4. **Medical Integration:**
   - Share skip data with healthcare providers
   - Integration with health records systems

5. **Smart Recommendations:**
   - Suggest optimal time windows based on skip patterns
   - Reminder adjustments based on forget patterns

---

## Support & Troubleshooting

### Common Issues

**Issue:** Skip doesn't appear in history
- **Solution:** Check that medicine_id is correct and medicine exists

**Issue:** Pill count decreased after skip
- **Solution:** This shouldn't happen. Check database integrity and report bug

**Issue:** Can't skip with custom date
- **Solution:** Ensure date format is YYYY-MM-DD

**Issue:** Skip reason rejected
- **Solution:** Use one of the predefined reasons (case-sensitive)

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Version History

- **v1.1.0** (2025-11-08): Initial skip feature implementation
- **v2.0.0** (2025-11-08): Base schema with tracking table

---

## License & Credits

Part of the Pi Zero 2W Medicine Tracker System
© 2025 - Medicine Tracker Development Team
