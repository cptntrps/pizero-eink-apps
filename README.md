# PiZero E-ink Apps

Raspberry Pi Zero 2W E-ink Display Application Suite with single-button navigation.

## 🎯 Overview

Complete application suite for Waveshare 2.13" V4 e-ink display, controlled by a single physical button. Features medicine tracking, flight monitoring, Disney wait times, and system utilities.

## 🔧 Hardware

- **Device:** Raspberry Pi Zero 2W
- **Display:** Waveshare 2.13" V4 E-ink (122x250px, B&W)
- **Input:** Single button (GPIO 3)
- **Control:** Short press (navigate), Long press ≥2s (select)

## 📱 Applications

### 1. Medicine Tracker
Daily medication adherence tracking with carousel navigation.
- ✅ Mark medicines as taken/skipped
- 📊 7-day adherence statistics
- 📋 Pending doses view
- ⏭️ Skip history (last 10 events)
- 🌐 Web UI for medicine management (http://192.168.50.202:5000)

### 2. Disney Wait Times
Live Magic Kingdom ride wait times from Disney API.

### 3. Flights Above Me
Real-time overhead flight tracking using FlightRadar24 API.
- ✈️ Flight details (callsign, altitude, speed, aircraft type)
- 🧭 Compass bearing indicator
- 📍 Configurable location and radius

### 4. Sai Curioso
Forbidden access message (Easter egg/placeholder).

### 5. Reboot System
Safe system reboot with confirmation dialog.

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/cptntrps/pizero-eink-apps.git
cd pizero-eink-apps
```

### 2. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configure Service
```bash
sudo cp pizero-menu.service /etc/systemd/system/
sudo systemctl enable pizero-menu.service
sudo systemctl start pizero-menu.service
```

### 4. Access Web UI
Open http://[PI_IP]:5000 to manage medicines.

## 📖 Navigation

### Universal Controls
- **Short Press:** Navigate to next item
- **Long Press (≥2s):** Select/execute current item

### Medicine App Navigation
```
Medicine Carousel: MENU → Med1 → Med2 → ... → EXIT
                    ↓                            ↓
                 Menu Options                Exit App
                    ↓
         Pending → History → Stats → Back
```

## 🗂️ Project Structure

```
pizero_apps/
├── menu_button.py              # Main menu controller
├── medicine_app_carousel.py    # Medicine tracker
├── disney_app.py               # Disney wait times
├── flights_app.py              # Flight tracker  
├── forbidden_app.py            # Forbidden message
├── reboot_app.py               # System reboot
├── web_config.py               # Web configuration interface
├── db/
│   ├── medicine_db.py          # Database ORM
│   └── medicine.db             # SQLite database
├── display/                    # Display utilities
├── shared/                     # Shared utilities
└── TP_lib/                     # Waveshare library
```

## ⚙️ Configuration

Edit `config/config.yaml`:

```yaml
medicine:
  update_interval: 60
  db_path: "db/medicine.db"

flights:
  latitude: 40.716389
  longitude: -73.954167
  radius: 15  # km
  update_interval: 30

disney:
  update_interval: 300  # 5 minutes
```

## 🛠️ Service Management

```bash
# Restart service (after code changes)
sudo systemctl restart pizero-menu.service

# View logs
journalctl -u pizero-menu.service -f

# Check status
sudo systemctl status pizero-menu.service
```

## 🐛 Troubleshooting

### Display Issues
- **Blank screen:** Check EPD initialization, restart service
- **Ghosting:** Use full update mode: `epd.init(epd.FULL_UPDATE)`

### Button Issues
- **Not responding:** Check GPIO 3, verify service running
- **Exit on long press:** Verify `handle_long_press_internally` flag set

### Medicine App
- **Not showing:** Check if marked as taken today, verify active status
- **Not updating:** Check database permissions, restart service

## 📚 Documentation

Complete documentation available in `docs/COMPLETE_APPLICATION_DOCUMENTATION.md`

## 🔄 Development

### Adding New Apps

1. Create `your_app.py` with `run_your_app(epd, GT_Dev, GT_Old, gt)` function
2. Add to `APPS` list in `menu_button.py`
3. Follow button control scheme (short press = navigate, long press = select)
4. Use shared display components
5. Test thoroughly

### Code Conventions
- Use shared components (`display/`, `shared/`)
- Follow button-to-touch conversion pattern  
- Implement graceful shutdown (signal handlers)
- Use partial updates for frequent changes
- Clear display on exit

## 📄 License

MIT License - See LICENSE file

## 👤 Author

cptntrps

## 🙏 Credits

- Waveshare EPD library
- FlightRadar24 API
- Disney API (unofficial)

---

**Last Updated:** November 9, 2025  
**Version:** 2.0 (Medicine Carousel Refactor)  
**Status:** Production Ready ✅
