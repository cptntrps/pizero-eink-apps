#!/usr/bin/python3
"""
Flights Tracker Application
===========================

Real-time flight tracking using FlightRadar24 API with e-ink display.
Refactored to use shared utilities and display components.

Key Features:
- Live overhead flight detection within configurable radius
- Compass bearing indicator
- Aviation quotes when no flights detected
- Animated flight information cycling
"""

from TP_lib import gt1151, epd2in13_V3
import time
import json
import subprocess
import math
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

from shared.app_utils import (
    setup_logging,
    ConfigLoader,
    check_exit_requested,
    cleanup_touch_state,
    setup_paths,
    PeriodicTimer,
    safe_execute
)
from display.touch_handler import TouchHandler
from display.icons import draw_compass_icon
from display.fonts import get_font_preset
from display import create_input_handler

# ============================================================================
# INITIALIZATION
# ============================================================================

setup_paths()

logger = setup_logging('flights_app', log_to_file=True)

# Load configuration
config = ConfigLoader.load()
flights_config = config.get("flights", {})
LAT = flights_config.get("latitude", 51.5)
LON = flights_config.get("longitude", -0.1)
RADIUS_KM = flights_config.get("radius_km", 50)

logger.info(f"Flights app initialized - Position: {LAT}, {LON}, Radius: {RADIUS_KM}km")

# FR24 API configuration
CACHE_FILE = "/tmp/flights_cache.json"
lat_offset = RADIUS_KM / 111.0
lon_offset = RADIUS_KM / (111.0 * abs(math.cos(math.radians(LAT))))

LAMIN = LAT - lat_offset
LAMAX = LAT + lat_offset
LOMIN = LON - lon_offset
LOMAX = LON + lon_offset

BOUNDS_BOX = f"{LAMAX},{LAMIN},{LOMIN},{LOMAX}"
FLIGHT_SEARCH_URL = f"https://data-cloud.flightradar24.com/zones/fcgi/feed.js?bounds={BOUNDS_BOX}&faa=1&satellite=1&mlat=1&flarm=1&adsb=1&gnd=0&air=1&vehicles=0&estimated=0&maxage=14400&gliders=0&stats=0&ems=1"

# Aviation quotes for display
AVIATION_QUOTES = [
    ("Flying is learning how to\nthrow yourself at the\nground and miss.", "Douglas Adams"),
    ("There are old pilots and\nbold pilots, but no old,\nbold pilots.", "Aviation Adage"),
    ("Every takeoff is optional.\nEvery landing is mandatory.", "Aviation Adage"),
    ("A good landing is one\nfrom which you can walk\naway.", "Aviation Adage"),
    ("The probability of\nsurvival is inversely\nproportional to the\nangle of arrival.", "Neil Armstrong"),
    ("Aviate, Navigate,\nCommunicate.", "Pilot's Mantra"),
    ("If you push the stick\nforward, the houses\nget bigger.", "Aviation Adage"),
    ("The propeller is just a\nbig fan to keep the\npilot cool.", "Aviation Humor"),
    ("Helicopters don't fly.\nThey beat the air into\nsubmission.", "Aviation Humor"),
    ("Gravity is not just a\ngood idea. It's the law.", "Aviation Adage"),
    ("Learn from the mistakes\nof others. You won't\nlive long enough.", "Aviation Adage"),
    ("A superior pilot uses\nsuperior judgment to\navoid situations.", "Frank Borman"),
    ("The only time you have\ntoo much fuel is when\nyou're on fire.", "Aviation Adage"),
]

# Display constants
UPDATE_INTERVAL = 30
ANIMATION_CYCLE_INTERVAL = 10
QUOTE_INTERVAL = 300


