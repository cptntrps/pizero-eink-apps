"""
Page Layout Components
======================

Provides reusable layout components for structuring e-ink display pages.
"""

from datetime import datetime
from typing import Optional, List, Tuple
from PIL import ImageDraw, ImageFont
from .canvas import DISPLAY_WIDTH, DISPLAY_HEIGHT
from .shapes import draw_horizontal_line, draw_vertical_line
from .text import get_text_size, truncate_text_to_width
from .fonts import get_font_preset


# ============================================================================
# HEADER LAYOUT
# ============================================================================

class HeaderLayout:
    """Standard header bar with title and optional time

    Example:
        >>> header = HeaderLayout("Medicine Tracker", show_time=True)
        >>> header.draw(draw)
    """

    def __init__(
        self,
        title: str,
        show_time: bool = False,
        height: int = 18,
        font: Optional[ImageFont.FreeTypeFont] = None,
        time_font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize header layout

        Args:
            title: Header title text
            show_time: Show current time on right side (default: False)
            height: Header height in pixels (default: 18)
            font: Title font (default: 'title' preset)
            time_font: Time font (default: 'body' preset)
        """
        self.title = title
        self.show_time = show_time
        self.height = height
        self.font = font or get_font_preset('subtitle')
        self.time_font = time_font or get_font_preset('body')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        draw_divider: bool = True
    ) -> int:
        """Draw header

        Args:
            draw: PIL ImageDraw object
            color: Color to use (default: 0 for black)
            draw_divider: Draw divider line below header (default: True)

        Returns:
            int: Y coordinate after header (for positioning next element)
        """
        # Draw title
        draw.text((5, 2), self.title, font=self.font, fill=color)

        # Draw time if enabled
        if self.show_time:
            time_str = datetime.now().strftime("%H:%M")
            time_width, _ = get_text_size(draw, time_str, self.time_font)
            draw.text((DISPLAY_WIDTH - time_width - 5, 2),
                      time_str, font=self.time_font, fill=color)

        # Draw divider line
        if draw_divider:
            draw_horizontal_line(draw, self.height, color=color, width=1)

        return self.height


# ============================================================================
# FOOTER LAYOUT
# ============================================================================

class FooterLayout:
    """Standard footer with instructions or status

    Example:
        >>> footer = FooterLayout("Tap: Next | Hold: Exit")
        >>> footer.draw(draw)
    """

    def __init__(
        self,
        text: str,
        height: int = 22,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize footer layout

        Args:
            text: Footer text
            height: Footer height in pixels (default: 22)
            font: Text font (default: 'small' preset)
        """
        self.text = text
        self.height = height
        self.font = font or get_font_preset('small')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        draw_divider: bool = True
    ) -> int:
        """Draw footer

        Args:
            draw: PIL ImageDraw object
            color: Color to use (default: 0 for black)
            draw_divider: Draw divider line above footer (default: True)

        Returns:
            int: Y coordinate of footer top
        """
        footer_y = DISPLAY_HEIGHT - self.height

        # Draw divider line
        if draw_divider:
            draw_horizontal_line(draw, footer_y, color=color, width=1)

        # Draw text
        draw.text((10, footer_y + 6), self.text, font=self.font, fill=color)

        return footer_y


# ============================================================================
# SPLIT LAYOUT
# ============================================================================

