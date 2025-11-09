#!/usr/bin/python3
"""
Medicine Tracker App - Dual-Input Refactored Version
=====================================================

E-ink display app for tracking medicine schedule and adherence.

Features:
- Dual-input support: Touchscreen OR Button control
- Skip functionality with reason tracking
- Enhanced adherence display (Taken / Skipped / Total)
- Mode-specific UI and instructions
- InputHandler abstraction for hardware flexibility

Input Modes:
------------

TOUCH MODE:
- Tap medicine to select
- Tap [Take] button to mark taken
- Tap [Skip] button to skip with reason selector
- Swipe to scroll list

BUTTON MODE:
- SHORT PRESS: Next medicine in list
- LONG PRESS: Show action menu (Take / Skip / Exit)
  - In menu: SHORT=toggle option, LONG=confirm
- Skip shows reason selector with same pattern

Architecture:
- Uses display.create_input_handler() for hardware abstraction
- Supports both GT touch objects and GPIO button input
- State machine for UI flow (view → action menu → skip reasons)
"""

from shared.app_utils import ConfigLoader, get_font, install_signal_handlers
from db.medicine_db import MedicineDatabase
from PIL import Image, ImageDraw, ImageFont
from TP_lib import gt1151, epd2in13_V3
from display import create_input_handler, InputHandler
import sys
import os
import time
from datetime import datetime, date
import logging
import threading

# Add library paths
picdir = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__))),
    'python/pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/lib')
sys.path.append(libdir)

# Add project root to path for local imports
project_root = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = ConfigLoader()
medicine_config = config.get_section('medicine')
UPDATE_INTERVAL = medicine_config.get('update_interval', 60)
REMINDER_WINDOW = medicine_config.get('reminder_window', 30)

# Initialize database
db = MedicineDatabase()

# Font cache (using shared utility)
FONT_DIR = fontdir

# Skip reasons (predefined options)
SKIP_REASONS = [
    "Forgot",
    "Side effects",
    "Out of stock",
    "Doctor advised",
    "Other"
]

# UI States for state machine
UI_STATE_REMINDER = "reminder"      # Main reminder view
UI_STATE_SCHEDULE = "schedule"      # Full schedule view
UI_STATE_ACTION_MENU = "action_menu"  # Take/Skip/Exit menu
UI_STATE_SKIP_REASON = "skip_reason"  # Skip reason selector
UI_STATE_CONFIRMATION = "confirmation"  # Confirmation screen


# ============================================================================
# DATABASE QUERY FUNCTIONS
# ============================================================================

def get_pending_medicines():
    """Get list of medicines that are due now using database"""
    try:
        pending = db.get_pending_medicines(check_date=date.today(), check_time=datetime.now())
        return pending
    except Exception as e:
        logger.error(f"Failed to get pending medicines: {e}")
        return []


def mark_medicines_taken(medicines):
    """Mark a list of medicines as taken using database"""
    try:
        results = []
        for med in medicines:
            result = db.mark_medicine_taken(
                medicine_id=med['id'],
                time_window=med.get('time_window'),
                taken_date=date.today(),
                timestamp=datetime.now()
            )
            results.append(result)

            # Log low stock warnings
            if result.get('low_stock'):
                logger.warning(
                    f"Low stock alert: {med['name']} - {result['pills_remaining']} pills remaining")

        return True
    except Exception as e:
        logger.error(f"Failed to mark medicines taken: {e}")
        return False


def skip_medicine_with_reason(medicine, reason):
    """Mark medicine as skipped with reason using database

    Args:
        medicine: Medicine dict
        reason: Skip reason string

    Returns:
        bool: True if successful
    """
    try:
        result = db.skip_medicine(
            medicine_id=medicine['id'],
            time_window=medicine.get('time_window'),
            skip_date=date.today(),
            skip_timestamp=datetime.now(),
            skip_reason=reason
        )

        logger.info(f"Skipped {medicine['name']} - reason: {reason}")
        return result.get('success', False)

    except Exception as e:
        logger.error(f"Failed to skip medicine: {e}")
        return False


def get_today_stats():
    """Get today's medicine statistics from database

    Returns:
        tuple: (taken, skipped, total) counts
    """
    try:
        taken, skipped, total = db.get_today_stats(check_date=date.today())
        return taken, skipped, total
    except Exception as e:
        logger.error(f"Failed to get today stats: {e}")
        return 0, 0, 0


