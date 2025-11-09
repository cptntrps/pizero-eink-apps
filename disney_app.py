#!/usr/bin/python3
"""
Disney Magic Kingdom Wait Times for E-Paper Display (DUAL-INPUT REFACTORED)
Shows current ride wait times with themed backgrounds
Supports both touchscreen and button input modes
Optimized for e-paper refresh limitations with shared utilities
"""
from display.components import MessageBox
from display.text import draw_centered_text, truncate_text_to_width
from display.fonts import get_font_preset
from display import create_input_handler, InputHandler
from shared.app_utils import ConfigLoader, setup_logging, setup_paths
from TP_lib import gt1151, epd2in13_V3
import sys
import os
import time
import json
import subprocess
import random
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Setup paths for imports
sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(__file__))),
        'python/lib'))


# Setup paths and logging
setup_paths()
logger = setup_logging('disney_app')

# Get directories
imagedir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'disney_images')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/pic')

# Cache for background images
BACKGROUND_CACHE = {}


# ============================================================================
# FETCH OPERATIONS
# ============================================================================

def fetch_wait_times():
    """Fetch Disney Magic Kingdom wait times from queue-times.com

    Returns:
        list: List of ride dictionaries with wait times and status
    """
    try:
        result = subprocess.run(
            ['curl', '-s', '-m', '10', 'https://queue-times.com/parks/6/queue_times.json'],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            rides = []
            for land in data['lands']:
                land_name = land['name']
                for ride in land['rides']:
                    ride_info = {
                        'name': ride['name'],
                        'wait_time': ride.get('wait_time'),
                        'is_open': ride['is_open'],
                        'land': land_name
                    }
                    rides.append(ride_info)
            logger.info(f"Fetched {len(rides)} rides from queue-times.com")
            return rides
    except subprocess.TimeoutExpired:
        logger.error("Timeout while fetching wait times")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response: {e}")
    except Exception as e:
        logger.error(f"Failed to fetch wait times: {e}")

    return []


# ============================================================================
# IMAGE HANDLING
# ============================================================================

def load_land_background(land_name):
    """Load and convert land background image to 1-bit with caching

    Args:
        land_name: Name of the land (e.g., 'Adventureland')

    Returns:
        PIL Image: 1-bit monochrome background image
    """
    # Check cache first
    if land_name in BACKGROUND_CACHE:
        return BACKGROUND_CACHE[land_name]

    # Map land names to image files
    land_map = {
        'Adventureland': 'Adventureland.png',
        'Fantasyland': 'Fantasyland.png',
        'Tomorrowland': 'Tomorrowland.png',
        'Frontierland': 'Frontierland.png',
        'Main Street U.S.A.': 'Main Street U.S.A..png',
        'Liberty Square': 'Liberty Square.png'
    }

    try:
        image_path = os.path.join(imagedir, land_map.get(land_name, 'Adventureland.png'))
        if os.path.exists(image_path):
            img = Image.open(image_path).convert('RGBA')
            img = img.resize((250, 122), Image.Resampling.LANCZOS)

            # Convert to 1-bit with dithering
            bw_img = Image.new('1', (250, 122), 255)
            pixels = img.load()
            bw_pixels = bw_img.load()

            for y in range(122):
                for x in range(250):
                    r, g, b, a = pixels[x, y]
                    if a < 128:
                        bw_pixels[x, y] = 255
                    else:
                        brightness = (r + g + b) / 3
                        bw_pixels[x, y] = 255 if brightness > 140 else 0

            BACKGROUND_CACHE[land_name] = bw_img
            logger.debug(f"Cached background for {land_name}")
            return bw_img
    except Exception as e:
        logger.error(f"Failed to load background for {land_name}: {e}")

    # Return blank image if loading fails
    blank = Image.new('1', (250, 122), 255)
    BACKGROUND_CACHE[land_name] = blank
    return blank


def draw_ride_info(ride, input_mode="touch", ride_index=0, total_rides=0):
    """Draw ride wait time with themed background

    Args:
        ride: Ride dictionary with name, wait_time, is_open, land
        input_mode: "touch" or "button" for mode-specific UI
        ride_index: Current ride index (for button mode)
        total_rides: Total number of rides (for button mode)

    Returns:
        PIL Image: Ride info display
    """
    # Load background for the land
    img = load_land_background(ride['land']).copy()
    draw = ImageDraw.Draw(img)

    # Draw semi-transparent overlay for text readability
    draw.rectangle([0, 40, 250, 82], fill=255, outline=0, width=2)

    # Get fonts
    f_name = get_font_preset('subtitle')
    f_time = get_font_preset('display')
    f_small = get_font_preset('small')

    # Ride name - truncate if too long
    name = ride['name']
    dummy_img = Image.new('1', (1, 1), 255)

    # Add selection indicator for button mode
    if input_mode == "button":
        name = f"> {name}"

    bbox = ImageDraw.Draw(dummy_img).textbbox((0, 0), name, font=f_name)
    text_width = bbox[2] - bbox[0]

    if text_width > 230:
        # Truncate with ellipsis
        name = truncate_text_to_width(draw, name, 230, f_name, suffix='...')
        draw.text((10, 45), name, font=f_name, fill=0)
    else:
        # Center text if it fits (but left-align for button mode with indicator)
        if input_mode == "button":
            draw.text((10, 45), name, font=f_name, fill=0)
        else:
            x_pos = (250 - text_width) // 2
            draw.text((x_pos, 45), name, font=f_name, fill=0)

    # Wait time or status
    wait_text = f"{ride['wait_time']} min" if ride['is_open'] else "CLOSED"
    bbox = ImageDraw.Draw(dummy_img).textbbox((0, 0), wait_text, font=f_time)
    w = bbox[2] - bbox[0]
    draw.text(((250 - w) // 2, 62), wait_text, font=f_time, fill=0)

    # Land name at top
    draw.text((5, 5), ride['land'], font=f_small, fill=0)

    # Mode-specific instructions and indicators at bottom
    if input_mode == "button":
        # Button mode: Show instructions and position
        draw.text((5, 110), "Press:Next | Hold:Exit", font=f_small, fill=0)

        # Position indicator (right-aligned)
        position_text = f"{ride_index + 1}/{total_rides}"
        bbox = ImageDraw.Draw(dummy_img).textbbox((0, 0), position_text, font=f_small)
        pos_width = bbox[2] - bbox[0]
        draw.text((245 - pos_width, 110), position_text, font=f_small, fill=0)
    else:
        # Touch mode: Show touch instruction
        draw.text((180, 110), "Tap=Exit", font=f_small, fill=0)

    return img


# ============================================================================
# DISPLAY OPERATIONS
# ============================================================================

def show_loading_screen(epd):
    """Show loading message on display

    Args:
        epd: Display driver object
    """
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)
    f = get_font_preset('body')
    draw.text((30, 50), "Loading Disney wait times...", font=f, fill=0)
    epd.displayPartial(epd.getbuffer(img))


def show_error_screen(epd, message):
    """Show error message on display

    Args:
        epd: Display driver object
        message: Error message to display
    """
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)
    f = get_font_preset('body')

    draw.text((20, 40), "Unable to fetch wait times", font=f, fill=0)
    draw.text((60, 60), message, font=f, fill=0)
    epd.displayPartial(epd.getbuffer(img))


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def run_disney_app(epd, gt_dev=None, gt_old=None, gt=None):
    """Disney wait times app with dual-input support

    Args:
        epd: E-paper display driver
        gt_dev: Touch device state (optional, for touch mode)
        gt_old: Previous touch state (optional, for touch mode)
        gt: Touch driver interface (optional, for touch mode)
    """
    # Create input handler (auto-detects touch vs button)
    input_handler = create_input_handler(
        gt=gt,
        gt_dev=gt_dev,
        gt_old=gt_old
    )

    input_mode = input_handler.mode
    logger.info(f"Disney app started in {input_mode} mode")

    # State for app control
    exit_requested = [False]
    next_ride_requested = [False]

    # Setup input callbacks
    def on_short_press():
        """Handle short press (button mode) or tap (touch mode)"""
        if input_mode == "button":
            # Button mode: Next ride
            logger.info("SHORT PRESS - Next ride")
            next_ride_requested[0] = True
        else:
            # Touch mode: Exit
            logger.info("TAP - Exit requested")
            exit_requested[0] = True

    def on_long_press():
        """Handle long press - Exit in button mode"""
        logger.info("LONG PRESS - Exit requested")
        exit_requested[0] = True

    def on_touch():
        """Handle generic touch - Exit in touch mode"""
        if input_mode == "touch":
            logger.info("TOUCH - Exit requested")
            exit_requested[0] = True

    # Register callbacks
    input_handler.on_short_press = on_short_press
    input_handler.on_long_press = on_long_press
    input_handler.on_touch = on_touch

    try:
        # Show loading screen
        show_loading_screen(epd)

        # Fetch wait times
        rides = fetch_wait_times()

        if not rides:
            logger.error("No wait times fetched")
            show_error_screen(epd, "Check internet connection")
            time.sleep(3)
            return

        logger.info(f"Displaying {len(rides)} rides")
        random.shuffle(rides)

        # Pre-cache backgrounds for all lands
        logger.debug("Pre-loading backgrounds...")
        unique_lands = set(ride['land'] for ride in rides)
        for land in unique_lands:
            load_land_background(land)

        # Configuration
        disney_config = ConfigLoader.get_section('disney', {})
        auto_advance_interval = disney_config.get('update_interval', 10)

        # Display loop
        ride_index = 0
        last_auto_advance = time.time()

        # Start input monitoring
        input_handler.start()

        # Initial display
        image = draw_ride_info(
            rides[ride_index],
            input_mode=input_mode,
            ride_index=ride_index,
            total_rides=len(rides)
        )
        epd.displayPartial(epd.getbuffer(image))

        # Wait for display to settle
        time.sleep(0.5)

        # Main loop
        while input_handler.is_active:
            # Check for exit
            if exit_requested[0]:
                logger.info("Exiting Disney app")
                break

            current_time = time.time()

            # Handle manual next ride (button mode)
            if next_ride_requested[0]:
                next_ride_requested[0] = False
                ride_index = (ride_index + 1) % len(rides)
                current_ride = rides[ride_index]

                # Re-fetch every 20 rides
                if ride_index % 20 == 0:
                    logger.debug("Re-fetching wait times...")
                    new_rides = fetch_wait_times()
                    if new_rides:
                        rides = new_rides
                        random.shuffle(rides)
                        BACKGROUND_CACHE.clear()
                        unique_lands = set(ride['land'] for ride in rides)
                        for land in unique_lands:
                            load_land_background(land)

                image = draw_ride_info(
                    current_ride,
                    input_mode=input_mode,
                    ride_index=ride_index,
                    total_rides=len(rides)
                )
                epd.displayPartial(epd.getbuffer(image))
                last_auto_advance = current_time

            # Auto-advance to next ride (touch mode or button mode after timeout)
            elif current_time - last_auto_advance >= auto_advance_interval:
                ride_index = (ride_index + 1) % len(rides)
                current_ride = rides[ride_index]

                # Re-fetch every 20 rides
                if ride_index % 20 == 0:
                    logger.debug("Re-fetching wait times...")
                    new_rides = fetch_wait_times()
                    if new_rides:
                        rides = new_rides
                        random.shuffle(rides)
                        BACKGROUND_CACHE.clear()
                        unique_lands = set(ride['land'] for ride in rides)
                        for land in unique_lands:
                            load_land_background(land)

                image = draw_ride_info(
                    current_ride,
                    input_mode=input_mode,
                    ride_index=ride_index,
                    total_rides=len(rides)
                )
                epd.displayPartial(epd.getbuffer(image))
                last_auto_advance = current_time

            # Small sleep to avoid busy waiting
            time.sleep(0.1)

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        show_error_screen(epd, f"Error: {str(e)[:30]}")
        time.sleep(3)

    finally:
        # Cleanup
        BACKGROUND_CACHE.clear()
        input_handler.stop()
        logger.info("Disney app cleanup complete")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        # Initialize display
        epd = epd2in13_V3.EPD()
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        epd.init(epd.PART_UPDATE)

        # Try to initialize touch (may not be available)
        gt = None
        gt_dev = None
        gt_old = None

        try:
            gt = gt1151.gt1151()
            gt_dev = gt1151.gt1151_dev()
            gt_old = gt1151.gt1151_dev()
            logger.info("Touch hardware detected")
        except Exception as e:
            logger.info(f"Touch not available, using button mode: {e}")

        # Run application
        run_disney_app(epd, gt_dev, gt_old, gt)

        # Cleanup display
        epd.sleep()
        epd.module_exit()

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
