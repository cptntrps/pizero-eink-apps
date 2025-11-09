# RESTful API Design - Pi Zero 2W Medicine Tracker

**Version:** 1.0
**Date:** 2025-11-08
**Author:** Phase 1.1 - API Architecture Design

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [API Structure](#api-structure)
3. [Versioning Strategy](#versioning-strategy)
4. [URL Design](#url-design)
5. [Response Format](#response-format)
6. [Error Handling](#error-handling)
7. [Endpoint Specifications](#endpoint-specifications)
8. [Data Models](#data-models)
9. [Module Architecture](#module-architecture)
10. [Migration Path](#migration-path)

---

## Design Principles

### RESTful Best Practices

1. **Resource-Based URLs**
   - Use nouns, not verbs: `/medicines` not `/getMedicines`
   - Use HTTP methods for actions: GET, POST, PUT, PATCH, DELETE
   - Hierarchical relationships: `/medicines/{id}/tracking`

2. **HTTP Method Semantics**
   - `GET`: Retrieve resources (safe, idempotent, cacheable)
   - `POST`: Create new resources (not idempotent)
   - `PUT`: Replace entire resource (idempotent)
   - `PATCH`: Partial update (idempotent)
   - `DELETE`: Remove resource (idempotent)

3. **Status Code Usage**
   - `200 OK`: Successful GET/PUT/PATCH/DELETE
   - `201 Created`: Successful POST with resource creation
   - `204 No Content`: Successful DELETE with no body
   - `400 Bad Request`: Invalid input/validation error
   - `404 Not Found`: Resource doesn't exist
   - `409 Conflict`: Duplicate resource
   - `500 Internal Server Error`: Server error

4. **Consistent Response Format**
   - Always return JSON
   - Include metadata (success, message, data)
   - Use standard error format
   - Include timestamps

5. **API Versioning**
   - Version in URL: `/api/v1/`
   - Major version changes break compatibility
   - Minor changes are backward compatible

---

## API Structure

### Base URL
```
http://192.168.50.202:5000/api/v1
```

### URL Hierarchy
```
/api/v1/
├── medicines/                    # Medicine management
│   ├── GET/POST                 # List all / Create new
│   ├── {id}                     # Specific medicine
│   │   ├── GET/PUT/PATCH/DELETE
│   ├── {id}/tracking            # Medicine tracking history
│   │   ├── GET                  # Get tracking history
│   │   └── POST                 # Mark as taken
│   ├── pending                  # Pending medicines
│   │   └── GET
│   └── low-stock               # Low stock warnings
│       └── GET
│
├── tracking/                     # Tracking operations
│   ├── GET                      # Get all tracking
│   ├── POST                     # Mark medicines taken (batch)
│   └── today                    # Today's statistics
│       └── GET
│
├── config/                       # Configuration management
│   ├── GET/PUT                  # Full config
│   ├── weather                  # Weather settings
│   │   └── GET/PUT/PATCH
│   ├── mbta                     # MBTA settings
│   │   └── GET/PUT/PATCH
│   ├── disney                   # Disney settings
│   │   └── GET/PUT/PATCH
│   ├── flights                  # Flights settings
│   │   └── GET/PUT/PATCH
│   ├── pomodoro                 # Pomodoro settings
│   │   └── GET/PUT/PATCH
│   └── forbidden                # Forbidden settings
│       └── GET/PUT/PATCH
│
└── health                       # Health check
    └── GET
```

---

## Versioning Strategy

### Version 1 (v1) - Current
- Initial RESTful API
- Database-backed storage (SQLite)
- Marshmallow validation
- Basic authentication ready

### Future Versions
- **v2**: GraphQL support, webhook subscriptions
- **v3**: Advanced analytics, machine learning predictions

### Version Migration
- Old versions supported for 12 months after deprecation
- Deprecation warnings in response headers
- Migration guides provided

---

## URL Design

### Endpoint Naming Rules

1. **Use plural nouns for collections**
   ```
   ✅ /api/v1/medicines
   ❌ /api/v1/medicine
   ```

2. **Use resource IDs in path**
   ```
   ✅ /api/v1/medicines/med_123
   ❌ /api/v1/medicines?id=med_123
   ```

3. **Use query parameters for filtering**
   ```
   ✅ /api/v1/medicines?active=true&time_window=morning
   ❌ /api/v1/medicines/active/morning
   ```

4. **Use sub-resources for relationships**
   ```
   ✅ /api/v1/medicines/med_123/tracking
   ❌ /api/v1/tracking?medicine_id=med_123
   ```

5. **Use kebab-case for multi-word endpoints**
   ```
   ✅ /api/v1/medicines/low-stock
   ❌ /api/v1/medicines/lowStock
   ```

---

## Response Format

### Success Response Structure

```json
{
  "success": true,
  "message": "Optional success message",
  "data": {
    // Resource data or result
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z",
    "version": "1.0"
  }
}
```

### List Response with Pagination

```json
{
  "success": true,
  "data": [
    { /* resource 1 */ },
    { /* resource 2 */ }
  ],
  "meta": {
    "total": 50,
    "count": 20,
    "page": 1,
    "per_page": 20,
    "total_pages": 3,
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "name": ["This field is required"],
      "dosage": ["Must be between 1 and 20 characters"]
    }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z",
    "request_id": "req_123456"
  }
}
```

---

## Error Handling

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `RESOURCE_NOT_FOUND` | 404 | Requested resource doesn't exist |
| `DUPLICATE_RESOURCE` | 409 | Resource already exists |
| `INVALID_REQUEST` | 400 | Malformed request |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `INTERNAL_ERROR` | 500 | Unexpected server error |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |

### Error Response Examples

**Validation Error (400)**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "pills_remaining": ["Must be between 0 and 1000"],
      "time_window": ["Must be one of: morning, afternoon, evening, night"]
    }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Not Found Error (404)**
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Medicine not found",
    "details": {
      "medicine_id": "med_999",
      "resource_type": "medicine"
    }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Server Error (500)**
```json
{
  "success": false,
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to save medicine",
    "details": {
      "error_id": "err_abc123"
    }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

## Endpoint Specifications

### Medicine Management

#### `GET /api/v1/medicines`
**Description:** List all medicines

**Query Parameters:**
- `active` (boolean): Filter by active status (default: true)
- `time_window` (string): Filter by time window
- `low_stock` (boolean): Filter medicines with low stock
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `sort` (string): Sort field (name, time_window, pills_remaining)
- `order` (string): Sort order (asc, desc)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
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
      "active": true,
      "created_at": "2025-11-01T10:00:00Z",
      "updated_at": "2025-11-07T14:30:00Z"
    }
  ],
  "meta": {
    "total": 5,
    "count": 5,
    "page": 1,
    "per_page": 20,
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

#### `POST /api/v1/medicines`
**Description:** Create a new medicine

**Request Body:**
```json
{
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

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Medicine created successfully",
  "data": {
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
    "active": true,
    "created_at": "2025-11-08T14:30:00Z",
    "updated_at": "2025-11-08T14:30:00Z"
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Headers:**
```
Location: /api/v1/medicines/med_1699564800000
```

---

#### `GET /api/v1/medicines/{id}`
**Description:** Get a specific medicine

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
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
    "active": true,
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-07T14:30:00Z"
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Medicine not found",
    "details": {
      "medicine_id": "med_999"
    }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

#### `PUT /api/v1/medicines/{id}`
**Description:** Replace entire medicine (full update)

**Request Body:** Complete medicine object (all fields required)

**Response (200 OK):** Updated medicine object

---

#### `PATCH /api/v1/medicines/{id}`
**Description:** Partial update of medicine

**Request Body:**
```json
{
  "pills_remaining": 25,
  "notes": "Updated note"
}
```

**Response (200 OK):** Updated medicine object

---

#### `DELETE /api/v1/medicines/{id}`
**Description:** Delete a medicine

**Response (204 No Content):** Empty body

---

#### `GET /api/v1/medicines/pending`
**Description:** Get pending medicines (due now)

**Query Parameters:**
- `date` (string): Check date YYYY-MM-DD (default: today)
- `time` (string): Check time HH:MM (default: now)
- `reminder_window` (integer): Minutes before/after window (default: 30)

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
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
  "meta": {
    "count": 1,
    "checked_at": "2025-11-08T08:30:00Z",
    "reminder_window": 30,
    "timestamp": "2025-11-08T08:30:00Z"
  }
}
```

---

#### `GET /api/v1/medicines/low-stock`
**Description:** Get medicines with low stock

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "id": "med_1699564800000",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "pills_remaining": 8,
      "pills_per_dose": 1,
      "low_stock_threshold": 10,
      "days_remaining": 8.0
    }
  ],
  "meta": {
    "count": 1,
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

### Tracking Operations

#### `POST /api/v1/medicines/{id}/tracking`
**Description:** Mark a specific medicine as taken

**Request Body:**
```json
{
  "timestamp": "2025-11-08T08:30:00"
}
```
(timestamp is optional, defaults to now)

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Medicine marked as taken",
  "data": {
    "medicine_id": "med_1699564800000",
    "medicine_name": "Vitamin D",
    "pills_remaining": 29,
    "low_stock": false,
    "taken_at": "2025-11-08T08:30:00Z"
  },
  "meta": {
    "timestamp": "2025-11-08T08:30:00Z"
  }
}
```

---

#### `GET /api/v1/medicines/{id}/tracking`
**Description:** Get tracking history for a medicine

**Query Parameters:**
- `start_date` (string): Start date YYYY-MM-DD
- `end_date` (string): End date YYYY-MM-DD
- `page` (integer): Page number
- `per_page` (integer): Items per page

**Response (200 OK):**
```json
{
  "success": true,
  "data": [
    {
      "medicine_id": "med_1699564800000",
      "date": "2025-11-08",
      "time_window": "morning",
      "taken": true,
      "timestamp": "2025-11-08T08:30:00Z",
      "pills_taken": 1
    }
  ],
  "meta": {
    "total": 30,
    "count": 20,
    "page": 1,
    "per_page": 20,
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

#### `POST /api/v1/tracking`
**Description:** Mark multiple medicines as taken (batch operation)

**Request Body:**
```json
{
  "medicine_ids": ["med_1699564800000", "med_1699564900000"],
  "timestamp": "2025-11-08T08:30:00"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Marked 2 medicine(s) as taken",
  "data": {
    "marked": [
      {
        "id": "med_1699564800000",
        "name": "Vitamin D",
        "pills_remaining": 29,
        "low_stock": false
      },
      {
        "id": "med_1699564900000",
        "name": "Omega-3",
        "pills_remaining": 45,
        "low_stock": false
      }
    ],
    "timestamp": "2025-11-08T08:30:00Z"
  },
  "meta": {
    "count": 2,
    "timestamp": "2025-11-08T08:30:00Z"
  }
}
```

---

#### `GET /api/v1/tracking/today`
**Description:** Get today's adherence statistics

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "date": "2025-11-08",
    "total_medicines": 5,
    "medicines_taken": 3,
    "medicines_pending": 2,
    "adherence_rate": 0.6,
    "low_stock_count": 1
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

### Configuration Management

#### `GET /api/v1/config`
**Description:** Get entire configuration

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "weather": { ... },
    "mbta": { ... },
    "disney": { ... },
    "flights": { ... },
    "pomodoro": { ... },
    "forbidden": { ... }
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

#### `GET /api/v1/config/weather`
**Description:** Get weather configuration

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "location": "Rio de Janeiro",
    "units": "metric",
    "update_interval": 300,
    "display_format": "detailed"
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

#### `PATCH /api/v1/config/weather`
**Description:** Update weather configuration (partial)

**Request Body:**
```json
{
  "location": "Boston",
  "update_interval": 600
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Weather configuration updated",
  "data": {
    "location": "Boston",
    "units": "metric",
    "update_interval": 600,
    "display_format": "detailed"
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

### Health Check

#### `GET /api/v1/health`
**Description:** API health check

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected",
    "uptime_seconds": 86400
  },
  "meta": {
    "timestamp": "2025-11-08T14:30:00Z"
  }
}
```

---

## Data Models

### Medicine

```python
{
  "id": "string",                    # Format: med_{timestamp}
  "name": "string",                  # 1-50 chars
  "dosage": "string",                # 1-20 chars
  "time_window": "string",           # morning|afternoon|evening|night
  "window_start": "string",          # HH:MM format
  "window_end": "string",            # HH:MM format
  "with_food": "boolean",
  "days": ["string"],                # Array of: mon|tue|wed|thu|fri|sat|sun
  "notes": "string|null",            # 0-100 chars
  "pills_remaining": "integer",      # 0-1000
  "pills_per_dose": "integer",       # 1-10
  "low_stock_threshold": "integer",  # 1-100
  "active": "boolean",
  "created_at": "string",            # ISO 8601 timestamp
  "updated_at": "string"             # ISO 8601 timestamp
}
```

### Tracking Record

```python
{
  "medicine_id": "string",
  "date": "string",                  # YYYY-MM-DD
  "time_window": "string",
  "taken": "boolean",
  "timestamp": "string",             # ISO 8601 timestamp
  "pills_taken": "integer"
}
```

### Configuration Section

```python
# Weather
{
  "location": "string",
  "units": "string",                 # metric|imperial
  "update_interval": "integer",      # seconds
  "display_format": "string"         # detailed|simple
}

# MBTA
{
  "home_station_id": "string",
  "home_station_name": "string",
  "work_station_id": "string",
  "work_station_name": "string",
  "update_interval": "integer",
  "morning_start": "string",         # HH:MM
  "morning_end": "string",           # HH:MM
  "evening_start": "string",         # HH:MM
  "evening_end": "string"            # HH:MM
}

# Disney
{
  "park_id": "integer",              # 5|6|7|8
  "update_interval": "integer",
  "data_refresh_rides": "integer",
  "sort_by": "string"                # wait_time|name
}

# Flights
{
  "lat": "string",
  "lon": "string",
  "altitude": "integer"
}

# Pomodoro
{
  "work_duration": "integer",        # seconds
  "short_break": "integer",          # seconds
  "long_break": "integer",           # seconds
  "sessions_until_long_break": "integer"
}

# Forbidden
{
  "message": "string"
}
```

---

## Module Architecture

### Directory Structure

```
api/
├── __init__.py                   # Flask app factory
├── config.py                     # Configuration management
├── extensions.py                 # Flask extensions (CORS, etc.)
│
├── v1/                           # Version 1 API
│   ├── __init__.py              # Blueprint registration
│   │
│   ├── routes/                   # Route handlers
│   │   ├── __init__.py
│   │   ├── medicines.py         # Medicine CRUD routes
│   │   ├── tracking.py          # Tracking routes
│   │   └── config.py            # Configuration routes
│   │
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── medicine_service.py  # Medicine business logic
│   │   ├── tracking_service.py  # Tracking business logic
│   │   └── config_service.py    # Config business logic
│   │
│   ├── serializers/              # Response formatting
│   │   ├── __init__.py
│   │   ├── medicine_serializer.py
│   │   └── tracking_serializer.py
│   │
│   └── middleware/               # Request/response processing
│       ├── __init__.py
│       ├── error_handler.py     # Error handling middleware
│       ├── validator.py         # Input validation middleware
│       └── logging_middleware.py # Request logging
│
├── templates/                    # HTML templates (if needed)
│   └── index.html
│
└── static/                       # Static files (if needed)
    ├── css/
    ├── js/
    └── images/
```

### Layer Responsibilities

#### 1. Routes Layer (`api/v1/routes/`)
- Parse HTTP requests
- Call service layer
- Return HTTP responses
- Handle HTTP-specific concerns (headers, status codes)
- NO business logic
- NO database access

#### 2. Services Layer (`api/v1/services/`)
- Business logic implementation
- Orchestrate database operations
- Data transformation
- Complex calculations
- NO HTTP concerns
- NO direct database queries (use repository)

#### 3. Repository Layer (`db/medicine_db.py`)
- Database access
- CRUD operations
- Transaction management
- Query building
- NO business logic

#### 4. Validation Layer (`shared/validation.py`)
- Input validation (Marshmallow)
- Data sanitization
- Schema validation
- Error formatting

#### 5. Serialization Layer (`api/v1/serializers/`)
- Format database objects for API responses
- Add metadata
- Handle pagination
- Format timestamps

---

## Migration Path

### Phase 1: API Infrastructure Setup
**Status:** In Progress (Phase 1.1)

1. ✅ Document existing endpoints (API_ENDPOINT_INVENTORY.md)
2. ✅ Design RESTful API (API_DESIGN.md)
3. ⏳ Create API module structure
4. ⏳ Implement Flask app factory
5. ⏳ Set up blueprints

### Phase 2: Medicine API Implementation
**Status:** Pending

1. Implement medicine routes
2. Implement medicine service
3. Integrate with MedicineDatabase
4. Add Marshmallow validation
5. Implement serializers
6. Unit tests

### Phase 3: Tracking API Implementation
**Status:** Pending

1. Implement tracking routes
2. Implement tracking service
3. Add validation
4. Implement serializers
5. Unit tests

### Phase 4: Configuration API Implementation
**Status:** Pending

1. Design config database schema
2. Implement config routes
3. Implement config service
4. Migrate JSON config to database
5. Unit tests

### Phase 5: Frontend Integration
**Status:** Pending

1. Update JavaScript to use new API endpoints
2. Handle new response format
3. Implement error handling
4. Add loading states
5. Integration tests

### Phase 6: Deployment
**Status:** Pending

1. Update systemd service
2. Database migration script
3. Rollback plan
4. Monitoring setup
5. Documentation

---

## Next Steps

### Immediate (Phase 1.2)
1. Create `api/__init__.py` with Flask app factory
2. Create `api/v1/__init__.py` with blueprint setup
3. Create basic route stubs for all endpoints
4. Create service layer stubs
5. Set up error handling middleware

### Short-term (Phase 1.3-1.5)
1. Implement medicine endpoints
2. Integrate with MedicineDatabase
3. Add comprehensive validation
4. Write unit tests
5. Update frontend to use new API

### Long-term (Phase 2.0+)
1. Migrate configuration to database
2. Add authentication/authorization
3. Implement rate limiting
4. Add caching layer
5. Generate OpenAPI documentation
6. Implement webhooks for notifications

---

## References

- **Existing Database:** `/home/user/pizerowgpio/db/medicine_db.py`
- **Existing Validation:** `/home/user/pizerowgpio/shared/validation.py`
- **Current Implementation:** `/home/user/pizerowgpio/web_config.py`
- **Endpoint Inventory:** `/home/user/pizerowgpio/docs/API_ENDPOINT_INVENTORY.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Next Review:** Phase 1.2 completion
