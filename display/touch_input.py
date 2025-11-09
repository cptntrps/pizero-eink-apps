"""
Touch Input Handler
===================

TouchInputHandler implementation for Waveshare 2.13" displays with GT1151 touch driver.

This module provides touchscreen input handling compatible with the existing
GT driver infrastructure (gt, gt_dev, gt_old objects).

Features:
- Thread-safe touch polling
- Coordinate detection (X/Y)
- Tap event detection
- Compatible with existing touchscreen code patterns
- Implements InputHandler interface

Hardware:
- Waveshare 2.13" e-ink display with GT1151 touch controller
- Supports multi-touch coordinate tracking
- Uses GPIO interrupt polling

Usage Example:
    >>> from TP_lib import gt1151
    >>> gt = gt1151.GT1151()
    >>> gt_dev = gt1151.GT_Development()
    >>> gt_old = gt1151.GT_Development()
    >>>
    >>> handler = TouchInputHandler(gt, gt_dev, gt_old)
    >>> handler.on_touch = lambda: print("Touched!")
    >>> handler.on_coordinates = lambda x, y: print(f"At {x}, {y}")
    >>>
    >>> with handler:
    ...     while running:
    ...         time.sleep(0.1)
"""

import time
import threading
import logging
from typing import Optional, Callable
from .input_handler import InputHandler, InputEvent

logger = logging.getLogger(__name__)


# ============================================================================
# TOUCH INPUT HANDLER
# ============================================================================

