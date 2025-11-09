# Upgrade Guide

**Version:** 1.0
**Last Updated:** November 8, 2025
**Current Release:** 1.0

---

## Table of Contents

1. [Pre-Upgrade Checklist](#pre-upgrade-checklist)
2. [Backup Procedures](#backup-procedures)
3. [Version-Specific Upgrades](#version-specific-upgrades)
4. [Step-by-Step Upgrade Process](#step-by-step-upgrade-process)
5. [Dependency Updates](#dependency-updates)
6. [Rollback Procedure](#rollback-procedure)
7. [Post-Upgrade Testing](#post-upgrade-testing)
8. [Migration Guides](#migration-guides)

---

## Pre-Upgrade Checklist

Before upgrading, complete this checklist:

- [ ] Note current version: `grep "Version" ~/pizero_apps/config.json` or app file headers
- [ ] Check available disk space: `df -h /`
- [ ] Backup all data (see [Backup Procedures](#backup-procedures))
- [ ] Document current configuration
- [ ] Stop all running services
- [ ] Plan maintenance window (if needed)
- [ ] Review release notes for breaking changes
- [ ] Test upgrade procedure (optional: practice on test device)

---

## Backup Procedures

### Complete System Backup

```bash
#!/bin/bash
# backup_complete.sh

BACKUP_DIR="/home/pi/backups/system_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup application files
cp -r ~/pizero_apps "$BACKUP_DIR/pizero_apps"

# Backup Python libraries
cp -r ~/python "$BACKUP_DIR/python"

# Backup system config
cp -r /etc/systemd/system/pizero* "$BACKUP_DIR/systemd_services" 2>/dev/null

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.txt" << EOF
Backup Date: $(date)
Pi Hostname: $(hostname)
Python Version: $(python3 --version)
Pip Packages: $(pip3 list)
EOF

# Compress backup
tar -czf "$BACKUP_DIR.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: $BACKUP_DIR.tar.gz"
```

Run before upgrade:

```bash
chmod +x ~/backup_complete.sh
~/backup_complete.sh
```

### Minimal Data Backup

For quick backup of just essential data:

```bash
# Create backup directory
mkdir -p ~/backups/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/backups/$(date +%Y%m%d_%H%M%S)

# Backup data files
cp ~/pizero_apps/medicine_data.json "$BACKUP_DIR/"
cp ~/pizero_apps/config.json "$BACKUP_DIR/"
cp ~/pizero_apps/web_config.py "$BACKUP_DIR/"

# Create version info
echo "Backup of version $(grep -m1 'Version' ~/pizero_apps/medicine_app.py)" > "$BACKUP_DIR/VERSION.txt"

echo "Backup: $BACKUP_DIR"
```

### Database Backup (if using SQLite)

```bash
# Backup SQLite database
cp ~/pizero_apps/medicine.db ~/pizero_apps/medicine.db.backup_$(date +%Y%m%d_%H%M%S)

# Export to JSON for safety
sqlite3 ~/pizero_apps/medicine.db ".mode json" > ~/pizero_apps/medicine_export_$(date +%Y%m%d_%H%M%S).json
```

---

## Version-Specific Upgrades

### Upgrading from 1.0 to 1.1 (Future)

**Release Date:** TBD
**Breaking Changes:** None expected
**Migration Required:** No

```bash
# Standard upgrade procedure applies
# See: Step-by-Step Upgrade Process
```

### Upgrading from 0.9 to 1.0

**Release Date:** November 8, 2025
**Breaking Changes:**
- Medicine data structure updated
- Web API endpoints changed
- Configuration format updated

**Migration Required:** Yes - see [Migration from 0.9 to 1.0](#migration-from-09-to-10)

---

## Step-by-Step Upgrade Process

### Phase 1: Preparation (5 minutes)

1. **Stop all services:**
   ```bash
   sudo systemctl stop pizero-webui pizero-menu
   # Wait for services to stop
   sleep 3
   ```

2. **Create backup:**
   ```bash
   mkdir -p ~/backups/before_upgrade_$(date +%Y%m%d_%H%M%S)
   cp ~/pizero_apps/medicine_data.json ~/backups/before_upgrade_$(date +%Y%m%d_%H%M%S)/
   cp ~/pizero_apps/config.json ~/backups/before_upgrade_$(date +%Y%m%d_%H%M%S)/
   ```

3. **Verify backup:**
   ```bash
   ls -la ~/backups/before_upgrade_*/
   ```

### Phase 2: Update Code (10 minutes)

1. **Navigate to app directory:**
   ```bash
   cd ~/pizero_apps
   ```

2. **Download new version:**

   **Option A: From Git Repository**
   ```bash
   git fetch origin
   git pull origin main
   ```

   **Option B: From Release Package**
   ```bash
   # Extract new version
   tar -xzf pizero_apps_1_1.tar.gz -C ~/
   ```

3. **Verify file integrity:**
   ```bash
   # Check Python syntax
   python3 -m py_compile *.py

   # Check JSON config
   python3 -m json.tool config.json > /dev/null && echo "Config OK"
   python3 -m json.tool medicine_data.json > /dev/null && echo "Data OK"
   ```

### Phase 3: Update Dependencies (5 minutes)

```bash
# Update pip itself
pip3 install --upgrade pip

# Install/update required packages
pip3 install -r requirements.txt --upgrade

# Verify installation
pip3 list | grep -E "Flask|Pillow|gpiozero"
```

### Phase 4: Migrate Configuration (if needed)

See version-specific migration guides below.

### Phase 5: Test Before Restart

```bash
# Test syntax
python3 -c "import medicine_app; print('medicine_app OK')"
python3 -c "import web_config; print('web_config OK')"

# Test configuration loading
python3 << 'EOF'
import json
data = json.load(open('config.json'))
medicines = json.load(open('medicine_data.json'))
print(f"Config sections: {list(data.keys())}")
print(f"Medicines loaded: {len(medicines['medicines'])}")
EOF
```

### Phase 6: Restart Services (5 minutes)

```bash
# Start services
sudo systemctl start pizero-webui
sleep 2
sudo systemctl start pizero-menu

# Verify startup
sudo systemctl status pizero-webui
sudo systemctl status pizero-menu
```

### Phase 7: Post-Upgrade Verification (10 minutes)

```bash
# Check if services are running
ps aux | grep python3 | grep -v grep

# Test web interface
curl http://localhost:5000/ | head -20

# Check logs for errors
tail /tmp/webserver.log
tail /tmp/menu.log
```

---

## Dependency Updates

### Check for Updates

```bash
# List outdated packages
pip3 list --outdated

# Check specific package
pip3 show Flask | grep Version
```

### Safe Dependency Update

```bash
# Update specific package (with version constraint)
pip3 install Flask==2.0.3  # Specific version
pip3 install "Flask>=2.0,<3.0"  # Version range

# Update with test
pip3 install --dry-run Flask --upgrade  # See what would change
pip3 install Flask --upgrade  # Apply update

# Verify after update
python3 -c "import flask; print(flask.__version__)"
```

### Critical Dependencies

These versions are tested and known to work:

```
Flask==2.0.0+
Pillow==8.0.0+
gpiozero==1.6.2+
marshmallow==3.14.0+
```

**Do not upgrade these to major versions without testing.**

### Python Version Upgrade

If upgrading Python itself:

```bash
# Check current version
python3 --version

# For Python 3.9 to 3.10:
sudo apt-get install python3.10 python3.10-venv python3.10-dev

# Reinstall packages with new version
python3.10 -m pip install -r requirements.txt

# Test before switching
python3.10 -c "import flask; print('OK')"

# Update symlinks (if needed)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
```

---

## Rollback Procedure

If upgrade fails or causes issues, rollback using backup.

### Quick Rollback (< 5 minutes)

```bash
# Stop services
sudo systemctl stop pizero-webui pizero-menu

# Restore backup
BACKUP_DIR=~/backups/before_upgrade_20251108_150000  # Use your backup date
cp "$BACKUP_DIR/config.json" ~/pizero_apps/
cp "$BACKUP_DIR/medicine_data.json" ~/pizero_apps/

# Restart services
sudo systemctl start pizero-webui pizero-menu

# Verify
curl http://localhost:5000/api/config
```

### Complete System Rollback

If Python code is broken:

```bash
# Stop services
sudo systemctl stop pizero-webui pizero-menu

# Restore from full backup
tar -xzf ~/backups/system_20251108_140000.tar.gz -C ~/

# Reinstall dependencies
pip3 install -r ~/pizero_apps/requirements.txt

# Restart services
sudo systemctl start pizero-webui pizero-menu
```

### Data-Only Rollback

If you only want to restore data, not code:

```bash
# Restore data files
cp ~/backups/before_upgrade_20251108_150000/medicine_data.json ~/pizero_apps/

# Verify data integrity
python3 -m json.tool ~/pizero_apps/medicine_data.json > /dev/null && echo "Data OK"

# Restart web server to reload data
sudo systemctl restart pizero-webui
```

---

## Post-Upgrade Testing

### Smoke Test (5 minutes)

Quick verification that system works:

```bash
# 1. Web server responds
curl -s http://localhost:5000/ | grep -q "<!DOCTYPE" && echo "✓ Web server OK" || echo "✗ Web server FAILED"

# 2. API works
curl -s http://localhost:5000/api/config | grep -q "weather" && echo "✓ API OK" || echo "✗ API FAILED"

# 3. Medicine data loads
curl -s http://localhost:5000/api/medicine/data | grep -q "medicines" && echo "✓ Medicine data OK" || echo "✗ Medicine data FAILED"

# 4. Services running
ps aux | grep "web_config.py" | grep -v grep > /dev/null && echo "✓ Web config running" || echo "✗ Web config NOT running"
ps aux | grep "menu_button.py" | grep -v grep > /dev/null && echo "✓ Menu running" || echo "✗ Menu NOT running"
```

### Full Test Suite

```bash
# Test display
python3 << 'EOF'
import sys
sys.path.append('/home/pi/python/lib')
try:
    from TP_lib import epd2in13_V4
    epd = epd2in13_V4.EPD()
    print(f"✓ Display OK: {epd.width}x{epd.height}")
except Exception as e:
    print(f"✗ Display FAILED: {e}")
EOF

# Test GPIO
python3 << 'EOF'
from gpiozero import Button
try:
    button = Button(3)
    print("✓ GPIO OK")
except Exception as e:
    print(f"✗ GPIO FAILED: {e}")
EOF

# Test each app
cd ~/pizero_apps
for app in weather_cal_app medicine_app pomodoro_app; do
    python3 -c "import importlib.util; spec = importlib.util.spec_from_file_location('app', '$app.py'); module = importlib.util.module_from_spec(spec)" && echo "✓ $app syntax OK" || echo "✗ $app syntax FAILED"
done
```

### Visual Testing

1. **Display Test:**
   - Press button on device
   - Verify menu appears
   - Navigate between apps
   - Launch medicine app
   - Verify display updates

2. **Web UI Test:**
   - Open browser to `http://<pi-ip>:5000`
   - Check all menu sections load
   - Modify a setting
   - Verify change applied
   - Check logs for errors

3. **Functionality Test:**
   - Add new medicine via web UI
   - Check display shows new medicine
   - Mark medicine as taken
   - Verify pill count decreased

### Performance Test

```bash
# Check system resources
free -h              # Memory usage
df -h /              # Disk usage
top -bn1 | head -20  # CPU usage

# Check service memory usage
ps aux | grep python3 | grep -v grep | awk '{print $6}' | paste -sd+ | bc  # Total Python memory
```

---

## Migration Guides

### Migration from 0.9 to 1.0

**Changes:**
- New JSON structure for medicine_data.json
- Updated config.json format
- Web API endpoints modified
- Python package versions updated

**Migration Steps:**

1. **Backup 0.9 version:**
   ```bash
   mkdir -p ~/backups/v0.9_backup
   cp ~/pizero_apps/* ~/backups/v0.9_backup/
   ```

2. **Export medicine data from 0.9:**
   ```bash
   python3 << 'EOF'
   # Load old format
   import json
   with open('/home/pi/backups/v0.9_backup/medicine_data.json') as f:
       old_data = json.load(f)

   # Save for reference
   with open('/tmp/medicine_data_v0.9_export.json', 'w') as f:
       json.dump(old_data, f, indent=2)
   print("Old format saved to /tmp/medicine_data_v0.9_export.json")
   EOF
   ```

3. **Migrate to new format:**
   ```bash
   python3 << 'EOF'
   import json
   from datetime import datetime

   # Load old data
   with open('/tmp/medicine_data_v0.9_export.json') as f:
       old = json.load(f)

   # Create new structure
   new_data = {
       "medicines": [],
       "tracking": {},
       "time_windows": {
           "morning": {"start": "06:00", "end": "10:00"},
           "afternoon": {"start": "12:00", "end": "16:00"},
           "evening": {"start": "18:00", "end": "22:00"},
           "night": {"start": "22:00", "end": "23:59"}
       }
   }

   # Migrate medicines
   for old_med in old.get('medicines', []):
       new_med = {
           "id": old_med.get('id', f"med_{int(datetime.now().timestamp()*1000)}"),
           "name": old_med.get('name'),
           "dosage": old_med.get('dosage'),
           "time_window": old_med.get('time_window', 'morning'),
           "window_start": old_med.get('window_start', '06:00'),
           "window_end": old_med.get('window_end', '10:00'),
           "days": old_med.get('days', ["mon","tue","wed","thu","fri","sat","sun"]),
           "with_food": old_med.get('with_food', False),
           "notes": old_med.get('notes', ''),
           "active": old_med.get('active', True),
           "pills_remaining": old_med.get('pills_remaining', 0),
           "pills_per_dose": old_med.get('pills_per_dose', 1),
           "low_stock_threshold": old_med.get('low_stock_threshold', 10)
       }
       new_data['medicines'].append(new_med)

   # Migrate tracking
   for date_str, entries in old.get('tracking', {}).items():
       new_data['tracking'][date_str] = entries

   # Save new format
   with open('/home/pi/pizero_apps/medicine_data.json', 'w') as f:
       json.dump(new_data, f, indent=2)

   print(f"✓ Migrated {len(new_data['medicines'])} medicines")
   EOF
   ```

4. **Verify migration:**
   ```bash
   python3 -m json.tool ~/pizero_apps/medicine_data.json | head -50
   ```

5. **Continue with standard upgrade process**

### Config Migration

```bash
# The upgrade script should handle this, but if needed manually:

python3 << 'EOF'
import json

# Load old config
with open('/tmp/config_v0.9.json') as f:
    old_config = json.load(f)

# Create new config (use template from CONFIGURATION_REFERENCE.md)
new_config = {
    "weather": old_config.get("weather", {}),
    "mbta": old_config.get("mbta", {}),
    "medicine": old_config.get("medicine", {}),
    # ... other sections
}

with open('/home/pi/pizero_apps/config.json', 'w') as f:
    json.dump(new_config, f, indent=2)

print("✓ Config migrated")
EOF
```

---

## Upgrade Troubleshooting

### Issue: Service Won't Start After Upgrade

```
systemctl[123]: pizero-webui.service: Main process exited, code=1/FAILURE
```

**Solution:**

```bash
# Check error
sudo systemctl status pizero-webui -l

# View detailed logs
journalctl -u pizero-webui -n 50

# Test Python imports
python3 -c "import flask, gpiozero, PIL"

# Reinstall dependencies
pip3 install --upgrade --force-reinstall -r requirements.txt

# Restart
sudo systemctl restart pizero-webui
```

### Issue: Configuration Not Loading

```
json.decoder.JSONDecodeError: Expecting value
```

**Solution:**

```bash
# Validate JSON
python3 -m json.tool ~/pizero_apps/config.json

# Restore from backup if corrupted
cp ~/backups/before_upgrade_20251108_150000/config.json ~/pizero_apps/

# Restart
sudo systemctl restart pizero-webui
```

### Issue: Medicine Data Lost After Upgrade

**Solution:**

```bash
# Restore from backup
BACKUP_DIR=~/backups/before_upgrade_20251108_150000
cp "$BACKUP_DIR/medicine_data.json" ~/pizero_apps/

# Verify data
python3 -m json.tool ~/pizero_apps/medicine_data.json | grep "name"

# Restart
sudo systemctl restart pizero-webui
```

### Issue: Performance Degradation After Upgrade

**Solution:**

```bash
# Check disk space
df -h /

# Check memory usage
free -h

# Monitor processes
top -bn1 | head -20

# Restart services to clear memory
sudo systemctl restart pizero-webui pizero-menu

# Check for large log files
du -sh /tmp/*.log /var/log/syslog
```

---

## Upgrade Automation Script

For more complex upgrades, use this script:

```bash
#!/bin/bash
# upgrade.sh - Automated upgrade script

set -e  # Exit on error

VERSION="1.1"
BACKUP_DIR="$HOME/backups/upgrade_$(date +%Y%m%d_%H%M%S)"

echo "Pi Zero 2W Medicine Tracker - Upgrade Script"
echo "Target Version: $VERSION"
echo "=========================================="

# Phase 1: Backup
echo "[1/6] Creating backup..."
mkdir -p "$BACKUP_DIR"
cp ~/pizero_apps/medicine_data.json "$BACKUP_DIR/"
cp ~/pizero_apps/config.json "$BACKUP_DIR/"
echo "✓ Backup: $BACKUP_DIR"

# Phase 2: Stop services
echo "[2/6] Stopping services..."
sudo systemctl stop pizero-webui pizero-menu 2>/dev/null || true
sleep 2
echo "✓ Services stopped"

# Phase 3: Update code
echo "[3/6] Updating code..."
cd ~/pizero_apps
git pull origin main || tar -xzf pizero_apps_$VERSION.tar.gz -C ~/
echo "✓ Code updated"

# Phase 4: Update dependencies
echo "[4/6] Updating dependencies..."
pip3 install -r requirements.txt --upgrade
echo "✓ Dependencies updated"

# Phase 5: Validate
echo "[5/6] Validating..."
python3 -m json.tool config.json > /dev/null || exit 1
python3 -m json.tool medicine_data.json > /dev/null || exit 1
echo "✓ Configuration valid"

# Phase 6: Restart
echo "[6/6] Starting services..."
sudo systemctl start pizero-webui
sleep 2
sudo systemctl start pizero-menu
sleep 2

# Verify
if curl -s http://localhost:5000/ > /dev/null; then
    echo "✓ Web server OK"
else
    echo "✗ Web server failed to start"
    echo "Rolling back from backup: $BACKUP_DIR"
    cp "$BACKUP_DIR/medicine_data.json" ~/pizero_apps/
    cp "$BACKUP_DIR/config.json" ~/pizero_apps/
    sudo systemctl restart pizero-webui
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Upgrade to $VERSION completed successfully!"
echo "Backup preserved at: $BACKUP_DIR"
echo "=========================================="
```

Make executable and run:

```bash
chmod +x ~/upgrade.sh
~/upgrade.sh
```

---

**Document Version:** 1.0
**Last Updated:** November 8, 2025
**Next Update:** Expected with version 1.1
