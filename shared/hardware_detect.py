"""
Hardware Detection Module for Pi Zero 2W

Detects connected hardware components including:
- GT1151 touchscreen (I2C 0x5D, GPIO 27 interrupt)
- PiSugar battery module (I2C 0x57 or 0x32)

Provides auto-detection and configuration recommendations.
"""

import logging
import os
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Hardware I2C addresses
GT1151_I2C_ADDRESS = 0x5D  # GT1151 touchscreen controller
PISUGAR_I2C_ADDRESSES = [0x57, 0x32]  # PiSugar 2/3 battery module addresses

# GPIO pins
GT1151_INT_PIN = 27  # GT1151 interrupt pin
PISUGAR_BUTTON_PIN = 3  # PiSugar button (also can be used as generic button)


def _check_i2c_device(address: int) -> bool:
    """
    Check if an I2C device exists at the given address.

    Args:
        address: I2C address to check (e.g., 0x5D)

    Returns:
        True if device detected, False otherwise
    """
    try:
        # Try to detect I2C device using i2cdetect command
        # Format: i2cdetect -y 1 (for Pi Zero 2W)
        import subprocess
        result = subprocess.run(
            ['i2cdetect', '-y', '1'],
            capture_output=True,
            text=True,
            timeout=2
        )

        # Convert address to hex string format used by i2cdetect
        hex_addr = f"{address:02x}"

        # Check if address appears in output
        if hex_addr in result.stdout.lower():
            logger.debug(f"I2C device detected at 0x{hex_addr}")
            return True

        logger.debug(f"No I2C device at 0x{hex_addr}")
        return False

    except FileNotFoundError:
        logger.warning("i2cdetect command not found. Install i2c-tools package.")
        return False
    except subprocess.TimeoutExpired:
        logger.warning(f"I2C detection timeout for address 0x{address:02x}")
        return False
    except Exception as e:
        logger.warning(f"Error checking I2C device at 0x{address:02x}: {e}")
        return False


def _check_gpio_pin(pin: int) -> Tuple[bool, Optional[str]]:
    """
    Check if a GPIO pin is available and get its state.

    Args:
        pin: GPIO pin number (BCM numbering)

    Returns:
        Tuple of (is_available, state_info)
    """
    try:
        gpio_path = f"/sys/class/gpio/gpio{pin}"

        # Check if GPIO is exported
        if os.path.exists(gpio_path):
            # Try to read direction and value
            try:
                with open(f"{gpio_path}/direction", 'r') as f:
                    direction = f.read().strip()
                with open(f"{gpio_path}/value", 'r') as f:
                    value = f.read().strip()

                state = f"direction={direction}, value={value}"
                logger.debug(f"GPIO {pin}: {state}")
                return True, state
            except Exception as e:
                logger.debug(f"GPIO {pin} exists but cannot read state: {e}")
                return True, "exported"

        # GPIO not exported, but may be available
        logger.debug(f"GPIO {pin} not exported")
        return True, "available"

    except Exception as e:
        logger.warning(f"Error checking GPIO pin {pin}: {e}")
        return False, None


def detect_touch_hardware() -> bool:
    """
    Detect GT1151 touchscreen hardware.

    Checks for:
    1. GT1151 I2C device at address 0x5D
    2. GPIO 27 availability (interrupt pin)

    Returns:
        True if touch hardware detected, False otherwise
    """
    logger.info("Detecting GT1151 touchscreen hardware...")

    # Check I2C device
    has_i2c = _check_i2c_device(GT1151_I2C_ADDRESS)

    # Check GPIO interrupt pin
    gpio_available, gpio_state = _check_gpio_pin(GT1151_INT_PIN)

    if has_i2c:
        logger.info("GT1151 touchscreen detected (I2C 0x5D)")
        if gpio_available:
            logger.info(f"GT1151 interrupt pin GPIO {GT1151_INT_PIN} is available")
        else:
            logger.warning(f"GT1151 detected but GPIO {GT1151_INT_PIN} may not be available")
        return True

    logger.info("No GT1151 touchscreen detected")
    return False


def detect_pisugar() -> bool:
    """
    Detect PiSugar battery module.

    Checks for PiSugar I2C addresses:
    - 0x57 (PiSugar 2)
    - 0x32 (PiSugar 3)

    Returns:
        True if PiSugar detected, False otherwise
    """
    logger.info("Detecting PiSugar battery module...")

    for address in PISUGAR_I2C_ADDRESSES:
        if _check_i2c_device(address):
            logger.info(f"PiSugar detected at I2C address 0x{address:02x}")
            return True

    logger.info("No PiSugar battery module detected")
    return False


