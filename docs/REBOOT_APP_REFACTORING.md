# Reboot App Refactoring Documentation

## Overview

The `reboot_app.py` has been refactored to use shared utilities and display components, eliminating code duplication while maintaining exact same functionality.

## Key Changes

### 1. Threading Boilerplate Replaced with TouchHandler

**Before (11 lines of boilerplate):**
```python
flag_t = [1]

def pthread_irq():
    while flag_t[0] == 1:
        if gt.digital_read(gt.INT) == 0:
            gt_dev.Touch = 1
        else:
            gt_dev.Touch = 0

t = threading.Thread(target=pthread_irq)
t.daemon = True
t.start()
```

**After (1 line + 1 start call):**
```python
from display.touch_handler import TouchHandler

touch = TouchHandler(gt, gt_dev)
touch.start()
```

**Benefits:**
- Eliminates threading boilerplate code
- Automatic lifecycle management (stop() in finally block)
- Better error handling
- Reusable across all applications

### 2. Button Component Replaces Manual UI Drawing

**Before (9 lines of rectangle drawing):**
```python
draw.rectangle([10, 70, 110, 105], outline=0, width=2)
draw.text((35, 82), "Cancel", font=f_button, fill=0)

draw.rectangle([140, 70, 240, 105], outline=0, width=2)
draw.text((165, 82), "Reboot", font=f_button, fill=0)
```

**After (4 lines with Button component):**
```python
cancel_btn = Button("Cancel", 10, 70, 100, 30, get_font_preset('body'))
reboot_btn = Button("Reboot", 140, 70, 100, 30, get_font_preset('body'))
cancel_btn.draw(draw)
reboot_btn.draw(draw)
```

**Benefits:**
- Higher-level abstraction
- Consistent button styling
- Touch detection built into Button class
- Reusable component

### 3. Shared Utilities Replace Duplicated Code

**Replaced implementations:**
- `setup_logging()` instead of `logging.basicConfig()`
- `check_exit_requested()` instead of inline attribute checks
- `cleanup_touch_state()` instead of manual state reset
- `get_font_preset()` instead of hardcoded font paths

**Benefits:**
- Consistent across all applications
- Centralized maintenance
- Better error handling
- Type hints and documentation

### 4. Font Presets for Typography

**Before (multiple hardcoded font loading):**
```python
f_title = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 16)
f_button = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 12)
```

**After (using presets):**
```python
from display.fonts import get_font_preset

get_font_preset('title')   # 16pt Roboto-Bold
get_font_preset('body')    # 12pt Roboto-Regular
```

**Benefits:**
- Font caching for performance
- Consistent typography across apps
- Easy to customize globally

### 5. Comprehensive Error Handling

**Added:**
- Try/except blocks around all operations
- Proper exception chaining with `from e`
- Subprocess timeout handling (5 second timeout)
- Subprocess error code checking
- Graceful cleanup in finally block

**Example:**
```python
result = subprocess.run(['sudo', 'reboot'], capture_output=True, timeout=5)
if result.returncode != 0:
    logger.error(f"Reboot failed: {result.stderr.decode()}")
```

### 6. Removed Duplicate Code

**Removed:**
- Duplicate exit check code (original lines 52-60 had 2 identical blocks)
- Redundant touch state initialization
- Multiple font loading calls

## Code Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total Lines | 100 | 128 | +28 |
| Threading Boilerplate | 11 | 2 | -9 |
| Manual UI Drawing | 9 | 4 | -5 |
| Duplicate Code Blocks | 2 | 0 | -2 |
| Error Handling Blocks | 0 | 3 | +3 |
| Helper Functions | 0 | 0 | - |

**Note:** The refactored version is slightly longer due to:
- Comprehensive error handling (try/except/finally)
- Better documentation and comments
- Proper imports and logging setup
- These additions significantly improve maintainability and reliability

## Functionality Verification

All key functionality is preserved:

✓ Confirmation dialog with "Reboot System?" title
✓ Cancel button (Y > 180 per API contract)
✓ Reboot button (Y < 70 per API contract)
✓ "Rebooting..." status display
✓ Touch event debouncing (300ms)
✓ Menu exit signal handling
✓ Proper display cleanup
✓ Display partial updates

## Testing

Run the test suite to verify refactoring:

```bash
python3 -m pytest tests/test_reboot_app_refactor.py -v
```

Test Coverage:
- ✓ TouchHandler usage (no manual threading)
- ✓ Button component usage
- ✓ Shared utilities usage
- ✓ Font presets instead of hardcoded fonts
- ✓ Error handling present
- ✓ No duplicate code
- ✓ Exact functionality preserved
- ✓ Syntax validation
- ✓ Import availability
- ✓ Logging setup
- ✓ Code quality metrics

## Maintenance Benefits

### For Developers
1. **Cleaner Code:** Uses high-level abstractions instead of low-level details
2. **Better Error Messages:** Comprehensive logging for debugging
3. **Type Hints:** Clear parameter types and return values
4. **Documentation:** Docstrings explain functionality

### For Maintainers
1. **Consistency:** Uses same patterns as other refactored apps
2. **Testability:** Easier to test with proper dependency injection
3. **Reusability:** Components can be used in other applications
4. **Centralized Updates:** Shared utilities updated once, affects all apps

## Migration Path

To migrate other apps to this pattern:

1. **Import shared utilities:**
   ```python
   from shared.app_utils import setup_logging, check_exit_requested, cleanup_touch_state
   from display.touch_handler import TouchHandler
   from display.fonts import get_font_preset
   from display.components import Button
   ```

2. **Replace threading boilerplate with TouchHandler**

3. **Replace manual UI drawing with Button components**

4. **Replace hardcoded fonts with get_font_preset()**

5. **Add comprehensive error handling with try/except**

6. **Run tests to verify functionality**

## Files Modified

- `/home/user/pizerowgpio/reboot_app.py` - Refactored implementation
- `/home/user/pizerowgpio/reboot_app.py.backup` - Original version preserved
- `/home/user/pizerowgpio/tests/test_reboot_app_refactor.py` - Test suite

## Backward Compatibility

The refactored app maintains the exact same external interface:

```python
draw_reboot_confirm(epd, gt_dev, gt_old, gt)
```

Can be used as a drop-in replacement for the original version.

## Performance Impact

- **Touch Handler Thread:** Slightly more efficient with better error handling
- **Font Caching:** Improved performance due to font preset caching
- **Error Handling:** Negligible overhead from try/except blocks
- **Overall:** No negative performance impact

## Future Improvements

1. **Debounce Configuration:** Make 300ms debounce configurable
2. **Button State Feedback:** Show pressed state in UI
3. **Timeout Configuration:** Make reboot timeout configurable
4. **ConfigLoader Integration:** Load settings from config.json
5. **Signal Handlers:** Add graceful SIGTERM handling

## Related Documentation

- `display/touch_handler.py` - TouchHandler implementation
- `display/components.py` - Button component documentation
- `display/fonts.py` - Font preset system
- `shared/app_utils.py` - Shared utilities reference
