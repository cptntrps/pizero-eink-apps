# Hardware Detection System

## Overview

The hardware detection system automatically identifies connected hardware components and configures the appropriate input mode for the Pi Zero 2W application.

## Supported Hardware Configurations

### Configuration A: Touch Input
- **Display**: Waveshare 2.13" e-Paper with GT1151 touchscreen
- **Input Mode**: Touch-based interaction
- **Detection**: GT1151 controller at I2C address 0x5D
- **GPIO**: Pin 27 (interrupt)

### Configuration B: Button Input
- **Display**: Waveshare 2.13" e-Paper (no touch)
- **Input Mode**: Button-based interaction via PiSugar or GPIO button
- **Detection**: PiSugar at I2C address 0x57 or 0x32
- **GPIO**: Pin 3 (button input)

## Detection Logic

The auto-detection follows this priority:

1. **Check for GT1151 touchscreen** (I2C 0x5D)
   - If found → **TOUCH mode**

2. **Check for PiSugar battery** (I2C 0x57 or 0x32)
   - If found (no touch) → **BUTTON mode**

3. **Fallback**
   - If nothing detected → **BUTTON mode** (safest default)

## Files Created

### 1. `/home/user/pizerowgpio/shared/hardware_detect.py`

Main hardware detection module with the following functions:

#### `detect_touch_hardware() -> bool`
Detects GT1151 touchscreen by checking:
- I2C device at address 0x5D
- GPIO 27 availability (interrupt pin)

#### `detect_pisugar() -> bool`
Detects PiSugar battery module by checking:
- I2C addresses 0x57 (PiSugar 2) or 0x32 (PiSugar 3)

#### `auto_detect_hardware_profile() -> str`
Returns recommended profile: "touch" or "button"

#### `get_hardware_info() -> dict`
Returns comprehensive hardware information:
```python
{
    "has_touch": bool,
    "has_pisugar": bool,
    "recommended_profile": str,
    "gpio_info": {
        "GT1151_INT": {"pin": 27, "available": bool, "state": str},
        "BUTTON": {"pin": 3, "available": bool, "state": str}
    },
    "i2c_devices": [list of detected I2C addresses],
    "detection_summary": {
        "GT1151_touchscreen": "detected" | "not detected",
        "PiSugar_battery": "detected" | "not detected",
        "input_mode": "touch" | "button"
    }
}
```

#### `get_input_mode() -> str`
Determines input mode with priority:
1. `PIZERO_INPUT_MODE` environment variable
2. `PIZERO_HARDWARE_PROFILE` environment variable
3. Auto-detection

### 2. `/home/user/pizerowgpio/config/hardware_profiles.json`

Hardware profile presets:

```json
{
  "profiles": {
    "touch": {
      "name": "Waveshare 2.13\" with Touch",
      "input_mode": "touch",
      "hardware": {
        "display": {...},
        "touch": {...},
        "button": {"enabled": false}
      }
    },
    "button": {
      "name": "Waveshare 2.13\" with PiSugar Button",
      "input_mode": "button",
      "hardware": {
        "display": {...},
        "button": {...},
        "touch": {"enabled": false}
      }
    },
    "auto": {
      "name": "Auto-detect",
      "input_mode": "auto"
    }
  },
  "default_profile": "auto"
}
```

### 3. Configuration Updates

#### `/home/user/pizerowgpio/config/development.json`
#### `/home/user/pizerowgpio/config/production.json`

Added hardware section:
```json
{
  "hardware": {
    "profile": "auto",
    "input_mode": "auto",
    "touch": {
      "enabled": true,
      "driver": "GT",
      "int_pin": 27,
      "i2c_address": "0x5D"
    },
    "button": {
      "gpio_pin": 3,
      "long_press_threshold": 2.0,
      "bounce_time": 0.1,
      "pull_up": true
    },
    "display": {
      "model": "2in13_V4",
      "has_touch": null
    }
  }
}
```

**Note**: `has_touch: null` triggers auto-detection

### 4. Environment Variables

Added to `/home/user/pizerowgpio/.env.example`:

```bash
# Hardware Configuration
PIZERO_INPUT_MODE=auto          # Options: auto, touch, button
PIZERO_HARDWARE_PROFILE=auto    # Options: auto, touch, button
PIZERO_BUTTON_GPIO=3            # GPIO pin for button (default: 3)
PIZERO_BUTTON_LONG_PRESS=2.0    # Long press threshold in seconds
```

### 5. Detection Script

`/home/user/pizerowgpio/scripts/detect_hardware.sh`

Bash script for testing hardware detection:

```bash
# Human-readable output
./scripts/detect_hardware.sh

# JSON output
./scripts/detect_hardware.sh --json
```

## Usage Examples

### Python Usage

```python
from shared.hardware_detect import (
    detect_touch_hardware,
    detect_pisugar,
    auto_detect_hardware_profile,
    get_hardware_info,
    get_input_mode
)

# Check for specific hardware
has_touch = detect_touch_hardware()
has_pisugar = detect_pisugar()

# Get recommended profile
profile = auto_detect_hardware_profile()  # Returns "touch" or "button"

# Get comprehensive info
info = get_hardware_info()
print(f"Recommended: {info['recommended_profile']}")
print(f"I2C devices: {info['i2c_devices']}")

# Get input mode (respects env vars)
mode = get_input_mode()
```

