# API Error Codes Reference

## Table of Contents

1. [Error Response Format](#error-response-format)
2. [HTTP Status Codes](#http-status-codes)
3. [Error Code Reference](#error-code-reference)
4. [Common Error Scenarios](#common-error-scenarios)
5. [Error Handling Guide](#error-handling-guide)
6. [Troubleshooting](#troubleshooting)

---

## Error Response Format

All error responses follow a consistent JSON structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "additional context about the error"
    }
  },
  "meta": {
    "timestamp": "2025-11-08T15:30:00.000000"
  }
}
```

### Response Components

| Component | Type | Description |
|-----------|------|-------------|
| success | boolean | Always `false` for errors |
| error.code | string | Machine-readable error code |
| error.message | string | Human-readable error message |
| error.details | object | Additional error context (optional) |
| meta.timestamp | string | When error occurred (ISO 8601) |

---

## HTTP Status Codes

### 2xx Success

| Status | Code | Description |
|--------|------|-------------|
| 200 | OK | Request succeeded, response body contains data |
| 201 | Created | Resource created successfully (POST) |
| 204 | No Content | Request succeeded, no content to return (DELETE) |

### 4xx Client Error

| Status | Code | Description |
|--------|------|-------------|
| 400 | Bad Request | Invalid request parameters or malformed data |
| 404 | Not Found | Requested resource doesn't exist |
| 405 | Method Not Allowed | HTTP method not supported for this endpoint |
| 409 | Conflict | Resource conflict (duplicate ID, etc.) |

### 5xx Server Error

| Status | Code | Description |
|--------|------|-------------|
| 500 | Internal Server Error | Unexpected server error |

---

## Error Code Reference

### Validation Errors (400)

#### VALIDATION_ERROR

**HTTP Status:** 400 Bad Request

**Occurs When:**
- Invalid request data
- Missing required fields
- Invalid data types
- Invalid format (date, time, etc.)

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid start_date format. Use YYYY-MM-DD",
    "details": {
      "field": "start_date",
      "provided": "2025-13-32",
      "expected": "YYYY-MM-DD"
    }
  }
}
```

**Common Causes:**

1. Invalid date format
   ```bash
   # Wrong
   curl "http://localhost:5000/api/v1/tracking?start_date=11/08/2025"

   # Correct
   curl "http://localhost:5000/api/v1/tracking?start_date=2025-11-08"
   ```

2. Invalid time format
   ```bash
   # Wrong - missing medicine data
   curl -X POST http://localhost:5000/api/v1/medicines

   # Correct
   curl -X POST http://localhost:5000/api/v1/medicines \
     -H "Content-Type: application/json" \
     -d '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}'
   ```

3. Wrong data type
   ```bash
   # Wrong - stock should be number
   curl -X POST http://localhost:5000/api/v1/medicines \
     -H "Content-Type: application/json" \
     -d '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": "one hundred"}'

   # Correct
   curl -X POST http://localhost:5000/api/v1/medicines \
     -H "Content-Type: application/json" \
     -d '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}'
   ```

**Resolution:**
- Check request body and query parameters
- Validate date format (YYYY-MM-DD)
- Validate time format (HH:MM)
- Ensure required fields are present
- Verify data types match expected types

---

### Not Found Errors (404)

#### RESOURCE_NOT_FOUND

**HTTP Status:** 404 Not Found

**Occurs When:**
- Requested resource doesn't exist
- Invalid resource ID

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Medicine not found",
    "details": {
      "medicine_id": "med_invalid_123",
      "type": "medicine"
    }
  }
}
```

**Common Causes:**

1. Invalid medicine ID
   ```bash
   # Wrong - ID doesn't exist
   curl http://localhost:5000/api/v1/medicines/med_invalid

   # First list medicines to get valid ID
   curl http://localhost:5000/api/v1/medicines
   ```

2. Typo in endpoint
   ```bash
   # Wrong
   curl http://localhost:5000/api/v1/medicinesx

   # Correct
   curl http://localhost:5000/api/v1/medicines
   ```

**Resolution:**
- Verify resource exists by listing endpoint
- Check resource ID is correct
- Verify endpoint path spelling
- Ensure you're using correct HTTP method

#### SECTION_NOT_FOUND

**HTTP Status:** 404 Not Found

**Occurs When:**
- Configuration section doesn't exist

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "SECTION_NOT_FOUND",
    "message": "Configuration section not found: invalid_section",
    "details": {
      "section": "invalid_section",
      "available_sections": ["weather", "mbta", "disney", "flights", "medicine"]
    }
  }
}
```

**Valid Sections:**
- weather
- mbta
- disney
- flights
- pomodoro
- forbidden
- medicine
- menu
- system
- display

#### FILE_NOT_FOUND

**HTTP Status:** 500 Internal Server Error (returned as 500)

**Occurs When:**
- Configuration file missing
- Database file missing

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "Configuration file not found",
    "details": {
      "file": "/home/pizero2w/pizero_apps/config.json"
    }
  }
}
```

**Resolution:**
- Check file exists at specified path
- Verify file permissions
- Check environment variables for correct paths

---

### Method Not Allowed (405)

#### METHOD_NOT_ALLOWED

**HTTP Status:** 405 Method Not Allowed

**Occurs When:**
- Unsupported HTTP method used

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "METHOD_NOT_ALLOWED",
    "message": "HTTP method not allowed"
  }
}
```

