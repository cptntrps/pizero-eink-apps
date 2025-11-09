"""
Touch Event Handler
===================

Abstracts GPIO/touch interrupt polling thread to eliminate boilerplate
duplication across applications.

Eliminates 88 lines of duplicated threading code across 8 applications.
"""

import time
import threading
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)


# ============================================================================
# TOUCH HANDLER CLASS
# ============================================================================

class TouchHandler:
    """Reusable touch detection thread

    Handles GPIO/touch interrupt polling in background thread with
    automatic lifecycle management.

    Eliminates the need to write threading boilerplate in every app.

    Example:
        >>> touch = TouchHandler(gt, gt_dev)
        >>> touch.start()
        >>> try:
        ...     while True:
        ...         if touch.is_touched():
        ...             print("Touch detected!")
        ...         time.sleep(0.1)
        ... finally:
        ...     touch.stop()
    """

    def __init__(
        self,
        gt,
        gt_dev,
        interval: float = 0.01,
        on_error: Optional[Callable] = None
    ):
        """Initialize touch handler

        Args:
            gt: Touch driver interface (e.g., gt1151 instance)
            gt_dev: Touch device state object
            interval: Polling interval in seconds (default: 10ms)
            on_error: Optional callback for error handling

        Example:
            >>> def handle_error(e):
            ...     logger.error(f"Touch error: {e}")
            >>> touch = TouchHandler(gt, gt_dev, on_error=handle_error)
        """
        self.gt = gt
        self.gt_dev = gt_dev
        self.interval = interval
        self.on_error = on_error or self._default_error_handler
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._flag = [1]  # List for mutable reference

    def start(self) -> None:
        """Start touch detection thread

        Safe to call multiple times - will not start duplicate threads.

        Example:
            >>> touch = TouchHandler(gt, gt_dev)
            >>> touch.start()
            >>> # Thread is now running
        """
        if self._running:
            logger.warning("Touch handler already running")
            return

        self._running = True
        self._flag[0] = 1
        self._thread = threading.Thread(target=self._irq_loop, daemon=True)
        self._thread.start()
        logger.debug("Touch detection thread started")

    def stop(self) -> None:
        """Stop touch detection thread

        Blocks until thread terminates (with timeout).

        Example:
            >>> touch.stop()
            >>> # Thread has stopped
        """
        if not self._running:
            return

        self._running = False
        self._flag[0] = 0

        if self._thread:
            self._thread.join(timeout=1.0)
            if self._thread.is_alive():
                logger.warning("Touch thread did not terminate cleanly")

        logger.debug("Touch detection thread stopped")

    def is_running(self) -> bool:
        """Check if touch detection is running

        Returns:
            bool: True if running, False otherwise

        Example:
            >>> if touch.is_running():
            ...     print("Touch detection active")
        """
        return self._running

    def is_touched(self) -> bool:
        """Check if touch is currently detected

        Returns:
            bool: True if touch active, False otherwise

        Example:
            >>> if touch.is_touched():
            ...     handle_touch_event()
        """
        return getattr(self.gt_dev, 'Touch', 0) == 1

    def get_flag(self) -> list:
        """Get flag reference for legacy app compatibility

        Returns:
            list: Mutable flag reference [0 or 1]

        Example:
            >>> flag_t = touch.get_flag()
            >>> while flag_t[0] == 1:
            ...     # App loop
        """
        return self._flag

    def _irq_loop(self) -> None:
        """Internal IRQ polling loop

        Runs in background thread, continuously polls GPIO pin.
        """
        while self._flag[0] == 1 and self._running:
            try:
                if self.gt.digital_read(self.gt.INT) == 0:
                    self.gt_dev.Touch = 1
                else:
                    self.gt_dev.Touch = 0
            except Exception as e:  # pylint: disable=broad-exception-caught
                self.on_error(e)

            time.sleep(self.interval)

    def _default_error_handler(self, error: Exception) -> None:
        """Default error handler

        Args:
            error: Exception that occurred
        """
        logger.error("Touch detection error: %s", error)

    def __enter__(self):
        """Context manager entry - start thread"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - stop thread"""
        self.stop()


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_touch_handler(gt, gt_dev, interval: float = 0.01) -> TouchHandler:
    """Factory function for TouchHandler

    Args:
        gt: Touch driver interface
        gt_dev: Touch device state object
        interval: Polling interval in seconds

    Returns:
        TouchHandler: Initialized handler (not started)

    Example:
        >>> touch = create_touch_handler(gt, gt_dev)
        >>> with touch:
        ...     # Use touch handler
        ...     pass
    """
    return TouchHandler(gt, gt_dev, interval)


def check_exit_requested(gt_dev) -> bool:
    """Check if exit has been requested by menu system

    Args:
        gt_dev: Touch device object

    Returns:
        bool: True if exit requested, False otherwise

    Example:
        >>> if check_exit_requested(gt_dev):
        ...     logger.info("Exit requested")
        ...     break
    """
    return hasattr(gt_dev, "exit_requested") and gt_dev.exit_requested


def cleanup_touch_state(gt_old) -> None:
    """Reset touch state to clean values

    Args:
        gt_old: Previous touch state object

    Example:
        >>> cleanup_touch_state(gt_old)
        >>> # Touch state reset to zeros
    """
    gt_old.X[0] = 0
    gt_old.Y[0] = 0
    gt_old.S[0] = 0
