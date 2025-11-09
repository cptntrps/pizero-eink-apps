"""
Display Component Library
=======================

A comprehensive component library for Pi Zero 2W e-ink display applications.

This library provides reusable components for building e-ink display applications
with consistent styling and reduced code duplication.

## Modules

- **fonts**: Font caching and presets
- **canvas**: Canvas creation and abstraction
- **touch_handler**: Touch event handling utilities
- **shapes**: Primitive shape drawing (lines, rectangles, circles)
- **text**: Text rendering utilities (centering, wrapping, truncation)
- **icons**: Icon library (pills, food, weather, compass, etc.)
- **layouts**: Page layout components (header, footer, split, list)
- **components**: Composite UI components (status bar, progress bar, buttons)

## Usage Example

```python
from display import fonts, canvas, shapes, text
from display.icons import draw_pill_icon
from display.layouts import HeaderLayout

# Create canvas
img, draw = canvas.create_canvas()

# Use layouts
header = HeaderLayout("Medicine Tracker", show_time=True)
header.draw(draw)

# Draw icons
draw_pill_icon(draw, 10, 30, size=15)

# Draw text
text.draw_centered_text(draw, "Hello World", y=60,
                       font=fonts.get_font_preset('headline'))

# Display
epd.displayPartial(epd.getbuffer(img))
```

## Design Principles

1. **DRY (Don't Repeat Yourself)**: Eliminates duplication across apps
2. **Consistent API**: Uniform function signatures and patterns
3. **Performance**: Font caching, efficient rendering
4. **Maintainability**: Clear documentation, typed interfaces
5. **Flexibility**: Composable components, customizable styling
"""

# Import key functions for convenience
from .fonts import get_font, get_font_preset, clear_font_cache
from .canvas import create_canvas, Canvas
from .touch_handler import TouchHandler
from .shapes import (
    draw_line,
    draw_rectangle,
    draw_circle,
    draw_horizontal_line,
    draw_vertical_line,
)
from .text import (
    draw_centered_text,
    draw_wrapped_text,
    truncate_text,
    get_text_size,
)
from .input_handler import (
    InputHandler,
    InputEvent,
    create_input_handler,
    detect_input_mode,
    get_input_info,
)
from .touch_input import TouchInputHandler, create_touch_handler
from .button_input import ButtonInputHandler, ButtonEvent, create_button_handler

__version__ = "1.0.0"
__author__ = "Pi Zero 2W Team"

__all__ = [
    # Fonts
    "get_font",
    "get_font_preset",
    "clear_font_cache",
    # Canvas
    "create_canvas",
    "Canvas",
    # Touch
    "TouchHandler",
    # Shapes
    "draw_line",
    "draw_rectangle",
    "draw_circle",
    "draw_horizontal_line",
    "draw_vertical_line",
    # Text
    "draw_centered_text",
    "draw_wrapped_text",
    "truncate_text",
    "get_text_size",
    # Input Abstraction
    "InputHandler",
    "InputEvent",
    "create_input_handler",
    "detect_input_mode",
    "get_input_info",
    # Touch Input
    "TouchInputHandler",
    "create_touch_handler",
    # Button Input
    "ButtonInputHandler",
    "ButtonEvent",
    "create_button_handler",
]
