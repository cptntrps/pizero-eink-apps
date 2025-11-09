# Display Component Library - Quick Reference

## Quick Start

```python
from display import canvas, fonts, TouchHandler
from display.layouts import HeaderLayout, FooterLayout
from display.icons import draw_pill_icon

# Create canvas
img, draw = canvas.create_canvas()

# Get fonts
title_font = fonts.get_font_preset('title')
body_font = fonts.get_font_preset('body')

# Draw header
header = HeaderLayout("My App", show_time=True)
header.draw(draw)

# Draw content
draw_pill_icon(draw, 10, 30, size=15)
draw.text((30, 30), "Content here", font=body_font, fill=0)

# Draw footer
footer = FooterLayout("Instructions")
footer.draw(draw)

# Display
epd.displayPartial(epd.getbuffer(img))
```

## Font Presets

```python
fonts.get_font_preset('headline')      # 20pt bold
fonts.get_font_preset('title')         # 16pt bold
fonts.get_font_preset('subtitle')      # 14pt bold
fonts.get_font_preset('body')          # 12pt regular
fonts.get_font_preset('body_bold')     # 12pt bold
fonts.get_font_preset('small')         # 10pt regular
fonts.get_font_preset('tiny')          # 9pt regular
fonts.get_font_preset('display')       # 24pt bold
fonts.get_font_preset('display_huge')  # 48pt bold
```

## Common Shapes

```python
from display import shapes

# Lines
shapes.draw_line(draw, x1, y1, x2, y2)
shapes.draw_horizontal_line(draw, y)
shapes.draw_vertical_line(draw, x)
shapes.draw_divider(draw, y, padding=10)

# Shapes
shapes.draw_rectangle(draw, x, y, width, height)
shapes.draw_circle(draw, x, y, radius)
shapes.draw_rounded_rectangle(draw, x, y, w, h, radius=10)
shapes.draw_frame(draw, padding=5)
```

## Text Functions

```python
from display import text

# Centering
text.draw_centered_text(draw, "Text", y=50, font=font)
text.draw_centered_text_both(draw, "Text", font=font)
text.draw_right_aligned_text(draw, "12:34", y=5, font=font)

# Wrapping
lines = text.wrap_text(draw, "Long text...", max_width=200, font=font)
next_y = text.draw_wrapped_text(draw, "Text", x, y, max_width=200, font=font)

# Truncation
short = text.truncate_text("Long text", max_length=10)
short = text.truncate_text_to_width(draw, "Text", max_width=100, font=font)
```

## Icons

```python
from display.icons import *

# Medicine
draw_pill_icon(draw, x, y, size=10)
draw_food_icon(draw, x, y, size=8)
draw_checkmark(draw, x, y, size=10)

# Weather
draw_weather_icon(draw, x, y, 'rain', size=30)  # sun/clouds/rain/snow/storm

# UI
draw_battery_icon(draw, x, y, level=75, size=20)
draw_wifi_icon(draw, x, y, strength=2, size=15)

# Pomodoro
draw_tomato_icon(draw, x, y, frame=1, size=30)  # frame 1 or 2

# Flight
draw_compass_icon(draw, x, y, direction=45, size=20)
draw_airplane_icon(draw, x, y, size=20)
```

## Layouts

```python
from display.layouts import *

# Header
header = HeaderLayout("Title", show_time=True)
header.draw(draw)

# Footer
footer = FooterLayout("Instructions")
footer.draw(draw)

# Split screen
split = SplitLayout(split_x=125)
split.draw_divider(draw)

# List
items = ["Item 1", "Item 2", "Item 3"]
list_view = ListLayout(items, start_y=20)
list_view.draw(draw)

# Grid
grid = GridLayout(rows=2, cols=2)
x, y = grid.get_cell_position(0)
```

## Components

```python
from display.components import *

# Status bar
status = StatusBar(show_time=True, show_battery=True)
status.draw(draw, battery_level=75, wifi_strength=2)

# Progress bar
progress = ProgressBar(x=10, y=50, width=200)
progress.draw(draw, progress=75, show_percentage=True)

# Button
button = Button("Click", x=50, y=80, width=100, height=30)
button.draw(draw)
if button.is_touched(touch_x, touch_y):
    handle_click()

# List item
item = ListItem("Task", y=20, checked=False)
item.draw(draw)
item.toggle_checked()
```

