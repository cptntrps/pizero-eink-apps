# Display Component Library - Visual Hierarchy

## Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Application Layer                                │
│  (medicine_app, weather_app, mbta_app, disney_app, flights_app, etc.)   │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
                                   │ imports
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      display/ Package (Public API)                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ __init__.py - Exports: Canvas, get_font, all layout/text/shapes   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└──────────┬──────────────────────────────────────────────────────────────┘
           │
           ├─────────────────────────────────────────────────────────┐
           │                                                         │
           ▼                                                         ▼
┌──────────────────────┐                              ┌─────────────────────────┐
│   Core Utilities     │                              │  High-Level Components  │
│  ─────────────────   │                              │  ─────────────────────  │
│  • fonts.py          │                              │  • layouts.py           │
│  • canvas.py         │◄─────────────────────────────│  • components.py        │
│  • touch_handler.py  │                              │  • icons.py             │
└──────────┬───────────┘                              └───────────┬─────────────┘
           │                                                      │
           │ provides base for                                   │ uses
           │                                                      │
           ▼                                                      │
┌──────────────────────┐                                         │
│  Drawing Primitives  │◄────────────────────────────────────────┘
│  ─────────────────   │
│  • text.py           │
│  • shapes.py         │
└──────────────────────┘
```

---

## Module Dependency Graph

```
display/__init__.py
    │
    ├─► fonts.py ────────────────────────┐
    │       │                            │
    │       │ (no dependencies)          │
    │       │                            │
    ├─► canvas.py ───────────────────────┤
    │       │                            │
    │       │ (no dependencies)          │
    │       │                            │
    ├─► shapes.py ───────────────────────┤
    │       │                            │
    │       └─► fonts.py                 │
    │                                    │
    ├─► text.py ─────────────────────────┤
    │       │                            │
    │       ├─► fonts.py                 │
    │       └─► canvas.py                │
    │                                    │
    ├─► icons.py ────────────────────────┤
    │       │                            │
    │       ├─► fonts.py                 │
    │       └─► shapes.py                │
    │                                    │
    ├─► layouts.py ──────────────────────┤
    │       │                            │
    │       ├─► fonts.py                 │
    │       ├─► text.py                  │
    │       └─► shapes.py                │
    │                                    │
    ├─► components.py ───────────────────┤
    │       │                            │
    │       ├─► fonts.py                 │
    │       ├─► text.py                  │
    │       ├─► shapes.py                │
    │       └─► layouts.py               │
    │                                    │
    └─► touch_handler.py                 │
            │                            │
            │ (no dependencies)          │
            │                            │
            └────────────────────────────┘
                    All use:
                    - PIL.Image
                    - PIL.ImageDraw
                    - PIL.ImageFont
```

---

## Component Layering Strategy

### Layer 0: Foundation (No Dependencies)
```
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   fonts.py       │  │   canvas.py      │  │ touch_handler.py │
│                  │  │                  │  │                  │
│ • FontCache      │  │ • Canvas         │  │ • TouchHandler   │
│ • get_font()     │  │ • WIDTH/HEIGHT   │  │ • check_exit()   │
│ • preload()      │  │ • clear()        │  │ • has_touch()    │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

**Characteristics:**
- No internal dependencies
- Can be used independently
- Provide core functionality

---

### Layer 1: Drawing Primitives (Use Layer 0)
```
┌──────────────────┐  ┌──────────────────┐
│   shapes.py      │  │   text.py        │
│                  │  │                  │
│ • draw_hline()   │  │ • centered()     │
│ • draw_vline()   │  │ • truncate()     │
│ • draw_button()  │  │ • wrap()         │
│ • draw_checkbox()│  │ • measure()      │
│                  │  │                  │
│ Uses: fonts      │  │ Uses: fonts      │
└──────────────────┘  └──────────────────┘
```

**Characteristics:**
- Use fonts for rendering
- Provide basic drawing operations
- Reusable across apps

---

### Layer 2: Visual Components (Use Layers 0 & 1)
```
┌──────────────────┐
│   icons.py       │
│                  │
│ • draw_pill()    │
│ • draw_weather() │
│ • draw_compass() │
│ • draw_tomato()  │
│                  │
│ Uses: fonts      │
│       shapes     │
└──────────────────┘
```

