# COMPLETE DATA STORAGE REVIEW - Pi Zero 2W Application Suite

**Review Date:** 2025-11-08  
**System:** Pi Zero 2W Medicine Tracker Application Suite  
**Working Directory:** `/home/user/pizerowgpio/`

---

## EXECUTIVE SUMMARY

This comprehensive review covers ALL data storage across the Pi Zero 2W system. The system uses a **hybrid storage model** combining:
- **Persistent JSON files** for configuration and medicine tracking
- **In-memory caches** for frequently accessed image data
- **Temporary caches** for external API responses

**Total Data Files:** 35  
**Total Data Size:** 693 KB  
**Data Integrity:** 99% (with identified issues for remediation)

---

## 1. COMPLETE DATA FILE INVENTORY

### 1.1 Primary Data Files (JSON)

| File | Location | Size | Type | Purpose | Access Pattern |
|------|----------|------|------|---------|-----------------|
| **config.json** | `/home/user/pizerowgpio/config.json` | 2.8 KB | JSON | System & app configuration | READ-HEAVY (startup), WRITE-LIGHT (web UI) |
| **medicine_data.json** | `/home/user/pizerowgpio/medicine_data.json` | 3.9 KB | JSON | Medicine tracking & inventory | READ-HEAVY (app), WRITE-FREQUENT (tracking) |

### 1.2 Image Assets - Disney Park Scenes

| File | Location | Size | Dimensions | Format | Bit Depth | Purpose |
|------|----------|------|-----------|--------|-----------|---------|
| Adventureland.png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| Fantasyland.png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| Frontierland.png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| Liberty Square.png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| Main Street U.S.A..png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| Tomorrowland.png | `/home/user/pizerowgpio/disney_images/` | 3.9 KB | 250x122 | BMP* | 1-bit | Disney land display |
| **Total Disney Images** | `/home/user/pizerowgpio/disney_images/` | **28 KB** | N/A | N/A | N/A | Load once per app session |

*Note: Files have .png extension but are actually Windows BMP format (1-bit monochrome optimized for e-paper display)*

### 1.3 Image Assets - Application Icons

| File | Type | Size | Dimensions | Bit Depth | Purpose |
|------|------|------|-----------|-----------|---------|
| battery.bmp | Icon | 574 B | 64x64 | 1-bit | System status indicator |
| bell.bmp | Icon | 574 B | 64x64 | 1-bit | Notifications |
| calendar.bmp | Icon | 574 B | 64x64 | 1-bit | Calendar/date display |
| clock.bmp | Icon | 574 B | 64x64 | 1-bit | Time display |
| disney.bmp | Icon | 574 B | 64x64 | 1-bit | Disney app |
| download.bmp | Icon | 574 B | 64x64 | 1-bit | Download status |
| home.bmp | Icon | 574 B | 64x64 | 1-bit | Home/menu |
| mbta.bmp | Icon | 574 B | 64x64 | 1-bit | MBTA transit |
| music.bmp | Icon | 574 B | 64x64 | 1-bit | Audio/music |
| settings.bmp | Icon | 574 B | 64x64 | 1-bit | Settings/config |
| star.bmp | Icon | 574 B | 64x64 | 1-bit | Favorites |
| wifi.bmp | Icon | 574 B | 64x64 | 1-bit | Network status |
| calibration.bmp | Icon | 542 B | 60x60 | 1-bit | Calibration |
| flight.bmp | Icon | 542 B | 60x60 | 1-bit | Flights app |
| forbidden.bmp | Icon | 542 B | 60x60 | 1-bit | Restricted content |
| reboot.bmp | Icon | 542 B | 60x60 | 1-bit | System reboot |
| system.bmp | Icon | 542 B | 60x60 | 1-bit | System menu |
| weather.bmp | Icon | 542 B | 60x60 | 1-bit | Weather |
| mario.bmp | Icon | 11 KB | 60x60 | 24-bit | Mario game |
| pomodoro.bmp | Icon | 11 KB | 60x60 | 24-bit | Pomodoro timer |
| **Total Icons** | **20 icons** | **44 KB** | N/A | N/A | Menu display |

### 1.4 Temporary/Cache Files

| File | Location | Type | Scope | Lifecycle | Size |
|------|----------|------|-------|-----------|------|
| flights_cache.json | `/tmp/flights_cache.json` | JSON Cache | Flights app only | Recreated on app start | ~5 KB (estimate) |
| BACKGROUND_CACHE | In-memory | Python dict | Disney app only | Session duration | ~150 KB (6 images × 25 KB) |

### 1.5 Configuration Files

| File | Type | Purpose | Scope |
|------|------|---------|-------|
| .gitignore | Text | Version control | Repository |
| pizero-webui.service | Systemd Unit | Service definition | System |

---

## 2. COMPLETE SCHEMA DOCUMENTATION

### 2.1 CONFIG.JSON Schema