class TouchInputHandler(InputHandler):
    """Touch input handler for GT1151 touchscreen

    Implements InputHandler interface for touchscreen input using the
    GT1151 touch driver. Provides coordinate detection and tap events.

    Thread-safe polling of touch state with callback-based event system.
    Compatible with existing GT driver patterns used across applications.

    Attributes:
        gt: Touch driver interface (GT1151)
        gt_dev: Touch device state object
        gt_old: Previous touch state object
        on_short_press: Callback for tap events
        on_touch: Callback for any touch detection
        on_coordinates: Callback for coordinate events (x, y)

    Example:
        >>> handler = TouchInputHandler(gt, gt_dev, gt_old)
        >>> handler.on_coordinates = lambda x, y: print(f"Touch at {x}, {y}")
        >>> handler.start()
    """

    def __init__(
        self,
        gt,
        gt_dev,
        gt_old=None,
        config: Optional[dict] = None,
        polling_interval: float = 0.01,
        tap_max_duration: float = 0.5
    ):
        """Initialize touch input handler

        Args:
            gt: Touch driver interface (e.g., gt1151 instance)
            gt_dev: Touch device state object
            gt_old: Previous touch state object (optional)
            config: Optional configuration dict
            polling_interval: Touch polling interval in seconds (default: 10ms)
            tap_max_duration: Max duration for tap vs hold (default: 0.5s)

        Example:
            >>> handler = TouchInputHandler(
            ...     gt=gt,
            ...     gt_dev=gt_dev,
            ...     gt_old=gt_old,
            ...     polling_interval=0.01
            ... )
        """
        super().__init__()

        self.gt = gt
        self.gt_dev = gt_dev
        self.gt_old = gt_old
        self.config = config or {}
        self.polling_interval = polling_interval
        self.tap_max_duration = tap_max_duration

        # Thread management
        self._running = False
        self._poll_thread: Optional[threading.Thread] = None
        self._irq_thread: Optional[threading.Thread] = None
        self._flag = [1]  # Mutable flag for thread control

        # Touch state tracking
        self._touch_start_time: Optional[float] = None
        self._last_touch_state = False
        self._last_coordinates: Optional[tuple] = None

        logger.info("TouchInputHandler initialized")

    @property
    def mode(self) -> str:
        """Get input mode identifier

        Returns:
            str: Always returns "touch"

        Example:
            >>> handler.mode
            'touch'
        """
        return "touch"

    def start(self) -> None:
        """Start touch monitoring threads

        Starts two background threads:
        1. IRQ polling thread - monitors GPIO interrupt pin
        2. Scan polling thread - reads touch coordinates

        Safe to call multiple times - will not create duplicate threads.

        Example:
            >>> handler.start()
            >>> # Touch monitoring now active
        """
        if self._running:
            logger.warning("Touch handler already running")
            return

        self._running = True
        self._is_active = True
        self._flag[0] = 1

        # Start IRQ monitoring thread (GPIO interrupt polling)
        self._irq_thread = threading.Thread(
            target=self._irq_polling_loop,
            daemon=True,
            name="TouchIRQ"
        )
        self._irq_thread.start()

        # Start touch scanning thread (coordinate reading)
        self._poll_thread = threading.Thread(
            target=self._touch_polling_loop,
            daemon=True,
            name="TouchScan"
        )
        self._poll_thread.start()

        logger.info("Touch monitoring threads started")

    def stop(self) -> None:
        """Stop touch monitoring

        Stops both background threads and cleans up resources.
        Blocks until threads terminate (with timeout).

        Example:
            >>> handler.stop()
            >>> # Touch monitoring stopped
        """
        if not self._running:
            return

        self._running = False
        self._is_active = False
        self._flag[0] = 0

        # Wait for threads to terminate
        if self._irq_thread:
            self._irq_thread.join(timeout=1.0)
            if self._irq_thread.is_alive():
                logger.warning("IRQ thread did not terminate cleanly")

        if self._poll_thread:
            self._poll_thread.join(timeout=1.0)
            if self._poll_thread.is_alive():
                logger.warning("Poll thread did not terminate cleanly")

        # Cleanup touch state
        if self.gt_old:
            self._cleanup_touch_state()

        logger.info("Touch monitoring stopped")

    def _irq_polling_loop(self) -> None:
        """Background thread: Poll GPIO interrupt pin

        Continuously monitors the GT driver's interrupt pin to detect
        when touch events occur. Updates gt_dev.Touch state.

        This mirrors the standard touch detection pattern used across
        the application codebase.
        """
        while self._flag[0] == 1 and self._running:
            try:
                # Check GPIO interrupt pin
                if self.gt.digital_read(self.gt.INT) == 0:
                    self.gt_dev.Touch = 1
                else:
                    self.gt_dev.Touch = 0
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"IRQ polling error: {e}")

            time.sleep(self.polling_interval)

    def _touch_polling_loop(self) -> None:
        """Background thread: Poll touch coordinates and events

        Continuously scans for touch input and processes coordinates.
        Triggers callbacks when touch events are detected.
        """
        while self._flag[0] == 1 and self._running:
            try:
                # Scan for touch input (updates gt_dev with coordinates)
                self.gt.GT_Scan(self.gt_dev, self.gt_old)

                # Process touch events
                self._process_touch_events()

            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(f"Touch polling error: {e}")

            time.sleep(self.polling_interval)

    def _process_touch_events(self) -> None:
        """Process current touch state and trigger callbacks

        Analyzes touch state changes and coordinates, then triggers
        appropriate callbacks based on the type of touch event detected.
        """
        current_touch = self.is_touched()

        # Touch started
        if current_touch and not self._last_touch_state:
            self._touch_start_time = time.time()
            logger.debug("Touch started")

            # Fire generic touch callback
            if self.on_touch:
                try:
                    self.on_touch()
                except Exception as e:  # pylint: disable=broad-exception-caught
                    logger.error(f"Error in on_touch callback: {e}")

        # Touch ended
        elif not current_touch and self._last_touch_state:
            if self._touch_start_time:
                duration = time.time() - self._touch_start_time
                logger.debug(f"Touch ended (duration: {duration:.2f}s)")

                # Get final coordinates
                x, y = self.get_coordinates()

                # Tap detection (short touch)
                if duration < self.tap_max_duration and x > 0 and y > 0:
                    logger.info(f"TAP detected at ({x}, {y})")

                    # Fire coordinate callback
                    if self.on_coordinates:
                        try:
                            self.on_coordinates(x, y)
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            logger.error(f"Error in on_coordinates callback: {e}")

                    # Fire short press callback
                    if self.on_short_press:
                        try:
                            self.on_short_press()
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            logger.error(f"Error in on_short_press callback: {e}")

                # Long touch/hold
                elif duration >= self.tap_max_duration:
                    logger.info(f"LONG TOUCH detected at ({x}, {y})")

                    # Fire long press callback
                    if self.on_long_press:
                        try:
                            self.on_long_press()
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            logger.error(f"Error in on_long_press callback: {e}")

                self._touch_start_time = None

        # Update state
        self._last_touch_state = current_touch

    def is_touched(self) -> bool:
        """Check if touch is currently detected

        Returns:
            bool: True if touch active, False otherwise

        Example:
            >>> if handler.is_touched():
            ...     print("Screen is being touched")
        """
        return getattr(self.gt_dev, 'Touch', 0) == 1

    def get_coordinates(self) -> tuple:
        """Get current touch coordinates

        Returns:
            tuple: (x, y) coordinates, or (0, 0) if no touch

        Example:
            >>> x, y = handler.get_coordinates()
            >>> print(f"Touch at {x}, {y}")
        """
        if self.gt_old:
            x = getattr(self.gt_old, 'X', [0])[0]
            y = getattr(self.gt_old, 'Y', [0])[0]
            return (x, y)
        return (0, 0)

    def get_touch_state(self) -> dict:
        """Get detailed touch state information

        Returns:
            dict: Touch state including coordinates, pressure, etc.

        Example:
            >>> state = handler.get_touch_state()
            >>> print(f"X: {state['x']}, Y: {state['y']}")
        """
        x, y = self.get_coordinates()
        s = getattr(self.gt_old, 'S', [0])[0] if self.gt_old else 0

        return {
            'active': self.is_touched(),
            'x': x,
            'y': y,
            'size': s,
            'duration': time.time() - self._touch_start_time if self._touch_start_time else 0
        }

    def _cleanup_touch_state(self) -> None:
        """Reset touch state to clean values

        Clears X, Y, S coordinates in gt_old object.
        """
        if self.gt_old:
            if hasattr(self.gt_old, 'X'):
                self.gt_old.X[0] = 0
            if hasattr(self.gt_old, 'Y'):
                self.gt_old.Y[0] = 0
            if hasattr(self.gt_old, 'S'):
                self.gt_old.S[0] = 0
            logger.debug("Touch state cleaned up")

    def get_flag(self) -> list:
        """Get flag reference for legacy compatibility

        Returns:
            list: Mutable flag reference [0 or 1]

        Example:
            >>> flag = handler.get_flag()
            >>> while flag[0] == 1:
            ...     # App loop
        """
        return self._flag


# ============================================================================
# FACTORY CONVENIENCE
# ============================================================================

def create_touch_handler(
    gt,
    gt_dev,
    gt_old=None,
    config: Optional[dict] = None
) -> TouchInputHandler:
    """Factory function for TouchInputHandler

    Args:
        gt: Touch driver interface
        gt_dev: Touch device state object
        gt_old: Previous touch state object (optional)
        config: Optional configuration dict

    Returns:
        TouchInputHandler: Initialized handler (not started)

    Example:
        >>> handler = create_touch_handler(gt, gt_dev, gt_old)
        >>> with handler:
        ...     # Use handler
        ...     pass
    """
    return TouchInputHandler(
        gt=gt,
        gt_dev=gt_dev,
        gt_old=gt_old,
        config=config
    )