## Touch Handling

```python
from display import TouchHandler

# Context manager (recommended)
with TouchHandler(gt, gt_dev) as touch:
    while True:
        if touch.check_exit_requested(gt_dev):
            break
        # ... app logic ...

# Manual control
touch = TouchHandler(gt, gt_dev)
touch.start()
# ... app logic ...
touch.stop()
```

## Common Patterns

### Simple Screen

```python
img, draw = canvas.create_canvas()

HeaderLayout("Title", show_time=True).draw(draw)

font = fonts.get_font_preset('body')
draw.text((10, 30), "Content", font=font, fill=0)

FooterLayout("Tap: Exit").draw(draw)

epd.displayPartial(epd.getbuffer(img))
```

### Split Screen

```python
img, draw = canvas.create_canvas()

split = SplitLayout(split_x=125)
split.draw_divider(draw)

# Left panel
font = fonts.get_font_preset('body')
draw.text((10, 30), "Left", font=font, fill=0)

# Right panel
draw.text((135, 30), "Right", font=font, fill=0)
```

### List with Icons

```python
img, draw = canvas.create_canvas()

HeaderLayout("My List").draw(draw)

items = [
    ("Medicine", draw_pill_icon),
    ("Food", draw_food_icon),
    ("Done", draw_checkmark)
]

y = 20
font = fonts.get_font_preset('small')
for text, icon_func in items:
    icon_func(draw, 10, y, size=10)
    draw.text((25, y), text, font=font, fill=0)
    y += 15
```

## Performance Tips

1. **Preload fonts at startup:**
   ```python
   fonts.preload_common_fonts()
   ```

2. **Cache fonts outside loops:**
   ```python
   font = fonts.get_font_preset('body')  # Once
   for item in items:
       draw.text((x, y), item, font=font, fill=0)  # Reuse
   ```

3. **Use context managers:**
   ```python
   with TouchHandler(gt, gt_dev) as touch:
       # Automatic cleanup
   ```

4. **Batch drawing operations:**
   ```python
   # Draw everything first
   draw.text(...)
   draw.line(...)
   draw.circle(...)
   # Then update display once
   epd.displayPartial(epd.getbuffer(img))
   ```

## Display Constants

```python
from display.canvas import (
    DISPLAY_WIDTH,      # 250
    DISPLAY_HEIGHT,     # 122
    DISPLAY_MODE,       # "1" (1-bit B&W)
    BACKGROUND_WHITE,   # 255
    BACKGROUND_BLACK    # 0
)

width, height = get_display_dimensions()  # (250, 122)
cx, cy = get_display_center()            # (125, 61)
```

## Error Handling

```python
try:
    font = fonts.get_font('Roboto-Regular', 12)
except OSError:
    print("Font file not found")

try:
    font = fonts.get_font_preset('invalid')
except KeyError:
    print("Invalid preset name")
```

## Testing

```python
# Clear font cache between tests
fonts.clear_font_cache()

# Check cache size
size = fonts.get_cache_size()

# List available presets
presets = fonts.list_presets()
```

## Common Gotchas

1. **Coordinate system:** (0, 0) is top-left
2. **Color values:** 0 = black, 255 = white (1-bit display)
3. **Text positioning:** (x, y) is top-left of text, not baseline
4. **Touch handler:** Always stop() or use context manager
5. **Font caching:** First load is slower, subsequent loads are fast

## Migration Checklist

- [ ] Replace `Image.new()` with `canvas.create_canvas()`
- [ ] Replace `ImageFont.truetype()` with `fonts.get_font_preset()`
- [ ] Replace threading boilerplate with `TouchHandler`
- [ ] Use layout components instead of manual positioning
- [ ] Use icon library instead of duplicated icon code
- [ ] Use text utilities for centering and wrapping
- [ ] Test on actual hardware before committing
