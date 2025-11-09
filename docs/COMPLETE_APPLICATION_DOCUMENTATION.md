# Raspberry Pi Zero 2W E-ink Display Application Suite

## System Overview

A complete single-button operated e-ink display system for Raspberry Pi Zero 2W with Waveshare 2.13" V4 display (122x250 pixels). The system features a main menu and multiple applications, all controlled by a single physical button with short press (navigation) and long press (selection) interactions.

---

## Hardware Setup

- **Device:** Raspberry Pi Zero 2W
- **Display:** Waveshare 2.13" V4 E-ink Display (122x250px, Black & White)
- **Input:** Single physical button (GPIO 3)
- **Optional:** GT1151 touch controller (disabled in button mode)
- **Power:** Standard 5V micro USB

---

## Button Control Scheme

### Universal Controls
- **SHORT PRESS** (< 0.5s): Navigate to next item in current menu/carousel
- **LONG PRESS** (≥ 2s): Select/execute current item

### Navigation Pattern
All menus and carousels follow the same pattern:
```
Item 1 → Item 2 → Item 3 → ... → Item N → (loops back to Item 1)
         ↑                                    ↓
    Short Press                          Short Press
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Systemd Service                      │
│              pizero-menu.service (Auto-start)           │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                   menu_button.py                        │
│              (Main Menu Controller)                     │
│  • Button monitoring (GPIO 3)                          │
│  • App launcher                                         │
│  • E-ink display manager                               │
│  • Button-to-touch conversion (DummyTouch)             │
└─────────────────────────────────────────────────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
                    ▼               ▼
        ┌────────────────┐  ┌────────────────┐
        │   Main Menu    │  │  Individual    │
        │   (5 Apps)     │  │     Apps       │
        └────────────────┘  └────────────────┘
                │                   │
                └───────┬───────────┘
                        │
        ┌───────────────┼───────────────┬──────────────┬─────────────┐
        │               │               │              │             │
        ▼               ▼               ▼              ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│   Medicine   │ │    Disney    │ │ Flights  │ │Forbidden │ │  Reboot  │
│   Tracker    │ │ Wait Times   │ │  Tracker │ │   App    │ │  System  │
└──────────────┘ └──────────────┘ └──────────┘ └──────────┘ └──────────┘
```

---

## Main Menu

### Overview
The main menu is the entry point to all applications. It displays on boot and when exiting any app.

### Menu Items (In Order)
1. **Medicine Tracker** - Daily medication management
2. **Disney Wait Times** - Magic Kingdom ride wait times
3. **Flights Above Me** - Real-time overhead flight tracking
4. **Sai Curioso** - Locked/Forbidden access message
5. **Reboot System** - System restart with confirmation

### Navigation
```
Medicine Tracker → Disney Wait Times → Flights Above Me → Sai Curioso → Reboot System
        ↑                                                                      ↓
        └──────────────────────────────────────────────────────────────────────┘
                              (Short press cycles through)
```

**Actions:**
- **Short Press:** Navigate to next app
- **Long Press:** Launch selected app

---

## Application 1: Medicine Tracker

### Purpose
Daily medication adherence tracking with carousel-based navigation. Manage medicines, track doses, view history, and monitor adherence statistics.

### Features
- Daily medicine carousel (shows only untaken medicines)
- Quick take/skip actions
- Skip reason tracking
- Pending doses view
- Skip history (last 10 events)
- 7-day adherence statistics
- Automatic removal from carousel when marked as taken

### Navigation Structure

```
┌─────────────────────────────────────────────────────────┐
│              MEDICINE CAROUSEL (Main View)              │
│                                                         │
│  MENU → Medicine 1 → Medicine 2 → ... → EXIT           │
│    ↓                                        ↓           │
│  (Long)                                  (Long)         │
│    ↓                                        ↓           │
│  Menu Options                          Exit App        │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼
        ┌──────────────────────┐
        │    MENU OPTIONS      │
        │                      │
        │  Pending Doses  →    │
        │  Skip History   →    │
        │  Adherence      →    │
        │  Back           →    │
        └──────────────────────┘
                │
        ┌───────┼───────┬───────┐
        │       │       │       │
        ▼       ▼       ▼       ▼
    Pending  History  Stats   Back to
     View     View    View   Medicines
```

### Detailed Navigation

