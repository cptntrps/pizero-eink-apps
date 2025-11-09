# Pi Zero 2W Systemd Services Documentation

## Overview

This document describes the systemd services for running Pi Zero 2W applications as background services. These services provide automatic startup, restart on failure, and centralized logging.

## Services Overview

### 1. pizero-menu.service
**Menu System Service**

Runs the interactive menu system that allows users to select and launch different applications.

- **Script**: `menu_button.py`
- **Type**: Simple service
- **Auto-restart**: Yes (on failure)
- **Start on boot**: Yes (enabled by default)
- **Port**: Display-only (no network)
- **User**: `pi`

#### Features
- Displays menu on e-ink display
- Handles button input for app selection
- Launches child applications
- Automatic restart on crash (10-second delay, max 5 restarts per 5 minutes)

### 2. pizero-web.service
**Web Server Service (Flask API)**

Runs the Flask-based RESTful API server for remote access and management.

- **Script**: `run_api.py`
- **Type**: Simple service
- **Auto-restart**: Yes (on failure)
- **Start on boot**: Yes (enabled by default)
- **Port**: 5000 (HTTP)
- **Host**: 0.0.0.0 (all interfaces)
- **User**: `pi`

#### Features
- RESTful API for medicine data management
- Web-based configuration interface
- Remote monitoring capabilities
- Automatic restart on crash (5-second delay, max 5 restarts per 5 minutes)

#### Environment Variables
- `FLASK_ENV=production` - Production mode
- `FLASK_APP=run_api.py` - Application entry point
- `FLASK_HOST=0.0.0.0` - Listen on all interfaces
- `FLASK_PORT=5000` - API port
- `FLASK_DEBUG=False` - Debug mode disabled

### 3. pizero-medicine.service
**Medicine Tracker Service**

Runs the medicine tracker application for managing medication schedules.

- **Script**: `medicine_app.py`
- **Type**: Simple service
- **Auto-restart**: Yes (on failure)
- **Start on boot**: Yes (enabled by default)
- **Port**: Display-only (no network)
- **User**: `pi`

#### Features
- Medicine schedule tracking
- Display-based UI
- Adherence monitoring
- Automatic restart on crash (10-second delay, max 5 restarts per 5 minutes)

## Installation

### Quick Installation

Run the installation script with elevated privileges:

```bash
sudo /home/pi/pizerowgpio/scripts/install-services.sh --all
```

This will:
1. Copy service files to `/etc/systemd/system/`
2. Reload the systemd daemon
3. Enable services to start on boot
4. Start all services immediately

### Manual Installation

If you prefer manual installation:

```bash
# Copy service files
sudo cp /home/pi/pizerowgpio/systemd/*.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable pizero-menu.service
sudo systemctl enable pizero-web.service
sudo systemctl enable pizero-medicine.service

# Start services
sudo systemctl start pizero-menu.service
sudo systemctl start pizero-web.service
sudo systemctl start pizero-medicine.service
```

## Service Management

### Viewing Service Status

```bash
# Check all services
sudo systemctl status pizero-*.service

# Check specific service
sudo systemctl status pizero-menu.service
```

### Starting/Stopping Services

```bash
# Start a service
sudo systemctl start pizero-menu.service

# Stop a service
sudo systemctl stop pizero-menu.service

# Restart a service
sudo systemctl restart pizero-menu.service

# Stop all Pi Zero services
sudo systemctl stop pizero-*.service
```

### Enabling/Disabling at Boot

```bash
# Enable service to start at boot
sudo systemctl enable pizero-menu.service

# Disable service from starting at boot
sudo systemctl disable pizero-menu.service

# Check if service is enabled
sudo systemctl is-enabled pizero-menu.service
```

## Logging and Troubleshooting

### Viewing Logs with journalctl

```bash
# View recent logs for a service
sudo journalctl -u pizero-menu.service -n 50

# Follow logs in real-time
sudo journalctl -u pizero-menu.service -f

# View logs since last boot
sudo journalctl -u pizero-menu.service -b

# View logs from the last hour
sudo journalctl -u pizero-menu.service --since "1 hour ago"

# View logs with verbose output
sudo journalctl -u pizero-menu.service -o verbose
```

### Common Issues and Solutions

#### Service fails to start

Check the service logs:
```bash
sudo journalctl -u pizero-menu.service -n 100
```

Common causes:
- Script not found: Verify paths in service file match actual locations
- Permission issues: Check file ownership and permissions
- Missing dependencies: Install required Python packages

#### Service keeps restarting

This indicates the service is crashing. Check logs for:
- Missing imports
- GPIO/display initialization errors
- Database connection issues
- Configuration file errors

#### Web server not accessible

```bash
# Check if web service is running
sudo systemctl status pizero-web.service

# Check listening ports
sudo netstat -tlnp | grep 5000

# Test local connection
curl http://localhost:5000/api/v1/health
```

#### Display not working

For menu and medicine services:
```bash
# Check for display hardware errors
sudo journalctl -u pizero-menu.service -f

# Verify GPIO is accessible to 'pi' user
groups pi  # Should include gpio, spi, i2c if needed
```

## Service Configuration

### Modifying Service Files

To change service configuration:

1. Edit the service file:
   ```bash
   sudo nano /etc/systemd/system/pizero-menu.service
   ```

2. Reload systemd daemon:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Restart the service:
   ```bash
   sudo systemctl restart pizero-menu.service
   ```