# ============================================================================
# GEOGRAPHIC CALCULATIONS
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2)
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate bearing from point 1 to point 2 in degrees (0-360)"""
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlon_rad = math.radians(lon2 - lon1)

    x = math.sin(dlon_rad) * math.cos(lat2_rad)
    y = (math.cos(lat1_rad) * math.sin(lat2_rad) -
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))

    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360


# ============================================================================
# FLIGHT DATA RETRIEVAL
# ============================================================================

def get_flight_search() -> tuple:
    """Search for closest commercial flight in area

    Returns:
        Tuple of (flight_id, distance_km, bearing_degrees) or (None, None, None)
    """
    def _fetch():
        result = subprocess.run(
            ["curl", "-s", "-m", "10", FLIGHT_SEARCH_URL],
            capture_output=True, text=True, timeout=12
        )

        if result.returncode != 0:
            return None, None, None

        data = json.loads(result.stdout)
        commercial_flights = []

        for flight_id, flight_info in data.items():
            if flight_id in ["version", "full_count"]:
                continue

            if len(flight_info) <= 13:
                continue

            flight_lat = flight_info[1]
            flight_lon = flight_info[2]
            callsign = flight_info[13]

            if not callsign or callsign.strip() == "":
                continue

            distance = haversine_distance(LAT, LON, flight_lat, flight_lon)

            if distance <= RADIUS_KM:
                bearing = calculate_bearing(LAT, LON, flight_lat, flight_lon)
                commercial_flights.append({
                    "id": flight_id,
                    "distance": distance,
                    "bearing": bearing,
                    "callsign": callsign
                })

        if not commercial_flights:
            logger.info("No commercial flights within radius")
            return None, None, None

        commercial_flights.sort(key=lambda x: x["distance"])
        chosen = commercial_flights[0]
        logger.info(f"Found flight {chosen['callsign']} at {chosen['distance']:.1f}km, "
                    f"bearing {chosen['bearing']:.0f}°")
        return chosen["id"], chosen["distance"], chosen["bearing"]

    return safe_execute(_fetch, "Flight search error", (None, None, None))


def get_flight_details(flight_id: str) -> dict:
    """Get detailed flight info from FR24

    Args:
        flight_id: Flight ID from FR24

    Returns:
        Dictionary with flight data or None on error
    """
    def _fetch():
        url = f"https://data-live.flightradar24.com/clickhandler/?flight={flight_id}"

        result = subprocess.run(
            ["curl", "-s", "-m", "10", url],
            capture_output=True, text=True, timeout=12
        )

        if result.returncode != 0:
            return None

        data = json.loads(result.stdout)

        # Extract identification data
        identification = data.get("identification", {})
        flight_number = identification.get("number", {})
        flight_number = flight_number.get("default", "") if flight_number else ""

        callsign = identification.get("callsign", "")
        if callsign == "Blocked":
            callsign = ""

        # Extract aircraft data
        aircraft = data.get("aircraft", {})
        aircraft_model = aircraft.get("model", {})
        aircraft_code = aircraft_model.get("code", "?") if aircraft_model else "?"

        # Extract airline data
        airline = data.get("airline", {})
        airline_name = airline.get("name", "") if airline else ""

        # Extract airport data
        airport = data.get("airport", {})
        origin = airport.get("origin") if airport else None
        destination = airport.get("destination") if airport else None

        origin_code = "?"
        dest_code = "?"
        origin_name = ""
        dest_name = ""

        if origin:
            origin_iata = origin.get("code", {})
            origin_code = origin_iata.get("iata", "?") if origin_iata else "?"
            origin_name = origin.get("name", "").replace(" Airport", "")

        if destination:
            dest_iata = destination.get("code", {})
            dest_code = dest_iata.get("iata", "?") if dest_iata else "?"
            dest_name = destination.get("name", "").replace(" Airport", "")

        # Extract trail data
        trail = data.get("trail", [])
        altitude = 0
        speed = 0
        if trail and len(trail) > 0:
            altitude = int(trail[0].get("alt", 0))
            speed = int(trail[0].get("spd", 0))

        return {
            "callsign": flight_number or callsign or flight_id[-4:].upper(),
            "airline": airline_name,
            "origin": origin_code,
            "destination": dest_code,
            "origin_name": origin_name,
            "dest_name": dest_name,
            "aircraft": aircraft_code,
            "altitude": altitude,
            "speed": speed,
            "timestamp": datetime.now().strftime("%H:%M")
        }

    flight_data = safe_execute(_fetch, "Flight details error", None)

    if flight_data:
        logger.info(f"Flight: {flight_data['callsign']} {flight_data['origin']}->"
                    f"{flight_data['destination']} on {flight_data['aircraft']}")

    return flight_data


def get_current_flight() -> dict:
    """Get current overhead flight with full details and bearing

    Returns:
        Flight data dictionary with distance and bearing, or None
    """
    flight_id, distance, bearing = get_flight_search()

    if not flight_id:
        return None

    flight_data = get_flight_details(flight_id)

    if flight_data:
        flight_data["distance"] = distance
        flight_data["bearing"] = bearing

        # Cache flight data
        try:
            with open(CACHE_FILE, "w") as f:
                json.dump(flight_data, f)
        except Exception as e:
            logger.warning(f"Failed to cache flight data: {e}")

    return flight_data


# ============================================================================
# DISPLAY RENDERING
# ============================================================================

def draw_quote(quote_text: str, author: str) -> Image.Image:
    """Draw aviation quote full screen

    Args:
        quote_text: Quote text (multiline)
        author: Quote author

    Returns:
        PIL Image object
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_quote = get_font_preset('body')
    f_author = get_font_preset('subtitle')

    draw.text((10, 15), quote_text, font=f_quote, fill=0)
    draw.text((10, 100), f"— {author}", font=f_author, fill=0)

    return img


