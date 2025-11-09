"""
Composite UI Components
=======================

Provides high-level reusable UI components built from primitives.
"""

from datetime import datetime
from typing import Optional, Tuple
from PIL import ImageDraw, ImageFont
from .canvas import DISPLAY_WIDTH
from .shapes import draw_rectangle, draw_horizontal_line
from .text import get_text_size, truncate_text_to_width
from .fonts import get_font_preset
from .icons import draw_battery_icon, draw_wifi_icon


# ============================================================================
# STATUS BAR
# ============================================================================

class StatusBar:
    """Status bar showing time, battery, and connectivity

    Example:
        >>> status = StatusBar(show_time=True, show_battery=True)
        >>> status.draw(draw, battery_level=75, wifi_strength=2)
    """

    def __init__(
        self,
        show_time: bool = True,
        show_battery: bool = False,
        show_wifi: bool = False,
        height: int = 16,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize status bar

        Args:
            show_time: Show current time (default: True)
            show_battery: Show battery indicator (default: False)
            show_wifi: Show WiFi indicator (default: False)
            height: Status bar height (default: 16)
            font: Time font (default: 'small' preset)
        """
        self.show_time = show_time
        self.show_battery = show_battery
        self.show_wifi = show_wifi
        self.height = height
        self.font = font or get_font_preset('small')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        battery_level: int = 100,
        wifi_strength: int = 3,
        color: int = 0
    ) -> int:
        """Draw status bar

        Args:
            draw: PIL ImageDraw object
            battery_level: Battery level 0-100 (default: 100)
            wifi_strength: WiFi strength 0-3 (default: 3)
            color: Color to use (default: 0 for black)

        Returns:
            int: Y coordinate after status bar
        """
        x_pos = DISPLAY_WIDTH - 5

        # Battery icon
        if self.show_battery:
            x_pos -= 25
            draw_battery_icon(draw, x_pos, 2, battery_level, size=20, color=color)

        # WiFi icon
        if self.show_wifi:
            x_pos -= 20
            draw_wifi_icon(draw, x_pos, 12, wifi_strength, size=12, color=color)

        # Time
        if self.show_time:
            time_str = datetime.now().strftime("%H:%M")
            _, _ = get_text_size(draw, time_str, self.font)
            draw.text((5, 2), time_str, font=self.font, fill=color)

        # Divider line
        draw_horizontal_line(draw, self.height, color=color, width=1)

        return self.height


# ============================================================================
# PROGRESS BAR
# ============================================================================

class ProgressBar:
    """Visual progress indicator

    Example:
        >>> progress = ProgressBar(x=10, y=50, width=200, height=10)
        >>> progress.draw(draw, progress=75)  # 75% complete
    """

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int = 10
    ):
        """Initialize progress bar

        Args:
            x: Left X coordinate
            y: Top Y coordinate
            width: Bar width
            height: Bar height (default: 10)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        progress: float,
        color: int = 0,
        show_percentage: bool = False,
        font: Optional[ImageFont.FreeTypeFont] = None
    ) -> None:
        """Draw progress bar

        Args:
            draw: PIL ImageDraw object
            progress: Progress value 0-100
            color: Bar color (default: 0 for black)
            show_percentage: Show percentage text (default: False)
            font: Percentage font (default: 'small' preset)
        """
        progress = max(0, min(100, progress))  # Clamp 0-100

        # Outer border
        draw_rectangle(draw, self.x, self.y, self.width, self.height,
                       outline=color, border_width=1)

        # Fill
        fill_width = int((self.width - 4) * progress / 100)
        if fill_width > 0:
            draw_rectangle(draw, self.x + 2, self.y + 2,
                           fill_width, self.height - 4,
                           outline=color, fill=color, border_width=0)

        # Percentage text
        if show_percentage:
            if font is None:
                font = get_font_preset('small')
            percentage_text = f"{int(progress)}%"
            text_width, _ = get_text_size(draw, percentage_text, font)
            text_x = self.x + (self.width - text_width) // 2
            text_y = self.y + self.height + 2
            draw.text((text_x, text_y), percentage_text, font=font, fill=color)


# ============================================================================
# BUTTON
# ============================================================================