**Characteristics:**
- Complex visual elements
- App-specific but reusable
- Built from primitives

---

### Layer 3: Layout Components (Use Layers 0, 1, 2)
```
┌──────────────────┐  ┌──────────────────┐
│   layouts.py     │  │  components.py   │
│                  │  │                  │
│ • draw_header()  │  │ • status_badge() │
│ • draw_footer()  │  │ • progress_bar() │
│ • split_layout() │  │ • info_panel()   │
│ • list_item()    │  │                  │
│                  │  │                  │
│ Uses: fonts      │  │ Uses: fonts      │
│       text       │  │       text       │
│       shapes     │  │       shapes     │
│                  │  │       layouts    │
└──────────────────┘  └──────────────────┘
```

**Characteristics:**
- Page-level layouts
- Composite components
- App-agnostic patterns

---

## Usage Flow

### Typical App Initialization
```
┌─────────────────────────────────────────────────────────────┐
│ App Startup                                                 │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ from display import ...       │
    │ from display.fonts import ... │
    │ from display.layouts import...│
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ preload_fonts() [Optional]    │ ◄── Improves performance
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ touch = TouchHandler(...)     │
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ Main Event Loop               │
    └───────────────────────────────┘
```

### Typical Render Flow
```
┌─────────────────────────────────────────────────────────────┐
│ draw_screen()                                               │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ canvas = Canvas()             │ ◄── Layer 0: Foundation
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ content_y = draw_header(...)  │ ◄── Layer 3: Layout
    │   ├─► uses get_font()         │     ├─► Layer 0: fonts
    │   └─► uses draw_hline()       │     └─► Layer 1: shapes
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ Draw app-specific content     │
    │   ├─► draw_text_centered()    │ ◄── Layer 1: text
    │   ├─► draw_pill_icon()        │ ◄── Layer 2: icons
    │   └─► draw_progress_bar()     │ ◄── Layer 3: components
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ draw_footer(...)              │ ◄── Layer 3: Layout
    └───────────────┬───────────────┘
                    │
                    ▼
    ┌───────────────────────────────┐
    │ return canvas.get_buffer()    │
    └───────────────────────────────┘
```

---

## App Usage Matrix

### Which Apps Use Which Components

```
Component           │ med │ wea │ mbt │ dis │ fli │ pom │ for │ reb │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
fonts.get_font()    │  ✓  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
canvas.Canvas()     │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
touch.TouchHandler()│  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
layouts.header()    │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
layouts.footer()    │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
layouts.split()     │     │     │     │     │  ○  │     │     │  ○  │
layouts.list_item() │  ○  │     │  ○  │     │     │     │     │     │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
text.centered()     │     │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │
text.truncate()     │  ○  │     │     │  ○  │     │     │     │     │
text.wrap()         │     │     │     │     │  ○  │     │     │     │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
shapes.hline()      │  ○  │  ○  │  ○  │  ○  │  ○  │  ○  │     │     │
shapes.vline()      │     │     │     │  ○  │  ○  │     │     │  ○  │
shapes.button()     │     │     │     │     │     │     │     │  ○  │
shapes.checkbox()   │  ○  │     │     │     │     │     │     │     │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
icons.pill()        │  ✓  │     │     │     │     │     │     │     │
icons.food()        │  ✓  │     │     │     │     │     │     │     │
icons.checkmark()   │  ✓  │     │  ○  │     │     │     │     │     │
icons.weather()     │     │  ✓  │     │     │     │     │     │     │
icons.compass()     │     │     │     │     │  ✓  │     │     │     │
icons.tomato()      │     │     │     │     │     │  ✓  │     │     │
────────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
comp.status_badge() │  ○  │     │  ○  │     │     │     │     │     │
comp.progress_bar() │  ○  │     │     │     │     │     │     │     │
comp.info_panel()   │     │  ○  │     │     │  ○  │     │     │     │
────────────────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

Legend:
  ✓ = Already implemented in current code
  ○ = Would benefit from component (to be added)
  (blank) = Not applicable to this app
```