#### 1. Medicine Carousel (Main Screen)
**Display:** Shows one medicine at a time with details
- Medicine name with 💊 icon
- Dosage (e.g., "150mg tablet")
- Pills remaining (with ⚠️ LOW warning if < threshold)
- Time window (e.g., "Morning (06:00-12:00)")

**Carousel Order:**
```
⚙️ MENU → 💊 Medicine 1 → 💊 Medicine 2 → ... → 🚪 EXIT
```

**Actions:**
- **Short Press:** Navigate to next item (MENU → Meds → EXIT → MENU)
- **Long Press on MENU:** Enter Menu Options
- **Long Press on Medicine:** Open action menu for that medicine
- **Long Press on EXIT:** Exit to main system menu

**Notes:**
- Only shows medicines not yet taken today
- Automatically reloads after marking medicine taken/skipped
- If all medicines taken: Shows "✓ All Done! No medicines due today"

---

#### 2. Action Menu (For Selected Medicine)
**Display:** Large centered action with icon
- ✓ TAKE NOW
- ⏭️ SKIP
- ← BACK

**Actions:**
- **Short Press:** Cycle through actions
- **Long Press on "Take Now":** Mark medicine as taken → show confirmation → return to carousel
- **Long Press on "Skip":** Enter skip reason selector
- **Long Press on "Back":** Return to medicine carousel

**Confirmation Screen:**
Shows for 2 seconds after successful action:
```
✓ [MEDICINE NAME] TAKEN

[Pills Remaining] pills remaining
Logged: 11/09 02:30 PM

[Returning to list...]
```

---

#### 3. Skip Reason Selector
**Display:** Reason with emoji
- 😴 FORGOT
- 🤢 SIDE EFFECTS
- 📦 OUT OF STOCK
- 🏥 DOCTOR ADVISED
- ❓ OTHER
- ← BACK

**Actions:**
- **Short Press:** Cycle through reasons
- **Long Press on Reason:** Record skip with that reason → show confirmation → return to carousel
- **Long Press on "Back":** Return to action menu

---

#### 4. Menu Options
**Display:** Large centered option with icon
- 📋 PENDING DOSES
- ⏭️ SKIP HISTORY
- 📊 ADHERENCE
- ← BACK

**Actions:**
- **Short Press:** Cycle through options
- **Long Press:** Enter selected view
- **Long Press on "Back":** Return to medicine carousel

---

#### 5. Pending Doses View
**Purpose:** View all medicines due today (within time window)

**Display:** Shows one medicine at a time:
- 💊 Medicine name
- Dosage
- Time window

**Carousel:**
```
Medicine 1 → Medicine 2 → ... → ← BACK
```

**Actions:**
- **Short Press:** Navigate through pending medicines
- **Long Press on Medicine:** Open action menu for that medicine (can take/skip from here)
- **Long Press on BACK:** Return to menu options

---

#### 6. Skip History View
**Purpose:** Review last 10 skip events

**Display:** Shows one skip event at a time:
- ⏭️ Medicine name
- Dosage
- Date: MM/DD/YYYY
- Reason: [reason text]

**Carousel:**
```
Skip 1 → Skip 2 → ... → Skip 10 → ← BACK
```

**Actions:**
- **Short Press:** Navigate through skip history
- **Long Press on BACK:** Return to menu options

**Note:** If no skips recorded, shows "No skips recorded"

---

#### 7. Adherence Stats View
**Purpose:** View 7-day adherence statistics

**Display:**
```
ADHERENCE STATS
───────────────
Last 7 Days: 85%

Taken: 12 | Skipped: 2
Pending: 3
```

**Carousel:**
```
Overall Stats → ← BACK
```

**Actions:**
- **Short Press:** Toggle between Overall and BACK
- **Long Press on BACK:** Return to menu options

---

### Medicine Database

**Storage:** SQLite database at `/home/pizero2w/pizero_apps/db/medicine.db`

**Managed via Web UI:** `http://192.168.50.202:5000`

**Medicine Properties:**
- Name
- Dosage (e.g., "150mg tablet")
- Pills per dose
- Pills remaining (auto-decremented when taken)
- Low stock threshold
- Time window (morning/afternoon/evening/night/anytime)
- Window start/end times
- Active status

**Tracking Data:**
- Date
- Taken (boolean)
- Skipped (boolean)
- Skip reason
- Timestamp

---

## Application 2: Disney Wait Times

### Purpose
Display current wait times for rides at Magic Kingdom theme park.

### Features
- Live wait time data from Disney API
- Themed backgrounds
- Ride cycling through carousel
- Auto-refresh every 5 minutes

