#!/usr/bin/python3
"""
Medicine Tracker App - Carousel Navigation UX
==============================================

Simplified single-button carousel navigation with Menu-first design.

Button Controls:
- SHORT PRESS (< 0.5s): Navigate to next item in carousel
- LONG PRESS (≥ 2s): Select/Execute current item

Navigation Flow:
1. Medicine List Carousel (Menu always first)
   - Menu → Medicine 1 → Medicine 2 → ... → Menu (loops)
2. Long press on medicine → Action Menu (Take/Skip/Back)
3. Long press on Menu → Menu Options (Pending/History/Stats/Exit)
4. Long press on action/option → Execute

States:
- MEDICINE_LIST: Carousel of medicines + menu
- ACTION_MENU: Take/Skip/Back for selected medicine
- MENU_OPTIONS: Pending/History/Stats/Exit
- SKIP_REASON: Reason selector for skip
- PENDING_VIEW: View pending doses
- HISTORY_VIEW: View skip history
- STATS_VIEW: View adherence stats
- CONFIRMATION: Success message (auto-transition)
"""

from shared.app_utils import ConfigLoader, install_signal_handlers
from display.fonts import get_font_preset
from db.medicine_db import MedicineDatabase
from PIL import Image, ImageDraw, ImageFont
from TP_lib import epd2in13_V3
from display import create_input_handler, InputHandler
import sys
import os
import time
from datetime import datetime, date, timedelta
import logging
import threading

# Setup paths
project_root = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, project_root)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
config = ConfigLoader()
medicine_config = config.get_section('medicine')
UPDATE_INTERVAL = medicine_config.get('update_interval', 60)

# Initialize database
db = MedicineDatabase()

# UI States
STATE_MEDICINE_LIST = "medicine_list"
STATE_ACTION_MENU = "action_menu"
STATE_MENU_OPTIONS = "menu_options"
STATE_SKIP_REASON = "skip_reason"
STATE_PENDING_VIEW = "pending_view"
STATE_HISTORY_VIEW = "history_view"
STATE_STATS_VIEW = "stats_view"
STATE_CONFIRMATION = "confirmation"

# Skip reasons
SKIP_REASONS = ["Forgot", "Side effects", "Out of stock", "Doctor advised", "Other"]

# Action menu items
ACTIONS = ["Take Now", "Skip", "Back"]

# Menu options
MENU_OPTIONS = ["Pending Doses", "Skip History", "Adherence", "Back"]

# Long press threshold
LONG_PRESS_DURATION = 2.0
CONFIRMATION_DURATION = 2.0


