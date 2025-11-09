#!/usr/bin/python3
"""Forbidden App - Shows locked message with unified input handling."""

from shared.app_utils import setup_logging, ConfigLoader
from display import canvas, fonts, text, create_input_handler
from TP_lib import gt1151, epd2in13_V3
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python/lib'))


logger = setup_logging("forbidden_app")


def draw_forbidden_message(epd, gt_dev, gt_old, gt):
    """Show the forbidden message with dual input support (touch/button)."""
    exit_requested = False

    def on_exit():
        """Exit handler for both input modes."""
        nonlocal exit_requested
        exit_requested = True
        logger.info("Exit requested via input handler")

    try:
        # Load configuration
        msg1 = ConfigLoader.get_value('forbidden', 'message_line1', 'Access Forbidden')
        msg2 = ConfigLoader.get_value('forbidden', 'message_line2', 'Access Denied')

        # Create canvas
        img, draw = canvas.create_canvas()
        font_big = fonts.get_font('Roboto-Bold', 16)
        font_small = fonts.get_font('Roboto-Regular', 11)

        # Draw centered messages
        text.draw_centered_text(draw, msg1, y=35, font=font_big, color=0)
        text.draw_centered_text(draw, msg2, y=60, font=font_big, color=0)
        text.draw_centered_text(draw, "Hold: Exit", y=110, font=font_small, color=0)

        # Display
        epd.displayPartial(epd.getbuffer(img))
        logger.info("Showing forbidden message")

        # Create unified input handler (auto-detects touch vs button)
        handler = create_input_handler(gt=gt, gt_dev=gt_dev, gt_old=gt_old)
        logger.info(f"Input mode: {handler.mode}")

        # Setup callbacks
        if handler.mode == "touch":
            # Touch mode: exit on tap
            handler.on_short_press = on_exit
        else:
            # Button mode: exit on long press
            handler.on_long_press = on_exit

        # Start input monitoring
        handler.start()

        try:
            while not exit_requested:
                time.sleep(0.1)
        finally:
            handler.stop()

    except Exception as e:
        logger.error(f"Error displaying forbidden message: {e}")
        raise
