#!/usr/bin/python3
"""
Reboot Application - Dual-Input Refactored
===========================================
Provides system reboot confirmation dialog supporting both touchscreen and button input.

Input Modes:
- Touch Mode: Tap "Cancel" or "Reboot" buttons directly
- Button Mode:
  - SHORT PRESS: Toggle selection between Cancel/Reboot
  - LONG PRESS: Confirm selection
  - Indicator (►) shows current selection

Safety:
- Default selection is Cancel (safe fallback)
- Clear instructions for each mode
- Visual feedback for selection state

Uses unified InputHandler abstraction for hardware compatibility.
"""

from display.components import Button
from display.fonts import get_font_preset
from display.input_handler import create_input_handler
from shared.app_utils import setup_logging, check_exit_requested
from PIL import Image, ImageDraw
from TP_lib import gt1151, epd2in13_V3
import sys
import os
import time
import subprocess
import logging

# Path setup
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/lib')
sys.path.append(libdir)


logger = setup_logging('reboot_app', log_to_file=True)


def draw_reboot_screen(epd, selection=0, input_mode="touch"):
    """Draw reboot confirmation screen with selection state

    Args:
        epd: E-ink display driver
        selection: 0 = Cancel (default), 1 = Reboot
        input_mode: "touch" or "button" (affects instructions and visuals)
    """
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)

    # Title
    draw.text((50, 10), "Reboot System?", font=get_font_preset('title'), fill=0)

    # Button labels with selection indicator
    cancel_text = ("► Cancel" if selection == 0 else "  Cancel") if input_mode == "button" else "Cancel"
    reboot_text = ("► Reboot" if selection == 1 else "  Reboot") if input_mode == "button" else "Reboot"

    # Draw button backgrounds
    draw.rectangle([10, 50, 110, 80], outline=0, fill=255)
    draw.rectangle([140, 50, 240, 80], outline=0, fill=255)

    # Draw text
    draw.text((25, 60), cancel_text, font=get_font_preset('body'), fill=0)
    draw.text((150, 60), reboot_text, font=get_font_preset('body'), fill=0)

    # Instructions based on input mode
    if input_mode == "button":
        instr = "Press: Toggle | Hold: Confirm"
    else:
        instr = "Tap button to confirm"

    draw.text((20, 100), instr, font=get_font_preset('small'), fill=0)

    epd.displayPartial(epd.getbuffer(img))


def draw_rebooting_screen(epd):
    """Draw rebooting status screen"""
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)
    draw.text((60, 50), "Rebooting...", font=get_font_preset('title'), fill=0)
    epd.displayPartial(epd.getbuffer(img))


def draw_reboot_confirm(epd, gt_dev, gt_old, gt):
    """Show reboot confirmation screen with dual-input support

    Supports both:
    - Touch Mode: Tap buttons directly
    - Button Mode: Toggle selection with short press, confirm with long press
    """
    logger.info("Showing reboot confirmation screen")

    # Selection state: 0 = Cancel (default/safe), 1 = Reboot
    selection = 0
    running = True
    confirmed = False

    try:
        # Create input handler (auto-detects touch vs button mode)
        handler = create_input_handler(gt=gt, gt_dev=gt_dev, gt_old=gt_old)
        input_mode = handler.mode
        logger.info(f"Input mode: {input_mode}")

        # Define button regions for touch mode
        cancel_region = (10, 50, 110, 80)  # x1, y1, x2, y2
        reboot_region = (140, 50, 240, 80)

        def on_touch_coordinates(x, y):
            """Handle touch input - direct button tapping"""
            nonlocal selection, confirmed, running

            logger.info(f"Touch detected at ({x}, {y})")

            # Check which button was tapped
            if cancel_region[0] <= x <= cancel_region[2] and cancel_region[1] <= y <= cancel_region[3]:
                logger.info("Cancel button tapped")
                selection = 0
                confirmed = True
                running = False
            elif reboot_region[0] <= x <= reboot_region[2] and reboot_region[1] <= y <= reboot_region[3]:
                logger.info("Reboot button tapped")
                selection = 1
                confirmed = True
                running = False

        def on_short_press():
            """Handle button short press - toggle selection"""
            nonlocal selection

            if input_mode == "button":
                selection = 1 - selection  # Toggle: 0 <-> 1
                logger.info(f"Selection toggled to: {selection}")
                draw_reboot_screen(epd, selection, input_mode)

        def on_long_press():
            """Handle button long press - confirm selection"""
            nonlocal confirmed, running

            if input_mode == "button":
                logger.info(f"Selection confirmed: {selection}")
                confirmed = True
                running = False

        # Setup callbacks based on input mode
        if input_mode == "touch":
            handler.on_coordinates = on_touch_coordinates
        else:  # button mode
            handler.on_short_press = on_short_press
            handler.on_long_press = on_long_press

        # Draw initial screen
        draw_reboot_screen(epd, selection, input_mode)

        # Start input handler
        handler.start()

        # Main interaction loop
        while running:
            if check_exit_requested(gt_dev):
                logger.info("Exit requested")
                break

            time.sleep(0.05)

        # Handle confirmation
        if confirmed:
            if selection == 1:
                # Reboot confirmed
                logger.info("Rebooting...")
                draw_rebooting_screen(epd)
                time.sleep(1)

                result = subprocess.run(['sudo', 'reboot'], capture_output=True, timeout=5)
                if result.returncode != 0:
                    logger.error(f"Reboot failed: {result.stderr.decode()}")
            else:
                # Cancel confirmed
                logger.info("Reboot cancelled")

        handler.stop()

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise RuntimeError(f"Reboot confirmation failed: {e}") from e


if __name__ == '__main__':
    try:
        epd = epd2in13_V3.EPD()
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        epd.init(epd.PART_UPDATE)

        gt = gt1151.GT1151()
        gt_dev = gt1151.GT_State()
        gt_old = gt1151.GT_State()

        logger.info("Reboot app started")
        draw_reboot_confirm(epd, gt_dev, gt_old, gt)
        logger.info("Reboot app completed")

    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        try:
            epd.sleep()
            epd.module_exit()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