class Button:
    """Interactive button component

    Example:
        >>> button = Button("Click Me", x=50, y=50, width=100, height=30)
        >>> button.draw(draw)
        >>> if button.is_touched(touch_x, touch_y):
        ...     handle_click()
    """

    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        width: int,
        height: int,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize button

        Args:
            text: Button text
            x: Left X coordinate
            y: Top Y coordinate
            width: Button width
            height: Button height
            font: Text font (default: 'body' preset)
        """
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font or get_font_preset('body')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        pressed: bool = False
    ) -> None:
        """Draw button

        Args:
            draw: PIL ImageDraw object
            color: Button color (default: 0 for black)
            pressed: Draw in pressed state (default: False)
        """
        # Button background
        if pressed:
            draw_rectangle(draw, self.x, self.y, self.width, self.height,
                           outline=color, fill=color, border_width=2)
            text_color = 255  # White text on black background
        else:
            draw_rectangle(draw, self.x, self.y, self.width, self.height,
                           outline=color, border_width=2)
            text_color = color

        # Center text
        text_width, text_height = get_text_size(draw, self.text, self.font)
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - text_height) // 2
        draw.text((text_x, text_y), self.text, font=self.font, fill=text_color)

    def is_touched(self, touch_x: int, touch_y: int) -> bool:
        """Check if touch point is within button bounds

        Args:
            touch_x: Touch X coordinate
            touch_y: Touch Y coordinate

        Returns:
            bool: True if touched, False otherwise
        """
        return (self.x <= touch_x <= self.x + self.width and
                self.y <= touch_y <= self.y + self.height)

    def get_bounds(self) -> Tuple[int, int, int, int]:
        """Get button bounds

        Returns:
            Tuple of (x, y, width, height)
        """
        return self.x, self.y, self.width, self.height


# ============================================================================
# LIST ITEM
# ============================================================================

class ListItem:
    """Item in a list with optional icon and checkbox

    Example:
        >>> item = ListItem("Task 1", y=20, checked=False)
        >>> item.draw(draw)
    """

    def __init__(
        self,
        text: str,
        y: int,
        checked: bool = False,
        show_checkbox: bool = True,
        show_icon: bool = False,
        height: int = 15,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize list item

        Args:
            text: Item text
            y: Y coordinate
            checked: Checked state (default: False)
            show_checkbox: Show checkbox (default: True)
            show_icon: Show icon before text (default: False)
            height: Item height (default: 15)
            font: Text font (default: 'small' preset)
        """
        self.text = text
        self.y = y
        self.checked = checked
        self.show_checkbox = show_checkbox
        self.show_icon = show_icon
        self.height = height
        self.font = font or get_font_preset('small')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        icon_callback=None
    ) -> None:
        """Draw list item

        Args:
            draw: PIL ImageDraw object
            color: Color to use (default: 0 for black)
            icon_callback: Optional function to draw custom icon
        """
        x = 5

        # Checkbox
        if self.show_checkbox:
            if self.checked:
                checkbox_text = "[✓]"
            else:
                checkbox_text = "[ ]"
            draw.text((x, self.y), checkbox_text, font=self.font, fill=color)
            x += 25

        # Icon
        if self.show_icon and icon_callback:
            icon_callback(draw, x, self.y + 2, size=10, color=color)
            x += 15

        # Text (truncate if needed)
        max_width = DISPLAY_WIDTH - x - 5
        item_text = truncate_text_to_width(draw, self.text, max_width, self.font)
        draw.text((x, self.y), item_text, font=self.font, fill=color)

    def toggle_checked(self) -> None:
        """Toggle checked state"""
        self.checked = not self.checked


# ============================================================================
# MESSAGE BOX
# ============================================================================

class MessageBox:
    """Simple message/dialog box

    Example:
        >>> msg = MessageBox("Success!", "Operation completed")
        >>> msg.draw(draw)
    """

    def __init__(
        self,
        title: str,
        message: str,
        width: int = 200,
        height: int = 80,
        title_font: Optional[ImageFont.FreeTypeFont] = None,
        message_font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize message box

        Args:
            title: Message box title
            message: Message text
            width: Box width (default: 200)
            height: Box height (default: 80)
            title_font: Title font (default: 'title' preset)
            message_font: Message font (default: 'body' preset)
        """
        self.title = title
        self.message = message
        self.width = width
        self.height = height
        self.title_font = title_font or get_font_preset('subtitle')
        self.message_font = message_font or get_font_preset('body')

        # Center on display
        self.x = (DISPLAY_WIDTH - width) // 2
        self.y = 20

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0
    ) -> None:
        """Draw message box

        Args:
            draw: PIL ImageDraw object
            color: Color to use (default: 0 for black)
        """
        # Box background (white with black border)
        draw_rectangle(draw, self.x, self.y, self.width, self.height,
                       outline=color, fill=255, border_width=2)

        # Title
        title_width, title_height = get_text_size(draw, self.title, self.title_font)
        title_x = self.x + (self.width - title_width) // 2
        title_y = self.y + 10
        draw.text((title_x, title_y), self.title, font=self.title_font, fill=color)

        # Divider
        draw_horizontal_line(draw, title_y + title_height + 5,
                             x1=self.x + 10, x2=self.x + self.width - 10,
                             color=color, width=1)

        # Message (truncate if needed)
        message_y = title_y + title_height + 15
        max_width = self.width - 20
        message_text = truncate_text_to_width(draw, self.message, max_width,
                                              self.message_font)
        message_width, _ = get_text_size(draw, message_text, self.message_font)
        message_x = self.x + (self.width - message_width) // 2
        draw.text((message_x, message_y), message_text,
                  font=self.message_font, fill=color)


# ============================================================================
# BADGE
# ============================================================================

class Badge:
    """Small badge/label component

    Example:
        >>> badge = Badge("NEW", x=200, y=10)
        >>> badge.draw(draw)
    """

    def __init__(
        self,
        text: str,
        x: int,
        y: int,
        padding: int = 3,
        font: Optional[ImageFont.FreeTypeFont] = None
    ):
        """Initialize badge

        Args:
            text: Badge text
            x: Left X coordinate
            y: Top Y coordinate
            padding: Internal padding (default: 3)
            font: Text font (default: 'tiny' preset)
        """
        self.text = text
        self.x = x
        self.y = y
        self.padding = padding
        self.font = font or get_font_preset('tiny')

    def draw(
        self,
        draw: ImageDraw.ImageDraw,
        color: int = 0,
        inverted: bool = False
    ) -> None:
        """Draw badge

        Args:
            draw: PIL ImageDraw object
            color: Badge color (default: 0 for black)
            inverted: Inverted style (white text on black) (default: False)
        """
        text_width, text_height = get_text_size(draw, self.text, self.font)
        badge_width = text_width + 2 * self.padding
        badge_height = text_height + 2 * self.padding

        if inverted:
            # Black background, white text
            draw_rectangle(draw, self.x, self.y, badge_width, badge_height,
                           outline=color, fill=color, border_width=1)
            text_color = 255
        else:
            # White background, black text
            draw_rectangle(draw, self.x, self.y, badge_width, badge_height,
                           outline=color, fill=255, border_width=1)
            text_color = color

        draw.text((self.x + self.padding, self.y + self.padding),
                  self.text, font=self.font, fill=text_color)