**Common Causes:**

```bash
# Wrong - GET not supported for creating
curl http://localhost:5000/api/v1/medicines

# Correct
curl -X POST http://localhost:5000/api/v1/medicines

# Wrong - POST not supported for single resource
curl -X POST http://localhost:5000/api/v1/medicines/med_123

# Correct
curl -X PUT http://localhost:5000/api/v1/medicines/med_123
```

**Supported Methods by Endpoint:**

| Endpoint | GET | POST | PUT | PATCH | DELETE |
|----------|-----|------|-----|-------|--------|
| /medicines | X | X | - | - | - |
| /medicines/{id} | X | - | X | X | X |
| /medicines/{id}/take | - | X | - | - | - |
| /medicines/batch-take | - | X | - | - | - |
| /tracking | X | X | - | - | - |
| /tracking/today | X | - | - | - | - |
| /config | X | X | - | - | - |
| /config/{section} | X | - | X | X | - |

---

### Conflict Errors (409)

#### CONFLICT

**HTTP Status:** 409 Conflict

**Occurs When:**
- Creating duplicate resource
- Resource state conflict

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "Medicine with ID already exists",
    "details": {
      "medicine_id": "med_123"
    }
  }
}
```

**Common Causes:**

```bash
# Trying to create medicine with duplicate ID
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"id": "med_existing", "name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}'
```

**Resolution:**
- Don't provide ID for new resources (let server generate)
- Use different ID for duplicate resource
- Check existing resources before creating

---

### Server Errors (500)

#### INTERNAL_ERROR

**HTTP Status:** 500 Internal Server Error

**Occurs When:**
- Unexpected server error
- Uncaught exception

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": "Internal details (debug mode only)"
  }
}
```

#### DATABASE_ERROR

**HTTP Status:** 500 Internal Server Error

**Occurs When:**
- Database connection fails
- Query execution error
- Data integrity error

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to retrieve medicines",
    "details": "database query error (debug mode only)"
  }
}
```

**Common Causes:**

1. Database connection issue
   - Database file missing
   - Database locked
   - Permission denied

2. Invalid data in database
   - Corrupted records
   - Constraint violations

**Resolution:**
- Check database file exists
- Check file permissions: `chmod 666 medicine.db`
- Verify database integrity: `sqlite3 medicine.db ".check"`
- Restart API server
- Check server logs for details

#### INVALID_CONFIG

**HTTP Status:** 500 Internal Server Error

**Occurs When:**
- Configuration file is invalid JSON

**Example:**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CONFIG",
    "message": "Configuration file is invalid",
    "details": "JSON decode error at line 5"
  }
}
```

**Resolution:**
- Validate config.json JSON syntax
- Use a JSON validator tool
- Check for trailing commas
- Ensure all quotes are matched

---

## Common Error Scenarios

### Scenario 1: Creating Medicine with Missing Fields

**Request:**
```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"name": "Aspirin"}'
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required fields",
    "details": {
      "missing_fields": ["dosage", "frequency", "stock"]
    }
  }
}
```

**Solution:**
```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 100
  }'
```

### Scenario 2: Invalid Date Range

**Request:**
```bash
curl "http://localhost:5000/api/v1/tracking?start_date=2025-13-45&end_date=2025-11-08"
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid start_date format. Use YYYY-MM-DD",
    "details": {
      "field": "start_date"
    }
  }
}
```

**Solution:**
```bash
curl "http://localhost:5000/api/v1/tracking?start_date=2025-11-01&end_date=2025-11-08"
```

### Scenario 3: Marking Non-Existent Medicine

**Request:**
```bash
curl -X POST http://localhost:5000/api/v1/medicines/med_does_not_exist/take
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Medicine not found",
    "details": {
      "medicine_id": "med_does_not_exist"
    }
  }
}
```

**Solution:**
```bash
# First, list medicines to find valid ID
curl http://localhost:5000/api/v1/medicines

# Then use a valid ID
curl -X POST http://localhost:5000/api/v1/medicines/med_valid_id/take
```

### Scenario 4: Invalid JSON in Request Body

**Request:**
```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"name": "Aspirin", "dosage": "500mg" invalid json}'
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid request",
    "details": "Failed to parse JSON"
  }
}
```

