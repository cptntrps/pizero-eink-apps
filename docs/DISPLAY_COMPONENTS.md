# Display Component Library Design

## Overview

This document outlines the design for a reusable display component library for the Pi Zero 2W e-ink applications. The goal is to eliminate 500-700 lines of duplicated code while improving consistency and maintainability.

---

## Component Hierarchy

```
display/
├── __init__.py           # Package initialization, exports all components
├── fonts.py              # Font loading and caching system
├── canvas.py             # Image creation and management
├── layouts.py            # Page layout components (header, footer, split)
├── text.py               # Text rendering utilities
├── shapes.py             # Common shape primitives
├── icons.py              # Icon library (weather, pill, compass, etc.)
├── components.py         # Higher-level UI components (lists, buttons)
└── touch_handler.py      # Touch event abstraction
```

---

## 1. Fonts Module (`display/fonts.py`)

### Purpose
Centralized font loading with caching to eliminate 40+ lines of duplication.

### Design

```python
class FontCache:
    """Singleton font cache for all applications"""

    # Semantic font definitions
    FONTS = {
        'display': ('Roboto-Bold', 48),      # Large timers/counters
        'headline': ('Roboto-Bold', 28),      # Main focus elements
        'title': ('Roboto-Bold', 16),         # Page titles
        'subtitle': ('Roboto-Bold', 14),      # Section headers
        'body': ('Roboto-Regular', 12),       # Main content
        'body_bold': ('Roboto-Bold', 12),     # Emphasized content
        'small': ('Roboto-Regular', 10),      # Instructions/details
        'tiny': ('Roboto-Regular', 9),        # Fine print
    }

    # Additional size variations
    SIZES = {
        'large': ('Roboto-Bold', 24),
        'medium': ('Roboto-Regular', 14),
        'medium_bold': ('Roboto-Bold', 14),
    }
```

### API

```python
# Get font by semantic name
font = get_font('title')
font = get_font('body')

# Get font by family and size (for custom needs)
font = get_font_by_size('Roboto-Bold', 20)

# Pre-load all common fonts (call once at app startup)
preload_fonts()

# Clear cache (for memory management)
clear_font_cache()
```

### Usage Example

```python
from display.fonts import get_font

# Old way (7 apps do this):
f_title = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 16)
f_body = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 12)
f_small = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 10)

# New way:
f_title = get_font('title')
f_body = get_font('body')
f_small = get_font('small')
```

### Benefits
- **Lines saved:** ~35 (87% reduction)
- **Performance:** Fonts loaded once, reused
- **Consistency:** All apps use same sizes
- **Flexibility:** Easy to change global font sizes

---

## 2. Canvas Module (`display/canvas.py`)

### Purpose
Standardize image creation and provide drawing context management.

### Design

```python
class Canvas:
    """E-ink canvas for 250x122 display"""

    WIDTH = 250
    HEIGHT = 122

    def __init__(self):
        self.image = Image.new("1", (self.WIDTH, self.HEIGHT), 255)
        self.draw = ImageDraw.Draw(self.image)

    def clear(self):
        """Clear canvas to white"""
        self.image = Image.new("1", (self.WIDTH, self.HEIGHT), 255)
        self.draw = ImageDraw.Draw(self.image)

    def get_buffer(self):
        """Get buffer for e-ink display"""
        return self.image
```

### API

```python
# Create new canvas
canvas = Canvas()

# Access draw object
canvas.draw.text((10, 10), "Hello", font=font, fill=0)

# Clear and reuse
canvas.clear()

# Get buffer for display
epd.displayPartial(epd.getbuffer(canvas.get_buffer()))
```

### Usage Example

```python
from display.canvas import Canvas

# Old way (40+ times across apps):
img = Image.new("1", (250, 122), 255)
draw = ImageDraw.Draw(img)
draw.text((10, 10), "Hello", font=font, fill=0)
epd.displayPartial(epd.getbuffer(img))

# New way:
canvas = Canvas()
canvas.draw.text((10, 10), "Hello", font=font, fill=0)
epd.displayPartial(epd.getbuffer(canvas.get_buffer()))
```

### Benefits
- **Lines saved:** ~78 (97% reduction)
- **Consistency:** Standard canvas size
- **Flexibility:** Easy to add utilities (save, copy, etc.)

---

## 3. Layouts Module (`display/layouts.py`)

### Purpose
Reusable page layout components used by all 8 apps.

### Components

#### 3.1 Header

