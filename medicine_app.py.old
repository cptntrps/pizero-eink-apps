#!/usr/bin/python3
import sys, os, time, json
from datetime import datetime
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/lib')
sys.path.append(libdir)

from TP_lib import gt1151, epd2in13_V3
from PIL import Image, ImageDraw, ImageFont
import logging, threading

logging.basicConfig(level=logging.INFO)

# Load configuration
CONFIG_FILE = "/home/pizero2w/pizero_apps/config.json"
MEDICINE_DATA_FILE = "/home/pizero2w/pizero_apps/medicine_data.json"

try:
    with open(CONFIG_FILE, "r") as f:
        CONFIG = json.load(f)
    MEDICINE_CONFIG = CONFIG.get("medicine", {})
except:
    MEDICINE_CONFIG = {}

UPDATE_INTERVAL = MEDICINE_CONFIG.get("update_interval", 60)
REMINDER_WINDOW = MEDICINE_CONFIG.get("reminder_window", 30)

def load_medicine_data():
    """Load medicine data from JSON file"""
    try:
        with open(MEDICINE_DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"medicines": [], "tracking": {}, "time_windows": {}}

def save_medicine_data(data):
    """Save medicine data to JSON file"""
    try:
        # Add last_updated timestamp
        from datetime import datetime
        data["last_updated"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        with open(MEDICINE_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Failed to save medicine data: {e}")
        return False

def get_data_timestamp(data):
    """Get the last updated timestamp from data"""
    return data.get("last_updated", "1970-01-01T00:00:00")

def is_in_time_window(window_start, window_end, current_time, reminder_window_minutes=30):
    """Check if current time is within the medicine time window (with reminder buffer)"""
    try:
        # Parse times
        start_h, start_m = map(int, window_start.split(":"))
        end_h, end_m = map(int, window_end.split(":"))
        curr_h, curr_m = current_time.hour, current_time.minute

        # Convert to minutes since midnight
        start_mins = start_h * 60 + start_m - reminder_window_minutes
        end_mins = end_h * 60 + end_m + reminder_window_minutes
        curr_mins = curr_h * 60 + curr_m

        return start_mins <= curr_mins <= end_mins
    except:
        return False

def get_current_day():
    """Get current day as 3-letter lowercase (mon, tue, etc.)"""
    return datetime.now().strftime("%a").lower()

def get_pending_medicines(data):
    """Get list of medicines that are due now"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    current_day = get_current_day()

    pending = []

    for med in data.get("medicines", []):
        if not med.get("active", True):
            continue

        # Check if today is a scheduled day
        if current_day not in med.get("days", []):
            continue

        # Check if in time window
        window_start = med.get("window_start", "00:00")
        window_end = med.get("window_end", "23:59")

        if not is_in_time_window(window_start, window_end, now, REMINDER_WINDOW):
            continue

        # Check if already taken today
        tracking_key = f"{med['id']}_{med['time_window']}"
        if today not in data.get("tracking", {}):
            data["tracking"][today] = {}

        if tracking_key in data["tracking"][today]:
            if data["tracking"][today][tracking_key].get("taken", False):
                continue

        pending.append(med)

    return pending

def mark_medicines_taken(data, medicines):
    """Mark a list of medicines as taken and decrement pill count"""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S")

    if today not in data["tracking"]:
        data["tracking"][today] = {}

    for med in medicines:
        tracking_key = f"{med['id']}_{med['time_window']}"
        data["tracking"][today][tracking_key] = {
            "taken": True,
            "timestamp": timestamp
        }

        # Decrement pill count
        for i, stored_med in enumerate(data.get("medicines", [])):
            if stored_med["id"] == med["id"]:
                pills_per_dose = stored_med.get("pills_per_dose", 1)
                current_count = stored_med.get("pills_remaining", 0)
                data["medicines"][i]["pills_remaining"] = max(0, current_count - pills_per_dose)
                break

    return save_medicine_data(data)

def get_today_stats(data):
    """Get today's medicine statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    current_day = get_current_day()

    total = 0
    taken = 0

    for med in data.get("medicines", []):
        if not med.get("active", True):
            continue
        if current_day not in med.get("days", []):
            continue

        total += 1

        tracking_key = f"{med['id']}_{med['time_window']}"
        if today in data.get("tracking", {}):
            if tracking_key in data["tracking"][today]:
                if data["tracking"][today][tracking_key].get("taken", False):
                    taken += 1

    return taken, total

def draw_pill_icon(draw, x, y, size=10):
    """Draw a simple pill icon"""
    # Capsule shape
    draw.ellipse([x, y, x+size, y+size], outline=0, width=2)
    draw.line([x+size//4, y, x+size//4, y+size], fill=0, width=1)

def draw_food_icon(draw, x, y, size=8):
    """Draw a simple fork/knife icon for 'with food'"""
    # Fork
    draw.line([x, y, x, y+size], fill=0, width=1)
    draw.line([x-1, y, x-1, y+size//2], fill=0, width=1)
    draw.line([x+1, y, x+1, y+size//2], fill=0, width=1)

def draw_current_reminder(pending_meds, current_index=0):
    """Draw current medicine reminder (rotate through if multiple)"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(os.path.join(fontdir, "Roboto-Bold.ttf"), 12)
    f_med = ImageFont.truetype(os.path.join(fontdir, "Roboto-Bold.ttf"), 16)
    f_dose = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 12)
    f_small = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 10)

    # Title bar
    now = datetime.now().strftime("%H:%M")
    draw.text((5, 2), "TIME TO TAKE MEDICINE", font=f_title, fill=0)
    draw.text((200, 2), now, font=f_title, fill=0)
    draw.line([(0, 18), (250, 18)], fill=0, width=1)

    if not pending_meds:
        # No pending medicines
        draw.text((40, 50), "All caught up!", font=f_med, fill=0)
        draw.text((60, 70), "No medicines due now", font=f_small, fill=0)
    else:
        # Show current medicine (rotate through)
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

    # Bottom instructions
    draw.line([(0, 100), (250, 100)], fill=0, width=1)
    if pending_meds:
        if len(pending_meds) > 1:
            instruction = "Tap: Next | Double-tap: Take | Hold: Exit"
        else:
            instruction = "Double-tap: Mark taken | Hold: Exit"
    else:
        instruction = "Hold 2s: Exit"
    draw.text((10, 106), instruction, font=f_small, fill=0)

    return img

def draw_schedule_view(data):
    """Draw today's full schedule"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_title = ImageFont.truetype(os.path.join(fontdir, "Roboto-Bold.ttf"), 12)
    f_item = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 11)
    f_small = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 9)

    today = datetime.now().strftime("%b %d")
    current_day = get_current_day()

    # Title
    draw.text((5, 2), f"Today's Medicines - {today}", font=f_title, fill=0)
    draw.line([(0, 16), (250, 16)], fill=0, width=1)

    # Group medicines by time window
    windows = {}
    for med in data.get("medicines", []):
        if not med.get("active", True):
            continue
        if current_day not in med.get("days", []):
            continue

        window = med.get("time_window", "morning")
        if window not in windows:
            windows[window] = []
        windows[window].append(med)

    # Draw schedule
    y_pos = 20
    today_str = datetime.now().strftime("%Y-%m-%d")

    for window in ["morning", "afternoon", "evening", "night"]:
        if window not in windows:
            continue

        meds = windows[window]
        window_text = window.capitalize()

        # Window header
        draw.text((5, y_pos), window_text, font=f_item, fill=0)
        y_pos += 14

        for med in meds:
            # Check if taken
            tracking_key = f"{med['id']}_{window}"
            taken = False
            if today_str in data.get("tracking", {}):
                if tracking_key in data["tracking"][today_str]:
                    taken = data["tracking"][today_str][tracking_key].get("taken", False)

            # Checkbox
            checkbox = "[✓]" if taken else "[ ]"
            med_text = f"{checkbox} {med['name']} ({med['dosage']})"
            draw.text((15, y_pos), med_text, font=f_small, fill=0)
            y_pos += 11

    # Stats at bottom
    taken, total = get_today_stats(data)
    if total > 0:
        percentage = int((taken / total) * 100)
        draw.line([(0, 95), (250, 95)], fill=0, width=1)
        stats_text = f"Progress: {taken}/{total} taken ({percentage}%)"
        draw.text((40, 100), stats_text, font=f_small, fill=0)
        draw.text((30, 110), "Tap: Refresh | Hold: Exit", font=f_small, fill=0)

    return img

def draw_confirmation_screen(medicines_taken, count):
    """Draw confirmation screen after marking medicines taken"""
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_big = ImageFont.truetype(os.path.join(fontdir, "Roboto-Bold.ttf"), 20)
    f_medium = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 12)
    f_small = ImageFont.truetype(os.path.join(fontdir, "Roboto-Regular.ttf"), 10)

    # Big checkmark
    draw.text((90, 15), "✓", font=f_big, fill=0)

    # Confirmation text
    draw.text((60, 45), "Marked as Taken!", font=f_medium, fill=0)

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
    draw.text((80, 105), f"Taken at {now}", font=f_small, fill=0)

    return img

def run_medicine_app(epd, gt_dev, gt_old, gt):
    """Medicine tracking app with button controls"""

    flag_t = [1]

    def pthread_irq():
        while flag_t[0] == 1:
            if gt.digital_read(gt.INT) == 0:
                gt_dev.Touch = 1
            else:
                gt_dev.Touch = 0
            time.sleep(0.01)

    t = threading.Thread(target=pthread_irq)
    t.daemon = True
    t.start()

    last_update = 0
    rotation_index = 0
    view_mode = "reminder"  # "reminder" or "schedule"
    last_timestamp_check = 0
    TIMESTAMP_CHECK_INTERVAL = 5  # Check for external changes every 5 seconds

    # Click tracking for double-click detection
    last_click_time = 0
    DOUBLE_CLICK_TIME = 0.5  # 500ms for double click

    # Initial display
    data = load_medicine_data()
    last_known_timestamp = get_data_timestamp(data)
    pending = get_pending_medicines(data)

    if pending:
        image = draw_current_reminder(pending, rotation_index)
    else:
        image = draw_schedule_view(data)
        view_mode = "schedule"

    epd.displayPartial(epd.getbuffer(image))
    last_update = time.time()

    logging.info("Medicine app started")

    while True:
        current_time = time.time()

        # Check for external data changes (push refresh)
        if current_time - last_timestamp_check > TIMESTAMP_CHECK_INTERVAL:
            data = load_medicine_data()
            current_timestamp = get_data_timestamp(data)

            if current_timestamp != last_known_timestamp:
                logging.info(f"Data changed externally (timestamp: {current_timestamp}), refreshing display")
                last_known_timestamp = current_timestamp
                pending = get_pending_medicines(data)
                rotation_index = 0

                if pending and view_mode == "reminder":
                    image = draw_current_reminder(pending, rotation_index)
                else:
                    image = draw_schedule_view(data)
                    if not pending:
                        view_mode = "schedule"

                epd.displayPartial(epd.getbuffer(image))
                last_update = current_time

            last_timestamp_check = current_time

        # Auto-refresh data periodically
        if current_time - last_update > UPDATE_INTERVAL:
            logging.info("Auto-refreshing medicine data")
            data = load_medicine_data()
            pending = get_pending_medicines(data)

            if pending and view_mode == "reminder":
                image = draw_current_reminder(pending, rotation_index)
            else:
                image = draw_schedule_view(data)
                view_mode = "schedule"

            epd.displayPartial(epd.getbuffer(image))
            last_update = current_time

        # NO AUTO-ROTATION - user controls cycling manually

        gt.GT_Scan(gt_dev, gt_old)

        # Check for exit signal from menu
        if hasattr(gt_dev, "exit_requested") and gt_dev.exit_requested:
            logging.info("Exit requested by menu")
            flag_t[0] = 0
            break

        # Handle button clicks (menu system sets TouchpointFlag)
        # Note: No position check needed for GPIO-only (no touchscreen)
        if gt_dev.TouchpointFlag:
            logging.info("Button clicked - processing")
            gt_dev.TouchpointFlag = 0

            current_click_time = time.time()

            # Check if this is a double click
            if current_click_time - last_click_time < DOUBLE_CLICK_TIME:
                # Double click detected - mark selected medicine as taken
                logging.info("Double click - marking selected medicine as taken")
                last_click_time = 0  # Reset to prevent triple-click

                data = load_medicine_data()
                pending = get_pending_medicines(data)

                if pending and len(pending) > 0:
                    # Mark only the currently selected medicine
                    selected_med = [pending[rotation_index % len(pending)]]
                    logging.info(f"Marking {selected_med[0]['name']} as taken")

                    if mark_medicines_taken(data, selected_med):
                        # Show confirmation screen
                        epd.init(epd.FULL_UPDATE)
                        epd.Clear(0xFF)

                        image = draw_confirmation_screen(selected_med, 1)
                        epd.displayPartBaseImage(epd.getbuffer(image))
                        epd.init(epd.PART_UPDATE)

                        time.sleep(2)  # Show confirmation for 2 seconds

                        # Refresh display
                        data = load_medicine_data()
                        last_known_timestamp = get_data_timestamp(data)
                        pending = get_pending_medicines(data)
                        rotation_index = 0

                        if pending:
                            image = draw_current_reminder(pending, rotation_index)
                            view_mode = "reminder"
                        else:
                            image = draw_schedule_view(data)
                            view_mode = "schedule"

                        epd.displayPartial(epd.getbuffer(image))
                        last_update = current_time
            else:
                # Single click - cycle to next medicine
                last_click_time = current_click_time

                data = load_medicine_data()
                pending = get_pending_medicines(data)

                if pending and len(pending) > 1:
                    rotation_index = (rotation_index + 1) % len(pending)
                    logging.info(f"Single click - cycling to medicine {rotation_index + 1}/{len(pending)}")
                    image = draw_current_reminder(pending, rotation_index)
                    epd.displayPartial(epd.getbuffer(image))
                elif pending and len(pending) == 1:
                    logging.info("Single click - only one medicine, just refresh")
                    image = draw_current_reminder(pending, 0)
                    epd.displayPartial(epd.getbuffer(image))
                else:
                    logging.info("Single click - no pending medicines, show schedule")
                    image = draw_schedule_view(data)
                    epd.displayPartial(epd.getbuffer(image))

        time.sleep(0.1)

    gt_old.X[0] = 0
    gt_old.Y[0] = 0
    gt_old.S[0] = 0