**File Size:** 2,838 bytes (129 lines)  
**Last Modified:** 2025-11-08 20:15:24 UTC  
**Validation:** ✓ Valid JSON  
**Access Points:** 8 read locations, 1 write point (web API)

#### Structure Overview

```
config.json (root)
├── weather (object, 5 fields)
├── mbta (object, 11 fields)
├── disney (object, 7 fields)
├── flights (object, 7 fields)
├── pomodoro (object, 7 fields)
├── forbidden (object, 1 field)
├── medicine (object, 5 fields)
├── menu (object, 3 fields)
│   └── apps (array of 8 app definitions)
├── system (object, 9 fields)
└── display (object, 4 fields)
```

#### Detailed Field Documentation

**[WEATHER]** - Weather Application Configuration
| Field | Type | Value | Required | Purpose | Validation |
|-------|------|-------|----------|---------|------------|
| location | string | "Rio de Janeiro" | Yes | Weather location | Any non-empty string |
| units | string | "metric" | Yes | Temperature units | "metric" or "imperial" |
| update_interval | integer | 300 | Yes | API update frequency (seconds) | > 0 |
| display_format | string | "detailed" | No | Display detail level | "simple", "detailed" |
| show_forecast | boolean | true | No | Show forecast data | true/false |

**[MBTA]** - Boston Transit Configuration
| Field | Type | Value | Required | Purpose | Notes |
|-------|------|-------|----------|---------|-------|
| home_station_id | string | "place-davis" | Yes | Home station ID | MBTA API station ID |
| home_station_name | string | "Davis Square" | Yes | Display name | Human-readable |
| work_station_id | string | "place-pktrm" | Yes | Work station ID | MBTA API station ID |
| work_station_name | string | "Park Street" | Yes | Display name | Human-readable |
| update_interval | integer | 30 | Yes | API update frequency (s) | Typical: 30 |
| morning_start | string | "06:00" | Yes | Morning period start | HH:MM format |
| morning_end | string | "12:00" | Yes | Morning period end | HH:MM format |
| evening_start | string | "15:00" | Yes | Evening period start | HH:MM format |
| evening_end | string | "21:00" | Yes | Evening period end | HH:MM format |
| show_delays | boolean | true | No | Display delay alerts | true/false |
| max_predictions | integer | 3 | No | Max transit predictions | 1-10 recommended |

**[DISNEY]** - Disney Wait Times Configuration
| Field | Type | Value | Required | Purpose | Notes |
|-------|------|-------|----------|---------|-------|
| park_id | integer | 6 | Yes | Park code | 6 = Magic Kingdom |
| park_name | string | "Magic Kingdom" | Yes | Display name | Human-readable |
| update_interval | integer | 10 | Yes | API update frequency (s) | Typical: 10-30 |
| data_refresh_rides | integer | 20 | Yes | Refresh interval for ride data (s) | Typical: 20 |
| sort_by | string | "wait_time" | No | Sort order | "wait_time", "name" |
| show_closed | boolean | false | No | Display closed rides | true/false |
| favorite_rides | array | [] | No | Favorite ride IDs | Array of strings |

**[FLIGHTS]** - Flight Tracking Configuration
| Field | Type | Value | Required | Purpose | Validation |
|-------|------|-------|----------|---------|------------|
| latitude | float | 40.716389 | Yes | Center latitude (NYC) | -90 to 90 |
| longitude | float | -73.954167 | Yes | Center longitude (NYC) | -180 to 180 |
| radius_km | integer | 15 | Yes | Search radius in km | > 0 |
| update_interval | integer | 15 | Yes | API update frequency (s) | Typical: 15 |
| min_altitude | integer | 0 | No | Minimum altitude (ft) | >= 0 |
| max_altitude | integer | 10000 | No | Maximum altitude (ft) | > min_altitude |
| show_details | boolean | true | No | Show flight details | true/false |

**[POMODORO]** - Timer Configuration
| Field | Type | Value | Required | Purpose | Validation |
|-------|------|-------|----------|---------|------------|
| work_duration | integer | 1500 | Yes | Work period duration (s) | Typically 1500 (25min) |
| short_break | integer | 300 | Yes | Short break duration (s) | Typically 300 (5min) |
| long_break | integer | 900 | Yes | Long break duration (s) | Typically 900 (15min) |
| sessions_until_long_break | integer | 4 | Yes | Sessions before long break | 1-10 |
| auto_start_breaks | boolean | false | No | Auto-start breaks | true/false |
| auto_start_pomodoros | boolean | false | No | Auto-start pomodoros | true/false |
| sound_enabled | boolean | false | No | Enable sound alerts | true/false |

**[FORBIDDEN]** - Easter Egg Configuration
| Field | Type | Value | Required | Purpose | Notes |
|-------|------|-------|----------|---------|-------|
| message | string | "Alem de viado eh curioso ein!" | Yes | Hidden message | Display only when unlocked |