```python
def draw_header(draw, title, subtitle=None, timestamp=None):
    """
    Draw standard header bar with title and optional elements.

    Args:
        draw: ImageDraw object
        title: Main title text
        subtitle: Optional subtitle (left side)
        timestamp: Optional timestamp (right side)

    Returns:
        int: Y-position where header ends (for content placement)
    """
```

**Layout:**
```
┌────────────────────────────────┐
│ TITLE              HH:MM       │ ← Line 2-16
├────────────────────────────────┤ ← Line 18
│                                │
```

**Used by:** All 8 apps

#### 3.2 Footer

```python
def draw_footer(draw, instruction_text, y_start=100):
    """
    Draw standard footer bar with instructions.

    Args:
        draw: ImageDraw object
        instruction_text: Text to display in footer
        y_start: Y-position to start footer (default 100)

    Returns:
        int: Y-position of footer top (for content sizing)
    """
```

**Layout:**
```
│                                │
├────────────────────────────────┤ ← y_start
│ Instruction text here          │ ← y_start + 5
└────────────────────────────────┘
```

**Used by:** All 8 apps

#### 3.3 Split Layout

```python
def draw_split_layout(draw, left_width=125):
    """
    Draw vertical split for two-column layout.

    Args:
        draw: ImageDraw object
        left_width: Width of left panel (default 125 = 50%)

    Returns:
        tuple: (left_width, right_x_start)
    """
```

**Layout:**
```
┌─────────────┬──────────────────┐
│             │                  │
│   Left      │      Right       │
│   Panel     │      Panel       │
│             │                  │
└─────────────┴──────────────────┘
```

**Used by:** flights, reboot (potentially more)

#### 3.4 List View

```python
def draw_list_item(draw, x, y, text, checked=None, bullet='•'):
    """
    Draw a single list item with optional checkbox or bullet.

    Args:
        draw: ImageDraw object
        x, y: Position
        text: Item text
        checked: True/False for checkbox, None for bullet
        bullet: Bullet character (default '•')

    Returns:
        int: Y-position for next item
    """
```

**Layout:**
```
[ ] Item text here          ← checkbox style
[✓] Completed item
• Bullet item               ← bullet style
```

**Used by:** medicine, mbta

### API Usage

```python
from display.layouts import draw_header, draw_footer, draw_split_layout
from display.canvas import Canvas

canvas = Canvas()

# Draw header
content_y = draw_header(canvas.draw, "App Title", timestamp="12:30")

# Draw content in available space (18 to 100)
canvas.draw.text((10, content_y + 5), "Content here", font=get_font('body'))

# Draw footer
draw_footer(canvas.draw, "Touch=Exit")
```

### Benefits
- **Lines saved:** ~28 (87% reduction)
- **Consistency:** All apps have same header/footer style
- **Flexibility:** Easy to modify globally

---

## 4. Text Module (`display/text.py`)

### Purpose
Text rendering utilities for centering, truncation, and wrapping.

### Components

#### 4.1 Centered Text

```python
def draw_text_centered(draw, y, text, font, canvas_width=250):
    """
    Draw horizontally centered text.

    Args:
        draw: ImageDraw object
        y: Y-position
        text: Text to draw
        font: Font object
        canvas_width: Canvas width (default 250)

    Returns:
        tuple: (x, y, text_width) - position and width of drawn text
    """
```

**Used by:** 6 apps, ~12 times

#### 4.2 Text Truncation

```python
def truncate_text(text, font, max_width, ellipsis='...'):
    """
    Truncate text to fit within max width.

    Args:
        text: Text to truncate
        font: Font object
        max_width: Maximum pixel width
        ellipsis: Ellipsis string (default '...')

    Returns:
        str: Truncated text with ellipsis if needed
    """
```

**Used by:** medicine, disney

#### 4.3 Text Wrapping

```python
def wrap_text(text, font, max_width):
    """
    Wrap text to multiple lines.

    Args:
        text: Text to wrap
        font: Font object
        max_width: Maximum line width in pixels

    Returns:
        list: List of text lines
    """
```

**Used by:** flights (for quotes), potentially others

#### 4.4 Text Measurement

```python
def measure_text(text, font):
    """
    Get dimensions of text.

    Args:
        text: Text to measure
        font: Font object

    Returns:
        tuple: (width, height)
    """
```

**Used by:** All apps (currently inline)

### API Usage

```python
from display.text import draw_text_centered, truncate_text

# Old way (appears ~12 times):
bbox = draw.textbbox((0, 0), text, font=font)
w = bbox[2] - bbox[0]
draw.text(((250 - w) // 2, y), text, font=font, fill=0)

# New way:
draw_text_centered(draw, y, text, font)

# Truncate long text
short_text = truncate_text("Very long medicine name here", font, max_width=230)
draw.text((10, 20), short_text, font=font, fill=0)
```

