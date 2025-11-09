# Pi Zero 2W Medicine Tracker API - Quick Start Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation & Setup](#installation--setup)
3. [Starting the API Server](#starting-the-api-server)
4. [Basic API Usage](#basic-api-usage)
5. [Common Use Cases](#common-use-cases)
6. [Testing the API](#testing-the-api)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

Welcome to the Pi Zero 2W Medicine Tracker API! This guide will help you get up and running with the API in just a few minutes.

### Prerequisites

- Python 3.7+ installed
- pip (Python package manager)
- Basic knowledge of REST APIs and HTTP
- cURL or a tool like Postman (optional)

### What You'll Learn

- How to start the API server
- How to make basic API requests
- How to manage medicines
- How to track medicine adherence
- How to access and modify configuration

---

## Installation & Setup

### 1. Clone or Navigate to Project

```bash
cd /home/user/pizerowgpio
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key Dependencies:**
- Flask: Web framework
- Flask-CORS: Cross-origin resource sharing
- Marshmallow: Data validation (optional)

### 3. Verify Installation

```bash
python3 -c "import flask; print(flask.__version__)"
```

---

## Starting the API Server

### Development Server

```bash
# From project root directory
python3 run_api.py
```

You should see output like:

```
Starting Flask API server on 0.0.0.0:5000
Debug mode: True
API Version: v1
Base URL: http://0.0.0.0:5000/api/v1
```

### Production Server

```bash
# Set environment variables
export FLASK_ENV=production
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export SECRET_KEY=your-secret-key-here

# Run the server
python3 run_api.py
```

### Configuration Options

**Environment Variables:**

```bash
# Server configuration
FLASK_HOST=0.0.0.0          # Listen on all interfaces
FLASK_PORT=5000              # Port to listen on
FLASK_DEBUG=True             # Enable debug mode
FLASK_ENV=development        # Environment (development/production/testing)

# Database
PIZERO_MEDICINE_DB=/path/to/medicine.db
PIZERO_CONFIG_FILE=/path/to/config.json

# Security
SECRET_KEY=your-secret-key-here
```

### Verify Server is Running

Open a new terminal and test:

```bash
curl http://localhost:5000/api/v1/
```

Expected response:

```json
{
  "success": true,
  "data": {
    "version": "1.0",
    "name": "Pi Zero 2W Medicine Tracker API",
    "endpoints": {
      "medicines": "/api/v1/medicines",
      "tracking": "/api/v1/tracking",
      "config": "/api/v1/config",
      "health": "/api/v1/health"
    }
  }
}
```

---

## Basic API Usage

### Check API Health

```bash
curl http://localhost:5000/api/v1/health
```

Response shows API and database status:

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "database": "connected"
  }
}
```

### Create Your First Medicine

```bash
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 100,
    "low_stock_threshold": 20
  }'
```

Response (note the ID for later use):

```json
{
  "success": true,
  "data": {
    "id": "med_1699457400000",
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 100,
    "low_stock_threshold": 20,
    "active": true,
    "created_at": "2025-11-08T15:30:00",
    "updated_at": "2025-11-08T15:30:00"
  }
}
```

### List All Medicines

```bash
curl http://localhost:5000/api/v1/medicines
```

### Get a Specific Medicine

```bash
# Replace with your medicine ID
curl http://localhost:5000/api/v1/medicines/med_1699457400000
```

### Mark Medicine as Taken

```bash
curl -X POST http://localhost:5000/api/v1/medicines/med_1699457400000/take \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:

```json
{
  "success": true,
  "data": {
    "medicine_id": "med_1699457400000",
    "medicine_name": "Aspirin",
    "pills_remaining": 99,
    "low_stock": false,
    "taken_at": "2025-11-08T15:30:00"
  }
}
```

### Get Today's Statistics

```bash
curl http://localhost:5000/api/v1/tracking/today
```

Response:

```json
{
  "success": true,
  "data": {
    "date": "2025-11-08",
    "total_medicines": 5,
    "medicines_taken": 4,
    "medicines_pending": 1,
    "adherence_rate": 0.8
  }
}
```

---

## Common Use Cases

### Use Case 1: Daily Medicine Management

**Morning - Check what needs to be taken:**

```bash
curl "http://localhost:5000/api/v1/medicines/pending?time=08:00"
```

**Mark medicines as taken:**

```bash
curl -X POST http://localhost:5000/api/v1/medicines/batch-take \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_ids": ["med_123", "med_456"],
    "timestamp": "2025-11-08T08:30:00"
  }'
```

**Evening - Check adherence:**

```bash
curl http://localhost:5000/api/v1/tracking/today
```

### Use Case 2: Medication Refill Monitoring

**Check low stock medicines:**

```bash
curl http://localhost:5000/api/v1/medicines/low-stock
```

**Update stock after refill:**

```bash
curl -X PATCH http://localhost:5000/api/v1/medicines/med_123 \
  -H "Content-Type: application/json" \
  -d '{"stock": 120}'
```

### Use Case 3: Weekly Adherence Report

**Get adherence statistics for the past week:**

```bash
curl "http://localhost:5000/api/v1/tracking/stats?start_date=2025-11-01&end_date=2025-11-08"
```

### Use Case 4: Medication History

**Get tracking records for a specific medicine:**

```bash
curl "http://localhost:5000/api/v1/medicines/med_123/tracking?start_date=2025-11-01&end_date=2025-11-08"
```

### Use Case 5: Configure Medicine Times

**Update medicine with specific times:**

```bash
curl -X PUT http://localhost:5000/api/v1/medicines/med_123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Metformin",
    "dosage": "1000mg",
    "frequency": "Twice daily",
    "stock": 60,
    "time_windows": [
      {"hour": 8, "minute": 0},
      {"hour": 20, "minute": 0}
    ]
  }'
```

---

## Testing the API

### Using cURL (Command Line)

cURL is built-in on most systems:

```bash
# Test GET
curl http://localhost:5000/api/v1/medicines

# Test POST with data
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "dosage": "100mg", "frequency": "Daily", "stock": 50}'

# Test with headers
curl -H "Accept: application/json" http://localhost:5000/api/v1/medicines
```

### Using Postman (GUI)

1. Download [Postman](https://www.postman.com/downloads/)
2. Import the OpenAPI specification:
   - File → Import → Select `docs/openapi.yaml`
3. Set base URL: `http://localhost:5000/api/v1`
4. Create requests in the collection

### Using Python

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:5000/api/v1"

# 1. Check health
response = requests.get(f"{BASE_URL}/health")
print("Health:", response.json())

# 2. Create medicine
medicine = {
    "name": "Aspirin",
    "dosage": "500mg",
    "frequency": "Twice daily",
    "stock": 100,
    "low_stock_threshold": 20
}
response = requests.post(f"{BASE_URL}/medicines", json=medicine)
medicine_data = response.json()
medicine_id = medicine_data['data']['id']
print(f"Created medicine: {medicine_id}")

# 3. Get medicine
response = requests.get(f"{BASE_URL}/medicines/{medicine_id}")
print("Medicine:", response.json())

# 4. Mark as taken
response = requests.post(f"{BASE_URL}/medicines/{medicine_id}/take")
print("Marked taken:", response.json())

# 5. Get today's stats
response = requests.get(f"{BASE_URL}/tracking/today")
print("Today's stats:", response.json())

# 6. Update medicine
response = requests.patch(
    f"{BASE_URL}/medicines/{medicine_id}",
    json={"stock": 90}
)
print("Updated:", response.json())

# 7. Delete medicine
response = requests.delete(f"{BASE_URL}/medicines/{medicine_id}")
print("Status code:", response.status_code)
```

### Using JavaScript/Node.js

```javascript
const BASE_URL = "http://localhost:5000/api/v1";

// 1. Check health
fetch(`${BASE_URL}/health`)
  .then(res => res.json())
  .then(data => console.log("Health:", data));

// 2. Create medicine
const medicine = {
  name: "Aspirin",
  dosage: "500mg",
  frequency: "Twice daily",
  stock: 100,
  low_stock_threshold: 20
};

fetch(`${BASE_URL}/medicines`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(medicine)
})
.then(res => res.json())
.then(data => {
  const medicineId = data.data.id;
  console.log("Created medicine:", medicineId);

  // 3. Get medicine
  return fetch(`${BASE_URL}/medicines/${medicineId}`);
})
.then(res => res.json())
.then(data => console.log("Medicine:", data));

