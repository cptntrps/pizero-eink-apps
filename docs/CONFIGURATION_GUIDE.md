# Pi Zero 2W Application Configuration Guide

This guide documents the environment-specific configuration system for the Pi Zero 2W application suite.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Overview](#environment-overview)
3. [Configuration Structure](#configuration-structure)
4. [Configuration Options Reference](#configuration-options-reference)
5. [Environment Variables](#environment-variables)
6. [Loading and Using Configuration](#loading-and-using-configuration)
7. [Configuration Validation](#configuration-validation)
8. [Migration Guide](#migration-guide)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Quick Start

The application supports three environments with pre-configured settings:

```bash
# Development (default, verbose logging, quick refresh rates)
export PIZERO_ENV=development

# Production (minimal logging, conservative refresh rates, longer timeouts)
export PIZERO_ENV=production

# Test (optimized for testing, short intervals, reduced features)
export PIZERO_ENV=test
```

Each environment automatically loads its corresponding config file:
- `config/development.json`
- `config/production.json`
- `config/test.json`

## Environment Overview

### Development
- **Use Case**: Local development and testing
- **Log Level**: DEBUG
- **API Timeouts**: 10 seconds
- **Update Intervals**: Short (5-30 seconds)
- **Features**: All features enabled
- **File Paths**: Relative (./medicine_data.json)
- **Metrics**: Enabled

### Production
- **Use Case**: Deployment on Pi Zero 2W hardware
- **Log Level**: WARNING
- **API Timeouts**: 5 seconds (conservative)
- **Update Intervals**: Long (30-600 seconds)
- **Features**: Non-essential features disabled (e.g., Forbidden app)
- **File Paths**: Absolute paths to mounted storage
- **Metrics**: Disabled
- **Auto-sleep**: Enabled with 10-minute timeout

### Test
- **Use Case**: Automated testing and CI/CD
- **Log Level**: INFO
- **API Timeouts**: 1 second
- **Update Intervals**: Very short (5-10 seconds)
- **Features**: Only essential features
- **File Paths**: Test-specific directories
- **Metrics**: Enabled for analysis

## Configuration Structure

```json
{
  "environment": "development",
  "debug": true,
  "log_level": "DEBUG",
  "weather": { ... },
  "mbta": { ... },
  "disney": { ... },
  "flights": { ... },
  "pomodoro": { ... },
  "medicine": { ... },
  "menu": { ... },
  "system": { ... },
  "display": { ... }
}
```

## Configuration Options Reference

### Top-Level Options

| Option | Type | Description |
|--------|------|-------------|
| `environment` | string | Environment name: `development`, `production`, `test` |
| `debug` | boolean | Enable debug mode (verbose logging, error details) |
| `log_level` | string | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Weather Section

```json
"weather": {
  "location": "Boston",
  "units": "metric|imperial",
  "update_interval": 300,
  "display_format": "detailed|compact",
  "show_forecast": true,
  "api_timeout": 10
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `location` | string | - | "Boston" | City name for weather lookup |
| `units` | string | metric, imperial | metric | Temperature units |
| `update_interval` | integer | 10-3600 | 300 | Seconds between updates |
| `display_format` | string | detailed, compact | detailed | UI display format |
| `show_forecast` | boolean | - | true | Show forecast data |
| `api_timeout` | integer | 1-60 | 10 | API request timeout (seconds) |

### MBTA Section

```json
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
  "max_predictions": 3,
  "api_timeout": 5
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `home_station_id` | string | - | - | MBTA station ID (home) |
| `home_station_name` | string | - | - | Station display name (home) |
| `work_station_id` | string | - | - | MBTA station ID (work) |
| `work_station_name` | string | - | - | Station display name (work) |
| `update_interval` | integer | 10-600 | 30 | Seconds between updates |
| `morning_start` | string | HH:MM | 06:00 | Start of morning commute window |
| `morning_end` | string | HH:MM | 12:00 | End of morning commute window |
| `evening_start` | string | HH:MM | 15:00 | Start of evening commute window |
| `evening_end` | string | HH:MM | 21:00 | End of evening commute window |
| `show_delays` | boolean | - | true | Show delay information |
| `max_predictions` | integer | 1-10 | 3 | Number of predictions to display |
| `api_timeout` | integer | 1-60 | 5 | API request timeout (seconds) |

### Disney Section

```json
"disney": {
  "park_id": 6,
  "park_name": "Magic Kingdom",
  "update_interval": 10,
  "data_refresh_rides": 20,
  "sort_by": "wait_time",
  "show_closed": false,
  "favorite_rides": [],
  "api_timeout": 5
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `park_id` | integer | >0 | 6 | Disney park ID |
| `park_name` | string | - | - | Park display name |
| `update_interval` | integer | 5-600 | 10 | Seconds between updates |
| `data_refresh_rides` | integer | 5-300 | 20 | Ride list refresh interval |
| `sort_by` | string | wait_time, name | wait_time | Sort rides by |
| `show_closed` | boolean | - | false | Show closed rides |
| `favorite_rides` | array | - | [] | List of favorite ride IDs |
| `api_timeout` | integer | 1-60 | 5 | API request timeout (seconds) |

### Flights Section

```json
"flights": {
  "latitude": 40.716389,
  "longitude": -73.954167,
  "radius_km": 15,
  "update_interval": 15,
  "min_altitude": 0,
  "max_altitude": 10000,
  "show_details": true,
  "api_timeout": 5
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `latitude` | float | -90 to 90 | - | Location latitude |
| `longitude` | float | -180 to 180 | - | Location longitude |
| `radius_km` | float | 1-500 | 15 | Tracking radius in kilometers |
| `update_interval` | integer | 5-600 | 15 | Seconds between updates |
| `min_altitude` | integer | >=0 | 0 | Minimum altitude filter (feet) |
| `max_altitude` | integer | >min | 10000 | Maximum altitude filter (feet) |
| `show_details` | boolean | - | true | Show detailed flight info |
| `api_timeout` | integer | 1-60 | 5 | API request timeout (seconds) |

### Pomodoro Section

```json
"pomodoro": {
  "work_duration": 1500,
  "short_break": 300,
  "long_break": 900,
  "sessions_until_long_break": 4,
  "auto_start_breaks": false,
  "auto_start_pomodoros": false,
  "sound_enabled": false
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `work_duration` | integer | 60-3600 | 1500 | Work session duration (seconds) |
| `short_break` | integer | 30-600 | 300 | Short break duration (seconds) |
| `long_break` | integer | 60-1800 | 900 | Long break duration (seconds) |
| `sessions_until_long_break` | integer | 1-20 | 4 | Sessions before long break |
| `auto_start_breaks` | boolean | - | false | Automatically start breaks |
| `auto_start_pomodoros` | boolean | - | false | Automatically start sessions |
| `sound_enabled` | boolean | - | false | Enable audio notifications |

### Medicine Section

```json
"medicine": {
  "data_file": "./medicine_data.json",
  "update_interval": 60,
  "reminder_window": 30,
  "alert_upcoming_minutes": 15,
  "rotate_interval": 3,
  "enable_backups": true,
  "backup_interval": 300
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `data_file` | string | - | - | Path to medicine database |
| `update_interval` | integer | 5-600 | 60 | Seconds between check intervals |
| `reminder_window` | integer | 5-120 | 30 | Minutes before to show reminder |
| `alert_upcoming_minutes` | integer | 1-120 | 15 | Minutes until medication shows alert |
| `rotate_interval` | integer | 1-10 | 3 | Display rotation interval (seconds) |
| `enable_backups` | boolean | - | true | Enable automatic backups |
| `backup_interval` | integer | 30-3600 | 300 | Seconds between backups |

### Menu Section

```json
"menu": {
  "apps": [
    {
      "id": "medicine",
      "name": "Medicine",
      "enabled": true,
      "order": 1
    }
  ],
  "button_hold_time": 2.0,
  "scroll_speed": 0.5
}
```

| Option | Type | Description |
|--------|------|-------------|
| `apps` | array | Array of app configurations |
| `apps[].id` | string | Unique app identifier |
| `apps[].name` | string | Display name |
| `apps[].enabled` | boolean | Enable/disable app |
| `apps[].order` | integer | Menu display order |
| `button_hold_time` | float | Seconds to hold for menu access |
| `scroll_speed` | float | Menu scroll sensitivity |

### System Section

```json
"system": {
  "wifi_ssid": "",
  "wifi_password": "",
  "hotspot_enabled": false,
  "hotspot_ssid": "PiZero-Config",
  "hotspot_password": "raspberry",
  "display_brightness": 100,
  "timezone": "America/New_York",
  "auto_sleep": false,
  "sleep_timeout": 300,
  "base_dir": "/home/pizero2w/pizero_apps",
  "enable_metrics": false
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `wifi_ssid` | string | - | "" | WiFi network SSID |
| `wifi_password` | string | - | "" | WiFi password |
| `hotspot_enabled` | boolean | - | false | Enable WiFi hotspot |
| `hotspot_ssid` | string | - | "PiZero-Config" | Hotspot network name |
| `hotspot_password` | string | - | "raspberry" | Hotspot password |
| `display_brightness` | integer | 0-100 | 100 | Display brightness percentage |
| `timezone` | string | - | "America/New_York" | System timezone (IANA format) |
| `auto_sleep` | boolean | - | false | Enable auto-sleep |
| `sleep_timeout` | integer | 30-3600 | 300 | Seconds before sleep (seconds) |
| `base_dir` | string | - | - | Base directory for app data |
| `enable_metrics` | boolean | - | false | Enable performance metrics |

### Display Section

```json
"display": {
  "rotation": 0,
  "invert_colors": false,
  "refresh_mode": "auto",
  "partial_update_limit": 10,
  "debug_mode": false
}
```

| Option | Type | Range | Default | Description |
|--------|------|-------|---------|-------------|
| `rotation` | integer | 0, 90, 180, 270 | 0 | Screen rotation (degrees) |
| `invert_colors` | boolean | - | false | Invert display colors |
| `refresh_mode` | string | auto, full, partial | auto | Display refresh mode |
| `partial_update_limit` | integer | 1-100 | 10 | Partial updates before full |
| `debug_mode` | boolean | - | false | Enable display debugging |

## Environment Variables

### Configuration Selection

| Variable | Values | Description | Example |
|----------|--------|-------------|---------|
| `PIZERO_ENV` | development, production, test | Environment to load | `export PIZERO_ENV=production` |
| `PIZERO_CONFIG` | file path | Override config file path | `export PIZERO_CONFIG=/etc/pizero/config.json` |
| `PIZERO_CONFIG_DIR` | directory path | Override config directory | `export PIZERO_CONFIG_DIR=/etc/pizero/` |

### Configuration Overrides

Override specific configuration values using environment variables with the format:
```
PIZERO_CONFIG_SECTION_KEY=value
```

**Examples:**

```bash
# Override medicine update interval to 120 seconds
export PIZERO_CONFIG_MEDICINE_UPDATE_INTERVAL=120

# Override weather location
export PIZERO_CONFIG_WEATHER_LOCATION="New York"

# Override system brightness to 50%
export PIZERO_CONFIG_SYSTEM_DISPLAY_BRIGHTNESS=50

# Override auto-sleep
export PIZERO_CONFIG_SYSTEM_AUTO_SLEEP=true
```

**Type Conversion:**
- `true`, `yes`, `1` → Boolean `true`
- `false`, `no`, `0` → Boolean `false`
- `123` → Integer `123`
- `3.14` → Float `3.14`
- Other values remain as strings

## Loading and Using Configuration

### Basic Usage

```python
from shared.app_utils import ConfigLoader

# Load configuration (automatically selects environment)
config = ConfigLoader.load()

# Get entire section
medicine_config = ConfigLoader.get_section('medicine')

# Get specific value
update_interval = ConfigLoader.get_value('medicine', 'update_interval')

# Get with default value
reminder = ConfigLoader.get_value('medicine', 'reminder_window', default=30)
```

### Using Dot Notation

```python
from shared.app_utils import ConfigLoader

# Get nested values using dot notation
interval = ConfigLoader.get_value_nested('medicine.update_interval')
brightness = ConfigLoader.get_value_nested('system.display_brightness', default=100)
```

### Switching Environments

```python
from shared.app_utils import ConfigLoader

# Switch to production and reload
ConfigLoader.set_environment('production')
config = ConfigLoader.load(force_reload=True)

# Get current environment
current_env = ConfigLoader.get_environment()
print(f"Running in {current_env} environment")
```

### Validating Configuration

```python
from shared.app_utils import ConfigLoader

try:
    # Validate loaded configuration
    is_valid = ConfigLoader.validate()
    print("Configuration is valid!")
except Exception as e:
    print(f"Configuration error: {e}")
```

## Configuration Validation

The `ConfigValidator` class provides schema-based validation:

```python
from shared.config_validator import ConfigValidator

# Load and validate
try:
    config = ConfigValidator.from_file('/path/to/config.json')
    print("Configuration is valid!")
except ConfigValidationError as e:
    print(f"Validation failed: {e}")
```

### Validation Features

- **Type Checking**: Ensures correct data types
- **Range Validation**: Checks numeric bounds
- **Choice Validation**: Validates allowed values
- **Time Format**: Validates HH:MM format times
- **Cross-Field Validation**: Validates time ranges (end > start)
- **Path Validation**: Optionally validates file paths

### Example Validation Errors

```python
from shared.config_validator import ConfigValidator, ConfigValidationError

validator = ConfigValidator('config/production.json')
validator.load_config()

try:
    validator.validate_config()
except ConfigValidationError as e:
    # Get list of validation errors
    errors = validator.get_errors()
    for error in errors:
        print(f"  Error: {error}")
```

## Migration Guide

### From Single config.json to Environment-Specific

#### Step 1: Backup Existing Config

```bash
cp config.json config.json.backup
```

#### Step 2: Copy to Development (Recommended)

```bash
mkdir -p config
cp config.json config/development.json
```

#### Step 3: Create Production Config

Copy `config/development.json` to `config/production.json` and adjust:

```bash
cp config/development.json config/production.json
```

Key production adjustments:
- Set `debug: false`
- Set `log_level: "WARNING"`
- Increase `update_interval` values (2-10x)
- Set `api_timeout: 5`
- Use absolute paths in `medicine.data_file`
- Set `system.auto_sleep: true`
- Set `system.base_dir` to production location

#### Step 4: Create Test Config

```bash
cp config/development.json config/test.json
```

Key test adjustments:
- Set `debug: true`
- Decrease `update_interval` values (1/3 to 1/5)
- Set `api_timeout: 1`
- Use test-relative paths
- Disable non-essential apps

#### Step 5: Validate Configs

```bash
python3 -c "
from shared.config_validator import ConfigValidator
for env in ['development', 'production', 'test']:
    try:
        ConfigValidator.from_file(f'config/{env}.json')
        print(f'{env}: OK')
    except Exception as e:
        print(f'{env}: FAILED - {e}')
"
```

#### Step 6: Test Environment Switching

```bash
python3 -c "
from shared.app_utils import ConfigLoader
for env in ['development', 'production', 'test']:
    ConfigLoader.set_environment(env)
    config = ConfigLoader.load(force_reload=True)
    path = ConfigLoader.get_config_path()
    print(f'{env}: {path}')
"
```

#### Step 7: Update Application Startup

In your application startup code:

```python
import os
from shared.app_utils import ConfigLoader

# Set environment based on deployment
if os.environ.get('PIZERO_ENV'):
    ConfigLoader.set_environment(os.environ['PIZERO_ENV'])
else:
    ConfigLoader.set_environment('production')  # Safe default

# Load and validate
config = ConfigLoader.load()
ConfigLoader.validate()

print(f"Running in {ConfigLoader.get_environment()} environment")
```

## Best Practices

### Configuration Management

1. **Always Validate**: Call `ConfigLoader.validate()` at startup
2. **Use Environment Variables**: For deployment-specific values
3. **Keep Defaults**: Don't require config file for basic functionality
4. **Version Control**: Track config files in git (without secrets)
5. **Document Changes**: Note any custom config values

### Security

1. **Never Commit Secrets**: Exclude passwords from version control
   ```
   # .gitignore
   *.key
   *.password
   secrets.json
   ```

2. **Use Environment Variables**: For sensitive values
   ```bash
   export PIZERO_CONFIG_SYSTEM_WIFI_PASSWORD="your-password"
   ```

3. **Restrict File Permissions**: Config files may contain sensitive data
   ```bash
   chmod 600 config/*.json
   ```

4. **Separate Secrets**: Keep sensitive config in separate file
   ```python
   # Load main config
   config = ConfigLoader.load()

   # Load secrets from environment/file
   secrets = json.load(open('/etc/pizero/secrets.json'))
   ```

### Performance

1. **Cache Configuration**: ConfigLoader caches config in memory
2. **Lazy Loading**: Only reload when environment changes
3. **Environment Variables**: Use for runtime overrides
4. **Validation Once**: Validate at startup, not repeatedly

### Deployment

1. **Set PIZERO_ENV**: In deployment scripts
   ```bash
   #!/bin/bash
   export PIZERO_ENV=production
   export PIZERO_CONFIG_DIR=/etc/pizero/config
   python3 /home/pizero/main.py
   ```

2. **Volume Mounts**: Use Docker/container mounts for config
   ```dockerfile
   COPY config/ /app/config/
   ENV PIZERO_ENV=production
   ```

3. **Configuration Servers**: For advanced deployments
   ```python
   # Load from etcd, consul, etc.
   config = fetch_from_config_server()
   ConfigLoader._config = config
   ```

## Troubleshooting

### Configuration Not Loading

**Problem**: "Config file not found"

**Solution**:
1. Check file exists: `ls -la config/development.json`
2. Check PIZERO_ENV: `echo $PIZERO_ENV`
3. Check PIZERO_CONFIG: `echo $PIZERO_CONFIG`
4. Use explicit path:
   ```python
   ConfigLoader.load('/home/pizero/config/development.json')
   ```

### Validation Failures

**Problem**: "Configuration validation failed"

**Solution**:
1. Check log messages for specific errors
2. Validate individual sections
3. Compare with example configs:
   ```bash
   diff config/development.json config/development.json.example
   ```

### Environment Variable Overrides Not Working

**Problem**: Changes not reflected in config

**Solution**:
1. Check variable format: `PIZERO_CONFIG_SECTION_KEY=value`
2. Force reload: `ConfigLoader.load(force_reload=True)`
3. Check type conversion:
   ```python
   value = ConfigLoader.get_value('section', 'key')
   print(f"Value: {value} (type: {type(value)})")
   ```

### Path Issues

**Problem**: File not found in production

**Solution**:
1. Use absolute paths in production config
2. Check current working directory: `pwd`
3. Use environment variables:
   ```bash
   export PIZERO_BASE_DIR=/home/pizero2w/pizero_apps
   ```

### Performance Issues

**Problem**: App slow in production

**Solution**:
1. Check update_interval values (increase them)
2. Check api_timeout values (reduce them)
3. Check enable_metrics (disable if not needed)
4. Enable debug logging temporarily:
   ```bash
   export PIZERO_CONFIG_DEBUG=true
   ```

## See Also

- [API Design Documentation](./API_DESIGN.md)
- [System Architecture](../ARCHITECTURE_REVIEW.md)
- [Database Documentation](../DATABASE_DOCUMENTATION.md)