### Benefits
- **Lines saved:** ~40 (90% reduction)
- **Consistency:** Same centering/truncation logic
- **Flexibility:** Easy to add text features

---

## 5. Shapes Module (`display/shapes.py`)

### Purpose
Common shape primitives used across apps.

### Components

#### 5.1 Horizontal Line

```python
def draw_hline(draw, y, x1=0, x2=250, width=1):
    """Draw horizontal line across canvas"""
```

**Used by:** All 8 apps, ~20 times

#### 5.2 Vertical Line

```python
def draw_vline(draw, x, y1=0, y2=122, width=1):
    """Draw vertical line down canvas"""
```

**Used by:** flights, reboot, disney

#### 5.3 Button/Box

```python
def draw_button(draw, x, y, width, height, label, font):
    """Draw button with border and centered label"""
```

**Used by:** reboot, potentially others

#### 5.4 Checkbox

```python
def draw_checkbox(draw, x, y, size=10, checked=False):
    """Draw checkbox (empty or checked)"""
```

**Used by:** medicine

### API Usage

```python
from display.shapes import draw_hline, draw_button

# Old way (appears ~20 times):
draw.line([(0, 18), (250, 18)], fill=0, width=1)

# New way:
draw_hline(draw, y=18)

# Button
draw_button(draw, x=10, y=70, width=100, height=35, label="Cancel", font=get_font('body'))
```

### Benefits
- **Lines saved:** ~30 (80% reduction)
- **Consistency:** Standard shape styles
- **Flexibility:** Easy to modify globally

---

## 6. Icons Module (`display/icons.py`)

### Purpose
Centralized icon library for all applications.

### Icon Inventory

```python
# Medicine icons
def draw_pill_icon(draw, x, y, size=10)
def draw_food_icon(draw, x, y, size=8)
def draw_checkmark(draw, x, y, size=20)

# Weather icons
def draw_sun_icon(draw, x, y, size=40)
def draw_cloud_icon(draw, x, y, size=40)
def draw_rain_icon(draw, x, y, size=40)
def draw_snow_icon(draw, x, y, size=40)

# Navigation icons
def draw_compass_rose(draw, cx, cy, radius, bearing=0)
def draw_arrow(draw, x, y, angle, length)

# Status icons
def draw_airplane_icon(draw, x, y, size=20)
def draw_timer_icon(draw, x, y, size=20)

# Characters (pomodoro)
def draw_tomato_character(draw, cx, cy, frame=0)
```

### API Usage

```python
from display.icons import draw_pill_icon, draw_weather_icon

# Draw medicine pill
draw_pill_icon(canvas.draw, x=10, y=30, size=15)

# Draw weather (auto-detect condition)
draw_weather_icon(canvas.draw, "Partly Cloudy", x=50, y=50)
```

### Benefits
- **Reusability:** Icons available to all apps
- **Consistency:** Same visual style
- **Maintainability:** Fix icon bugs once

---

## 7. Components Module (`display/components.py`)

### Purpose
Higher-level composite components.

### Components

#### 7.1 Status Badge

```python
def draw_status_badge(draw, x, y, text, status='normal'):
    """
    Draw colored status badge (normal, warning, error).

    Args:
        status: 'normal' (hollow), 'warning' (bold), 'error' (filled)
    """
```

**Used by:** mbta (delays), medicine (low stock)

#### 7.2 Progress Bar

```python
def draw_progress_bar(draw, x, y, width, height, progress):
    """
    Draw horizontal progress bar.

    Args:
        progress: 0.0 to 1.0
    """
```

**Used by:** medicine (percentage), potentially pomodoro

#### 7.3 Info Panel

```python
def draw_info_panel(draw, x, y, width, height, title, items):
    """
    Draw bordered panel with title and key-value items.

    Args:
        items: List of (key, value) tuples
    """
```

**Used by:** flights, weather

### API Usage

```python
from display.components import draw_status_badge, draw_info_panel

# Status badge
draw_status_badge(canvas.draw, x=100, y=50, text="DELAY", status='warning')

# Info panel
draw_info_panel(
    canvas.draw, x=10, y=20, width=110, height=80,
    title="Flight Info",
    items=[
        ("Route", "BOS→SFO"),
        ("Alt", "35,000 ft"),
        ("Speed", "450 kts")
    ]
)
```

---

