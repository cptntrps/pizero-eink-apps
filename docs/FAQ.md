# Frequently Asked Questions (FAQ)

**Version:** 1.0
**Last Updated:** November 8, 2025

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Installation & Setup](#installation--setup)
3. [Configuration](#configuration)
4. [Medicine Tracking](#medicine-tracking)
5. [Web Interface](#web-interface)
6. [Hardware & Display](#hardware--display)
7. [Performance & Optimization](#performance--optimization)
8. [Backup & Data](#backup--data)
9. [Updates & Upgrades](#updates--upgrades)
10. [Troubleshooting Tips](#troubleshooting-tips)

---

## General Questions

### Q: What is the Pi Zero 2W Medicine Tracker?

**A:** It's a complete medication reminder and inventory management system for Raspberry Pi Zero 2W with an e-ink display. Features include:
- Time-based medicine reminders
- Automatic pill count tracking
- Low-stock alerts
- Web-based configuration
- Single-button operation on device
- Multi-app system (weather, flights, pomodoro, transit, etc.)

---

### Q: What hardware do I need?

**A:** Minimum requirements:
- Raspberry Pi Zero 2W ($15)
- Waveshare 2.13" V4 e-ink display ($30-40)
- MicroSD card 16GB+ ($10)
- USB power supply 2.5A+ ($10)
- Button for GPIO pin 3 (optional, $2)
- Total estimated cost: $75-100

---

### Q: Is this a medical device?

**A:** No. This is a personal reminder and tracking tool. It's not FDA-approved or clinically validated. Always follow your doctor's prescribed medication schedule. This tool helps you remember, but you remain responsible for proper medication management.

---

### Q: Can it send me notifications?

**A:** Currently, reminders appear only on the e-ink display. Future versions may support email/SMS notifications. For now:
- Check display regularly
- Set phone alarms as backup
- Review web UI for upcoming medicines

---

### Q: Is my medicine data secure?

**A:** Data is stored locally on the device in JSON files. Security features:
- No cloud upload (data stays on device)
- Web UI has no built-in authentication
- Recommend keeping device on private network
- Regularly backup data files

For sensitive information, consider:
- Changing WiFi password
- Using VPN if accessing remotely
- Encrypting MicroSD card

---

### Q: Can I run this on other Raspberry Pi models?

**A:** Yes, but test first. Tested on:
- ✓ Raspberry Pi Zero 2W (official)
- ✓ Raspberry Pi 4 (works)
- ? Raspberry Pi Pico (not recommended - different architecture)
- ? Other models (may work, test thoroughly)

Code is Python 3, so any Pi running Python 3.7+ should work.

---

### Q: Is there a mobile app?

**A:** Not yet. Current access methods:
- Physical e-ink display on device
- Web browser at `http://<pi-ip>:5000`
- SSH access for advanced users

Mobile app is planned for future version.

---

## Installation & Setup

### Q: How long does installation take?

**A:** Typically 30-45 minutes:
- System preparation: 5 min
- Dependency installation: 10 min
- Code setup: 10 min
- Configuration: 10 min
- Testing: 5-10 min

If you're experienced with Raspberry Pi, 20-30 minutes is possible.

---

### Q: Do I need to know Linux/programming?

**A:** Basic comfort with Linux is helpful:
- SSH access
- Basic command line
- Text file editing
- Concepts like GPIO, SPI

The DEPLOYMENT_GUIDE.md provides copy-paste commands, so you can follow along even if unfamiliar.

---

### Q: Can I install from USB drive instead of cloning?

**A:** Yes. Copy project files from USB:

```bash
# Create pizero_apps directory
mkdir -p ~/pizero_apps

# Copy from USB
cp -r /mnt/usb/pizero_apps/* ~/pizero_apps/

# Then continue with dependency installation
```

---

### Q: What if my Pi already has other services running?

**A:** Usually no conflict. Port 5000 is available on most systems. To check:

```bash
netstat -tulpn | grep 5000
```

If port 5000 is in use, change in `web_config.py`:

```python
app.run(host='0.0.0.0', port=5001)  # Use 5001 instead
```

---

### Q: Do I need to connect it to the internet?

**A:** Not strictly required for basic functionality:
- Medicine reminders work offline
- Display updates work offline
- Web UI works on local network

You need internet for:
- Weather app
- MBTA transit info
- Disney wait times
- Flight tracking

---

## Configuration

### Q: Where do I edit settings?

**A:** Two ways:

1. **Web UI (Recommended):**
   - Open `http://<pi-ip>:5000`
   - Click on app sections
   - Save changes

2. **SSH (Advanced):**
   ```bash
   nano ~/pizero_apps/config.json
   # Edit and save
   ```

---

### Q: What's the difference between config.json and medicine_data.json?

**A:**
- **config.json:** System settings (all apps, display, timings)
- **medicine_data.json:** Medicine list and tracking history

Both are important and require valid JSON syntax.

---

### Q: Can I have the same medicine at multiple times?

**A:** Not directly, but workaround:
1. Create two separate medicine entries:
   - "Vitamin D (Morning)"
   - "Vitamin D (Evening)"
2. Set different time windows for each

---

### Q: What if my medication schedule changes?

**A:** Easy to update via web UI:
1. Open web interface
2. Edit medicine details
3. Change time window or days
4. Click Save

Changes take effect immediately.

---

### Q: Can I edit medicine_data.json manually?

**A:** Yes, but be careful:
1. Always backup first
2. Maintain valid JSON syntax
3. Restart services after changes:
   ```bash
   sudo systemctl restart pizero-webui
   ```

Use `python3 -m json.tool` to validate before restarting.

---

### Q: How do I disable an app?

**A:** Edit config.json:

```json
"menu": {
  "apps": [
    {
      "id": "weather",
      "name": "Weather",
      "enabled": false,  // Changed from true
      "order": 1
    }
  ]
}
```

Then restart: `sudo systemctl restart pizero-menu`

---

## Medicine Tracking

### Q: How often does the app check for medicines?

**A:** Every 60 seconds by default (configurable in config.json):

```json
"medicine": {
  "update_interval": 60  // Check every 60 seconds
}
```

Lower values = more responsive but higher CPU usage.

---

### Q: What's the reminder window?

**A:** ±30 minutes by default. If medicine is due 8:00 AM with 30-min window:
- Reminder shows 7:30-8:30 AM
- Change in config.json:

```json
"medicine": {
  "reminder_window": 30  // ±30 minutes
}
```

---

### Q: Does it track adherence?

**A:** Yes, automatically:
- Timestamps recorded when marked taken
- Data stored in medicine_data.json tracking section
- Progress shown on display: "3/4 taken (75%)"

View full history by examining medicine_data.json.

---

### Q: Can I mark medicine taken manually via web?

**A:** Currently only via physical button:
1. Press button when reminder shows
2. Medication marked as taken
3. Pill count decrements
4. Confirmation displayed

Web UI is for configuration only (currently).

---

### Q: What happens if I miss a dose?

**A:** System continues normally:
1. Reminder expires after window passes
2. Next scheduled time shows reminder again
3. No "missed dose" alert (yet)

Future version may show missed dose statistics.

---

### Q: Can multiple people use the same device?

**A:** Yes, but:
- All medicines on shared list
- Anyone can mark taken
- Tracking shows combined history
- No per-person accounts

For privacy, maintain separate device or document independently.

---

## Web Interface

### Q: How do I access the web interface?

**A:** From any device on the network:

```
http://192.168.x.x:5000
```

Replace 192.168.x.x with your Pi's IP address:

```bash
# Find IP on Pi:
hostname -I
```

---

### Q: Why is my web UI showing old data?

**A:** Browser cache. Try:
1. Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
2. Clear browser cache
3. Restart web server: `sudo systemctl restart pizero-webui`

---

### Q: Can I access the web UI from outside my home?

**A:** Technically yes, but not recommended for security. If needed:
1. Set up port forwarding on router (advanced)
2. Use VPN to access home network
3. Add authentication to web_config.py (modify code)

---

### Q: The web UI looks broken - why?

**A:** Usually CSS/JavaScript issues. Try:
1. Hard refresh browser
2. Try different browser
3. Check browser console for errors: `F12` → Console tab
4. Restart web server

---

### Q: Can I customize the web UI colors/layout?

**A:** Yes, edit web_config.py. It uses Flask with HTML/CSS. Modify:
- Templates in the file
- CSS styles inline
- JavaScript for interactivity

---

## Hardware & Display

### Q: Why e-ink instead of LCD?

**A:** E-ink advantages:
- Low power consumption (hours on battery)
- No backlight (works in any light)
- Readability (like paper)
- Less eye strain
- Long battery life

Disadvantages:
- Slower updates (200-500ms)
- Limited colors (black & white)
- Can show ghosting if abused

---

### Q: Can I use a different display?

**A:** Yes, but requires code changes:
1. Find driver library for your display
2. Replace import statements in app files
3. Adjust buffer/size constants
4. Test thoroughly

Common alternatives:
- Waveshare 7.5" e-ink
- Waveshare 1.54" e-ink
- LCD displays (requires backlighting)

---

### Q: Why does the display sometimes show old content?

**A:** Ghosting from excessive partial updates. Solutions:
1. Force full refresh: restart app
2. Adjust refresh_mode in config.json
3. Reduce partial_update_limit

---

### Q: Can I connect a touchscreen?

**A:** Display supports touch, but app doesn't use it yet. You could modify app to:
1. Initialize touch controller
2. Detect touch coordinates
3. Handle touch events instead of button

---

### Q: How long does the display last?

**A:** E-ink displays typically last:
- 10+ years in storage
- Years of daily use
- Unaffected by on-off cycles

Not officially rated for lifespan, but very durable.

---

### Q: Can I rotate the display orientation?

**A:** Yes, in config.json:

```json
"display": {
  "rotation": 0      // 0, 90, 180, or 270 degrees
}
```

---

## Performance & Optimization

### Q: Why does the device get hot?

**A:** Possible causes:
1. High CPU usage (check with `top`)
2. No ventilation/case
3. Sustained full updates
4. Other processes running

Solutions:
- Reduce update frequency
- Ensure airflow
- Check processes: `ps aux`
- Disable unused apps

---

### Q: How much power does it consume?

**A:** Estimated usage:
- Idle: ~200-300mW
- Active (display updating): ~500mW-1W
- Display takes ~80% of power
- WiFi adds 50-200mW

Total daily: ~3-5Wh (very low)

---

### Q: Can I run it on battery?

**A:** Yes! Estimates:
- 10,000mAh battery: 3-5 days
- 20,000mAh battery: 1-2 weeks
- Solar charging possible

---

### Q: How to make it run faster?

**A:** Optimization tips:
1. Reduce update intervals
2. Use partial updates instead of full
3. Disable unused apps
4. Optimize image rendering

```python
# Good: only update changed area
epd.displayPartial(buffer)

# Slower: full redraw
epd.display(buffer)
```

---

### Q: What's the CPU bottleneck?

**A:** Usually image rendering to e-ink display, not computation. To improve:
1. Reduce image size/complexity
2. Optimize PIL operations
3. Cache fonts/images

---

## Backup & Data

### Q: How often should I backup?

**A:** Recommended schedule:
- **Daily:** Before making changes
- **Weekly:** Routine backup
- **Before updates:** Always backup first

---

### Q: Where should I store backups?

**A:** Multiple locations:
1. On device: `~/backups/` (local)
2. USB drive: Portable backup
3. Another computer: Off-site backup
4. Cloud: Google Drive, OneDrive (if privacy allows)

---

### Q: What if I accidentally delete a medicine?

**A:** Restore from backup:

```bash
cp ~/backups/before_delete/medicine_data.json ~/pizero_apps/
sudo systemctl restart pizero-webui
```

Or manually re-add via web UI.

---

### Q: How much storage does the data take?

**A:** Very small:
- config.json: ~5-10KB
- medicine_data.json: ~5-50KB (depends on tracking history)
- Total: <1MB

Won't be an issue even with years of history.

---

### Q: Can I export my medication history?

**A:** Yes, medicine_data.json is plain text:

```bash
# Copy for analysis
cp ~/pizero_apps/medicine_data.json ~/my_medicine_history.json

# Import into spreadsheet/database
# Or analyze with Python/Excel
```

---

### Q: Is my data permanently deleted if I reboot?

**A:** No. Data is stored on:
- MicroSD card (persistent)
- Survives power cycles
- Only deleted if you manually remove or format

---

## Updates & Upgrades

### Q: How do I update to a new version?

**A:** Follow UPGRADE_GUIDE.md:
1. Backup current setup
2. Download new version
3. Replace files
4. Update Python dependencies
5. Test

Always backup before upgrading.

---

### Q: Will upgrading delete my medicine data?

**A:** No, data files are preserved:
- medicine_data.json stays unchanged
- config.json usually compatible
- Backup anyway as safety precaution

---

### Q: How often are updates released?

**A:** Currently:
- Version 1.0: November 8, 2025
- Version 1.1+: TBD

Check GitHub/documentation for release schedule.

---

### Q: Can I downgrade to a previous version?

**A:** Yes, use rollback from backup:

```bash
cp ~/backups/before_upgrade_date/medicine_data.json ~/pizero_apps/
```

Or restore entire version from backup.

---

### Q: What if an update breaks something?

**A:** Rollback procedure:
1. Restore from backup
2. Restart services
3. Report issue with details
4. Stay on previous version until fix

See UPGRADE_GUIDE.md for detailed rollback.

---

## Troubleshooting Tips

### Q: Button not responding - what do I check first?

**A:** Troubleshooting order:
1. Verify button is pressed (hardware test)
2. Check GPIO pin connection
3. Restart menu service: `sudo systemctl restart pizero-menu`
4. Check logs: `tail /tmp/menu.log`
5. Reboot if all else fails: `sudo reboot`

---

### Q: Web server won't start - where do I look?

**A:** Check these in order:
1. Logs: `tail -50 /tmp/webserver.log`
2. Processes: `ps aux | grep web_config`
3. Port: `sudo netstat -tulpn | grep 5000`
4. Permissions: `ls -la ~/pizero_apps/`

---

### Q: Display shows nothing - basic checks?

**A:** Quick diagnostics:
1. Is display powered? (check cable)
2. Is SPI enabled? (`raspi-config`)
3. Does test script work? (see TROUBLESHOOTING.md)
4. Reboot device

---

### Q: System running slow - how to diagnose?

**A:** Check these metrics:
1. CPU: `top` (Python shouldn't exceed 20%)
2. Memory: `free -h` (should have 100+MB available)
3. Disk: `df -h /` (should have 1GB+ free)
4. Processes: `ps aux` (look for unexpected processes)

---

### Q: I'm stuck - what should I do?

**A:** Escalation path:
1. Read relevant section in TROUBLESHOOTING.md
2. Check application logs
3. Verify configuration files are valid JSON
4. Try system reboot: `sudo reboot`
5. Collect diagnostics (see TROUBLESHOOTING.md)
6. Review issue-specific guides
7. Consider factory reset if necessary

---

## Advanced Questions

### Q: Can I develop custom apps?

**A:** Yes! App template:

```python
# my_custom_app.py
import sys
sys.path.append('/home/pi/python/lib')
from TP_lib import epd2in13_V4
from PIL import Image, ImageDraw

epd = epd2in13_V4.EPD()
image = Image.new('1', (epd.width, epd.height), 255)
draw = ImageDraw.Draw(image)

# Draw your content
draw.text((10, 10), "Hello", fill=0)

epd.display(epd.getbuffer(image))
```

---

### Q: Can I integrate with smart home?

**A:** Possible integrations:
1. **IFTTT:** Trigger web hooks from home automation
2. **Home Assistant:** Add as HTTP entity
3. **Custom scripts:** Call API endpoints
4. **Webhooks:** Modify web_config.py to add hooks

---

### Q: Can I use this with a database backend?

**A:** Yes, modify app:
1. Replace JSON file reads with SQLite queries
2. Or use cloud database (requires internet)
3. Migrate data using migration script

Current JSON approach is simple and sufficient for single-user.

---

### Q: Can I add authentication to the web UI?

**A:** Yes, add Flask-Login:

```python
from flask_login import LoginManager, login_required

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/api/medicine/add')
@login_required
def add_medicine():
    # Protected endpoint
```

---

## Still Have Questions?

If your question isn't answered here:

1. **Search documentation:**
   - DEPLOYMENT_GUIDE.md
   - CONFIGURATION_REFERENCE.md
   - TROUBLESHOOTING.md

2. **Check logs:**
   - `/tmp/webserver.log`
   - `/tmp/menu.log`

3. **Review code:**
   - Source files have inline comments
   - Check function docstrings

4. **Test step-by-step:**
   - Isolate issue component
   - Test individually
   - Add debug logging

---

## Common Misconceptions

### "This is a medical device"
**Fact:** It's a personal reminder tool. Always follow doctor's instructions.

### "My data goes to the cloud"
**Fact:** All data stays locally on device. No cloud upload.

### "It works without power"
**Fact:** Requires constant power. E-ink display can show last image temporarily if powered off.

### "It's 100% accurate"
**Fact:** It can malfunction. Use as reminder, not sole medication manager.

### "It's secure out of the box"
**Fact:** No authentication by default. Use on trusted network only.

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
**Total Questions:** 100+
