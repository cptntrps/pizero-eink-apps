# WEB CONFIGURATION SYSTEM ARCHITECTURE

## System Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER DEVICES                               │
├─────────────────────────────────────────────────────────────────────┤
│ Browser (Chrome, Safari, Firefox)                                   │
│ http://device:5000 (localhost:5000)                                │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     │ HTTP/fetch()
                     │
        ┌────────────▼────────────┐
        │  FLASK WEB SERVER      │
        │  web_config.py         │
        │  Port: 5000            │
        ├────────────────────────┤
        │ Routes (9 endpoints)   │
        │ - GET /                │
        │ - GET /api/config      │
        │ - POST /api/config/*   │
        │ - GET/POST/DELETE      │
        │   /api/medicine/*      │
        └────────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────────┐        ┌─────────────────┐
    │ config.json │        │medicine_data.   │
    │             │        │json             │
    │ - weather   │        │                 │
    │ - mbta      │        │ - medicines     │
    │ - disney    │        │ - tracking      │
    │ - flights   │        │ - time_windows  │
    │ - pomodoro  │        │ - last_updated  │
    │ - forbidden │        │                 │
    │ - system    │        └─────────────────┘
    │ - display   │
    └─────────────┘
         │                       │
         │   File reads/writes   │
         │   (Config: 1 file,    │
         │    Medicine: 1 file)  │
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │ DISPLAY APPS          │
         │ (Pi Zero 2W)          │
         ├───────────────────────┤
         │ - weather_cal_app.py  │
         │ - mbta_app.py         │
         │ - disney_app.py       │
         │ - flights_app.py      │
         │ - pomodoro_app.py     │
         │ - medicine_app.py     │
         │ - forbidden_app.py    │
         │                       │
         │ e-ink Display         │
         │ 2.13" V4              │
         └───────────────────────┘
```

---

## Data Flow: Configuration Update Cycle

```
STEP 1: USER INTERACTION
┌─────────────────────────────────────┐
│ User opens web UI (browser)         │
│ http://localhost:5000/              │
│                                     │
│ JavaScript runs:                    │
│ - DOMContentLoaded event           │
│ - loadConfig() fetches /api/config │
│ - Populates form fields            │
│                                     │
│ User fills Weather form:            │
│ - Location: "Rio de Janeiro"       │
│ - Units: "metric"                  │
│ - Update Interval: 300             │
│ - Display Format: "detailed"       │
│                                     │
│ User clicks "Save Weather Settings"│
└────────────┬────────────────────────┘
             │
STEP 2: WEB FORM SUBMISSION
             │
             ▼
┌─────────────────────────────────────┐
│ JavaScript form submit handler:     │
│                                     │
│ fetch('/api/config/weather', {      │
│   method: 'POST',                   │
│   headers: {                        │
│     'Content-Type':                 │
│       'application/json'            │
│   },                                │
│   body: JSON.stringify({            │
│     location: "Rio de Janeiro",    │
│     units: "metric",               │
│     update_interval: 300,          │
│     display_format: "detailed"     │
│   })                               │
│ })                                 │
│                                     │
│ Response received:                  │
│ {                                   │
│   "success": true,                 │
│   "message": "Weather settings     │
│     saved successfully!"           │
│ }                                   │
│                                     │
│ showStatus() displays success msg  │
│ (auto-dismisses after 3 seconds)   │
└────────────┬────────────────────────┘
             │
STEP 3: SERVER-SIDE PROCESSING
             │
             ▼
┌─────────────────────────────────────┐
│ Flask Route Handler                 │
│ @app.route('/api/config/weather',   │
│   methods=['POST'])                │
│                                     │
│ def update_config('weather'):       │
│                                     │
│ 1. Read config.json from disk       │
│    {"weather": {...},               │
│     "mbta": {...},                 │
│     ...}                           │
│                                     │
│ 2. Parse JSON to Python dict        │
│                                     │
│ 3. Get request body:                │
│    data = request.get_json()        │
│    {location: "Rio...",            │
│     units: "metric",               │
│     ...}                           │
│                                     │
│ 4. Update config dictionary:        │
│    config['weather'] = data         │
│                                     │
│ 5. Write updated config back:       │
│    with open(CONFIG_FILE, 'w'):    │
│      json.dump(config, f,          │
│        indent=2)                   │
│                                     │
│ 6. Return success response          │
│    jsonify({                        │
│      "success": True,              │
│      "message": "..."              │
│    })                              │
└────────────┬────────────────────────┘
             │
STEP 4: FILE SYSTEM UPDATE
             │
             ▼
┌─────────────────────────────────────┐
│ /home/pizero2w/pizero_apps/         │
│ config.json (updated)               │
│                                     │
│ {                                   │
│   "weather": {                      │
│     "location":                     │
│       "Rio de Janeiro", ✓ UPDATED  │
│     "units": "metric", ✓ UPDATED   │
│     "update_interval": 300,         │
│     "display_format":              │
│       "detailed", ✓ UPDATED        │
│     "show_forecast": true          │
│   },                               │
│   "mbta": {...},                   │
│   "disney": {...},                 │
│   ...                              │
│ }                                   │
└────────────┬────────────────────────┘
             │
STEP 5: DISPLAY APP RELOAD
             │
             ▼
┌─────────────────────────────────────┐
│ weather_cal_app.py                  │
│ (running on Pi Zero 2W)             │
│                                     │
│ Periodic update cycle:              │
│ 1. Read config.json (every 300s)   │
│                                     │
│ 2. Parse JSON to Python dict        │
│                                     │
│ 3. Extract weather section:         │
│    weather_config = {              │
│      "location":                    │
│        "Rio de Janeiro", ✓ LOADED  │
│      "units": "metric",            │
│      "update_interval": 300,       │
│      ...                           │
│    }                               │
│                                     │
│ 4. Fetch weather data from API     │
│    using location "Rio de Janeiro" │
│                                     │
│ 5. Render on e-ink display         │
│    with updated location           │
│                                     │
│ 6. Sleep for update_interval (300s)│
│                                     │
│ 7. Repeat                          │
└─────────────────────────────────────┘
```

---

## Data Flow: Medicine Tracking

```
WEB UI MEDICINE MANAGEMENT
┌──────────────────────────────────────┐
│ Medicine Form                        │
│ - Name: "Vitamin D"                 │
│ - Dosage: "2000 IU"                │
│ - Time Window: "morning"            │
│ - Days: [all checked]              │
│ - Pills Remaining: 30               │
│ - Pills Per Dose: 1                │
│ - Low Stock Alert: 10              │
└────────────┬─────────────────────────┘
             │
             ▼ POST /api/medicine/add
┌──────────────────────────────────────┐
│ Flask Handler (add_medicine)         │
│                                      │
│ 1. Read medicine_data.json           │
│                                      │
│ 2. Get request JSON                  │
│                                      │
│ 3. Append to medicines array         │
│                                      │
│ 4. Add timestamp:                    │
│    data['last_updated'] = now        │
│                                      │
│ 5. Write to file                     │
│                                      │
│ 6. Return success                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ medicine_data.json (updated)         │
│                                      │
│ {                                    │
│   "medicines": [                     │
│     {...old medicines...},           │
│     {                                │
│       "id": "med_1234567890",       │
│       "name": "Vitamin D", ✓ NEW    │
│       "dosage": "2000 IU",          │
│       "time_window": "morning",     │
│       "window_start": "06:00",      │
│       "window_end": "12:00",        │
│       "days": [all 7 days],         │
│       "pills_remaining": 30,        │
│       "pills_per_dose": 1,          │
│       "low_stock_threshold": 10,    │
│       "active": true                │
│     }                               │
│   ],                                │
│   "tracking": {...},                │
│   "last_updated":                   │
│     "2025-11-08T10:30:45" ✓ UPDATED│
│ }                                    │
└────────────┬─────────────────────────┘
             │
MEDICINE TAKEN MARKING
             │
             ▼
┌──────────────────────────────────────┐
│ Medicine App Display                 │
│ (medicine_app.py)                    │
│                                      │
│ Shows pending medicines:             │
│ - Vitamin D (morning, 30 pills)     │
│ - [Edit] [Mark Taken]              │
│                                      │
│ User presses button → Mark Taken     │
│                                      │
│ Sends:                               │
│ POST /api/medicine/mark-taken        │
│ {                                    │
│   "medicine_id": "med_1234567890"   │
│ }                                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Flask Handler (mark_taken)           │
│                                      │
│ 1. Read medicine_data.json           │
│                                      │
│ 2. Find medicine by ID               │
│                                      │
│ 3. Update tracking:                  │
│    tracking[today][med_id] = {       │
│      "taken": true,                  │
│      "timestamp": now                │
│    }                                 │
│                                      │
│ 4. Decrement pill count:             │
│    pills = 30 - 1 = 29               │
│    Update medicine object            │
│                                      │
│ 5. Update timestamp:                 │
│    last_updated = now                │
│                                      │
│ 6. Write to file                     │
│                                      │
│ 7. Return response with              │
│    pills_remaining: 29               │
│    low_stock: false                  │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ medicine_data.json (updated)         │
│                                      │
│ {                                    │
│   "medicines": [                     │
│     {                                │
│       "id": "med_1234567890",       │
│       ...                            │
│       "pills_remaining": 29 ✓ UPDATED
│     }                               │
│   ],                                │
│   "tracking": {                      │
│     "2025-11-08": {                 │
│       "med_1234567890_morning": {    │
│         "taken": true, ✓ UPDATED    │
│         "timestamp": "2025-11-08    │
│           T10:35:20"                │
│       }                             │
│     }                               │
│   },                                │
│   "last_updated":                   │
│     "2025-11-08T10:35:20" ✓ UPDATED│
│ }                                    │
└────────────┬─────────────────────────┘
             │
             ▼
┌──────────────────────────────────────┐
│ Push Refresh Mechanism               │
│ (medicine_app.py watches timestamp) │
│                                      │
│ 1. Read medicine_data.json           │
│                                      │
│ 2. Check last_updated timestamp     │
│                                      │
│ 3. If changed from cached value:    │
│    - Reload all medicine data       │
│    - Update e-ink display           │
│    - Show updated pill count        │
│                                      │
│ 4. Cache new timestamp              │
│                                      │
│ 5. Continue monitoring for changes  │
└──────────────────────────────────────┘
```

---

## Web UI Component Hierarchy

```
HTML_TEMPLATE (929 lines)
├── Head
│   ├── Metadata (charset, viewport, title)
│   ├── Embedded CSS (218 lines)
│   │   ├── Global styles
│   │   ├── Sidebar styles (256px fixed width)
│   │   ├── Main content styles
│   │   ├── Form styles
│   │   ├── Card styles
│   │   ├── Status message styles
│   │   └── Responsive grid
│   └── Script tag (inline)
│
├── Body (flex layout)
│   ├── Aside.sidebar
│   │   ├── h1 "Pi Zero 2W"
│   │   └── Nav
│   │       ├── Dashboard button
│   │       ├── Applications button (expandable)
│   │       │   └── Submenu
│   │       │       ├── Weather
│   │       │       ├── MBTA
│   │       │       ├── Disney
│   │       │       ├── Flights
│   │       │       ├── Pomodoro
│   │       │       ├── Medicine
│   │       │       └── Forbidden
│   │       └── Settings button
│   │
│   └── Main.main-content
│       ├── Dashboard Section
│       ├── Weather Section
│       │   └── Form (4 fields)
│       ├── MBTA Section
│       │   └── Form (9 fields)
│       ├── Disney Section
│       │   └── Form (4 fields)
│       ├── Flights Section
│       │   └── Form (3 fields)
│       ├── Pomodoro Section
│       │   └── Form (4 fields)
│       ├── Medicine Section
│       │   ├── Medicine List (dynamic)
│       │   └── Add/Edit Form (8+ fields)
│       ├── Forbidden Section
│       │   └── Form (1 field)
│       └── Settings Section
│
└── JavaScript (360 lines)
    ├── Initialization (DOMContentLoaded)
    ├── Config Loading (loadConfig)
    ├── Navigation
    │   ├── showSection()
    │   └── toggleSubmenu()
    ├── UI Helpers
    │   └── showStatus()
    ├── Form Handlers
    │   ├── Weather form handler
    │   ├── MBTA form handler
    │   ├── Disney form handler
    │   ├── Flights form handler
    │   ├── Pomodoro form handler
    │   └── Forbidden form handler
    └── Medicine Management
        ├── loadMedicineData()
        ├── displayMedicineList()
        ├── showAddMedicineForm()
        ├── editMedicine()
        ├── deleteMedicine()
        ├── cancelMedicineForm()
        └── Medicine form submit handler
```

---

## API Request/Response Flow

```
CLIENT (Browser)
│
├─ loadConfig()
│  ├─ GET /api/config
│  └─ Response: {weather: {...}, mbta: {...}, ...}
│     └─ Populates all form fields
│
├─ Weather Form Submit
│  ├─ POST /api/config/weather
│  │  Body: {location, units, update_interval, display_format}
│  └─ Response: {success: true, message: "..."}
│
├─ MBTA Form Submit
│  ├─ POST /api/config/mbta
│  │  Body: {home_station_id, work_station_id, times...}
│  └─ Response: {success: true, message: "..."}
│
├─ Medicine Management
│  ├─ GET /api/medicine/data
│  │  └─ Response: {medicines: [...], tracking: {...}, ...}
│  │
│  ├─ POST /api/medicine/add
│  │  Body: {id, name, dosage, time_window, days, pills...}
│  │  └─ Response: {success: true, message: "..."}
│  │
│  ├─ POST /api/medicine/update
│  │  Body: {id, name, dosage, ...}
│  │  └─ Response: {success: true, message: "..."}
│  │
│  ├─ DELETE /api/medicine/delete/<id>
│  │  └─ Response: {success: true, message: "..."}
│  │
│  ├─ POST /api/medicine/mark-taken
│  │  Body: {medicine_id(s), timestamp}
│  │  └─ Response: {success: true, marked: [...], timestamp: "..."}
│  │
│  └─ GET /api/medicine/pending
│     Query: ?date=...&time=...
│     └─ Response: {success: true, count: N, medicines: [...]}

SERVER (Flask)
│
├─ Route handlers process requests
├─ Read/write JSON files
├─ Return JSON responses
└─ No authentication/validation ⚠️
```

---

## File Organization

```
/home/pizero2w/pizero_apps/
│
├── web_config.py                (54 KB)
│   └── Flask app with embedded HTML/CSS/JS
│
├── config.json                   (3 KB)
│   ├── weather config
│   ├── mbta config
│   ├── disney config
│   ├── flights config
│   ├── pomodoro config
│   ├── forbidden config
│   ├── medicine config
│   ├── menu config
│   ├── system config
│   └── display config
│
├── medicine_data.json            (4 KB)
│   ├── medicines array
│   ├── tracking history
│   ├── time windows
│   └── last_updated timestamp
│
├── weather_cal_app.py
├── mbta_app.py
├── disney_app.py
├── flights_app.py
├── pomodoro_app.py
├── medicine_app.py
├── forbidden_app.py
└── menu_simple.py
    (All read config.json periodically)
```

---

## Synchronization Mechanism

### Config Updates → Display Apps

1. User submits form → POST /api/config/[section]
2. Flask updates config.json
3. Display apps read config periodically (every N seconds)
4. Apps apply new settings
5. e-ink display updates

**Latency:** Update_interval seconds (varies by app)

### Medicine Tracking → Display

1. User marks medicine taken → POST /api/medicine/mark-taken
2. Flask updates medicine_data.json + last_updated timestamp
3. medicine_app.py monitors last_updated
4. On change detected: reloads medicine_data.json
5. Updates e-ink display with new pill count

**Latency:** <1 second (push refresh)

### Web UI ↔ Config

**No real-time sync currently**
- Manual refresh needed for external changes
- No polling mechanism
- No WebSocket connection
- Status messages only confirm submission

---

## Security Perimeter

```
TRUSTED ZONE (Local Network)
┌──────────────────────────────────────┐
│ Pi Zero 2W Device (192.168.50.202)  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Flask Web Server (Port 5000)   │  │
│ │ - No authentication ⚠️         │  │
│ │ - No input validation ⚠️       │  │
│ │ - No TLS/HTTPS ⚠️             │  │
│ │ - No rate limiting ⚠️         │  │
│ └────────────────────────────────┘  │
│                                      │
│ ┌────────────────────────────────┐  │
│ │ Config/Medicine JSON Files     │  │
│ │ - World-readable (likely) ⚠️   │  │
│ │ - No backup ⚠️                 │  │
│ │ - No encryption ⚠️             │  │
│ └────────────────────────────────┘  │
└──────────────────────────────────────┘
        ▲              │
        │              │ Should only allow
        │              │ local network access
        │              ▼
    Browser  (localhost or 192.168.x.x)
    (Same network)
```

**RISK:** If device exposed to internet, all configuration can be accessed/modified.