### Navigation
```
Ride 1 → Ride 2 → Ride 3 → ... → Ride N
  ↑                                  ↓
  └──────────────────────────────────┘
```

**Display Format:**
```
[Ride Name]
Wait: [XX] minutes
Status: [Operating/Closed/Down]
```

**Actions:**
- **Short Press:** Next ride
- **Long Press:** Exit to main menu

**Special States:**
- **Down:** Shows ⚠️ icon
- **Closed:** Shows different message
- **No data:** Shows "Data unavailable"

---

## Application 3: Flights Above Me

### Purpose
Real-time tracking of aircraft flying overhead using FlightRadar24 API.

### Features
- Detects flights within configurable radius (default 15km)
- Shows flight details: callsign, altitude, speed, aircraft type
- Compass bearing indicator
- Aviation quotes when no flights detected
- Auto-refresh every 30 seconds

### Display Format

**When Flight Detected:**
```
✈️ [CALLSIGN]

From: [ORIGIN]
To: [DESTINATION]

Alt: [ALTITUDE] ft
Speed: [SPEED] kts
Type: [AIRCRAFT]

Bearing: [N/NE/E/SE/S/SW/W/NW]
[Compass diagram]
```

**When No Flights:**
```
No flights overhead

[Random aviation quote]

Example: "The engine is the heart of an
          airplane, but the pilot is its soul."
```

**Actions:**
- **Short Press:** Refresh data immediately
- **Long Press:** Exit to main menu

**Configuration:**
- Location: 40.716389, -73.954167 (configurable)
- Radius: 15km
- Update interval: 30 seconds

---

## Application 4: Sai Curioso (Forbidden App)

### Purpose
Displays a "forbidden access" message - a placeholder/easter egg app.

### Display
```
🚫

Access Forbidden

Access Denied
```

**Actions:**
- **Any button press:** Exit to main menu

**Configuration:**
- Messages customizable via config file
- Uses display components library for centered text

---

## Application 5: Reboot System

### Purpose
Safe system reboot with confirmation dialog.

### Features
- Two-option selection: Cancel / Reboot
- Default selection: Cancel (safe)
- Visual selection indicator (►)
- Prevents accidental reboots

### Display
```
Reboot System?

► Cancel    Reboot

SHORT PRESS: Toggle
LONG PRESS: Confirm
```

**Navigation:**
```
► Cancel  ⇄  Reboot ◄
```

**Actions:**
- **Short Press:** Toggle selection between Cancel/Reboot
- **Long Press on Cancel:** Return to main menu (no action)
- **Long Press on Reboot:** Execute `sudo reboot` immediately

**Safety Features:**
- Default selection is Cancel
- Clear visual indicator of current selection
- Two-step process (select + confirm)

---

## Web Configuration Interface

### Access
**URL:** `http://192.168.50.202:5000`
**Service:** `web_config.py` (runs automatically)

### Features

#### Medicine Management
- Add new medicines
- Edit existing medicines (name, dosage, schedule, stock)
- Activate/deactivate medicines
- View all medicines in table format
- Set low stock thresholds
- Configure time windows

#### Password Management
- Change system password
- Secure authentication required

#### System Information
- View system status
- Monitor service health

---

## Technical Architecture

### Shared Components

#### 1. Display Library (`display/`)
- **fonts.py:** Font presets (title, body, subtitle, mono)
- **components.py:** Reusable UI components (Button, MessageBox)
- **text.py:** Text rendering utilities (centering, truncation, wrapping)
- **canvas.py:** Drawing utilities
- **input_handler.py:** Unified input abstraction (touch/button modes)

#### 2. Shared Utilities (`shared/`)
- **app_utils.py:**
  - ConfigLoader: YAML configuration management
  - Logging setup
  - Signal handlers (graceful shutdown)
  - Path setup
  - Exit request checking

#### 3. Database (`db/`)
- **medicine_db.py:** SQLite ORM for medicine tracking
  - ACID transactions
  - Schema migrations
  - Medicine CRUD operations
  - Tracking history management
  - Adherence calculations

#### 4. TP_lib (Waveshare Library)
- **epd2in13_V4.py:** E-ink display driver
  - Full update mode (complete refresh)
  - Partial update mode (fast refresh, reduces ghosting)
- **gt1151.py:** Touch controller driver (disabled in button mode)
- **epdconfig.py:** GPIO and hardware configuration