class SplitLayout:
    """Split screen layout with left and right panels

    Example:
        >>> split = SplitLayout(split_x=125)
        >>> split.draw_divider(draw)
        >>> # Draw content in left and right panels
    """

    def __init__(self, split_x: int = DISPLAY_WIDTH // 2):
        """Initialize split layout

        Args:
            split_x: X coordinate of divider (default: center)
        """
        self.split_x = split_x
        self.left_width = split_x
        self.right_width = DISPLAY_WIDTH - split_x

    def draw_divider(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        width: int = 1
    ) -> None:
        """Draw vertical divider line

        Args:
            draw: PIL ImageDraw object
            color: Line color (default: 0 for black)
            width: Line width (default: 1)
        """
        draw_vertical_line(draw, self.split_x, color=color, width=width)

    def get_left_bounds(self) -> Tuple[int, int, int, int]:
        """Get left panel bounds

        Returns:
            Tuple of (x, y, width, height)
        """
        return 0, 0, self.left_width, DISPLAY_HEIGHT

    def get_right_bounds(self) -> Tuple[int, int, int, int]:
        """Get right panel bounds

        Returns:
            Tuple of (x, y, width, height)
        """
        return self.split_x, 0, self.right_width, DISPLAY_HEIGHT


# ============================================================================
# LIST LAYOUT
# ============================================================================

class ListLayout:
    """Scrollable list view layout

    Example:
        >>> items = ["Item 1", "Item 2", "Item 3"]
        >>> list_view = ListLayout(items, item_height=15)
        >>> list_view.draw(draw)
    """

    def __init__(
        self,
        items: List[str],
        item_height: int = 15,
        padding: int = 5,
        start_y: int = 20,
        max_height: Optional[int] = None,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize list layout

        Args:
            items: List of item strings
            item_height: Height per item in pixels (default: 15)
            padding: Left padding (default: 5)
            start_y: Starting Y coordinate (default: 20)
            max_height: Maximum height for list (default: full display)
            font: Item font (default: 'small' preset)
        """
        self.items = items
        self.item_height = item_height
        self.padding = padding
        self.start_y = start_y
        self.max_height = max_height or (DISPLAY_HEIGHT - start_y)
        self.font = font or get_font_preset('small')
        self.scroll_offset = 0

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        show_bullets: bool = True
    ) -> int:
        """Draw list items

        Args:
            draw: PIL ImageDraw object
            color: Text color (default: 0 for black)
            show_bullets: Show bullet points (default: True)

        Returns:
            int: Y coordinate after last item
        """
        y = self.start_y
        max_items = self.max_height // self.item_height

        for i, item in enumerate(self.items[self.scroll_offset:]):
            if i >= max_items:
                break

            # Bullet point
            if show_bullets:
                bullet = "•"
                draw.text((self.padding, y), bullet, font=self.font, fill=color)
                text_x = self.padding + 10
            else:
                text_x = self.padding

            # Item text (truncate if too long)
            max_width = DISPLAY_WIDTH - text_x - 5
            item_text = truncate_text_to_width(draw, item, max_width, self.font)
            draw.text((text_x, y), item_text, font=self.font, fill=color)

            y += self.item_height

        return y

    def scroll_down(self) -> None:
        """Scroll list down one item"""
        max_scroll = max(0, len(self.items) - (self.max_height // self.item_height))
        self.scroll_offset = min(self.scroll_offset + 1, max_scroll)

    def scroll_up(self) -> None:
        """Scroll list up one item"""
        self.scroll_offset = max(0, self.scroll_offset - 1)

    def reset_scroll(self) -> None:
        """Reset scroll to top"""
        self.scroll_offset = 0


# ============================================================================
# GRID LAYOUT
# ============================================================================

class GridLayout:
    """Grid layout for arranging items in rows and columns

    Example:
        >>> grid = GridLayout(rows=2, cols=2, cell_width=125, cell_height=61)
        >>> for i in range(4):
        ...     x, y = grid.get_cell_position(i)
        ...     draw.text((x + 10, y + 10), f"Cell {i}", font=font, fill=0)
    """

    def __init__(
        self,
        rows: int,
        cols: int,
        cell_width: Optional[int] = None,
        cell_height: Optional[int] = None,
        padding: int = 0
    ):
        """Initialize grid layout

        Args:
            rows: Number of rows
            cols: Number of columns
            cell_width: Width per cell (default: auto-calculated)
            cell_height: Height per cell (default: auto-calculated)
            padding: Padding between cells (default: 0)
        """
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self.cell_width = cell_width or (DISPLAY_WIDTH // cols)
        self.cell_height = cell_height or (DISPLAY_HEIGHT // rows)

    def get_cell_position(self, index: int) -> Tuple[int, int]:
        """Get position of cell by index

        Args:
            index: Cell index (0-based, row-major order)

        Returns:
            Tuple of (x, y): Top-left corner of cell
        """
        row = index // self.cols
        col = index % self.cols

        x = col * self.cell_width + self.padding
        y = row * self.cell_height + self.padding

        return x, y

    def get_cell_bounds(self, index: int) -> Tuple[int, int, int, int]:
        """Get bounds of cell by index

        Args:
            index: Cell index

        Returns:
            Tuple of (x, y, width, height)
        """
        x, y = self.get_cell_position(index)
        width = self.cell_width - 2 * self.padding
        height = self.cell_height - 2 * self.padding
        return x, y, width, height

    def draw_grid_lines(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        width: int = 1
    ) -> None:
        """Draw grid lines

        Args:
            draw: PIL ImageDraw object
            color: Line color (default: 0 for black)
            width: Line width (default: 1)
        """
        # Horizontal lines
        for i in range(1, self.rows):
            y = i * self.cell_height
            draw_horizontal_line(draw, y, color=color, width=width)

        # Vertical lines
        for i in range(1, self.cols):
            x = i * self.cell_width
            draw_vertical_line(draw, x, color=color, width=width)


# ============================================================================
# CENTER LAYOUT
# ============================================================================

class CenterLayout:
    """Layout helper for centering content

    Example:
        >>> center = CenterLayout()
        >>> center.draw_centered_text(draw, "Hello", font)
    """

    def __init__(
        self,
        width: int = DISPLAY_WIDTH,
        height: int = DISPLAY_HEIGHT
    ):
        """Initialize center layout

        Args:
            width: Container width (default: full display)
            height: Container height (default: full display)
        """
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2

    def get_centered_text_position(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont
    ) -> Tuple[int, int]:
        """Get position for centered text

        Args:
            draw: PIL ImageDraw object
            text: Text to center
            font: Font to use

        Returns:
            Tuple of (x, y): Position for text
        """
        text_width, text_height = get_text_size(draw, text, font)
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        return x, y

    def draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        font: ImageFont.FreeTypeFont,
        color: int = 0
    ) -> None:
        """Draw text centered in layout

        Args:
            draw: PIL ImageDraw object
            text: Text to draw
            font: Font to use
            color: Text color (default: 0 for black)
        """
        x, y = self.get_centered_text_position(draw, text, font)
        draw.text((x, y), text, font=font, fill=color)