### Common Configuration Changes

#### Change restart delay
In the service file, modify `RestartSec`:
```ini
RestartSec=5  # Wait 5 seconds before restarting
```

#### Change restart policy
In the service file, modify `Restart`:
```ini
Restart=always        # Restart on any exit
Restart=on-failure    # Restart only on non-zero exit
Restart=no            # Never restart
```

#### Change logging
In the service file, modify `StandardOutput` and `StandardError`:
```ini
StandardOutput=file:/var/log/pizero/menu.log
StandardError=file:/var/log/pizero/menu-error.log
```

## Dependency and Startup Order

### Startup Dependencies

The services have the following boot dependencies:

```
network-online.target
    ↓
pizero-web.service (Web API)
pizero-menu.service (Menu system)
pizero-medicine.service (Medicine app)
```

All services depend on network being online but can run independently.

### Service Interactions

- **pizero-menu.service** can launch other applications
- **pizero-web.service** provides API access to shared data
- **pizero-medicine.service** can run standalone or access data via API
- All services use the same SQLite database at `/home/pi/pizerowgpio/medicine.db`

## Performance Tuning

### Memory Usage

The services are lightweight but monitor resource usage:

```bash
# Check memory usage
sudo systemctl status pizero-menu.service --no-pager | grep Memory

# Monitor all services
watch 'ps aux | grep pizero'
```

### CPU Optimization

Services are configured with:
- `Type=simple` - Minimal overhead
- `PrivateTmp=true` - Isolated temporary files
- Standard Python PYTHONUNBUFFERED mode

## Auto-Restart Behavior

All services include restart policies to ensure continuous operation:

```ini
Restart=always              # Always restart, including clean exits
RestartSec=10              # Wait 10 seconds before restart
StartLimitInterval=300     # Time window for rate limiting
StartLimitBurst=5          # Max 5 restarts in the interval
```

This configuration:
- Automatically restarts on crash
- Prevents rapid restart loops (max 5 restarts per 5 minutes)
- Waits before restarting to avoid consuming resources

## Monitoring and Maintenance

### Health Checks

For the web service:
```bash
# Check API health
curl -s http://localhost:5000/api/v1/health | python3 -m json.tool

# Check service endpoints
curl -s http://localhost:5000/api/v1/medicines | python3 -m json.tool
```

### Log Rotation

Systemd/journald automatically manages logs. Current limit is typically 500MB per boot.

To check journal usage:
```bash
sudo journalctl --disk-usage
```

### Regular Maintenance

```bash
# Monthly: Clean old logs older than 30 days
sudo journalctl --vacuum-time=30d

# Check service health
sudo systemctl status pizero-*.service

# Update service files if code changes
sudo systemctl daemon-reload
sudo systemctl restart pizero-*.service
```

## Security Considerations

### User Permissions

Services run as the `pi` user. Ensure proper permissions:

```bash
# Check directory ownership
ls -ld /home/pi/pizerowgpio/
ls -ld /home/pi/pizerowgpio/database/

# Fix if needed
sudo chown -R pi:pi /home/pi/pizerowgpio/
sudo chmod -R u+rwX,g+rX,o= /home/pi/pizerowgpio/
```

### Service File Security

Service files should only be modifiable by root:

```bash
ls -l /etc/systemd/system/pizero-*.service
```

Should show: `-rw-r--r-- 1 root root`

### Network Security

For production deployments:
- Consider using a reverse proxy (nginx) in front of Flask
- Implement API authentication
- Restrict network access via firewall rules

## Uninstallation

To remove services:

```bash
# Stop services
sudo systemctl stop pizero-*.service

# Disable services
sudo systemctl disable pizero-*.service

# Remove service files
sudo rm /etc/systemd/system/pizero-*.service

# Reload systemd
sudo systemctl daemon-reload

# Verify removal
sudo systemctl list-units --state=loaded | grep pizero
```

## Advanced Topics

### Custom Logging

To enable verbose logging for debugging:

1. Edit the service file:
   ```bash
   sudo nano /etc/systemd/system/pizero-menu.service
   ```

2. Change environment variables:
   ```ini
   Environment="PYTHONUNBUFFERED=1"
   Environment="LOG_LEVEL=DEBUG"
   ```

3. Reload and restart:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart pizero-menu.service
   ```

### Running Multiple Instances

To run multiple instances of a service (e.g., for testing):

1. Create a template service: `pizero-menu@.service`
2. Create instances: `pizero-menu@1.service`, `pizero-menu@2.service`
3. Manage as a group: `systemctl start pizero-menu@*.service`

### Integration with Monitoring

Services output to systemd journal, which can be:
- Forwarded to syslog
- Monitored by log aggregation tools (ELK, Splunk)
- Integrated with monitoring systems (Prometheus, Grafana)

## References

- [systemd Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [journalctl Documentation](https://www.freedesktop.org/software/systemd/man/journalctl.html)
- [systemctl Documentation](https://www.freedesktop.org/software/systemd/man/systemctl.html)

## Support

For issues or questions:
1. Check the logs: `sudo journalctl -u pizero-menu.service -f`
2. Verify service status: `sudo systemctl status pizero-*.service`
3. Review configuration files in `/home/pi/pizerowgpio/systemd/`

---

**Last Updated**: 2025-11-08
**Version**: 1.0