---

## Code Sharing Visualization

### Current State (Before Components)

```
medicine_app.py (495 lines)
  ├─ Font loading: 6 lines
  ├─ Threading: 11 lines
  ├─ Touch handling: 20 lines
  ├─ Image creation: 6 lines
  ├─ Header/footer: 4 lines
  ├─ Icons: 9 lines
  └─ App logic: 439 lines

weather_cal_app.py (171 lines)
  ├─ Font loading: 4 lines
  ├─ Threading: 11 lines
  ├─ Touch handling: 20 lines
  ├─ Image creation: 2 lines
  ├─ Header/footer: 2 lines
  ├─ Weather icon: 34 lines
  └─ App logic: 98 lines

... (similar for other 6 apps)

Total: ~1800 lines
Duplicated: ~600 lines (33%)
```

### After Components

```
display/
  ├─ fonts.py (80 lines) ◄─────────────────┐
  ├─ canvas.py (40 lines) ◄────────────────┤
  ├─ touch_handler.py (60 lines) ◄─────────┤
  ├─ shapes.py (100 lines) ◄───────────────┤
  ├─ text.py (80 lines) ◄──────────────────┤
  ├─ icons.py (250 lines) ◄────────────────┤  Shared by all apps
  ├─ layouts.py (120 lines) ◄──────────────┤
  ├─ components.py (100 lines) ◄───────────┤
  └─ __init__.py (20 lines)                │
      Total: 850 lines                     │
                                           │
medicine_app.py (200 lines) ──────────────┤
  ├─ Imports: 3 lines                      │
  └─ App logic: 197 lines                  │
                                           │
weather_cal_app.py (80 lines) ────────────┤
  ├─ Imports: 3 lines                      │
  └─ App logic: 77 lines                   │
                                           │
... (other 6 apps similar) ───────────────┘

Total: ~1100 lines (39% reduction)
Duplicated: ~50 lines (5%)
```

---

## File Size Comparison

### Before
```
medicine_app.py         ████████████████ 495 lines
weather_cal_app.py      ████████ 171 lines
mbta_app.py             ████████████ 268 lines
disney_app.py           ██████████████ 293 lines
flights_app.py          ██████████████████████████████ 606 lines
pomodoro_app.py         ██████████████ 289 lines
forbidden_app.py        ████ 76 lines
reboot_app.py           ████ 101 lines

TOTAL: ~2300 lines
```

### After
```
display/fonts.py        ████ 80 lines
display/canvas.py       ██ 40 lines
display/touch_handler.py ███ 60 lines
display/shapes.py       █████ 100 lines
display/text.py         ████ 80 lines
display/icons.py        ████████████ 250 lines
display/layouts.py      ██████ 120 lines
display/components.py   █████ 100 lines

medicine_app.py         ██████████ 200 lines
weather_cal_app.py      ████ 80 lines
mbta_app.py             ████████ 150 lines
disney_app.py           ████████ 160 lines
flights_app.py          ████████████████ 320 lines
pomodoro_app.py         ██████████ 180 lines
forbidden_app.py        ██ 40 lines
reboot_app.py           ███ 60 lines

TOTAL: ~1820 lines (21% reduction)
SHARED: 830 lines (one-time cost, used by all apps)
```

---

## Component Reusability Graph

```
                      ┌─────────────┐
                      │ All 8 Apps  │
                      └──────┬──────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  Fonts   │      │  Canvas  │      │  Touch   │
    │  Cache   │      │          │      │ Handler  │
    └──────────┘      └──────────┘      └──────────┘
          │                  │                  │
          └──────────┬───────┴────────┬─────────┘
                     │                │
                     ▼                ▼
              ┌──────────┐      ┌──────────┐
              │  Shapes  │      │   Text   │
              │          │      │          │
              └─────┬────┘      └────┬─────┘
                    │                │
                    └────┬───────┬───┘
                         │       │
                         ▼       ▼
                   ┌──────────┬──────────┐
                   │  Icons   │ Layouts  │
                   └────┬─────┴───┬──────┘
                        │         │
                        └────┬────┘
                             │
                             ▼
                      ┌──────────┐
                      │Components│
                      └──────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ medicine │      │  weather │      │   mbta   │
    │   app    │      │    app   │      │   app    │
    └──────────┘      └──────────┘      └──────────┘
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  disney  │      │ flights  │      │ pomodoro │
    │   app    │      │   app    │      │   app    │
    └──────────┘      └──────────┘      └──────────┘
          ▼                  ▼
    ┌──────────┐      ┌──────────┐
    │forbidden │      │  reboot  │
    │   app    │      │   app    │
    └──────────┘      └──────────┘
```