def draw_flight_portal(flight_data: dict, animation_frame: int = 0, input_mode: str = "touch") -> Image.Image:
    """Draw flight info portal with compass

    Split screen layout: info left, compass right.
    Animated cycling between flight info and flight data.

    Args:
        flight_data: Flight data dictionary or None
        animation_frame: Current animation frame
        input_mode: Input mode - "touch" or "button"

    Returns:
        PIL Image object
    """
    img = Image.new("1", (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_large = get_font_preset('title')
    f_medium = get_font_preset('body')
    f_medium_bold = get_font_preset('subtitle')
    f_small = get_font_preset('small')
    f_tiny = get_font_preset('tiny')

    if not flight_data:
        draw.text((30, 50), "No flights overhead", font=f_medium, fill=0)
        if input_mode == "button":
            draw.text((140, 110), "Hold: Exit", font=f_small, fill=0)
        else:
            draw.text((170, 110), "Touch=Exit", font=f_small, fill=0)
        return img

    # Center divider
    draw.line([(125, 0), (125, 122)], fill=0, width=1)

    # Right Panel: Compass rose with bearing arrow
    draw_compass_icon(
        draw,
        x=187,
        y=61,
        direction=flight_data.get("bearing", 0),
        size=45,
        color=0,
        user_heading=310
    )
    draw.text((135, 5), f"Live {flight_data['timestamp']}", font=f_small, fill=0)

    # Input mode specific instructions
    if input_mode == "button":
        draw.text((135, 102), "Press: Next", font=f_tiny, fill=0)
        draw.text((135, 112), "Hold: Exit", font=f_tiny, fill=0)
    else:
        draw.text((135, 110), "Touch=Exit", font=f_small, fill=0)

    # Left Panel: Flight info with animation cycling
    draw.text((5, 5), flight_data["callsign"], font=f_large, fill=0)

    cycle = animation_frame % 2

    if cycle == 0:
        # Frame 0: Route and airline
        route = f"{flight_data['origin']}->{flight_data['destination']}"
        draw.text((5, 35), route, font=f_medium, fill=0)

        airline = flight_data.get("airline", "")
        if airline and len(airline) > 12:
            airline = airline[:12]
        draw.text((5, 55), airline or flight_data['aircraft'], font=f_medium, fill=0)

    else:
        # Frame 1: Altitude and speed
        if flight_data["altitude"] > 0:
            draw.text((5, 35), f"Alt: {flight_data['altitude']:,} ft", font=f_medium, fill=0)
        else:
            draw.text((5, 35), flight_data['aircraft'], font=f_medium, fill=0)

        if flight_data["speed"] > 0:
            draw.text((5, 55), f"Speed: {flight_data['speed']} kts", font=f_medium, fill=0)
        else:
            draw.text((5, 55), "On Ground", font=f_medium, fill=0)

    # Distance and bearing (bold for prominence)
    draw.text((5, 85), f"Dist: {flight_data.get('distance', 0):.1f} km",
              font=f_medium_bold, fill=0)
    draw.text((5, 105), f"Bear: {flight_data.get('bearing', 0):.0f}°",
              font=f_medium_bold, fill=0)

    # Position indicator (Frame X of 2)
    if input_mode == "button":
        current_frame = (cycle % 2) + 1
        draw.text((3, 112), f"View {current_frame}/2", font=f_tiny, fill=0)

    return img


# ============================================================================
# MAIN APPLICATION LOOP
# ============================================================================

def run_flights_app(epd, gt_dev, gt_old, gt):
    """Main flights display application

    Args:
        epd: E-ink display driver
        gt_dev: Touch device state
        gt_old: Previous touch state
        gt: Touch controller
    """
    try:
        _run_flights_app_impl(epd, gt_dev, gt_old, gt)
    except Exception as e:
        logger.error(f"Flights app crashed: {e}", exc_info=True)
        img = Image.new("1", (250, 122), 255)
        draw = ImageDraw.Draw(img)
        f = get_font_preset('body')
        error_text = f"Error: {str(e)[:30]}"
        draw.text((10, 50), error_text, font=f, fill=0)
        epd.displayPartial(epd.getbuffer(img))
        time.sleep(5)


def _run_flights_app_impl(epd, gt_dev, gt_old, gt):
    """Internal implementation of flights app

    Manages three states:
    1. Quote intro (10 seconds)
    2. Quote cycle (if no flights)
    3. Flight display with animation
    """

    # Initialize input handler (auto-detects touch or button mode)
    handler = create_input_handler(gt=gt, gt_dev=gt_dev, gt_old=gt_old)
    input_mode = handler.mode
    logger.info(f"Flights app using {input_mode} input mode")

    # State for exit request
    exit_requested = [False]

    def request_exit():
        """Handle exit request from input"""
        logger.info(f"Exit requested via {input_mode} input")
        exit_requested[0] = True

    # Set up exit callback (long press or touch depending on mode)
    if input_mode == "button":
        handler.on_long_press = request_exit
    else:
        handler.on_touch = request_exit

    handler.start()

    try:
        # Initialize timers
        update_timer = PeriodicTimer(UPDATE_INTERVAL)
        animation_timer = PeriodicTimer(ANIMATION_CYCLE_INTERVAL)
        quote_timer = PeriodicTimer(QUOTE_INTERVAL)

        animation_frame = 0
        quote_index = random.randint(0, len(AVIATION_QUOTES) - 1)

        # Show initial quote
        quote_text, author = AVIATION_QUOTES[quote_index]
        quote_img = draw_quote(quote_text, author)
        epd.displayPartial(epd.getbuffer(quote_img))

        quote_start = time.time()
        flight_data = None

        # Quote intro phase (10 seconds)
        while time.time() - quote_start < 10:
            if input_mode == "touch":
                gt.GT_Scan(gt_dev, gt_old)

            if check_exit_requested(gt_dev) or exit_requested[0]:
                logger.info("Exit requested during quote intro")
                handler.stop()
                return

            # Legacy touch check for compatibility
            if input_mode == "touch":
                if gt_old.X[0] == gt_dev.X[0] and gt_old.Y[0] == gt_dev.Y[0] and gt_old.S[0] == gt_dev.S[0]:
                    time.sleep(0.1)
                    continue

                if gt_dev.TouchpointFlag:
                    gt_dev.TouchpointFlag = 0
                    logger.info("Exiting during quote display")
                    cleanup_touch_state(gt_old)
                    handler.stop()
                    return

            time.sleep(0.1)

        # Try to get current flight
        flight_data = get_current_flight()

        if not flight_data:
            logger.info("No flights - starting quote cycle mode (every 30 min)")
            _quote_cycle_mode(epd, gt, gt_dev, gt_old, handler, exit_requested, quote_index, AVIATION_QUOTES, input_mode)
            return

        # Flight display mode
        _flight_display_mode(
            epd,
            gt,
            gt_dev,
            gt_old,
            handler,
            exit_requested,
            flight_data,
            animation_frame,
            update_timer,
            animation_timer,
            quote_timer,
            quote_index,
            AVIATION_QUOTES,
            input_mode)

    finally:
        handler.stop()


def _quote_cycle_mode(epd, gt, gt_dev, gt_old, handler, exit_requested, quote_index, quotes, input_mode):
    """Display quotes when no flights are available

    Cycles through aviation quotes every 30 minutes, checking periodically
    for overhead flights.

    Args:
        epd: E-ink display driver
        gt: Touch controller
        gt_dev: Touch device state
        gt_old: Previous touch state
        handler: InputHandler instance
        exit_requested: List with exit flag
        quote_index: Current quote index
        quotes: List of quotes
        input_mode: Input mode ("touch" or "button")
    """
    quote_timer = PeriodicTimer(1800)  # 30 min

    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)

    quote_text, author = quotes[quote_index]
    quote_img = draw_quote(quote_text, author)
    epd.displayPartBaseImage(epd.getbuffer(quote_img))
    epd.init(epd.PART_UPDATE)

    logger.info(f"Showing quote {quote_index}: {author}")
    quote_index = (quote_index + 1) % len(quotes)

    while True:
        if input_mode == "touch":
            gt.GT_Scan(gt_dev, gt_old)

        if check_exit_requested(gt_dev) or exit_requested[0]:
            logger.info("Exit requested in quote cycle mode")
            return

        # Check if time to show next quote
        if quote_timer.is_ready():
            logger.info(f"30 min elapsed, showing next quote {quote_index}")

            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)

            quote_text, author = quotes[quote_index]
            quote_img = draw_quote(quote_text, author)
            epd.displayPartBaseImage(epd.getbuffer(quote_img))
            epd.init(epd.PART_UPDATE)

            quote_index = (quote_index + 1) % len(quotes)

            # Check for flights
            logger.info("Checking for flights...")
            flight_data = get_current_flight()
            if flight_data:
                logger.info(f"Flight found: {flight_data.get('callsign')}, "
                            "exiting quote mode")
                return
            else:
                logger.info("Still no flights, continuing quote cycle")

        # Legacy touch check for compatibility
        if input_mode == "touch":
            if gt_old.X[0] == gt_dev.X[0] and gt_old.Y[0] == gt_dev.Y[0] and gt_old.S[0] == gt_dev.S[0]:
                time.sleep(0.1)
                continue

            if gt_dev.TouchpointFlag:
                gt_dev.TouchpointFlag = 0
                logger.info("Exiting quote cycle mode")
                cleanup_touch_state(gt_old)
                return

        time.sleep(0.1)


