# WebUI Migration Guide - Quick Reference

**Phase 4 - Agent 4.1**: WebUI Backend Redesign
**Date**: 2025-11-08

---

## What Changed?

The WebUI backend (`web_config.py`) was redesigned from a monolithic file handler to a clean API proxy/gateway.

### Old Architecture ❌
```
Browser → WebUI (port 5000) → Direct file access (medicine_data.json)
```

### New Architecture ✅
```
Browser → WebUI (port 5000) → Proxy → Main API (port 8000) → SQLite Database
```

---

## For Frontend Developers

### Medicine API Endpoints - CHANGED

**OLD (Deprecated)** ❌
```javascript
// These no longer work!
fetch('/api/medicine/data')
fetch('/api/medicine/add', { method: 'POST', ... })
fetch('/api/medicine/update', { method: 'POST', ... })
fetch('/api/medicine/delete/med_123', { method: 'DELETE' })
fetch('/api/medicine/mark-taken', { method: 'POST', ... })
fetch('/api/medicine/pending')
```

**NEW (Use These)** ✅
```javascript
// Get all medicines
fetch('/api/v1/medicines')

// Create medicine
fetch('/api/v1/medicines', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Aspirin', dosage: '500mg', ... })
})

// Update medicine
fetch('/api/v1/medicines/med_123', {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'Aspirin', dosage: '500mg', ... })
})

// Delete medicine
fetch('/api/v1/medicines/med_123', { method: 'DELETE' })

// Mark medicine taken
fetch('/api/v1/medicines/med_123/take', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ timestamp: '2025-11-08T08:30:00' })
})

// Get pending medicines
fetch('/api/v1/medicines/pending')
```

### New Features Available ✨

```javascript
// Get low stock medicines
fetch('/api/v1/medicines/low-stock')

// Batch mark medicines as taken
fetch('/api/v1/medicines/batch-take', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    medicine_ids: ['med_123', 'med_456'],
    timestamp: '2025-11-08T08:30:00'
  })
})

// Skip a medicine
fetch('/api/v1/tracking/skip', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    medicine_id: 'med_123',
    skip_reason: 'Forgot',
    skip_date: '2025-11-08'
  })
})

// Get skip history
fetch('/api/v1/tracking/skip-history?start_date=2025-11-01')

// Get adherence statistics
fetch('/api/v1/tracking/stats?start_date=2025-11-01&end_date=2025-11-08')

// Get today's stats
fetch('/api/v1/tracking/today')
```

### Configuration API - NO CHANGE

Configuration endpoints remain the same:

```javascript
// Get all config
fetch('/api/config')

// Get specific section
fetch('/api/config/disney')
fetch('/api/config/flights')
fetch('/api/config/forbidden')
fetch('/api/config/system')

// Update config section
fetch('/api/config/disney', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ park_id: 6, ... })
})
```

**Note**: `weather`, `mbta`, and `pomodoro` sections are no longer valid!

---

## For Backend Developers

### Starting Services

```bash
# Start in this order:

# 1. Main API (port 8000)
cd /home/user/pizerowgpio
python3 api/main.py

# 2. WebUI (port 5000) - in another terminal
python3 web_config.py
```

### Dependencies

```bash
# Install dependencies
pip3 install -r requirements.txt

# Key new dependencies:
# - requests>=2.31.0
# - Flask-CORS>=4.0.0 (already present)
```

### Configuration

Edit `/home/user/pizerowgpio/web_config.py`:

```python
# Main API URL (default: http://localhost:8000/api/v1)
MAIN_API_URL = "http://localhost:8000/api/v1"

# Valid config sections (deleted apps removed)
VALID_CONFIG_SECTIONS = [
    'disney', 'flights', 'forbidden',
    'system', 'display', 'menu', 'medicine'
]
```

### Health Check

```bash
# Check WebUI health
curl http://localhost:5000/health

# Response:
{
  "status": "healthy",
  "service": "web-config",
  "port": 5000,
  "main_api": {
    "url": "http://localhost:8000/api/v1",
    "healthy": true
  }
}
```