def auto_detect_hardware_profile() -> str:
    """
    Auto-detect hardware configuration profile.

    Detection logic:
    1. If GT1151 touchscreen detected -> "touch"
    2. If PiSugar detected (no touch) -> "button"
    3. Fallback -> "button" (safest default)

    Returns:
        Profile name: "touch" or "button"
    """
    logger.info("Auto-detecting hardware profile...")

    has_touch = detect_touch_hardware()
    has_pisugar = detect_pisugar()

    if has_touch:
        profile = "touch"
        logger.info(f"Selected profile: {profile} (GT1151 touchscreen detected)")
    elif has_pisugar:
        profile = "button"
        logger.info(f"Selected profile: {profile} (PiSugar button detected)")
    else:
        profile = "button"
        logger.info(f"Selected profile: {profile} (fallback - no specific hardware detected)")

    return profile


def get_hardware_info() -> Dict:
    """
    Get comprehensive hardware detection information.

    Returns:
        Dictionary containing:
        - has_touch: bool - GT1151 detected
        - has_pisugar: bool - PiSugar detected
        - recommended_profile: str - "touch" or "button"
        - gpio_info: dict - GPIO pin states
        - i2c_devices: list - Detected I2C addresses
    """
    logger.info("Gathering hardware information...")

    # Detect hardware
    has_touch = detect_touch_hardware()
    has_pisugar = detect_pisugar()
    recommended_profile = auto_detect_hardware_profile()

    # Check GPIO pins
    gpio_info = {}
    for pin, name in [
        (GT1151_INT_PIN, "GT1151_INT"),
        (PISUGAR_BUTTON_PIN, "BUTTON")
    ]:
        available, state = _check_gpio_pin(pin)
        gpio_info[name] = {
            "pin": pin,
            "available": available,
            "state": state
        }

    # List detected I2C devices
    i2c_devices = []
    if has_touch:
        i2c_devices.append(f"0x{GT1151_I2C_ADDRESS:02x}")
    for addr in PISUGAR_I2C_ADDRESSES:
        if _check_i2c_device(addr):
            i2c_devices.append(f"0x{addr:02x}")

    info = {
        "has_touch": has_touch,
        "has_pisugar": has_pisugar,
        "recommended_profile": recommended_profile,
        "gpio_info": gpio_info,
        "i2c_devices": i2c_devices,
        "detection_summary": {
            "GT1151_touchscreen": "detected" if has_touch else "not detected",
            "PiSugar_battery": "detected" if has_pisugar else "not detected",
            "input_mode": "touch" if has_touch else "button"
        }
    }

    logger.info(f"Hardware detection complete: {info['detection_summary']}")
    return info


def get_hardware_profile_from_env() -> Optional[str]:
    """
    Get hardware profile from environment variable.

    Returns:
        Profile name from PIZERO_HARDWARE_PROFILE env var, or None
    """
    profile = os.getenv('PIZERO_HARDWARE_PROFILE')
    if profile and profile.lower() != 'auto':
        logger.info(f"Hardware profile from environment: {profile}")
        return profile.lower()
    return None


def get_input_mode() -> str:
    """
    Determine input mode based on environment or auto-detection.

    Priority:
    1. PIZERO_INPUT_MODE environment variable
    2. PIZERO_HARDWARE_PROFILE environment variable
    3. Auto-detection

    Returns:
        Input mode: "touch" or "button"
    """
    # Check environment variable for input mode
    input_mode = os.getenv('PIZERO_INPUT_MODE')
    if input_mode and input_mode.lower() != 'auto':
        logger.info(f"Input mode from PIZERO_INPUT_MODE: {input_mode}")
        return input_mode.lower()

    # Check environment variable for hardware profile
    profile = get_hardware_profile_from_env()
    if profile:
        logger.info(f"Input mode from PIZERO_HARDWARE_PROFILE: {profile}")
        return profile

    # Auto-detect
    logger.info("Auto-detecting input mode...")
    profile = auto_detect_hardware_profile()
    return profile


if __name__ == "__main__":
    # Setup logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "="*60)
    print("Pi Zero 2W Hardware Detection")
    print("="*60 + "\n")

    # Get full hardware info
    info = get_hardware_info()

    # Print results
    print("DETECTION RESULTS:")
    print("-" * 60)
    print(f"GT1151 Touchscreen:  {info['detection_summary']['GT1151_touchscreen']}")
    print(f"PiSugar Battery:     {info['detection_summary']['PiSugar_battery']}")
    print(f"Recommended Profile: {info['recommended_profile']}")
    print(f"Input Mode:          {info['detection_summary']['input_mode']}")

    if info['i2c_devices']:
        print(f"\nI2C Devices Found:   {', '.join(info['i2c_devices'])}")

    print("\nGPIO STATUS:")
    print("-" * 60)
    for name, gpio in info['gpio_info'].items():
        status = "✓" if gpio['available'] else "✗"
        print(f"{status} {name:20s} GPIO {gpio['pin']:2d}  ({gpio['state'] or 'unavailable'})")

    print("\n" + "="*60 + "\n")
