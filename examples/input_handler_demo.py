#!/usr/bin/python3
"""
Input Handler Demo
==================

Demonstrates the unified input abstraction system supporting both
touchscreen and button input modes.

This example shows:
1. Auto-detection of input hardware
2. Callback-based event handling
3. Mode-specific features
4. Factory pattern usage
5. Context manager support

Hardware Modes:
- Touch Mode: Waveshare 2.13" with GT1151 touchscreen
- Button Mode: GPIO button (default: GPIO 3, PiSugar)

Usage:
    # Auto-detect mode
    python3 examples/input_handler_demo.py

    # Force button mode (for testing without hardware)
    python3 examples/input_handler_demo.py --button

    # With config file
    python3 examples/input_handler_demo.py --config config.json
"""

import sys
import os
import time
import signal
import logging
import argparse

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, project_root)

from display import (
    create_input_handler,
    InputHandler,
    InputEvent,
    detect_input_mode,
    get_input_info,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# EXAMPLE 1: BASIC USAGE WITH AUTO-DETECTION
# ============================================================================

def example_basic():
    """Basic usage example with auto-detection"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Auto-Detection")
    print("="*60 + "\n")

    # Create handler (auto-detects hardware)
    # For button mode, defaults to GPIO 3 (PiSugar)
    handler = create_input_handler()

    # Display handler info
    info = get_input_info(handler)
    print(f"Input Mode: {info['mode']}")
    print(f"Handler Type: {info['type']}")
    print(f"Active: {info['active']}")
    print()

    # Setup callbacks
    handler.on_short_press = lambda: print("⚡ SHORT PRESS detected!")
    handler.on_long_press = lambda: print("🔥 LONG PRESS detected!")

    # Touch-specific callbacks (ignored in button mode)
    handler.on_touch = lambda: print("👆 TOUCH detected!")
    handler.on_coordinates = lambda x, y: print(f"📍 TAP at coordinates ({x}, {y})")

    print("Handler configured. Press button or touch screen...")
    print("(Will run for 30 seconds)\n")

    # Use context manager for automatic start/stop
    with handler:
        # Run for 30 seconds
        start_time = time.time()
        while time.time() - start_time < 30:
            time.sleep(0.1)

    print("\nHandler stopped automatically.")


# ============================================================================
# EXAMPLE 2: EXPLICIT BUTTON MODE
# ============================================================================

def example_button_mode():
    """Explicit button mode example"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Explicit Button Mode")
    print("="*60 + "\n")

    from display import ButtonInputHandler

    # Create button handler directly
    handler = ButtonInputHandler(
        gpio_pin=3,
        long_press_threshold=2.0,
        bounce_time=0.1
    )

    print(f"Mode: {handler.mode}")
    print(f"GPIO Pin: {handler.gpio_pin}")
    print(f"Long Press Threshold: {handler.long_press_threshold}s")
    print()

    # Event counter
    event_count = {"short": 0, "long": 0}

    def on_short():
        event_count["short"] += 1
        print(f"✓ Short press #{event_count['short']}")

    def on_long():
        event_count["long"] += 1
        print(f"⏱ Long press #{event_count['long']}")

    handler.on_short_press = on_short
    handler.on_long_press = on_long

    print("Press button to test...")
    print("(Will run for 30 seconds)\n")

    handler.start()
    try:
        start_time = time.time()
        while time.time() - start_time < 30:
            time.sleep(0.1)
    finally:
        handler.stop()

    print(f"\nTotal events: {event_count['short']} short, {event_count['long']} long")


# ============================================================================
# EXAMPLE 3: TOUCH MODE (requires hardware)
# ============================================================================