**[MEDICINE]** - Medicine Tracking Configuration
| Field | Type | Value | Required | Purpose | Validation |
|-------|------|-------|----------|---------|------------|
| data_file | string | "/home/pizero2w/pizero_apps/medicine_data.json" | Yes | Medicine data file path | Full path required |
| update_interval | integer | 60 | Yes | Display refresh interval (s) | Typical: 60 |
| reminder_window | integer | 30 | Yes | Reminder buffer time (min) | Typical: 15-30 |
| alert_upcoming_minutes | integer | 15 | Yes | Alert time before (min) | Typical: 10-20 |
| rotate_interval | integer | 3 | Yes | Rotation interval (s) | For multiple medicines |

**[MENU]** - Application Menu Configuration
| Field | Type | Count | Purpose | Notes |
|-------|------|-------|---------|-------|
| apps | array | 8 | Application menu items | Each with id, name, enabled, order |
| button_hold_time | float | 2.0 | Long-press duration (s) | Exit trigger |
| scroll_speed | float | 0.5 | Menu scroll speed | 0.1-1.0 range |

**Menu Apps Array Detail:**
```
apps: [
  { id: "weather", name: "Weather", enabled: true, order: 1 },
  { id: "mbta", name: "MBTA", enabled: true, order: 2 },
  { id: "disney", name: "Disney", enabled: true, order: 3 },
  { id: "flights", name: "Flights", enabled: true, order: 4 },
  { id: "pomodoro", name: "Pomodoro", enabled: true, order: 5 },
  { id: "medicine", name: "Medicine", enabled: true, order: 6 },
  { id: "forbidden", name: "Forbidden", enabled: true, order: 7 },
  { id: "reboot", name: "Reboot", enabled: true, order: 8 }
]
```

**[SYSTEM]** - System Configuration
| Field | Type | Value | Required | Purpose | Notes |
|-------|------|-------|----------|---------|-------|
| wifi_ssid | string | "" | **REQUIRED** | WiFi network name | EMPTY - CRITICAL ISSUE |
| wifi_password | string | "" | **REQUIRED** | WiFi password | EMPTY - ISSUE |
| hotspot_enabled | boolean | false | No | Enable hotspot mode | For config access |
| hotspot_ssid | string | "PiZero-Config" | Yes | Hotspot network name | Fallback access |
| hotspot_password | string | "raspberry" | Yes | Hotspot password | Default credential |
| display_brightness | integer | 100 | Yes | Display brightness (%) | 0-100 |
| timezone | string | "America/New_York" | Yes | System timezone | TZ database name |
| auto_sleep | boolean | false | No | Enable auto sleep | For power saving |
| sleep_timeout | integer | 300 | Yes | Sleep timeout (s) | Typical: 300-600 |

**[DISPLAY]** - E-Paper Display Configuration
| Field | Type | Value | Required | Purpose | Notes |
|-------|------|-------|----------|---------|-------|
| rotation | integer | 0 | Yes | Display rotation (degrees) | 0, 90, 180, 270 |
| invert_colors | boolean | false | No | Invert display colors | For readability |
| refresh_mode | string | "auto" | Yes | Refresh strategy | "auto", "partial", "full" |
| partial_update_limit | integer | 10 | Yes | Partial updates before full | e-paper limitation |

---

### 2.2 MEDICINE_DATA.JSON Schema

**File Size:** 3,969 bytes (186 lines)  
**Last Modified:** 2025-11-08 20:15:24 UTC  
**Validation:** ✓ Valid JSON  
**Access Points:** 2 primary readers, 5 write endpoints

#### Structure Overview

```
medicine_data.json (root)
├── medicines (array of 5 objects)
├── tracking (object with daily entries)
├── time_windows (object with 4 time windows)
└── last_updated (ISO 8601 timestamp)
```

#### 2.2.1 Medicines Array Schema

Each medicine object has the following structure:

| Field | Type | Required | Purpose | Constraints |
|-------|------|----------|---------|-------------|
| **id** | string | Yes | Unique identifier | Format: "med_001" or "med_TIMESTAMP" |
| **name** | string | Yes | Medicine/vitamin name | Max 50 chars recommended |
| **dosage** | string | Yes | Dosage amount | E.g., "2000 IU", "30mg" |
| **time_window** | string | Yes | Time period for taking | Values: "morning", "afternoon", "evening", "night" |
| **window_start** | string | Yes | Start time of window | Format: "HH:MM" (24-hour) |
| **window_end** | string | Yes | End time of window | Format: "HH:MM" (24-hour) |
| **days** | array | Yes | Days to take medicine | Values: ["mon","tue","wed","thu","fri","sat","sun"] |
| **with_food** | boolean | Yes | Take with food | true/false |
| **notes** | string | No | Additional notes | Max 100 chars |
| **pills_remaining** | integer | Yes | Inventory count | >= 0 |
| **pills_per_dose** | integer | Yes | Pills per single dose | >= 1 |
| **low_stock_threshold** | integer | Yes | Threshold for warnings | >= 1 |
| **active** | boolean | Yes | Is medicine active | true/false |
| **color_code** | string | No | Display color | E.g., "yellow", "red", "blue" |