def get_all_medicines_for_today():
    """Get all active medicines scheduled for today"""
    try:
        all_medicines = db.get_all_medicines(include_inactive=False)
        today_day = datetime.now().strftime("%a").lower()

        # Filter for today
        today_medicines = [m for m in all_medicines if today_day in m.get('days', [])]
        return today_medicines
    except Exception as e:
        logger.error(f"Failed to get medicines: {e}")
        return []


def get_tracking_for_today():
    """Get tracking data for today"""
    try:
        today_str = date.today().strftime('%Y-%m-%d')
        tracking = db.get_tracking_history(
            start_date=date.today(),
            end_date=date.today()
        )

        # Convert to dict keyed by medicine_id_timewindow
        tracking_dict = {}
        for entry in tracking:
            key = f"{entry['medicine_id']}_{entry['time_window']}"
            tracking_dict[key] = entry

        return tracking_dict
    except Exception as e:
        logger.error(f"Failed to get tracking: {e}")
        return {}


def get_data_timestamp():
    """Get the last updated timestamp from database"""
    try:
        return db.get_last_updated()
    except Exception as e:
        logger.error(f"Failed to get timestamp: {e}")
        return datetime.now().isoformat()


# ============================================================================
# ICON DRAWING FUNCTIONS
# ============================================================================