### Button-to-Touch Conversion

The system uses a clever pattern to support both touch and button modes:

1. **menu_button.py** owns GPIO 3 (the physical button)
2. Creates `DummyTouch` objects that simulate touch events
3. Sets `TouchpointFlag`:
   - `0` = no press
   - `1` = short press
   - `2` = long press
4. Apps poll `TouchpointFlag` in their main loop
5. Apps call button handlers based on flag value

This allows apps to use unified input handling code regardless of input method.

---

## File Structure

```
/home/pizero2w/pizero_apps/
│
├── menu_button.py              # Main menu controller & launcher
│
├── medicine_app_carousel.py    # Medicine tracker (carousel UI)
├── disney_app.py               # Disney wait times
├── flights_app.py              # Flight tracker
├── forbidden_app.py            # Forbidden access message
├── reboot_app.py               # System reboot
│
├── web_config.py               # Web configuration interface
│
├── db/
│   ├── medicine_db.py          # Medicine database ORM
│   └── medicine.db             # SQLite database
│
├── display/
│   ├── fonts.py                # Font utilities
│   ├── components.py           # UI components
│   ├── text.py                 # Text rendering
│   ├── canvas.py               # Drawing utilities
│   └── input_handler.py        # Input abstraction
│
├── shared/
│   └── app_utils.py            # Shared utilities
│
├── TP_lib/                     # Waveshare library
│   ├── epd2in13_V4.py          # Display driver
│   ├── gt1151.py               # Touch controller
│   └── epdconfig.py            # GPIO config
│
└── config/
    └── config.yaml             # Application configuration
```

---

## Service Management

### Systemd Service
**Service:** `pizero-menu.service`
**Location:** `/etc/systemd/system/pizero-menu.service`

**Commands:**
```bash
# Start service
sudo systemctl start pizero-menu.service

# Stop service
sudo systemctl stop pizero-menu.service

# Restart service (reload code changes)
sudo systemctl restart pizero-menu.service

# View status
sudo systemctl status pizero-menu.service

# View logs
journalctl -u pizero-menu.service -f

# Enable auto-start on boot
sudo systemctl enable pizero-menu.service
```

### Service Configuration
```ini
[Unit]
Description=PiZero E-ink Button Menu (Refactored)
After=network.target

[Service]
Type=simple
User=pizero2w
WorkingDirectory=/home/pizero2w/pizero_apps
ExecStart=/usr/bin/python3 /home/pizero2w/pizero_apps/menu_button.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## Configuration

### Main Config File
**Location:** `/home/pizero2w/pizero_apps/config/config.yaml`

**Structure:**
```yaml
medicine:
  update_interval: 60  # Auto-refresh interval (seconds)
  db_path: "db/medicine.db"

flights:
  latitude: 40.716389
  longitude: -73.954167
  radius: 15  # km
  update_interval: 30

disney:
  update_interval: 300  # 5 minutes

forbidden:
  message_line1: "Access Forbidden"
  message_line2: "Access Denied"

display:
  width: 122
  height: 250
  refresh_mode: "partial"  # or "full"

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

---

## Display Optimization

### E-ink Characteristics
- **Resolution:** 122x250 pixels (portrait)
- **Colors:** Black & White only
- **Refresh Time:**
  - Full: ~2 seconds (complete refresh, eliminates ghosting)
  - Partial: ~0.3 seconds (fast, may cause ghosting over time)

### Optimization Techniques
1. **Partial Updates:** Used for frequent changes (medicine carousel, flight updates)
2. **Full Updates:** Used on app launch and periodically to clear ghosting
3. **Base Image:** Set with `displayPartBaseImage()` before partial updates
4. **Minimal Redraws:** Only redraw when data changes

### Font Presets
- **Title:** 14pt bold (headers, medicine names)
- **Body:** 11pt regular (details, descriptions)
- **Subtitle:** 9pt regular (hints, status text)
- **Mono:** 10pt monospace (data display)

---

## User Workflows

### Daily Medicine Routine

**Morning Scenario:**
1. System shows medicine carousel on wake
2. User navigates (short press) to first medicine
3. Long press → Action Menu
4. Long press "Take Now"
5. Confirmation shows, medicine removed from carousel
6. Repeat for other medicines
7. When done: Navigate to EXIT, long press to leave

**Skipping Medicine:**
1. Navigate to medicine
2. Long press → Action Menu
3. Navigate to "Skip"
4. Long press → Skip Reason menu
5. Navigate to reason (e.g., "Side effects")
6. Long press → Confirm skip
7. Medicine removed from carousel

