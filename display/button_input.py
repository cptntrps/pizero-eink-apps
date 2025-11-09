"""
Button Input Handler
Simplified single-button input system for Pi Zero 2W e-ink display

Supports only SHORT and LONG press (no multi-press patterns)
Designed for single GPIO button (PiSugar battery button on GPIO 3)
"""

import time
import logging
from enum import Enum
from typing import Optional, Callable
from gpiozero import Button
import threading
from .input_handler import InputHandler

logger = logging.getLogger(__name__)


class ButtonEvent(Enum):
    """Button event types (simplified)"""
    NONE = 0
    SHORT_PRESS = 1  # Quick press (<2s)
    LONG_PRESS = 2   # Hold (≥2s)


class ButtonInputHandler(InputHandler):
    """
    Simple button input handler with SHORT and LONG press detection

    Usage:
        handler = ButtonInputHandler(gpio_pin=3)
        handler.on_short_press = lambda: print("Short!")
        handler.on_long_press = lambda: print("Long!")
        handler.start()

        # In main loop
        while running:
            handler.poll()
            time.sleep(0.1)

        handler.stop()
    """

    def __init__(
        self,
        gpio_pin: int = 3,
        long_press_threshold: float = 2.0,
        bounce_time: float = 0.1,
        pull_up: bool = True
    ):
        """
        Initialize button handler

        Args:
            gpio_pin: GPIO pin number (default: 3 for PiSugar)
            long_press_threshold: Seconds to trigger long press (default: 2.0)
            bounce_time: Debounce time in seconds (default: 0.1)
            pull_up: Use pull-up resistor (default: True)
        """
        super().__init__()

        self.gpio_pin = gpio_pin
        self.long_press_threshold = long_press_threshold

        # Initialize button
        self.button = Button(gpio_pin, pull_up=pull_up, bounce_time=bounce_time)

        # State tracking
        self.press_start_time: Optional[float] = None
        self.long_press_triggered = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.running = False

        # Setup button event handlers
        self.button.when_pressed = self._on_button_pressed
        self.button.when_released = self._on_button_released

        logger.info(f"Button handler initialized on GPIO {gpio_pin}")

    def _on_button_pressed(self):
        """Internal: Called when button is pressed down"""
        self.press_start_time = time.time()
        self.long_press_triggered = False
        logger.debug("Button pressed")

    def _on_button_released(self):
        """Internal: Called when button is released"""
        if self.press_start_time is None:
            return

        duration = time.time() - self.press_start_time
        self.press_start_time = None

        logger.debug(f"Button released after {duration:.2f}s")

        # Don't trigger short press if long press already handled
        if self.long_press_triggered:
            logger.debug("Long press already handled, skipping short press")
            return

        # Short press
        if duration < self.long_press_threshold:
            logger.info("SHORT PRESS detected")
            if self.on_short_press:
                try:
                    self.on_short_press()
                except Exception as e:
                    logger.error(f"Error in short press callback: {e}")

    def _monitor_long_press(self):
        """Background thread: Monitor for long press"""
        while self.running:
            if self.press_start_time is not None and not self.long_press_triggered:
                duration = time.time() - self.press_start_time

                # Long press threshold reached
                if duration >= self.long_press_threshold and self.button.is_pressed:
                    self.long_press_triggered = True
                    logger.info("LONG PRESS detected")

                    if self.on_long_press:
                        try:
                            self.on_long_press()
                        except Exception as e:
                            logger.error(f"Error in long press callback: {e}")

            time.sleep(0.1)

    @property
    def mode(self) -> str:
        """Get input mode identifier

        Returns:
            str: Always returns "button"
        """
        return "button"

    def start(self):
        """Start button monitoring thread"""
        if self.running:
            logger.warning("Button handler already running")
            return

        self.running = True
        self._is_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitor_long_press,
            daemon=True,
            name="ButtonMonitor"
        )
        self.monitoring_thread.start()
        logger.info("Button monitoring started")

    def stop(self):
        """Stop button monitoring"""
        self.running = False
        self._is_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        logger.info("Button monitoring stopped")

    def poll(self) -> ButtonEvent:
        """
        Poll for button events (non-blocking)

        Note: Events are handled via callbacks (on_short_press, on_long_press)
        This method is here for API compatibility but callbacks are recommended.

        Returns:
            ButtonEvent.NONE (events are callback-based)
        """
        # Events are handled via callbacks in background thread
        return ButtonEvent.NONE

    def is_pressed(self) -> bool:
        """Check if button is currently pressed"""
        return self.button.is_pressed

    def get_press_duration(self) -> float:
        """Get current press duration if button is held"""
        if self.press_start_time is None:
            return 0.0
        return time.time() - self.press_start_time

    def __enter__(self):
        """Context manager support"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support"""
        self.stop()


# Convenience function for getting button handler from config
def create_button_handler(config: dict = None) -> ButtonInputHandler:
    """
    Create button handler from configuration

    Args:
        config: Configuration dict with hardware.button settings

    Returns:
        Configured ButtonInputHandler

    Example config:
        {
            "hardware": {
                "button": {
                    "gpio_pin": 3,
                    "long_press_threshold": 2.0,
                    "bounce_time": 0.1
                }
            }
        }
    """
    if config is None:
        config = {}

    button_config = config.get('hardware', {}).get('button', {})

    return ButtonInputHandler(
        gpio_pin=button_config.get('gpio_pin', 3),
        long_press_threshold=button_config.get('long_press_threshold', 2.0),
        bounce_time=button_config.get('bounce_time', 0.1),
        pull_up=button_config.get('pull_up', True)
    )
