"""
Enhanced GT1151 Capacitive Touch Controller Driver
===================================================

Improved driver for GT1151 touch screen controller with:
- Hardware detection and auto-fallback
- Mock mode for testing
- Better event handling
- Detailed logging

Touch controller specifications:
- I2C address: 0x5D or 0x14
- Interrupt pin: GPIO 27
- Up to 5 touch points
- 250x122 resolution mapping
"""

import logging
import time
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)

# Try to import hardware libraries
try:
    import smbus2 as smbus
    import RPi.GPIO as GPIO
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False
    logger.warning("Hardware libraries not available - GT1151 running in MOCK mode")


class GT1151:
    """GT1151 Capacitive Touch Screen Controller"""

    # I2C Configuration
    I2C_BUS = 1
    I2C_ADDR = 0x5D  # Primary address
    I2C_ADDR_ALT = 0x14  # Alternative address

    # GPIO Configuration
    INT_PIN = 27  # Interrupt pin
    RST_PIN = 17  # Reset pin (shared with display)

    # Touch point registers
    POINT_INFO = 0x814E
    POINT1_REG = 0x814F

    # Display dimensions for touch mapping
    SCAN_DIR_DFT = 0  # Default scan direction
    X_MAX = 250
    Y_MAX = 122

    def __init__(self, mock_mode: bool = None):
        """Initialize GT1151 touch controller

        Args:
            mock_mode: Force mock mode (None = auto-detect, True = mock, False = hardware)
        """
        self.mock_mode = mock_mode if mock_mode is not None else (not HW_AVAILABLE)
        self.i2c_addr = self.I2C_ADDR
        self.scan_dir = self.SCAN_DIR_DFT

        if self.mock_mode:
            logger.info("GT1151 initialized in MOCK mode (no hardware)")
            self.bus = None
            self.gt_dev = GT_Development()
            self.gt_old = GT_Old()
        else:
            logger.info("GT1151 initializing with hardware")
            self._init_hardware()

    def _init_hardware(self):
        """Initialize I2C and GPIO for hardware"""
        try:
            # Initialize I2C bus
            self.bus = smbus.SMBus(self.I2C_BUS)

            # Try primary address
            try:
                self.bus.read_byte_data(self.I2C_ADDR, 0)
                logger.info(f"GT1151 found at address {self.I2C_ADDR:#x}")
            except:
                # Try alternative address
                try:
                    self.i2c_addr = self.I2C_ADDR_ALT
                    self.bus.read_byte_data(self.I2C_ADDR_ALT, 0)
                    logger.info(f"GT1151 found at address {self.I2C_ADDR_ALT:#x}")
                except:
                    logger.warning("GT1151 not detected, switching to mock mode")
                    self.mock_mode = True
                    self.bus = None

            # Initialize GPIO for interrupt pin
            if not self.mock_mode:
                GPIO.setmode(GPIO.BCM)
                GPIO.setup(self.INT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                logger.debug("GT1151 GPIO initialized")

            # Initialize device state objects
            self.gt_dev = GT_Development()
            self.gt_old = GT_Old()

        except Exception as e:
            logger.error(f"GT1151 hardware initialization failed: {e}")
            self.mock_mode = True
            self.bus = None
            self.gt_dev = GT_Development()
            self.gt_old = GT_Old()

    def _read_reg(self, reg_addr: int, length: int = 1) -> Optional[List[int]]:
        """Read register(s) from GT1151

        Args:
            reg_addr: Register address (16-bit)
            length: Number of bytes to read

        Returns:
            List of bytes or None on error
        """
        if self.mock_mode or not self.bus:
            return [0] * length

        try:
            # GT1151 uses 16-bit register addresses
            addr_high = (reg_addr >> 8) & 0xFF
            addr_low = reg_addr & 0xFF

            # Write register address
            self.bus.write_i2c_block_data(self.i2c_addr, addr_high, [addr_low])
            time.sleep(0.001)

            # Read data
            data = self.bus.read_i2c_block_data(self.i2c_addr, addr_high, length)
            return data

        except Exception as e:
            logger.error(f"GT1151 read error at {reg_addr:#x}: {e}")
            return None

    def _write_reg(self, reg_addr: int, data: List[int]) -> bool:
        """Write register(s) to GT1151

        Args:
            reg_addr: Register address (16-bit)
            data: List of bytes to write

        Returns:
            True on success, False on error
        """
        if self.mock_mode or not self.bus:
            return True

        try:
            addr_high = (reg_addr >> 8) & 0xFF
            addr_low = reg_addr & 0xFF

            write_data = [addr_low] + data
            self.bus.write_i2c_block_data(self.i2c_addr, addr_high, write_data)
            return True

        except Exception as e:
            logger.error(f"GT1151 write error at {reg_addr:#x}: {e}")
            return False

    def read_touch(self) -> int:
        """Read touch status and update device state

        Returns:
            Number of touch points detected (0-5)
        """
        if self.mock_mode:
            # Mock mode - no touches
            self.gt_dev.Touch = 0
            self.gt_dev.X = [0] * 5
            self.gt_dev.Y = [0] * 5
            return 0

        try:
            # Read touch point info register
            point_info = self._read_reg(self.POINT_INFO, 1)
            if not point_info:
                return 0

            # Extract touch count (lower 4 bits)
            touch_count = point_info[0] & 0x0F

            if touch_count > 0 and touch_count <= 5:
                # Read touch point data
                point_data = self._read_reg(self.POINT1_REG, touch_count * 8)

                if point_data:
                    self.gt_dev.Touch = touch_count

                    # Parse touch points
                    for i in range(touch_count):
                        offset = i * 8
                        # X coordinate (16-bit little endian)
                        x = point_data[offset + 1] | (point_data[offset + 2] << 8)
                        # Y coordinate (16-bit little endian)
                        y = point_data[offset + 3] | (point_data[offset + 4] << 8)

                        # Map to display coordinates
                        self.gt_dev.X[i] = self._map_x(x)
                        self.gt_dev.Y[i] = self._map_y(y)

                    # Clear touch flag
                    self._write_reg(self.POINT_INFO, [0x00])

                    return touch_count

            self.gt_dev.Touch = 0
            return 0

        except Exception as e:
            logger.error(f"Touch read error: {e}")
            self.gt_dev.Touch = 0
            return 0

    def _map_x(self, raw_x: int) -> int:
        """Map raw X coordinate to display coordinates"""
        return int((raw_x * self.X_MAX) / 1024)

    def _map_y(self, raw_y: int) -> int:
        """Map raw Y coordinate to display coordinates"""
        return int((raw_y * self.Y_MAX) / 1024)

    def scan(self, scan_dir: int = 0) -> int:
        """Scan for touch events

        Args:
            scan_dir: Scan direction (0-3 for rotation)

        Returns:
            Number of touch points detected
        """
        self.scan_dir = scan_dir

        # Save old state
        self.gt_old.X[0] = self.gt_dev.X[0]
        self.gt_old.Y[0] = self.gt_dev.Y[0]
        self.gt_old.Touch = self.gt_dev.Touch

        # Read new touch data
        return self.read_touch()

    def get_point(self) -> Tuple[int, int, bool]:
        """Get first touch point coordinates

        Returns:
            Tuple of (x, y, is_touched)
        """
        if self.gt_dev.Touch > 0:
            return (self.gt_dev.X[0], self.gt_dev.Y[0], True)
        return (0, 0, False)


class GT_Development:
    """Touch device state"""

    def __init__(self):
        self.Touch = 0  # Number of touch points
        self.X = [0] * 5  # X coordinates for up to 5 points
        self.Y = [0] * 5  # Y coordinates for up to 5 points
        self.S = [0] * 5  # Touch size/pressure (optional)


class GT_Old:
    """Previous touch state for comparison"""

    def __init__(self):
        self.Touch = 0
        self.X = [0] * 5
        self.Y = [0] * 5
        self.S = [0] * 5


# Convenience function for testing
def test_touch():
    """Test touch controller"""
    gt = GT1151()

    logger.info("Touch controller test - touch the screen (Ctrl+C to exit)")
    try:
        while True:
            count = gt.scan()
            if count > 0:
                x, y, touched = gt.get_point()
                logger.info(f"Touch detected: ({x}, {y}) - {count} point(s)")
            time.sleep(0.1)

    except KeyboardInterrupt:
        logger.info("Test stopped")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_touch()
