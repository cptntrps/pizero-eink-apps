"""
Input Abstraction Layer
=======================

Unified input handling system supporting both touchscreen and button input modes.

This module provides:
- Abstract InputHandler base class defining the common interface
- InputEvent enum for standardized event types
- Factory function for auto-detecting and creating appropriate handler

Hardware Support:
- Config A: Waveshare 2.13" WITH touch (GT driver, X/Y coordinates)
- Config B: Waveshare 2.13" WITHOUT touch + PiSugar button (GPIO 3)

Usage Example:
    >>> # Auto-detect hardware
    >>> handler = create_input_handler()
    >>> handler.on_short_press = lambda: print("Pressed!")
    >>> handler.on_touch = lambda x, y: print(f"Touched at {x}, {y}")
    >>>
    >>> with handler:
    ...     while running:
    ...         time.sleep(0.1)

Design Pattern:
    Uses Abstract Base Class pattern with factory for hardware abstraction.
    Callbacks provide event-driven architecture without polling complexity.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Callable, Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# INPUT EVENT TYPES
# ============================================================================

class InputEvent(Enum):
    """Standardized input event types across all input modes

    Values:
        NONE: No event detected
        SHORT_PRESS: Quick button press or tap (<2s)
        LONG_PRESS: Long button hold (≥2s)
        TOUCH: Touch detected (generic)
        TAP: Touch tap at specific coordinates
    """
    NONE = 0
    SHORT_PRESS = 1
    LONG_PRESS = 2
    TOUCH = 3
    TAP = 4


# ============================================================================
# ABSTRACT INPUT HANDLER
# ============================================================================

class InputHandler(ABC):
    """Abstract base class for unified input handling

    Defines common interface for both touchscreen and button input modes.
    Implementations must provide mode-specific behavior while maintaining
    consistent callback-based API.

    All input handlers support:
    - Start/stop lifecycle management
    - Active state checking
    - Event callbacks (mode-dependent)
    - Context manager protocol

    Attributes:
        on_short_press: Callback for short press/tap events
        on_long_press: Callback for long press/hold events
        on_touch: Callback for touch events (touch mode only)
        on_coordinates: Callback for coordinate events (x, y)

    Example:
        >>> handler = create_input_handler()
        >>> handler.on_short_press = lambda: print("Short press!")
        >>> handler.start()
        >>> try:
        ...     # Main loop
        ...     while running:
        ...         time.sleep(0.1)
        ... finally:
        ...     handler.stop()
    """

    def __init__(self):
        """Initialize base input handler"""
        self.on_short_press: Optional[Callable[[], None]] = None
        self.on_long_press: Optional[Callable[[], None]] = None
        self.on_touch: Optional[Callable[[], None]] = None
        self.on_coordinates: Optional[Callable[[int, int], None]] = None
        self._is_active = False

    @property
    @abstractmethod
    def mode(self) -> str:
        """Get input mode identifier

        Returns:
            str: Either "touch" or "button"

        Example:
            >>> if handler.mode == "touch":
            ...     print("Touch mode enabled")
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """Start input monitoring

        Begins background monitoring for input events. Safe to call
        multiple times - will not create duplicate threads.

        Example:
            >>> handler.start()
            >>> # Input monitoring now active
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop input monitoring

        Stops background monitoring and cleans up resources.
        Blocks until monitoring thread terminates.

        Example:
            >>> handler.stop()
            >>> # Input monitoring stopped
        """
        pass

    @property
    def is_active(self) -> bool:
        """Check if input monitoring is active

        Returns:
            bool: True if monitoring, False otherwise

        Example:
            >>> if handler.is_active:
            ...     print("Handler is running")
        """
        return self._is_active

    def __enter__(self):
        """Context manager entry - start monitoring

        Example:
            >>> with handler:
            ...     # Handler automatically started
            ...     pass
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop monitoring

        Example:
            >>> with handler:
            ...     pass
            >>> # Handler automatically stopped
        """
        self.stop()


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_input_handler(
    config: Optional[dict] = None,
    gt=None,
    gt_dev=None,
    gt_old=None,
    gpio_pin: Optional[int] = None
) -> InputHandler:
    """Factory function to create appropriate input handler

    Auto-detects hardware configuration and returns the correct handler
    implementation (TouchInputHandler or ButtonInputHandler).

    Detection Logic:
        1. If gt, gt_dev, gt_old provided -> TouchInputHandler
        2. If gpio_pin provided or config specifies button -> ButtonInputHandler
        3. If config has touch settings -> TouchInputHandler
        4. Default -> ButtonInputHandler (GPIO 3)

    Args:
        config: Optional configuration dict with hardware settings
        gt: Touch driver interface (for touch mode)
        gt_dev: Touch device state object (for touch mode)
        gt_old: Previous touch state object (for touch mode)
        gpio_pin: GPIO pin number (for button mode)

    Returns:
        InputHandler: Configured handler instance (not started)

    Config Format:
        {
            "hardware": {
                "touch": {
                    "enabled": true,
                    "driver": "GT1151"
                },
                "button": {
                    "enabled": true,
                    "gpio_pin": 3,
                    "long_press_threshold": 2.0
                }
            }
        }

    Example:
        >>> # Auto-detect from GT objects
        >>> handler = create_input_handler(gt=gt, gt_dev=gt_dev, gt_old=gt_old)
        >>> print(handler.mode)  # "touch"

        >>> # Explicit button mode
        >>> handler = create_input_handler(gpio_pin=3)
        >>> print(handler.mode)  # "button"

        >>> # From config
        >>> config = {"hardware": {"button": {"gpio_pin": 3}}}
        >>> handler = create_input_handler(config=config)
    """
    # Import here to avoid circular dependencies
    from .touch_input import TouchInputHandler
    from .button_input import ButtonInputHandler

    # Explicit touch mode - GT objects provided
    if gt is not None and gt_dev is not None:
        logger.info("Creating TouchInputHandler (GT objects provided)")
        return TouchInputHandler(
            gt=gt,
            gt_dev=gt_dev,
            gt_old=gt_old,
            config=config
        )

    # Check config for explicit mode
    if config:
        hardware_config = config.get('hardware', {})

        # Touch mode configured
        touch_config = hardware_config.get('touch', {})
        if touch_config.get('enabled', False):
            logger.info("Creating TouchInputHandler (config enabled)")
            # Note: Touch mode requires GT objects, cannot create from config alone
            logger.warning("Touch mode enabled in config but no GT objects provided")
            logger.warning("Falling back to ButtonInputHandler")

        # Button mode configured
        button_config = hardware_config.get('button', {})
        if button_config.get('enabled', True):  # Default to enabled
            logger.info("Creating ButtonInputHandler (config enabled)")
            return ButtonInputHandler(
                gpio_pin=button_config.get('gpio_pin', gpio_pin or 3),
                long_press_threshold=button_config.get('long_press_threshold', 2.0),
                bounce_time=button_config.get('bounce_time', 0.1),
                pull_up=button_config.get('pull_up', True)
            )

    # Explicit button mode - GPIO pin provided
    if gpio_pin is not None:
        logger.info(f"Creating ButtonInputHandler (GPIO {gpio_pin})")
        return ButtonInputHandler(gpio_pin=gpio_pin)

    # Default: Button mode on GPIO 3 (PiSugar)
    logger.info("Creating ButtonInputHandler (default: GPIO 3)")
    return ButtonInputHandler(gpio_pin=3)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_input_mode(config: Optional[dict] = None) -> str:
    """Detect input mode from configuration

    Args:
        config: Optional configuration dict

    Returns:
        str: Either "touch" or "button"

    Example:
        >>> mode = detect_input_mode(config)
        >>> print(f"Detected: {mode}")
    """
    if config:
        hardware_config = config.get('hardware', {})

        # Check touch
        touch_config = hardware_config.get('touch', {})
        if touch_config.get('enabled', False):
            return "touch"

        # Check button
        button_config = hardware_config.get('button', {})
        if button_config.get('enabled', True):
            return "button"

    # Default to button
    return "button"


def get_input_info(handler: InputHandler) -> dict:
    """Get information about an input handler

    Args:
        handler: InputHandler instance

    Returns:
        dict: Handler information (mode, active state, etc.)

    Example:
        >>> info = get_input_info(handler)
        >>> print(f"Mode: {info['mode']}, Active: {info['active']}")
    """
    return {
        'mode': handler.mode,
        'active': handler.is_active,
        'type': type(handler).__name__,
        'has_short_press': handler.on_short_press is not None,
        'has_long_press': handler.on_long_press is not None,
        'has_touch': handler.on_touch is not None,
        'has_coordinates': handler.on_coordinates is not None,
    }
