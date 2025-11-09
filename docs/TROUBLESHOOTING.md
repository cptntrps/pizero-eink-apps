# Troubleshooting Guide

**Version:** 1.0
**Last Updated:** November 8, 2025

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Hardware Issues](#hardware-issues)
3. [Software Issues](#software-issues)
4. [Display Problems](#display-problems)
5. [GPIO & Button Issues](#gpio--button-issues)
6. [Web Server Issues](#web-server-issues)
7. [Medicine Tracker Issues](#medicine-tracker-issues)
8. [Performance Issues](#performance-issues)
9. [Network Issues](#network-issues)
10. [System Recovery](#system-recovery)
11. [Log Files & Debugging](#log-files--debugging)

---

## Quick Diagnostics

Use this checklist to quickly identify the problem type:

```bash
#!/bin/bash
echo "=== System Health Check ==="

# 1. Check processes
echo -n "Services running: "
ps aux | grep -c "[p]ython3"

# 2. Check network
echo -n "Network OK: "
ping -c 1 8.8.8.8 > /dev/null && echo "YES" || echo "NO"

# 3. Check disk space
echo -n "Disk usage: "
df -h / | tail -1 | awk '{print $5}'

# 4. Check web server
echo -n "Web server responsive: "
curl -s http://localhost:5000/ > /dev/null && echo "YES" || echo "NO"

# 5. Check memory
echo -n "Memory available: "
free -h | grep Mem | awk '{print $7}'

# 6. Check services
echo "=== Service Status ==="
sudo systemctl is-active pizero-webui
sudo systemctl is-active pizero-menu
```

---

## Hardware Issues

### Issue: Display Not Showing Anything (Blank Screen)

**Symptoms:**
- Display shows nothing
- No error messages
- Device appears to be running

**Diagnosis:**

```bash
# 1. Check if display is powered
# Visual inspection: Look for any LED indicators

# 2. Check SPI is enabled
raspi-config  # Menu: Interfacing Options → SPI → Enable

# 3. Test display connection
python3 << 'EOF'
import sys
sys.path.append('/home/pi/python/lib')
from TP_lib import epd2in13_V4
from PIL import Image, ImageDraw

try:
    epd = epd2in13_V4.EPD()
    print(f"Display initialized: {epd.width}x{epd.height}")

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "TEST", fill=0)

    epd.init(epd.FULL_UPDATE)
    epd.display(epd.getbuffer(image))
    print("✓ Display test image sent")
except Exception as e:
    print(f"✗ Display error: {e}")
    print(f"✗ Check display cable connections and SPI settings")
EOF
```

**Solutions:**

1. **Check cables:**
   - Display SPI cable connected to GPIO pins
   - Power cable properly connected
   - No loose connections

2. **Enable SPI Interface:**
   ```bash
   sudo raspi-config
   # Select: Interfacing Options → SPI → Enable
   # Reboot: sudo reboot
   ```

3. **Check driver files:**
   ```bash
   ls -la ~/python/lib/TP_lib/
   # Should contain: epd2in13_V4.py, epdconfig.py
   ```

4. **Try alternative driver (if available):**
   ```bash
   # If V4 driver fails, try V3
   # Edit epd2in13_V4.py import in app
   ```

5. **Reboot and test:**
   ```bash
   sudo reboot
   # Wait 2 minutes
   # Power cycle display
   ```

---

### Issue: Display Shows Ghosting (Previous Images Visible)

**Symptoms:**
- Old images still visible on screen
- Multiple overlapping displays
- Fading previous content

**Diagnosis:**

```bash
# Check refresh mode
grep "refresh_mode" ~/pizero_apps/config.json

# Check application logs
tail -50 /tmp/menu.log | grep -i "refresh\|display"
```

**Solutions:**

1. **Force full display refresh:**
   ```python
   import sys
   sys.path.append('/home/pi/python/lib')
   from TP_lib import epd2in13_V4

   epd = epd2in13_V4.EPD()
   epd.init(epd.FULL_UPDATE)  # Not PART_UPDATE
   epd.Clear(0xFF)  # White out
   epd.display(epd.getbuffer(image))
   ```

2. **Update config to use full refresh:**
   ```bash
   # Edit config.json
   nano ~/pizero_apps/config.json
   # Change "refresh_mode": "partial" to "full"

   # Restart
   sudo systemctl restart pizero-menu
   ```

3. **Clear display completely:**
   ```bash
   python3 << 'EOF'
   import sys
   sys.path.append('/home/pi/python/lib')
   from TP_lib import epd2in13_V4
   from PIL import Image

   epd = epd2in13_V4.EPD()
   epd.init(epd.FULL_UPDATE)
   epd.Clear(0xFF)  # Full white
   print("Display cleared")
   EOF
   ```

4. **Check partial update limit:**
   ```bash
   # In config.json, ensure:
   "display": {
     "partial_update_limit": 10  # Force full refresh after 10 partial updates
   }
   ```

---

### Issue: Display Rotated or Upside Down

**Symptoms:**
- Content appears rotated 90°, 180°, or 270°
- Text is upside down
- Menu appears sideways

**Solutions:**

1. **Adjust rotation setting:**
   ```bash
   nano ~/pizero_apps/config.json
   # Find "display" section, change "rotation":
   "rotation": 0      # Normal (0°)
   "rotation": 90     # 90° clockwise
   "rotation": 180    # Upside down
   "rotation": 270    # 270° clockwise
   ```

2. **Restart application:**
   ```bash
   sudo systemctl restart pizero-menu
   ```

3. **Check physical orientation:**
   - Display connector should face down
   - Text should be readable normally

---

## Software Issues

### Issue: Python Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'flask'
ImportError: cannot import name 'EPD'
```

**Solution:**

1. **Check Python version:**
   ```bash
   python3 --version  # Should be 3.7+
   ```

2. **Verify installation:**
   ```bash
   pip3 list | grep Flask
   # If not listed, install:
   pip3 install Flask==2.0.0
   ```

3. **Install all requirements:**
   ```bash
   cd ~/pizero_apps
   pip3 install -r requirements.txt
   ```

4. **Check installation path:**
   ```bash
   python3 -c "import flask; print(flask.__file__)"
   ```

---

### Issue: Application Crashes Immediately

**Symptoms:**
- App starts and stops instantly
- No error message
- No log entry

**Diagnosis:**

```bash
# Run directly to see error
cd ~/pizero_apps
python3 medicine_app.py

# Or check systemd logs
sudo journalctl -u pizero-menu -n 50
```

**Common Causes:**

1. **Missing configuration file:**
   ```bash
   ls ~/pizero_apps/config.json
   # If missing, copy from backup or create new
   ```

2. **Invalid JSON:**
   ```bash
   python3 -m json.tool ~/pizero_apps/config.json
   # Fix syntax errors
   ```

3. **Missing data file:**
   ```bash
   ls ~/pizero_apps/medicine_data.json
   # Create if missing:
   echo '{"medicines":[],"tracking":{},"time_windows":{}}' > ~/pizero_apps/medicine_data.json
   ```

4. **Permission denied:**
   ```bash
   chmod 755 ~/pizero_apps/*.py
   chmod 664 ~/pizero_apps/*.json
   ```

---

## Display Problems

### Issue: Certain Text Not Visible

**Symptoms:**
- Some text missing from display
- Partial content cut off
- Words disappear

**Solutions:**

1. **Check font files exist:**
   ```bash
   ls ~/python/pic/*.ttf
   # Should see: Roboto-Bold.ttf, Roboto-Regular.ttf
   ```

2. **Verify font path in code:**
   ```bash
   grep -n "truetype\|\.ttf" ~/pizero_apps/medicine_app.py
   # Path should be absolute: /home/pi/python/pic/Roboto*.ttf
   ```

3. **Test font loading:**
   ```bash
   python3 << 'EOF'
   from PIL import ImageFont
   try:
       font = ImageFont.truetype("/home/pi/python/pic/Roboto-Bold.ttf", 16)
       print("✓ Font loaded successfully")
   except Exception as e:
       print(f"✗ Font error: {e}")
   EOF
   ```

4. **Increase text area:**
   ```bash
   # In app, ensure text rendering within bounds:
   # Display is 250×122 pixels
   # Leave margins: top 20px, bottom 20px
   ```

---

### Issue: Display Updates Too Slowly

**Symptoms:**
- Takes several seconds to update
- Lag between button press and display change
- Sluggish menu navigation

**Solutions:**

1. **Check update interval:**
   ```bash
   grep "update_interval" ~/pizero_apps/config.json
   # Reduce value (in seconds)
   ```

2. **Switch to partial updates:**
   ```bash
   nano ~/pizero_apps/config.json
   # Change: "refresh_mode": "partial"
   # Only use full refresh on major changes
   ```

3. **Optimize display code:**
   ```python
   # Instead of full image redraw, use partial update:
   epd.displayPartial(epd.getbuffer(image_update))
   # Instead of:
   epd.display(epd.getbuffer(full_image))
   ```

4. **Check system performance:**
   ```bash
   top -bn1 | head -20
   # Look for CPU usage > 50%
   # Check for other processes consuming resources
   ```

---

## GPIO & Button Issues

### Issue: GPIO Busy Error

**Error:**
```
RuntimeError: GPIO 3 is currently being used by another application
```

**Solutions:**

1. **Kill all Python processes:**
   ```bash
   pkill -9 python3
   sleep 2
   ```

2. **Clear GPIO state:**
   ```bash
   sudo rm -f /run/gpio*.lock
   ```

3. **Clean restart:**
   ```bash
   sudo systemctl restart pizero-menu
   ```

4. **If still failing, reboot:**
   ```bash
   sudo reboot
   ```

---

### Issue: Button Not Responding

**Symptoms:**
- Pressing button does nothing
- No change in display
- No log entries when pressing

**Diagnosis:**

```bash
# Test GPIO directly
python3 << 'EOF'
from gpiozero import Button
import time

button = Button(3)  # GPIO pin 3
print("Testing GPIO 3. Press button now...")
print("Button pressed state:", button.is_pressed)

for i in range(30):
    if button.is_pressed:
        print(f"[{i}s] Button pressed!")
    time.sleep(1)
EOF
```

**Solutions:**

1. **Check button connection:**
   - Button connected to GPIO pin 3
   - Button connected to ground
   - No loose connections

2. **Check GPIO configuration:**
   ```bash
   # Verify pin is available
   gpio readall
   # Pin 3 should not be in use
   ```

3. **Verify pull-up resistor:**
   ```python
   from gpiozero import Button
   # In code, should have:
   button = Button(3, pull_up=True, bounce_time=0.1)
   ```

4. **Test with simple script:**
   ```bash
   python3 << 'EOF'
   from gpiozero import Button
   button = Button(3)
   button.wait_for_press()
   print("Button pressed!")
   EOF
   ```

---

### Issue: Button Double-Pressing or False Triggers

**Symptoms:**
- Button seems to trigger twice per press
- Ghost presses with no button touch
- Menu skips multiple items

**Solutions:**

1. **Increase debounce time:**
   ```python
   # In code:
   button = Button(3, bounce_time=0.2)  # Default 0.1s
   # Try: 0.2, 0.3, or 0.5
   ```

2. **Add software debouncing:**
   ```python
   import time
   last_press = 0

   while True:
       if button.is_pressed:
           now = time.time()
           if now - last_press > 0.5:  # Ignore presses within 500ms
               handle_button_press()
               last_press = now
       time.sleep(0.1)
   ```

3. **Check button hardware:**
   - Physical button might be worn
   - Contact might be dirty
   - Try cleaning contacts with isopropyl alcohol

---

## Web Server Issues

### Issue: Web Server Not Accessible

**Error:**
```
Connection refused: http://192.168.x.x:5000
```

**Diagnosis:**

```bash
# Check if server is running
ps aux | grep web_config.py | grep -v grep

# Check if port is listening
sudo netstat -tulpn | grep 5000

# Try connecting locally
curl http://localhost:5000/
```

**Solutions:**

1. **Start web server:**
   ```bash
   cd ~/pizero_apps
   nohup python3 web_config.py > /tmp/webserver.log 2>&1 &
   ```

2. **Check for port conflict:**
   ```bash
   # Find what's on port 5000
   sudo lsof -i :5000

   # If something else is using it:
   sudo kill -9 <PID>
   ```

3. **Restart via systemd:**
   ```bash
   sudo systemctl restart pizero-webui
   sudo systemctl status pizero-webui
   ```

4. **Check logs for errors:**
   ```bash
   tail -50 /tmp/webserver.log
   ```

---

### Issue: Web Server Crashes After a While

**Symptoms:**
- Server works initially, then stops
- Can't access web UI after some time
- Manual refresh needed to bring back up

**Solutions:**

1. **Check for memory leaks:**
   ```bash
   # Monitor memory usage
   watch -n 1 'ps aux | grep web_config.py | grep -v grep | awk "{print $6}"'
   # If memory keeps increasing, there's a leak
   ```

2. **Implement auto-restart:**
   ```bash
   # In systemd service (/etc/systemd/system/pizero-webui.service):
   Restart=on-failure
   RestartSec=10
   StartLimitInterval=60
   StartLimitBurst=3
   ```

3. **Add watchdog script:**
   ```bash
   #!/bin/bash
   # check_webui.sh - Run every minute via cron

   if ! curl -s http://localhost:5000/ > /dev/null; then
       sudo systemctl restart pizero-webui
       echo "$(date): Restarted web server" >> /tmp/webui_restarts.log
   fi
   ```

---

### Issue: 404 Errors When Accessing Pages

**Error:**
```
404 Not Found
```

**Solutions:**

1. **Check web_config.py has all routes:**
   ```bash
   grep -n "@app.route" ~/pizero_apps/web_config.py
   ```

2. **Verify file paths:**
   ```bash
   # Routes should reference correct files
   grep -n "render_template\|static" ~/pizero_apps/web_config.py
   ```

3. **Check for syntax errors:**
   ```bash
   python3 -m py_compile ~/pizero_apps/web_config.py
   ```

4. **Restart server:**
   ```bash
   sudo systemctl restart pizero-webui
   ```

---

## Medicine Tracker Issues

### Issue: Medicine Not Appearing in Reminders

**Symptoms:**
- Added medicine but doesn't show
- No reminders at scheduled time
- Medicine list shows empty

**Checklist:**

```bash
# 1. Verify medicine is active
python3 << 'EOF'
import json
data = json.load(open('~/pizero_apps/medicine_data.json'))
for med in data['medicines']:
    print(f"{med['name']}: active={med.get('active', True)}")
EOF

# 2. Check if today is in medicine's days
python3 << 'EOF'
from datetime import datetime
import json
data = json.load(open('~/pizero_apps/medicine_data.json'))
today = datetime.now().strftime('%a').lower()
for med in data['medicines']:
    if today in med['days']:
        print(f"✓ {med['name']} scheduled today")
    else:
        print(f"✗ {med['name']} not scheduled for {today.upper()}")
EOF

# 3. Check if current time is in window
python3 << 'EOF'
from datetime import datetime
import json
data = json.load(open('~/pizero_apps/medicine_data.json'))
now = datetime.now()
for med in data['medicines']:
    start = datetime.strptime(med['window_start'], '%H:%M').time()
    end = datetime.strptime(med['window_end'], '%H:%M').time()
    in_window = start <= now.time() <= end
    print(f"{med['name']}: {start}-{end}, in_window={in_window}")
EOF
```

**Solutions:**

1. **Ensure medicine is active:**
   ```bash
   # Edit medicine_data.json
   # Set "active": true for the medicine
   ```

2. **Check days of week:**
   ```bash
   # Ensure "days" array includes today:
   "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
   ```

3. **Check time window:**
   ```bash
   # Current time should be within window
   # With reminder_window buffer (default ±30min)
   ```

4. **Check reminder window setting:**
   ```bash
   # In config.json, "reminder_window": 30 means ±30 minutes
   # Increase if needed
   ```

5. **Force refresh:**
   ```bash
   # Restart medicine app
   sudo systemctl restart pizero-menu

   # Or access via web UI and refresh
   curl http://localhost:5000/api/medicine/data
   ```

---

### Issue: Pill Count Not Decrementing

**Symptoms:**
- Mark medicine as taken
- Pill count stays same
- No change in database

**Solutions:**

1. **Check pills_per_dose field:**
   ```bash
   # Ensure medicine has this field:
   "pills_per_dose": 1
   ```

2. **Verify file permissions:**
   ```bash
   ls -la ~/pizero_apps/medicine_data.json
   # Should be: -rw-rw-r-- (664)

   # Fix if needed:
   chmod 664 ~/pizero_apps/medicine_data.json
   ```

3. **Check write access:**
   ```bash
   python3 << 'EOF'
   import json
   import os

   file_path = '~/pizero_apps/medicine_data.json'
   if os.access(file_path, os.W_OK):
       print("✓ File is writable")
   else:
       print("✗ File is not writable")
   EOF
   ```

4. **Test update directly:**
   ```bash
   python3 << 'EOF'
   import json
   import sys
   sys.path.append('~/pizero_apps')

   # Load data
   with open('~/pizero_apps/medicine_data.json') as f:
       data = json.load(f)

   # Update first medicine
   if data['medicines']:
       data['medicines'][0]['pills_remaining'] -= 1

       # Save
       with open('~/pizero_apps/medicine_data.json', 'w') as f:
           json.dump(data, f, indent=2)

       print("✓ Update successful")
       print(f"Pills remaining: {data['medicines'][0]['pills_remaining']}")
   EOF
   ```

---

### Issue: Low Stock Warning Not Showing

**Symptoms:**
- Medicine has low pills but no alert
- No red border on web UI
- "REORDER!" message missing

**Solutions:**

1. **Check low_stock_threshold:**
   ```bash
   # Edit medicine in web UI or medicine_data.json
   # Ensure "low_stock_threshold" is set
   # Currently: pills_remaining <= threshold shows alert
   ```

2. **Verify pills_remaining:**
   ```bash
   # Check actual pill count
   python3 << 'EOF'
   import json
   data = json.load(open('~/pizero_apps/medicine_data.json'))
   for med in data['medicines']:
       print(f"{med['name']}: {med['pills_remaining']} pills, alert at {med.get('low_stock_threshold', 10)}")
   EOF
   ```

3. **Force update:**
   ```bash
   # In web UI, edit medicine and save to trigger refresh
   curl -X POST http://localhost:5000/api/medicine/update \
     -H "Content-Type: application/json" \
     -d '{"id":"med_123","pills_remaining":5,"low_stock_threshold":10}'
   ```

---

## Performance Issues

### Issue: High CPU Usage (Pi Getting Hot)

**Symptoms:**
- Device running hot
- Battery drains quickly
- Top shows python3 at 50%+ CPU

**Diagnosis:**

```bash
# Check processes
top -bn1 | head -20

# Check specific app
ps aux | grep python3 | grep -v grep | awk '{print $2}' | xargs kill -0 2>&1

# Monitor continuously
watch -n 1 'top -bn1 | grep python3'
```

**Solutions:**

1. **Check for infinite loops:**
   ```bash
   # Add delays to loops:
   import time
   while True:
       # ... do something
       time.sleep(1)  # Add delay
   ```

2. **Reduce update frequency:**
   ```bash
   # In config.json, increase intervals:
   "medicine": {
       "update_interval": 120  # Changed from 60
   }
   ```

3. **Disable unnecessary features:**
   ```bash
   # In config.json:
   "system": {
       "auto_sleep": true,
       "sleep_timeout": 300
   }
   ```

4. **Check for memory leaks:**
   ```bash
   # Monitor memory
   while true; do ps aux | grep web_config.py | awk '{print $6}'; sleep 5; done
   # If consistently increasing, kill and restart
   ```

---

### Issue: Out of Memory

**Error:**
```
MemoryError
Killed (Out of memory)
```

**Solutions:**

1. **Check available memory:**
   ```bash
   free -h
   ```

2. **Clear caches:**
   ```bash
   sudo sync
   sudo echo 3 > /proc/sys/vm/drop_caches
   ```

3. **Find memory hogs:**
   ```bash
   ps aux --sort=-%mem | head -10
   ```

4. **Reduce cache sizes:**
   ```bash
   # In web_config.py, limit Flask cache
   # In medicine_app.py, avoid loading entire database into memory
   ```

---

### Issue: Disk Space Running Out

**Error:**
```
No space left on device
```

**Solutions:**

1. **Check disk usage:**
   ```bash
   df -h /
   du -sh ~/pizero_apps
   du -sh /tmp
   ```

2. **Clean up logs:**
   ```bash
   sudo journalctl --vacuum=100M  # Keep last 100MB
   rm -f /tmp/*.log               # Remove old logs
   ```

3. **Remove backups (if space critical):**
   ```bash
   # Keep only recent backups
   ls -t ~/backups | tail -n +5 | xargs rm -rf
   ```

4. **Check for large files:**
   ```bash
   find ~ -size +100M -type f
   # Remove unnecessary large files
   ```

---

## Network Issues

### Issue: Can't Connect to WiFi

**Symptoms:**
- Device shows no WiFi
- Disconnects frequently
- Weak signal

**Solutions:**

1. **Check WiFi configuration:**
   ```bash
   sudo iwconfig
   sudo ip link show wlan0
   ```

2. **Scan for networks:**
   ```bash
   sudo iwlist wlan0 scan | grep SSID
   ```

3. **Reconnect to WiFi:**
   ```bash
   # Using nmcli
   nmcli device wifi connect "SSID" password "PASSWORD"

   # Or edit /etc/wpa_supplicant/wpa_supplicant.conf
   sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
   ```

4. **Check signal strength:**
   ```bash
   iwconfig wlan0 | grep "Signal level"
   ```

---

### Issue: Can't SSH Into Device

**Error:**
```
Connection refused
ssh: connect to host 192.168.x.x port 22: Connection refused
```

**Solutions:**

1. **Enable SSH:**
   ```bash
   # On device, run:
   sudo systemctl start ssh
   sudo systemctl enable ssh

   # Or:
   sudo raspi-config
   # Enable SSH in Interfacing Options
   ```

2. **Find device IP:**
   ```bash
   # On device:
   hostname -I

   # Or from router admin panel
   ```

3. **Verify network connectivity:**
   ```bash
   ping 192.168.x.x
   ```

---

### Issue: Web UI Times Out Loading

**Symptoms:**
- Browser hangs when accessing web UI
- Eventually shows "Connection timed out"
- Other devices can't access

**Solutions:**

1. **Check network connectivity:**
   ```bash
   ping 192.168.x.x
   nslookup 192.168.x.x  # If using hostname
   ```

2. **Check web server:**
   ```bash
   sudo systemctl status pizero-webui
   tail -50 /tmp/webserver.log
   ```

3. **Test with curl:**
   ```bash
   curl -v http://localhost:5000/
   # If localhost works, might be network issue
   ```

4. **Check firewall:**
   ```bash
   sudo ufw status
   # May need to allow port 5000
   sudo ufw allow 5000
   ```

---

## System Recovery

### Issue: System Won't Boot

**Symptoms:**
- Device powered on but nothing happens
- No display output
- LED activity but no response

**Solutions:**

1. **Force reboot:**
   ```bash
   # Hold power button for 10 seconds
   # Wait 5 seconds
   # Power on again
   ```

2. **Check SD card:**
   ```bash
   # Remove SD card, check for corruption
   # Try on another Pi if possible
   ```

3. **Reflash OS:**
   ```bash
   # Use Raspberry Pi Imager to reflash SD card
   # Then reinstall application (see DEPLOYMENT_GUIDE.md)
   ```

---

### Issue: File System Corruption

**Symptoms:**
- File not found errors for existing files
- JSON parsing errors
- Unexpected file modifications

**Solutions:**

1. **Check file system:**
   ```bash
   sudo fsck -f /
   # This requires unmounting filesystem (usually requires reboot)
   ```

2. **Restore from backup:**
   ```bash
   cp ~/backups/before_upgrade_20251108/medicine_data.json ~/pizero_apps/
   sudo systemctl restart pizero-webui
   ```

3. **Verify file integrity:**
   ```bash
   # Check JSON files
   python3 -m json.tool ~/pizero_apps/config.json > /dev/null && echo "OK"

   # Check Python files
   python3 -m py_compile ~/pizero_apps/*.py
   ```

---

## Log Files & Debugging

### Main Log Locations

```bash
# Web Server Log
tail -f /tmp/webserver.log

# Menu System Log
tail -f /tmp/menu.log

# System Logs
journalctl -u pizero-webui -f
journalctl -u pizero-menu -f

# General System
tail -f /var/log/syslog
```

### Enable Debug Logging

In Python applications, add:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Collecting Diagnostic Information

```bash
#!/bin/bash
# collect_diagnostics.sh

echo "=== System Information ===" > /tmp/diagnostics.txt
uname -a >> /tmp/diagnostics.txt
cat /etc/os-release >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Python Version ===" >> /tmp/diagnostics.txt
python3 --version >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Installed Packages ===" >> /tmp/diagnostics.txt
pip3 list >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Processes ===" >> /tmp/diagnostics.txt
ps aux | grep python3 >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Disk Usage ===" >> /tmp/diagnostics.txt
df -h >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Memory Usage ===" >> /tmp/diagnostics.txt
free -h >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Network ===" >> /tmp/diagnostics.txt
hostname -I >> /tmp/diagnostics.txt
iwconfig >> /tmp/diagnostics.txt

echo "" >> /tmp/diagnostics.txt
echo "=== Recent Logs ===" >> /tmp/diagnostics.txt
tail -100 /tmp/webserver.log >> /tmp/diagnostics.txt
tail -100 /tmp/menu.log >> /tmp/diagnostics.txt

echo "Diagnostics saved to /tmp/diagnostics.txt"
```

Run and review:

```bash
chmod +x collect_diagnostics.sh
./collect_diagnostics.sh
cat /tmp/diagnostics.txt
```

---

## Emergency Contact

If you've exhausted these troubleshooting steps:

1. **Gather diagnostics** (see above)
2. **Note error messages** exactly as they appear
3. **Document steps taken** so far
4. **Consider factory reset** if all else fails (see Reflash OS section)

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