def example_touch_mode():
    """Touch mode example (requires GT1151 hardware)"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Touch Mode (Requires Hardware)")
    print("="*60 + "\n")

    try:
        # Import GT driver (will fail if not on Pi with touchscreen)
        from TP_lib import gt1151
        from display import TouchInputHandler

        # Initialize GT driver
        gt = gt1151.GT1151()
        gt_dev = gt1151.GT_Development()
        gt_old = gt1151.GT_Development()

        # Create touch handler
        handler = TouchInputHandler(
            gt=gt,
            gt_dev=gt_dev,
            gt_old=gt_old,
            polling_interval=0.01,
            tap_max_duration=0.5
        )

        print(f"Mode: {handler.mode}")
        print(f"Polling Interval: {handler.polling_interval}s")
        print(f"Tap Max Duration: {handler.tap_max_duration}s")
        print()

        # Touch event tracking
        touch_events = []

        def on_tap(x, y):
            touch_events.append((x, y))
            print(f"📍 TAP at ({x:3d}, {y:3d}) - Total taps: {len(touch_events)}")

        def on_touch():
            state = handler.get_touch_state()
            print(f"👆 TOUCH - X:{state['x']}, Y:{state['y']}, Size:{state['size']}")

        handler.on_coordinates = on_tap
        handler.on_touch = on_touch

        print("Touch the screen to test...")
        print("(Will run for 30 seconds)\n")

        with handler:
            start_time = time.time()
            while time.time() - start_time < 30:
                time.sleep(0.1)

        print(f"\nTotal touch events: {len(touch_events)}")

    except ImportError as e:
        print(f"❌ Touch hardware not available: {e}")
        print("   This example requires GT1151 driver and hardware")


# ============================================================================
# EXAMPLE 4: FACTORY WITH CONFIG
# ============================================================================

def example_with_config():
    """Factory usage with configuration"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Factory with Configuration")
    print("="*60 + "\n")

    # Sample configuration
    config = {
        "hardware": {
            "button": {
                "enabled": True,
                "gpio_pin": 3,
                "long_press_threshold": 2.0,
                "bounce_time": 0.1,
                "pull_up": True
            },
            "touch": {
                "enabled": False,
                "driver": "GT1151"
            }
        }
    }

    print("Configuration:")
    print(f"  Button enabled: {config['hardware']['button']['enabled']}")
    print(f"  Touch enabled: {config['hardware']['touch']['enabled']}")
    print()

    # Detect mode from config
    mode = detect_input_mode(config)
    print(f"Detected mode: {mode}\n")

    # Create handler from config
    handler = create_input_handler(config=config)

    info = get_input_info(handler)
    print(f"Created handler:")
    print(f"  Type: {info['type']}")
    print(f"  Mode: {info['mode']}")
    print(f"  Active: {info['active']}")
    print()

    handler.on_short_press = lambda: print("✓ Event triggered!")

    print("Running with config-based handler...")
    print("(Will run for 10 seconds)\n")

    with handler:
        time.sleep(10)

    print("Done.")


# ============================================================================
# EXAMPLE 5: COMPREHENSIVE EVENT DEMO
# ============================================================================

def example_comprehensive():
    """Comprehensive event handling demo"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Comprehensive Event Handling")
    print("="*60 + "\n")

    handler = create_input_handler()

    # Event statistics
    stats = {
        "short_press": 0,
        "long_press": 0,
        "touch": 0,
        "coordinates": []
    }

    def on_short_press():
        stats["short_press"] += 1
        print(f"[{time.strftime('%H:%M:%S')}] SHORT PRESS - Count: {stats['short_press']}")

    def on_long_press():
        stats["long_press"] += 1
        print(f"[{time.strftime('%H:%M:%S')}] LONG PRESS - Count: {stats['long_press']}")

    def on_touch():
        stats["touch"] += 1
        print(f"[{time.strftime('%H:%M:%S')}] TOUCH - Count: {stats['touch']}")

    def on_coordinates(x, y):
        stats["coordinates"].append((x, y))
        print(f"[{time.strftime('%H:%M:%S')}] COORDINATES ({x}, {y}) - Total: {len(stats['coordinates'])}")

    # Register all callbacks
    handler.on_short_press = on_short_press
    handler.on_long_press = on_long_press
    handler.on_touch = on_touch
    handler.on_coordinates = on_coordinates

    print(f"Handler mode: {handler.mode}")
    print("All callbacks registered.")
    print("\nInteract with input device...")
    print("(Will run for 60 seconds)\n")

    # Setup signal handler for graceful exit
    running = [True]

    def signal_handler(sig, frame):
        print("\n\nInterrupted. Stopping...")
        running[0] = False

    signal.signal(signal.SIGINT, signal_handler)

    with handler:
        start_time = time.time()
        while running[0] and time.time() - start_time < 60:
            time.sleep(0.1)

    # Print statistics
    print("\n" + "="*60)
    print("EVENT STATISTICS")
    print("="*60)
    print(f"Short Presses: {stats['short_press']}")
    print(f"Long Presses: {stats['long_press']}")
    print(f"Touch Events: {stats['touch']}")
    print(f"Coordinate Events: {len(stats['coordinates'])}")
    if stats['coordinates']:
        print("\nCoordinates:")
        for i, (x, y) in enumerate(stats['coordinates'][:10], 1):
            print(f"  {i}. ({x}, {y})")
        if len(stats['coordinates']) > 10:
            print(f"  ... and {len(stats['coordinates']) - 10} more")
    print("="*60)


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Input Handler Demo")
    parser.add_argument(
        '--example',
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run specific example (1-5)"
    )
    parser.add_argument(
        '--button',
        action='store_true',
        help="Force button mode"
    )
    parser.add_argument(
        '--config',
        type=str,
        help="Path to config file"
    )

    args = parser.parse_args()

    print("\n" + "="*60)
    print("INPUT HANDLER DEMO")
    print("="*60)

    if args.example == 1:
        example_basic()
    elif args.example == 2:
        example_button_mode()
    elif args.example == 3:
        example_touch_mode()
    elif args.example == 4:
        example_with_config()
    elif args.example == 5:
        example_comprehensive()
    else:
        # Run all examples
        print("\nRunning all examples...\n")
        example_basic()
        example_button_mode()
        example_touch_mode()
        example_with_config()
        example_comprehensive()

    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
