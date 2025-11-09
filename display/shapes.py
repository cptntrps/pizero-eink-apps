"""
Primitive Shape Drawing
=======================

Provides consistent, high-level functions for drawing basic shapes.
Reduces boilerplate and ensures consistent styling.
"""

from typing import Optional
from PIL import ImageDraw
from .canvas import DISPLAY_WIDTH, DISPLAY_HEIGHT


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_COLOR = 0  # Black
DEFAULT_WIDTH = 1
DEFAULT_FILL = None


# ============================================================================
# BASIC SHAPES
# ============================================================================

def draw_line(
    draw: ImageDraw.ImageDraw,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a line between two points

    Args:
        draw: PIL ImageDraw object
        x1: Start X coordinate
        y1: Start Y coordinate
        x2: End X coordinate
        y2: End Y coordinate
        color: Line color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> img, draw = create_canvas()
        >>> draw_line(draw, 0, 0, 250, 122)  # Diagonal line
    """
    draw.line([(x1, y1), (x2, y2)], fill=color, width=width)


def draw_rectangle(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    outline: int = DEFAULT_COLOR,
    fill: Optional[int] = DEFAULT_FILL,
    border_width: int = DEFAULT_WIDTH
) -> None:
    """Draw a rectangle

    Args:
        draw: PIL ImageDraw object
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Rectangle width
        height: Rectangle height
        outline: Border color (default: 0 for black)
        fill: Fill color (default: None for transparent)
        border_width: Border width in pixels (default: 1)

    Example:
        >>> draw_rectangle(draw, 10, 10, 50, 30)  # Outlined box
        >>> draw_rectangle(draw, 10, 50, 50, 30, fill=0)  # Filled black box
    """
    coords = [x, y, x + width, y + height]
    draw.rectangle(coords, outline=outline, fill=fill, width=border_width)


def draw_circle(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    radius: int,
    outline: int = DEFAULT_COLOR,
    fill: Optional[int] = DEFAULT_FILL,
    border_width: int = DEFAULT_WIDTH
) -> None:
    """Draw a circle centered at (x, y)

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        radius: Circle radius in pixels
        outline: Border color (default: 0 for black)
        fill: Fill color (default: None for transparent)
        border_width: Border width in pixels (default: 1)

    Example:
        >>> draw_circle(draw, 125, 61, 30)  # Circle in display center
    """
    coords = [x - radius, y - radius, x + radius, y + radius]
    draw.ellipse(coords, outline=outline, fill=fill, width=border_width)


def draw_ellipse(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    outline: int = DEFAULT_COLOR,
    fill: Optional[int] = DEFAULT_FILL,
    border_width: int = DEFAULT_WIDTH
) -> None:
    """Draw an ellipse

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        width: Ellipse width (diameter on X axis)
        height: Ellipse height (diameter on Y axis)
        outline: Border color (default: 0 for black)
        fill: Fill color (default: None for transparent)
        border_width: Border width in pixels (default: 1)

    Example:
        >>> draw_ellipse(draw, 125, 61, 80, 40)  # Horizontal ellipse
    """
    half_w = width // 2
    half_h = height // 2
    coords = [x - half_w, y - half_h, x + half_w, y + half_h]
    draw.ellipse(coords, outline=outline, fill=fill, width=border_width)


def draw_polygon(
    draw: ImageDraw.ImageDraw,
    points: list,
    outline: int = DEFAULT_COLOR,
    fill: Optional[int] = DEFAULT_FILL,
    border_width: int = DEFAULT_WIDTH
) -> None:
    """Draw a polygon

    Args:
        draw: PIL ImageDraw object
        points: List of (x, y) tuples defining vertices
        outline: Border color (default: 0 for black)
        fill: Fill color (default: None for transparent)
        border_width: Border width in pixels (default: 1)

    Example:
        >>> # Draw triangle
        >>> points = [(125, 30), (100, 80), (150, 80)]
        >>> draw_polygon(draw, points, fill=0)
    """
    draw.polygon(points, outline=outline, fill=fill, width=border_width)


def draw_arc(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    radius: int,
    start_angle: float,
    end_angle: float,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw an arc (portion of circle)

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        radius: Arc radius in pixels
        start_angle: Start angle in degrees (0 = right, 90 = bottom)
        end_angle: End angle in degrees
        color: Arc color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> # Draw smile (arc from 0° to 180°)
        >>> draw_arc(draw, 125, 61, 20, 0, 180)
    """
    coords = [x - radius, y - radius, x + radius, y + radius]
    draw.arc(coords, start_angle, end_angle, fill=color, width=width)


# ============================================================================
# CONVENIENCE SHAPES
# ============================================================================

def draw_horizontal_line(
    draw: ImageDraw.ImageDraw,
    y: int,
    x1: int = 0,
    x2: Optional[int] = None,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a horizontal line spanning the display

    Args:
        draw: PIL ImageDraw object
        y: Y coordinate
        x1: Start X coordinate (default: 0)
        x2: End X coordinate (default: full width)
        color: Line color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> draw_horizontal_line(draw, 60)  # Line across middle
    """
    if x2 is None:
        x2 = DISPLAY_WIDTH

    draw.line([(x1, y), (x2, y)], fill=color, width=width)


def draw_vertical_line(
    draw: ImageDraw.ImageDraw,
    x: int,
    y1: int = 0,
    y2: Optional[int] = None,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a vertical line spanning the display

    Args:
        draw: PIL ImageDraw object
        x: X coordinate
        y1: Start Y coordinate (default: 0)
        y2: End Y coordinate (default: full height)
        color: Line color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> draw_vertical_line(draw, 125)  # Line down center
    """
    if y2 is None:
        y2 = DISPLAY_HEIGHT

    draw.line([(x, y1), (x, y2)], fill=color, width=width)


def draw_rounded_rectangle(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    radius: int,
    outline: int = DEFAULT_COLOR,
    fill: Optional[int] = DEFAULT_FILL,
    border_width: int = DEFAULT_WIDTH
) -> None:
    """Draw a rectangle with rounded corners

    Args:
        draw: PIL ImageDraw object
        x: Top-left X coordinate
        y: Top-left Y coordinate
        width: Rectangle width
        height: Rectangle height
        radius: Corner radius in pixels
        outline: Border color (default: 0 for black)
        fill: Fill color (default: None for transparent)
        border_width: Border width in pixels (default: 1)

    Example:
        >>> draw_rounded_rectangle(draw, 10, 10, 100, 50, 10)
    """
    coords = [x, y, x + width, y + height]
    draw.rounded_rectangle(
        coords,
        radius=radius,
        outline=outline,
        fill=fill,
        width=border_width
    )


# ============================================================================
# COMPOSITE SHAPES
# ============================================================================

def draw_frame(
    draw: ImageDraw.ImageDraw,
    padding: int = 2,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a frame around the entire display

    Args:
        draw: PIL ImageDraw object
        padding: Padding from edge in pixels (default: 2)
        color: Frame color (default: 0 for black)
        width: Frame width in pixels (default: 1)

    Example:
        >>> draw_frame(draw, padding=5, width=2)  # Thick border
    """
    draw.rectangle(
        [padding, padding, DISPLAY_WIDTH - padding, DISPLAY_HEIGHT - padding],
        outline=color,
        width=width
    )


def draw_divider(
    draw: ImageDraw.ImageDraw,
    y: int,
    padding: int = 0,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a horizontal divider line

    Common pattern for separating sections.

    Args:
        draw: PIL ImageDraw object
        y: Y coordinate
        padding: Horizontal padding from edges (default: 0)
        color: Line color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> draw_divider(draw, 18)  # Divider below header
    """
    draw_horizontal_line(draw, y, x1=padding, x2=DISPLAY_WIDTH - padding,
                         color=color, width=width)


def draw_cross(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    size: int,
    color: int = DEFAULT_COLOR,
    width: int = DEFAULT_WIDTH
) -> None:
    """Draw a cross/plus symbol

    Args:
        draw: PIL ImageDraw object
        x: Center X coordinate
        y: Center Y coordinate
        size: Cross size (radius from center)
        color: Cross color (default: 0 for black)
        width: Line width in pixels (default: 1)

    Example:
        >>> draw_cross(draw, 125, 61, 10)  # Small cross in center
    """
    draw_line(draw, x - size, y, x + size, y, color, width)
    draw_line(draw, x, y - size, x, y + size, color, width)