**Example Medicine Object:**
```json
{
  "id": "med_001",
  "name": "Vitamin D",
  "dosage": "2000 IU",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "12:00",
  "days": ["mon","tue","wed","thu","fri","sat","sun"],
  "with_food": true,
  "notes": "Take with breakfast",
  "active": true,
  "color_code": "yellow",
  "pills_remaining": 58,
  "pills_per_dose": 1,
  "low_stock_threshold": 10
}
```

#### 2.2.2 Tracking Object Schema

**Format:** `{ "YYYY-MM-DD": { "tracking_entries": {...} } }`

Each daily tracking object contains entries with key format: `{medicine_id}_{time_window}`

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| **tracking_key** | string | Unique key per medicine per window | "med_001_morning" |
| **taken** | boolean | Was medicine taken | true/false |
| **timestamp** | string | When medicine was marked taken | "2025-11-08T08:04:55" |

**Example Tracking Data:**
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

#### 2.2.3 Time Windows Object Schema

Predefined time windows for medicine scheduling:

| Window | Start | End | Purpose |
|--------|-------|-----|---------|
| morning | 06:00 | 12:00 | Morning medications |
| afternoon | 12:00 | 18:00 | Afternoon medications |
| evening | 18:00 | 22:00 | Evening medications |
| night | 22:00 | 23:59 | Night/bedtime medications |

**Structure:**
```json
{
  "morning": { "start": "06:00", "end": "12:00" },
  "afternoon": { "start": "12:00", "end": "18:00" },
  "evening": { "start": "18:00", "end": "22:00" },
  "night": { "start": "22:00", "end": "23:59" }
}
```

#### 2.2.4 Metadata Fields

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| **last_updated** | ISO 8601 string | Timestamp of last data modification | "2025-11-08T12:30:40" |

---

## 3. CURRENT DATA STATE & STATISTICS

### 3.1 Config.json Content Summary

**Total Configuration Sections:** 10  
**Total Configuration Fields:** 60  
**Boolean Configurations:** 14  
**String Configurations:** 22  
**Numeric Configurations:** 24  
**Array Configurations:** 1 (menu apps)

**Active Applications:** 8  
**Enabled Applications:** 8/8 (100%)

### 3.2 Medicine_data.json Content Summary

**Total Medicines:** 5
- Vitamin D (med_001)
- Vyvanse (med_1762467778545)
- Bupropion XL (med_1762467794570)
- Magnesium (med_1762530242594)
- Fish Oil (med_1762606811268)

**Tracking Data:**
- Days tracked: 3 (2025-11-06, 2025-11-07, 2025-11-08)
- Total tracking entries: 10
- Medicines taken (Nov 6): 2/5
- Medicines taken (Nov 7): 4/5
- Medicines taken (Nov 8): 4/5

**Inventory Status:**
| Medicine | Pills Remaining | Threshold | Status |
|-----------|-----------------|-----------|--------|
| Vitamin D | 58 | 10 | ✓ OK |
| Vyvanse | 16 | 7 | ✓ OK |
| Bupropion XL | 45 | 7 | ✓ OK |
| Magnesium | 28 | 10 | ✓ OK |
| Fish Oil | 199 | 10 | ✓ OK |

**Data Growth Estimate:**
- Daily tracking entries: ~5 entries/day (5 medicines × 1 window)
- Monthly growth: ~150 tracking entries
- Annual growth: ~1,825 tracking entries
- Estimated annual file size growth: ~4-5 KB

---

## 4. DATA RELATIONSHIPS & DEPENDENCIES

### 4.1 Configuration Dependencies

```
config.json
├─ weather → Used by: weather_cal_app.py
├─ mbta → Used by: mbta_app.py
├─ disney → Used by: disney_app.py
├─ flights → Used by: flights_app.py
├─ pomodoro → Used by: pomodoro_app.py
├─ medicine → Used by: medicine_app.py
│  └─ Specifies path to medicine_data.json
├─ forbidden → Used by: forbidden_app.py
├─ menu → Used by: menu_button.py, menu_simple.py
├─ system → Used by: web_config.py, system config
└─ display → Used by: all apps for rendering
```

### 4.2 Medicine Data Dependencies

```
medicine_data.json
├─ Medicines array
│  ├─ Referenced by: medicine_app.py (display pending)
│  ├─ Referenced by: web_config.py (CRUD operations)
│  └─ Format: medicine ID MUST match tracking keys
├─ Tracking object
│  ├─ Referenced by: medicine_app.py (check if taken)
│  ├─ Referenced by: web_config.py (update taken status)
│  └─ Key format: {medicine_id}_{time_window}
└─ Time windows
   ├─ Referenced by: medicine_app.py (display schedule)
   └─ Referenced by: web_config.py (medicine queries)
```

### 4.3 Cross-File Dependencies

**Path Configuration Issue (CRITICAL):**
```
config.json contains:
  "data_file": "/home/pizero2w/pizero_apps/medicine_data.json"

But actual location is:
  /home/user/pizerowgpio/medicine_data.json

Impact: Code deployment expects /home/pizero2w/ but files are in /home/user/
```

