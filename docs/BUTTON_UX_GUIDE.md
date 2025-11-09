# Button-Only UX Guide
## Single Button Navigation for Pi Zero 2W E-ink Apps

**Hardware:** PiSugar battery button on GPIO 3

**Input Types:**
- **SHORT PRESS:** Quick tap (<2 seconds)
- **LONG PRESS:** Hold button (≥2 seconds)

---

## Universal Principles

1. **Visual Feedback:** Always show which item is selected/highlighted
2. **On-Screen Instructions:** Display "Press: Next | Hold: [Action]" at bottom
3. **Consistent Exit:** LONG PRESS always exits to menu when no other action
4. **Cyclic Navigation:** SHORT PRESS cycles through options in a loop

---

## App-Specific Navigation Patterns

### 1. Menu (menu_button.py)

**Display:**
```
PiZero Menu
─────────────
> Weather & Calendar    ← Highlighted
  Flights Above Me
  MBTA Trains
  Disney Wait Times
  ...

Press: Next  |  Hold 2s: Select
```

**Interactions:**
- **SHORT PRESS:** Move highlight to next app (cycles to top)
- **LONG PRESS:** Launch highlighted app

---

### 2. Medicine Tracker

**Scenario A: Pending Medicines**

**Display:**
```
MEDICINE TRACKER
─────────────────
⏰ Morning Medicines Due

► Vitamin D (2000 IU)    ← Current
  1 pill with food
  Due: 08:00-10:00

  [1 of 3 pending]

Press: Next Med  |  Hold: Mark Taken
```

**Interactions:**
- **SHORT PRESS:** Next pending medicine in list
- **LONG PRESS:** Mark current medicine as taken
  - Shows confirmation: "✓ Vitamin D marked as taken"
  - Auto-advances to next pending medicine
  - If last medicine: Shows summary screen

**Scenario B: No Pending Medicines**

**Display:**
```
MEDICINE TRACKER
─────────────────
✓ All medicines taken!

Today's Adherence: 4/5 (80%)

Next dose: Vyvanse
Due in 2 hours (12:00)

Press: View Stats  |  Hold: Exit
```

**Interactions:**
- **SHORT PRESS:** Cycle through: Summary → Today's List → Week View
- **LONG PRESS:** Exit to menu

---

### 3. Weather & Calendar

**Display:**
```
WEATHER - TODAY
─────────────────
Boston, MA

🌤️  Partly Cloudy
72°F (feels like 70°F)
Humidity: 65%
Wind: 8 mph NE

Tomorrow: Sunny 75°

Press: Next Day  |  Hold: Exit
```

**Interactions:**
- **SHORT PRESS:** Cycle through: Today → Tomorrow → 7-Day Forecast
- **LONG PRESS:** Exit to menu

---

### 4. MBTA Trains

**Display:**
```
MBTA - ORANGE LINE
─────────────────
► Forest Hills → Oak Grove

Next Arrivals:
  2 min
  8 min
  15 min

Updated: 10:34 AM

Press: Next Route  |  Hold: Exit
```

**Interactions:**
- **SHORT PRESS:** Cycle through configured routes
- **LONG PRESS:** Exit to menu

---

### 5. Disney Wait Times

**Display:**
```
DISNEY WAIT TIMES
─────────────────
Magic Kingdom

► Space Mountain        ← Current
   Wait: 45 minutes
   Status: OPEN

  [Ride 1 of 12]

Press: Next Ride  |  Hold: Exit
```

**Interactions:**
- **SHORT PRESS:** Next ride in list
- **LONG PRESS:** Exit to menu

---

### 6. Flights Above

**Display:**
```
FLIGHTS ABOVE ME
─────────────────
Boston, MA

► UAL2341  Airbus A320    ← Current
  ✈ Denver → Boston
  Alt: 3,200 ft
  Speed: 245 mph

  [Aircraft 3 of 7]

Press: Next  |  Hold: Exit
```

**Interactions:**
- **SHORT PRESS:** Next aircraft
- **LONG PRESS:** Exit to menu

