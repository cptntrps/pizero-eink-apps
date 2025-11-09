"""
Icon Library
============

Provides reusable icon drawing functions for common UI elements.
All icons are designed for 1-bit e-ink display rendering.
"""

import math
from typing import Optional
from PIL import ImageDraw


# ============================================================================
# MEDICINE ICONS
# ============================================================================

def draw_pill_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int = 10,
    color: int = 0
) -> None:
    """Draw a simple pill/capsule icon

    Args:
        draw: PIL ImageDraw object
        x: Left X coordinate
        y: Top Y coordinate
        size: Icon size in pixels (default: 10)
        color: Icon color (default: 0 for black)

    Example:
        >>> draw_pill_icon(draw, 10, 20, size=15)
    """
    # Capsule shape with dividing line
    draw.ellipse([x, y, x + size, y + size], outline=color, width=2)
    draw.line([x + size // 4, y, x + size // 4, y + size], fill=color, width=1)


def draw_food_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int = 8,
    color: int = 0
) -> None:
    """Draw a simple fork icon for 'with food' indication

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Top Y coordinate
        size: Icon height in pixels (default: 8)
        color: Icon color (default: 0 for black)

    Example:
        >>> draw_food_icon(draw, 20, 30, size=10)
    """
    # Fork with handle and tines
    draw.line([x, y, x, y + size], fill=color, width=1)
    draw.line([x - 1, y, x - 1, y + size // 2], fill=color, width=1)
    draw.line([x + 1, y, x + 1, y + size // 2], fill=color, width=1)


def draw_checkmark(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int = 10,
    color: int = 0,
    width: int = 2
) -> None:
    """Draw a checkmark/tick icon

    Args:
        draw: PIL ImageDraw object
        x: Left X coordinate
        y: Top Y coordinate
        size: Icon size in pixels (default: 10)
        color: Icon color (default: 0 for black)
        width: Line width (default: 2)

    Example:
        >>> draw_checkmark(draw, 15, 25, size=12)
    """
    # Checkmark shape
    mid_x = x + size // 3
    mid_y = y + size * 2 // 3

    # Left stroke
    draw.line([x, y + size // 2, mid_x, mid_y], fill=color, width=width)
    # Right stroke
    draw.line([mid_x, mid_y, x + size, y], fill=color, width=width)


# ============================================================================
# POMODORO ICONS
# ============================================================================

def draw_tomato_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    frame: int = 1,
    size: int = 30,
    color: int = 0
) -> None:
    """Draw animated tomato icon for Pomodoro timer

    Supports two animation frames for working state.

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        frame: Animation frame (1 or 2)
        size: Tomato diameter in pixels (default: 30)
        color: Icon color (default: 0 for black)

    Example:
        >>> # Animated tomato
        >>> draw_tomato_icon(draw, 125, 60, frame=1, size=40)
    """
    radius = size // 2

    # Tomato body (circle)
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=color,
        width=2
    )

    # Leaf/stem on top
    stem_size = radius // 3
    draw.polygon(
        [(x - stem_size, y - radius),
         (x, y - radius - stem_size),
         (x + stem_size, y - radius)],
        outline=color,
        fill=color
    )

    # Eyes and expression change by frame
    eye_offset = radius // 3
    eye_y = y - radius // 4
    eye_size = radius // 5

    if frame == 1:
        # Happy/excited eyes (open)
        draw.ellipse(
            [x - eye_offset - eye_size, eye_y - eye_size,
             x - eye_offset + eye_size, eye_y + eye_size],
            outline=color,
            fill=color
        )
        draw.ellipse(
            [x + eye_offset - eye_size, eye_y - eye_size,
             x + eye_offset + eye_size, eye_y + eye_size],
            outline=color,
            fill=color
        )
        # Wide smile
        draw.arc(
            [x - radius // 2, y - radius // 4, x + radius // 2, y + radius // 2],
            0, 180,
            fill=color,
            width=2
        )
    else:
        # Focused eyes (lines)
        draw.line(
            [x - eye_offset - eye_size, eye_y, x - eye_offset + eye_size, eye_y],
            fill=color,
            width=2
        )
        draw.line(
            [x + eye_offset - eye_size, eye_y, x + eye_offset + eye_size, eye_y],
            fill=color,
            width=2
        )
        # Small smile
        draw.arc(
            [x - radius // 3, y, x + radius // 3, y + radius // 3],
            0, 180,
            fill=color,
            width=2
        )


# ============================================================================
# WEATHER ICONS
# ============================================================================

def draw_weather_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    condition: str,
    size: int = 30,
    color: int = 0
) -> None:
    """Draw weather condition icon

    Supported conditions: 'sun', 'clouds', 'rain', 'snow', 'storm'

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        condition: Weather condition name
        size: Icon size in pixels (default: 30)
        color: Icon color (default: 0 for black)

    Example:
        >>> draw_weather_icon(draw, 50, 50, 'rain', size=40)
    """
    condition = condition.lower()

    if condition in ['sun', 'clear']:
        _draw_sun_icon(draw, x, y, size, color)
    elif condition in ['clouds', 'cloudy', 'overcast']:
        _draw_cloud_icon(draw, x, y, size, color)
    elif condition in ['rain', 'rainy', 'drizzle']:
        _draw_rain_icon(draw, x, y, size, color)
    elif condition in ['snow', 'snowy']:
        _draw_snow_icon(draw, x, y, size, color)
    elif condition in ['storm', 'thunderstorm']:
        _draw_storm_icon(draw, x, y, size, color)
    else:
        # Default: question mark
        _draw_cloud_icon(draw, x, y, size, color)


def _draw_sun_icon(draw, x, y, size, color):
    """Draw sun icon"""
    radius = size // 3

    # Sun circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=color,
        width=2
    )

    # Sun rays (8 directions)
    ray_length = size // 6
    for angle in range(0, 360, 45):
        angle_rad = math.radians(angle)
        x1 = x + int((radius + 2) * math.cos(angle_rad))
        y1 = y + int((radius + 2) * math.sin(angle_rad))
        x2 = x + int((radius + ray_length + 2) * math.cos(angle_rad))
        y2 = y + int((radius + ray_length + 2) * math.sin(angle_rad))
        draw.line([x1, y1, x2, y2], fill=color, width=2)


def _draw_cloud_icon(draw, x, y, size, color):
    """Draw cloud icon"""
    # Cloud made of overlapping circles
    r1 = size // 4
    r2 = size // 3
    r3 = size // 5

    draw.ellipse([x - r2, y - r1, x + r2, y + r1], outline=color, width=2)
    draw.ellipse([x - r2 - r3, y - r3, x - r2 + r3, y + r3], outline=color, width=2)
    draw.ellipse([x + r2 - r3, y - r3, x + r2 + r3, y + r3], outline=color, width=2)


def _draw_rain_icon(draw, x, y, size, color):
    """Draw rain icon (cloud + raindrops)"""
    # Cloud
    _draw_cloud_icon(draw, x, y - size // 6, size * 2 // 3, color)

    # Raindrops
    drop_spacing = size // 5
    for i in range(3):
        drop_x = x - drop_spacing + i * drop_spacing
        drop_y = y + size // 4
        draw.line([drop_x, drop_y, drop_x, drop_y + size // 5], fill=color, width=2)


def _draw_snow_icon(draw, x, y, size, color):
    """Draw snow icon (cloud + snowflakes)"""
    # Cloud
    _draw_cloud_icon(draw, x, y - size // 6, size * 2 // 3, color)

    # Snowflakes (asterisks)
    flake_spacing = size // 5
    for i in range(3):
        flake_x = x - flake_spacing + i * flake_spacing
        flake_y = y + size // 4
        flake_size = size // 10
        # Cross
        draw.line([flake_x - flake_size, flake_y, flake_x + flake_size, flake_y],
                  fill=color, width=1)
        draw.line([flake_x, flake_y - flake_size, flake_x, flake_y + flake_size],
                  fill=color, width=1)


def _draw_storm_icon(draw, x, y, size, color):
    """Draw storm icon (cloud + lightning)"""
    # Cloud
    _draw_cloud_icon(draw, x, y - size // 6, size * 2 // 3, color)

    # Lightning bolt
    bolt_top = y + size // 6
    bolt_height = size // 3
    draw.polygon([
        (x, bolt_top),
        (x - size // 8, bolt_top + bolt_height // 2),
        (x + size // 16, bolt_top + bolt_height // 2),
        (x - size // 16, bolt_top + bolt_height)
    ], outline=color, fill=color)


# ============================================================================
# FLIGHT/COMPASS ICONS
# ============================================================================

def draw_compass_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    direction: float,
    size: int = 20,
    color: int = 0,
    user_heading: float = 0
) -> None:
    """Draw compass rose with directional arrow

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        direction: Direction in degrees (0 = North, 90 = East)
        size: Compass radius in pixels (default: 20)
        color: Icon color (default: 0 for black)
        user_heading: User's heading for rotation (default: 0 = North up)

    Example:
        >>> draw_compass_icon(draw, 125, 61, 45, size=30)  # NE direction
    """
    radius = size

    # Outer circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=color,
        width=2
    )

    # Cardinal marks (N, E, S, W)
    cardinals = [
        (0, "N"), (90, "E"), (180, "S"), (270, "W")
    ]

    for angle, _ in cardinals:
        rotated_angle = angle - user_heading
        angle_rad = math.radians(rotated_angle - 90)

        x1 = x + int((radius - 5) * math.cos(angle_rad))
        y1 = y + int((radius - 5) * math.sin(angle_rad))
        x2 = x + int(radius * math.cos(angle_rad))
        y2 = y + int(radius * math.sin(angle_rad))
        draw.line([x1, y1, x2, y2], fill=color, width=2)

    # Direction arrow
    rotated_direction = direction - user_heading
    arrow_rad = math.radians(rotated_direction - 90)
    arrow_len = radius - 5

    # Arrow point
    ax = x + int(arrow_len * math.cos(arrow_rad))
    ay = y + int(arrow_len * math.sin(arrow_rad))

    # Arrowhead
    tip1_rad = arrow_rad + math.radians(150)
    tip2_rad = arrow_rad - math.radians(150)
    tx1 = ax + int(5 * math.cos(tip1_rad))
    ty1 = ay + int(5 * math.sin(tip1_rad))
    tx2 = ax + int(5 * math.cos(tip2_rad))
    ty2 = ay + int(5 * math.sin(tip2_rad))

    draw.line([x, y, ax, ay], fill=color, width=2)
    draw.polygon([(ax, ay), (tx1, ty1), (tx2, ty2)], outline=color, fill=color)


def draw_airplane_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int = 20,
    color: int = 0,
    angle: float = 0  # pylint: disable=unused-argument
) -> None:
    """Draw airplane icon

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        size: Icon size in pixels (default: 20)
        color: Icon color (default: 0 for black)
        angle: Rotation angle in degrees (default: 0 = pointing up)
               (Currently not implemented - reserved for future use)

    Example:
        >>> draw_airplane_icon(draw, 100, 50, size=25, angle=45)
    """
    # Simplified airplane shape
    # Fuselage
    draw.line([x, y - size // 2, x, y + size // 2], fill=color, width=3)

    # Wings
    wing_width = size // 2
    wing_y = y
    draw.line([x - wing_width, wing_y, x + wing_width, wing_y], fill=color, width=2)

    # Tail
    tail_width = size // 3
    tail_y = y + size // 3
    draw.line([x - tail_width, tail_y, x + tail_width, tail_y], fill=color, width=2)


# ============================================================================
# UI ICONS
# ============================================================================

def draw_battery_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    level: int,
    size: int = 20,
    color: int = 0
) -> None:
    """Draw battery level icon

    Args:
        draw: PIL ImageDraw object
        x: Left X coordinate
        y: Top Y coordinate
        level: Battery level 0-100
        size: Icon width in pixels (default: 20)
        color: Icon color (default: 0 for black)

    Example:
        >>> draw_battery_icon(draw, 200, 5, level=75, size=25)
    """
    height = size // 2

    # Battery outline
    draw.rectangle([x, y, x + size, y + height], outline=color, width=1)

    # Battery terminal
    terminal_width = 2
    draw.rectangle(
        [x + size, y + height // 3, x + size + terminal_width, y + 2 * height // 3],
        outline=color,
        fill=color
    )

    # Fill level
    fill_width = int((size - 4) * level / 100)
    if fill_width > 0:
        draw.rectangle(
            [x + 2, y + 2, x + 2 + fill_width, y + height - 2],
            outline=color,
            fill=color
        )


def draw_wifi_icon(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    strength: int,
    size: int = 15,
    color: int = 0
) -> None:
    """Draw WiFi signal strength icon

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Bottom Y coordinate
        strength: Signal strength 0-3 (bars)
        size: Icon size in pixels (default: 15)
        color: Icon color (default: 0 for black)

    Example:
        >>> draw_wifi_icon(draw, 220, 15, strength=2, size=12)
    """
    # WiFi signal arcs
    for i in range(min(strength, 3)):
        radius = (i + 1) * size // 3
        draw.arc(
            [x - radius, y - radius, x + radius, y + radius],
            180, 360,
            fill=color,
            width=2
        )

    # Center dot
    draw.ellipse([x - 1, y - 1, x + 1, y + 1], outline=color, fill=color)
