"""
Canvas Abstraction
==================

Provides simplified canvas creation for e-ink display applications.
Handles standard display dimensions and PIL setup boilerplate.

Standard display size: 250x122 pixels (Waveshare 2.13" e-ink)
"""

from typing import Tuple
from PIL import Image, ImageDraw


# ============================================================================
# DISPLAY CONSTANTS
# ============================================================================

DISPLAY_WIDTH = 250
DISPLAY_HEIGHT = 122
DISPLAY_MODE = "1"  # 1-bit black and white
BACKGROUND_WHITE = 255
BACKGROUND_BLACK = 0


# ============================================================================
# CANVAS CREATION
# ============================================================================

def create_canvas(
    width: int = DISPLAY_WIDTH,
    height: int = DISPLAY_HEIGHT,
    mode: str = DISPLAY_MODE,
    background: int = BACKGROUND_WHITE
) -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create a new canvas for drawing

    Convenience function that creates both the image and drawing context
    in one call, reducing boilerplate code.

    Args:
        width: Canvas width in pixels (default: 250)
        height: Canvas height in pixels (default: 122)
        mode: PIL image mode (default: "1" for 1-bit B&W)
        background: Background color (default: 255 for white)

    Returns:
        Tuple of (Image, ImageDraw): Ready to use canvas and drawing context

    Example:
        >>> img, draw = create_canvas()
        >>> draw.text((10, 10), "Hello", fill=0)
        >>> epd.displayPartial(epd.getbuffer(img))
    """
    img = Image.new(mode, (width, height), background)
    draw = ImageDraw.Draw(img)
    return img, draw


def create_canvas_black() -> Tuple[Image.Image, ImageDraw.ImageDraw]:
    """Create canvas with black background

    Useful for inverted displays or dark mode UI.

    Returns:
        Tuple of (Image, ImageDraw): Canvas with black background

    Example:
        >>> img, draw = create_canvas_black()
        >>> draw.text((10, 10), "Hello", fill=255)  # White text on black
    """
    return create_canvas(background=BACKGROUND_BLACK)


# ============================================================================
# CANVAS CLASS
# ============================================================================

class Canvas:
    """Object-oriented canvas wrapper

    Provides a more structured interface for canvas operations with
    context manager support.

    Example:
        >>> with Canvas() as canvas:
        ...     canvas.draw.text((10, 10), "Hello", fill=0)
        ...     buffer = canvas.get_buffer(epd)
        >>> epd.displayPartial(buffer)
    """

    def __init__(
        self,
        width: int = DISPLAY_WIDTH,
        height: int = DISPLAY_HEIGHT,
        mode: str = DISPLAY_MODE,
        background: int = BACKGROUND_WHITE
    ):
        """Initialize canvas

        Args:
            width: Canvas width in pixels (default: 250)
            height: Canvas height in pixels (default: 122)
            mode: PIL image mode (default: "1" for 1-bit B&W)
            background: Background color (default: 255 for white)
        """
        self.width = width
        self.height = height
        self.mode = mode
        self.background = background
        self.image = Image.new(mode, (width, height), background)
        self.draw = ImageDraw.Draw(self.image)

    def clear(self, color: int = BACKGROUND_WHITE) -> None:
        """Clear canvas to solid color

        Args:
            color: Color to clear to (default: 255 for white)

        Example:
            >>> canvas = Canvas()
            >>> canvas.draw.text((10, 10), "Hello", fill=0)
            >>> canvas.clear()  # Reset to blank white canvas
        """
        self.image = Image.new(self.mode, (self.width, self.height), color)
        self.draw = ImageDraw.Draw(self.image)

    def get_buffer(self, epd) -> bytes:
        """Get display buffer from image

        Args:
            epd: E-paper display driver instance

        Returns:
            bytes: Display buffer ready for epd.display() methods

        Example:
            >>> canvas = Canvas()
            >>> canvas.draw.text((10, 10), "Hello", fill=0)
            >>> buffer = canvas.get_buffer(epd)
            >>> epd.displayPartial(buffer)
        """
        return epd.getbuffer(self.image)

    def get_image(self) -> Image.Image:
        """Get the underlying PIL Image object

        Returns:
            Image: PIL Image object

        Example:
            >>> canvas = Canvas()
            >>> img = canvas.get_image()
            >>> img.save('/tmp/output.png')
        """
        return self.image

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Context manager exit"""
        # Cleanup if needed - no resources to clean
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_display_dimensions() -> Tuple[int, int]:
    """Get standard display dimensions

    Returns:
        Tuple of (width, height): Display dimensions in pixels

    Example:
        >>> width, height = get_display_dimensions()
        >>> print(f"Display is {width}x{height} pixels")
    """
    return DISPLAY_WIDTH, DISPLAY_HEIGHT


def get_display_center() -> Tuple[int, int]:
    """Get center point of display

    Returns:
        Tuple of (x, y): Center coordinates

    Example:
        >>> cx, cy = get_display_center()
        >>> draw.ellipse([cx-10, cy-10, cx+10, cy+10], outline=0)
    """
    return DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2