### Command Line Usage

```bash
# Run detection with Python directly
cd /home/user/pizerowgpio
python3 shared/hardware_detect.py

# Use detection script (recommended)
./scripts/detect_hardware.sh

# Get JSON output
./scripts/detect_hardware.sh --json
```

### Environment Variable Override

```bash
# Force touch mode
export PIZERO_INPUT_MODE=touch
python3 shared/hardware_detect.py

# Force button mode
export PIZERO_HARDWARE_PROFILE=button
python3 shared/hardware_detect.py
```

## Example Detection Results

### With GT1151 Touch

```
============================================================
Pi Zero 2W Hardware Detection
============================================================

DETECTION RESULTS:
------------------------------------------------------------
GT1151 Touchscreen:  detected
PiSugar Battery:     not detected
Recommended Profile: touch
Input Mode:          touch

I2C Devices Found:   0x5d

GPIO STATUS:
------------------------------------------------------------
✓ GT1151_INT          GPIO 27  (available)
✓ BUTTON              GPIO  3  (available)

============================================================
```

### Without Touch (PiSugar)

```
============================================================
Pi Zero 2W Hardware Detection
============================================================

DETECTION RESULTS:
------------------------------------------------------------
GT1151 Touchscreen:  not detected
PiSugar Battery:     detected
Recommended Profile: button
Input Mode:          button

I2C Devices Found:   0x57

GPIO STATUS:
------------------------------------------------------------
✓ GT1151_INT          GPIO 27  (available)
✓ BUTTON              GPIO  3  (available)

============================================================
```

### No Hardware Detected (Fallback)

```
============================================================
Pi Zero 2W Hardware Detection
============================================================

DETECTION RESULTS:
------------------------------------------------------------
GT1151 Touchscreen:  not detected
PiSugar Battery:     not detected
Recommended Profile: button
Input Mode:          button

GPIO STATUS:
------------------------------------------------------------
✓ GT1151_INT          GPIO 27  (available)
✓ BUTTON              GPIO  3  (available)

============================================================
```

## Safety Features

### Error Handling

1. **I2C Errors**: Gracefully handled with warnings logged
2. **GPIO Access**: Falls back safely if GPIO unavailable
3. **Timeout Protection**: 2-second timeout for I2C detection
4. **Missing Tools**: Detects missing i2c-tools and logs warnings

### Safe Defaults

- **Fallback mode**: Button (safest, works without special hardware)
- **Null detection**: `has_touch: null` triggers auto-detection
- **Environment override**: Can force specific mode via env vars

## Integration Points

### For Application Code

```python
from shared.hardware_detect import get_input_mode

# Get current input mode
input_mode = get_input_mode()

if input_mode == "touch":
    from display.touch_input import TouchInput
    input_handler = TouchInput()
else:
    from display.button_input import ButtonInput
    input_handler = ButtonInput()
```

### For Configuration Loading

```python
import json
from shared.hardware_detect import get_hardware_info

# Load config
with open('config/development.json') as f:
    config = json.load(f)

# Auto-detect if needed
if config['hardware']['display']['has_touch'] is None:
    info = get_hardware_info()
    config['hardware']['display']['has_touch'] = info['has_touch']
    config['hardware']['input_mode'] = info['recommended_profile']
```

## Prerequisites

### Required Packages

```bash
# I2C tools for hardware detection
sudo apt-get install i2c-tools

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options -> I2C -> Enable
```

### Python Dependencies

```bash
# No additional Python packages required
# Uses only standard library modules
```

## Testing

### Manual Testing

```bash
# Test detection
./scripts/detect_hardware.sh

# Test Python module
python3 -c "from shared.hardware_detect import get_hardware_info; print(get_hardware_info())"

# Test with environment override
PIZERO_INPUT_MODE=touch python3 shared/hardware_detect.py
```

### Validation Checks

```bash
# Validate JSON syntax
python3 -m json.tool config/hardware_profiles.json
python3 -m json.tool config/development.json
python3 -m json.tool config/production.json

# Validate Python syntax
python3 -m py_compile shared/hardware_detect.py
```

## Troubleshooting

### I2C Detection Issues

```bash
# Check I2C is enabled
ls -l /dev/i2c*

# Manual I2C scan
i2cdetect -y 1

# Check kernel modules
lsmod | grep i2c
```

### GPIO Permission Issues

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Log out and back in for changes to take effect
```

### Import Errors

```bash
# Ensure shared module is in Python path
export PYTHONPATH=/home/user/pizerowgpio:$PYTHONPATH
```

## Next Steps

The hardware detection system is now ready for integration with:

1. **Input Handler**: Auto-select TouchInput vs ButtonInput
2. **Display Manager**: Configure based on hardware capabilities
3. **Application Launcher**: Choose appropriate input mode
4. **Config Validator**: Validate hardware settings match detected hardware

See the integration examples above for implementation details.
