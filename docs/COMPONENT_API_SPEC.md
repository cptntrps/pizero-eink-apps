# Display Component Library - API Specification

## Table of Contents

1. [Fonts API](#1-fonts-api)
2. [Canvas API](#2-canvas-api)
3. [Layouts API](#3-layouts-api)
4. [Text API](#4-text-api)
5. [Shapes API](#5-shapes-api)
6. [Icons API](#6-icons-api)
7. [Components API](#7-components-api)
8. [Touch Handler API](#8-touch-handler-api)
9. [Usage Examples](#9-usage-examples)

---

## 1. Fonts API

**Module:** `display.fonts`

### 1.1 `get_font(name: str) -> ImageFont`

Get a cached font by semantic name.

**Parameters:**
- `name` (str): Semantic font name from predefined set

**Returns:**
- `ImageFont`: Cached font object

**Available Names:**
- `'display'` - 48pt Bold - Large timers/counters
- `'headline'` - 28pt Bold - Main focus elements
- `'title'` - 16pt Bold - Page titles
- `'subtitle'` - 14pt Bold - Section headers
- `'body'` - 12pt Regular - Main content
- `'body_bold'` - 12pt Bold - Emphasized content
- `'small'` - 10pt Regular - Instructions/details
- `'tiny'` - 9pt Regular - Fine print
- `'large'` - 24pt Bold - Large emphasis
- `'medium'` - 14pt Regular - Medium text
- `'medium_bold'` - 14pt Bold - Medium bold text

**Example:**
```python
from display.fonts import get_font

title_font = get_font('title')
body_font = get_font('body')
draw.text((10, 10), "Hello", font=title_font, fill=0)
```

**Apps Using:** All 8 apps

---

### 1.2 `get_font_by_size(family: str, size: int) -> ImageFont`

Get a font by family name and size for custom requirements.

**Parameters:**
- `family` (str): Font family name ('Roboto-Bold' or 'Roboto-Regular')
- `size` (int): Font size in points

**Returns:**
- `ImageFont`: Cached font object

**Example:**
```python
custom_font = get_font_by_size('Roboto-Bold', 22)
```

**Apps Using:** Custom scenarios

---

### 1.3 `preload_fonts() -> None`

Pre-load all common fonts into cache. Call once at application startup for better performance.

**Example:**
```python
from display.fonts import preload_fonts

# At app startup
preload_fonts()
```

---

### 1.4 `clear_font_cache() -> None`

Clear the font cache to free memory. Rarely needed.

**Example:**
```python
from display.fonts import clear_font_cache

clear_font_cache()
```

---

## 2. Canvas API

**Module:** `display.canvas`

### 2.1 `class Canvas`

E-ink canvas for 250x122 pixel display.

#### Constructor

```python
Canvas()
```

**Example:**
```python
from display.canvas import Canvas

canvas = Canvas()
```

#### Properties

- `canvas.image` (Image): PIL Image object (250x122, 1-bit)
- `canvas.draw` (ImageDraw): PIL ImageDraw object
- `canvas.WIDTH` (int): Canvas width (250)
- `canvas.HEIGHT` (int): Canvas height (122)

#### Methods

##### `clear() -> None`

Clear canvas to white background.

**Example:**
```python
canvas.clear()  # Reset to blank white canvas
```

##### `get_buffer() -> Image`

Get image buffer for e-ink display.

**Returns:**
- `Image`: PIL Image object ready for display

**Example:**
```python
epd.displayPartial(epd.getbuffer(canvas.get_buffer()))
```

---

## 3. Layouts API

**Module:** `display.layouts`

### 3.1 `draw_header(draw, title: str, subtitle: str = None, timestamp: str = None, y_start: int = 2) -> int`

Draw standard header bar with title and optional elements.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `title` (str): Main title text
- `subtitle` (str, optional): Left-side subtitle
- `timestamp` (str, optional): Right-side timestamp (e.g., "12:30")
- `y_start` (int, optional): Starting Y position (default: 2)

**Returns:**
- `int`: Y-position where content can start (after header separator)

**Example:**
```python
from display.layouts import draw_header

content_y = draw_header(canvas.draw, "Medicine Tracker", timestamp="14:30")
# Draw content starting at content_y
```

**Apps Using:** All 8 apps

---

### 3.2 `draw_footer(draw, instruction: str, y_start: int = 100) -> int`

Draw standard footer bar with instruction text.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `instruction` (str): Instruction text to display
- `y_start` (int, optional): Y position for separator line (default: 100)

**Returns:**
- `int`: Y-position of footer top (for content sizing)

**Example:**
```python
from display.layouts import draw_footer

footer_y = draw_footer(canvas.draw, "Touch=Exit | Hold=Menu")
# Content area is from header_y to footer_y
```

**Apps Using:** All 8 apps

---

### 3.3 `draw_split_layout(draw, left_width: int = 125) -> tuple[int, int]`

Draw vertical divider for two-column layout.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `left_width` (int, optional): Width of left panel in pixels (default: 125)

**Returns:**
- `tuple[int, int]`: (left_width, right_x_start)

**Example:**
```python
from display.layouts import draw_split_layout

left_w, right_x = draw_split_layout(canvas.draw, left_width=125)
# Draw in left panel: x = 0 to left_w
# Draw in right panel: x = right_x to 250
```

**Apps Using:** flights, reboot

---

### 3.4 `draw_list_item(draw, x: int, y: int, text: str, checked: bool = None, bullet: str = '•', font = None) -> int`

Draw a single list item with checkbox or bullet.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `x` (int): X position
- `y` (int): Y position
- `text` (str): Item text
- `checked` (bool, optional): True/False for checkbox, None for bullet
- `bullet` (str, optional): Bullet character (default: '•')
- `font` (ImageFont, optional): Font to use (default: 'small')

**Returns:**
- `int`: Y-position for next item

**Example:**
```python
from display.layouts import draw_list_item

y = 30
y = draw_list_item(canvas.draw, 10, y, "Morning meds", checked=True)
y = draw_list_item(canvas.draw, 10, y, "Evening meds", checked=False)
y = draw_list_item(canvas.draw, 10, y, "Call doctor", checked=None)  # Bullet
```

**Apps Using:** medicine, mbta

---

## 4. Text API

**Module:** `display.text`

### 4.1 `draw_text_centered(draw, y: int, text: str, font, canvas_width: int = 250) -> tuple[int, int, int]`

Draw horizontally centered text.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `y` (int): Y position
- `text` (str): Text to draw
- `font` (ImageFont): Font object
- `canvas_width` (int, optional): Canvas width (default: 250)

**Returns:**
- `tuple[int, int, int]`: (x_position, y_position, text_width)

**Example:**
```python
from display.text import draw_text_centered
from display.fonts import get_font

x, y, w = draw_text_centered(canvas.draw, 50, "Centered Text", get_font('title'))
```

**Apps Using:** weather, mbta, disney, flights, pomodoro, reboot (6 apps)

---

### 4.2 `truncate_text(text: str, font, max_width: int, ellipsis: str = '...') -> str`

Truncate text to fit within maximum width.

**Parameters:**
- `text` (str): Text to truncate
- `font` (ImageFont): Font object
- `max_width` (int): Maximum width in pixels
- `ellipsis` (str, optional): Ellipsis string (default: '...')

**Returns:**
- `str`: Truncated text with ellipsis if needed

**Example:**
```python
from display.text import truncate_text
from display.fonts import get_font

short_text = truncate_text("Very long medicine name here", get_font('body'), 200)
canvas.draw.text((10, 20), short_text, font=get_font('body'), fill=0)
```

**Apps Using:** medicine, disney

---

### 4.3 `wrap_text(text: str, font, max_width: int) -> list[str]`

Wrap text to multiple lines to fit within maximum width.

**Parameters:**
- `text` (str): Text to wrap
- `font` (ImageFont): Font object
- `max_width` (int): Maximum line width in pixels

**Returns:**
- `list[str]`: List of wrapped text lines

**Example:**
```python
from display.text import wrap_text
from display.fonts import get_font

lines = wrap_text("Long text that needs to wrap to multiple lines", get_font('body'), 230)
y = 20
for line in lines:
    canvas.draw.text((10, y), line, font=get_font('body'), fill=0)
    y += 14
```

**Apps Using:** flights (quotes)

---

### 4.4 `measure_text(text: str, font) -> tuple[int, int]`

Get pixel dimensions of text.

**Parameters:**
- `text` (str): Text to measure
- `font` (ImageFont): Font object

**Returns:**
- `tuple[int, int]`: (width, height) in pixels

**Example:**
```python
from display.text import measure_text
from display.fonts import get_font

width, height = measure_text("Hello World", get_font('body'))
print(f"Text is {width}px wide and {height}px tall")
```

**Apps Using:** All apps (currently done inline)

---

## 5. Shapes API

**Module:** `display.shapes`

### 5.1 `draw_hline(draw, y: int, x1: int = 0, x2: int = 250, width: int = 1) -> None`

Draw horizontal line.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `y` (int): Y position
- `x1` (int, optional): Start X position (default: 0)
- `x2` (int, optional): End X position (default: 250)
- `width` (int, optional): Line width (default: 1)

**Example:**
```python
from display.shapes import draw_hline

draw_hline(canvas.draw, y=20)  # Full width line
draw_hline(canvas.draw, y=50, x1=10, x2=240)  # Partial line
```

**Apps Using:** All 8 apps (~20 times total)

---

### 5.2 `draw_vline(draw, x: int, y1: int = 0, y2: int = 122, width: int = 1) -> None`

Draw vertical line.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `x` (int): X position
- `y1` (int, optional): Start Y position (default: 0)
- `y2` (int, optional): End Y position (default: 122)
- `width` (int, optional): Line width (default: 1)

**Example:**
```python
from display.shapes import draw_vline

draw_vline(canvas.draw, x=125)  # Full height divider
```

**Apps Using:** flights, reboot, disney

---

### 5.3 `draw_button(draw, x: int, y: int, width: int, height: int, label: str, font, filled: bool = False) -> None`

Draw button with border and label.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `x` (int): X position (top-left)
- `y` (int): Y position (top-left)
- `width` (int): Button width
- `height` (int): Button height
- `label` (str): Button label text
- `font` (ImageFont): Font for label
- `filled` (bool, optional): Fill button background (default: False)

**Example:**
```python
from display.shapes import draw_button
from display.fonts import get_font

draw_button(canvas.draw, 10, 70, 100, 35, "Cancel", get_font('body'))
draw_button(canvas.draw, 140, 70, 100, 35, "OK", get_font('body'), filled=True)
```

**Apps Using:** reboot

---

### 5.4 `draw_checkbox(draw, x: int, y: int, size: int = 10, checked: bool = False) -> None`

Draw checkbox (empty or checked).

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `x` (int): X position
- `y` (int): Y position
- `size` (int, optional): Checkbox size (default: 10)
- `checked` (bool, optional): Checked state (default: False)

**Example:**
```python
from display.shapes import draw_checkbox

draw_checkbox(canvas.draw, 10, 30, checked=False)  # Empty box
draw_checkbox(canvas.draw, 10, 50, checked=True)   # Checked box
```

**Apps Using:** medicine

---

### 5.5 `draw_rounded_rect(draw, x: int, y: int, width: int, height: int, radius: int = 5, outline_width: int = 1, filled: bool = False) -> None`

Draw rounded rectangle.

**Parameters:**
- `draw` (ImageDraw): ImageDraw object
- `x` (int): X position (top-left)
- `y` (int): Y position (top-left)
- `width` (int): Rectangle width
- `height` (int): Rectangle height
- `radius` (int, optional): Corner radius (default: 5)
- `outline_width` (int, optional): Border width (default: 1)
- `filled` (bool, optional): Fill background (default: False)

**Example:**
```python
from display.shapes import draw_rounded_rect

draw_rounded_rect(canvas.draw, 10, 20, 230, 80, radius=10)
```

---

## 6. Icons API

**Module:** `display.icons`

### 6.1 Medicine Icons

#### `draw_pill_icon(draw, x: int, y: int, size: int = 10) -> None`

Draw capsule/pill icon.

**Example:**
```python
from display.icons import draw_pill_icon

draw_pill_icon(canvas.draw, 10, 30, size=15)
```

**Apps Using:** medicine

---

#### `draw_food_icon(draw, x: int, y: int, size: int = 8) -> None`

Draw fork icon for "take with food".

**Example:**
```python
from display.icons import draw_food_icon

draw_food_icon(canvas.draw, 20, 40)
```

**Apps Using:** medicine

---

#### `draw_checkmark(draw, x: int, y: int, size: int = 20, bold: bool = False) -> None`

Draw checkmark symbol.

**Example:**
```python
from display.icons import draw_checkmark

draw_checkmark(canvas.draw, 100, 50, size=30, bold=True)
```

**Apps Using:** medicine, mbta

---

### 6.2 Weather Icons

#### `draw_weather_icon(draw, condition: str, x: int, y: int, size: int = 40) -> None`

Draw weather icon based on condition string.

**Parameters:**
- `condition` (str): Weather condition (e.g., "sunny", "cloudy", "rain", "snow")

**Recognized Conditions:**
- Contains "sun" or "clear" → Sun icon
- Contains "cloud" → Cloud icon
- Contains "rain" or "drizzle" → Rain icon
- Contains "snow" → Snow icon
- Other → Question mark

**Example:**
```python
from display.icons import draw_weather_icon

draw_weather_icon(canvas.draw, "Partly Cloudy", 50, 50, size=50)
```

**Apps Using:** weather

---

#### `draw_sun_icon(draw, x: int, y: int, size: int = 40) -> None`

Draw sun icon with rays.

**Apps Using:** weather

---

#### `draw_cloud_icon(draw, x: int, y: int, size: int = 40) -> None`

Draw cloud icon.

**Apps Using:** weather

---

#### `draw_rain_icon(draw, x: int, y: int, size: int = 40) -> None`

Draw rain cloud icon with rain drops.

**Apps Using:** weather

---

#### `draw_snow_icon(draw, x: int, y: int, size: int = 40) -> None`

Draw snowflake icon.

**Apps Using:** weather

---

### 6.3 Navigation Icons

#### `draw_compass_rose(draw, cx: int, cy: int, radius: int, bearing: float, user_heading: float = 310) -> None`

Draw compass rose with bearing arrow.

**Parameters:**
- `cx` (int): Center X
- `cy` (int): Center Y
- `radius` (int): Compass radius
- `bearing` (float): Target bearing in degrees (0-360)
- `user_heading` (float, optional): User's heading (default: 310)

**Example:**
```python
from display.icons import draw_compass_rose

draw_compass_rose(canvas.draw, cx=187, cy=61, radius=45, bearing=45)
```

**Apps Using:** flights

---

#### `draw_arrow(draw, x: int, y: int, angle: float, length: int, width: int = 2) -> None`

Draw arrow pointing in specified direction.

**Parameters:**
- `angle` (float): Angle in degrees (0 = right, 90 = down)
- `length` (int): Arrow length
- `width` (int, optional): Line width (default: 2)

**Example:**
```python
from display.icons import draw_arrow

draw_arrow(canvas.draw, 100, 60, angle=45, length=30)
```

---

### 6.4 Status Icons

#### `draw_airplane_icon(draw, x: int, y: int, size: int = 20) -> None`

Draw airplane icon.

**Apps Using:** flights

---

#### `draw_timer_icon(draw, x: int, y: int, size: int = 20) -> None`

Draw timer/clock icon.

**Apps Using:** pomodoro

---

### 6.5 Characters

#### `draw_tomato_character(draw, cx: int, cy: int, frame: int = 0) -> None`

Draw animated tomato character.

**Parameters:**
- `frame` (int): Animation frame (0 or 1)

**Example:**
```python
from display.icons import draw_tomato_character

draw_tomato_character(canvas.draw, 125, 60, frame=0)
```

**Apps Using:** pomodoro

---

## 7. Components API

**Module:** `display.components`

### 7.1 `draw_status_badge(draw, x: int, y: int, text: str, status: str = 'normal', font = None) -> None`

Draw status badge with text.

**Parameters:**
- `status` (str): 'normal' (hollow), 'warning' (bold), 'error' (filled)

**Example:**
```python
from display.components import draw_status_badge

draw_status_badge(canvas.draw, 100, 50, "DELAY", status='warning')
draw_status_badge(canvas.draw, 100, 70, "CLOSED", status='error')
```

**Apps Using:** mbta, medicine

---

### 7.2 `draw_progress_bar(draw, x: int, y: int, width: int, height: int, progress: float, show_percent: bool = True) -> None`

Draw horizontal progress bar.

**Parameters:**
- `progress` (float): Progress from 0.0 to 1.0
- `show_percent` (bool, optional): Show percentage text (default: True)

**Example:**
```python
from display.components import draw_progress_bar

draw_progress_bar(canvas.draw, 10, 80, 230, 10, progress=0.75)
```

**Apps Using:** medicine

---

### 7.3 `draw_info_panel(draw, x: int, y: int, width: int, height: int, title: str, items: list[tuple[str, str]], font = None) -> None`

Draw bordered panel with title and key-value items.

**Parameters:**
- `items` (list[tuple[str, str]]): List of (key, value) tuples

**Example:**
```python
from display.components import draw_info_panel

draw_info_panel(
    canvas.draw, 10, 20, 110, 80,
    title="Flight Info",
    items=[
        ("Route", "BOS→SFO"),
        ("Alt", "35,000 ft"),
        ("Speed", "450 kts")
    ]
)
```

**Apps Using:** flights, weather

---

## 8. Touch Handler API

**Module:** `display.touch_handler`

### 8.1 `class TouchHandler`

Manages touch events and threading.

#### Constructor

```python
TouchHandler(gt_dev, gt_old, gt)
```

**Parameters:**
- `gt_dev`: Touch device object
- `gt_old`: Previous touch state object
- `gt`: Touch controller object

**Example:**
```python
from display.touch_handler import TouchHandler

touch = TouchHandler(gt_dev, gt_old, gt)
```

---

#### Methods

##### `check_exit_requested() -> bool`

Check if menu requested exit.

**Returns:**
- `bool`: True if exit requested

**Example:**
```python
if touch.check_exit_requested():
    break
```

**Apps Using:** All 8 apps

---

##### `has_touch_event() -> bool`

Check if there's a new touch event.

**Returns:**
- `bool`: True if touch detected

**Example:**
```python
if touch.has_touch_event():
    x, y = touch.get_touch_position()
    handle_touch(x, y)
```

**Apps Using:** All 8 apps

---

##### `get_touch_position() -> tuple[int, int]`

Get current touch position.

**Returns:**
- `tuple[int, int]`: (x, y) coordinates

**Example:**
```python
x, y = touch.get_touch_position()
if x < 125:
    print("Left side touched")
```

---

##### `clear_touch_state() -> None`

Clear touch state and flags.

**Example:**
```python
touch.clear_touch_state()
```

**Apps Using:** All 8 apps

---

##### `stop() -> None`

Stop touch handler and cleanup resources.

**Example:**
```python
touch.stop()
```

**Apps Using:** All 8 apps

---

## 9. Usage Examples

### 9.1 Simple App Template

```python
from display import Canvas, get_font
from display.layouts import draw_header, draw_footer
from display.text import draw_text_centered
from display.touch_handler import TouchHandler

def draw_screen():
    canvas = Canvas()

    # Header
    content_y = draw_header(canvas.draw, "My App", timestamp="12:30")

    # Content
    draw_text_centered(canvas.draw, 60, "Hello World", get_font('title'))

    # Footer
    draw_footer(canvas.draw, "Touch=Exit")

    return canvas.get_buffer()

def run_my_app(epd, gt_dev, gt_old, gt):
    touch = TouchHandler(gt_dev, gt_old, gt)

    # Initial display
    image = draw_screen()
    epd.displayPartial(epd.getbuffer(image))

    # Main loop
    while True:
        if touch.check_exit_requested():
            break

        if touch.has_touch_event():
            # Handle touch
            image = draw_screen()
            epd.displayPartial(epd.getbuffer(image))

        time.sleep(0.1)

    touch.stop()
```

---

### 9.2 List View Example

```python
from display import Canvas, get_font
from display.layouts import draw_header, draw_footer, draw_list_item

def draw_task_list(tasks):
    canvas = Canvas()

    content_y = draw_header(canvas.draw, "Task List")

    y = content_y + 5
    for task in tasks:
        y = draw_list_item(
            canvas.draw, 10, y,
            task['name'],
            checked=task['completed']
        )

    draw_footer(canvas.draw, "Touch=Toggle")

    return canvas.get_buffer()
```

---

### 9.3 Split Layout Example

```python
from display import Canvas, get_font
from display.layouts import draw_header, draw_split_layout
from display.icons import draw_compass_rose

def draw_flight_info(flight_data):
    canvas = Canvas()

    draw_header(canvas.draw, "Flight Tracker")

    # Split layout
    left_w, right_x = draw_split_layout(canvas.draw)

    # Left panel - info
    canvas.draw.text((10, 30), flight_data['callsign'],
                     font=get_font('large'), fill=0)
    canvas.draw.text((10, 50), f"Alt: {flight_data['altitude']} ft",
                     font=get_font('body'), fill=0)

    # Right panel - compass
    draw_compass_rose(canvas.draw, right_x + 60, 60, 45,
                     bearing=flight_data['bearing'])

    return canvas.get_buffer()
```

---

### 9.4 Weather Display Example

```python
from display import Canvas, get_font
from display.layouts import draw_header
from display.shapes import draw_hline
from display.icons import draw_weather_icon
from display.text import truncate_text

def draw_weather(weather_data):
    canvas = Canvas()

    draw_header(canvas.draw, "Weather", timestamp="14:30")

    # Temperature (large)
    canvas.draw.text((10, 30), weather_data['temp'],
                     font=get_font('headline'), fill=0)

    # Weather icon
    draw_weather_icon(canvas.draw, weather_data['condition'], 100, 30)

    # Separator
    draw_hline(canvas.draw, y=70)

    # Condition text
    condition = truncate_text(weather_data['condition'],
                             get_font('body'), 200)
    canvas.draw.text((10, 75), condition, font=get_font('body'), fill=0)

    # Humidity
    canvas.draw.text((10, 95), f"Humidity: {weather_data['humidity']}",
                     font=get_font('small'), fill=0)

    return canvas.get_buffer()
```

---

### 9.5 Timer Display Example

```python
from display import Canvas, get_font
from display.layouts import draw_header, draw_footer
from display.text import draw_text_centered
from display.components import draw_progress_bar

def draw_timer(state, time_left, total_time):
    canvas = Canvas()

    draw_header(canvas.draw, "Pomodoro Timer")

    # Time display
    mins, secs = divmod(time_left, 60)
    time_text = f"{mins:02}:{secs:02}"
    draw_text_centered(canvas.draw, 40, time_text, get_font('display'))

    # Progress bar
    progress = 1.0 - (time_left / total_time)
    draw_progress_bar(canvas.draw, 10, 90, 230, 8, progress)

    # State
    draw_text_centered(canvas.draw, 20, state, get_font('subtitle'))

    draw_footer(canvas.draw, "Click=Start/Pause")

    return canvas.get_buffer()
```

---

## 10. Migration Checklist

For migrating an existing app to use the component library:

### Step 1: Update Imports
```python
# Add these imports
from display import Canvas, get_font
from display.layouts import draw_header, draw_footer
from display.text import draw_text_centered
from display.shapes import draw_hline
from display.touch_handler import TouchHandler
```

### Step 2: Replace Font Loading
```python
# Remove:
f_title = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 16)

# Replace with:
f_title = get_font('title')
```

### Step 3: Replace Image Creation
```python
# Remove:
img = Image.new("1", (250, 122), 255)
draw = ImageDraw.Draw(img)

# Replace with:
canvas = Canvas()
draw = canvas.draw
```

### Step 4: Replace Headers/Footers
```python
# Remove:
draw.text((5, 2), "Title", font=f_title, fill=0)
draw.line([(0, 18), (250, 18)], fill=0, width=1)

# Replace with:
content_y = draw_header(draw, "Title")
```

### Step 5: Replace Touch Handling
```python
# Remove threading boilerplate
# Replace with:
touch = TouchHandler(gt_dev, gt_old, gt)

# In main loop:
if touch.check_exit_requested():
    break
```

### Step 6: Update Buffer Calls
```python
# Remove:
epd.displayPartial(epd.getbuffer(img))

# Replace with:
epd.displayPartial(epd.getbuffer(canvas.get_buffer()))
```

### Step 7: Test and Iterate
- Run app and verify display
- Check touch interactions
- Compare visual output to original
- Adjust as needed

---

## 11. Performance Notes

### Font Caching
- First call to `get_font()`: ~5-10ms (loads from disk)
- Subsequent calls: <0.1ms (cached)
- Recommendation: Call `preload_fonts()` at startup

### Canvas Reuse
- Creating new Canvas: ~1ms
- Reusing with `clear()`: ~0.5ms
- Recommendation: Reuse canvas when possible

### Touch Handler
- No performance overhead vs manual threading
- Cleaner code, same speed

---

## 12. Debugging Tips

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Verify Font Loading
```python
from display.fonts import get_font
font = get_font('title')
print(f"Font loaded: {font}")
```

### Check Canvas Size
```python
canvas = Canvas()
print(f"Canvas size: {canvas.image.size}")  # Should be (250, 122)
```

### Touch Event Debugging
```python
if touch.has_touch_event():
    x, y = touch.get_touch_position()
    print(f"Touch at ({x}, {y})")
```

---

## 13. FAQ

**Q: Can I use custom font sizes not in the semantic names?**
A: Yes, use `get_font_by_size('Roboto-Bold', 22)`

**Q: How do I add a new semantic font name?**
A: Edit `display/fonts.py` and add to the `FONTS` dictionary.

**Q: Can I mix old and new code?**
A: Yes, the library is designed for gradual migration.

**Q: What's the memory overhead?**
A: ~50-100KB for font cache, negligible for other components.

**Q: How do I report bugs?**
A: File an issue with minimal reproduction code.

---

## Appendix A: Complete API Reference

### Quick Reference Table

| Module | Function | Purpose | Priority |
|--------|----------|---------|----------|
| fonts | get_font() | Get cached font | HIGH |
| fonts | preload_fonts() | Pre-cache fonts | MEDIUM |
| canvas | Canvas() | Create canvas | HIGH |
| layouts | draw_header() | Draw header bar | HIGH |
| layouts | draw_footer() | Draw footer bar | HIGH |
| layouts | draw_split_layout() | Two columns | MEDIUM |
| layouts | draw_list_item() | List items | MEDIUM |
| text | draw_text_centered() | Center text | HIGH |
| text | truncate_text() | Truncate text | MEDIUM |
| text | measure_text() | Get text size | MEDIUM |
| shapes | draw_hline() | Horizontal line | HIGH |
| shapes | draw_vline() | Vertical line | MEDIUM |
| shapes | draw_button() | Button UI | MEDIUM |
| icons | draw_weather_icon() | Weather icons | MEDIUM |
| icons | draw_compass_rose() | Compass | LOW |
| components | draw_status_badge() | Status badge | LOW |
| touch_handler | TouchHandler() | Touch events | HIGH |

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Maintainer:** Display Component Library Team
