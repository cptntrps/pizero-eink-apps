# Deployment Scripts - Quick Reference

## Scripts at a Glance

```
/home/user/pizerowgpio/scripts/
├── install.sh         Initial setup and dependency installation
├── deploy.sh          Deploy code updates with automatic backup
├── rollback.sh        Restore previous deployment version
├── health_check.sh    Comprehensive system health verification
└── monitor.sh         Real-time application monitoring
```

## Command Cheat Sheet

### Installation (First Time Setup)

```bash
# Initial installation with sudo
sudo ./scripts/install.sh

# Preview installation without changes
sudo ./scripts/install.sh --dry-run

# Installation with no output
sudo ./scripts/install.sh --quiet
```

### Deployment (Update Code)

```bash
# Preview deployment
./scripts/deploy.sh --dry-run

# Deploy with automatic backup
./scripts/deploy.sh

# Deploy despite uncommitted changes
./scripts/deploy.sh --force

# Deploy without creating backup
./scripts/deploy.sh --no-backup

# Quiet deployment
./scripts/deploy.sh --quiet
```

### Rollback (Undo Bad Deployment)

```bash
# Interactive rollback (lists available backups)
./scripts/rollback.sh

# Rollback to specific backup
./scripts/rollback.sh --backup-id 20251108_143022

# Preview rollback
./scripts/rollback.sh --dry-run

# Quiet rollback
./scripts/rollback.sh --quiet
```

### Health Check (Verify System)

```bash
# Standard health check (text output)
./scripts/health_check.sh

# JSON output (for automated parsing)
./scripts/health_check.sh --format json

# Detailed output with explanations
./scripts/health_check.sh --verbose

# JSON + verbose
./scripts/health_check.sh --format json --verbose
```

### Monitoring (Real-Time Metrics)

```bash
# Monitor continuously (Ctrl+C to stop)
./scripts/monitor.sh

# Monitor with 10-second interval
./scripts/monitor.sh --interval 10

# Monitor for 30 minutes then stop
./scripts/monitor.sh --duration 30

# Log monitoring to file
./scripts/monitor.sh --log-file /tmp/monitor.log

# Background monitoring
./scripts/monitor.sh --log-file /tmp/monitor.log &

# Monitor with 60-second updates for 60 minutes
./scripts/monitor.sh --interval 60 --duration 60
```

## Common Workflows

### Workflow: Fresh Installation

```bash
cd /home/user/pizerowgpio/scripts

# Install with sudo
sudo ./install.sh

# Verify installation
./health_check.sh

# Start services
sudo systemctl start pizero-webserver
sudo systemctl start pizero-menu

# Final verification
./health_check.sh --verbose
```

### Workflow: Deploy Update

```bash
cd /home/user/pizerowgpio/scripts

# Preview changes
./deploy.sh --dry-run

# Deploy
./deploy.sh

# Verify deployment
./health_check.sh

# Monitor for 5 minutes
./monitor.sh --duration 5
```

### Workflow: Handle Failed Deployment

```bash
cd /home/user/pizerowgpio/scripts

# Check what's wrong
./health_check.sh --verbose

# Rollback immediately
./rollback.sh

# Verify rollback successful
./health_check.sh
```

## Essential Information

### Directories

| Path | Purpose |
|------|---------|
| `/home/user/pizerowgpio/scripts/` | Deployment scripts location |
| `/home/user/pizerowgpio/docs/` | Documentation |
| `/home/user/pizerowgpio/logs/` | Script execution logs |
| `/home/pizero2w/pizero_apps/` | Application directory |
| `/home/pizero2w/pizero_apps/backups/` | Deployment backups |
| `/var/log/pizero-app/` | Application logs |

### Services

| Service | Purpose | Check Command |
|---------|---------|---|
| `pizero-webserver` | Flask web interface | `systemctl status pizero-webserver` |
| `pizero-menu` | GPIO button & menu | `systemctl status pizero-menu` |

## Log Locations

| Operation | Log Path |
|-----------|----------|
| Installation | `/home/user/pizerowgpio/logs/install_*.log` |
| Deployment | `/home/user/pizerowgpio/logs/deploy_*.log` |
| Rollback | `/home/user/pizerowgpio/logs/rollback_*.log` |
| Health Check | `/home/user/pizerowgpio/logs/health_check_*.log` |
| Web Server | `/var/log/pizero-app/webserver.log` |
| Menu System | `/var/log/pizero-app/menu.log` |

## Troubleshooting Quick Tips

### Permission Denied

```bash
chmod +x /home/user/pizerowgpio/scripts/*.sh
```

### Services Not Running

```bash
systemctl status pizero-webserver pizero-menu
sudo systemctl restart pizero-webserver pizero-menu
tail -f /var/log/pizero-app/*.log
```

### Deployment Failed

```bash
./scripts/health_check.sh --verbose
./scripts/rollback.sh
```

---

**For detailed documentation, see:** `/home/user/pizerowgpio/docs/DEPLOYMENT_SCRIPTS.md`