def _flight_display_mode(epd, gt, gt_dev, gt_old, handler, exit_requested, flight_data, animation_frame,
                         update_timer, animation_timer, quote_timer, quote_index, quotes, input_mode):
    """Display flight info with animated cycling and periodic quotes

    Three periodic operations:
    - Quote display every QUOTE_INTERVAL (300s)
    - Flight update check every UPDATE_INTERVAL (30s)
    - Animation frame change every ANIMATION_CYCLE_INTERVAL (10s) in touch mode
    - In button mode, short press advances frame manually

    Args:
        epd: E-ink display driver
        gt: Touch controller
        gt_dev: Touch device state
        gt_old: Previous touch state
        handler: InputHandler instance
        exit_requested: List with exit flag
        flight_data: Current flight data
        animation_frame: Current animation frame
        update_timer: Timer for flight updates
        animation_timer: Timer for auto-animation (touch mode)
        quote_timer: Timer for quote display
        quote_index: Current quote index
        quotes: List of quotes
        input_mode: Input mode ("touch" or "button")
    """

    # State for manual frame advance in button mode
    frame_update_needed = [False]

    def advance_frame():
        """Callback for short press in button mode"""
        nonlocal animation_frame
        animation_frame += 1
        frame_update_needed[0] = True
        logger.info(f"Manual frame advance to {animation_frame}")

    # Set up short press callback for button mode
    if input_mode == "button":
        handler.on_short_press = advance_frame

    image = draw_flight_portal(flight_data, animation_frame, input_mode)
    epd.displayPartial(epd.getbuffer(image))

    quote_index = (quote_index + 1) % len(quotes)
    update_timer.reset()
    animation_timer.reset()
    quote_timer.reset()

    logger.info(f"Flights app started in {input_mode} mode")

    while True:
        if input_mode == "touch":
            gt.GT_Scan(gt_dev, gt_old)

        if check_exit_requested(gt_dev) or exit_requested[0]:
            logger.info("Exit requested from flight display")
            if input_mode == "touch":
                cleanup_touch_state(gt_old)
            return

        # Handle manual frame update in button mode
        if input_mode == "button" and frame_update_needed[0]:
            frame_update_needed[0] = False
            image = draw_flight_portal(flight_data, animation_frame, input_mode)
            epd.displayPartial(epd.getbuffer(image))

        # Quote display cycle
        if quote_timer.is_ready():
            logger.info(f"Showing quote {quote_index}")

            epd.init(epd.FULL_UPDATE)
            epd.Clear(0xFF)

            quote_text, author = quotes[quote_index]
            quote_img = draw_quote(quote_text, author)
            epd.displayPartBaseImage(epd.getbuffer(quote_img))
            epd.init(epd.PART_UPDATE)
            time.sleep(10)

            flight_data = get_current_flight()
            if flight_data:
                image = draw_flight_portal(flight_data, 0, input_mode)
                epd.displayPartial(epd.getbuffer(image))

            quote_index = (quote_index + 1) % len(quotes)
            update_timer.reset()
            animation_timer.reset()

        # Flight update cycle
        elif update_timer.is_ready():
            logger.info("Checking for new flight")
            new_flight = get_current_flight()

            if new_flight:
                flight_data = new_flight
                animation_frame = 0
                image = draw_flight_portal(flight_data, animation_frame, input_mode)
                epd.displayPartial(epd.getbuffer(image))

            animation_timer.reset()

        # Animation frame cycle (auto-advance in touch mode only)
        elif input_mode == "touch" and animation_timer.is_ready():
            animation_frame += 1
            image = draw_flight_portal(flight_data, animation_frame, input_mode)
            epd.displayPartial(epd.getbuffer(image))

        # Legacy touch input handling
        if input_mode == "touch":
            if gt_old.X[0] == gt_dev.X[0] and gt_old.Y[0] == gt_dev.Y[0] and gt_old.S[0] == gt_dev.S[0]:
                time.sleep(0.01)
                continue

            if gt_dev.TouchpointFlag:
                gt_dev.TouchpointFlag = 0
                logger.info("Exiting flights app via touch")
                cleanup_touch_state(gt_old)
                break

        time.sleep(0.01)