// 4. Mark as taken
async function markTaken(medicineId) {
  const response = await fetch(
    `${BASE_URL}/medicines/${medicineId}/take`,
    { method: "POST" }
  );
  return response.json();
}

// 5. Get today's stats
async function getTodayStats() {
  const response = await fetch(`${BASE_URL}/tracking/today`);
  return response.json();
}
```

### Test Scripts

**Bash script to test main endpoints:**

```bash
#!/bin/bash

BASE_URL="http://localhost:5000/api/v1"

echo "1. Testing Health Check"
curl -s $BASE_URL/health | jq .

echo -e "\n2. Testing List Medicines"
curl -s $BASE_URL/medicines | jq .

echo -e "\n3. Testing Create Medicine"
MED_RESPONSE=$(curl -s -X POST $BASE_URL/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Medicine",
    "dosage": "100mg",
    "frequency": "Daily",
    "stock": 50
  }')

MED_ID=$(echo $MED_RESPONSE | jq -r '.data.id')
echo "Created medicine: $MED_ID"
echo $MED_RESPONSE | jq .

echo -e "\n4. Testing Get Medicine"
curl -s $BASE_URL/medicines/$MED_ID | jq .

echo -e "\n5. Testing Mark as Taken"
curl -s -X POST $BASE_URL/medicines/$MED_ID/take | jq .

echo -e "\n6. Testing Today's Stats"
curl -s $BASE_URL/tracking/today | jq .

echo -e "\n7. Testing Delete Medicine"
curl -s -X DELETE $BASE_URL/medicines/$MED_ID