---

## Dependency Depth Analysis

### Layer 0 (No dependencies)
- `fonts.py`
- `canvas.py`
- `touch_handler.py`

**Impact:** Changes here affect all layers

---

### Layer 1 (Depends on Layer 0)
- `shapes.py` → uses `fonts.py`
- `text.py` → uses `fonts.py`, `canvas.py`

**Impact:** Changes affect Layer 2 and 3

---

### Layer 2 (Depends on Layers 0, 1)
- `icons.py` → uses `fonts.py`, `shapes.py`

**Impact:** Changes affect Layer 3 only

---

### Layer 3 (Depends on Layers 0, 1, 2)
- `layouts.py` → uses `fonts.py`, `text.py`, `shapes.py`
- `components.py` → uses all lower layers

**Impact:** Changes only affect applications

---

## Evolution Path

### Phase 2.2 (Week 1) - Foundation
```
[Create]
  ├─► display/fonts.py
  ├─► display/canvas.py
  ├─► display/touch_handler.py
  └─► display/shapes.py

[Migrate]
  └─► medicine_app.py (proof of concept)
```

### Phase 2.3 (Week 2) - Layouts & Text
```
[Create]
  ├─► display/layouts.py
  └─► display/text.py

[Migrate]
  ├─► weather_cal_app.py
  └─► mbta_app.py
```

### Phase 2.4 (Week 3) - Icons & Components
```
[Create]
  ├─► display/icons.py
  └─► display/components.py

[Migrate]
  ├─► disney_app.py
  ├─► flights_app.py
  ├─► pomodoro_app.py
  ├─► forbidden_app.py
  └─► reboot_app.py
```

### Phase 2.5 (Week 4) - Polish
```
[Complete]
  ├─► Integration testing
  ├─► Performance optimization
  ├─► Documentation
  └─► Code review
```

---

## Benefits Visualization

### Code Reduction by Category

```
Font Loading:        ████████████████████████████████████ 40 lines → 0 lines (100%)
Threading:           ████████████████████████████████████ 88 lines → 0 lines (100%)
Touch Handling:      ████████████████████████████████████ 60 lines → 0 lines (100%)
Image Creation:      ████████████████████████████████████ 80 lines → 2 lines (97%)
Headers/Footers:     ████████████████████████████████████ 32 lines → 4 lines (87%)
Centered Text:       ████████████████████████████████████ 36 lines → 3 lines (92%)
Icons:               ████████████████████ 216 lines → 36 lines (83%)
────────────────────────────────────────────────────────────────────────
TOTAL REDUCTION:     552 lines saved (88% duplication eliminated)
```

### Development Velocity Impact

```
Time to create new app:

Before:  ████████████████████ ~4 hours
         ├─ Copy boilerplate: 30 min
         ├─ Font setup: 15 min
         ├─ Touch handling: 20 min
         ├─ Layout code: 60 min
         ├─ Icon drawing: 45 min
         └─ App logic: 90 min

After:   ████████ ~1.5 hours
         ├─ Import components: 5 min
         ├─ Use layouts: 10 min
         ├─ Use icons: 5 min
         └─ App logic: 70 min

IMPROVEMENT: 2.5x faster development
```

---

## Summary

The component library provides:

✓ **Layered architecture** - Clean dependencies from foundation to app
✓ **Maximal reuse** - 88% duplication elimination
✓ **Easy migration** - Gradual, one app at a time
✓ **Clear ownership** - Each module has specific responsibility
✓ **Future proof** - Easy to extend with new components

**Next Action:** Proceed to Phase 2.2 implementation
