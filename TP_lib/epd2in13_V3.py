"""
Enhanced EPD 2.13" V3 E-ink Display Driver
===========================================

Improved driver for Waveshare 2.13" V3 e-ink display with:
- Automatic hardware detection
- Mock mode for testing without hardware
- Better error handling
- Performance optimizations
- Detailed logging

Display specifications:
- Resolution: 250x122 pixels
- Interface: SPI
- Partial refresh support
- Black and white display
"""

import logging
import time
from typing import Optional
from PIL import Image

logger = logging.getLogger(__name__)

# Try to import hardware libraries
try:
    import spidev
    import RPi.GPIO as GPIO
    HW_AVAILABLE = True
except ImportError:
    HW_AVAILABLE = False
    logger.warning("Hardware libraries not available - running in MOCK mode")


class EPD:
    """E-Paper Display 2.13" V3 Driver"""

    # Display resolution
    WIDTH = 122
    HEIGHT = 250

    # Display update modes
    FULL_UPDATE = 0
    PART_UPDATE = 1

    # GPIO pin definitions (BCM numbering)
    RST_PIN = 17
    DC_PIN = 25
    CS_PIN = 8
    BUSY_PIN = 24

    def __init__(self, mock_mode: bool = None):
        """Initialize EPD driver

        Args:
            mock_mode: Force mock mode (None = auto-detect, True = mock, False = hardware)
        """
        self.mock_mode = mock_mode if mock_mode is not None else (not HW_AVAILABLE)
        self.width = EPD.WIDTH
        self.height = EPD.HEIGHT
        self.FULL_UPDATE = EPD.FULL_UPDATE
        self.PART_UPDATE = EPD.PART_UPDATE

        if self.mock_mode:
            logger.info("EPD initialized in MOCK mode (no hardware)")
            self.spi = None
        else:
            logger.info("EPD initializing with hardware")
            self._init_gpio()
            self._init_spi()

    def _init_gpio(self):
        """Initialize GPIO pins"""
        if self.mock_mode:
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.RST_PIN, GPIO.OUT)
            GPIO.setup(self.DC_PIN, GPIO.OUT)
            GPIO.setup(self.CS_PIN, GPIO.OUT)
            GPIO.setup(self.BUSY_PIN, GPIO.IN)
            logger.debug("GPIO pins initialized successfully")
        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
            self.mock_mode = True

    def _init_spi(self):
        """Initialize SPI interface"""
        if self.mock_mode:
            return

        try:
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)  # Bus 0, Device 0
            self.spi.max_speed_hz = 4000000
            self.spi.mode = 0
            logger.debug("SPI interface initialized successfully")
        except Exception as e:
            logger.error(f"SPI initialization failed: {e}")
            self.mock_mode = True
            self.spi = None

    def _digital_write(self, pin, value):
        """Write digital value to GPIO pin"""
        if not self.mock_mode:
            GPIO.output(pin, value)

    def _digital_read(self, pin):
        """Read digital value from GPIO pin"""
        if self.mock_mode:
            return 0
        return GPIO.input(pin)

    def _spi_writebyte(self, data):
        """Write bytes to SPI"""
        if self.mock_mode or not self.spi:
            return

        if isinstance(data, (list, bytearray, bytes)):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])

    def _reset(self):
        """Hardware reset"""
        if self.mock_mode:
            time.sleep(0.1)
            return

        self._digital_write(self.RST_PIN, 1)
        time.sleep(0.2)
        self._digital_write(self.RST_PIN, 0)
        time.sleep(0.002)
        self._digital_write(self.RST_PIN, 1)
        time.sleep(0.2)

    def _send_command(self, command):
        """Send command to display"""
        if self.mock_mode:
            return

        self._digital_write(self.DC_PIN, 0)
        self._digital_write(self.CS_PIN, 0)
        self._spi_writebyte([command])
        self._digital_write(self.CS_PIN, 1)

    def _send_data(self, data):
        """Send data to display"""
        if self.mock_mode:
            return

        self._digital_write(self.DC_PIN, 1)
        self._digital_write(self.CS_PIN, 0)
        self._spi_writebyte([data])
        self._digital_write(self.CS_PIN, 1)

    def _send_data_bulk(self, data):
        """Send bulk data to display (more efficient for large transfers)"""
        if self.mock_mode:
            return

        self._digital_write(self.DC_PIN, 1)
        self._digital_write(self.CS_PIN, 0)
        self._spi_writebyte(data)  # Send all data at once
        self._digital_write(self.CS_PIN, 1)

    def _wait_until_idle(self):
        """Wait until display is idle"""
        if self.mock_mode:
            time.sleep(0.01)
            return

        logger.debug("Waiting for display idle...")
        timeout = time.time() + 10  # 10 second timeout
        while self._digital_read(self.BUSY_PIN) == 1:
            time.sleep(0.01)
            if time.time() > timeout:
                logger.warning("Display busy timeout!")
                break
        time.sleep(0.01)

    def init(self, update_mode=FULL_UPDATE):
        """Initialize display

        Args:
            update_mode: FULL_UPDATE or PART_UPDATE
        """
        logger.info(f"Initializing display (mode={'FULL' if update_mode == self.FULL_UPDATE else 'PARTIAL'})")

        if self.mock_mode:
            time.sleep(0.1)
            return 0

        try:
            self._reset()
            self._wait_until_idle()

            if update_mode == self.FULL_UPDATE:
                self._init_full()
            else:
                self._init_part()

            return 0
        except Exception as e:
            logger.error(f"Display initialization failed: {e}")
            return -1

    def _init_full(self):
        """Initialize for full update"""
        self._send_command(0x12)  # SWRESET
        self._wait_until_idle()

        self._send_command(0x01)  # Driver output control
        self._send_data(0xF9)
        self._send_data(0x00)
        self._send_data(0x00)

        self._send_command(0x11)  # Data entry mode
        self._send_data(0x03)

        self._send_command(0x44)  # Set RAM X address
        self._send_data(0x00)
        self._send_data(0x0F)

        self._send_command(0x45)  # Set RAM Y address
        self._send_data(0xF9)
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x00)

        self._send_command(0x3C)  # Border waveform
        self._send_data(0x03)

        self._send_command(0x2C)  # VCOM voltage
        self._send_data(0x55)

        self._send_command(0x03)  # Gate voltage
        self._send_data(0x15)

        self._send_command(0x04)  # Source voltage
        self._send_data(0x41)
        self._send_data(0xA8)
        self._send_data(0x32)

        self._send_command(0x3A)  # Dummy line period
        self._send_data(0x30)

        self._send_command(0x3B)  # Gate time
        self._send_data(0x0A)

        self._wait_until_idle()

    def _init_part(self):
        """Initialize for partial update"""
        self._send_command(0x2C)  # VCOM voltage
        self._send_data(0x26)
        self._wait_until_idle()

        self._send_command(0x32)  # Write LUT register
        # Partial update LUT
        lut_vcom_dc = [
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x01, 0x20, 0x20, 0x00, 0x00, 0x01,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ]
        for val in lut_vcom_dc:
            self._send_data(val)

        self._send_command(0x37)  # Display update control
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x00)
        self._send_data(0x40)
        self._send_data(0x00)
        self._send_data(0x00)

        self._send_command(0x22)  # Display update sequence
        self._send_data(0xC0)
        self._send_command(0x20)  # Activate
        self._wait_until_idle()

        self._send_command(0x3C)  # Border waveform
        self._send_data(0x01)

    def Clear(self, color=0xFF):
        """Clear display to color

        Args:
            color: 0xFF for white, 0x00 for black
        """
        logger.debug(f"Clearing display to color {color:#x}")

        if self.mock_mode:
            time.sleep(0.1)
            return

        self._send_command(0x24)  # Write RAM
        # Bulk send for efficiency
        self._send_data_bulk([color] * (self.height * self.width // 8))

        self._send_command(0x22)  # Display update sequence
        self._send_data(0xf7)
        self._send_command(0x20)  # Activate
        self._wait_until_idle()

    def getbuffer(self, image):
        """Convert PIL image to display buffer

        Args:
            image: PIL Image object (must be mode '1')

        Returns:
            Byte array suitable for display
        """
        if image.mode != '1':
            raise ValueError("Image must be in mode '1' (1-bit pixels)")

        # Rotate and flip image to match display orientation
        img = image.rotate(180)

        buf = bytearray(img.tobytes('raw'))
        return buf

    def displayPartial(self, image_buffer):
        """Display image buffer using partial update

        Args:
            image_buffer: Byte array from getbuffer()
        """
        if self.mock_mode:
            logger.debug("Mock partial display update")
            time.sleep(0.05)
            return

        self._send_command(0x24)  # Write RAM
        self._send_data_bulk(image_buffer)

        self._send_command(0x22)  # Display update sequence
        self._send_data(0x0F)
        self._send_command(0x20)  # Activate
        self._wait_until_idle()

    def displayPartBaseImage(self, image_buffer):
        """Set base image for partial updates

        Args:
            image_buffer: Byte array from getbuffer()
        """
        if self.mock_mode:
            logger.debug("Mock base image set")
            time.sleep(0.05)
            return

        self._send_command(0x24)  # Write RAM (old data)
        self._send_data_bulk(image_buffer)

        self._send_command(0x26)  # Write RAM (new data)
        self._send_data_bulk(image_buffer)

        self._send_command(0x22)  # Display update
        self._send_data(0xf7)
        self._send_command(0x20)  # Activate
        self._wait_until_idle()

    def sleep(self):
        """Put display into deep sleep mode"""
        logger.debug("Entering sleep mode")

        if self.mock_mode:
            return

        self._send_command(0x10)  # Deep sleep
        self._send_data(0x01)
        time.sleep(0.1)

    def module_exit(self):
        """Clean up resources"""
        logger.info("Cleaning up EPD resources")

        if self.mock_mode:
            return

        try:
            if self.spi:
                self.spi.close()
            GPIO.output(self.RST_PIN, 0)
            GPIO.output(self.DC_PIN, 0)
            GPIO.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


# Convenience function for testing
def test_display():
    """Test display with simple pattern"""
    epd = EPD()
    epd.init(EPD.FULL_UPDATE)
    epd.Clear(0xFF)

    # Create test image
    from PIL import Image, ImageDraw
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    draw.rectangle((10, 10, 100, 50), outline=0)
    draw.text((20, 20), "TEST", fill=0)

    epd.displayPartBaseImage(epd.getbuffer(image))
    epd.sleep()
    epd.module_exit()
    logger.info("Test complete")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    test_display()