**Checking Adherence:**
1. Navigate to MENU, long press
2. Navigate to "Adherence", long press
3. View 7-day stats
4. Short press to cycle to BACK
5. Long press to return

---

### Checking Flights Overhead

1. From main menu, navigate to "Flights Above Me"
2. Long press to launch
3. View current overhead flights (auto-refreshes every 30s)
4. Short press to manually refresh
5. Long press to exit

---

### Planning Disney Visit

1. Navigate to "Disney Wait Times"
2. Long press to launch
3. View current ride wait times
4. Short press to cycle through rides
5. Note shortest waits for visit planning
6. Long press to exit

---

## Troubleshooting

### Display Issues

**Problem:** Display shows blank/white screen
- **Solution:** Check EPD initialization, ensure full update mode used on first render

**Problem:** Ghosting/artifacts on screen
- **Solution:** Run full update mode to clear, use `epd.init(epd.FULL_UPDATE)`

**Problem:** Display not updating
- **Solution:** Check service status, restart pizero-menu.service

### Button Issues

**Problem:** Button not responding
- **Solution:** Check GPIO 3 connection, verify not claimed by another process

**Problem:** Long press triggers immediately
- **Solution:** Adjust `bounce_time` in menu_button.py (default 0.1s)

**Problem:** App exits on long press instead of selecting
- **Solution:** Check `handle_long_press_internally` flag is set in app

### App Issues

**Problem:** Medicine not showing in carousel
- **Solution:** Check if already marked as taken today, verify active status in web UI

**Problem:** Medicine carousel shows "All Done" but medicines remain
- **Solution:** Check database tracking table, verify date format

**Problem:** Flights showing no data
- **Solution:** Check internet connection, verify FlightRadar24 API access

**Problem:** Disney wait times not updating
- **Solution:** Check Disney API access, verify update interval

### Database Issues

**Problem:** Cannot add medicine via web UI
- **Solution:** Check database permissions, verify medicine.db writable

**Problem:** Tracking data not saving
- **Solution:** Check database connection, verify ACID transaction completion

---

## Development Notes

### Adding New Apps

1. Create new Python file in `/home/pizero2w/pizero_apps/`
2. Implement `run_[appname]_app(epd, GT_Dev, GT_Old, gt)` function
3. Add to `APPS` list in `menu_button.py`
4. Use shared components and utilities
5. Follow button control scheme
6. Test thoroughly before deployment

### Code Conventions

- Use shared display components for consistency
- Follow button-to-touch conversion pattern
- Implement graceful shutdown (signal handlers)
- Use ConfigLoader for settings
- Log important events
- Handle errors gracefully
- Use partial updates for frequent changes
- Clear display on exit

---

## API Dependencies

### External APIs Used
1. **FlightRadar24:** Flight tracking data
2. **Disney API:** Wait time data (unofficial)

### Rate Limiting
- Flights: 30-second intervals (120 requests/hour)
- Disney: 5-minute intervals (12 requests/hour)

---

## Future Enhancements

### Planned Features
- Weather app
- Calendar/agenda view
- Package tracking
- News headlines
- Music player controls

### Possible Improvements
- Per-medicine adherence breakdown (stats view)
- Button debouncing improvements
- Error recovery mechanisms
- Offline mode for apps
- User profiles for medicine tracking

---

## Credits

**Hardware:**
- Raspberry Pi Zero 2W
- Waveshare 2.13" V4 E-ink Display
- Waveshare Touch Hat (disabled in button mode)

**Software:**
- Python 3.x
- Waveshare EPD library
- FlightRadar24 API
- Custom display/shared libraries

**Development:**
- Single-button UX design
- Carousel navigation pattern
- ACID database transactions
- Unified input handling

---

## Version History

**v2.0 (Current) - Medicine Carousel Refactor**
- Complete rewrite of medicine app with carousel UI
- Single-button navigation throughout
- Fixed all critical navigation bugs
- Added EXIT to medicine carousel
- Simplified menu options
- 100% functional with comprehensive testing

**v1.x - Initial Release**
- Touch-based navigation
- Basic medicine tracking
- Flight and Disney apps
- Web configuration interface

---

**Last Updated:** November 9, 2025
**System Location:** Raspberry Pi Zero 2W @ 192.168.50.202
**Documentation:** Complete and production-ready
