"""
Text Rendering Utilities
=========================

Provides high-level text rendering functions including centering,
wrapping, truncation, and measurement.
"""

from typing import Tuple, Optional
from PIL import ImageDraw, ImageFont
from .canvas import DISPLAY_WIDTH, DISPLAY_HEIGHT


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_COLOR = 0  # Black
DEFAULT_TRUNCATE_SUFFIX = "..."


# ============================================================================
# TEXT MEASUREMENT
# ============================================================================

def get_text_size(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont
) -> Tuple[int, int]:
    """Get width and height of text

    Args:
        draw: PIL ImageDraw object
        text: Text to measure
        font: Font to use for measurement

    Returns:
        Tuple of (width, height) in pixels

    Example:
        >>> width, height = get_text_size(draw, "Hello", font)
        >>> print(f"Text is {width}px wide and {height}px tall")
    """
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    return width, height


def get_text_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont
) -> int:
    """Get width of text

    Args:
        draw: PIL ImageDraw object
        text: Text to measure
        font: Font to use

    Returns:
        int: Width in pixels

    Example:
        >>> width = get_text_width(draw, "Hello", font)
    """
    width, _ = get_text_size(draw, text, font)
    return width


def get_text_height(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont
) -> int:
    """Get height of text

    Args:
        draw: PIL ImageDraw object
        text: Text to measure
        font: Font to use

    Returns:
        int: Height in pixels

    Example:
        >>> height = get_text_height(draw, "Hello", font)
    """
    _, height = get_text_size(draw, text, font)
    return height


# ============================================================================
# TEXT POSITIONING
# ============================================================================

def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    width: Optional[int] = None
) -> Tuple[int, int]:
    """Draw text centered horizontally

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        y: Y coordinate (top of text)
        font: Font to use
        color: Text color (default: 0 for black)
        width: Width to center within (default: full display width)

    Returns:
        Tuple of (x, y): Position where text was drawn

    Example:
        >>> from display import fonts
        >>> font = fonts.get_font_preset('headline')
        >>> draw_centered_text(draw, "Hello World", y=50, font=font)
    """
    if width is None:
        width = DISPLAY_WIDTH

    text_width, _ = get_text_size(draw, text, font)
    x = (width - text_width) // 2

    draw.text((x, y), text, font=font, fill=color)
    return x, y


def draw_right_aligned_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    padding: int = 0
) -> Tuple[int, int]:
    """Draw text aligned to the right edge

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        y: Y coordinate (top of text)
        font: Font to use
        color: Text color (default: 0 for black)
        padding: Padding from right edge (default: 0)

    Returns:
        Tuple of (x, y): Position where text was drawn

    Example:
        >>> draw_right_aligned_text(draw, "12:34", y=5, font=font, padding=5)
    """
    text_width, _ = get_text_size(draw, text, font)
    x = DISPLAY_WIDTH - text_width - padding

    draw.text((x, y), text, font=font, fill=color)
    return x, y


def draw_centered_text_vertical(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    height: Optional[int] = None
) -> Tuple[int, int]:
    """Draw text centered vertically

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        x: X coordinate (left of text)
        font: Font to use
        color: Text color (default: 0 for black)
        height: Height to center within (default: full display height)

    Returns:
        Tuple of (x, y): Position where text was drawn

    Example:
        >>> draw_centered_text_vertical(draw, "Side", x=10, font=font)
    """
    if height is None:
        height = DISPLAY_HEIGHT

    _, text_height = get_text_size(draw, text, font)
    y = (height - text_height) // 2

    draw.text((x, y), text, font=font, fill=color)
    return x, y


def draw_centered_text_both(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> Tuple[int, int]:
    """Draw text centered both horizontally and vertically

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        font: Font to use
        color: Text color (default: 0 for black)
        width: Width to center within (default: full display width)
        height: Height to center within (default: full display height)

    Returns:
        Tuple of (x, y): Position where text was drawn

    Example:
        >>> draw_centered_text_both(draw, "Center", font=font)
    """
    if width is None:
        width = DISPLAY_WIDTH
    if height is None:
        height = DISPLAY_HEIGHT

    text_width, text_height = get_text_size(draw, text, font)
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, font=font, fill=color)
    return x, y


# ============================================================================
# TEXT WRAPPING
# ============================================================================