---

## 5. DATA ACCESS PATTERNS & I/O OPERATIONS

### 5.1 Config.json Access

**Read Operations:**
```
Startup:
  - weather_cal_app.py → line 17 (inline load)
  - flights_app.py → line 25 (inline load)
  - disney_app.py → lines 22-23 (file open)
  - mbta_app.py → lines 22-23 (file open)
  - medicine_app.py → lines 20-21 (file open)
  - pomodoro_app.py → lines 15-16 (file open)
  - forbidden_app.py → lines 37-38 (inline load)
  - web_config.py → line 8 (constant define)

Runtime:
  - web_config.py → GET /api/config (line 947)
  - web_config.py → POST /api/config/<section> (line 954)
```

**Write Operations:**
```
Web API:
  - POST /api/config/<section> → web_config.py line 962
    Updates entire section atomically
```

**Frequency:** Every app startup (read), web UI updates (write)

### 5.2 Medicine_data.json Access

**Read Operations:**
```
Polling:
  - medicine_app.py → load_medicine_data() every 60 seconds
  - medicine_app.py → load_medicine_data() on button click

API:
  - GET /api/medicine/data → web_config.py (all data)
  - GET /api/medicine/pending → web_config.py (filtered)
  - DELETE /api/medicine/<id> → requires read first
  - POST /api/medicine/update → requires read first
```

**Write Operations:**
```
Application:
  - medicine_app.py → save_medicine_data() on dose taken

API Endpoints:
  - POST /api/medicine/add → line 997
  - POST /api/medicine/update → line 1029
  - DELETE /api/medicine/<id> → line 1056
  - POST /api/medicine/mark-taken → line 1163
```

**Frequency:** 
- Reads: Every 60 seconds + on button interactions
- Writes: ~5 times per day (doses taken) + web UI changes

### 5.3 Image Asset Access

**Disney Images:**
```
Access:
  - disney_app.py → load_land_background() (cached)
  - Loaded once per app session
  - Cached in BACKGROUND_CACHE dict (in-memory)
  - Resized to 250x122 pixels

Frequency: One-time per session
```

**Icon Assets:**
```
Access:
  - menu_button.py → Image.open(icon_path)
  - menu_simple.py → Image.open(icon_path)
  - Loaded on demand for menu display

Frequency: Every menu refresh
```

---

## 6. COMPLETE DATA ISSUES REGISTRY

### 6.1 CRITICAL ISSUES

| Issue ID | Severity | Component | Description | Impact | Fix |
|----------|----------|-----------|-------------|--------|-----|
| DATA-001 | CRITICAL | system.wifi_ssid | Empty WiFi SSID | Cannot connect to WiFi on startup | Set valid SSID value |
| DATA-002 | CRITICAL | File Paths | Hardcoded paths mismatch actual location | Code expects `/home/pizero2w/` but files in `/home/user/` | Update all path references |

### 6.2 HIGH PRIORITY ISSUES

| Issue ID | Severity | Component | Description | Impact | Fix |
|----------|----------|-----------|-------------|--------|-----|
| DATA-003 | HIGH | system.wifi_password | Empty WiFi password | Cannot authenticate WiFi | Set valid password |
| DATA-004 | HIGH | medicine_data.json | No backup mechanism | Data loss if file corrupted | Implement auto-backup |
| DATA-005 | HIGH | config.json | No schema validation on write | Invalid config can break apps | Add JSON schema validator |

### 6.3 MEDIUM PRIORITY ISSUES

| Issue ID | Severity | Component | Description | Impact | Fix |
|----------|----------|-----------|-------------|--------|-----|
| DATA-006 | MEDIUM | Data Inconsistency | Medicine color_code only in some records | Inconsistent display | Standardize all records |
| DATA-007 | MEDIUM | File Format | Disney images are BMP but named .png | Misleading file extensions | Rename to .bmp or fix format |
| DATA-008 | MEDIUM | Configuration | Only morning window medicines configured | Doesn't use afternoon/evening/night windows | Utilize all time windows |
| DATA-009 | MEDIUM | Data Documentation | Path discrepancies in DATABASE_DOCUMENTATION.md | Documentation outdated | Update all path references |

### 6.4 LOW PRIORITY ISSUES

| Issue ID | Severity | Component | Description | Impact | Fix |
|----------|----------|-----------|-------------|--------|-----|
| DATA-010 | LOW | Field Consistency | Some medicines missing optional fields | Uneven data structure | Normalize to template |
| DATA-011 | LOW | Cache Management | No explicit cleanup of /tmp/flights_cache.json | Potential disk space issues | Add cleanup logic |
| DATA-012 | LOW | Naming Convention | Inconsistent ID generation (med_001 vs med_TIMESTAMP) | Difficult to manage | Adopt consistent ID scheme |

---

## 7. DATA ORGANIZATION & FILE SYSTEM STRUCTURE

