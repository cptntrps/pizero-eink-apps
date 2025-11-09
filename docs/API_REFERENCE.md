# Pi Zero 2W Medicine Tracker API - Complete Reference

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Versioning](#api-versioning)
4. [Response Format](#response-format)
5. [Error Codes](#error-codes)
6. [Health & Info Endpoints](#health--info-endpoints)
7. [Medicines Endpoints](#medicines-endpoints)
8. [Tracking Endpoints](#tracking-endpoints)
9. [Configuration Endpoints](#configuration-endpoints)
10. [Rate Limiting](#rate-limiting)
11. [Pagination](#pagination)
12. [Date/Time Formats](#datetime-formats)

---

## Overview

The Pi Zero 2W Medicine Tracker API provides a comprehensive RESTful interface for managing medicines, tracking adherence, and configuring application settings.

**Base URL:**
- Development: `http://localhost:5000/api/v1`
- Production: `http://{hostname}:5000/api/v1`

**API Version:** 1.0.0

**Supported Media Types:** `application/json`

---

## Authentication

Currently, the API operates without authentication mechanisms. In future releases, the following authentication methods are planned:

- API Key authentication
- JWT tokens
- OAuth 2.0

For now, ensure the API server is protected at the network level.

---

## API Versioning

The API uses URI versioning. All endpoints are prefixed with `/api/v1`.

**Future Versions:**
- `/api/v2` - Planned for future enhancements
- `/api/v3` - Reserved for future use

Version compatibility is maintained through the `API_VERSION` header in responses.

---

## Response Format

All API responses follow a consistent JSON structure:

### Success Response

```json
{
  "success": true,
  "message": "Optional success message",
  "data": {
    // Response data
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000",
    // Additional metadata
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      // Additional error details
    }
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [
    // Array of items
  ],
  "meta": {
    "total": 100,
    "count": 20,
    "page": 1,
    "per_page": 20,
    "total_pages": 5,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

---

## Error Codes

### HTTP Status Codes

| Status | Code | Description |
|--------|------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request succeeded, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not supported |
| 409 | Conflict | Resource conflict (duplicate, etc.) |
| 500 | Internal Server Error | Server error |

### Error Response Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Request validation failed |
| RESOURCE_NOT_FOUND | 404 | Requested resource doesn't exist |
| SECTION_NOT_FOUND | 404 | Configuration section not found |
| FILE_NOT_FOUND | 500 | Configuration file not found |
| DATABASE_ERROR | 500 | Database operation failed |
| INVALID_CONFIG | 500 | Configuration file is invalid |
| INTERNAL_ERROR | 500 | Unexpected server error |
| BAD_REQUEST | 400 | Invalid request format |
| METHOD_NOT_ALLOWED | 405 | HTTP method not allowed |
| CONFLICT | 409 | Resource conflict |

### Error Response Example

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid start_date format. Use YYYY-MM-DD",
    "details": {
      "field": "start_date"
    }
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

---

## Health & Info Endpoints

### Get API Root Information

Get API version and available endpoints.

```
GET /
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "version": "1.0",
    "name": "Pi Zero 2W Medicine Tracker API",
    "description": "RESTful API for medicine tracking and configuration",
    "endpoints": {
      "medicines": "/api/v1/medicines",
      "tracking": "/api/v1/tracking",
      "config": "/api/v1/config",
      "health": "/api/v1/health"
    },
    "documentation": "/api/v1/docs"
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Health Check

Check API and database health status.

```
GET /health
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected",
    "timestamp": "2025-11-08T15:30:00.000000"
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### API Documentation

Get links to API documentation resources.

```
GET /docs
```

**Response:** 200 OK

---

## Medicines Endpoints

### List Medicines

Get list of medicines with optional filtering and pagination.

```
GET /medicines
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| active | boolean | true | Filter by active status |
| page | integer | 1 | Page number |
| per_page | integer | 20 | Items per page (max 100) |
| sort | string | - | Field to sort by |
| order | string | - | Sort order (asc/desc) |

**Example Request:**

```bash
curl "http://localhost:5000/api/v1/medicines?active=true&page=1&per_page=20"
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "med_123456789",
      "name": "Aspirin",
      "dosage": "500mg",
      "frequency": "Twice daily",
      "stock": 100,
      "low_stock_threshold": 20,
      "time_windows": [
        {"hour": 8, "minute": 0},
        {"hour": 20, "minute": 0}
      ],
      "active": true,
      "created_at": "2025-11-01T10:00:00",
      "updated_at": "2025-11-08T10:00:00"
    }
  ],
  "meta": {
    "total": 5,
    "count": 5,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Create Medicine

Create a new medicine.

```
POST /medicines
```

**Request Body:**

```json
{
  "name": "Metformin",
  "dosage": "1000mg",
  "frequency": "Daily",
  "stock": 60,
  "low_stock_threshold": 20,
  "time_windows": [
    {"hour": 8, "minute": 0},
    {"hour": 20, "minute": 0}
  ],
  "active": true
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Metformin",
    "dosage": "1000mg",
    "frequency": "Daily",
    "stock": 60,
    "low_stock_threshold": 20
  }'
```

**Response:** 201 Created

```json
{
  "success": true,
  "data": {
    "id": "med_1699457400000",
    "name": "Metformin",
    "dosage": "1000mg",
    "frequency": "Daily",
    "stock": 60,
    "low_stock_threshold": 20,
    "time_windows": [],
    "active": true,
    "created_at": "2025-11-08T15:30:00",
    "updated_at": "2025-11-08T15:30:00"
  },
  "message": "Medicine created successfully",
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

**Headers:**
- `Location: /api/v1/medicines/med_1699457400000`

### Get Medicine

Get a specific medicine by ID.

```
GET /medicines/{medicineId}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| medicineId | string | Medicine ID |

**Example Request:**

```bash
curl http://localhost:5000/api/v1/medicines/med_123456789
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "id": "med_123456789",
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 100,
    "low_stock_threshold": 20,
    "active": true,
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2025-11-08T10:00:00"
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Update Medicine (Full)

Replace entire medicine (full update).

```
PUT /medicines/{medicineId}
```

**Request Body:**

```json
{
  "name": "Aspirin",
  "dosage": "500mg",
  "frequency": "Twice daily",
  "stock": 80,
  "low_stock_threshold": 15,
  "active": true
}
```

**Example Request:**

```bash
curl -X PUT http://localhost:5000/api/v1/medicines/med_123456789 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 80,
    "low_stock_threshold": 15,
    "active": true
  }'
```

**Response:** 200 OK

### Update Medicine (Partial)

Partial update of medicine (only specified fields).

```
PATCH /medicines/{medicineId}
```

**Request Body:**

```json
{
  "stock": 80
}
```

**Example Request:**

```bash
curl -X PATCH http://localhost:5000/api/v1/medicines/med_123456789 \
  -H "Content-Type: application/json" \
  -d '{"stock": 80}'
```

**Response:** 200 OK

### Delete Medicine

Delete a medicine.

```
DELETE /medicines/{medicineId}
```

**Example Request:**

```bash
curl -X DELETE http://localhost:5000/api/v1/medicines/med_123456789
```

**Response:** 204 No Content

### Get Pending Medicines

Get medicines that are due now (within time window).

```
GET /medicines/pending
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Check date (YYYY-MM-DD, default: today) |
| time | string | Check time (HH:MM, default: now) |
| reminder_window | integer | Minutes before/after window (default: 30) |

**Example Request:**

```bash
curl "http://localhost:5000/api/v1/medicines/pending?reminder_window=30"
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "med_123456789",
      "name": "Aspirin",
      "dosage": "500mg",
      "frequency": "Twice daily",
      "stock": 100,
      "low_stock_threshold": 20,
      "time_windows": [
        {"hour": 8, "minute": 0},
        {"hour": 20, "minute": 0}
      ],
      "active": true
    }
  ],
  "meta": {
    "count": 1,
    "checked_at": "2025-11-08T15:30:00",
    "reminder_window": 30,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Get Low Stock Medicines

Get medicines with low stock.

```
GET /medicines/low-stock
```

**Example Request:**

```bash
curl http://localhost:5000/api/v1/medicines/low-stock
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "med_987654321",
      "name": "Ibuprofen",
      "dosage": "200mg",
      "frequency": "Every 6 hours",
      "stock": 15,
      "low_stock_threshold": 20
    }
  ],
  "meta": {
    "count": 1,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Mark Medicine Taken

Mark a specific medicine as taken (convenience endpoint).

```
POST /medicines/{medicineId}/take
```

**Request Body (optional):**

```json
{
  "timestamp": "2025-11-08T08:30:00"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/medicines/med_123456789/take \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:** 201 Created

```json
{
  "success": true,
  "data": {
    "medicine_id": "med_123456789",
    "medicine_name": "Aspirin",
    "pills_remaining": 99,
    "low_stock": false,
    "taken_at": "2025-11-08T15:30:00"
  },
  "message": "Medicine marked as taken",
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Mark Multiple Medicines Taken (Batch)

Mark multiple medicines as taken (batch operation).

```
POST /medicines/batch-take
```

**Request Body:**

```json
{
  "medicine_ids": ["med_123456789", "med_987654321"],
  "timestamp": "2025-11-08T08:30:00"
}
```

**Example Request:**

```bash
curl -X POST http://localhost:5000/api/v1/medicines/batch-take \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_ids": ["med_123456789", "med_987654321"]
  }'
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "marked": [
      {
        "id": "med_123456789",
        "name": "Aspirin",
        "pills_remaining": 99,
        "low_stock": false
      },
      {
        "id": "med_987654321",
        "name": "Ibuprofen",
        "pills_remaining": 14,
        "low_stock": true
      }
    ],
    "errors": [],
    "timestamp": "2025-11-08T15:30:00"
  },
  "message": "Marked 2 medicine(s) as taken",
  "meta": {
    "count": 2,
    "error_count": 0,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

---

## Tracking Endpoints

### Get Medicine Tracking History

Get tracking history for a specific medicine.

```
GET /medicines/{medicineId}/tracking
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Start date (YYYY-MM-DD, optional) |
| end_date | string | End date (YYYY-MM-DD, optional) |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |

**Example Request:**

```bash
curl "http://localhost:5000/api/v1/medicines/med_123456789/tracking?start_date=2025-11-01&end_date=2025-11-08"
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": [
    {
      "id": "track_1",
      "medicine_id": "med_123456789",
      "date": "2025-11-08",
      "taken": true,
      "timestamp": "2025-11-08T08:30:00"
    },
    {
      "id": "track_2",
      "medicine_id": "med_123456789",
      "date": "2025-11-08",
      "taken": true,
      "timestamp": "2025-11-08T20:30:00"
    }
  ],
  "meta": {
    "total": 16,
    "count": 2,
    "page": 1,
    "per_page": 20,
    "total_pages": 1,
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Mark Medicine Taken (Tracking)

Mark a specific medicine as taken (tracking endpoint).

```
POST /medicines/{medicineId}/tracking
```

**Request Body (optional):**

```json
{
  "timestamp": "2025-11-08T08:30:00"
}
```

**Response:** 201 Created

### Get All Tracking

Get tracking history for all medicines with filtering.

```
GET /tracking
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| medicine_id | string | Filter by medicine ID (optional) |
| start_date | string | Start date (YYYY-MM-DD, optional) |
| end_date | string | End date (YYYY-MM-DD, optional) |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |

**Example Request:**

```bash
curl "http://localhost:5000/api/v1/tracking?start_date=2025-11-01"
```

**Response:** 200 OK

### Batch Mark Medicines Taken

Mark multiple medicines as taken (batch operation).

```
POST /tracking
```

**Request Body:**

```json
{
  "medicine_ids": ["med_123456789", "med_987654321"],
  "timestamp": "2025-11-08T08:30:00"
}
```

**Response:** 200 OK

### Get Today's Statistics

Get today's medicine adherence statistics.

```
GET /tracking/today
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| date | string | Check date (YYYY-MM-DD, default: today) |

**Example Request:**

```bash
curl http://localhost:5000/api/v1/tracking/today
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "date": "2025-11-08",
    "total_medicines": 5,
    "medicines_taken": 4,
    "medicines_pending": 1,
    "adherence_rate": 0.8,
    "low_stock_count": 1
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Get Adherence Statistics

Get adherence statistics over a period.

```
GET /tracking/stats
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| start_date | string | Start date (YYYY-MM-DD, default: 7 days ago) |
| end_date | string | End date (YYYY-MM-DD, default: today) |
| medicine_id | string | Filter by medicine ID (optional) |

**Example Request:**

```bash
curl "http://localhost:5000/api/v1/tracking/stats?start_date=2025-11-01&end_date=2025-11-08"
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2025-11-01",
      "end_date": "2025-11-08",
      "days": 8
    },
    "overall": {
      "total_records": 80,
      "taken_records": 72,
      "adherence_rate": 0.9
    },
    "daily": [
      {
        "date": "2025-11-08",
        "total": 10,
        "taken": 8,
        "adherence_rate": 0.8
      },
      {
        "date": "2025-11-07",
        "total": 10,
        "taken": 10,
        "adherence_rate": 1.0
      }
    ]
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

---

## Configuration Endpoints

### Get All Configuration

Get entire application configuration.

```
GET /config
```

**Example Request:**

```bash
curl http://localhost:5000/api/v1/config
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    "weather": { },
    "mbta": { },
    "disney": { },
    "flights": { },
    "pomodoro": { },
    "forbidden": { },
    "medicine": { },
    "menu": { },
    "system": { },
    "display": { }
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Update All Configuration

Replace entire application configuration.

```
PUT /config
```

**Request Body:**

```json
{
  "weather": { },
  "mbta": { },
  "medicine": { },
  // ... other sections
}
```

**Response:** 200 OK

### Get Configuration Section

Get specific configuration section.

```
GET /config/{section}
```

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| section | string | Section name (weather, mbta, disney, flights, pomodoro, forbidden, medicine, menu, system, display) |

**Example Request:**

```bash
curl http://localhost:5000/api/v1/config/medicine
```

**Response:** 200 OK

```json
{
  "success": true,
  "data": {
    // Medicine configuration
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Update Configuration Section (Full)

Replace entire configuration section.

```
PUT /config/{section}
```

**Request Body:**

```json
{
  // Section data
}
```

**Response:** 200 OK

### Update Configuration Section (Partial)

Partial update of configuration section.

```
PATCH /config/{section}
```

**Request Body:**

```json
{
  "key": "value"
}
```

**Example Request:**

```bash
curl -X PATCH http://localhost:5000/api/v1/config/medicine \
  -H "Content-Type: application/json" \
  -d '{"setting": "value"}'
```

**Response:** 200 OK

---

## Rate Limiting

**Current Status:** Disabled in development, enabled in production.

**Production Limits:**
- 60 requests per minute per client
- Rate limit information provided in response headers (future)

---

## Pagination

Paginated endpoints support the following query parameters:

**Query Parameters:**

| Parameter | Type | Default | Max |
|-----------|------|---------|-----|
| page | integer | 1 | - |
| per_page | integer | 20 | 100 |

**Meta Information:**

The `meta` field in paginated responses includes:

```json
{
  "total": 100,          // Total number of items
  "count": 20,           // Number of items in this page
  "page": 1,             // Current page number
  "per_page": 20,        // Items per page
  "total_pages": 5,      // Total number of pages
  "timestamp": "..."     // Response timestamp
}
```

**Calculation:**

- Total pages = `ceil(total / per_page)`
- Current offset = `(page - 1) * per_page`

---

## Date/Time Formats

### Date Format

- Format: `YYYY-MM-DD`
- Example: `2025-11-08`
- Used for: `start_date`, `end_date`, `date` query parameters

### Time Format

- Format: `HH:MM` (24-hour)
- Example: `15:30`
- Range: `00:00` to `23:59`

### DateTime Format

- Format: ISO 8601 with timezone (UTC)
- Example: `2025-11-08T15:30:00.000000`
- Used in: Responses, optional timestamps

### Timezone

All timestamps are in UTC/ISO 8601 format. Clients should convert to local timezone as needed.

---

## Common Request Patterns

### Using cURL

**GET Request:**

```bash
curl http://localhost:5000/api/v1/medicines
```

**POST Request:**

```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"name": "Medicine", "dosage": "100mg", "frequency": "Daily", "stock": 50}'
```

**PUT Request:**

```bash
curl -X PUT http://localhost:5000/api/v1/medicines/med_123 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Medicine", "stock": 40}'
```

**PATCH Request:**

```bash
curl -X PATCH http://localhost:5000/api/v1/medicines/med_123 \
  -H "Content-Type: application/json" \
  -d '{"stock": 40}'
```

**DELETE Request:**

```bash
curl -X DELETE http://localhost:5000/api/v1/medicines/med_123
```

### Using Python Requests

```python
import requests

# GET
response = requests.get('http://localhost:5000/api/v1/medicines')
print(response.json())

# POST
data = {
    'name': 'Aspirin',
    'dosage': '500mg',
    'frequency': 'Daily',
    'stock': 100
}
response = requests.post('http://localhost:5000/api/v1/medicines', json=data)
print(response.status_code)
print(response.json())

# PUT
response = requests.put('http://localhost:5000/api/v1/medicines/med_123', json={'stock': 80})

# PATCH
response = requests.patch('http://localhost:5000/api/v1/medicines/med_123', json={'stock': 80})

# DELETE
response = requests.delete('http://localhost:5000/api/v1/medicines/med_123')
```

### Using JavaScript Fetch

```javascript
// GET
fetch('http://localhost:5000/api/v1/medicines')
  .then(res => res.json())
  .then(data => console.log(data));

// POST
fetch('http://localhost:5000/api/v1/medicines', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Aspirin',
    dosage: '500mg',
    frequency: 'Daily',
    stock: 100
  })
})
.then(res => res.json())
.then(data => console.log(data));

// PUT
fetch('http://localhost:5000/api/v1/medicines/med_123', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({stock: 80})
});

// DELETE
fetch('http://localhost:5000/api/v1/medicines/med_123', {
  method: 'DELETE'
});
```

---

## Best Practices

1. **Always check the `success` field** in responses to determine if the request was successful.

2. **Use appropriate HTTP methods:**
   - `GET` for retrieving data
   - `POST` for creating resources
   - `PUT` for full updates
   - `PATCH` for partial updates
   - `DELETE` for removing resources

3. **Handle pagination** for large datasets:
   - Check `meta.total_pages` to understand pagination
   - Iterate through pages to get all data

4. **Use date filters** for tracking data:
   - Specify date ranges to improve query performance
   - Use `start_date` and `end_date` parameters

5. **Batch operations** when marking multiple medicines taken:
   - Use `/medicines/batch-take` instead of multiple POST requests
   - More efficient and atomic operations

6. **Monitor low stock:**
   - Use `/medicines/low-stock` endpoint regularly
   - Set appropriate `low_stock_threshold` values

7. **Check API health:**
   - Use `/health` endpoint to verify API availability
   - Monitor database connectivity

8. **Cache configuration data:**
   - Configuration changes infrequently
   - Cache results to reduce API calls

9. **Use appropriate pagination:**
   - Default `per_page` is 20, adjust as needed
   - Max `per_page` is 100

10. **Handle errors gracefully:**
    - Check error codes and messages
    - Implement retry logic for transient errors
    - Log errors for debugging

---

## Troubleshooting

### 404 Not Found

- Verify the endpoint path is correct
- Check that the resource ID is valid
- Ensure the HTTP method matches the endpoint

### 400 Bad Request

- Validate request body JSON syntax
- Check required fields are included
- Verify date/time format (YYYY-MM-DD, HH:MM)
- Confirm query parameter types and values

### 500 Internal Server Error

- Check server logs for details
- Verify database connectivity
- Ensure configuration files are valid JSON
- Check file permissions on the Pi Zero device

### Empty Response Data

- Verify filters are not too restrictive
- Check pagination parameters
- Ensure date ranges contain data

---

## Related Documentation

- [API Quick Start](./API_QUICKSTART.md) - Getting started guide
- [OpenAPI Specification](./openapi.yaml) - Complete API schema
- [Architecture Documentation](./API_DESIGN.md) - API design details
