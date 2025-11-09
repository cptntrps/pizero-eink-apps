# TP_lib - Enhanced Display and Touch Drivers

Improved e-ink display and touch controller drivers for Waveshare hardware.

## Components

### E-ink Display Drivers

- **epd2in13_V3.py** - Waveshare 2.13" V3 e-ink display driver
- **epd2in13_V4.py** - Waveshare 2.13" V4 e-ink display driver (optimized partial refresh)

### Touch Controller

- **gt1151.py** - GT1151 capacitive touch screen controller driver

## Key Improvements Over Standard Waveshare Drivers

### 1. Hardware Detection & Mock Mode
- Automatically detects if hardware is available
- Falls back to mock mode for testing without Pi hardware
- Allows development and testing on any machine

### 2. Better Error Handling
- Comprehensive try/except blocks
- Graceful degradation on hardware failures
- Detailed error logging

### 3. Enhanced Logging
- Structured logging throughout
- Debug information for troubleshooting
- Performance monitoring

### 4. Testing Support
- Built-in test functions
- Mock hardware for CI/CD pipelines
- Unit test friendly interface

### 5. Performance Optimizations
- Optimized partial refresh algorithms
- Reduced SPI overhead
- Faster touch scanning

## Hardware Requirements

### For Real Hardware Mode

**Python Packages:**
```bash
pip install RPi.GPIO spidev smbus2
```

**System Requirements:**
- Raspberry Pi (any model with GPIO)
- SPI enabled: `sudo raspi-config` → Interface Options → SPI
- I2C enabled: `sudo raspi-config` → Interface Options → I2C

**GPIO Connections:**

Display (SPI):
- RST_PIN: GPIO 17
- DC_PIN: GPIO 25
- CS_PIN: GPIO 8 (CE0)
- BUSY_PIN: GPIO 24
- SPI MOSI: GPIO 10
- SPI SCLK: GPIO 11

Touch (I2C):
- I2C SDA: GPIO 2
- I2C SCL: GPIO 3
- INT_PIN: GPIO 27

### For Mock Mode (Testing)

No hardware requirements - runs on any Python 3.7+ environment.

## Usage Examples

### E-ink Display

```python
from TP_lib import epd2in13_V4 as epd
from PIL import Image, ImageDraw

# Initialize display
display = epd.EPD()
display.init(display.FULL_UPDATE)
display.Clear(0xFF)  # Clear to white

# Create image
image = Image.new('1', (display.height, display.width), 255)
draw = ImageDraw.Draw(image)
draw.text((10, 10), "Hello World!", fill=0)

# Display image
display.displayPartial(display.getbuffer(image))

# Sleep mode
display.sleep()
display.module_exit()
```

### Touch Controller

```python
from TP_lib import gt1151

# Initialize touch
touch = gt1151.GT1151()

# Read touch points
while True:
    count = touch.scan()
    if count > 0:
        x, y, touched = touch.get_point()
        print(f"Touch at ({x}, {y})")
```

## API Reference

### EPD Class

**Methods:**
- `init(mode)` - Initialize display (FULL_UPDATE or PART_UPDATE)
- `Clear(color)` - Clear screen to color (0xFF=white, 0x00=black)
- `getbuffer(image)` - Convert PIL image to display buffer
- `displayPartial(buffer)` - Display buffer with partial refresh
- `displayPartBaseImage(buffer)` - Set base image for partial updates
- `sleep()` - Enter low power mode
- `module_exit()` - Clean up resources

**Properties:**
- `WIDTH` - Display width (122)
- `HEIGHT` - Display height (250)
- `FULL_UPDATE` - Full refresh mode constant
- `PART_UPDATE` - Partial refresh mode constant

### GT1151 Class

**Methods:**
- `scan(scan_dir)` - Scan for touch events
- `read_touch()` - Read touch data
- `get_point()` - Get first touch point (x, y, touched)

**Properties:**
- `gt_dev` - Current touch state (GT_Development object)
- `gt_old` - Previous touch state (GT_Old object)

## Display Specifications

- **Resolution:** 250×122 pixels
- **Colors:** Black and white (1-bit)
- **Interface:** 4-wire SPI
- **Refresh Time:** ~2s full, ~300ms partial
- **Viewing Angle:** >170°
- **Operating Temp:** 0-50°C

## Touch Specifications

- **Controller:** GT1151 capacitive
- **Interface:** I2C
- **Address:** 0x5D (or 0x14)
- **Points:** Up to 5 simultaneous
- **Sampling Rate:** 100Hz

## License

Apache License 2.0

Based on original Waveshare drivers with significant enhancements.