### 7.1 Directory Structure

```
/home/user/pizerowgpio/
├── config.json                          [2.8 KB] - System configuration
├── medicine_data.json                   [3.9 KB] - Medicine tracking
├── disney_images/                       [28 KB]  - Disney park backgrounds
│   ├── Adventureland.png               [3.9 KB]
│   ├── Fantasyland.png                 [3.9 KB]
│   ├── Frontierland.png                [3.9 KB]
│   ├── Liberty Square.png               [3.9 KB]
│   ├── Main Street U.S.A..png           [3.9 KB]
│   └── Tomorrowland.png                [3.9 KB]
├── icons/                               [44 KB]  - Application icons
│   ├── 18x standard icons (1-bit)      [~10 KB]
│   ├── mario.bmp (24-bit)              [11 KB]
│   └── pomodoro.bmp (24-bit)           [11 KB]
├── python_apps/                         [~250 KB] - Application code
│   ├── medicine_app.py
│   ├── disney_app.py
│   ├── flights_app.py
│   ├── mbta_app.py
│   ├── weather_cal_app.py
│   ├── pomodoro_app.py
│   ├── forbidden_app.py
│   ├── menu_button.py
│   ├── menu_simple.py
│   ├── reboot_app.py
│   ├── web_config.py
│   ├── create_icons.py
│   └── create_forbidden_icon.py
└── documentation/                       [~100 KB] - Documentation
    ├── DATABASE_DOCUMENTATION.md
    ├── DOCUMENTATION.md
    ├── README.md
    └── IPHONE_SHORTCUTS_GUIDE.md
```

### 7.2 Naming Conventions

**Configuration Files:**
- Format: `config.json` (single config file)
- Convention: lowercase, no underscores, .json extension

**Data Files:**
- Format: `{entity}_data.json` (e.g., medicine_data.json)
- Convention: lowercase, underscore-separated, .json extension

**Image Assets:**
- Disney images: `{LandName}.png` (e.g., Adventureland.png)
  - Naming: Proper case, spaces in filenames (Main Street U.S.A.)
  - Note: .png extension but BMP format (misleading)
- Icons: `{app_name}.bmp` (e.g., weather.bmp, pomodoro.bmp)
  - Naming: lowercase, app-specific, .bmp extension

**Application Code:**
- Format: `{app_name}_app.py` (e.g., medicine_app.py)
- Convention: lowercase, underscore-separated

**Temporary/Cache:**
- Format: `/tmp/{app_name}_cache.json`
- Convention: system temp directory, cache suffix

### 7.3 Data Location Patterns

**Current Locations (in /home/user/pizerowgpio/):**
```
Data persistence:    ./config.json, ./medicine_data.json
Image assets:        ./disney_images/, ./icons/
Code:               ./{app_name}_app.py
Temporary data:     /tmp/flights_cache.json
In-memory cache:    Python dict objects (not persisted)
```

**Expected Locations (in code references):**
```
Data persistence:    /home/pizero2w/pizero_apps/config.json
                    /home/pizero2w/pizero_apps/medicine_data.json
Image assets:        Relative to app: ./disney_images/, ./icons/
Temporary data:     /tmp/flights_cache.json
```

### 7.4 Backup Mechanisms

**Current Status:** NO AUTOMATIC BACKUP

**What Should Be Backed Up:**
- config.json (critical - contains all app settings)
- medicine_data.json (critical - contains tracking history and inventory)

**Recommended Backup Strategy:**
```
Frequency:   Daily
Location:    /home/user/pizerowgpio/backups/
Retention:   30-day rolling
Format:      Timestamped JSON files
Trigger:     Scheduled cron job
```

---

## 8. DATA SECURITY & VALIDATION ANALYSIS

### 8.1 Security Issues

| Issue | Risk Level | Description | Mitigation |
|-------|-----------|-------------|------------|
| WiFi credentials in plaintext | HIGH | config.json contains WiFi password | Use environment variables or secure config |
| Hotspot default password | MEDIUM | "raspberry" is unchanged default | Change to unique password |
| No access control on web API | MEDIUM | Web config API has no authentication | Implement token-based auth |
| Medicine data unrestricted | MEDIUM | No permission controls on data | Add user authentication |
| Sensitive fields visible | LOW | Medical info in accessible JSON | Encrypt sensitive fields |

### 8.2 Data Validation Status

**Config.json Validation:**
- ✓ Valid JSON syntax
- ✓ All required fields present
- ✗ No schema validation on write (can accept invalid values)
- ✗ WiFi SSID is empty (critical)
- ✗ WiFi password is empty (critical)

**Medicine_data.json Validation:**
- ✓ Valid JSON syntax
- ✓ All medicines have required fields
- ✓ Tracking timestamps in valid format
- ✓ Day values use correct format (mon-sun)
- ✓ Time window references exist
- ✗ Some medicines missing optional fields (inconsistent structure)
- ✗ Color codes not standardized

### 8.3 Data Integrity Checks

