# Configuration Reference Guide

**Version:** 1.0
**Last Updated:** November 8, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [config.json Structure](#configjson-structure)
3. [medicine_data.json Structure](#medicine_datajson-structure)
4. [Configuration Sections](#configuration-sections)
5. [Valid Values & Constraints](#valid-values--constraints)
6. [Example Configurations](#example-configurations)
7. [Configuration Management](#configuration-management)

---

## Overview

The Pi Zero 2W Medicine Tracker uses two main configuration files:

| File | Purpose | Location |
|------|---------|----------|
| `config.json` | System-wide configuration (all apps) | `~/pizero_apps/config.json` |
| `medicine_data.json` | Medicine database and tracking | `~/pizero_apps/medicine_data.json` |

Both files use JSON format and must maintain valid syntax.

---

## config.json Structure

### Complete Configuration Template

```json
{
  "weather": {
    "location": "string",
    "units": "metric|imperial",
    "update_interval": 300,
    "display_format": "detailed|simple",
    "show_forecast": true
  },
  "mbta": {
    "home_station_id": "string",
    "home_station_name": "string",
    "work_station_id": "string",
    "work_station_name": "string",
    "update_interval": 30,
    "morning_start": "HH:MM",
    "morning_end": "HH:MM",
    "evening_start": "HH:MM",
    "evening_end": "HH:MM",
    "show_delays": true,
    "max_predictions": 3
  },
  "disney": {
    "park_id": 0,
    "park_name": "string",
    "update_interval": 10,
    "data_refresh_rides": 20,
    "sort_by": "wait_time|name",
    "show_closed": false,
    "favorite_rides": []
  },
  "flights": {
    "latitude": 0.0,
    "longitude": 0.0,
    "radius_km": 15,
    "update_interval": 15,
    "min_altitude": 0,
    "max_altitude": 10000,
    "show_details": true
  },
  "pomodoro": {
    "work_duration": 1500,
    "short_break": 300,
    "long_break": 900,
    "sessions_until_long_break": 4,
    "auto_start_breaks": false,
    "auto_start_pomodoros": false,
    "sound_enabled": false
  },
  "medicine": {
    "data_file": "/path/to/medicine_data.json",
    "update_interval": 60,
    "reminder_window": 30,
    "alert_upcoming_minutes": 15,
    "rotate_interval": 3
  },
  "forbidden": {
    "message": "string"
  },
  "menu": {
    "apps": [
      {
        "id": "string",
        "name": "string",
        "enabled": true,
        "order": 1
      }
    ],
    "button_hold_time": 2.0,
    "scroll_speed": 0.5
  },
  "system": {
    "wifi_ssid": "string",
    "wifi_password": "string",
    "hotspot_enabled": false,
    "hotspot_ssid": "string",
    "hotspot_password": "string",
    "display_brightness": 100,
    "timezone": "string",
    "auto_sleep": false,
    "sleep_timeout": 300
  },
  "display": {
    "rotation": 0,
    "invert_colors": false,
    "refresh_mode": "auto|full|partial",
    "partial_update_limit": 10
  }
}
```

---

## medicine_data.json Structure

### Complete Medicine Data Template

```json
{
  "medicines": [
    {
      "id": "med_1234567890",
      "name": "Medicine Name",
      "dosage": "Amount + Unit",
      "time_window": "morning|afternoon|evening|night",
      "window_start": "HH:MM",
      "window_end": "HH:MM",
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "with_food": true,
      "notes": "Optional notes",
      "active": true,
      "pills_remaining": 60,
      "pills_per_dose": 1,
      "low_stock_threshold": 10
    }
  ],
  "tracking": {
    "YYYY-MM-DD": {
      "med_id_time_window": {
        "taken": true,
        "timestamp": "2025-11-08T08:15:00"
      }
    }
  },
  "time_windows": {
    "morning": {"start": "06:00", "end": "10:00"},
    "afternoon": {"start": "12:00", "end": "16:00"},
    "evening": {"start": "18:00", "end": "22:00"},
    "night": {"start": "22:00", "end": "23:59"}
  }
}
```

---

## Configuration Sections

### 1. Weather Configuration

Controls the Weather & Calendar application.

```json
"weather": {
  "location": "Boston",
  "units": "metric",
  "update_interval": 300,
  "display_format": "detailed",
  "show_forecast": true
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `location` | string | "Boston" | City name for weather lookup |
| `units` | string | "metric" | "metric" (°C) or "imperial" (°F) |
| `update_interval` | integer | 300 | Refresh interval in seconds (min: 60) |
| `display_format` | string | "detailed" | "detailed" or "simple" display |
| `show_forecast` | boolean | true | Show 5-day forecast |

**Example:**
```json
"weather": {
  "location": "Rio de Janeiro",
  "units": "metric",
  "update_interval": 600,
  "display_format": "detailed",
  "show_forecast": false
}
```

---

### 2. MBTA Configuration

Boston transit app configuration.

```json
"mbta": {
  "home_station_id": "place-davis",
  "home_station_name": "Davis Square",
  "work_station_id": "place-pktrm",
  "work_station_name": "Park Street",
  "update_interval": 30,
  "morning_start": "06:00",
  "morning_end": "12:00",
  "evening_start": "15:00",
  "evening_end": "21:00",
  "show_delays": true,
  "max_predictions": 3
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `home_station_id` | string | Required | MBTA station ID (home) |
| `home_station_name` | string | Required | Station name (home) |
| `work_station_id` | string | Required | MBTA station ID (work) |
| `work_station_name` | string | Required | Station name (work) |
| `update_interval` | integer | 30 | Refresh interval in seconds |
| `morning_start` | string | "06:00" | Morning commute start time (HH:MM) |
| `morning_end` | string | "12:00" | Morning commute end time (HH:MM) |
| `evening_start` | string | "15:00" | Evening commute start time (HH:MM) |
| `evening_end` | string | "21:00" | Evening commute end time (HH:MM) |
| `show_delays` | boolean | true | Show delay information |
| `max_predictions` | integer | 3 | Number of predictions to show |

**Common Station IDs:**
- Davis Square: `place-davis`
- Park Street: `place-pktrm`
- Downtown Crossing: `place-dtxst`
- Harvard Square: `place-harsq`

---

### 3. Disney Configuration

Disney wait times app configuration.

```json
"disney": {
  "park_id": 6,
  "park_name": "Magic Kingdom",
  "update_interval": 10,
  "data_refresh_rides": 20,
  "sort_by": "wait_time",
  "show_closed": false,
  "favorite_rides": []
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `park_id` | integer | 6 | Park ID (see table below) |
| `park_name` | string | Required | Display name of park |
| `update_interval` | integer | 10 | Seconds per ride rotation |
| `data_refresh_rides` | integer | 20 | Full data refresh interval (seconds) |
| `sort_by` | string | "wait_time" | "wait_time" or "name" |
| `show_closed` | boolean | false | Show closed rides |
| `favorite_rides` | array | [] | IDs of favorite rides to highlight |

**Park IDs:**
| ID | Park |
|----|----|
| 5 | Epcot |
| 6 | Magic Kingdom |
| 7 | Hollywood Studios |
| 8 | Animal Kingdom |

---

### 4. Flights Configuration

Aircraft tracking configuration.

```json
"flights": {
  "latitude": 40.716389,
  "longitude": -73.954167,
  "radius_km": 15,
  "update_interval": 15,
  "min_altitude": 0,
  "max_altitude": 10000,
  "show_details": true
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `latitude` | float | Required | Your latitude (decimal degrees) |
| `longitude` | float | Required | Your longitude (decimal degrees) |
| `radius_km` | integer | 15 | Detection radius in kilometers |
| `update_interval` | integer | 15 | Refresh interval in seconds |
| `min_altitude` | integer | 0 | Minimum altitude in feet |
| `max_altitude` | integer | 10000 | Maximum altitude in feet |
| `show_details` | boolean | true | Show flight details |

**Latitude/Longitude Examples:**
- New York City: 40.7128, -74.0060
- Boston: 42.3601, -71.0589
- San Francisco: 37.7749, -122.4194

---

### 5. Pomodoro Configuration

Productivity timer configuration.

```json
"pomodoro": {
  "work_duration": 1500,
  "short_break": 300,
  "long_break": 900,
  "sessions_until_long_break": 4,
  "auto_start_breaks": false,
  "auto_start_pomodoros": false,
  "sound_enabled": false
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `work_duration` | integer | 1500 | Work session duration in seconds (25min) |
| `short_break` | integer | 300 | Short break duration in seconds (5min) |
| `long_break` | integer | 900 | Long break duration in seconds (15min) |
| `sessions_until_long_break` | integer | 4 | Sessions before long break |
| `auto_start_breaks` | boolean | false | Auto-start breaks after sessions |
| `auto_start_pomodoros` | boolean | false | Auto-start next session |
| `sound_enabled` | boolean | false | Enable sound notifications |

**Duration Examples:**
- 25 minutes: 1500 seconds
- 5 minutes: 300 seconds
- 15 minutes: 900 seconds
- 10 minutes: 600 seconds

---

### 6. Medicine Configuration

Medicine tracker app configuration.

```json
"medicine": {
  "data_file": "/home/pizero2w/pizero_apps/medicine_data.json",
  "update_interval": 60,
  "reminder_window": 30,
  "alert_upcoming_minutes": 15,
  "rotate_interval": 3
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data_file` | string | Required | Full path to medicine_data.json |
| `update_interval` | integer | 60 | Check interval in seconds (60=1min) |
| `reminder_window` | integer | 30 | Reminder buffer in minutes (±30min) |
| `alert_upcoming_minutes` | integer | 15 | Minutes before showing "coming soon" |
| `rotate_interval` | integer | 3 | Rotation speed in seconds per medicine |

**Important:**
- `update_interval`: How often app checks for due medicines
- `reminder_window`: If medicine due at 8:00 AM with 30min window, shows 7:30-8:30 AM
- `rotate_interval`: Time each medicine displays before showing next one

---

### 7. Forbidden Message Configuration

Custom message display.

```json
"forbidden": {
  "message": "Custom text here"
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `message` | string | Required | Message to display |

---

### 8. Menu Configuration

Main menu system configuration.

```json
"menu": {
  "apps": [
    {
      "id": "weather",
      "name": "Weather",
      "enabled": true,
      "order": 1
    },
    {
      "id": "mbta",
      "name": "MBTA",
      "enabled": true,
      "order": 2
    },
    {
      "id": "medicine",
      "name": "Medicine",
      "enabled": true,
      "order": 6
    }
  ],
  "button_hold_time": 2.0,
  "scroll_speed": 0.5
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `apps` | array | Required | List of available apps |
| `button_hold_time` | float | 2.0 | Long press duration in seconds |
| `scroll_speed` | float | 0.5 | Menu scroll speed multiplier |

**App Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique app identifier |
| `name` | string | Display name on menu |
| `enabled` | boolean | Show in menu |
| `order` | integer | Position in menu (1-8) |

**Valid App IDs:**
- `weather` - Weather & Calendar
- `mbta` - Boston Transit
- `disney` - Disney Wait Times
- `flights` - Flight Tracker
- `pomodoro` - Pomodoro Timer
- `medicine` - Medicine Tracker
- `forbidden` - Custom Message
- `reboot` - System Reboot

---

### 9. System Configuration

System-wide settings.

```json
"system": {
  "wifi_ssid": "Your Network",
  "wifi_password": "password123",
  "hotspot_enabled": false,
  "hotspot_ssid": "PiZero-Config",
  "hotspot_password": "raspberry",
  "display_brightness": 100,
  "timezone": "America/New_York",
  "auto_sleep": false,
  "sleep_timeout": 300
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `wifi_ssid` | string | "" | WiFi network name |
| `wifi_password` | string | "" | WiFi password (empty = open network) |
| `hotspot_enabled` | boolean | false | Enable AP hotspot mode |
| `hotspot_ssid` | string | "PiZero-Config" | Hotspot network name |
| `hotspot_password` | string | "raspberry" | Hotspot password |
| `display_brightness` | integer | 100 | Brightness 0-100% (e-ink: no effect) |
| `timezone` | string | "America/New_York" | System timezone |
| `auto_sleep` | boolean | false | Auto-sleep after timeout |
| `sleep_timeout` | integer | 300 | Sleep timeout in seconds |

**Common Timezones:**
- `America/New_York` - Eastern
- `America/Chicago` - Central
- `America/Denver` - Mountain
- `America/Los_Angeles` - Pacific
- `Europe/London` - GMT
- `Europe/Paris` - CET
- `Asia/Tokyo` - JST
- `Australia/Sydney` - AEDT

---

### 10. Display Configuration

Display driver settings.

```json
"display": {
  "rotation": 0,
  "invert_colors": false,
  "refresh_mode": "auto",
  "partial_update_limit": 10
}
```

**Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rotation` | integer | 0 | Screen rotation: 0, 90, 180, 270 |
| `invert_colors` | boolean | false | Invert black/white |
| `refresh_mode` | string | "auto" | "auto", "full", or "partial" |
| `partial_update_limit` | integer | 10 | Partial updates before full refresh |

---

## medicine_data.json Fields

### Medicine Object

```json
{
  "id": "med_1625467778545",
  "name": "Vitamin D",
  "dosage": "2000 IU",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "10:00",
  "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
  "with_food": true,
  "notes": "Take with breakfast",
  "active": true,
  "pills_remaining": 60,
  "pills_per_dose": 1,
  "low_stock_threshold": 10
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique ID (auto-generated as "med_" + timestamp) |
| `name` | string | Yes | Medicine/supplement name |
| `dosage` | string | Yes | Dosage (e.g., "30mg", "2000 IU") |
| `time_window` | string | Yes | "morning", "afternoon", "evening", or "night" |
| `window_start` | string | Yes | Start time in HH:MM format |
| `window_end` | string | Yes | End time in HH:MM format |
| `days` | array | Yes | Days active: ["mon", "tue", "wed", "thu", "fri", "sat", "sun"] |
| `with_food` | boolean | No | Display food indicator |
| `notes` | string | No | Custom notes (optional) |
| `active` | boolean | Yes | Include in tracking |
| `pills_remaining` | integer | Yes | Current pill count |
| `pills_per_dose` | integer | Yes | Pills taken per dose |
| `low_stock_threshold` | integer | Yes | Alert threshold (shows warning when ≤) |

### Time Windows

```json
"time_windows": {
  "morning": {"start": "06:00", "end": "10:00"},
  "afternoon": {"start": "12:00", "end": "16:00"},
  "evening": {"start": "18:00", "end": "22:00"},
  "night": {"start": "22:00", "end": "23:59"}
}
```

These define when reminders appear. User can customize these times.

### Tracking Object

```json
"tracking": {
  "2025-11-08": {
    "med_1625467778545_morning": {
      "taken": true,
      "timestamp": "2025-11-08T08:15:30"
    },
    "med_001_morning": {
      "taken": true,
      "timestamp": "2025-11-08T08:15:30"
    }
  }
}
```

**Structure:**
- Key: Date as "YYYY-MM-DD"
- Value: Object with keys as "{medicine_id}_{time_window}"
- Each entry tracks whether medicine was taken and when

---

## Valid Values & Constraints

### Time Format (HH:MM)

```
06:00   = 6:00 AM
18:00   = 6:00 PM
23:59   = 11:59 PM
00:00   = 12:00 AM (midnight)
```

### Day Abbreviations

Valid days in medicine `days` array:
```
"mon"   = Monday
"tue"   = Tuesday
"wed"   = Wednesday
"thu"   = Thursday
"fri"   = Friday
"sat"   = Saturday
"sun"   = Sunday
```

### Time Window Values

Valid `time_window` options:
- `"morning"` - 6:00 AM to 10:00 AM (default)
- `"afternoon"` - 12:00 PM to 4:00 PM
- `"evening"` - 6:00 PM to 10:00 PM
- `"night"` - 10:00 PM to 11:59 PM

### Numeric Constraints

| Setting | Min | Max | Unit |
|---------|-----|-----|------|
| `update_interval` | 10 | 3600 | seconds |
| `reminder_window` | 0 | 60 | minutes |
| `rotate_interval` | 1 | 10 | seconds |
| `work_duration` | 60 | 7200 | seconds |
| `max_predictions` | 1 | 10 | count |
| `radius_km` | 1 | 100 | kilometers |
| `pills_remaining` | 0 | 999 | integer |
| `low_stock_threshold` | 0 | 999 | integer |
| `display_brightness` | 0 | 100 | percent |

---

## Example Configurations

### Minimal Configuration (Medicine Only)

For a device running just the medicine tracker:

```json
{
  "medicine": {
    "data_file": "/home/pi/pizero_apps/medicine_data.json",
    "update_interval": 60,
    "reminder_window": 30,
    "alert_upcoming_minutes": 15,
    "rotate_interval": 3
  },
  "menu": {
    "apps": [
      {
        "id": "medicine",
        "name": "Medicine",
        "enabled": true,
        "order": 1
      }
    ],
    "button_hold_time": 2.0,
    "scroll_speed": 0.5
  },
  "system": {
    "timezone": "America/New_York"
  },
  "display": {
    "rotation": 0,
    "invert_colors": false,
    "refresh_mode": "auto",
    "partial_update_limit": 10
  }
}
```

### Full Featured Configuration

All apps enabled:

```json
{
  "weather": {
    "location": "Boston",
    "units": "metric",
    "update_interval": 300,
    "display_format": "detailed",
    "show_forecast": true
  },
  "mbta": {
    "home_station_id": "place-davis",
    "home_station_name": "Davis Square",
    "work_station_id": "place-pktrm",
    "work_station_name": "Park Street",
    "update_interval": 30,
    "morning_start": "06:00",
    "morning_end": "12:00",
    "evening_start": "15:00",
    "evening_end": "21:00",
    "show_delays": true,
    "max_predictions": 3
  },
  "disney": {
    "park_id": 6,
    "park_name": "Magic Kingdom",
    "update_interval": 10,
    "data_refresh_rides": 20,
    "sort_by": "wait_time",
    "show_closed": false,
    "favorite_rides": []
  },
  "flights": {
    "latitude": 42.3601,
    "longitude": -71.0589,
    "radius_km": 15,
    "update_interval": 15,
    "min_altitude": 1000,
    "max_altitude": 35000,
    "show_details": true
  },
  "pomodoro": {
    "work_duration": 1500,
    "short_break": 300,
    "long_break": 900,
    "sessions_until_long_break": 4,
    "auto_start_breaks": false,
    "auto_start_pomodoros": false,
    "sound_enabled": false
  },
  "medicine": {
    "data_file": "/home/pi/pizero_apps/medicine_data.json",
    "update_interval": 60,
    "reminder_window": 30,
    "alert_upcoming_minutes": 15,
    "rotate_interval": 3
  },
  "forbidden": {
    "message": "Custom message here"
  },
  "menu": {
    "apps": [
      {"id": "weather", "name": "Weather", "enabled": true, "order": 1},
      {"id": "mbta", "name": "MBTA", "enabled": true, "order": 2},
      {"id": "disney", "name": "Disney", "enabled": true, "order": 3},
      {"id": "flights", "name": "Flights", "enabled": true, "order": 4},
      {"id": "pomodoro", "name": "Pomodoro", "enabled": true, "order": 5},
      {"id": "medicine", "name": "Medicine", "enabled": true, "order": 6},
      {"id": "forbidden", "name": "Forbidden", "enabled": true, "order": 7},
      {"id": "reboot", "name": "Reboot", "enabled": true, "order": 8}
    ],
    "button_hold_time": 2.0,
    "scroll_speed": 0.5
  },
  "system": {
    "wifi_ssid": "MyNetwork",
    "wifi_password": "",
    "hotspot_enabled": false,
    "hotspot_ssid": "PiZero-Config",
    "hotspot_password": "raspberry",
    "display_brightness": 100,
    "timezone": "America/New_York",
    "auto_sleep": false,
    "sleep_timeout": 300
  },
  "display": {
    "rotation": 0,
    "invert_colors": false,
    "refresh_mode": "auto",
    "partial_update_limit": 10
  }
}
```

---

## Configuration Management

### Editing Configuration

1. **Via Web UI (Recommended):**
   - Open `http://<pi-ip>:5000`
   - Click on app section
   - Modify settings and save

2. **Via SSH:**
   ```bash
   ssh pi@<pi-ip>
   nano ~/pizero_apps/config.json
   # Edit and save with Ctrl+O, Enter, Ctrl+X
   ```

3. **Via JSON Editor:**
   ```bash
   # Validate before and after
   python3 -m json.tool ~/pizero_apps/config.json > /dev/null && echo "Valid"
   ```

### Validating Configuration

```bash
# Check config.json syntax
python3 -c "import json; json.load(open('/home/pi/pizero_apps/config.json'))" && echo "Valid"

# Check medicine_data.json syntax
python3 -c "import json; json.load(open('/home/pi/pizero_apps/medicine_data.json'))" && echo "Valid"

# Pretty print for review
cat ~/pizero_apps/config.json | python3 -m json.tool | less
```

### Applying Changes

Most changes take effect immediately. Some require service restart:

```bash
# Restart all services
sudo systemctl restart pizero-webui pizero-menu

# Or manually
pkill -f web_config.py
pkill -f menu_button.py
cd ~/pizero_apps
python3 web_config.py &
python3 menu_button.py &
```

### Backup Before Changes

```bash
# Always backup before editing
cp ~/pizero_apps/config.json ~/config_backup_$(date +%Y%m%d_%H%M%S).json
```

### Rolling Back Changes

```bash
# List backups
ls -lh ~/config_backup_*.json

# Restore from backup
cp ~/config_backup_20251108_150000.json ~/pizero_apps/config.json

# Restart services
sudo systemctl restart pizero-webui
```

---

## Configuration Troubleshooting

### Issue: Invalid JSON

```
Error: json.decoder.JSONDecodeError
```

**Solution:**
1. Use Python to identify the error:
   ```bash
   python3 -m json.tool ~/pizero_apps/config.json
   ```
2. Common issues:
   - Missing commas between fields
   - Trailing commas at end of objects/arrays
   - Unquoted strings
   - Unclosed braces/brackets

### Issue: Settings Not Applied

**Solution:**
1. Verify file was saved: `cat ~/pizero_apps/config.json | grep "setting_name"`
2. Restart services: `sudo systemctl restart pizero-webui`
3. Check service status: `sudo systemctl status pizero-menu`

### Issue: Web UI Shows Old Config

**Solution:**
1. Hard refresh browser: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Clear browser cache
3. Restart web server: `sudo systemctl restart pizero-webui`

---

## Quick Configuration Commands

```bash
# View current config
cat ~/pizero_apps/config.json | python3 -m json.tool

# Edit config
nano ~/pizero_apps/config.json

# Validate config
python3 << 'EOF'
import json
try:
    with open('/home/pi/pizero_apps/config.json') as f:
        json.load(f)
    print("✓ config.json is valid")
except Exception as e:
    print(f"✗ Error: {e}")
EOF

# Find specific setting
grep -A 5 '"weather"' ~/pizero_apps/config.json

# Update single setting (using jq if installed)
jq '.weather.update_interval = 600' ~/pizero_apps/config.json > temp.json && mv temp.json ~/pizero_apps/config.json
```

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