---

## Deleted Apps

These apps were removed in Phase 4:

| App | Config Section | Status |
|-----|----------------|--------|
| Weather | `weather` | ❌ DELETED |
| MBTA | `mbta` | ❌ DELETED |
| Pomodoro | `pomodoro` | ❌ DELETED |

**Attempting to access these will return a 400 error**:

```bash
curl http://localhost:5000/api/config/weather
# Response: {"error": "Invalid configuration section: weather", ...}
```

---

## Testing

### Manual Testing

```bash
# 1. Health check
curl http://localhost:5000/health

# 2. Get medicines (via proxy)
curl http://localhost:5000/api/v1/medicines

# 3. Get config
curl http://localhost:5000/api/config/disney

# 4. Create medicine (via proxy)
curl -X POST http://localhost:5000/api/v1/medicines \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Medicine",
    "dosage": "100mg",
    "time_window": "morning",
    "active": true
  }'

# 5. Mark medicine taken (via proxy)
curl -X POST http://localhost:5000/api/v1/medicines/med_123/take \
  -H "Content-Type: application/json" \
  -d '{"timestamp": "2025-11-08T08:30:00"}'
```

### Verification Script

```bash
# Run verification script
./verify_webui_redesign.sh
```

---

## Error Handling

### Common Errors

1. **Main API not running** (503):
```json
{
  "error": "Main API not available",
  "message": "The main REST API is not running. Please start it on port 8000."
}
```
**Solution**: Start the main API: `python3 api/main.py`

2. **Invalid config section** (400):
```json
{
  "error": "Invalid configuration section: weather",
  "valid_sections": ["disney", "flights", ...]
}
```
**Solution**: Use a valid section (not weather/mbta/pomodoro)

3. **Request timeout** (504):
```json
{
  "error": "Request timeout",
  "message": "The main API took too long to respond."
}
```
**Solution**: Check main API performance, increase timeout in web_config.py

---

## Architecture Diagram

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ HTTP (port 5000)
       ▼
┌───────────────────────────────┐
│   web_config.py (WebUI)       │
│                               │
│  ┌─────────────────────────┐  │
│  │ Config Endpoints        │  │
│  │ /api/config             │  │
│  │ /api/config/<section>   │  │
│  └─────────────────────────┘  │
│                               │
│  ┌─────────────────────────┐  │
│  │ Proxy Endpoint          │  │
│  │ /api/v1/*               │  │
│  └──────────┬──────────────┘  │
└─────────────┼─────────────────┘
              │
              │ HTTP Proxy (port 8000)
              ▼
┌───────────────────────────────┐
│   api/main.py (Main API)      │
│                               │
│  ┌─────────────────────────┐  │
│  │ api/v1/routes/          │  │
│  │ - medicines.py          │  │
│  │ - tracking.py           │  │
│  │ - config.py             │  │
│  └──────────┬──────────────┘  │
│             │                 │
│             ▼                 │
│  ┌─────────────────────────┐  │
│  │ MedicineDatabase        │  │
│  │ (SQLite)                │  │
│  └─────────────────────────┘  │
└───────────────────────────────┘
```

---

## Summary of Changes

| Component | Before | After | Change |
|-----------|--------|-------|--------|
| WebUI endpoints | 11 | 6 | -5 |
| Medicine endpoints | 6 (direct) | 0 (proxied) | -6 |
| Proxy endpoints | 0 | 1 | +1 |
| Code size | 368 lines | 306 lines | -17% |
| Config sections | 10 | 7 | -3 (deleted apps) |
| Data storage | JSON files | SQLite (via API) | ✅ |

---

## Need Help?

- **Full Report**: `cat PHASE4_AGENT4.1_REPORT.md`
- **Verification**: `./verify_webui_redesign.sh`
- **API Docs**: See `api/v1/routes/*.py` for endpoint documentation

---

**Last Updated**: 2025-11-08
**Phase**: 4 - Agent 4.1
**Status**: ✅ COMPLETED