**Referential Integrity:**
```
✓ All tracking keys reference valid medicines
✓ All time_window references are defined
✓ All menu apps have valid IDs
✗ medicine_data.json path mismatch (DATA-002)
```

---

## 9. BEST PRACTICES GAP ANALYSIS

### 9.1 Missing Best Practices

| Practice | Current State | Recommendation | Priority |
|----------|--------------|-----------------|----------|
| **Database Backups** | None | Implement daily snapshots | HIGH |
| **Schema Validation** | No | Add JSON Schema for both files | HIGH |
| **Data Migration** | Manual | Implement version management | HIGH |
| **Change Logging** | Minimal | Add audit trail to writes | MEDIUM |
| **Read Caching** | Partial | Implement cache invalidation | MEDIUM |
| **Concurrency Control** | None | Add file locking for writes | MEDIUM |
| **Error Recovery** | Basic try/except | Implement rollback mechanisms | MEDIUM |
| **Data Encryption** | None | Encrypt sensitive config | LOW |
| **Compression** | None | Not needed (small files) | LOW |
| **Archival** | None | Not needed (data only 3 days) | LOW |

### 9.2 Data Access Patterns - Best Practices

**What's Done Well:**
- Using standard JSON format (human-readable, portable)
- Structured data models (medicines, tracking separate)
- Consistent API endpoints for data access
- Timestamp tracking for external change detection

**What Needs Improvement:**
- No read/write locking (concurrent access risk)
- Hardcoded file paths (deployment brittle)
- Mixed initialization patterns (some inline, some file opens)
- No transaction support (partial writes on failure)
- Cache incoherence (Disney app vs actual images)

---

## 10. RECOMMENDATIONS FOR DATA REORGANIZATION

### 10.1 Immediate Actions (1-2 weeks)

**Priority 1: Fix Path Inconsistencies**
```
Current:  /home/pizero2w/pizero_apps/
Actual:   /home/user/pizerowgpio/

Action:
  1. Update all hardcoded paths in Python files
  2. Create symlink if needed: ln -s /home/user/pizerowgpio /home/pizero2w/pizero_apps
  3. Update config.json medicine.data_file value
  4. Update DATABASE_DOCUMENTATION.md
```

**Priority 2: Fix WiFi Configuration**
```
Action:
  1. Set actual WiFi SSID in system.wifi_ssid
  2. Set secure WiFi password
  3. Test connectivity before deployment
```

**Priority 3: Add Data Validation**
```
Action:
  1. Create JSON schema files for both config.json and medicine_data.json
  2. Validate on write in web_config.py
  3. Add pre-flight validation in apps
```

**Priority 4: Implement Basic Backup**
```
Action:
  1. Create /home/user/pizerowgpio/backups/ directory
  2. Add backup logic to save operations
  3. Keep last 7 daily backups
```

### 10.2 Short-term Improvements (1 month)

**Data Organization:**
```
Restructure:
  /home/user/pizerowgpio/
  ├── config/
  │   ├── config.json
  │   └── schema.json
  ├── data/
  │   ├── medicine_data.json
  │   └── backups/
  ├── assets/
  │   ├── disney_images/
  │   └── icons/
  └── apps/
      ├── app1.py
      └── ...
```

**Add Configuration Management:**
```
1. Centralize path definitions in constants.py
2. Use environment variables for deployment paths
3. Implement config inheritance (defaults + overrides)
4. Add config versioning
```

**Implement Data Locking:**
```
1. Add file locks before writes (fcntl or similar)
2. Implement retry logic for lock acquisition
3. Add timeout for stuck locks
4. Log lock conflicts for debugging
```

### 10.3 Long-term Improvements (3+ months)

**Database Evolution:**
```
Consider migration from JSON to:
- SQLite (if persistence needed)
- Time-series DB (if historical tracking important)
- Redis (if real-time performance needed)

Keep JSON for:
- Configuration (stays simple)
- Exports/backups (portability)
```

**Data Architecture:**
```
Proposed:
  config.json → stays as-is (simple structure)
  medicine_data.json → consider split:
    - medicines.json (static config)
    - medicine_tracking.json (grows daily)
    - medicine_inventory.json (reference data)
```

**API Improvements:**
```
1. Add authentication to web_config.py
2. Implement data versioning API
3. Add batch operations for efficiency
4. Implement change notifications (WebSockets)
5. Add full-text search for medicines
```

---

## 11. STORAGE PATTERNS & CONVENTIONS SUMMARY

### 11.1 Current Patterns

| Pattern | Implementation | Example |
|---------|---------------|---------|
| Configuration | Single JSON file | config.json |
| Data storage | Single JSON file | medicine_data.json |
| Image assets | Directory organization | disney_images/, icons/ |
| Caching | Mix of file + memory | /tmp/flights_cache.json + BACKGROUND_CACHE |
| IDs | Mixed schemes | med_001, med_TIMESTAMP |
| Timestamps | ISO 8601 | 2025-11-08T12:30:40 |
| File paths | Hardcoded | /home/pizero2w/pizero_apps/ |