**Solution:**
```bash
# Validate JSON syntax before sending
echo '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}' | jq .

# Then send valid JSON
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}'
```

### Scenario 5: Database Locked

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to retrieve medicines",
    "details": "database is locked"
  }
}
```

**Solution:**
```bash
# Check what's accessing the database
lsof | grep medicine.db

# Restart API server
# Press Ctrl+C on the running server
# Then restart:
python3 run_api.py

# Or check file locks
fuser medicine.db
```

---

## Error Handling Guide

### Client-Side Error Handling

#### Python

```python
import requests
from requests.exceptions import RequestException

def api_call(method, endpoint, data=None):
    """Make API call with error handling"""
    try:
        url = f"http://localhost:5000/api/v1{endpoint}"
        headers = {"Content-Type": "application/json"}

        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        # Check if request was successful
        if response.status_code >= 400:
            error_data = response.json()
            error_code = error_data['error']['code']
            error_message = error_data['error']['message']

            # Handle specific errors
            if error_code == "VALIDATION_ERROR":
                print(f"Invalid input: {error_message}")
                print(f"Details: {error_data['error'].get('details')}")
                return None

            elif error_code == "RESOURCE_NOT_FOUND":
                print(f"Resource not found: {error_message}")
                return None

            elif error_code == "DATABASE_ERROR":
                print(f"Database error: {error_message}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
                return api_call(method, endpoint, data)

            else:
                print(f"Error {error_code}: {error_message}")
                return None

        return response.json()

    except RequestException as e:
        print(f"Request failed: {e}")
        return None

# Usage
result = api_call("GET", "/medicines")
if result:
    print(f"Found {len(result['data'])} medicines")
```

#### JavaScript

```javascript
async function apiCall(method, endpoint, data = null) {
  try {
    const url = `http://localhost:5000/api/v1${endpoint}`;
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };

    if (data) {
      options.body = JSON.stringify(data);
    }

    const response = await fetch(url, options);
    const result = await response.json();

    if (!response.ok) {
      const errorCode = result.error.code;
      const errorMessage = result.error.message;

      switch (errorCode) {
        case 'VALIDATION_ERROR':
          console.error(`Invalid input: ${errorMessage}`);
          console.error(`Details:`, result.error.details);
          break;
        case 'RESOURCE_NOT_FOUND':
          console.error(`Resource not found: ${errorMessage}`);
          break;
        case 'DATABASE_ERROR':
          console.error(`Database error: ${errorMessage}`);
          // Implement retry logic
          await new Promise(resolve => setTimeout(resolve, 5000));
          return apiCall(method, endpoint, data);
        default:
          console.error(`Error ${errorCode}: ${errorMessage}`);
      }
      return null;
    }

    return result;
  } catch (error) {
    console.error('Request failed:', error);
    return null;
  }
}

// Usage
const result = await apiCall('GET', '/medicines');
if (result) {
  console.log(`Found ${result.data.length} medicines`);
}
```

### Error Logging

```python
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_errors.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_error(error_response, endpoint, method):
    """Log API error for debugging"""
    error_data = error_response.json()

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'method': method,
        'endpoint': endpoint,
        'status_code': error_response.status_code,
        'error_code': error_data['error']['code'],
        'error_message': error_data['error']['message'],
        'details': error_data['error'].get('details')
    }

    logger.error(json.dumps(log_entry, indent=2))
```

---

## Troubleshooting

### API Not Responding

**Symptoms:** Connection refused or timeout

**Diagnosis:**
```bash
# Check if server is running
curl -v http://localhost:5000/api/v1/

# Check if port is open
netstat -tlnp | grep 5000

# Check process
ps aux | grep python
```

**Solution:**
```bash
# Start the server
python3 run_api.py

# Or use a different port
export FLASK_PORT=5001
python3 run_api.py
```

### Database Errors

**Symptoms:** DATABASE_ERROR responses

**Diagnosis:**
```bash
# Check database file
ls -la medicine.db

# Check if database is valid
sqlite3 medicine.db ".schema"

# Check for locks
fuser medicine.db
```

**Solution:**
```bash
# Fix permissions
chmod 666 medicine.db

# Rebuild database if corrupted
sqlite3 medicine.db ".restore backup.db"

# Or start fresh (careful!)
rm medicine.db
python3 run_api.py  # Will recreate empty database
```

### Validation Errors

**Symptoms:** VALIDATION_ERROR for valid data

**Diagnosis:**
- Check exact error message and details
- Review required fields
- Validate data types

**Solution:**
- Use provided error details to fix data
- Check API documentation for requirements
- Test with curl first before integrating

---

## Getting Help

1. Check this error codes reference
2. Review error message and details
3. Check API_REFERENCE.md for endpoint details
4. Enable debug logging: `export FLASK_DEBUG=True`
5. Check server console output
6. Review examples in API_QUICKSTART.md
