# Pi Zero 2W Medicine & Vitamin Tracking System
## Complete Documentation

**Version:** 1.0
**Last Updated:** November 6, 2025
**Device:** Raspberry Pi Zero 2W with Waveshare 2.13" V4 e-ink display

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Hardware Specifications](#hardware-specifications)
4. [Application Details](#application-details)
5. [User Experience (UX)](#user-experience-ux)
6. [File Structure](#file-structure)
7. [Configuration](#configuration)
8. [API Documentation](#api-documentation)
9. [Display Patterns](#display-patterns)
10. [Troubleshooting](#troubleshooting)

---

## System Overview

The Pi Zero 2W Medicine Tracking System is a complete e-ink display-based reminder and inventory management solution for medications, vitamins, and supplements.

### Key Features
- ✅ **Time-based reminders** with configurable time windows
- ✅ **Automatic pill inventory tracking** with low-stock alerts
- ✅ **Web-based configuration** via modern UI
- ✅ **Single-button operation** on the device
- ✅ **Multi-medicine rotation** display
- ✅ **Daily tracking** with timestamp logging
- ✅ **Food requirement indicators**
- ✅ **Customizable schedules** (daily, specific days)

### Current State
- **Status:** Fully deployed and operational
- **Web UI:** Running on port 5000 (http://192.168.50.202:5000)
- **Menu System:** Requires reboot to start (GPIO busy issue)
- **Data Storage:** JSON-based with automatic persistence
- **Apps Configured:** 8 total (Weather, MBTA, Disney, Flights, Pomodoro, Medicine, Forbidden, Reboot)

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interfaces                       │
├──────────────────────┬──────────────────────────────────┤
│   Pi Zero Display    │         Web Browser              │
│   (250x122 e-ink)    │    (http://192.168.50.202:5000)  │
└──────────────────────┴──────────────────────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌────────────────────────┐
│   menu_button.py     │    │   web_config.py        │
│   Button Handler     │    │   Flask Web Server     │
└──────────────────────┘    └────────────────────────┘
           │                           │
           ▼                           ▼
┌──────────────────────┐    ┌────────────────────────┐
│  medicine_app.py     │◄───┤  REST API Endpoints    │
│  Display Logic       │    │  /api/medicine/*       │
└──────────────────────┘    └────────────────────────┘
           │                           │
           └───────────┬───────────────┘
                       ▼
           ┌───────────────────────┐
           │   medicine_data.json  │
           │   config.json         │
           └───────────────────────┘
```

### Component Overview

| Component | Type | Purpose | Port/GPIO |
|-----------|------|---------|-----------|
| **menu_button.py** | System Service | App launcher & menu navigation | GPIO 3 |
| **medicine_app.py** | Python App | Medicine reminder display | - |
| **web_config.py** | Flask Server | Configuration web interface | Port 5000 |
| **medicine_data.json** | Data Store | Medicine database & tracking | - |
| **config.json** | Config Store | System-wide configuration | - |
| **epd2in13_V4** | Driver | E-ink display controller | SPI |

---

## Hardware Specifications

### Display
- **Model:** Waveshare 2.13" V4 e-ink display
- **Resolution:** 250 × 122 pixels
- **Color:** 1-bit (black & white)
- **Refresh Modes:**
  - `FULL_UPDATE`: Complete refresh, eliminates ghosting (~2s)
  - `PART_UPDATE`: Partial refresh, faster updates (~0.2s)
- **Interface:** SPI
- **Touch:** Not used in medicine app

### Button
- **GPIO Pin:** 3
- **Pull-up:** Enabled (internal)
- **Bounce Time:** 0.1s
- **Actions:**
  - **Short press (<2s):** Navigate menu / Mark medicines taken
  - **Long press (≥2s):** Select app / Exit app

### System
- **CPU:** Broadcom BCM2710A1 (ARMv8, quad-core 1GHz)
- **RAM:** 512MB
- **OS:** Raspberry Pi OS (Debian-based)
- **Python:** 3.x
- **Network:** WiFi (192.168.50.202)

---

## Application Details

### 1. Weather & Calendar (`weather_cal_app.py`)
**Description:** Displays current weather, time, and date with auto-refresh.

**Features:**
- Current time (HH:MM, 28pt bold)
- Date (Day, Mon DD)
- Weather condition with icon
- Temperature & humidity
- 5-minute auto-refresh

**Config:** `config.json → weather`
- `location`: City name (e.g., "Rio de Janeiro")
- `units`: "metric" or "imperial"
- `update_interval`: Refresh time in seconds (default: 300)
- `display_format`: "detailed" or "simple"

---

### 2. MBTA Transit (`mbta_app.py`)
**Description:** Real-time train arrival predictions for Boston MBTA.

**Features:**
- Morning/evening route switching
- Next 3 train arrivals
- Time-based station selection
- 30-second refresh

**Config:** `config.json → mbta`
- `home_station_id`: MBTA station ID
- `work_station_id`: Destination station ID
- `morning_start`: Morning commute start time
- `evening_start`: Evening commute start time
- `update_interval`: Refresh seconds (default: 30)

---

### 3. Disney Wait Times (`disney_app.py`)
**Description:** Real-time ride wait times for Disney theme parks.

**Features:**
- Rotating ride display
- Wait time in minutes
- Operating status (Open/Closed)
- Sort by wait time or name

**Config:** `config.json → disney`
- `park_id`: Park identifier (6=Magic Kingdom, 5=Epcot, etc.)
- `update_interval`: Seconds per ride (default: 10)
- `data_refresh_rides`: Full data refresh interval (default: 20)
- `sort_by`: "wait_time" or "name"

---

### 4. Flights Above (`flights_app.py`)
**Description:** Aircraft tracking overhead using ADS-B data.

**Features:**
- Flight number/callsign
- Altitude & heading
- Airline information
- Distance from location

**Config:** `config.json → flights`
- `latitude`: Your location latitude
- `longitude`: Your location longitude
- `radius_km`: Detection radius (default: 15)
- `min_altitude`: Minimum altitude filter
- `max_altitude`: Maximum altitude filter

---

### 5. Pomodoro Timer (`pomodoro_app.py`)
**Description:** Productivity timer with work/break cycles.

**Features:**
- Animated tomato character
- Work/break/long break timers
- Session counter
- Auto-transition between states

**Config:** `config.json → pomodoro`
- `work_duration`: Work time in seconds (default: 1500 = 25min)
- `short_break`: Short break seconds (default: 300 = 5min)
- `long_break`: Long break seconds (default: 900 = 15min)
- `sessions_until_long_break`: Cycles before long break (default: 4)

**Button Controls:**
- Click: Start/Pause
- Hold 2s: Exit to menu

---

### 6. Medicine Tracker (`medicine_app.py`) ⭐ NEW
**Description:** Medicine reminder and inventory tracking system.

**Features:**
- Time window-based reminders (Morning/Afternoon/Evening/Night)
- Automatic pill count decrement
- Low stock alerts (red border + "REORDER!" text)
- Multi-medicine rotation (3-second intervals)
- Daily tracking with timestamps
- "With food" indicators
- Custom notes support
- Progress tracking (e.g., "2/3 taken - 67%")

**Display Views:**

1. **Current Reminder View** (when medicines are due):
   ```
   ┌─────────────────────────────────┐
   │ TIME TO TAKE MEDICINE    08:15  │
   │─────────────────────────────────│
   │  💊  Vyvanse - 30mg             │
   │      with food                  │
   │      Pills left: 30             │
   │                                 │
   │      (1/3)                      │
   │─────────────────────────────────│
   │ Click: Mark all 3 taken         │
   └─────────────────────────────────┘
   ```

2. **Schedule View** (when nothing is currently due):
   ```
   ┌─────────────────────────────────┐
   │ Today's Medicines - Nov 6       │
   │─────────────────────────────────│
   │ Morning                         │
   │  [✓] Vitamin D (2000 IU)        │
   │  [✓] Vyvanse (30mg)             │
   │  [✓] Wellbutrin (150mg)         │
   │                                 │
   │ Evening                         │
   │  [ ] Fish Oil (1 cap)           │
   │─────────────────────────────────│
   │ Progress: 3/4 taken (75%)       │
   │ Click: Refresh | Hold: Exit     │
   └─────────────────────────────────┘
   ```

3. **Confirmation View** (after marking taken):
   ```
   ┌─────────────────────────────────┐
   │                                 │
   │        ✓ Marked as Taken!       │
   │                                 │
   │    • Vyvanse (30mg)             │
   │    • Wellbutrin (150mg)         │
   │                                 │
   │    Taken at 08:15               │
   │                                 │
   └─────────────────────────────────┘
   ```

**Time Windows:**
- **Morning:** 6:00-10:00 AM (±30min reminder buffer = 5:30-10:30)
- **Afternoon:** 12:00-4:00 PM (±30min = 11:30-4:30)
- **Evening:** 6:00-10:00 PM (±30min = 5:30-10:30)
- **Night:** 10:00 PM-11:59 PM (±30min = 9:30-12:29)

**Behavior:**
- Checks schedule every 60 seconds
- Rotates between pending medicines every 3 seconds
- Marks ALL pending medicines with single button click
- Decrements pill count automatically
- Shows low stock warning when pills ≤ threshold
- Full refresh on state transitions, partial refresh for updates

**Config:** `config.json → medicine`
- `data_file`: Path to medicine_data.json
- `update_interval`: Check interval seconds (default: 60)
- `reminder_window`: Reminder buffer minutes (default: 30)
- `rotate_interval`: Rotation speed seconds (default: 3)

**Data Model:** See `medicine_data.json` section below

---

### 7. Forbidden Message (`forbidden_app.py`)
**Description:** Displays custom message (user-specific).

**Config:** `config.json → forbidden`
- `message_line1`: First line of text
- `message_line2`: Second line of text
- `display_duration`: Display time in seconds

---

### 8. Reboot System (`reboot_app.py`)
**Description:** Safely reboots the Pi Zero.

**Features:**
- Countdown timer (5 seconds)
- Confirmation screen
- System reboot via `sudo reboot`

---

## User Experience (UX)

### Navigation Flow

```
Power On
   │
   ▼
┌──────────────┐
│  Menu Screen │ ◄─────────────────┐
└──────────────┘                   │
   │                               │
   │ Click: Move Down              │
   │ Hold 2s: Select               │
   ▼                               │
┌──────────────────────┐           │
│  Select App          │           │
│  1. Weather          │           │
│  2. Flights          │           │
│  3. MBTA             │           │
│  4. Disney           │           │
│  5. Pomodoro         │           │
│►6. Medicine Tracker◄─┤           │
│  7. Forbidden        │           │
│  8. Reboot           │           │
└──────────────────────┘           │
   │                               │
   │ Hold 2s on Medicine           │
   ▼                               │
┌──────────────────────┐           │
│  Medicine App        │           │
│  - View Reminders    │           │
│  - Mark Taken        │           │
│  - See Schedule      │           │
└──────────────────────┘           │
   │                               │
   │ Hold 2s: Exit                 │
   └───────────────────────────────┘
```

### Button Interaction Patterns

| Context | Action | Result |
|---------|--------|--------|
| **In Menu** | Click (<2s) | Move to next app |
| **In Menu** | Hold (≥2s) | Launch selected app |
| **In Medicine App (reminder shown)** | Click | Mark all pending medicines as taken |
| **In Medicine App (schedule shown)** | Click | Refresh display |
| **In Any App** | Hold (≥2s) | Exit to menu |

### Visual Design Language

**Typography:**
- **Titles:** Roboto-Bold 12pt
- **Medicine Names:** Roboto-Bold 16pt
- **Dosages:** Roboto-Regular 12pt
- **Body Text:** Roboto-Regular 10pt
- **Time:** Roboto-Bold 12pt

**Icons:**
- **Pill:** Simple ellipse with vertical line
- **Food:** Fork tines (3 vertical lines)
- **Checkmark:** Unicode ✓
- **Warning:** Text "REORDER!"

**Layout:**
- **Top Bar (18px):** Title + Time
- **Main Area (90px):** Content
- **Bottom Bar (14px):** Instructions/Progress

**Spacing:**
- **Margins:** 5-10px
- **Line Height:** 12-14px
- **Section Gaps:** 8-16px

---

## File Structure

```
/home/pizero2w/
├── pizero_apps/
│   ├── config.json                    # System configuration
│   ├── medicine_data.json             # Medicine database & tracking
│   │
│   ├── menu_button.py                 # Main menu system
│   ├── medicine_app.py                # Medicine tracker app
│   ├── weather_cal_app.py             # Weather display
│   ├── mbta_app.py                    # Transit tracker
│   ├── disney_app.py                  # Disney wait times
│   ├── flights_app.py                 # Flight tracker
│   ├── pomodoro_app.py                # Pomodoro timer
│   ├── forbidden_app.py               # Custom message
│   ├── reboot_app.py                  # System reboot
│   │
│   ├── web_config.py                  # Flask web server
│   │
│   └── [backups]
│       ├── config.json.backup.*
│       ├── medicine_data.json.backup.*
│       ├── menu_button.py.backup.*
│       └── web_config.py.backup.*
│
├── python/
│   ├── lib/
│   │   └── TP_lib/
│   │       ├── epd2in13_V4.py        # E-ink driver (V4)
│   │       ├── epd2in13_V3.py        # E-ink driver (V3)
│   │       ├── gt1151.py             # Touch controller
│   │       └── epdconfig.py          # GPIO config
│   │
│   └── pic/
│       ├── Roboto-Bold.ttf
│       ├── Roboto-Regular.ttf
│       └── 2in13/                    # Icon assets
│
└── /tmp/
    ├── webserver.log                  # Web server logs
    └── menu.log                       # Menu system logs
```

---

## Configuration

### config.json Structure

```json
{
  "weather": {
    "location": "Rio de Janeiro",
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
    "latitude": 40.716389,
    "longitude": -73.954167,
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
    "data_file": "/home/pizero2w/pizero_apps/medicine_data.json",
    "update_interval": 60,
    "reminder_window": 30,
    "alert_upcoming_minutes": 15,
    "rotate_interval": 3
  },
  "forbidden": {
    "message_line1": "Custom text",
    "message_line2": "line 2",
    "display_duration": 3,
    "font_size": "large"
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
    "wifi_ssid": "",
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

### medicine_data.json Structure

```json
{
  "medicines": [
    {
      "id": "med_001",
      "name": "Vitamin D",
      "dosage": "2000 IU",
      "time_window": "morning",
      "window_start": "06:00",
      "window_end": "10:00",
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "with_food": true,
      "notes": "Take with breakfast",
      "active": true,
      "color_code": "yellow",
      "pills_remaining": 60,
      "pills_per_dose": 1,
      "low_stock_threshold": 10
    },
    {
      "id": "med_1762467778545",
      "name": "Vyvanse",
      "dosage": "30mg",
      "time_window": "morning",
      "window_start": "06:00",
      "window_end": "10:00",
      "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
      "with_food": true,
      "notes": "",
      "active": true,
      "pills_remaining": 30,
      "pills_per_dose": 1,
      "low_stock_threshold": 7
    }
  ],
  "tracking": {
    "2025-11-06": {
      "med_001_morning": {
        "taken": true,
        "timestamp": "2025-11-06T08:15:00"
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

**Medicine Object Fields:**
- `id`: Unique identifier (auto-generated as "med_" + timestamp)
- `name`: Medicine/vitamin name
- `dosage`: Dosage amount (e.g., "30mg", "2000 IU")
- `time_window`: "morning", "afternoon", "evening", or "night"
- `window_start`: Window start time (HH:MM format)
- `window_end`: Window end time (HH:MM format)
- `days`: Array of active days ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
- `with_food`: Boolean - display food icon if true
- `notes`: Custom notes (optional)
- `active`: Boolean - whether medicine is active
- `pills_remaining`: Current pill count (integer)
- `pills_per_dose`: Pills taken per dose (integer, default: 1)
- `low_stock_threshold`: Alert threshold (integer, default: 10)

**Tracking Object:**
- Key: Date in "YYYY-MM-DD" format
- Value: Object with keys "{medicine_id}_{time_window}"
- Each tracking entry contains:
  - `taken`: Boolean
  - `timestamp`: ISO 8601 timestamp

---

## API Documentation

### Base URL
`http://192.168.50.202:5000`

### Endpoints

#### GET /
**Description:** Serve main web interface
**Response:** HTML page

---

#### GET /api/config
**Description:** Get full system configuration
**Response:**
```json
{
  "weather": {...},
  "mbta": {...},
  "medicine": {...}
}
```

---

#### POST /api/config/{section}
**Description:** Update configuration section
**Parameters:**
- `section`: Config section name (e.g., "weather", "mbta")

**Request Body:** Section configuration object
**Response:**
```json
{
  "success": true,
  "message": "Weather settings saved successfully!"
}
```

---

#### GET /api/medicine/data
**Description:** Get all medicine data
**Response:**
```json
{
  "medicines": [...],
  "tracking": {...},
  "time_windows": {...}
}
```

---

#### POST /api/medicine/add
**Description:** Add new medicine
**Request Body:**
```json
{
  "id": "med_123456789",
  "name": "Aspirin",
  "dosage": "81mg",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "10:00",
  "days": ["mon", "tue", "wed", "thu", "fri"],
  "with_food": false,
  "notes": "For heart health",
  "pills_remaining": 100,
  "pills_per_dose": 1,
  "low_stock_threshold": 15,
  "active": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Medicine added successfully!"
}
```

---

#### POST /api/medicine/update
**Description:** Update existing medicine
**Request Body:** Complete medicine object with same ID
**Response:**
```json
{
  "success": true,
  "message": "Medicine updated successfully!"
}
```

---

#### DELETE /api/medicine/delete/{med_id}
**Description:** Delete medicine by ID
**Parameters:**
- `med_id`: Medicine ID to delete

**Response:**
```json
{
  "success": true,
  "message": "Medicine deleted successfully!"
}
```

---

## Display Patterns

### Refresh Strategy

| Scenario | Refresh Type | Reason |
|----------|--------------|--------|
| App Launch | FULL_UPDATE | Clear previous app content |
| State Change (Reminder → Schedule) | FULL_UPDATE | Major layout change |
| Timer Update (Pomodoro) | PART_UPDATE | Fast updates needed |
| Medicine Rotation | PART_UPDATE | Quick transitions |
| Return to Menu | FULL_UPDATE | Clean slate |

### Text Rendering Best Practices

1. **Font Selection:**
   - Use Roboto family (pre-installed)
   - Bold for emphasis, Regular for body
   - Sizes: 10pt (small), 12pt (body), 16pt (medium), 20pt+ (large)

2. **Text Positioning:**
   - Use `textbbox()` to calculate text width for centering
   - Account for line numbers from `cat -n` format
   - Standard margins: 5px (tight), 10px (normal)

3. **Contrast:**
   - Black text (fill=0) on white background (255)
   - Invert for highlights: white text on black rectangle
   - 2px borders for emphasis

### Layout Grid

```
┌───────────────────────────────────────────┐
│  0px   Title Bar (18px)           250px   │ ← Top
├───────────────────────────────────────────┤
│        Main Content Area                  │
│                                           │ 18-108px
│        (90px height)                      │
│                                           │
├───────────────────────────────────────────┤
│  108px Bottom Bar (14px)          250px   │ ← Bottom
└───────────────────────────────────────────┘
  Total: 122px height
```

---

## Troubleshooting

### Common Issues

#### 1. Menu Not Appearing / GPIO Busy Error

**Symptom:** Menu service fails to start with "GPIO busy" error

**Cause:** GPIO pins not properly released from previous session

**Solution:**
```bash
# Option 1: Reboot
sudo reboot

# Option 2: Kill all Python processes
pkill -9 python3
sleep 2
cd ~/pizero_apps
python3 menu_button.py
```

---

#### 2. Web Server Not Accessible

**Symptom:** Cannot connect to http://192.168.50.202:5000

**Diagnosis:**
```bash
# Check if server is running
ps aux | grep web_config.py

# Check if port is listening
netstat -tulpn | grep 5000
```

**Solution:**
```bash
# Restart web server
pkill -f web_config.py
cd ~/pizero_apps
nohup python3 web_config.py > /tmp/webserver.log 2>&1 &

# Check logs
tail -f /tmp/webserver.log
```

---

#### 3. Medicine Not Appearing in Reminders

**Checklist:**
- [ ] Medicine is marked as `active: true`
- [ ] Current day is in `days` array
- [ ] Current time is within time window ±30min
- [ ] Medicine not already marked as taken today

**Debug:**
```python
# SSH into Pi
ssh pizero2w@192.168.50.202

# Run Python shell
python3
>>> import json
>>> from datetime import datetime
>>> data = json.load(open('/home/pizero2w/pizero_apps/medicine_data.json'))
>>> now = datetime.now()
>>> print(f"Current time: {now.strftime('%H:%M')}")
>>> print(f"Current day: {now.strftime('%a').lower()}")
>>> for med in data['medicines']:
...     print(f"{med['name']}: {med['time_window']} - Active: {med.get('active', True)}")
```

---

#### 4. Pill Count Not Decrementing

**Symptom:** Pills remaining stays same after marking taken

**Cause:** `pills_per_dose` field missing or medicine_data.json not saving

**Solution:**
1. Check medicine has `pills_per_dose` field
2. Verify file permissions:
```bash
ls -la ~/pizero_apps/medicine_data.json
# Should be: -rw-rw-r--
```

3. Manually edit if needed:
```bash
nano ~/pizero_apps/medicine_data.json
```

---

#### 5. Display Ghosting

**Symptom:** Previous image visible on screen

**Cause:** Too many partial updates without full refresh

**Solution:**
```python
# In app code, force full refresh:
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF)
image = draw_your_screen()
epd.displayPartBaseImage(epd.getbuffer(image))
epd.init(epd.PART_UPDATE)  # Back to partial for updates
```

---

### Log Locations

| Service | Log File | Command |
|---------|----------|---------|
| Web Server | `/tmp/webserver.log` | `tail -f /tmp/webserver.log` |
| Menu System | `/tmp/menu.log` | `tail -f /tmp/menu.log` |
| System | `/var/log/syslog` | `tail -f /var/log/syslog` |

---

### Useful Commands

```bash
# Restart all services
sudo systemctl restart pizero-menu  # If using systemd

# Or manually:
pkill -9 python3
cd ~/pizero_apps
python3 menu_button.py &
python3 web_config.py &

# Check system status
ps aux | grep python
netstat -tulpn | grep -E "5000|LISTEN"

# View medicine data
cat ~/pizero_apps/medicine_data.json | python3 -m json.tool

# Backup data
cp ~/pizero_apps/medicine_data.json ~/medicine_data_backup_$(date +%Y%m%d).json

# Check disk space
df -h

# View network config
ip addr show wlan0
```

---

## Web UI Screenshots & Features

### Dashboard
- Navigation sidebar with 8 apps
- Clean card-based layout
- Real-time updates via AJAX

### Medicine Tracker Panel
**Features:**
- Medicine list with visual stock indicators
- Red borders for low stock items
- "⚠️ REORDER SOON!" warnings
- Edit/Delete buttons per medicine
- Add New Medicine form with:
  - Name & Dosage
  - Time Window selector (4 options)
  - Days of week checkboxes
  - With Food toggle
  - Pills Remaining, Per Dose, Alert Threshold
  - Notes field

**Visual Indicators:**
- **Green/Gray Border:** Normal stock
- **Red Border:** Low stock (≤ threshold)
- **Bold Red Text:** "Pills remaining: 8 ⚠️ REORDER SOON!"

---

## Future Enhancements

### Planned Features
- [ ] Email/SMS notifications for low stock
- [ ] Calendar integration (Google Calendar, iCal)
- [ ] Medication adherence reports (weekly/monthly)
- [ ] Export tracking data to CSV
- [ ] Streak counter ("7 days perfect!")
- [ ] Refill reminder scheduling
- [ ] Multiple doses per day for same medicine
- [ ] Barcode scanner for adding medicines
- [ ] Voice confirmation (optional TTS)

### Performance Optimizations
- [ ] Implement display update batching
- [ ] Add caching layer for API responses
- [ ] Optimize partial refresh areas
- [ ] Reduce JSON file reads (in-memory cache)

---

## Developer Notes

### Adding New Medicines via CLI

```bash
# SSH into Pi
ssh pizero2w@192.168.50.202

# Edit medicine_data.json
nano ~/pizero_apps/medicine_data.json

# Add new entry to medicines array:
{
  "id": "med_1234567890",
  "name": "Fish Oil",
  "dosage": "1000mg",
  "time_window": "evening",
  "window_start": "18:00",
  "window_end": "22:00",
  "days": ["mon", "wed", "fri"],
  "with_food": false,
  "notes": "Omega-3 supplement",
  "active": true,
  "pills_remaining": 90,
  "pills_per_dose": 2,
  "low_stock_threshold": 20
}

# Verify JSON syntax
python3 -m json.tool ~/pizero_apps/medicine_data.json > /dev/null && echo "Valid JSON"
```

### Testing Reminder Logic

```python
# Quick test script
import sys
sys.path.append('/home/pizero2w/pizero_apps')
import medicine_app
import json

data = medicine_app.load_medicine_data()
pending = medicine_app.get_pending_medicines(data)

print(f"Pending medicines: {len(pending)}")
for med in pending:
    print(f"  - {med['name']} ({med['dosage']})")
```

---

## Support & Maintenance

### Backup Strategy

**Automated Backups:** Currently manual. Recommended schedule:
- **Daily:** Before making changes
- **Weekly:** Full system backup
- **Before Updates:** Always backup first

**Backup Command:**
```bash
#!/bin/bash
BACKUP_DIR=~/backups/$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp ~/pizero_apps/medicine_data.json $BACKUP_DIR/
cp ~/pizero_apps/config.json $BACKUP_DIR/
echo "Backed up to $BACKUP_DIR"
```

### Restore from Backup

```bash
# List backups
ls -lh ~/backups/

# Restore specific backup
BACKUP_DATE="20251106_143000"
cp ~/backups/$BACKUP_DATE/medicine_data.json ~/pizero_apps/
cp ~/backups/$BACKUP_DATE/config.json ~/pizero_apps/

# Restart services
pkill -f web_config.py
cd ~/pizero_apps && python3 web_config.py &
```

---

## Contact & Documentation

**Project Repository:** (If applicable)
**Web Interface:** http://192.168.50.202:5000
**Device IP:** 192.168.50.202
**SSH Access:** `ssh pizero2w@192.168.50.202`

**Generated:** Claude Code Assistant
**Version:** 1.0
**Last Updated:** November 6, 2025

---

## Appendix A: Complete Medicine Data Example

See `/home/pizero2w/pizero_apps/medicine_data.json` for live data.

Sample complete medicine entry:
```json
{
  "id": "med_1762467778545",
  "name": "Vyvanse",
  "dosage": "30mg",
  "time_window": "morning",
  "window_start": "06:00",
  "window_end": "10:00",
  "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
  "with_food": true,
  "notes": "Take 30 minutes before breakfast",
  "active": true,
  "pills_remaining": 30,
  "pills_per_dose": 1,
  "low_stock_threshold": 7,
  "color_code": "blue"
}
```

## Appendix B: Display Coordinate Reference

```
E-ink Display: 250px × 122px

Safe Zones:
- Left margin: 5px
- Right margin: 245px (5px from edge)
- Top margin: 2px
- Bottom margin: 120px

Font Sizes (Roboto):
- 48pt: Large timer (Pomodoro)
- 28pt: Time display
- 20pt: Headers/Titles
- 16pt: Medicine names
- 14pt: Date
- 12pt: Body text
- 10pt: Small text/notes

Common Y Positions:
- Title bar: 2px
- Title separator: 18px
- Content start: 20px
- Content mid: 60px
- Bottom separator: 100px
- Bottom text: 106px
```

---

**END OF DOCUMENTATION**