---

### 7. Pomodoro Timer

**State A: Stopped**

**Display:**
```
POMODORO TIMER
─────────────────
Ready to Start

Duration: ► 25 minutes    ← Selected
          20 minutes
          15 minutes

Press: Change Time  |  Hold: Start
```

**Interactions:**
- **SHORT PRESS:** Cycle through durations (25/20/15 min)
- **LONG PRESS:** Start timer

**State B: Running**

**Display:**
```
POMODORO TIMER
─────────────────
🍅 FOCUS MODE

    18:45
  remaining

Started: 10:30 AM

Press: [None]  |  Hold: Stop
```

**Interactions:**
- **SHORT PRESS:** (disabled during timer)
- **LONG PRESS:** Stop timer and return to setup

---

### 8. Forbidden Island (Game)

**Display:**
```
FORBIDDEN ISLAND
─────────────────
Water Level: 3/10 ⬆

Actions Remaining: ► 3    ← Adjustable
Treasures Found: 1/4

Press: Change  |  Hold: Update
```

**Interactions:**
- **SHORT PRESS:** Cycle through game state options
- **LONG PRESS:** Confirm changes / Exit to menu

---

### 9. System Reboot

**Display:**
```
SYSTEM REBOOT
─────────────────
⚠️  Warning!

This will restart the
Raspberry Pi.

► Cancel              ← Selected
  Reboot Now

Press: Toggle  |  Hold: Confirm
```

**Interactions:**
- **SHORT PRESS:** Toggle between Cancel / Reboot
- **LONG PRESS:** Execute selected option

---

## Implementation Guidelines

### For App Developers

1. **Use ButtonInputHandler:**
```python
from display.button_input import ButtonInputHandler

button = ButtonInputHandler(gpio_pin=3)
button.on_short_press = handle_short_press
button.on_long_press = handle_long_press
button.start()
```

2. **Always Show Current State:**
- Use `►` or highlight to show selection
- Show pagination: `[2 of 5]`
- Display instructions at bottom

3. **Cyclic Navigation:**
```python
def handle_short_press():
    global current_index
    current_index = (current_index + 1) % total_items
    redraw_screen()
```

4. **Long Press Exit:**
```python
def handle_long_press():
    if has_action:
        perform_action()
    else:
        exit_to_menu()
```

5. **Visual Feedback:**
- Use partial refresh for navigation (fast)
- Use full refresh for state changes (crisp)
- Show confirmation screens (1-2 seconds)

---

## Configuration

Add to `config.json`:

```json
{
  "hardware": {
    "input_mode": "button",
    "button": {
      "gpio_pin": 3,
      "long_press_threshold": 2.0,
      "bounce_time": 0.1,
      "pull_up": true
    }
  }
}
```

---

## Testing Checklist

For each app, verify:

- [ ] SHORT PRESS navigates correctly
- [ ] LONG PRESS performs correct action
- [ ] Navigation loops/cycles properly
- [ ] Visual highlight is clear
- [ ] Instructions shown at bottom
- [ ] Partial refresh for navigation (fast)
- [ ] Full refresh for actions (crisp)
- [ ] Exit to menu works
- [ ] No touchscreen code dependencies

---

## Migration from Touchscreen

**Remove:**
```python
# Old touchscreen code
if gt_dev.Touch == 1:
    if 10 < gt_dev.X[0] < 100:
        handle_click()
```

**Replace with:**
```python
# New button code
button.on_short_press = handle_next
button.on_long_press = handle_action
```

**Delete:**
- All `gt`, `gt_dev`, `gt_old` references
- All X/Y coordinate checking
- TouchHandler imports and usage

---

## Future Enhancements

Potential additions (optional):
- Visual progress bar for long press (shows 2s countdown)
- Haptic feedback (if hardware added)
- Configurable press thresholds
- Accessibility options (longer thresholds)

---

**Last Updated:** 2025-11-08
**Hardware:** Raspberry Pi Zero 2W + 2.13" e-ink + PiSugar Button
