# API Endpoint Inventory - web_config.py

**Analysis Date:** 2025-11-08
**Source File:** `/home/user/pizerowgpio/web_config.py`
**Total Lines:** 1,275
**HTML/CSS/JS Lines:** ~900 (lines 10-938)
**Python/API Lines:** ~375 (lines 1-9, 939-1276)

---

## Summary Statistics

- **Total Endpoints:** 9
- **GET Endpoints:** 4
- **POST Endpoints:** 4
- **DELETE Endpoints:** 1
- **Configuration Endpoints:** 2
- **Medicine Endpoints:** 6
- **Frontend Endpoint:** 1

---

## Endpoint Details

### 1. Frontend / UI

#### `GET /`
**Purpose:** Serve the main dashboard HTML interface
**Handler:** `index()`
**Line:** 940-942

**Request:**
- Method: GET
- Parameters: None
- Body: None

**Response:**
- Content-Type: text/html
- Body: Rendered HTML template (embedded in `HTML_TEMPLATE`)

**Current Implementation:**
```python
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
```

**Notes:**
- Returns 938-line HTML template with embedded CSS and JavaScript
- Single-page application (SPA) design
- Handles all UI routing client-side

---

### 2. Configuration Management

#### `GET /api/config`
**Purpose:** Retrieve entire configuration file
**Handler:** `get_config()`
**Line:** 944-951

**Request:**
- Method: GET
- Parameters: None
- Body: None

**Response:**
```json
{
  "weather": {
    "location": "Rio de Janeiro",
    "units": "metric",
    "update_interval": 300,
    "display_format": "detailed"
  },
  "mbta": { ... },
  "disney": { ... },
  "flights": { ... },
  "pomodoro": { ... },
  "forbidden": { ... }
}
```

**Current Implementation:**
```python
@app.route('/api/config', methods=['GET'])
def get_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
```

**Issues:**
- Direct file I/O (no abstraction)
- Generic exception handling
- Returns 500 on file not found (should return 200 with defaults)
- No validation of returned data

---

#### `POST /api/config/<section>`
**Purpose:** Update a specific configuration section
**Handler:** `update_config(section)`
**Line:** 953-967

**Request:**
- Method: POST
- URL Parameter: `section` (e.g., "weather", "mbta", "disney", "flights", "pomodoro", "forbidden")
- Content-Type: application/json
- Body: Section-specific configuration object

**Example - Weather:**
```json
{
  "location": "Rio de Janeiro",
  "units": "metric",
  "update_interval": 300,
  "display_format": "detailed"
}
```

**Example - MBTA:**
```json
{
  "home_station_id": "place-davis",
  "home_station_name": "Davis Square",
  "work_station_id": "place-pktrm",
  "work_station_name": "Park Street",
  "update_interval": 30,
  "morning_start": "06:00",
  "morning_end": "12:00",
  "evening_start": "15:00",
  "evening_end": "21:00"
}
```