## 8. Touch Handler Module (`display/touch_handler.py`)

### Purpose
Abstract touch event handling to eliminate 160+ lines of duplication.

### Design

```python
class TouchHandler:
    """
    Manages touch events and threading for e-ink apps.
    Eliminates IRQ thread boilerplate in every app.
    """

    def __init__(self, gt_dev, gt_old, gt):
        self.gt_dev = gt_dev
        self.gt_old = gt_old
        self.gt = gt
        self.running = True
        self._start_irq_thread()

    def _start_irq_thread(self):
        """Start IRQ monitoring thread"""
        # Replaces 11 lines in every app

    def check_exit_requested(self):
        """Check if menu requested exit"""
        # Replaces 4 lines in every app

    def has_touch_event(self):
        """Check if there's a new touch event"""
        # Replaces 3 lines in every app

    def get_touch_position(self):
        """Get current touch position"""
        return (self.gt_dev.X[0], self.gt_dev.Y[0])

    def clear_touch_state(self):
        """Clear touch state"""
        # Replaces 3 lines in every app

    def stop(self):
        """Stop handler and cleanup"""
        self.running = False
        self.clear_touch_state()
```

### API Usage

```python
from display.touch_handler import TouchHandler

# Old way (11+ lines per app × 8 apps = 88 lines):
flag_t = [1]
def pthread_irq():
    while flag_t[0] == 1:
        if gt.digital_read(gt.INT) == 0:
            gt_dev.Touch = 1
        else:
            gt_dev.Touch = 0
        time.sleep(0.01)
t = threading.Thread(target=pthread_irq)
t.daemon = True
t.start()
# ... later ...
if hasattr(gt_dev, "exit_requested") and gt_dev.exit_requested:
    logging.info("Exit requested by menu")
    flag_t[0] = 0
    break

# New way (3 lines):
touch = TouchHandler(gt_dev, gt_old, gt)
while True:
    if touch.check_exit_requested():
        break

    if touch.has_touch_event():
        x, y = touch.get_touch_position()
        # Handle touch

    time.sleep(0.1)

touch.stop()
```

### Benefits
- **Lines saved:** ~160 (87% reduction)
- **Consistency:** Same touch handling logic
- **Maintainability:** Fix touch bugs once
- **Features:** Easy to add double-tap, hold, gestures

---

## Component Integration Example

### Before (weather_cal_app.py lines 71-111)

```python
def draw_weather_screen():
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)

    f_time = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 28)
    f_date = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 14)
    f_temp = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 20)
    f_small = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 10)

    target_date = datetime.now()

    time_str = target_date.strftime("%H:%M")
    draw.text((10, 5), time_str, font=f_time, fill=0)

    date_str = target_date.strftime("%a, %b %d")
    draw.text((10, 38), date_str, font=f_date, fill=0)

    draw.line((5, 60, 245, 60), fill=0, width=1)

    weather = get_weather()
    if weather:
        draw_weather_icon(draw, weather['condition'], 10, 65)
        temp_text = weather['temp']
        draw.text((70, 68), temp_text, font=f_temp, fill=0)
        condition_short = weather['condition'][:15]
        draw.text((70, 95), condition_short, font=f_small, fill=0)
        draw.text((170, 75), f"Humid:", font=f_small, fill=0)
        draw.text((170, 90), weather['humidity'], font=f_small, fill=0)
    else:
        draw.text((50, 75), "Weather unavailable", font=f_small, fill=0)
        draw.text((50, 90), "Check connection", font=f_small, fill=0)

    draw.text((75, 112), "Auto-refresh: 5 min", font=f_small, fill=0)

    return img
```

**Lines:** 41 lines

### After (with components)

```python
from display import Canvas, get_font, draw_hline
from display.icons import draw_weather_icon
from display.text import truncate_text

def draw_weather_screen():
    canvas = Canvas()

    target_date = datetime.now()

    # Time and date
    canvas.draw.text((10, 5), target_date.strftime("%H:%M"),
                     font=get_font('headline'), fill=0)
    canvas.draw.text((10, 38), target_date.strftime("%a, %b %d"),
                     font=get_font('medium'), fill=0)

    # Separator
    draw_hline(canvas.draw, y=60)

    # Weather
    weather = get_weather()
    if weather:
        draw_weather_icon(canvas.draw, weather['condition'], 10, 65)
        canvas.draw.text((70, 68), weather['temp'], font=get_font('large'), fill=0)
        condition = truncate_text(weather['condition'], get_font('small'), 15)
        canvas.draw.text((70, 95), condition, font=get_font('small'), fill=0)
        canvas.draw.text((170, 75), "Humid:", font=get_font('small'), fill=0)
        canvas.draw.text((170, 90), weather['humidity'], font=get_font('small'), fill=0)
    else:
        canvas.draw.text((50, 75), "Weather unavailable", font=get_font('small'), fill=0)
        canvas.draw.text((50, 90), "Check connection", font=get_font('small'), fill=0)

    canvas.draw.text((75, 112), "Auto-refresh: 5 min", font=get_font('small'), fill=0)

    return canvas.get_buffer()
```

