#!/usr/bin/python3
import medicine_app
import disney_app
import flights_app
import reboot_app
import forbidden_app
import logging
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from TP_lib.epd2in13_V4 import EPD as epd2in13_V4
import sys
import os
import time
import threading
from datetime import datetime
picdir = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__))),
    "python/pic/2in13")
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "python/pic")
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "python/lib")
sys.path.append(libdir)


logging.basicConfig(level=logging.INFO)

# Import apps

# Menu items
APPS = [
    {"name": "Medicine Tracker", "func": "medicine"},
    {"name": "Disney Wait Times", "func": "disney"},
    {"name": "Flights Above Me", "func": "flights"},
    {"name": "Sai Curioso", "func": "forbidden"},
    {"name": "Reboot System", "func": "reboot"}
]

# Global state
current_selection = 0
button_press_start = None
hold_processed = False
launch_requested = False
launch_app_index = -1

# Global dummy touch objects
global_GT_Dev = None
global_GT_Old = None
global_gt = None
exit_requested = False
in_app = False
menu_running = True

# Initialize display
epd = epd2in13_V4()
epd.init(epd.FULL_UPDATE)
epd.Clear(0xFF)

# Button on GPIO 3
pisugar_button = Button(3, pull_up=True, bounce_time=0.1)


def draw_menu(selected_index):
    """Draw text menu with selection highlight"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 10)
        font_item = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 12)
    except BaseException:
        font_title = ImageFont.load_default()
        font_item = ImageFont.load_default()

    # Title
    draw.text((5, 2), "PiZero Menu (Button Control)", font=font_title, fill=0)
    draw.line([(0, 14), (250, 14)], fill=0, width=1)

    # Menu items
    y_start = 16
    item_height = 12

    for i, app in enumerate(APPS):
        y_pos = y_start + (i * item_height)

        if i == selected_index:
            draw.rectangle([(2, y_pos), (248, y_pos + item_height - 1)], fill=0)
            text_color = 255
            prefix = ">"
        else:
            text_color = 0
            prefix = " "

        draw.text((5, y_pos + 1), f"{prefix} {app['name']}", font=font_item, fill=text_color)

    # Instructions
    draw.text((40, 108), "Click: Next  |  Hold 2s: Select", font=font_title, fill=0)

    return img


def button_pressed():
    """Called when button is pressed"""
    global button_press_start, hold_processed, in_app
    button_press_start = time.time()
    hold_processed = False
    logging.info(f"Button pressed (in_app={in_app})")


def button_released():
    """Called when button is released"""
    global button_press_start, current_selection, hold_processed
    global global_GT_Dev, in_app

    if button_press_start is None:
        return

    hold_duration = time.time() - button_press_start
    button_press_start = None

    logging.info(f"Button released after {hold_duration:.2f}s")

    if hold_processed:
        logging.info("Hold already processed, ignoring release")
        return

    # If in app, short press triggers touch event
    if in_app and hold_duration < 2.0:
        if global_GT_Dev:
            global_GT_Dev.TouchpointFlag = 1
            logging.info("Button click in app")
        return

    # Short press in menu: navigate down with PARTIAL refresh (fast!)
    if hold_duration < 2.0 and not in_app:
        current_selection = (current_selection + 1) % len(APPS)
        logging.info(f"Navigate to: {APPS[current_selection]['name']}")

        # Use partial refresh for fast navigation
        image = draw_menu(current_selection)
        epd.displayPartial(epd.getbuffer(image))


def monitor_button_hold():
    """Background thread monitoring button hold"""
    global button_press_start, current_selection, exit_requested, in_app, menu_running, hold_processed
    global global_GT_Dev, launch_requested, launch_app_index

    while menu_running:
        if button_press_start is not None:
            is_pressed = pisugar_button.is_pressed
            hold_duration = time.time() - button_press_start

            # Debug logging every 0.2s during a hold (more frequent)
            if hold_duration >= 0.2 and int(hold_duration * 100) % 20 == 0:
                logging.info(
                    f"HOLD DEBUG: duration={hold_duration:.2f}s, is_pressed={is_pressed}, in_app={in_app}, hold_processed={hold_processed}")

            if is_pressed and hold_duration >= 2.0 and not hold_processed:
                hold_processed = True

                if in_app:
                    # Check if app wants to handle long press internally
                    if global_GT_Dev and getattr(global_GT_Dev, 'handle_long_press_internally', False):
                        # App handles long press - signal via TouchpointFlag with special value
                        global_GT_Dev.TouchpointFlag = 2  # 2 = long press
                        logging.info("LONG PRESS - App handling internally")
                    else:
                        # Default behavior - exit app
                        logging.info("EXIT APP - Hold complete")
                        exit_requested = True
                        if global_GT_Dev:
                            global_GT_Dev.exit_requested = True
                else:
                    logging.info(
                        f"LAUNCH APP - {APPS[current_selection]['name']} (requesting launch)")
                    launch_requested = True
                    launch_app_index = current_selection

                button_press_start = None

        time.sleep(0.1)


def launch_app(app):
    """Launch selected app"""
    global in_app, exit_requested
    global global_GT_Dev, global_GT_Old, global_gt

    in_app = True
    exit_requested = False

    # Full refresh for app launch
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    try:
        # Create dummy touch objects
        class DummyTouch:
            def __init__(self):
                self.X = [0]
                self.Y = [0]
                self.S = [0]
                self.TouchpointFlag = 0
                self.Touch = 0
                self.exit_requested = False  # Signal for app to exit
                self.handle_long_press_internally = False  # If True, app handles long press

        class DummyGT:
            def __init__(self):
                self.INT = 27

            def digital_read(self, pin):
                return 1

            def GT_Scan(self, gt_dev, gt_old):
                pass

            def GT_Init(self):
                pass

        GT_Dev = DummyTouch()
        GT_Old = DummyTouch()
        gt = DummyGT()

        global_GT_Dev = GT_Dev
        global_GT_Old = GT_Old
        global_gt = gt

        # Launch app
        if app["func"] == "medicine":
            medicine_app.run_medicine_app(epd, GT_Dev, GT_Old, gt)
        elif app["func"] == "disney":
            disney_app.run_disney_app(epd, GT_Dev, GT_Old, gt)
        elif app["func"] == "flights":
            flights_app.run_flights_app(epd, GT_Dev, GT_Old, gt)
        elif app["func"] == "forbidden":
            forbidden_app.run_forbidden_app(epd, GT_Dev, GT_Old, gt)
        elif app["func"] == "reboot":
            reboot_app.run_reboot_app(epd, GT_Dev, GT_Old, gt)

    except Exception as e:
        logging.error(f"App error: {e}")

    finally:
        in_app = False
        exit_requested = False

        # Return to menu with full refresh to clear any ghosting
        epd.init(epd.FULL_UPDATE)
        epd.Clear(0xFF)
        image = draw_menu(current_selection)
        epd.displayPartBaseImage(epd.getbuffer(image))
        epd.init(epd.PART_UPDATE)  # Switch to partial for navigation

        logging.info("Returned to menu")


# Main
if __name__ == "__main__":
    try:
        # Start monitor thread
        monitor_thread = threading.Thread(target=monitor_button_hold, daemon=True)
        monitor_thread.start()

        # Set button callbacks
        pisugar_button.when_pressed = button_pressed
        pisugar_button.when_released = button_released

        # Display initial menu with full refresh, then set base for partial updates
        image = draw_menu(current_selection)
        epd.displayPartBaseImage(epd.getbuffer(image))
        epd.init(epd.PART_UPDATE)  # Switch to partial update mode

        logging.info("Button menu started")

        while menu_running:
            # Check if app launch was requested
            if launch_requested:
                launch_requested = False
                app_to_launch = APPS[launch_app_index]
                logging.info(f"Main thread launching: {app_to_launch['name']}")
                launch_app(app_to_launch)

            time.sleep(0.1)

    except KeyboardInterrupt:
        logging.info("Menu interrupted")

    finally:
        menu_running = False
        epd.sleep()
        epd.module_exit()
        logging.info("Menu stopped")
