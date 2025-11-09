#!/usr/bin/python3
"""
Validate Display Package Structure
===================================

Tests that all modules are importable and have correct structure.
Does not require PIL or hardware.
"""

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")

    modules = [
        'display',
        'display.fonts',
        'display.canvas',
        'display.touch_handler',
        'display.shapes',
        'display.text',
        'display.icons',
        'display.layouts',
        'display.components',
    ]

    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError as e:
            print(f"  ✗ {module}: {e}")
            return False

    return True


def test_package_exports():
    """Test that package exports are correct"""
    print("\nTesting package exports...")

    try:
        import display

        exports = [
            'get_font', 'get_font_preset', 'clear_font_cache',
            'create_canvas', 'Canvas',
            'TouchHandler',
            'draw_line', 'draw_rectangle', 'draw_circle',
            'draw_horizontal_line', 'draw_vertical_line',
            'draw_centered_text', 'draw_wrapped_text',
            'truncate_text', 'get_text_size',
        ]

        for export in exports:
            if hasattr(display, export):
                print(f"  ✓ display.{export}")
            else:
                print(f"  ✗ display.{export} not found")
                return False

        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_module_functions():
    """Test that key functions exist"""
    print("\nTesting module functions...")

    tests = [
        ('display.fonts', ['get_font', 'get_font_preset', 'clear_font_cache', 'list_presets']),
        ('display.canvas', ['create_canvas', 'get_display_dimensions', 'get_display_center']),
        ('display.touch_handler', ['TouchHandler', 'check_exit_requested', 'cleanup_touch_state']),
        ('display.shapes', ['draw_line', 'draw_rectangle', 'draw_circle', 'draw_divider']),
        ('display.text', ['get_text_size', 'draw_centered_text', 'truncate_text', 'wrap_text']),
        ('display.icons', ['draw_pill_icon', 'draw_weather_icon', 'draw_compass_icon']),
        ('display.layouts', ['HeaderLayout', 'FooterLayout', 'SplitLayout', 'ListLayout']),
        ('display.components', ['StatusBar', 'ProgressBar', 'Button', 'ListItem']),
    ]

    for module_name, functions in tests:
        module = __import__(module_name, fromlist=[''])
        print(f"\n  {module_name}:")
        for func in functions:
            if hasattr(module, func):
                print(f"    ✓ {func}")
            else:
                print(f"    ✗ {func} not found")
                return False

    return True


def test_constants():
    """Test that constants are defined"""
    print("\nTesting constants...")

    from display.canvas import DISPLAY_WIDTH, DISPLAY_HEIGHT

    if DISPLAY_WIDTH == 250 and DISPLAY_HEIGHT == 122:
        print(f"  ✓ Display dimensions: {DISPLAY_WIDTH}×{DISPLAY_HEIGHT}")
    else:
        print(f"  ✗ Incorrect display dimensions")
        return False

    from display.fonts import FONT_PRESETS

    if len(FONT_PRESETS) > 0:
        print(f"  ✓ Font presets defined: {len(FONT_PRESETS)}")
    else:
        print(f"  ✗ No font presets found")
        return False

    return True


def test_documentation():
    """Test that modules have docstrings"""
    print("\nTesting documentation...")

    modules = [
        'display',
        'display.fonts',
        'display.canvas',
        'display.touch_handler',
        'display.shapes',
        'display.text',
        'display.icons',
        'display.layouts',
        'display.components',
    ]

    for module_name in modules:
        module = __import__(module_name, fromlist=[''])
        if module.__doc__:
            doc_lines = len(module.__doc__.strip().split('\n'))
            print(f"  ✓ {module_name}: {doc_lines} lines")
        else:
            print(f"  ✗ {module_name}: No docstring")
            return False

    return True


def main():
    """Run all validation tests"""
    print("=" * 70)
    print("DISPLAY COMPONENT LIBRARY - STRUCTURE VALIDATION")
    print("=" * 70)

    tests = [
        ("Module Imports", test_imports),
        ("Package Exports", test_package_exports),
        ("Module Functions", test_module_functions),
        ("Constants", test_constants),
        ("Documentation", test_documentation),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  Error in {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False

    print("=" * 70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("\nThe display component library is correctly structured.")
        print("Ready for use in Pi Zero 2W applications!")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("\nPlease fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