echo -e "\nTest complete!"
```

---

## Troubleshooting

### Issue: "Connection refused" error

**Cause:** API server is not running

**Solution:**
```bash
# Start the server
python3 run_api.py

# Verify it's running
curl http://localhost:5000/api/v1/
```

### Issue: "404 Not Found"

**Cause:** Invalid endpoint or resource ID

**Solutions:**
1. Check endpoint path spelling
2. Verify resource ID exists:
   ```bash
   curl http://localhost:5000/api/v1/medicines
   ```
3. Check OpenAPI documentation for correct endpoints

### Issue: "400 Bad Request"

**Cause:** Invalid request data

**Solutions:**
1. Validate JSON syntax:
   ```bash
   echo '{"name": "Aspirin", "dosage": "500mg", "frequency": "Daily", "stock": 100}' | jq .
   ```
2. Ensure required fields are included
3. Check date format is YYYY-MM-DD
4. Verify time format is HH:MM

### Issue: "500 Internal Server Error"

**Cause:** Server or database error

**Solutions:**
1. Check server logs:
   ```bash
   # Look at console output from python3 run_api.py
   ```
2. Verify database file exists:
   ```bash
   ls -la medicine.db
   ```
3. Check file permissions
4. Restart the API server:
   ```bash
   # Press Ctrl+C in the server terminal
   python3 run_api.py
   ```

### Issue: Port already in use

**Cause:** Something else is using port 5000

**Solutions:**
```bash
# Use a different port
export FLASK_PORT=5001
python3 run_api.py

# Or kill the process using port 5000
lsof -ti:5000 | xargs kill -9
```

### Issue: Database locked or inaccessible

**Cause:** Permission issues or database corruption

**Solutions:**
```bash
# Check permissions
ls -la medicine.db

# Fix permissions (if needed)
chmod 666 medicine.db

# Check if database is valid
sqlite3 medicine.db ".tables"
```

---

## Next Steps

1. **Read the complete API reference:**
   - See [API_REFERENCE.md](./API_REFERENCE.md)

2. **Review the OpenAPI specification:**
   - See [openapi.yaml](./openapi.yaml)
   - Use with tools like Swagger UI or Postman

3. **Explore advanced features:**
   - Batch operations for marking multiple medicines
   - Adherence statistics and reporting
   - Configuration management

4. **Integrate with your application:**
   - Use the API from your frontend
   - Build custom workflows
   - Create dashboards and reports

5. **Deploy to production:**
   - Use proper SECRET_KEY
   - Enable HTTPS/SSL
   - Set up proper logging
   - Configure database backups

---

## API Endpoints Quick Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/medicines` | List medicines |
| POST | `/medicines` | Create medicine |
| GET | `/medicines/{id}` | Get medicine |
| PUT | `/medicines/{id}` | Update medicine |
| PATCH | `/medicines/{id}` | Partial update |
| DELETE | `/medicines/{id}` | Delete medicine |
| GET | `/medicines/pending` | Pending medicines |
| GET | `/medicines/low-stock` | Low stock medicines |
| POST | `/medicines/{id}/take` | Mark taken |
| POST | `/medicines/batch-take` | Batch mark taken |
| GET | `/medicines/{id}/tracking` | Medicine history |
| GET | `/tracking` | All tracking |
| POST | `/tracking` | Batch mark taken |
| GET | `/tracking/today` | Today's stats |
| GET | `/tracking/stats` | Adherence stats |
| GET | `/config` | Get config |
| PUT | `/config` | Update config |
| GET | `/config/{section}` | Get section |
| PUT | `/config/{section}` | Update section |
| PATCH | `/config/{section}` | Partial update |

---

## Getting Help

- Check the [API Reference](./API_REFERENCE.md) for detailed endpoint documentation
- Review the [OpenAPI Specification](./openapi.yaml) for schema details
- Check the [Architecture Documentation](./API_DESIGN.md) for design decisions
- Enable debug logging for troubleshooting
- Check server console output for error messages

---

## Sample Workflow

Here's a typical daily workflow:

```bash
# 1. Start your day - check pending medicines
curl "http://localhost:5000/api/v1/medicines/pending"

# 2. Mark morning medicines as taken
curl -X POST http://localhost:5000/api/v1/medicines/batch-take \
  -H "Content-Type: application/json" \
  -d '{"medicine_ids": ["med_1", "med_2"]}'

# 3. During day - check low stock
curl http://localhost:5000/api/v1/medicines/low-stock

# 4. Evening - mark evening medicines as taken
curl -X POST http://localhost:5000/api/v1/medicines/batch-take \
  -H "Content-Type: application/json" \
  -d '{"medicine_ids": ["med_3"]}'

# 5. Before bed - check today's adherence
curl http://localhost:5000/api/v1/tracking/today

# 6. Weekly - get adherence report
curl "http://localhost:5000/api/v1/tracking/stats?start_date=2025-11-01&end_date=2025-11-08"
```

Happy tracking!