def draw_pill_icon(draw, x, y, size=10):
    """Draw a simple pill icon"""
    # Capsule shape
    draw.ellipse([x, y, x + size, y + size], outline=0, width=2)
    draw.line([x + size // 4, y, x + size // 4, y + size], fill=0, width=1)


def draw_food_icon(draw, x, y, size=8):
    """Draw a simple fork/knife icon for 'with food'"""
    # Fork
    draw.line([x, y, x, y + size], fill=0, width=1)
    draw.line([x - 1, y, x - 1, y + size // 2], fill=0, width=1)
    draw.line([x + 1, y, x + 1, y + size // 2], fill=0, width=1)


def draw_selection_indicator(draw, x, y, width, height):
    """Draw selection indicator for button mode

    Args:
        draw: ImageDraw object
        x, y: Top-left corner
        width, height: Dimensions
    """
    # Draw rectangle around selected item
    draw.rectangle([x, y, x + width, y + height], outline=0, width=2)

    # Draw arrow indicator
    arrow_x = x - 10
    arrow_y = y + height // 2
    draw.polygon([
        (arrow_x, arrow_y),
        (arrow_x + 5, arrow_y - 3),
        (arrow_x + 5, arrow_y + 3)
    ], fill=0)


# ============================================================================
# MAIN REMINDER VIEW
# ============================================================================

def draw_current_reminder(pending_meds, current_index=0, input_mode="button", selected_index=0):
    """Draw current medicine reminder (supports both input modes)

    Args:
        pending_meds: List of pending medicines
        current_index: Index of currently displayed medicine
        input_mode: "button" or "touch"
        selected_index: Index of selected medicine (for button mode)
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = get_font('Roboto-Bold', 12)
    f_med = get_font('Roboto-Bold', 16)
    f_dose = get_font('Roboto-Regular', 12)
    f_small = get_font('Roboto-Regular', 10)
    f_tiny = get_font('Roboto-Regular', 8)

    # Title bar
    now = datetime.now().strftime("%H:%M")
    draw.text((5, 2), "TIME TO TAKE MEDICINE", font=f_title, fill=0)
    draw.text((200, 2), now, font=f_title, fill=0)
    draw.line([(0, 18), (250, 18)], fill=0, width=1)

    if not pending_meds:
        # No pending medicines
        draw.text((40, 50), "All caught up!", font=f_med, fill=0)
        draw.text((60, 70), "No medicines due now", font=f_small, fill=0)

        # Instructions based on mode
        draw.line([(0, 100), (250, 100)], fill=0, width=1)
        if input_mode == "button":
            instruction = "LONG PRESS: Exit"
        else:
            instruction = "Hold to exit"
        draw.text((10, 106), instruction, font=f_small, fill=0)

    else:
        # Show current medicine
        med = pending_meds[current_index % len(pending_meds)]
        y_pos = 30

        # Pill icon
        draw_pill_icon(draw, 10, y_pos + 5, 15)

        # Medicine name
        draw.text((35, y_pos), med["name"], font=f_med, fill=0)

        # Dosage
        draw.text((35, y_pos + 20), med["dosage"], font=f_dose, fill=0)

        # With food indicator
        if med.get("with_food", False):
            draw_food_icon(draw, 10, y_pos + 25, 10)
            draw.text((25, y_pos + 22), "with food", font=f_small, fill=0)

        # Pills remaining and low stock warning
        pills_remaining = med.get("pills_remaining", 0)
        low_threshold = med.get("low_stock_threshold", 10)

        y_info = y_pos + 40
        if med.get("notes"):
            notes_text = med["notes"][:25]  # Truncate if too long
            draw.text((10, y_info), notes_text, font=f_small, fill=0)
            y_info += 12

        # Show pill count
        pill_text = f"Pills left: {pills_remaining}"
        if pills_remaining <= low_threshold:
            pill_text += " - REORDER!"
        draw.text((10, y_info), pill_text, font=f_small, fill=0)

        # If multiple, show count
        if len(pending_meds) > 1:
            count_text = f"({current_index + 1}/{len(pending_meds)})"
            draw.text((200, y_pos + 40), count_text, font=f_small, fill=0)

    # Bottom instructions - MODE SPECIFIC
    draw.line([(0, 100), (250, 100)], fill=0, width=1)

    if input_mode == "button":
        # Button mode instructions
        if pending_meds:
            if len(pending_meds) > 1:
                instruction = "SHORT: Next | LONG: Action Menu"
            else:
                instruction = "LONG PRESS: Action Menu"
        else:
            instruction = "LONG PRESS: Exit"
    else:
        # Touch mode instructions
        if pending_meds:
            instruction = "Tap medicine | Use buttons below"
        else:
            instruction = "Hold to exit"

    draw.text((10, 106), instruction, font=f_small, fill=0)

    return img


# ============================================================================
# ACTION MENU (Button Mode)
# ============================================================================

def draw_action_menu(medicine, selected_option=0):
    """Draw action menu for selected medicine (button mode)

    Args:
        medicine: Medicine dict
        selected_option: Currently selected option (0=Take, 1=Skip, 2=Exit)
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = get_font('Roboto-Bold', 12)
    f_option = get_font('Roboto-Regular', 14)
    f_small = get_font('Roboto-Regular', 10)

    # Title
    draw.text((5, 2), "ACTION MENU", font=f_title, fill=0)
    draw.line([(0, 18), (250, 18)], fill=0, width=1)

    # Medicine name
    med_name = medicine["name"][:25]  # Truncate if needed
    draw.text((10, 25), f"Medicine: {med_name}", font=f_small, fill=0)

    # Menu options
    options = ["Take Medicine", "Skip (with reason)", "Cancel"]
    y_start = 45
    option_height = 20

    for i, option in enumerate(options):
        y = y_start + (i * option_height)

        # Draw selection indicator for current option
        if i == selected_option:
            draw_selection_indicator(draw, 8, y - 2, 234, option_height - 4)

        # Draw option text
        draw.text((20, y), option, font=f_option, fill=0)

    # Bottom instructions
    draw.line([(0, 100), (250, 100)], fill=0, width=1)
    draw.text((10, 106), "SHORT: Next | LONG: Confirm", font=f_small, fill=0)

    return img


# ============================================================================
# SKIP REASON SELECTOR
# ============================================================================

def draw_skip_reason_selector(medicine, selected_reason=0):
    """Draw skip reason selector

    Args:
        medicine: Medicine dict
        selected_reason: Index of selected reason
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = get_font('Roboto-Bold', 12)
    f_option = get_font('Roboto-Regular', 11)
    f_small = get_font('Roboto-Regular', 9)

    # Title
    draw.text((5, 2), "SKIP REASON", font=f_title, fill=0)
    draw.line([(0, 18), (250, 18)], fill=0, width=1)

    # Medicine name
    med_name = medicine["name"][:25]
    draw.text((10, 22), f"Skipping: {med_name}", font=f_small, fill=0)

    # Reason options (compact layout)
    y_start = 38
    option_height = 13

    for i, reason in enumerate(SKIP_REASONS):
        y = y_start + (i * option_height)

        # Draw selection indicator
        if i == selected_reason:
            # Highlight selected reason
            draw.rectangle([8, y - 2, 242, y + option_height - 4], outline=0, width=2)
            # Arrow
            arrow_x = 10
            arrow_y = y + option_height // 2
            draw.text((arrow_x, y - 2), ">", font=f_option, fill=0)

        # Draw reason text
        draw.text((25, y), reason, font=f_option, fill=0)

    # Bottom instructions
    draw.line([(0, 100), (250, 100)], fill=0, width=1)
    draw.text((10, 106), "SHORT: Next | LONG: Confirm", font=f_small, fill=0)

    return img


# ============================================================================
# SCHEDULE VIEW
# ============================================================================

def draw_schedule_view():
    """Draw today's full schedule with updated adherence stats"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = get_font('Roboto-Bold', 12)
    f_item = get_font('Roboto-Regular', 11)
    f_small = get_font('Roboto-Regular', 9)

    today = datetime.now().strftime("%b %d")
    current_day = datetime.now().strftime("%a").lower()

    # Title
    draw.text((5, 2), f"Today's Medicines - {today}", font=f_title, fill=0)
    draw.line([(0, 16), (250, 16)], fill=0, width=1)

    # Get medicines and tracking for today
    medicines = get_all_medicines_for_today()
    tracking = get_tracking_for_today()

    # Group medicines by time window
    windows = {}
    for med in medicines:
        window = med.get("time_window", "morning")
        if window not in windows:
            windows[window] = []
        windows[window].append(med)

    # Draw schedule
    y_pos = 20

    for window in ["morning", "afternoon", "evening", "night"]:
        if window not in windows:
            continue

        meds = windows[window]
        window_text = window.capitalize()

        # Window header
        draw.text((5, y_pos), window_text, font=f_item, fill=0)
        y_pos += 14

        for med in meds:
            # Check if taken or skipped
            tracking_key = f"{med['id']}_{window}"
            entry = tracking.get(tracking_key, {})
            taken = entry.get('taken', False)
            skipped = entry.get('skipped', False)

            # Checkbox with status
            if taken:
                checkbox = "[✓]"  # Taken
            elif skipped:
                checkbox = "[S]"  # Skipped
            else:
                checkbox = "[ ]"  # Not taken

            med_text = f"{checkbox} {med['name']} ({med['dosage']})"
            draw.text((15, y_pos), med_text, font=f_small, fill=0)
            y_pos += 11

    # Stats at bottom - UPDATED to show Taken/Skipped/Total
    taken, skipped, total = get_today_stats()
    if total > 0:
        draw.line([(0, 95), (250, 95)], fill=0, width=1)

        # Calculate percentages
        taken_pct = int((taken / total) * 100)
        skipped_pct = int((skipped / total) * 100)

        # Display stats
        stats_text = f"Today: {taken} taken, {skipped} skipped / {total} total"
        draw.text((10, 100), stats_text, font=f_small, fill=0)
        draw.text((30, 110), f"Adherence: {taken_pct}%", font=f_small, fill=0)

    return img


# ============================================================================
# CONFIRMATION SCREENS
# ============================================================================

def draw_confirmation_screen(medicines_taken, count, action="taken"):
    """Draw confirmation screen after action

    Args:
        medicines_taken: List of medicines
        count: Number of medicines
        action: "taken" or "skipped"
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_big = get_font('Roboto-Bold', 20)
    f_medium = get_font('Roboto-Regular', 12)
    f_small = get_font('Roboto-Regular', 10)

    # Big checkmark or skip symbol
    if action == "taken":
        draw.text((90, 15), "✓", font=f_big, fill=0)
        confirmation_text = "Marked as Taken!"
    else:
        draw.text((90, 15), "S", font=f_big, fill=0)
        confirmation_text = "Marked as Skipped!"

    # Confirmation text
    draw.text((60, 45), confirmation_text, font=f_medium, fill=0)

    # List medicines
    y_pos = 65
    for i, med in enumerate(medicines_taken[:3]):  # Show max 3
        med_text = f"• {med['name']} ({med['dosage']})"
        draw.text((30, y_pos), med_text, font=f_small, fill=0)
        y_pos += 12

    if count > 3:
        draw.text((50, y_pos), f"+ {count - 3} more...", font=f_small, fill=0)

    # Timestamp
    now = datetime.now().strftime("%H:%M")
    draw.text((80, 105), f"At {now}", font=f_small, fill=0)

    return img


# ============================================================================
# MAIN APPLICATION LOGIC
# ============================================================================

def run_medicine_app(epd, gt_dev, gt_old, gt):
    """Medicine tracking app with dual-input support

    Args:
        epd: E-paper display object
        gt_dev: Touch device state (for touch mode) or dummy object
        gt_old: Previous touch state (for touch mode) or dummy object
        gt: Touch driver (for touch mode) or dummy object
    """

    # ========================================================================
    # INITIALIZE INPUT HANDLER
    # ========================================================================

    # Create input handler using factory (auto-detects touch vs button)
    # If GT objects are real touch hardware, uses TouchInputHandler
    # Otherwise uses ButtonInputHandler (GPIO 3)
    input_handler = create_input_handler(
        gt=gt,
        gt_dev=gt_dev,
        gt_old=gt_old
    )

    input_mode = input_handler.mode  # "touch" or "button"
    logger.info(f"Medicine app starting in {input_mode.upper()} mode")

    # ========================================================================
    # STATE VARIABLES
    # ========================================================================

    # UI state machine
    ui_state = UI_STATE_REMINDER

    # Medicine tracking
    pending = []
    current_index = 0  # Which medicine we're viewing
    selected_index = 0  # Which medicine is selected (button mode)

    # Menu state
    menu_selection = 0  # For action menu (0=Take, 1=Skip, 2=Exit)
    reason_selection = 0  # For skip reason selector

    # Display update tracking
    last_update = 0
    last_timestamp_check = 0
    last_known_timestamp = get_data_timestamp()

    # Refresh intervals
    TIMESTAMP_CHECK_INTERVAL = 5  # Check for external changes every 5s

    # Exit flag
    exit_requested = [False]

    # ========================================================================
    # INPUT EVENT HANDLERS
    # ========================================================================

    def on_short_press():
        """Handle SHORT PRESS events (button mode)"""
        nonlocal ui_state, current_index, selected_index, menu_selection, reason_selection
        nonlocal pending, last_update

        logger.info(f"SHORT PRESS - State: {ui_state}")

        if ui_state == UI_STATE_REMINDER:
            # Cycle to next medicine
            pending = get_pending_medicines()
            if pending and len(pending) > 1:
                current_index = (current_index + 1) % len(pending)
                selected_index = current_index
                logger.info(f"Cycled to medicine {current_index + 1}/{len(pending)}")

                image = draw_current_reminder(
                    pending, current_index, input_mode, selected_index
                )
                epd.displayPartial(epd.getbuffer(image))
                last_update = time.time()

        elif ui_state == UI_STATE_ACTION_MENU:
            # Cycle through menu options
            menu_selection = (menu_selection + 1) % 3  # 3 options: Take/Skip/Exit
            logger.info(f"Menu selection: {menu_selection}")

            image = draw_action_menu(pending[selected_index], menu_selection)
            epd.displayPartial(epd.getbuffer(image))

        elif ui_state == UI_STATE_SKIP_REASON:
            # Cycle through skip reasons
            reason_selection = (reason_selection + 1) % len(SKIP_REASONS)
            logger.info(f"Reason selection: {SKIP_REASONS[reason_selection]}")

            image = draw_skip_reason_selector(pending[selected_index], reason_selection)
            epd.displayPartial(epd.getbuffer(image))


    def on_long_press():
        """Handle LONG PRESS events (button mode)"""
        nonlocal ui_state, current_index, selected_index, menu_selection, reason_selection
        nonlocal pending, last_update, last_known_timestamp, exit_requested

        logger.info(f"LONG PRESS - State: {ui_state}")

        if ui_state == UI_STATE_REMINDER:
            # Open action menu if medicines pending
            pending = get_pending_medicines()

            if pending:
                ui_state = UI_STATE_ACTION_MENU
                menu_selection = 0
                logger.info("Opening action menu")

                image = draw_action_menu(pending[selected_index], menu_selection)
                epd.displayPartial(epd.getbuffer(image))
            else:
                # No pending medicines, exit
                logger.info("Exit requested (no pending medicines)")
                exit_requested[0] = True

        elif ui_state == UI_STATE_ACTION_MENU:
            # Confirm menu selection
            if menu_selection == 0:
                # Take medicine
                logger.info("Taking medicine")
                handle_take_medicine()

            elif menu_selection == 1:
                # Skip medicine - go to reason selector
                logger.info("Opening skip reason selector")
                ui_state = UI_STATE_SKIP_REASON
                reason_selection = 0

                image = draw_skip_reason_selector(pending[selected_index], reason_selection)
                epd.displayPartial(epd.getbuffer(image))

            elif menu_selection == 2:
                # Cancel - back to reminder
                logger.info("Cancelled action menu")
                ui_state = UI_STATE_REMINDER

                image = draw_current_reminder(
                    pending, current_index, input_mode, selected_index
                )
                epd.displayPartial(epd.getbuffer(image))

        elif ui_state == UI_STATE_SKIP_REASON:
            # Confirm skip with reason
            logger.info(f"Confirming skip with reason: {SKIP_REASONS[reason_selection]}")
            handle_skip_medicine(SKIP_REASONS[reason_selection])


    def handle_take_medicine():
        """Handle taking the selected medicine"""
        nonlocal ui_state, pending, current_index, selected_index, last_update, last_known_timestamp

        selected_med = [pending[selected_index]]
        logger.info(f"Marking {selected_med[0]['name']} as taken")

        if mark_medicines_taken(selected_med):
            # Show confirmation screen
            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)

            image = draw_confirmation_screen(selected_med, 1, "taken")
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)

            time.sleep(2)  # Show confirmation for 2 seconds

            # Refresh display and return to reminder
            ui_state = UI_STATE_REMINDER
            last_known_timestamp = get_data_timestamp()
            pending = get_pending_medicines()
            current_index = 0
            selected_index = 0

            if pending:
                image = draw_current_reminder(pending, current_index, input_mode, selected_index)
            else:
                image = draw_schedule_view()
                ui_state = UI_STATE_SCHEDULE

            epd.displayPartial(epd.getbuffer(image))
            last_update = time.time()


    def handle_skip_medicine(reason):
        """Handle skipping the selected medicine with reason"""
        nonlocal ui_state, pending, current_index, selected_index, last_update, last_known_timestamp

        selected_med = pending[selected_index]
        logger.info(f"Skipping {selected_med['name']} - reason: {reason}")

        if skip_medicine_with_reason(selected_med, reason):
            # Show confirmation screen
            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)

            image = draw_confirmation_screen([selected_med], 1, "skipped")
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)

            time.sleep(2)  # Show confirmation for 2 seconds

            # Refresh display and return to reminder
            ui_state = UI_STATE_REMINDER
            last_known_timestamp = get_data_timestamp()
            pending = get_pending_medicines()
            current_index = 0
            selected_index = 0

            if pending:
                image = draw_current_reminder(pending, current_index, input_mode, selected_index)
            else:
                image = draw_schedule_view()
                ui_state = UI_STATE_SCHEDULE

            epd.displayPartial(epd.getbuffer(image))
            last_update = time.time()


    def on_touch():
        """Handle generic touch events (touch mode)"""
        logger.debug("Touch detected")


    def on_coordinates(x, y):
        """Handle coordinate touch events (touch mode)

        Touch mode UI:
        - Tap medicine to select
        - Tap [Take] button to mark taken
        - Tap [Skip] button to skip with reason
        """
        nonlocal ui_state, pending, current_index, selected_index, last_update

        logger.info(f"Touch at ({x}, {y}) - State: {ui_state}")

        if ui_state == UI_STATE_REMINDER:
            pending = get_pending_medicines()

            if not pending:
                return

            # Define touch zones (approximate for 250x122 display)
            # Medicine area: y=30-90
            # Take button: x=10-120, y=100-120
            # Skip button: x=130-240, y=100-120

            if 30 <= y <= 90:
                # Tapped on medicine - select it
                # For now, just toggle to next if multiple
                if len(pending) > 1:
                    current_index = (current_index + 1) % len(pending)
                    selected_index = current_index

                    image = draw_current_reminder(
                        pending, current_index, input_mode, selected_index
                    )
                    epd.displayPartial(epd.getbuffer(image))

            elif y >= 100:
                # Tapped in button area
                if x < 125:
                    # Take button
                    logger.info("Take button tapped")
                    handle_take_medicine()
                else:
                    # Skip button - go to reason selector
                    logger.info("Skip button tapped")
                    ui_state = UI_STATE_SKIP_REASON
                    reason_selection = 0

                    image = draw_skip_reason_selector(pending[selected_index], reason_selection)
                    epd.displayPartial(epd.getbuffer(image))

        elif ui_state == UI_STATE_SKIP_REASON:
            # Touch on reason selector
            # Reasons are at y=38, 51, 64, 77, 90 (13px spacing)
            reason_index = (y - 38) // 13

            if 0 <= reason_index < len(SKIP_REASONS):
                reason = SKIP_REASONS[reason_index]
                logger.info(f"Selected reason: {reason}")
                handle_skip_medicine(reason)

    # ========================================================================
    # REGISTER CALLBACKS
    # ========================================================================

    input_handler.on_short_press = on_short_press
    input_handler.on_long_press = on_long_press
    input_handler.on_touch = on_touch
    input_handler.on_coordinates = on_coordinates

    # ========================================================================
    # START INPUT HANDLER
    # ========================================================================

    input_handler.start()
    logger.info("Input handler started")

    # ========================================================================
    # INITIAL DISPLAY
    # ========================================================================

    last_known_timestamp = get_data_timestamp()
    pending = get_pending_medicines()

    if pending:
        image = draw_current_reminder(pending, current_index, input_mode, selected_index)
    else:
        image = draw_schedule_view()
        ui_state = UI_STATE_SCHEDULE

    epd.displayPartial(epd.getbuffer(image))
    last_update = time.time()

    logger.info("Medicine app display initialized")

    # ========================================================================
    # MAIN EVENT LOOP
    # ========================================================================

    try:
        while not exit_requested[0]:
            current_time = time.time()

            # Check for external data changes (push refresh)
            if current_time - last_timestamp_check > TIMESTAMP_CHECK_INTERVAL:
                current_timestamp = get_data_timestamp()

                if current_timestamp != last_known_timestamp:
                    logger.info(
                        f"Data changed externally (timestamp: {current_timestamp}), refreshing display")
                    last_known_timestamp = current_timestamp
                    pending = get_pending_medicines()
                    current_index = 0
                    selected_index = 0

                    if ui_state == UI_STATE_REMINDER:
                        if pending:
                            image = draw_current_reminder(
                                pending, current_index, input_mode, selected_index
                            )
                        else:
                            image = draw_schedule_view()
                            ui_state = UI_STATE_SCHEDULE

                        epd.displayPartial(epd.getbuffer(image))
                        last_update = current_time

                last_timestamp_check = current_time

            # Auto-refresh data periodically (only in reminder/schedule states)
            if ui_state in [UI_STATE_REMINDER, UI_STATE_SCHEDULE]:
                if current_time - last_update > UPDATE_INTERVAL:
                    logger.info("Auto-refreshing medicine data")
                    pending = get_pending_medicines()

                    if pending and ui_state == UI_STATE_REMINDER:
                        image = draw_current_reminder(
                            pending, current_index, input_mode, selected_index
                        )
                    else:
                        image = draw_schedule_view()
                        ui_state = UI_STATE_SCHEDULE

                    epd.displayPartial(epd.getbuffer(image))
                    last_update = current_time

            # Check for exit via gt_dev flag (legacy compatibility)
            if hasattr(gt_dev, "exit_requested") and gt_dev.exit_requested:
                logger.info("Exit requested by menu")
                exit_requested[0] = True
                break

            time.sleep(0.1)

    finally:
        # ====================================================================
        # CLEANUP
        # ====================================================================

        logger.info("Stopping input handler...")
        input_handler.stop()
        logger.info("Medicine app stopped")


# ============================================================================
# SIGNAL HANDLER & CLEANUP
# ============================================================================

def cleanup():
    """Cleanup database connection on exit"""
    logger.info("Cleaning up medicine app...")
    try:
        db.close()
    except BaseException:
        pass


# Install signal handlers for graceful shutdown
install_signal_handlers(cleanup)