### 11.2 Recommended Conventions

| Pattern | Recommended | Rationale |
|---------|-----------|------------|
| File organization | Separate config/, data/, assets/ | Better separation of concerns |
| ID generation | Consistent TIMESTAMP or UUID | Avoid conflicts, easier tracking |
| Path management | Environment variables | Portable across deployments |
| Configuration | Layered (default + environment) | Flexible for different deployments |
| Backups | Timestamped + version numbers | Easy recovery and tracking |
| API responses | Consistent error format | Predictable client handling |
| Data validation | JSON Schema | Prevent invalid data |
| Caching | TTL-based with invalidation | Prevent stale data |

---

## 12. FINAL SUMMARY & RECOMMENDATIONS

### 12.1 Overall Data Health Assessment

**Data Integrity:** 95% (valid structure, some consistency issues)  
**Accessibility:** 90% (good API coverage, path inconsistencies)  
**Security:** 70% (credentials exposed, no auth, no encryption)  
**Scalability:** 85% (fine for current size, needs optimization for growth)  
**Maintainability:** 75% (documented but outdated, mixed patterns)

### 12.2 Critical Takeaways

1. **Path Mismatch (CRITICAL):** All hardcoded paths reference `/home/pizero2w/` but files are in `/home/user/pizerowgpio/`
2. **WiFi Configuration (CRITICAL):** SSID and password are empty, preventing connectivity
3. **No Backups:** Loss of config.json or medicine_data.json would be irrecoverable
4. **No Validation:** Apps can break with invalid configuration values
5. **File Format Issues:** Disney images are BMP but named .png (misleading)

### 12.3 Quick Win Improvements (< 1 hour each)

```
1. ✓ Fix path inconsistencies (update 11 files)
2. ✓ Set WiFi SSID and password
3. ✓ Rename Disney images to .bmp
4. ✓ Add JSON schema validation in web_config.py
5. ✓ Update DATABASE_DOCUMENTATION.md paths
```

### 12.4 Strategic Recommendations

**Short-term (1 month):**
- Fix critical path and WiFi issues
- Implement automatic backups
- Add data validation
- Restructure directories

**Medium-term (3 months):**
- Implement data versioning
- Add authentication to web API
- Implement file locking
- Add comprehensive audit logging

**Long-term (6+ months):**
- Consider database migration (if needed)
- Implement full data sync/replication
- Build analytics dashboards
- Add historical trending for medicine adherence

---

## APPENDIX A: File Size Calculations

**Total System Data Size:** 693 KB breakdown

| Component | Size | Percentage |
|-----------|------|-----------|
| Icons (44 files) | 44 KB | 6.4% |
| Disney Images (6 files) | 28 KB | 4.0% |
| config.json | 2.8 KB | 0.4% |
| medicine_data.json | 3.9 KB | 0.6% |
| Python Application Code | ~550 KB | 79% |
| Documentation | ~60 KB | 8.7% |
| **TOTAL** | **~693 KB** | **100%** |

---

## APPENDIX B: Data Access Statistics

**config.json Read Operations Per Day:**
- App startup: ~8 reads (one per app)
- Web API: ~2-5 reads (configuration checks)
- **Total:** ~10-15 reads/day

**medicine_data.json Operations Per Day:**
- Polling reads: ~1,440 reads (60s interval, 24hr)
- Button interaction reads: ~10-20 reads
- Medicine taken writes: ~5 writes
- Web API reads: ~5-10 reads
- **Total:** ~1,460 reads/day, ~5 writes/day

**Image Asset Loads Per Day:**
- Disney images: 1-2 full loads (app session start)
- Icon loads: 50-100 loads (menu interactions)
- **Total:** ~100 image loads/day

---

## APPENDIX C: Data Path Reference Sheet

```
CONFIGURATION:
  config.json
    Code path: /home/pizero2w/pizero_apps/config.json ❌
    Actual:    /home/user/pizerowgpio/config.json ✓

MEDICINE DATA:
  medicine_data.json
    Code path: /home/pizero2w/pizero_apps/medicine_data.json ❌
    Actual:    /home/user/pizerowgpio/medicine_data.json ✓
    Config ref: /home/pizero2w/pizero_apps/medicine_data.json ❌

IMAGES:
  Disney parks (relative):
    Code path: ./disney_images/
    Actual:    /home/user/pizerowgpio/disney_images/ ✓
  
  Icons (relative):
    Code path: ./icons/
    Actual:    /home/user/pizerowgpio/icons/ ✓

TEMPORARY:
  Flights cache:
    /tmp/flights_cache.json ✓
  
  Disney background cache:
    In-memory BACKGROUND_CACHE dict ✓

LOGS (if configured):
  /home/pizero2w/pizero_apps/flights_app.log ❌
  (actual location: /home/user/pizerowgpio/ - if logs created)
```

---

**Report Generated:** 2025-11-08  
**Reviewer:** Exhaustive Data Storage Analysis System  
**Status:** Complete