**Lines:** 32 lines (22% reduction in this function alone)

**Global savings:**
- Font loading: 4 lines → 0 lines (done once in imports)
- Image creation: 2 lines → 1 line
- Separator line: 1 line → 1 line (but cleaner)
- Text truncation: Would save 7 lines if needed

---

## Migration Strategy

### Phase 2.2: Core Infrastructure (Week 1)
1. Create `display/fonts.py` - Font cache system
2. Create `display/canvas.py` - Canvas abstraction
3. Create `display/touch_handler.py` - Touch abstraction
4. Create `display/shapes.py` - Basic shapes
5. Update medicine_app.py to use new components (proof of concept)

### Phase 2.3: Layout & Text (Week 2)
6. Create `display/layouts.py` - Header, footer, split
7. Create `display/text.py` - Text utilities
8. Update weather_cal_app.py and mbta_app.py

### Phase 2.4: Icons & Components (Week 3)
9. Create `display/icons.py` - Icon library
10. Create `display/components.py` - Composite components
11. Update remaining 5 apps

### Phase 2.5: Polish & Testing (Week 4)
12. Integration testing
13. Performance optimization
14. Documentation updates

---

## Testing Strategy

### Unit Tests

```python
# tests/test_fonts.py
def test_font_cache():
    font1 = get_font('title')
    font2 = get_font('title')
    assert font1 is font2  # Should be same cached object

# tests/test_text.py
def test_centered_text():
    # Mock draw object
    # Verify text is centered correctly

# tests/test_canvas.py
def test_canvas_creation():
    canvas = Canvas()
    assert canvas.image.size == (250, 122)
```

### Integration Tests

```python
# tests/test_integration.py
def test_full_screen_render():
    """Test complete screen rendering with all components"""
    canvas = Canvas()
    content_y = draw_header(canvas.draw, "Test", timestamp="12:00")
    draw_footer(canvas.draw, "Test instruction")
    # Verify image is valid
```

### Visual Tests

- Generate reference images for each component
- Compare rendered output to reference
- Flag visual regressions

---

## Performance Metrics

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Font load time | ~100ms | ~20ms | 80% faster |
| Code size | ~1800 lines | ~1100 lines | 39% smaller |
| Memory usage | Baseline | +50KB (cached fonts) | Acceptable |
| App startup | ~500ms | ~400ms | 20% faster |
| Render time | Baseline | Same | No change |

### Memory Considerations

- Font cache: ~30-50KB
- Icon cache: ~20KB
- Total overhead: <100KB (acceptable for Pi Zero 2W with 512MB RAM)

---

## Backward Compatibility

### Strategy
- Keep existing apps working during migration
- Components provide new interface, don't break old code
- Gradual migration, one app at a time
- No breaking changes to app signatures

### Example
```python
# Old code continues to work:
img = Image.new("1", (250, 122), 255)
draw = ImageDraw.Draw(img)

# New code uses components:
from display import Canvas
canvas = Canvas()
```

---

## Future Enhancements

### Phase 3 (Optional)

1. **Animation framework**
   - Frame sequencing
   - Easing functions
   - Transition effects

2. **Theme system**
   - Light/dark themes
   - Custom color schemes (for future color displays)

3. **Layout engine**
   - Flexbox-like layout
   - Auto-sizing
   - Responsive design

4. **Widget library**
   - Charts/graphs
   - Tables
   - Forms/inputs

5. **Template system**
   - Pre-built page templates
   - Rapid app development

---

## Summary

This component library will:

✓ **Reduce code by 500-700 lines** (39% reduction)
✓ **Improve consistency** across all 8 apps
✓ **Enhance maintainability** (fix bugs once)
✓ **Increase velocity** (new apps develop faster)
✓ **Better performance** (font caching, optimizations)
✓ **Easier testing** (components tested in isolation)

**Next Steps:**
1. Review this design with team
2. Start Phase 2.2 implementation
3. Create proof of concept with medicine_app.py
4. Iterate based on feedback
