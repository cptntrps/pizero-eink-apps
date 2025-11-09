# API ENDPOINT QUICK REFERENCE

## Base Configuration
- **Base URL:** `http://localhost:5000`
- **Framework:** Flask
- **Response Format:** JSON
- **Authentication:** None (Security Issue)

---

## ENDPOINT SUMMARY TABLE

| # | Method | Endpoint | Purpose | Status Code | Auth |
|----|--------|----------|---------|------------|------|
| 1 | GET | `/` | Serve web dashboard | 200 | No |
| 2 | GET | `/api/config` | Get all config | 200/500 | No |
| 3 | POST | `/api/config/<section>` | Update config section | 200/500 | No |
| 4 | GET | `/api/medicine/data` | Get medicine data | 200 | No |
| 5 | POST | `/api/medicine/add` | Add medicine | 200/500 | No |
| 6 | POST | `/api/medicine/update` | Update medicine | 200/404/500 | No |
| 7 | DELETE | `/api/medicine/delete/<id>` | Delete medicine | 200/404/500 | No |
| 8 | POST | `/api/medicine/mark-taken` | Mark medicine taken | 200/400/404/500 | No |
| 9 | GET | `/api/medicine/pending` | Get due medicines | 200/500 | No |

---

## CONFIGURATION SECTIONS

### 1. Weather
```
POST /api/config/weather
{
  "location": "string",
  "units": "metric" | "imperial",
  "update_interval": number,
  "display_format": "detailed" | "simple"
}
```

### 2. MBTA Transit
```
POST /api/config/mbta
{
  "home_station_id": "string",
  "home_station_name": "string",
  "work_station_id": "string",
  "work_station_name": "string",
  "update_interval": number,
  "morning_start": "HH:MM",
  "morning_end": "HH:MM",
  "evening_start": "HH:MM",
  "evening_end": "HH:MM"
}
```

### 3. Disney Parks
```
POST /api/config/disney
{
  "park_id": 6 | 5 | 7 | 8,
  "update_interval": number,
  "data_refresh_rides": number,
  "sort_by": "wait_time" | "name"
}
```

### 4. Flights Above
```
POST /api/config/flights
{
  "lat": "number",
  "lon": "number",
  "altitude": number
}
```

### 5. Pomodoro Timer
```
POST /api/config/pomodoro
{
  "work_duration": number,
  "short_break": number,
  "long_break": number,
  "sessions_until_long_break": number
}
```

### 6. Forbidden Message
```
POST /api/config/forbidden
{
  "message": "string"
}
```

---

## MEDICINE ENDPOINTS

### Get All Medicine Data
```
GET /api/medicine/data

Response:
{
  "medicines": [...],
  "tracking": {...},
  "time_windows": {...},
  "last_updated": "ISO-8601"
}
```

### Add Medicine
```
POST /api/medicine/add
{
  "id": "med_" + timestamp,
  "name": "string (required)",
  "dosage": "string (required)",
  "time_window": "morning|afternoon|evening|night",
  "with_food": boolean,
  "days": ["mon", "tue", ...],
  "notes": "string",
  "pills_remaining": number,
  "pills_per_dose": number,
  "low_stock_threshold": number,
  "window_start": "HH:MM",
  "window_end": "HH:MM",
  "active": true
}
```

### Update Medicine
```
POST /api/medicine/update
{
  "id": "existing_id",
  ... (same fields as add)
}
```

### Delete Medicine
```
DELETE /api/medicine/delete/med_1762606811268

Response:
{
  "success": true,
  "message": "Medicine deleted successfully!"
}
```

### Mark Medicine as Taken
```
POST /api/medicine/mark-taken
{
  "medicine_ids": ["med_001", "med_002"],
  "timestamp": "2025-11-08T08:30:00" (optional)
}

OR

{
  "medicine_id": "med_001"
}

Response:
{
  "success": true,
  "marked": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "pills_remaining": 57,
      "low_stock": false
    }
  ],
  "timestamp": "2025-11-08T08:30:00"
}
```

### Get Pending Medicines (Due Now)
```
GET /api/medicine/pending
GET /api/medicine/pending?date=2025-11-08&time=08:30

Response:
{
  "success": true,
  "count": 2,
  "medicines": [...],
  "checked_at": "2025-11-08T08:30:00"
}
```

---

## RESPONSE CODES SUMMARY

| Code | Meaning | Conditions |
|------|---------|-----------|
| 200 | Success | All successful responses |
| 400 | Bad Request | Missing required fields, invalid format |
| 404 | Not Found | Medicine ID doesn't exist |
| 500 | Server Error | File read/write error, exception |

---

## EXAMPLE CURL COMMANDS

### Get Config
```bash
curl http://localhost:5000/api/config
```

### Update Weather Config
```bash
curl -X POST http://localhost:5000/api/config/weather \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Boston",
    "units": "imperial",
    "update_interval": 300,
    "display_format": "simple"
  }'
```

### Add Medicine
```bash
curl -X POST http://localhost:5000/api/medicine/add \
  -H "Content-Type: application/json" \
  -d '{
    "id": "med_1234567890",
    "name": "Vitamin D",
    "dosage": "2000 IU",
    "time_window": "morning",
    "with_food": true,
    "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    "pills_remaining": 30,
    "pills_per_dose": 1,
    "low_stock_threshold": 10,
    "window_start": "06:00",
    "window_end": "12:00",
    "active": true
  }'
```

### Mark Medicine Taken
```bash
curl -X POST http://localhost:5000/api/medicine/mark-taken \
  -H "Content-Type: application/json" \
  -d '{
    "medicine_ids": ["med_001", "med_002"],
    "timestamp": "2025-11-08T08:30:00"
  }'
```

### Delete Medicine
```bash
curl -X DELETE http://localhost:5000/api/medicine/delete/med_1762606811268
```

### Get Pending Medicines
```bash
curl "http://localhost:5000/api/medicine/pending?date=2025-11-08&time=08:30"
```

---

## DATA FILES

- **Config:** `/home/pizero2w/pizero_apps/config.json`
- **Medicine:** `/home/pizero2w/pizero_apps/medicine_data.json`

---

## SECURITY STATUS

❌ CRITICAL ISSUES (Fix Before Production)
- No authentication
- No input validation
- XSS vulnerabilities
- No CSRF protection
- Exception details exposed

⚠️ MEDIUM ISSUES
- No HTTPS/TLS
- No rate limiting
- No audit logging
- No atomic writes

✓ LOW ISSUES
- Content-Type not validated
- No file backup