class MedicineApp:
    """Medicine tracker with carousel navigation"""

    def __init__(self):
        self.epd = epd2in13_V3()
        self.input_handler = None
        self.running = False
        self.display_lock = threading.Lock()

        # Touch/button objects passed from menu_button.py
        self.gt_dev = None
        self.gt_old = None
        self.gt = None

        # Navigation state
        self.state = STATE_MEDICINE_LIST
        self.carousel_index = 0
        self.medicines = []
        self.carousel_items = []  # ["MENU"] + medicines

        # Selected items
        self.selected_medicine = None
        self.selected_action = None
        self.selected_option = None
        self.selected_reason = None

        # Pending/History data
        self.pending_doses = []
        self.skip_history = []
        self.stats = {}

        # Index tracking for sub-views
        self.pending_index = 0
        self.history_index = 0
        self.stats_index = 0

        # Confirmation state
        self.confirmation_message = ""
        self.confirmation_timer = None

        # Auto-refresh
        self.refresh_timer = None

        # Button press tracking
        self.button_press_start = None

    def initialize(self):
        """Initialize display and input"""
        try:
            # Initialize display in FULL update mode and clear
            self.epd.init(self.epd.FULL_UPDATE)
            self.epd.Clear(0xFF)
            logger.info("Display initialized (FULL mode, cleared)")

            # Load initial data
            self.load_medicines()

            # Setup input handler
            self.setup_input()

            return True
        except Exception as e:
            logger.error(f"Initialize failed: {e}")
            return False

    def setup_input(self):
        """Setup input handler (uses TouchInputHandler via DummyTouch objects)"""
        try:
            # Use DummyTouch objects from menu_button.py
            # menu_button simulates touch by setting GT_Dev.TouchpointFlag = 1
            # TouchInputHandler detects this and triggers callbacks
            self.input_handler = create_input_handler(
                config=None,
                gt=self.gt,
                gt_dev=self.gt_dev,
                gt_old=self.gt_old
            )

            input_mode = self.input_handler.mode
            logger.info(f"Medicine app using {input_mode} input (button→touch conversion via menu_button)")

            # Button presses from menu_button are converted to touch events
            # BUT: menu_button ALSO sets GT_Dev.exit_requested on long press
            # So we need to check exit_requested in our main loop
            self.input_handler.on_touch = self.handle_touch
            self.input_handler.on_short_press = self.handle_touch  # Tap same as touch

            # Long press detection - BUT menu_button hijacks this for exit
            # So long press won't work for selecting items in carousel
            # We'll need to use a different interaction model

            self.input_handler.start()
            logger.info("Input handler started (touch events only, long press exits app)")

        except Exception as e:
            logger.error(f"Input setup failed: {e}")
            raise

    def load_medicines(self):
        """Load medicines for today's carousel (all active medicines not yet taken today)"""
        try:
            all_medicines = db.get_all_medicines()
            active_medicines = [m for m in all_medicines if m.get('active', True)]

            logger.info(f"DEBUG: Total medicines from DB: {len(all_medicines)}, Active: {len(active_medicines)}")

            # Get ALL active medicines that have NOT been taken today
            today = date.today()

            logger.info(f"DEBUG: Today: {today}")

            available_medicines = []
            for med in active_medicines:
                med_name = med.get('name', 'Unknown')
                med_id = med.get('id')

                logger.info(f"DEBUG: Checking {med_name} (ID: {med_id})")

                # Check if not already taken today
                tracking = db.get_tracking_history(
                    medicine_id=med['id'],
                    start_date=today,
                    end_date=today
                )

                logger.info(f"DEBUG:   Tracking records: {len(tracking)}")
                for t in tracking:
                    logger.info(f"DEBUG:     - Date: {t.get('date')}, Taken: {t.get('taken')}, Skipped: {t.get('skipped')}")

                # Only add if NOT taken today
                already_taken = any(t.get('taken', False) for t in tracking)
                logger.info(f"DEBUG:   Already taken today: {already_taken}")

                if not already_taken:
                    available_medicines.append(med)
                    logger.info(f"DEBUG:   ✓ ADDED to carousel")
                else:
                    logger.info(f"DEBUG:   ✗ SKIPPED (already taken)")

            self.medicines = available_medicines

            # Build carousel: MENU first, then all medicines, then EXIT
            self.carousel_items = ["MENU"] + self.medicines + ["EXIT"]
            self.carousel_index = 0

            logger.info(f"Loaded {len(self.medicines)} medicines for carousel")
            logger.info(f"DEBUG: Carousel medicines: {[m.get('name') for m in self.medicines]}")

        except Exception as e:
            logger.error(f"Failed to load medicines: {e}")
            logger.exception("Full traceback:")
            self.medicines = []
            self.carousel_items = ["MENU"]

    def load_pending_doses(self):
        """Load pending doses for today"""
        try:
            today = date.today()
            current_time = datetime.now().time()

            self.pending_doses = []
            for med in self.medicines:
                # Check if medicine is due in current time window
                if self.is_in_time_window(med, current_time):
                    # Check if not already taken today
                    tracking = db.get_tracking_history(
                        medicine_id=med['id'],
                        start_date=today,
                        end_date=today
                    )
                    if not any(t.get('taken', False) for t in tracking):
                        self.pending_doses.append(med)

            logger.info(f"Found {len(self.pending_doses)} pending doses")

        except Exception as e:
            logger.error(f"Failed to load pending doses: {e}")
            self.pending_doses = []

    def load_skip_history(self):
        """Load recent skip history (last 10)"""
        try:
            # Get last 7 days of tracking
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

            all_skips = []
            for med in self.medicines:
                tracking = db.get_tracking_history(
                    medicine_id=med['id'],
                    start_date=start_date,
                    end_date=end_date
                )
                for t in tracking:
                    if t.get('skipped', False):
                        all_skips.append({
                            'medicine': med['name'],
                            'dosage': med['dosage'],
                            'date': t['date'],
                            'reason': t.get('skip_reason', 'Unknown')
                        })

            # Sort by date (most recent first)
            all_skips.sort(key=lambda x: x['date'], reverse=True)
            self.skip_history = all_skips[:10]

            logger.info(f"Loaded {len(self.skip_history)} skip events")

        except Exception as e:
            logger.error(f"Failed to load skip history: {e}")
            self.skip_history = []

    def calculate_stats(self):
        """Calculate adherence stats for last 7 days"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

            total_taken = 0
            total_skipped = 0
            total_pending = 0

            for med in self.medicines:
                tracking = db.get_tracking_history(
                    medicine_id=med['id'],
                    start_date=start_date,
                    end_date=end_date
                )
                total_taken += sum(1 for t in tracking if t.get('taken', False))
                total_skipped += sum(1 for t in tracking if t.get('skipped', False))

            # Add today's pending
            self.load_pending_doses()
            total_pending = len(self.pending_doses)

            total = total_taken + total_skipped
            adherence_pct = int((total_taken / total * 100)) if total > 0 else 0

            self.stats = {
                'adherence': adherence_pct,
                'taken': total_taken,
                'skipped': total_skipped,
                'pending': total_pending
            }

            logger.info(f"Stats: {adherence_pct}% adherence")

        except Exception as e:
            logger.error(f"Failed to calculate stats: {e}")
            self.stats = {'adherence': 0, 'taken': 0, 'skipped': 0, 'pending': 0}

    def is_in_time_window(self, medicine, current_time):
        """Check if current time is in medicine's time window"""
        try:
            window_start = medicine.get('window_start', '00:00')
            window_end = medicine.get('window_end', '23:59')

            start_parts = window_start.split(':')
            end_parts = window_end.split(':')

            start_time = datetime.strptime(window_start, '%H:%M').time()
            end_time = datetime.strptime(window_end, '%H:%M').time()

            return start_time <= current_time <= end_time
        except:
            return True  # Default to always due if parsing fails

    # ========================================================================
    # BUTTON/TOUCH HANDLERS
    # ========================================================================

    def handle_button_press(self):
        """Button pressed - record time"""
        self.button_press_start = time.time()

    def handle_button_release(self):
        """Button released - determine short or long press"""
        if self.button_press_start is None:
            return

        duration = time.time() - self.button_press_start
        self.button_press_start = None

        if duration < 0.5:
            self.handle_short_press()
        elif duration >= LONG_PRESS_DURATION:
            self.handle_long_press()

    def handle_touch(self, x=0, y=0):
        """Touch detected - check if short or long press"""
        # Check TouchpointFlag to distinguish short (1) vs long press (2)
        if self.gt_dev and self.gt_dev.TouchpointFlag == 2:
            # Long press - select/execute
            self.gt_dev.TouchpointFlag = 0  # Clear flag
            self.handle_long_press()
        else:
            # Short press - navigate
            if self.gt_dev:
                self.gt_dev.TouchpointFlag = 0  # Clear flag
            self.handle_short_press()

    def handle_short_press(self):
        """Navigate to next item in current context"""
        if self.state == STATE_MEDICINE_LIST:
            self.next_medicine()
        elif self.state == STATE_ACTION_MENU:
            self.next_action()
        elif self.state == STATE_MENU_OPTIONS:
            self.next_menu_option()
        elif self.state == STATE_SKIP_REASON:
            self.next_skip_reason()
        elif self.state == STATE_PENDING_VIEW:
            self.next_pending()
        elif self.state == STATE_HISTORY_VIEW:
            self.next_history()
        elif self.state == STATE_STATS_VIEW:
            self.next_stats_view()
        elif self.state == STATE_CONFIRMATION:
            pass  # Ignore during confirmation

    def handle_long_press(self):
        """Select/execute current item"""
        if self.state == STATE_MEDICINE_LIST:
            current_item = self.carousel_items[self.carousel_index]
            if current_item == "MENU":
                self.enter_menu_options()
            elif current_item == "EXIT":
                self.stop()
            else:
                self.selected_medicine = current_item
                self.enter_action_menu()

        elif self.state == STATE_ACTION_MENU:
            self.execute_action()

        elif self.state == STATE_MENU_OPTIONS:
            self.execute_menu_option()

        elif self.state == STATE_SKIP_REASON:
            self.confirm_skip()

        elif self.state == STATE_PENDING_VIEW:
            # Handle pending view long press
            pending_items = self.pending_doses + ["BACK"]
            current_item = pending_items[self.pending_index]

            if current_item == "BACK":
                # Go back to menu options
                self.return_to_menu_options()
            else:
                # Open action menu for this medicine
                self.selected_medicine = current_item
                self.enter_action_menu()

        elif self.state == STATE_HISTORY_VIEW:
            # Handle history view long press
            history_items = self.skip_history + ["BACK"]
            current_item = history_items[self.history_index]

            if current_item == "BACK":
                self.return_to_menu_options()
            # Note: Can't take action on historical skip events, just go back

        elif self.state == STATE_STATS_VIEW:
            # Handle stats view long press
            stats_items = ["Overall", "BACK"]
            current_item = stats_items[self.stats_index]

            if current_item == "BACK":
                self.return_to_menu_options()
            # Note: No action on stats, just viewing

    # ========================================================================
    # NAVIGATION METHODS
    # ========================================================================

    def next_medicine(self):
        """Move to next item in medicine carousel"""
        self.carousel_index = (self.carousel_index + 1) % len(self.carousel_items)
        self.render()

    def next_action(self):
        """Move to next action in action menu"""
        if self.selected_action is None:
            self.selected_action = 0
        else:
            self.selected_action = (self.selected_action + 1) % len(ACTIONS)
        self.render()

    def next_menu_option(self):
        """Move to next menu option"""
        if self.selected_option is None:
            self.selected_option = 0
        else:
            self.selected_option = (self.selected_option + 1) % len(MENU_OPTIONS)
        self.render()

    def next_skip_reason(self):
        """Move to next skip reason"""
        if self.selected_reason is None:
            self.selected_reason = 0
        else:
            self.selected_reason = (self.selected_reason + 1) % (len(SKIP_REASONS) + 1)  # +1 for Back
        self.render()

    def next_pending(self):
        """Move to next pending dose"""
        # Build carousel: pending doses + BACK
        pending_items = self.pending_doses + ["BACK"]

        # Cycle through items
        self.pending_index = (self.pending_index + 1) % len(pending_items)
        self.render()

    def next_history(self):
        """Move to next history item"""
        # Build carousel: skip history + BACK
        history_items = self.skip_history + ["BACK"]

        # Cycle through items
        self.history_index = (self.history_index + 1) % len(history_items)
        self.render()

    def next_stats_view(self):
        """Cycle stats views"""
        # Build carousel: Overall stats + BACK
        stats_items = ["Overall", "BACK"]

        # Cycle through items
        self.stats_index = (self.stats_index + 1) % len(stats_items)
        self.render()

    # ========================================================================
    # STATE TRANSITIONS
    # ========================================================================

    def enter_action_menu(self):
        """Enter action menu for selected medicine"""
        self.state = STATE_ACTION_MENU
        self.selected_action = 0
        logger.info(f"Entered action menu for {self.selected_medicine['name']}")
        self.render()

    def enter_menu_options(self):
        """Enter menu options"""
        self.state = STATE_MENU_OPTIONS
        self.selected_option = 0
        logger.info("Entered menu options")
        self.render()

    def enter_skip_reason(self):
        """Enter skip reason selector"""
        self.state = STATE_SKIP_REASON
        self.selected_reason = 0
        logger.info("Entered skip reason selector")
        self.render()

    def return_to_medicine_list(self):
        """Return to main medicine carousel"""
        self.state = STATE_MEDICINE_LIST
        self.selected_medicine = None
        self.selected_action = None

        # Reload medicines to reflect any changes (taken/skipped)
        self.load_medicines()

        # Reset carousel index if it's now out of bounds
        if self.carousel_index >= len(self.carousel_items):
            self.carousel_index = 0

        logger.info("Returned to medicine list")
        self.render()

    def return_to_menu_options(self):
        """Return to menu options"""
        self.state = STATE_MENU_OPTIONS
        self.selected_option = 0  # Reset to first option
        logger.info("Returned to menu options")
        self.render()

    # ========================================================================
    # ACTIONS
    # ========================================================================

    def execute_action(self):
        """Execute selected action from action menu"""
        action = ACTIONS[self.selected_action]

        if action == "Take Now":
            self.take_medicine()
        elif action == "Skip":
            self.enter_skip_reason()
        elif action == "Back":
            self.return_to_medicine_list()

    def take_medicine(self):
        """Mark medicine as taken"""
        try:
            med = self.selected_medicine
            success = db.mark_medicine_taken(
                medicine_id=med['id'],
                time_window=med.get('time_window', 'anytime'),
                taken_date=date.today()
            )

            if success:
                pills_remaining = med.get('pills_remaining', 0) - med.get('pills_per_dose', 1)
                self.show_confirmation(
                    f"✓ {med['name'].upper()} TAKEN\n\n"
                    f"{pills_remaining} pills remaining\n"
                    f"Logged: {datetime.now().strftime('%m/%d %I:%M %p')}"
                )
                logger.info(f"Marked {med['name']} as taken")
            else:
                self.show_confirmation("Error marking taken\nPlease try again")

        except Exception as e:
            logger.error(f"Failed to mark taken: {e}")
            self.show_confirmation("Error marking taken")

    def confirm_skip(self):
        """Confirm skip with selected reason"""
        if self.selected_reason >= len(SKIP_REASONS):
            # Selected "Back"
            self.state = STATE_ACTION_MENU
            self.render()
            return

        try:
            med = self.selected_medicine
            reason = SKIP_REASONS[self.selected_reason]

            success = db.skip_medicine(
                med['id'],
                date.today().isoformat(),
                reason=reason
            )

            if success:
                self.show_confirmation(
                    f"⏭️ {med['name'].upper()} SKIPPED\n\n"
                    f"Reason: {reason}\n"
                    f"Logged: {datetime.now().strftime('%m/%d %I:%M %p')}"
                )
                logger.info(f"Skipped {med['name']} - {reason}")
            else:
                self.show_confirmation("Error recording skip")

        except Exception as e:
            logger.error(f"Failed to record skip: {e}")
            self.show_confirmation("Error recording skip")

    def execute_menu_option(self):
        """Execute selected menu option"""
        option = MENU_OPTIONS[self.selected_option]

        if option == "Pending Doses":
            self.load_pending_doses()
            self.pending_index = 0  # Reset index when entering view
            self.state = STATE_PENDING_VIEW
            self.render()

        elif option == "Skip History":
            self.load_skip_history()
            self.history_index = 0  # Reset index when entering view
            self.state = STATE_HISTORY_VIEW
            self.render()

        elif option == "Adherence":
            self.calculate_stats()
            self.stats_index = 0  # Reset index when entering view
            self.state = STATE_STATS_VIEW
            self.render()

        elif option == "Back":
            self.return_to_medicine_list()

    def show_confirmation(self, message):
        """Show confirmation message and auto-return"""
        self.confirmation_message = message
        self.state = STATE_CONFIRMATION
        self.render()

        # Auto-return to medicine list after delay
        if self.confirmation_timer:
            self.confirmation_timer.cancel()

        self.confirmation_timer = threading.Timer(
            CONFIRMATION_DURATION,
            self.return_to_medicine_list
        )
        self.confirmation_timer.start()

    # ========================================================================
    # RENDERING
    # ========================================================================

    def render_to_image(self):
        """Create image for current state without displaying (used for base image setup)"""
        # For now, just render medicine list since that's the initial state
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        current_item = self.carousel_items[self.carousel_index]

        # Header
        draw.text((5, 5), "MEDICINE TRACKER", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        if current_item == "MENU":
            # Show menu icon
            draw.text((self.epd.height//2 - 30, 50), "⚙️  MENU", font=font_title, fill=0)
        else:
            # Show medicine details
            med = current_item
            y = 35

            # Medicine name
            draw.text((5, y), f"💊 {med['name']}", font=font_title, fill=0)
            y += 22

            # Dosage
            draw.text((5, y), med['dosage'], font=font_body, fill=0)
            y += 18

            # Pills remaining (with warning if low)
            pills = med.get('pills_remaining', 0)
            threshold = med.get('low_stock_threshold', 7)
            warning = " ⚠️ LOW" if pills <= threshold else ""
            draw.text((5, y), f"{pills} pills{warning}", font=font_body, fill=0)
            y += 18

            # Time window
            window = med.get('time_window', 'anytime').capitalize()
            start = med.get('window_start', '')
            end = med.get('window_end', '')
            draw.text((5, y), f"{window} ({start}-{end})", font=font_body, fill=0)

        # Instructions at bottom - single line
        y = self.epd.width - 12
        draw.text((5, y), "Click: Next | Hold 2s: Select", font=font_hint, fill=0)

        return image

    def render(self):
        """Render current state to display using displayPartial()"""
        logger.info(f"DEBUG: render() called, state={self.state}")
        with self.display_lock:
            try:
                if self.state == STATE_MEDICINE_LIST:
                    logger.info("DEBUG: Calling render_medicine_list()")
                    self.render_medicine_list()
                    logger.info("DEBUG: render_medicine_list() completed")
                elif self.state == STATE_ACTION_MENU:
                    logger.info("DEBUG: Calling render_action_menu()")
                    self.render_action_menu()
                elif self.state == STATE_MENU_OPTIONS:
                    logger.info("DEBUG: Calling render_menu_options()")
                    self.render_menu_options()
                elif self.state == STATE_SKIP_REASON:
                    logger.info("DEBUG: Calling render_skip_reason()")
                    self.render_skip_reason()
                elif self.state == STATE_PENDING_VIEW:
                    logger.info("DEBUG: Calling render_pending_view()")
                    self.render_pending_view()
                elif self.state == STATE_HISTORY_VIEW:
                    logger.info("DEBUG: Calling render_history_view()")
                    self.render_history_view()
                elif self.state == STATE_STATS_VIEW:
                    logger.info("DEBUG: Calling render_stats_view()")
                    self.render_stats_view()
                elif self.state == STATE_CONFIRMATION:
                    logger.info("DEBUG: Calling render_confirmation()")
                    self.render_confirmation()

            except Exception as e:
                logger.error(f"Render failed: {e}", exc_info=True)

    def render_medicine_list(self):
        """Render medicine carousel"""
        logger.info(f"DEBUG: render_medicine_list() start, carousel_index={self.carousel_index}")
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)
        logger.info("DEBUG: Image created")

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')
        logger.info("DEBUG: Fonts loaded")

        current_item = self.carousel_items[self.carousel_index]
        logger.info(f"DEBUG: Current item = {current_item if current_item == 'MENU' else 'MEDICINE'}")

        # Header
        draw.text((5, 5), "MEDICINE TRACKER", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)
        logger.info("DEBUG: Header drawn")

        if current_item == "MENU":
            # Show menu icon
            if len(self.medicines) == 0:
                # No pending medicines - show completion message
                draw.text((self.epd.height//2 - 60, 45), "✓ All Done!", font=font_title, fill=0)
                draw.text((5, 70), "No medicines due today", font=font_body, fill=0)
                logger.info("DEBUG: No pending medicines message shown")
            else:
                draw.text((self.epd.height//2 - 30, 50), "⚙️  MENU", font=font_title, fill=0)
                logger.info("DEBUG: Menu item drawn")
        elif current_item == "EXIT":
            # Show EXIT option
            draw.text((self.epd.height//2 - 30, 50), "🚪 EXIT", font=font_title, fill=0)
            logger.info("DEBUG: Exit item drawn")
        else:
            # Show medicine details
            med = current_item
            y = 35

            # Medicine name
            draw.text((5, y), f"💊 {med['name']}", font=font_title, fill=0)
            y += 22

            # Dosage
            draw.text((5, y), med['dosage'], font=font_body, fill=0)
            y += 18

            # Pills remaining (with warning if low)
            pills = med.get('pills_remaining', 0)
            threshold = med.get('low_stock_threshold', 7)
            warning = " ⚠️ LOW" if pills <= threshold else ""
            draw.text((5, y), f"{pills} pills{warning}", font=font_body, fill=0)
            y += 18

            # Time window
            window = med.get('time_window', 'anytime').capitalize()
            start = med.get('window_start', '')
            end = med.get('window_end', '')
            draw.text((5, y), f"{window} ({start}-{end})", font=font_body, fill=0)
            logger.info("DEBUG: Medicine details drawn")

        # Instructions at bottom - single line
        y = self.epd.width - 12
        draw.text((5, y), "Click: Next | Hold 2s: Select", font=font_hint, fill=0)
        logger.info("DEBUG: Instructions drawn, about to call displayPartial()")

        self.epd.displayPartial(self.epd.getbuffer(image))
        logger.info("DEBUG: displayPartial() completed")

    def render_action_menu(self):
        """Render action menu (Take/Skip/Back)"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('body')
        font_action = get_font_preset('title')
        font_hint = get_font_preset('subtitle')

        med = self.selected_medicine

        # Header - medicine name
        draw.text((5, 5), f"{med['name']} - {med['dosage']}", font=font_title, fill=0)
        draw.line([(0, 22), (self.epd.height, 22)], fill=0, width=1)

        # Current action (large)
        action = ACTIONS[self.selected_action]
        icon = "✓" if action == "Take Now" else "⏭️" if action == "Skip" else "←"
        draw.text((self.epd.height//2 - 50, 50), f"{icon} {action.upper()}", font=font_action, fill=0)

        # Pills remaining info
        y = 85
        pills = med.get('pills_remaining', 0)
        draw.text((5, y), f"{pills} pills remaining", font=font_title, fill=0)

        # Time window
        y += 18
        window = med.get('time_window', 'anytime').capitalize()
        start = med.get('window_start', '')
        end = med.get('window_end', '')
        draw.text((5, y), f"{window} ({start}-{end})", font=font_title, fill=0)

        # Instructions - single line
        y = self.epd.width - 12
        draw.text((5, y), "Click: Next | Hold 2s: Confirm", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_menu_options(self):
        """Render menu options"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        # Header
        draw.text((5, 5), "MENU OPTIONS", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        # Current option
        option = MENU_OPTIONS[self.selected_option]
        icons = {"Pending Doses": "📋", "Skip History": "⏭️", "Adherence": "📊", "Back": "←"}
        icon = icons.get(option, "")

        y = 50
        draw.text((self.epd.height//2 - 60, y), f"{icon} {option.upper()}", font=font_title, fill=0)

        # Option-specific info
        y = 80
        if option == "Pending Doses":
            count = len(self.pending_doses) if hasattr(self, 'pending_doses') else 0
            draw.text((5, y), f"{count} medicines due today", font=font_body, fill=0)
        elif option == "Skip History":
            draw.text((5, y), "Recent skips", font=font_body, fill=0)
        elif option == "Adherence":
            draw.text((5, y), "Last 7 days stats", font=font_body, fill=0)

        # Instructions - single line
        y = self.epd.width - 12
        draw.text((5, y), "Click: Next | Hold 2s: View", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_skip_reason(self):
        """Render skip reason selector"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        # Header
        draw.text((5, 5), "WHY SKIP?", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        # Current reason
        if self.selected_reason < len(SKIP_REASONS):
            reason = SKIP_REASONS[self.selected_reason]
            icons = {"Forgot": "😴", "Side effects": "🤢", "Out of stock": "📦",
                     "Doctor advised": "🏥", "Other": "❓"}
            icon = icons.get(reason, "")
            draw.text((self.epd.height//2 - 50, 50), f"{icon} {reason.upper()}", font=font_title, fill=0)
        else:
            draw.text((self.epd.height//2 - 30, 50), "← BACK", font=font_title, fill=0)

        # Instructions - single line
        y = self.epd.width - 12
        draw.text((5, y), "Click: Next | Hold 2s: Confirm", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_pending_view(self):
        """Render pending doses view"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        # Header
        draw.text((5, 5), "PENDING DOSES", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        if not self.pending_doses:
            draw.text((5, 50), "No pending doses!", font=font_body, fill=0)
        else:
            # Build carousel: pending doses + BACK
            pending_items = self.pending_doses + ["BACK"]
            current_item = pending_items[self.pending_index]

            if current_item == "BACK":
                # Show BACK option
                draw.text((self.epd.height//2 - 30, 50), "← BACK", font=font_title, fill=0)
            else:
                # Show medicine details
                dose = current_item
                y = 35
                draw.text((5, y), f"💊 {dose['name']}", font=font_title, fill=0)
                y += 22
                draw.text((5, y), dose['dosage'], font=font_body, fill=0)
                y += 18
                window = dose.get('time_window', 'anytime').capitalize()
                start = dose.get('window_start', '')
                end = dose.get('window_end', '')
                draw.text((5, y), f"{window} ({start}-{end})", font=font_body, fill=0)

        # Instructions
        draw.text((5, self.epd.width - 12), "Click: Next | Hold 2s: Select", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_history_view(self):
        """Render skip history view"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        # Header
        draw.text((5, 5), "SKIP HISTORY", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        if not self.skip_history:
            draw.text((5, 50), "No skips recorded", font=font_body, fill=0)
        else:
            # Build carousel: skip history + BACK
            history_items = self.skip_history + ["BACK"]
            current_item = history_items[self.history_index]

            if current_item == "BACK":
                # Show BACK option
                draw.text((self.epd.height//2 - 30, 50), "← BACK", font=font_title, fill=0)
            else:
                # Show skip event details
                skip = current_item
                y = 35
                draw.text((5, y), f"⏭️ {skip['medicine']}", font=font_title, fill=0)
                y += 22
                draw.text((5, y), skip['dosage'], font=font_body, fill=0)
                y += 18
                draw.text((5, y), f"Date: {skip['date']}", font=font_body, fill=0)
                y += 18
                draw.text((5, y), f"Reason: {skip['reason']}", font=font_body, fill=0)

        draw.text((5, self.epd.width - 12), "Click: Next | Hold 2s: Select", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_stats_view(self):
        """Render adherence stats view"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_title = get_font_preset('title')
        font_body = get_font_preset('body')
        font_hint = get_font_preset('subtitle')

        # Header
        draw.text((5, 5), "ADHERENCE STATS", font=font_title, fill=0)
        draw.line([(0, 25), (self.epd.height, 25)], fill=0, width=1)

        # Build carousel: Overall stats + BACK
        stats_items = ["Overall", "BACK"]
        current_item = stats_items[self.stats_index]

        if current_item == "BACK":
            # Show BACK option
            draw.text((self.epd.height//2 - 30, 50), "← BACK", font=font_title, fill=0)
        else:
            # Show overall stats
            y = 40
            draw.text((5, y), f"Last 7 Days: {self.stats.get('adherence', 0)}%", font=font_title, fill=0)
            y += 25
            draw.text((5, y), f"Taken: {self.stats.get('taken', 0)} | Skipped: {self.stats.get('skipped', 0)}", font=font_body, fill=0)
            y += 20
            draw.text((5, y), f"Pending: {self.stats.get('pending', 0)}", font=font_body, fill=0)

        draw.text((5, self.epd.width - 12), "Click: Next | Hold 2s: Select", font=font_hint, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    def render_confirmation(self):
        """Render confirmation message"""
        image = Image.new('1', (self.epd.height, self.epd.width), 255)
        draw = ImageDraw.Draw(image)

        font_body = get_font_preset('body')

        # Center the message
        y = 30
        for line in self.confirmation_message.split('\n'):
            draw.text((5, y), line, font=font_body, fill=0)
            y += 15

        draw.text((5, self.epd.width - 15), "[Returning to list...]", font=font_body, fill=0)

        self.epd.displayPartial(self.epd.getbuffer(image))

    # ========================================================================
    # LIFECYCLE
    # ========================================================================

    def run(self):
        """Main run loop"""
        self.running = True
        logger.info("Medicine app started")

        # Initial FULL render to set base image for partial updates
        logger.info("DEBUG: Drawing initial screen (FULL mode)")
        image = self.render_to_image()

        # Set this as the base image for partial updates
        self.epd.displayPartBaseImage(self.epd.getbuffer(image))
        logger.info("DEBUG: Base image set with displayPartBaseImage()")

        # CRITICAL: Wait for base image to fully commit before switching modes
        time.sleep(1)
        logger.info("DEBUG: Waited for base image to settle")

        # Switch to partial update mode for fast refreshes
        self.epd.init(self.epd.PART_UPDATE)
        logger.info("DEBUG: Switched to PARTIAL update mode")

        # Setup auto-refresh
        self.schedule_refresh()

        # Keep running - poll for button presses via TouchpointFlag
        logger.info("DEBUG: Entering main while loop")
        try:
            while self.running:
                # Check for button press (menu_button sets TouchpointFlag)
                if self.gt_dev and self.gt_dev.TouchpointFlag:
                    flag_value = self.gt_dev.TouchpointFlag
                    self.gt_dev.TouchpointFlag = 0  # Clear flag

                    if flag_value == 2:
                        # Long press
                        logger.info(f"DEBUG: Long press detected in state={self.state}")
                        self.handle_long_press()
                    elif flag_value == 1:
                        # Short press
                        logger.info(f"DEBUG: Short press detected in state={self.state}")
                        self.handle_short_press()

                # Check for exit request
                if self.gt_dev and hasattr(self.gt_dev, 'exit_requested') and self.gt_dev.exit_requested:
                    logger.info("Exit requested via long press")
                    break

                time.sleep(0.1)  # Poll every 100ms
        except KeyboardInterrupt:
            logger.info("Interrupted by user")

    def schedule_refresh(self):
        """Schedule periodic data refresh"""
        if not self.running:
            return

        logger.info("Auto-refreshing medicine data")
        self.load_medicines()
        self.render()

        self.refresh_timer = threading.Timer(UPDATE_INTERVAL, self.schedule_refresh)
        self.refresh_timer.start()

    def stop(self):
        """Cleanup and exit"""
        logger.info("Cleaning up medicine app...")
        self.running = False

        if self.confirmation_timer:
            self.confirmation_timer.cancel()

        if self.refresh_timer:
            self.refresh_timer.cancel()

        if self.input_handler:
            logger.info("Stopping input handler...")
            self.input_handler.stop()

        db.close()
        logger.info("Medicine app stopped")


def main():
    """Main entry point"""
    app = MedicineApp()

    # Install signal handlers with app cleanup
    install_signal_handlers(app.stop)

    if not app.initialize():
        logger.error("Failed to initialize app")
        return

    try:
        app.run()
    finally:
        app.stop()


def run_medicine_app(epd, GT_Dev, GT_Old, gt):
    """
    Wrapper function for compatibility with menu_button.py

    Args:
        epd: E-ink display instance
        GT_Dev, GT_Old, gt: Touch controller instances (button mode uses existing handler from menu)
    """
    logger.info("Starting medicine app via menu_button wrapper")

    app = MedicineApp()

    # CRITICAL: Use EPD instance from menu_button (don't create new one!)
    app.epd = epd
    logger.info("Using EPD instance from menu_button")

    # Pass touch/button objects from menu to avoid GPIO conflict
    app.gt_dev = GT_Dev
    app.gt_old = GT_Old
    app.gt = gt

    # Enable internal long-press handling for carousel selection
    # menu_button will send TouchpointFlag=2 instead of exiting
    if GT_Dev:
        GT_Dev.handle_long_press_internally = True
        logger.info("Enabled internal long-press handling (carousel mode)")

    # Install signal handlers with app cleanup
    install_signal_handlers(app.stop)

    if not app.initialize():
        logger.error("Failed to initialize app")
        return

    try:
        app.run()
    finally:
        app.stop()


if __name__ == "__main__":
    main()
