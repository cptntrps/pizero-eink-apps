# Pi Zero 2W Medicine Tracker - Deployment Guide

**Version:** 1.0
**Last Updated:** November 8, 2025
**Target Platform:** Raspberry Pi Zero 2W with Waveshare 2.13" V4 e-ink display

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Verification](#verification)
5. [First Run](#first-run)
6. [Post-Deployment Configuration](#post-deployment-configuration)
7. [Service Management](#service-management)
8. [Backup Strategy](#backup-strategy)

---

## Pre-Deployment Checklist

Before starting deployment, verify the following:

- [ ] Raspberry Pi Zero 2W is available
- [ ] Waveshare 2.13" V4 e-ink display purchased and compatible
- [ ] MicroSD card (16GB minimum recommended)
- [ ] USB power supply (2.5A minimum)
- [ ] Raspberry Pi OS installed on MicroSD card
- [ ] GPIO pin 3 available for button control
- [ ] SPI interface enabled on Raspberry Pi
- [ ] Network connectivity (WiFi or Ethernet)
- [ ] SSH access available
- [ ] Python 3.7+ installed

---

## System Requirements

### Hardware

| Component | Specification | Notes |
|-----------|---------------|-------|
| **SBC** | Raspberry Pi Zero 2W | ARMv8, 512MB RAM, quad-core 1GHz |
| **Display** | Waveshare 2.13" V4 e-ink | 250×122px, 1-bit color, SPI interface |
| **Button** | Standard momentary switch | Connected to GPIO pin 3 |
| **Storage** | MicroSD card | 16GB minimum recommended |
| **Power** | USB micro power | 2.5A minimum |
| **Network** | WiFi | 802.11b/g/n |

### Software

| Requirement | Version | Purpose |
|------------|---------|---------|
| **OS** | Raspberry Pi OS (Lite or Desktop) | Base operating system |
| **Python** | 3.7+ (3.9+ recommended) | Runtime environment |
| **pip** | Latest | Package manager |
| **Flask** | 2.0.0+ | Web server framework |
| **Pillow** | 8.0.0+ | Image processing |
| **gpiozero** | 1.6.2+ | GPIO control library |
| **marshmallow** | 3.14.0+ | Data validation |

### System Permissions

- Python must run with GPIO access (may require `sudo`)
- User must have read/write access to application directory
- Port 5000 must be available for web server

---

## Installation Steps

### Step 1: Prepare the Raspberry Pi

1. **Flash Raspberry Pi OS:**
   ```bash
   # Use Raspberry Pi Imager or dd command
   # Boot with default credentials: pi/raspberry
   ```

2. **Enable Required Interfaces:**
   ```bash
   sudo raspi-config
   # Navigate to: Interfacing Options → SPI → Enable
   # Navigate to: Interfacing Options → GPIO → Enable
   # Select Finish and reboot
   ```

3. **Update System:**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   sudo apt-get install -y python3-pip python3-dev git
   ```

### Step 2: Create Application Directory

```bash
# Create directory structure
mkdir -p ~/pizero_apps
cd ~/pizero_apps

# Set permissions
chmod 755 ~/pizero_apps
```

### Step 3: Clone or Copy Project Files

**Option A: Clone from Repository**
```bash
cd ~
git clone <repository-url> pizero_apps
cd pizero_apps
```

**Option B: Copy from USB or Network**
```bash
# Using scp
scp -r /local/path/to/project pi@192.168.x.x:~/pizero_apps

# Or copy files manually to ~/pizero_apps
```

### Step 4: Install Python Dependencies

```bash
cd ~/pizero_apps

# Install from requirements.txt
pip3 install -r requirements.txt

# Verify installation
python3 -c "import flask, PIL, gpiozero; print('All dependencies OK')"
```

### Step 5: Install Display Driver

The display driver should be included in the project. If not:

```bash
# Create driver directory if it doesn't exist
mkdir -p ~/python/lib/TP_lib
cd ~/python/lib/TP_lib

# Copy or download Waveshare drivers
# Ensure epd2in13_V4.py, epdconfig.py, etc. are present
```

### Step 6: Create and Configure Data Files

```bash
# Create medicine data file
cat > ~/pizero_apps/medicine_data.json << 'EOF'
{
  "medicines": [],
  "tracking": {},
  "time_windows": {
    "morning": {"start": "06:00", "end": "10:00"},
    "afternoon": {"start": "12:00", "end": "16:00"},
    "evening": {"start": "18:00", "end": "22:00"},
    "night": {"start": "22:00", "end": "23:59"}
  }
}
EOF

# Verify config.json exists and is valid
python3 -m json.tool config.json > /dev/null && echo "config.json is valid"

# Set file permissions
chmod 664 medicine_data.json config.json
```

### Step 7: Create systemd Service Files (Optional)

**For Web Server:**
```bash
sudo tee /etc/systemd/system/pizero-webui.service > /dev/null << 'EOF'
[Unit]
Description=Pi Zero Web Configuration Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/pizero_apps
ExecStart=/usr/bin/python3 /home/pi/pizero_apps/web_config.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable pizero-webui
```

**For Menu System:**
```bash
sudo tee /etc/systemd/system/pizero-menu.service > /dev/null << 'EOF'
[Unit]
Description=Pi Zero Menu Button Handler
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/pizero_apps
ExecStart=/usr/bin/python3 /home/pi/pizero_apps/menu_button.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable pizero-menu
```

### Step 8: Test Display Connection

```bash
# Create simple test script
python3 << 'EOF'
import sys
sys.path.append('/home/pi/python/lib')

try:
    from TP_lib import epd2in13_V4
    epd = epd2in13_V4.EPD()
    print(f"Display initialized: {epd.width}x{epd.height}")
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    print("Display test successful!")
except Exception as e:
    print(f"Display error: {e}")
    sys.exit(1)
EOF
```

### Step 9: Test GPIO Button

```bash
# Create GPIO test script
python3 << 'EOF'
from gpiozero import Button
import time

try:
    button = Button(3)  # GPIO pin 3
    print("GPIO initialized successfully")
    print("Press button to test (will exit after 10 seconds)...")

    for i in range(10):
        if button.is_pressed:
            print(f"Button pressed at {time.time()}")
        time.sleep(1)
    print("GPIO test complete!")
except Exception as e:
    print(f"GPIO error: {e}")
EOF
```

### Step 10: Start Services

```bash
# If using systemd services:
sudo systemctl start pizero-webui
sudo systemctl start pizero-menu

# Or manually:
cd ~/pizero_apps
nohup python3 web_config.py > /tmp/webserver.log 2>&1 &
nohup python3 menu_button.py > /tmp/menu.log 2>&1 &

# Verify processes
ps aux | grep python3
```

---

## Verification

### Check Installation

```bash
# 1. Verify all files are in place
ls -la ~/pizero_apps/
# Should see: config.json, medicine_data.json, *.py files

# 2. Verify Python packages
pip3 list | grep -E "Flask|Pillow|gpiozero"

# 3. Check JSON files
python3 -m json.tool ~/pizero_apps/config.json > /dev/null && echo "config.json OK"
python3 -m json.tool ~/pizero_apps/medicine_data.json > /dev/null && echo "medicine_data.json OK"

# 4. Verify permissions
ls -la ~/pizero_apps/*.json
# Should show: -rw-rw-r-- or similar
```

### Check Services

```bash
# Via systemd
sudo systemctl status pizero-webui
sudo systemctl status pizero-menu

# Via manual processes
ps aux | grep web_config.py
ps aux | grep menu_button.py

# Check port 5000
netstat -tulpn | grep 5000
# Should show: tcp 0.0.0.0:5000 LISTEN
```

### Test Web Interface

```bash
# Find Pi's IP address
hostname -I

# From another computer, open browser:
# http://<pi-ip-address>:5000

# Or test via curl:
curl http://localhost:5000/
# Should return HTML content
```

---

## First Run

### Initial Setup

1. **Access Web Interface:**
   - Open browser to `http://<pi-ip>:5000`
   - You should see the dashboard

2. **Add First Medicine:**
   - Click "Add New Medicine" in the Medicine section
   - Fill in details:
     - Name: "Vitamin D"
     - Dosage: "2000 IU"
     - Time Window: "Morning"
     - Days: Select all days
     - Pills Remaining: 60
   - Click Save

3. **Test Display:**
   - Press the button on the Pi
   - Select "Medicine" from menu
   - Display should show today's medicines
   - Press button to mark as taken (should see confirmation)

4. **Test Menu Navigation:**
   - Short press: Move between apps
   - Long press (2+ seconds): Launch app
   - While in app, long press to exit

### Verify All Components

```bash
# Check display updates
tail -f /tmp/menu.log  # Menu logs

# Check web server
tail -f /tmp/webserver.log  # Web server logs

# Monitor system
top
# Check CPU and memory usage
```

---

## Post-Deployment Configuration

### Configure Weather Settings

1. Edit `/home/pi/pizero_apps/config.json`
2. Update weather section:
   ```json
   "weather": {
     "location": "Your City",
     "units": "metric",
     "update_interval": 300
   }
   ```

### Configure MBTA (Boston Transit)

```json
"mbta": {
  "home_station_id": "place-davis",
  "work_station_id": "place-pktrm",
  "morning_start": "06:00",
  "evening_start": "15:00",
  "update_interval": 30
}
```

### Configure System Settings

```json
"system": {
  "wifi_ssid": "Your WiFi SSID",
  "timezone": "America/New_York",
  "display_brightness": 100
}
```

See [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) for all options.

---

## Service Management

### Starting Services

```bash
# Using systemd
sudo systemctl start pizero-webui
sudo systemctl start pizero-menu

# Manually (one-time run)
cd ~/pizero_apps
python3 web_config.py &
python3 menu_button.py &
```

### Stopping Services

```bash
# Using systemd
sudo systemctl stop pizero-webui
sudo systemctl stop pizero-menu

# Manually
pkill -f web_config.py
pkill -f menu_button.py
```

### Checking Status

```bash
# Via systemd
sudo systemctl status pizero-webui
sudo systemctl status pizero-menu

# Via processes
ps aux | grep python3

# View logs
sudo journalctl -u pizero-webui -f
sudo journalctl -u pizero-menu -f
```

### Auto-Start on Boot

```bash
# Enable services at startup
sudo systemctl enable pizero-webui
sudo systemctl enable pizero-menu

# Disable auto-start
sudo systemctl disable pizero-webui
sudo systemctl disable pizero-menu
```

### Restart Services

```bash
# Individual services
sudo systemctl restart pizero-webui

# All services
sudo systemctl restart pizero-webui pizero-menu

# Hard restart (kill processes)
pkill -9 python3
sleep 2
cd ~/pizero_apps && python3 web_config.py &
cd ~/pizero_apps && python3 menu_button.py &
```

---

## Backup Strategy

### Automatic Backup Script

Create `/home/pi/backup_medicines.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/pi/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup data files
cp /home/pi/pizero_apps/medicine_data.json "$BACKUP_DIR/"
cp /home/pi/pizero_apps/config.json "$BACKUP_DIR/"

# Backup web config
cp /home/pi/pizero_apps/web_config.py "$BACKUP_DIR/"

# Keep only last 30 days
find /home/pi/backups -type d -mtime +30 -exec rm -rf {} \;

echo "Backup created at $BACKUP_DIR"
```

Make executable and schedule:

```bash
chmod +x ~/backup_medicines.sh

# Add to crontab for daily backups at 3 AM
(crontab -l 2>/dev/null; echo "0 3 * * * /home/pi/backup_medicines.sh") | crontab -
```

### Manual Backup

```bash
# Backup before making changes
cp ~/pizero_apps/medicine_data.json ~/medicine_data_backup_$(date +%Y%m%d_%H%M%S).json
cp ~/pizero_apps/config.json ~/config_backup_$(date +%Y%m%d_%H%M%S).json
```

### Restore from Backup

```bash
# List backups
ls -lh ~/backups/

# Restore specific backup
BACKUP_DATE="20251108_150000"
cp ~/backups/$BACKUP_DATE/medicine_data.json ~/pizero_apps/
cp ~/backups/$BACKUP_DATE/config.json ~/pizero_apps/

# Restart services
sudo systemctl restart pizero-webui
```

---

## Troubleshooting Deployment

### Issue: Python Module Not Found

```bash
# Error: ModuleNotFoundError: No module named 'flask'

# Solution: Install requirements
pip3 install -r requirements.txt

# Or install specific package
pip3 install Flask==2.0.0
```

### Issue: GPIO Busy Error

```bash
# Error: GPIO 3 already in use

# Solution: Kill all Python processes
pkill -9 python3
sleep 2

# Clear GPIO
sudo rm -f /run/gpio-*.lock

# Restart
cd ~/pizero_apps && python3 menu_button.py
```

### Issue: Display Not Initialized

```bash
# Error: Failed to initialize SPI display

# Check SPI is enabled
sudo raspi-config  # Enable SPI interface

# Check driver path
ls ~/python/lib/TP_lib/epd2in13_V4.py

# Test display directly
python3 << 'EOF'
import sys
sys.path.append('/home/pi/python/lib')
from TP_lib import epd2in13_V4
epd = epd2in13_V4.EPD()
print(f"Display: {epd.width}x{epd.height}")
EOF
```

### Issue: Web Server Won't Start

```bash
# Check if port 5000 is in use
sudo netstat -tulpn | grep 5000

# Kill process on port 5000
sudo fuser -k 5000/tcp

# Start web server
cd ~/pizero_apps && python3 web_config.py
```

### Issue: Permissions Error

```bash
# Error: Permission denied when writing to files

# Fix ownership
sudo chown -R pi:pi ~/pizero_apps

# Fix permissions
chmod 755 ~/pizero_apps
chmod 664 ~/pizero_apps/*.json
chmod 755 ~/pizero_apps/*.py
```

---

## Post-Deployment Testing

### Test Each Application

```bash
# Weather app
python3 weather_cal_app.py

# MBTA app
python3 mbta_app.py

# Disney app
python3 disney_app.py

# Medicine app
python3 medicine_app.py

# Pomodoro app
python3 pomodoro_app.py
```

### Test Web API

```bash
# Get configuration
curl http://localhost:5000/api/config

# Get medicine data
curl http://localhost:5000/api/medicine/data

# Add medicine (test)
curl -X POST http://localhost:5000/api/medicine/add \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","dosage":"1mg","time_window":"morning"}'
```

---

## Next Steps

1. Read [CONFIGURATION_REFERENCE.md](CONFIGURATION_REFERENCE.md) for detailed configuration options
2. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues
3. Review [UPGRADE_GUIDE.md](UPGRADE_GUIDE.md) for future updates
4. Check [FAQ.md](FAQ.md) for common questions

---

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review application logs in `/tmp/`
3. Test components individually
4. Check system resources (`free -h`, `df -h`)

**Estimated Deployment Time:** 30-45 minutes
**Skill Level:** Intermediate (comfortable with Linux/SSH)

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