**Response - Success:**
```json
{
  "success": true,
  "message": "Weather settings saved successfully!"
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
```python
@app.route('/api/config/<section>', methods=['POST'])
def update_config(section):
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)

        data = request.get_json()
        config[section] = data

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)

        return jsonify({"success": True, "message": f"{section.title()} settings saved successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
```

**Issues:**
- No validation of section name
- No validation of incoming data
- Direct file I/O with no locking
- Race condition possible (read-modify-write)
- Overwrites entire section (no partial updates)
- No audit trail

**Supported Sections:**
1. `weather` - Weather & calendar settings
2. `mbta` - MBTA transit settings
3. `disney` - Disney wait times settings
4. `flights` - Flight tracking settings
5. `pomodoro` - Pomodoro timer settings
6. `forbidden` - Forbidden message settings

---

### 3. Medicine Management

#### `GET /api/medicine/data`
**Purpose:** Retrieve all medicine data (medicines list + tracking data)
**Handler:** `get_medicine_data()`
**Line:** 972-979

**Request:**
- Method: GET
- Parameters: None
- Body: None

**Response - Success:**
```json
{
  "medicines": [
    {
      "id": "med_1699564800000",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "time_window": "morning",
      "window_start": "06:00",
      "window_end": "12:00",
      "with_food": true,
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "notes": "Take with breakfast",
      "pills_remaining": 30,
      "pills_per_dose": 1,
      "low_stock_threshold": 10,
      "active": true
    }
  ],
  "tracking": {
    "2025-11-07": {
      "med_1699564800000_morning": {
        "taken": true,
        "timestamp": "2025-11-07T08:30:00"
      }
    }
  },
  "time_windows": {},
  "last_updated": "2025-11-07T14:30:00"
}
```

**Response - File Not Found:**
```json
{
  "medicines": [],
  "tracking": {},
  "time_windows": {}
}
```

**Current Implementation:**
```python
@app.route('/api/medicine/data', methods=['GET'])
def get_medicine_data():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"medicines": [], "tracking": {}, "time_windows": {}}), 200
```

**Issues:**
- Returns 200 even on errors (should distinguish between empty and error)
- No pagination for large datasets
- Returns entire tracking history (could be huge)
- Direct file I/O
- No filtering options

---

#### `POST /api/medicine/add`
**Purpose:** Add a new medicine
**Handler:** `add_medicine()`
**Line:** 981-1002

**Request:**
- Method: POST
- Content-Type: application/json
- Body:
```json
{
  "id": "med_1699564800000",
  "name": "Vitamin D",
  "dosage": "2000 IU",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "12:00",
  "with_food": true,
  "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
  "notes": "Take with breakfast",
  "pills_remaining": 30,
  "pills_per_dose": 1,
  "low_stock_threshold": 10,
  "active": true
}
```

**Response - Success:**
```json
{
  "success": true,
  "message": "Medicine added successfully!"
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
```python
@app.route('/api/medicine/add', methods=['POST'])
def add_medicine():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        new_med = request.get_json()

        if 'medicines' not in data:
            data['medicines'] = []

        data['medicines'].append(new_med)

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
```

**Issues:**
- No validation of input data
- No check for duplicate IDs
- Direct file I/O with race conditions
- No atomicity (file could be corrupted on crash)
- ID generated client-side (should be server-side)
- No resource URI returned (not RESTful)

---

#### `POST /api/medicine/update`
**Purpose:** Update an existing medicine
**Handler:** `update_medicine()`
**Line:** 1004-1034

**Request:**
- Method: POST
- Content-Type: application/json
- Body: Complete medicine object with existing `id`
```json
{
  "id": "med_1699564800000",
  "name": "Vitamin D",
  "dosage": "3000 IU",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "12:00",
  "with_food": true,
  "days": ["mon", "wed", "fri"],
  "notes": "Updated dosage",
  "pills_remaining": 25,
  "pills_per_dose": 1,
  "low_stock_threshold": 10,
  "active": true
}
```

**Response - Success:**
```json
{
  "success": true,
  "message": "Medicine updated successfully!"
}
```

**Response - Not Found:**
```json
{
  "success": false,
  "message": "Medicine not found"
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
```python
@app.route('/api/medicine/update', methods=['POST'])
def update_medicine():
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        updated_med = request.get_json()

        if 'medicines' not in data:
            data['medicines'] = []

        # Find and update the medicine
        found = False
        for i, med in enumerate(data['medicines']):
            if med['id'] == updated_med['id']:
                data['medicines'][i] = updated_med
                found = True
                break

        if not found:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
```

**Issues:**
- Should use PUT/PATCH method, not POST
- Should have ID in URL path (e.g., PUT /api/medicine/{id})
- No validation of input data
- Direct file I/O with race conditions
- Full replacement only (no partial updates)
- No optimistic locking (lost update problem)

---

#### `DELETE /api/medicine/delete/<med_id>`
**Purpose:** Delete a medicine
**Handler:** `delete_medicine(med_id)`
**Line:** 1036-1060

**Request:**
- Method: DELETE
- URL Parameter: `med_id` (medicine ID)
- Body: None

**Example:**
```
DELETE /api/medicine/delete/med_1699564800000
```

**Response - Success:**
```json
{
  "success": true,
  "message": "Medicine deleted successfully!"
}
```

**Response - Not Found:**
```json
{
  "success": false,
  "message": "Medicine not found"
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
```python
@app.route('/api/medicine/delete/<med_id>', methods=['DELETE'])
def delete_medicine(med_id):
    try:
        with open(MEDICINE_DATA_FILE, 'r') as f:
            data = json.load(f)

        if 'medicines' not in data:
            data['medicines'] = []

        # Filter out the medicine to delete
        original_length = len(data['medicines'])
        data['medicines'] = [m for m in data['medicines'] if m['id'] != med_id]

        if len(data['medicines']) == original_length:
            return jsonify({"success": False, "message": "Medicine not found"}), 404

        # Add timestamp for push refresh
        data['last_updated'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

        return jsonify({"success": True, "message": "Medicine deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
```

**Issues:**
- URL path has redundant "/delete/" prefix (should be DELETE /api/medicine/{id})
- Direct file I/O with race conditions
- Doesn't clean up associated tracking data
- No soft delete option
- No confirmation or undo mechanism

---

#### `POST /api/medicine/mark-taken`
**Purpose:** Mark one or more medicines as taken
**Handler:** `mark_medicine_taken()`
**Line:** 1062-1188

**Request:**
- Method: POST
- Content-Type: application/json
- Body (single medicine):
```json
{
  "medicine_id": "med_1699564800000",
  "timestamp": "2025-11-07T08:30:00"
}
```
- Body (multiple medicines):
```json
{
  "medicine_ids": ["med_1699564800000", "med_1699564900000"],
  "timestamp": "2025-11-07T08:30:00"
}
```

**Response - Success:**
```json
{
  "success": true,
  "message": "Marked 1 medicine(s) as taken",
  "marked": [
    {
      "id": "med_1699564800000",
      "name": "Vitamin D",
      "pills_remaining": 29,
      "low_stock": false
    }
  ],
  "timestamp": "2025-11-07T08:30:00"
}
```

**Response - Partial Success:**
```json
{
  "success": true,
  "message": "Marked 1 medicine(s) as taken (1 not found)",
  "marked": [ ... ],
  "not_found": ["med_9999"],
  "timestamp": "2025-11-07T08:30:00"
}
```

**Response - Not Found:**
```json
{
  "success": false,
  "message": "No medicines found",
  "not_found": ["med_9999"]
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
- Lines 1062-1188 (127 lines - most complex endpoint)
- Supports both single and batch operations
- Validates timestamp format
- Decrements pill count atomically
- Tracks low stock warnings
- Updates last_updated timestamp

**Issues:**
- Direct file I/O with no locking
- Complex logic in route handler (should be in service layer)
- No idempotency (can mark taken multiple times)
- No undo mechanism
- Timestamp is optional but defaults to now (could cause confusion)

---

#### `GET /api/medicine/pending`
**Purpose:** Get medicines due now (within time window)
**Handler:** `get_pending_medicines()`
**Line:** 1190-1272

**Request:**
- Method: GET
- Query Parameters (optional):
  - `date`: YYYY-MM-DD (defaults to today)
  - `time`: HH:MM (defaults to current time)

**Example:**
```
GET /api/medicine/pending
GET /api/medicine/pending?date=2025-11-07&time=08:30
```

**Response - Success:**
```json
{
  "success": true,
  "count": 2,
  "medicines": [
    {
      "id": "med_1699564800000",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "time_window": "morning",
      "with_food": true,
      "notes": "Take with breakfast",
      "pills_remaining": 30,
      "low_stock": false
    }
  ],
  "checked_at": "2025-11-07T08:30:00"
}
```

**Response - Error:**
```json
{
  "success": false,
  "message": "Error: [error details]"
}
```

**Current Implementation:**
- Complex business logic (82 lines)
- Calculates time windows with 30-minute reminder buffer
- Filters by active status
- Checks scheduled days
- Checks if already taken today
- Returns pending medicines with stock status

**Issues:**
- Business logic in route handler
- Direct file I/O
- No pagination
- 30-minute window is hardcoded
- No customizable reminder preferences
- Complex time calculation logic should be in service layer

---

## Data Files

### CONFIG_FILE
**Path:** `/home/pizero2w/pizero_apps/config.json`
**Format:** JSON
**Purpose:** Application configuration for all apps
**Structure:**
```json
{
  "weather": { ... },
  "mbta": { ... },
  "disney": { ... },
  "flights": { ... },
  "pomodoro": { ... },
  "forbidden": { ... }
}
```

### MEDICINE_DATA_FILE
**Path:** `/home/pizero2w/pizero_apps/medicine_data.json`
**Format:** JSON
**Purpose:** Medicine tracking data
**Structure:**
```json
{
  "medicines": [ ... ],
  "tracking": { ... },
  "time_windows": { ... },
  "last_updated": "2025-11-07T14:30:00"
}
```

---

## Critical Issues Summary

### 1. Architecture Issues
- No separation of concerns (routes, business logic, data access mixed)
- No service layer
- No repository/DAO pattern
- Direct file I/O throughout
- No dependency injection

### 2. Data Integrity Issues
- Race conditions on read-modify-write operations
- No file locking
- No transactions
- No backup/recovery
- No data validation

### 3. RESTful Design Issues
- Inconsistent HTTP methods (POST for updates, redundant URL paths)
- No resource-based URLs
- No HATEOAS links
- No proper status codes
- ID generation client-side

### 4. Error Handling Issues
- Generic exception catching
- Inconsistent error responses
- No error codes
- No structured logging
- Stack traces exposed to clients

### 5. Security Issues
- No authentication/authorization
- No input validation
- No rate limiting
- No CSRF protection
- File paths hardcoded

### 6. Performance Issues
- Reads entire file on every request
- No caching
- No pagination
- No compression
- Synchronous I/O blocks

### 7. Scalability Issues
- Single file for all data
- No database
- No horizontal scaling possible
- File size will grow unbounded
- No archival strategy

---

## Migration Requirements

### Must Haves
1. Database migration (JSON → SQLite via MedicineDatabase)
2. Input validation (Marshmallow schemas)
3. Proper RESTful design (resource-based URLs, correct HTTP methods)
4. Separation of concerns (routes → services → repository)
5. Error handling (structured errors, proper status codes)
6. Logging and monitoring

### Should Haves
1. API versioning (/api/v1/)
2. Pagination for list endpoints
3. Partial updates (PATCH support)
4. Filtering and sorting
5. Response caching
6. Rate limiting

### Nice to Haves
1. OpenAPI/Swagger documentation
2. API key authentication
3. Webhooks for notifications
4. GraphQL alternative
5. WebSocket for real-time updates
6. Audit trail

---

## Next Steps

1. **Phase 1.2:** Design RESTful API structure (see API_DESIGN.md)
2. **Phase 1.3:** Create API module structure with blueprints
3. **Phase 1.4:** Implement service layer
4. **Phase 1.5:** Integrate with MedicineDatabase
5. **Phase 1.6:** Add validation middleware
6. **Phase 1.7:** Implement proper error handling
7. **Phase 1.8:** Write unit tests
8. **Phase 2.0:** Migrate configuration to database