def wrap_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    font: ImageFont.FreeTypeFont
) -> list:
    """Wrap text to fit within maximum width

    Args:
        draw: PIL ImageDraw object
        text: Text to wrap
        max_width: Maximum width in pixels
        font: Font to use

    Returns:
        list: List of lines that fit within max_width

    Example:
        >>> lines = wrap_text(draw, "Long text here", 100, font)
        >>> for i, line in enumerate(lines):
        ...     draw.text((10, 10 + i * 15), line, font=font, fill=0)
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        width, _ = get_text_size(draw, test_line, font)

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    x: int,
    y: int,
    max_width: int,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    line_spacing: int = 2
) -> int:
    """Draw text with automatic wrapping

    Args:
        draw: PIL ImageDraw object
        text: Text to draw
        x: Left X coordinate
        y: Top Y coordinate
        max_width: Maximum width in pixels
        font: Font to use
        color: Text color (default: 0 for black)
        line_spacing: Extra spacing between lines (default: 2)

    Returns:
        int: Y coordinate after last line (useful for positioning next element)

    Example:
        >>> next_y = draw_wrapped_text(draw, "Long text...", 10, 20, 200, font)
        >>> draw.text((10, next_y + 5), "Next element", font=font, fill=0)
    """
    lines = wrap_text(draw, text, max_width, font)
    current_y = y

    for line in lines:
        draw.text((x, current_y), line, font=font, fill=color)
        _, line_height = get_text_size(draw, line, font)
        current_y += line_height + line_spacing

    return current_y


# ============================================================================
# TEXT TRUNCATION
# ============================================================================

def truncate_text(
    text: str,
    max_length: int,
    suffix: str = DEFAULT_TRUNCATE_SUFFIX
) -> str:
    """Truncate text to maximum length with suffix

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append (default: "...")

    Returns:
        str: Truncated text

    Example:
        >>> truncated = truncate_text("Very long text here", 10)
        >>> print(truncated)  # "Very lo..."
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def truncate_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    font: ImageFont.FreeTypeFont,
    suffix: str = DEFAULT_TRUNCATE_SUFFIX
) -> str:
    """Truncate text to fit within pixel width

    Args:
        draw: PIL ImageDraw object
        text: Text to truncate
        max_width: Maximum width in pixels
        font: Font to use
        suffix: Suffix to append (default: "...")

    Returns:
        str: Truncated text that fits within max_width

    Example:
        >>> text = truncate_text_to_width(draw, "Long name", 50, font)
        >>> draw.text((10, 10), text, font=font, fill=0)
    """
    width, _ = get_text_size(draw, text, font)

    if width <= max_width:
        return text

    # Binary search for optimal truncation point
    left, right = 0, len(text)

    while left < right:
        mid = (left + right + 1) // 2
        test_text = text[:mid] + suffix
        width, _ = get_text_size(draw, test_text, font)

        if width <= max_width:
            left = mid
        else:
            right = mid - 1

    return text[:left] + suffix if left > 0 else suffix


# ============================================================================
# MULTILINE TEXT
# ============================================================================

def draw_multiline_text(
    draw: ImageDraw.ImageDraw,
    lines: list,
    x: int,
    y: int,
    font: ImageFont.FreeTypeFont,
    color: int = DEFAULT_COLOR,
    line_spacing: int = 2,
    align: str = "left"
) -> int:
    """Draw multiple lines of text

    Args:
        draw: PIL ImageDraw object
        lines: List of text lines
        x: Left X coordinate (or center if align='center')
        y: Top Y coordinate
        font: Font to use
        color: Text color (default: 0 for black)
        line_spacing: Extra spacing between lines (default: 2)
        align: Text alignment ('left', 'center', 'right')

    Returns:
        int: Y coordinate after last line

    Example:
        >>> lines = ["Line 1", "Line 2", "Line 3"]
        >>> draw_multiline_text(draw, lines, 10, 20, font)
    """
    current_y = y

    for line in lines:
        if align == "center":
            width, _ = get_text_size(draw, line, font)
            line_x = x - width // 2
        elif align == "right":
            width, _ = get_text_size(draw, line, font)
            line_x = x - width
        else:  # left
            line_x = x

        draw.text((line_x, current_y), line, font=font, fill=color)
        _, line_height = get_text_size(draw, line, font)
        current_y += line_height + line_spacing

    return current_y
