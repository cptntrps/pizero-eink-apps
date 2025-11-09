# Pi Zero 2W Medicine Tracker - Database Documentation

## Overview

The Pi Zero 2W Medicine Tracker System uses JSON-based file storage as its database. This document provides a comprehensive review of the database structure, operations, and API endpoints.

**Database Files:**
- `medicine_data.json` - Primary medicine tracking database
- `config.json` - System and application configuration

**Last Updated:** 2025-11-08

---

## Table of Contents

1. [Database Schema](#database-schema)
2. [Data Models](#data-models)
3. [Database Operations](#database-operations)
4. [API Endpoints](#api-endpoints)
5. [Data Flow](#data-flow)
6. [Backup and Maintenance](#backup-and-maintenance)

---

## Database Schema

### 1. medicine_data.json

The primary database file containing all medicine tracking data.

**Location:** `/home/pizero2w/pizero_apps/medicine_data.json`

**Top-Level Structure:**
```json
{
  "medicines": [],      // Array of medicine objects
  "tracking": {},       // Daily tracking records
  "time_windows": {},   // Predefined time windows
  "last_updated": ""    // ISO timestamp of last modification
}
```

#### 1.1 medicines Array

Stores all medicine/vitamin records with their configuration.

**Schema:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | String | Yes | Unique identifier (e.g., "med_001", "med_1762467778545") |
| `name` | String | Yes | Medicine/vitamin name |
| `dosage` | String | Yes | Dosage information (e.g., "2000 IU", "30mg") |
| `time_window` | String | Yes | Time category: "morning", "afternoon", "evening", "night" |
| `window_start` | String | Yes | Window start time in HH:MM format |
| `window_end` | String | Yes | Window end time in HH:MM format |
| `days` | Array[String] | Yes | Active days: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] |
| `with_food` | Boolean | Yes | Whether to take with food |
| `notes` | String | No | Additional notes (e.g., "Take with breakfast") |
| `active` | Boolean | Yes | Whether medicine is active |
| `color_code` | String | No | Optional color identifier |
| `pills_remaining` | Integer | Yes | Current pill count |
| `pills_per_dose` | Integer | Yes | Pills consumed per dose |
| `low_stock_threshold` | Integer | Yes | Trigger for low stock warning |

**Example:**
```json
{
  "id": "med_001",
  "name": "Vitamin D",
  "dosage": "2000 IU",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "12:00",
  "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
  "with_food": true,
  "notes": "Take with breakfast",
  "active": true,
  "color_code": "yellow",
  "pills_remaining": 58,
  "pills_per_dose": 1,
  "low_stock_threshold": 10
}
```

#### 1.2 tracking Object

Nested object tracking daily medicine consumption.

**Structure:**
```json
{
  "YYYY-MM-DD": {
    "med_{id}_{time_window}": {
      "taken": boolean,
      "timestamp": "YYYY-MM-DDTHH:MM:SS"
    }
  }
}
```

**Tracking Key Format:** `{medicine_id}_{time_window}`
- Example: `"med_001_morning"`, `"med_1762467778545_evening"`

**Example:**
```json
{
  "2025-11-08": {
    "med_001_morning": {
      "taken": true,
      "timestamp": "2025-11-08T08:04:55"
    },
    "med_1762467778545_morning": {
      "taken": true,
      "timestamp": "2025-11-08T08:07:57"
    }
  }
}
```

#### 1.3 time_windows Object

Predefined time window definitions.

**Schema:**
```json
{
  "window_name": {
    "start": "HH:MM",
    "end": "HH:MM"
  }
}
```

**Default Windows:**
| Window | Start | End | Description |
|--------|-------|-----|-------------|
| morning | 06:00 | 12:00 | Morning medications |
| afternoon | 12:00 | 18:00 | Afternoon medications |
| evening | 18:00 | 22:00 | Evening medications |
| night | 22:00 | 23:59 | Night medications |

#### 1.4 last_updated Field

ISO 8601 timestamp tracking the last database modification.

**Format:** `"YYYY-MM-DDTHH:MM:SS"`
**Example:** `"2025-11-08T12:30:40"`
**Purpose:** Enables push-refresh functionality for external data changes

---

### 2. config.json

System-wide configuration file.

**Location:** `/home/pizero2w/pizero_apps/config.json`

**Medicine-Relevant Configuration:**
```json
{
  "medicine": {
    "data_file": "/home/pizero2w/pizero_apps/medicine_data.json",
    "update_interval": 60,
    "reminder_window": 30,
    "alert_upcoming_minutes": 15,
    "rotate_interval": 3
  }
}
```

**Medicine Config Fields:**
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data_file` | String | - | Path to medicine_data.json |
| `update_interval` | Integer | 60 | Auto-refresh interval (seconds) |
| `reminder_window` | Integer | 30 | Reminder buffer before/after window (minutes) |
| `alert_upcoming_minutes` | Integer | 15 | Upcoming reminder alert (minutes) |
| `rotate_interval` | Integer | 3 | Display rotation interval (seconds) |

---

## Data Models

### Medicine Model

**File:** `medicine_app.py` (Lines 29-135)

**Core Functions:**

#### load_medicine_data()
**Location:** `medicine_app.py:29-35`
```python
def load_medicine_data():
    """Load medicine data from JSON file"""
    try:
        with open(MEDICINE_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"medicines": [], "tracking": {}, "time_windows": {}}
```
- Returns full database object
- Provides default structure on failure

#### save_medicine_data(data)
**Location:** `medicine_app.py:37-49`
```python
def save_medicine_data(data):
    """Save medicine data to JSON file"""
    try:
        data["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        with open(MEDICINE_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save medicine data: {e}")
        return False
```
- Automatically adds `last_updated` timestamp
- Returns boolean success status
- Logs errors

---

## Database Operations

### Query Operations

#### 1. get_pending_medicines(data)
**Location:** `medicine_app.py:76-110`
**Purpose:** Retrieve medicines due in current time window

**Logic Flow:**
1. Get current datetime, date, and day-of-week
2. Filter medicines by:
   - Active status (`active: true`)
   - Scheduled day matches current day
   - Current time within reminder window (time_window ± reminder_window_minutes)
   - Not already marked as taken today
3. Return list of pending medicine objects

**Time Window Check Algorithm:**
```python
def is_in_time_window(window_start, window_end, current_time, reminder_window_minutes=30):
    start_mins = start_h * 60 + start_m - reminder_window_minutes
    end_mins = end_h * 60 + end_m + reminder_window_minutes
    curr_mins = curr_h * 60 + curr_m
    return start_mins <= curr_mins <= end_mins
```
- Converts times to "minutes since midnight"
- Adds buffer before/after window
- Example: 06:00-12:00 window with 30min buffer → 05:30-12:30

#### 2. get_today_stats(data)
**Location:** `medicine_app.py:138-160`
**Purpose:** Calculate daily completion statistics

**Returns:** `(taken_count, total_count)`

**Logic:**
1. Count total medicines scheduled for today
2. Count medicines marked as taken
3. Return tuple of (taken, total)

Used for progress display: `"Progress: 3/5 taken (60%)"`

#### 3. get_data_timestamp(data)
**Location:** `medicine_app.py:51-53`
**Purpose:** Extract last update timestamp

**Returns:** ISO timestamp string or `"1970-01-01T00:00:00"` if missing

---

### Write Operations

#### 1. mark_medicines_taken(data, medicines)
**Location:** `medicine_app.py:112-136`
**Purpose:** Mark medicine(s) as taken and update pill count

**Process:**
1. Generate tracking key: `{medicine_id}_{time_window}`
2. Add tracking record:
   ```json
   {
     "taken": true,
     "timestamp": "2025-11-08T12:30:40"
   }
   ```
3. Decrement pill count:
   ```python
   pills_remaining = max(0, current_count - pills_per_dose)
   ```
4. Save updated data with new timestamp
5. Return boolean success status

**Side Effects:**
- Updates `tracking[date][tracking_key]`
- Decrements `medicines[].pills_remaining`
- Updates `last_updated` timestamp
- Triggers push-refresh for display

---

## API Endpoints

All endpoints provided by Flask web server in `web_config.py`.

**Base URL:** `http://{device_ip}:5000`

### Configuration Endpoints

#### GET /api/config
**Purpose:** Retrieve full configuration

**Response:**
```json
{
  "weather": {...},
  "mbta": {...},
  "medicine": {...},
  ...
}
```

#### POST /api/config/{section}
**Purpose:** Update configuration section

**Request Body:** Section-specific configuration object

**Response:**
```json
{
  "success": true,
  "message": "Medicine settings saved successfully!"
}
```

---

### Medicine Data Endpoints

#### GET /api/medicine/data
**Location:** `web_config.py:972-979`
**Purpose:** Retrieve complete medicine database

**Response:**
```json
{
  "medicines": [...],
  "tracking": {...},
  "time_windows": {...},
  "last_updated": "2025-11-08T12:30:40"
}
```

**Error Handling:** Returns empty structure on file read failure

---

#### POST /api/medicine/add
**Location:** `web_config.py:981-1002`
**Purpose:** Add new medicine record

**Request Body:**
```json
{
  "id": "med_1762606811268",
  "name": "Fish Oil",
  "dosage": "1200mg",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "12:00",
  "with_food": false,
  "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
  "notes": "",
  "pills_remaining": 199,
  "pills_per_dose": 1,
  "low_stock_threshold": 10,
  "active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Medicine added successfully!"
}
```

**Process:**
1. Load current database
2. Append new medicine to `medicines` array
3. Add `last_updated` timestamp
4. Save database
5. Trigger display refresh via timestamp change

---

#### POST /api/medicine/update
**Location:** `web_config.py:1004-1034`
**Purpose:** Update existing medicine record

**Request Body:** Complete medicine object with matching `id`

**Response:**
```json
{
  "success": true,
  "message": "Medicine updated successfully!"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Medicine not found"
}
```

**Process:**
1. Load database
2. Find medicine by `id`
3. Replace entire medicine object
4. Add timestamp
5. Save and trigger refresh

---

#### DELETE /api/medicine/delete/{med_id}
**Location:** `web_config.py:1036-1060`
**Purpose:** Delete medicine by ID

**URL Parameter:** `med_id` - Medicine identifier

**Response:**
```json
{
  "success": true,
  "message": "Medicine deleted successfully!"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "message": "Medicine not found"
}
```

**Process:**
1. Filter out medicine with matching `id`
2. Verify deletion occurred
3. Add timestamp
4. Save and trigger refresh

**Note:** Does not remove historical tracking data

---

#### POST /api/medicine/mark-taken
**Location:** `web_config.py:1062-1188`
**Purpose:** Mark medicine(s) as taken with timestamp

**Request Body (Single):**
```json
{
  "medicine_id": "med_001",
  "timestamp": "2025-11-07T08:30:00"  // Optional
}
```

**Request Body (Multiple):**
```json
{
  "medicine_ids": ["med_001", "med_002"],
  "timestamp": "2025-11-07T08:30:00"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "message": "Marked 2 medicine(s) as taken",
  "marked": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "pills_remaining": 57,
      "low_stock": false
    },
    {
      "id": "med_002",
      "name": "Fish Oil",
      "pills_remaining": 8,
      "low_stock": true
    }
  ],
  "timestamp": "2025-11-07T08:30:00",
  "not_found": []  // Present if any IDs not found
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "Invalid timestamp format. Use ISO 8601 (e.g., 2025-11-07T08:30:00)"
}
```

**Process:**
1. Parse medicine IDs (single or array)
2. Validate/generate timestamp
3. For each medicine:
   - Create tracking record
   - Decrement pill count
4. Add `last_updated` timestamp
5. Save database
6. Return detailed response with stock warnings

**Stock Warning Logic:**
- `low_stock: true` when `pills_remaining <= low_stock_threshold`
- Enables UI alerts for reordering

---

#### GET /api/medicine/pending
**Location:** `web_config.py:1190-1272`
**Purpose:** Get medicines due now (or at specified time)

**Query Parameters (Optional):**
- `date` - YYYY-MM-DD format (defaults to today)
- `time` - HH:MM format (defaults to current time)

**Example Request:**
```
GET /api/medicine/pending?date=2025-11-08&time=08:30
```

**Response:**
```json
{
  "success": true,
  "count": 2,
  "medicines": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "time_window": "morning",
      "with_food": true,
      "notes": "Take with breakfast",
      "pills_remaining": 58,
      "low_stock": false
    },
    {
      "id": "med_1762467778545",
      "name": "Vyvanse",
      "dosage": "30mg",
      "time_window": "morning",
      "with_food": true,
      "notes": "",
      "pills_remaining": 5,
      "low_stock": true
    }
  ],
  "checked_at": "2025-11-08T08:30:00"
}
```

**Algorithm:**
1. Parse date/time parameters or use current
2. Calculate current day-of-week and minutes since midnight
3. Filter medicines by:
   - Active status
   - Scheduled for current day
   - Within time window (± 30 minute buffer)
   - Not already taken today
4. Return filtered list with stock status

**Use Cases:**
- Display reminder notifications
- iPhone Shortcuts integration
- Scheduled health checks

---

## Data Flow

### 1. Adding a New Medicine (Web UI)

```
User Input (Web Form)
    ↓
POST /api/medicine/add
    ↓
web_config.py:add_medicine()
    ↓
Load medicine_data.json
    ↓
Append to medicines array
    ↓
Set last_updated timestamp
    ↓
Save medicine_data.json
    ↓
Return success response
    ↓
UI refreshes medicine list
```

---

### 2. Marking Medicine as Taken (Display)

```
User Double-Tap (E-ink Display)
    ↓
medicine_app.py:run_medicine_app() (Line 454)
    ↓
Load current pending medicines
    ↓
medicine_app.py:mark_medicines_taken()
    ↓
Create tracking record
    ↓
Decrement pills_remaining
    ↓
Save with timestamp
    ↓
Display confirmation screen
    ↓
Refresh display with updated data
```

---

### 3. Push Refresh Detection

```
Display App Loop (medicine_app.py:396)
    ↓
Every 5 seconds: Check last_updated timestamp
    ↓
Compare with last_known_timestamp
    ↓
If changed:
    - Reload medicine_data.json
    - Refresh pending medicines
    - Update display
    - Update last_known_timestamp
```

**Mechanism:** Enables external changes (web UI, API) to immediately update display

---

### 4. iPhone Shortcuts Integration

```
iOS Shortcuts App
    ↓
HTTP GET /api/medicine/pending
    ↓
Parse JSON response
    ↓
Display notification with count
    ↓
User taps "Mark Taken"
    ↓
HTTP POST /api/medicine/mark-taken
    ↓
Receive confirmation with stock alerts
    ↓
Display iOS notification
    ↓
E-ink display auto-refreshes via timestamp
```

---

## Backup and Maintenance

### Automatic Backups

**Current Implementation:** No automatic backups

**Recommendation:** Implement daily backups via cron:
```bash
0 2 * * * cp /home/pizero2w/pizero_apps/medicine_data.json /home/pizero2w/backups/medicine_$(date +\%Y\%m\%d).json
```

---

### Data Cleanup

**Tracking Data Growth:**
- Each day adds new entries to `tracking` object
- 5 medicines/day × 365 days = ~1,825 tracking records/year
- Estimated size: ~200 KB/year

**Cleanup Strategy:**
```python
# Remove tracking data older than 90 days
from datetime import datetime, timedelta

def cleanup_old_tracking(data, days_to_keep=90):
    cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime("%Y-%m-%d")
    data['tracking'] = {
        date: records
        for date, records in data['tracking'].items()
        if date >= cutoff_date
    }
    return data
```

**Recommendation:** Run monthly cleanup via cron

---

### Data Integrity Checks

**Potential Issues:**
1. **Orphaned Tracking Records:** Medicine deleted but tracking remains
2. **Negative Pill Counts:** Edge case in decrement logic
3. **Invalid Date Keys:** Malformed YYYY-MM-DD strings
4. **Missing Required Fields:** Incomplete medicine objects

**Validation Function:**
```python
def validate_medicine_data(data):
    errors = []

    # Check required fields
    required_fields = ['id', 'name', 'dosage', 'time_window', 'days',
                       'pills_remaining', 'pills_per_dose', 'low_stock_threshold']

    for med in data.get('medicines', []):
        for field in required_fields:
            if field not in med:
                errors.append(f"Missing {field} in {med.get('id', 'unknown')}")

        # Check pill count
        if med.get('pills_remaining', 0) < 0:
            errors.append(f"Negative pills in {med['id']}")

    return errors
```

---

## Database Statistics (Current State)

**As of 2025-11-08:**

### Medicines Table
- Total Records: 5
- Active Medicines: 5
- Inactive Medicines: 0

**Breakdown by Time Window:**
| Window | Count |
|--------|-------|
| Morning | 5 |
| Afternoon | 0 |
| Evening | 0 |
| Night | 0 |

**Breakdown by Frequency:**
| Days/Week | Count |
|-----------|-------|
| Daily (7) | 5 |

### Tracking Records
- Total Days Tracked: 3
- Date Range: 2025-11-06 to 2025-11-08
- Total Tracking Entries: 10
- Average Compliance: ~3.3 medicines/day

### Stock Status
| Medicine | Pills Remaining | Low Stock | Status |
|----------|----------------|-----------|--------|
| Vitamin D | 58 | < 10 | OK |
| Vyvanse | 16 | < 7 | OK |
| Buproprion XL | 45 | < 7 | OK |
| Magnesium | 28 | < 10 | OK |
| Fish Oil | 199 | < 10 | OK |

**No medicines currently at low stock threshold**

---

## API Usage Examples

### cURL Examples

**Get pending medicines:**
```bash
curl http://192.168.50.202:5000/api/medicine/pending
```

**Mark medicine as taken:**
```bash
curl -X POST http://192.168.50.202:5000/api/medicine/mark-taken \
  -H "Content-Type: application/json" \
  -d '{"medicine_id": "med_001"}'
```

**Add new medicine:**
```bash
curl -X POST http://192.168.50.202:5000/api/medicine/add \
  -H "Content-Type: application/json" \
  -d '{
    "id": "med_'$(date +%s)'",
    "name": "Aspirin",
    "dosage": "81mg",
    "time_window": "morning",
    "window_start": "06:00",
    "window_end": "12:00",
    "with_food": true,
    "days": ["mon","wed","fri"],
    "notes": "Baby aspirin",
    "pills_remaining": 90,
    "pills_per_dose": 1,
    "low_stock_threshold": 10,
    "active": true
  }'
```

---

## Security Considerations

### Current Security Posture

**Strengths:**
- Local network only (no internet exposure)
- No authentication required (trusted network)
- File-based storage (no SQL injection risk)

**Vulnerabilities:**
- No input validation on API endpoints
- No rate limiting
- No authentication/authorization
- Direct file system access

**Recommendations:**

1. **Input Validation:**
```python
def validate_medicine_input(data):
    # Validate required fields
    # Sanitize string inputs
    # Check integer ranges
    # Validate date formats
```

2. **Basic Authentication:**
```python
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@app.route('/api/medicine/data')
@auth.login_required
def get_medicine_data():
    # ...
```

3. **Rate Limiting:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/medicine/mark-taken')
@limiter.limit("10 per minute")
def mark_taken():
    # ...
```

---

## Performance Optimization

### Current Performance

**File Operations:**
- Average read time: ~5ms
- Average write time: ~10ms
- Current file size: ~4 KB

**Bottlenecks:**
- None identified at current scale
- JSON parsing overhead negligible

### Scaling Considerations

**When to Consider Migration to SQL:**
- User count > 10
- Total medicines > 100
- Tracking history > 1 year
- Need for complex queries/analytics

**Migration Path:**
```sql
-- Example SQLite schema
CREATE TABLE medicines (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dosage TEXT NOT NULL,
    time_window TEXT NOT NULL,
    pills_remaining INTEGER DEFAULT 0,
    pills_per_dose INTEGER DEFAULT 1,
    low_stock_threshold INTEGER DEFAULT 10,
    active BOOLEAN DEFAULT 1
);

CREATE TABLE tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_id TEXT NOT NULL,
    date DATE NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);

CREATE INDEX idx_tracking_date ON tracking(date);
CREATE INDEX idx_tracking_medicine ON tracking(medicine_id);
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Display Not Updating After Web Change
**Symptom:** Web UI shows updated data, display shows old data

**Diagnosis:**
1. Check `last_updated` timestamp in medicine_data.json
2. Verify display app is running
3. Check logs for timestamp comparison

**Solution:**
```bash
# Restart medicine app
sudo systemctl restart pizero-menu
```

---

#### Issue 2: Medicine Marked Twice
**Symptom:** Pills decremented twice for single dose

**Diagnosis:**
- Double-click detection issue
- API called multiple times

**Prevention:**
```python
# Add idempotency check
if tracking_key in data['tracking'][today]:
    if data['tracking'][today][tracking_key]['taken']:
        return {"already_taken": True}
```

---

#### Issue 3: Negative Pill Count
**Symptom:** `pills_remaining` shows negative number

**Cause:** Edge case in decrement logic

**Fix:**
```python
# Already implemented in line 133
new_count = max(0, current_count - pills_per_dose)
```

---

## Conclusion

The Pi Zero 2W Medicine Tracker uses a simple, effective JSON-based database system suitable for single-user medication tracking. The architecture prioritizes:

- **Simplicity:** No database server required
- **Reliability:** File-based persistence
- **Flexibility:** Easy manual editing and backup
- **Real-time Sync:** Push-refresh via timestamp mechanism

**Future Enhancements:**
1. Automated backups
2. Data analytics (adherence rates, trends)
3. Multi-user support
4. Cloud sync capabilities
5. Historical reporting

---

## Appendix: File Locations

| File | Path | Purpose |
|------|------|---------|
| Medicine Data | /home/pizero2w/pizero_apps/medicine_data.json | Primary database |
| Config | /home/pizero2w/pizero_apps/config.json | System configuration |
| Display App | /home/pizero2w/pizero_apps/medicine_app.py | E-ink display logic |
| Web Server | /home/pizero2w/pizero_apps/web_config.py | Flask API server |
| Menu | /home/pizero2w/pizero_apps/menu_button.py | Main menu system |

---

**Document Version:** 1.0
**Author:** Automated Documentation System
**Date:** 2025-11-08
