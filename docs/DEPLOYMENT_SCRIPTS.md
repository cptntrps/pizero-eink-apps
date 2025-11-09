# Pi Zero 2W Medicine Tracking System - Deployment Scripts

**Version:** 1.0
**Last Updated:** November 8, 2025
**Author:** Claude Code Assistant

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Scripts Guide](#scripts-guide)
4. [Common Workflows](#common-workflows)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Reference](#reference)

---

## Overview

This documentation covers the deployment automation system for the Pi Zero 2W Medicine Tracking System. Five complementary shell scripts provide complete lifecycle management:

| Script | Purpose | Trigger |
|--------|---------|---------|
| `install.sh` | Initial setup and dependency installation | First deployment |
| `deploy.sh` | Deploy code updates with automatic backup | Code changes |
| `rollback.sh` | Restore previous deployment version | Failed deployment |
| `health_check.sh` | Comprehensive system health verification | Scheduled or on-demand |
| `monitor.sh` | Real-time system and application monitoring | Continuous or diagnostic |

### Key Features

- **Error Handling:** Graceful error handling with detailed logging
- **Dry-Run Mode:** Preview changes without execution
- **Automatic Backup:** Backup before deployment with rollback capability
- **Health Monitoring:** Comprehensive health checks and metrics
- **Clear Output:** Structured, color-coded output with timestamps
- **Logging:** All operations logged to timestamped files
- **Flexibility:** Various options for different use cases

---

## Quick Start

### Prerequisites

```bash
# Required commands
python3 (≥3.7)
pip3
git
systemctl
wget
curl

# Required user/group
pizero2w:pizero2w (user and group)

# Required directories
/home/pizero2w/pizero_apps
/var/log/pizero-app
```

### Initial Installation

```bash
# Make scripts executable
chmod +x /home/user/pizerowgpio/scripts/*.sh

# Run installation with sudo
cd /home/user/pizerowgpio/scripts
sudo ./install.sh

# Verify installation
./health_check.sh
```

### Deploy an Update

```bash
cd /home/user/pizerowgpio/scripts

# Preview changes (dry-run)
./deploy.sh --dry-run

# Deploy with automatic backup
./deploy.sh

# Check health after deployment
./health_check.sh
```

### Rollback if Needed

```bash
cd /home/user/pizerowgpio/scripts

# Rollback to most recent backup
./rollback.sh

# Or specify a specific backup
./rollback.sh --backup-id 20251108_143022
```

---

## Scripts Guide

### 1. install.sh - Initial Installation

**Purpose:** Install application and all dependencies on a fresh Raspberry Pi

**Requirements:**
- Root/sudo privileges
- Python 3 and pip3 installed
- Internet connectivity
- At least 100MB free disk space

**Usage:**

```bash
# Standard installation
sudo ./install.sh

# Dry-run preview
sudo ./install.sh --dry-run

# Quiet mode (log only)
sudo ./install.sh --quiet

# Show help
./install.sh --help
```

**What It Does:**

1. **Prerequisites Check**
   - Verifies Python 3 availability
   - Checks for required commands (pip3, git, systemctl, wget)
   - Confirms Raspberry Pi device
   - Validates disk space

2. **System Updates**
   - Updates system package lists
   - May update existing packages

3. **Python Dependencies**
   - Flask 2.3.3 (web framework)
   - Requests 2.31.0 (HTTP client)
   - Pillow 10.0.0 (image processing)
   - RPi.GPIO 0.7.0 (GPIO control)
   - NumPy 1.21.6 (numerical computing)

4. **Directory Structure**
   - Creates `/home/pizero2w/pizero_apps`
   - Creates `/home/pizero2w/pizero_apps/backups`
   - Creates `/var/log/pizero-app`
   - Creates `/tmp/pizero-tmp`

5. **Application Files**
   - Copies Python applications
   - Copies display library
   - Deploys configuration files

6. **Permissions**
   - Sets ownership: `pizero2w:pizero2w`
   - Sets directory permissions: 755
   - Sets file permissions: 644

7. **Systemd Services**
   - Creates `pizero-webserver.service`
   - Creates `pizero-menu.service`
   - Enables auto-start (optional)

8. **Verification**
   - Validates installation completeness
   - Confirms Python packages

**Output Example:**

```
╔════════════════════════════════════════════════════════════════╗
║  Pi Zero 2W Medicine Tracking System - Installation Script    ║
║  Version 1.0                                                  ║
╚════════════════════════════════════════════════════════════════╝

[INFO] Running with appropriate privileges
━━━ Checking Prerequisites ━━━
[✓] Python 3.11.2 found
[✓] pip3 available
[INFO] Disk space available: 2048000KB
...
Installation Complete!
```

**Next Steps After Installation:**

```bash
# Start services manually
sudo systemctl start pizero-webserver
sudo systemctl start pizero-menu

# Enable auto-start (optional)
sudo systemctl enable pizero-webserver
sudo systemctl enable pizero-menu

# Verify
./health_check.sh
```

---

### 2. deploy.sh - Deploy Updates

**Purpose:** Deploy code updates with automatic backup and validation

**Requirements:**
- Application already installed (via install.sh)
- Git repository (optional, for version tracking)
- Write access to application directory

**Usage:**

```bash
# Deploy with automatic backup
./deploy.sh

# Dry-run preview
./deploy.sh --dry-run

# Deploy without creating backup
./deploy.sh --no-backup

# Deploy despite uncommitted git changes
./deploy.sh --force

# Quiet mode
./deploy.sh --quiet

# Combine options
./deploy.sh --dry-run --force
```

**What It Does:**

1. **Verification**
   - Checks application directory exists
   - Checks git status (if applicable)

2. **Backup Creation**
   - Creates timestamped backup directory
   - Backs up all Python files
   - Backs up display library
   - Stores deployment info
   - Location: `/home/pizero2w/pizero_apps/backups/backup_YYYYMMDD_HHMMSS`

3. **Service Management**
   - Stops web server
   - Stops menu system
   - Waits for graceful shutdown

4. **File Deployment**
   - Copies updated Python files
   - Copies display library
   - Updates configuration

5. **Validation**
   - Validates JSON configuration files
   - Sets correct permissions
   - Verifies file integrity

6. **Service Restart**
   - Starts web server
   - Starts menu system
   - Verifies startup

7. **Health Checks**
   - Checks service status
   - Verifies web server responds
   - Validates configuration

8. **Cleanup**
   - Removes old backups (keeps 5 most recent)

**Backup Structure:**

```
/home/pizero2w/pizero_apps/backups/
├── backup_20251108_140000/
│   ├── medicine_app.py
│   ├── menu_button.py
│   ├── web_config.py
│   ├── config.json
│   ├── display/
│   └── BACKUP_INFO.txt
├── backup_20251108_143022/
│   └── ...
└── backup_20251108_150000/
    └── ...
```

**Deployment Workflow:**

```bash
# Step 1: Make changes locally
# Edit files, test locally

# Step 2: Preview deployment
./deploy.sh --dry-run

# Step 3: Deploy changes
./deploy.sh

# Step 4: Verify
./health_check.sh

# Step 5 (if needed): Rollback
./rollback.sh
```

---

### 3. rollback.sh - Rollback to Previous Version

**Purpose:** Restore application from a previous deployment backup

**Requirements:**
- Existing backups in `/home/pizero2w/pizero_apps/backups/`
- Write access to application directory

**Usage:**

```bash
# Rollback to most recent backup (interactive)
./rollback.sh

# Rollback to specific backup
./rollback.sh --backup-id 20251108_143022

# Dry-run preview
./rollback.sh --dry-run

# Quiet mode
./rollback.sh --quiet
```

**What It Does:**

1. **Backup Discovery**
   - Lists available backups
   - Displays backup dates, sizes, and info
   - Identifies most recent

2. **Backup Selection**
   - Uses most recent by default
   - Can specify specific backup ID
   - Validates backup integrity

3. **Validation**
   - Checks for required files
   - Verifies file integrity
   - Displays backup information

4. **User Confirmation**
   - Shows backup details
   - Lists actions to be performed
   - Requires explicit "yes" confirmation

5. **Rollback Process**
   - Stops services
   - Creates emergency backup of current files
   - Restores files from selected backup
   - Restarts services
   - Verifies service health

**Available Backups Display:**

```
━━━ Available Backups ━━━

ID (Timestamp)        Path                           Size
─────────────────────────────────────────────────────────
backup_20251108_150000 backup_20251108_150000        2.3M
  ^ Most recent backup (recommended)
backup_20251108_143022 backup_20251108_143022        2.3M
backup_20251107_120500 backup_20251107_120500        2.2M
```

**Rollback Scenarios:**

```bash
# Scenario 1: Bad deployment, rollback to previous
./rollback.sh
# Uses most recent backup automatically

# Scenario 2: Rollback to specific version
./rollback.sh --backup-id 20251107_120500
# Restores from that specific date

# Scenario 3: Preview before rollback
./rollback.sh --dry-run
# Shows what would happen

# Scenario 4: Emergency rollback
./rollback.sh --quiet
# Minimal output, just perform rollback
```

---

### 4. health_check.sh - Comprehensive Health Check

**Purpose:** Verify system health and application status

**Requirements:**
- No special privileges required
- Most checks work on any system

**Usage:**

```bash
# Standard health check (text output)
./health_check.sh

# JSON output (for parsing/monitoring)
./health_check.sh --format json

# Detailed text output
./health_check.sh --verbose

# Combined options
./health_check.sh --format json --verbose

# Show help
./health_check.sh --help
```

**What It Checks:**

1. **Services**
   - pizero-webserver status
   - pizero-menu status
   - Service responsiveness

2. **Files and Directories**
   - Application directory exists
   - Required files present
   - File sizes

3. **Configuration**
   - config.json valid JSON
   - medicine_data.json valid JSON
   - Configuration integrity

4. **Permissions**
   - Directory permissions
   - File permissions
   - Ownership

5. **System Resources**
   - Disk space usage
   - CPU utilization
   - Memory usage
   - Process count

6. **Network**
   - Internet connectivity
   - Local network interfaces
   - IP address

7. **Web Server**
   - HTTP response
   - Port 5000 listening
   - Connectivity

8. **Logs**
   - Log directory exists
   - Recent errors
   - Log file sizes

9. **Backups**
   - Backup directory exists
   - Backup count
   - Most recent backup

10. **Systemd**
    - Services enabled at boot
    - Auto-start status

**Text Output Example:**

```
╔════════════════════════════════════════════════════════════════╗
║  Pi Zero 2W Medicine Tracking System - Health Check           ║
║  Version 1.0 | Generated: 2025-11-08 15:00:22                 ║
╚════════════════════════════════════════════════════════════════╝

━━━ DETAILED RESULTS ━━━

SERVICES
───────────────────────────────────────────────────────────────
  ✓ pizero-webserver: Service is running
     Active: active
  ✓ pizero-menu: Service is running
     Active: active

FILES
───────────────────────────────────────────────────────────────
  ✓ App Directory: Directory exists
     Path: /home/pizero2w/pizero_apps, Size: 2.3M
  ✓ medicine_app.py: File exists
     Size: 45K

[... more checks ...]

━━━ HEALTH CHECK SUMMARY ━━━

Overall Status: HEALTHY

Checks Performed: 20
  Passed: 18
  Warnings: 2
  Failed: 0
```

**JSON Output Example:**

```json
{
  "timestamp": "2025-11-08T15:00:22Z",
  "overall_status": "HEALTHY",
  "summary": {
    "total_checks": 20,
    "passed": 18,
    "warnings": 2,
    "failed": 0
  },
  "checks": [
    {
      "category": "SERVICES",
      "name": "pizero-webserver",
      "status": "PASS",
      "message": "Service is running",
      "details": "Active: active"
    },
    ...
  ]
}
```

**Exit Codes:**

- `0` = HEALTHY (all checks passed)
- `1` = WARNING (some issues detected)
- `2` = UNHEALTHY (critical failures)

**Common Issues Detected:**

```
STATUS          CAUSE                          RESOLUTION
─────────────────────────────────────────────────────────────
FAIL: Service   Service not running            systemctl start service
FAIL: File      Missing required file          ./deploy.sh
WARN: Disk      >80% full                      Clean up old logs
WARN: Memory    >80% used                      Restart services
WARN: No Backup No recent backups              Run deploy.sh
```

---

### 5. monitor.sh - Real-Time Monitoring

**Purpose:** Continuously monitor application and system metrics

**Requirements:**
- No special privileges required
- Useful for diagnostics and performance monitoring

**Usage:**

```bash
# Monitor with default 5-second interval
./monitor.sh

# Custom update interval
./monitor.sh --interval 10

# Monitor for specific duration
./monitor.sh --duration 30

# Log output to file
./monitor.sh --log-file /tmp/monitoring.log

# Combine options
./monitor.sh --interval 5 --duration 60 --log-file /tmp/monitor.log

# Quiet mode (no screen output)
./monitor.sh --quiet --log-file /tmp/monitor.log

# Show help
./monitor.sh --help
```

**What It Monitors:**

1. **Services**
   - Service status (running/stopped)
   - Service uptime
   - Recent restarts

2. **System Resources**
   - CPU usage (with threshold warnings)
   - Memory usage (with threshold warnings)
   - Disk usage (with threshold warnings)
   - Process count

3. **Network**
   - Network interface status
   - Data transferred (RX/TX)
   - Connectivity

4. **Application**
   - Missing files count
   - Python file count
   - Log directory size
   - Recent error count

5. **Web Server**
   - Response status
   - Active connections
   - Port binding

**Monitor Display Example:**

```
╔════════════════════════════════════════════════════════════════╗
║  Pi Zero 2W Medicine Tracking System - Monitoring              ║
║  Version 1.0                                                  ║
╚════════════════════════════════════════════════════════════════╝

Interval: 5s | Duration: ∞
Press Ctrl+C to stop monitoring

━━━ SERVICES ━━━
pizero-webserver         ● Running (uptime: 2d 5h 30m)
pizero-menu              ● Running (uptime: 2d 5h 25m)

━━━ SYSTEM RESOURCES ━━━
CPU Usage:       15.3%        Memory Usage:    42.1%        Disk Usage:      65.2%
Processes:       145          Network (wlan0): RX: 2.45MB | TX: 1.23MB

━━━ APPLICATION ━━━
App Directory:   /home/pizero2w/pizero_apps   Missing Files:   0          Log Size:        1.2M
Python Files:    8            Recent Errors:   0

━━━ WEB SERVER ━━━
Web Server:      Responding (HTTP 200)
Connections:     2

━━━ MONITORING ━━━
Last Update:     2025-11-08 15:02:30

[Refreshes every 5 seconds]
```

**Monitoring Workflow:**

```bash
# Diagnostic monitoring (1 minute, 5-second intervals)
./monitor.sh --duration 1

# Long-term monitoring (60 minutes, log to file)
./monitor.sh --interval 60 --duration 60 --log-file monitoring.log

# Continuous monitoring (Ctrl+C to stop)
./monitor.sh

# Background monitoring with logging
./monitor.sh --log-file /tmp/monitor.log &
```

**Threshold Warnings:**

- **CPU:** > 80% = warning (shown in red)
- **Memory:** > 80% = warning (shown in red)
- **Disk:** > 80% = warning (shown in red)

---

## Common Workflows

### Workflow 1: Fresh Installation

```bash
# Step 1: Run installation
cd /home/user/pizerowgpio/scripts
sudo ./install.sh

# Step 2: Verify installation
./health_check.sh

# Step 3: Manually start services (if not auto-starting)
sudo systemctl start pizero-webserver
sudo systemctl start pizero-menu

# Step 4: Test
./health_check.sh
./monitor.sh --duration 1
```

### Workflow 2: Deploy Code Update

```bash
# Step 1: Preview deployment
./deploy.sh --dry-run

# Step 2: Deploy
./deploy.sh

# Step 3: Quick verification
./health_check.sh --format json | grep overall_status

# Step 4: If issues, rollback
./rollback.sh
```

### Workflow 3: Handle Deployment Failure

```bash
# Step 1: Check system status
./health_check.sh --verbose

# Step 2: Review logs
tail -f /var/log/pizero-app/webserver.log

# Step 3: Rollback immediately
./rollback.sh --dry-run
./rollback.sh

# Step 4: Investigate root cause
# Check git diff, config issues, etc.
```

### Workflow 4: Continuous Monitoring

```bash
# Terminal 1: Start monitoring
./monitor.sh --interval 10

# Terminal 2: Run deployment in background
./deploy.sh --log-file /tmp/deploy.log

# Terminal 3: Check logs
tail -f /tmp/deploy.log
```

### Workflow 5: Scheduled Health Checks

```bash
# Add to crontab for automated checks
crontab -e

# Add this line (runs health check every hour):
0 * * * * /home/user/pizerowgpio/scripts/health_check.sh --format json >> /tmp/health_checks.log 2>&1

# Or every 5 minutes:
*/5 * * * * /home/user/pizerowgpio/scripts/health_check.sh --quiet >> /tmp/health.log 2>&1
```

---

## Advanced Usage

### Environment Variables

```bash
# Set application directory
export APP_DIR="/custom/app/path"

# Enable verbose logging
export VERBOSE=true

# Custom log directory
export LOG_DIR="/custom/log/path"
```

### Chaining Scripts

```bash
# Deploy and monitor for 5 minutes
./deploy.sh && ./monitor.sh --duration 5

# Automatic rollback if health check fails
./deploy.sh && ./health_check.sh || ./rollback.sh
```

### Integration with CI/CD

```bash
#!/bin/bash
# deploy.yaml or similar

deploy:
  script:
    - ./scripts/deploy.sh --dry-run  # Preview
    - ./scripts/deploy.sh             # Deploy
    - ./scripts/health_check.sh       # Verify
    - |
      if [ $? -ne 0 ]; then
        ./scripts/rollback.sh
        exit 1
      fi
```

### Custom Health Checks

```bash
# Add custom checks by extending health_check.sh
# Or create your own script that calls health_check.sh:

#!/bin/bash
./health_check.sh --format json | jq '.overall_status'
```

### Monitoring with Webhooks

```bash
# Send health status to monitoring service:

#!/bin/bash
STATUS=$(./health_check.sh --format json)
curl -X POST https://monitoring.example.com/health \
  -H "Content-Type: application/json" \
  -d "$STATUS"
```

---

## Troubleshooting

### Script Permission Issues

```bash
# Make scripts executable
chmod +x /home/user/pizerowgpio/scripts/*.sh

# Verify permissions
ls -la /home/user/pizerowgpio/scripts/
```

### Installation Fails with "Permission Denied"

```bash
# Must run with sudo
sudo ./install.sh

# Check user
whoami  # Should output "root"
```

### Deployment Fails to Stop Services

```bash
# Check service status
systemctl status pizero-webserver
systemctl status pizero-menu

# Manually stop services
sudo systemctl stop pizero-webserver
sudo systemctl stop pizero-menu

# Check for hung processes
ps aux | grep python
sudo pkill -f python3
```

### Rollback Fails to Find Backups

```bash
# Check backup directory
ls -la /home/pizero2w/pizero_apps/backups/

# If empty, create backup from deploy
./deploy.sh  # Creates backup
./rollback.sh  # Now has backup available
```

### Health Check Shows Warnings

```bash
# View detailed health information
./health_check.sh --verbose

# For JSON parsing:
./health_check.sh --format json | jq '.checks[] | select(.status=="WARN")'

# Check specific category:
./health_check.sh --verbose | grep -A 5 "SYSTEM"
```

### Monitor Script Exits Immediately

```bash
# Check for errors in previous logs
cat /home/user/pizerowgpio/logs/monitor_*.log

# Try with verbose output
./monitor.sh --verbose

# Check dependencies
which top curl free
```

### Git Status Check Prevents Deployment

```bash
# Option 1: Commit changes
git add .
git commit -m "Deploy changes"
./deploy.sh

# Option 2: Force deployment (for emergency)
./deploy.sh --force

# Option 3: Check what changed
git status
git diff
```

---

## Best Practices

### 1. Always Preview Before Deploying

```bash
./deploy.sh --dry-run  # Always run this first
./deploy.sh            # Then deploy
```

### 2. Create Health Baseline

```bash
# Run health check immediately after installation
./health_check.sh > /tmp/baseline_health.txt

# Compare with future runs
./health_check.sh > /tmp/current_health.txt
diff /tmp/baseline_health.txt /tmp/current_health.txt
```

### 3. Monitor During Critical Operations

```bash
# Terminal 1: Start monitoring
./monitor.sh

# Terminal 2: Perform operation
./deploy.sh
```

### 4. Keep Backups Organized

```bash
# Manually organize important backups
cp -r /home/pizero2w/pizero_apps/backups/backup_* \
      /home/pizero2w/pizero_apps/backups/archive/

# Keep script-created backups for rollback
ls -t /home/pizero2w/pizero_apps/backups/ | tail -5
```

### 5. Log Important Operations

```bash
# Redirect output to file
./deploy.sh 2>&1 | tee /tmp/deploy_$(date +%s).log
./health_check.sh >> /tmp/health_$(date +%s).log
```

### 6. Regular Health Checks

```bash
# Schedule daily health checks
echo "0 2 * * * /home/user/pizerowgpio/scripts/health_check.sh --format json >> /var/log/health_checks.log" | sudo crontab -
```

### 7. Backup Before Major Changes

```bash
# Always deploy before making config changes
./deploy.sh  # Creates backup
# Then make changes
# If needed, rollback
./rollback.sh
```

### 8. Test Rollback Procedure

```bash
# Periodically test rollback
./deploy.sh  # Creates new backup
./health_check.sh  # Verify current state
./rollback.sh --dry-run  # Preview rollback
# Don't actually rollback unless needed
```

---

## Reference

### Directory Structure

```
/home/user/pizerowgpio/
├── scripts/
│   ├── install.sh
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── health_check.sh
│   └── monitor.sh
├── logs/
│   ├── install_*.log
│   ├── deploy_*.log
│   ├── rollback_*.log
│   ├── health_check_*.log
│   └── monitor_*.log
└── docs/
    └── DEPLOYMENT_SCRIPTS.md

/home/pizero2w/pizero_apps/
├── backups/
│   ├── backup_20251108_140000/
│   ├── backup_20251108_143022/
│   └── backup_20251108_150000/
├── medicine_app.py
├── menu_button.py
├── web_config.py
├── config.json
├── medicine_data.json
└── display/

/var/log/pizero-app/
├── webserver.log
└── menu.log
```

### Log File Locations

| Operation | Log File | View Command |
|-----------|----------|--------------|
| Installation | `/home/user/pizerowgpio/logs/install_*.log` | `tail -f logs/install_*.log` |
| Deployment | `/home/user/pizerowgpio/logs/deploy_*.log` | `tail -f logs/deploy_*.log` |
| Rollback | `/home/user/pizerowgpio/logs/rollback_*.log` | `tail -f logs/rollback_*.log` |
| Health Check | `/home/user/pizerowgpio/logs/health_check_*.log` | `tail -f logs/health_check_*.log` |
| Monitoring | `/home/user/pizerowgpio/logs/monitor_*.log` | `tail -f logs/monitor_*.log` |
| Web Server | `/var/log/pizero-app/webserver.log` | `tail -f /var/log/pizero-app/webserver.log` |
| Menu System | `/var/log/pizero-app/menu.log` | `tail -f /var/log/pizero-app/menu.log` |

### Command Reference

```bash
# Installation
sudo ./install.sh
sudo ./install.sh --dry-run

# Deployment
./deploy.sh
./deploy.sh --dry-run
./deploy.sh --force
./deploy.sh --no-backup

# Rollback
./rollback.sh
./rollback.sh --backup-id 20251108_143022
./rollback.sh --dry-run

# Health Check
./health_check.sh
./health_check.sh --format json
./health_check.sh --verbose

# Monitoring
./monitor.sh
./monitor.sh --interval 10
./monitor.sh --duration 60
./monitor.sh --log-file /tmp/monitor.log
```

### Configuration Files

**config.json:** Application settings
```json
{
  "medicine": {
    "data_file": "/home/pizero2w/pizero_apps/medicine_data.json",
    "update_interval": 60
  }
}
```

**medicine_data.json:** Medicine database
```json
{
  "medicines": [...],
  "tracking": {...}
}
```

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1 | Warning/Partial Failure | Review logs |
| 2 | Critical Failure | Investigate immediately |

---

## Support & Maintenance

### Viewing Logs

```bash
# Most recent log
ls -lt /home/user/pizerowgpio/logs/ | head -1

# View all logs
ls -lh /home/user/pizerowgpio/logs/

# Search logs
grep ERROR /home/user/pizerowgpio/logs/*.log
```

### Reporting Issues

Include in bug reports:

1. Log file contents
2. Health check output
3. Git status/diff
4. Steps to reproduce
5. Environment details

```bash
# Collect diagnostic info
mkdir /tmp/diag_$(date +%s)
./health_check.sh --verbose > /tmp/diag_*/health.txt
git status > /tmp/diag_*/git_status.txt
git diff > /tmp/diag_*/git_diff.txt
tar czf diagnostic_$(date +%s).tar.gz /tmp/diag_*/
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-08 | Initial release |

---

## Document Information

- **Author:** Claude Code Assistant
- **Created:** 2025-11-08
- **Last Modified:** 2025-11-08
- **Status:** Complete
- **License:** Same as project

---

**END OF DOCUMENTATION**
