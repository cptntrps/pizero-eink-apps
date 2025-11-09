"""
Font Caching System
===================

Provides efficient font loading with caching to avoid repeated disk I/O.
Includes named presets for consistent typography across applications.

Performance: Font cache reduces load time from ~50ms to <1ms per font access.
"""

import os
from typing import Dict, Tuple
from PIL import ImageFont


# ============================================================================
# FONT PATHS
# ============================================================================

def get_font_dir() -> str:
    """Get directory containing font files

    Returns:
        str: Absolute path to font directory
    """
    base = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    return os.path.join(base, 'python/pic')


# ============================================================================
# FONT CACHE
# ============================================================================

_font_cache: Dict[Tuple[str, int], ImageFont.FreeTypeFont] = {}


def get_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Get font with caching to avoid repeated disk loads

    Loads font from disk only on first access, subsequent calls return
    cached instance for significant performance improvement.

    Args:
        name: Font name without extension (e.g., 'Roboto-Bold', 'Roboto-Regular')
        size: Font size in points

    Returns:
        PIL ImageFont object ready for drawing

    Raises:
        OSError: If font file not found

    Example:
        >>> font = get_font('Roboto-Bold', 16)
        >>> draw.text((10, 10), "Hello", font=font, fill=0)
    """
    key = (name, size)

    if key not in _font_cache:
        font_path = os.path.join(get_font_dir(), f"{name}.ttf")
        _font_cache[key] = ImageFont.truetype(font_path, size)

    return _font_cache[key]


def clear_font_cache() -> None:
    """Clear the font cache

    Useful for testing or freeing memory. In production, cache should
    remain populated for performance.

    Example:
        >>> clear_font_cache()
        >>> # Cache is empty, next get_font() will reload from disk
    """
    _font_cache.clear()


def get_cache_size() -> int:
    """Get number of fonts currently cached

    Returns:
        int: Number of cached font instances

    Example:
        >>> size = get_cache_size()
        >>> print(f"Cache contains {size} fonts")
    """
    return len(_font_cache)


# ============================================================================
# FONT PRESETS
# ============================================================================

# Typography system for consistent styling
FONT_PRESETS = {
    # Headlines and titles
    'headline': ('Roboto-Bold', 20),
    'title': ('Roboto-Bold', 16),
    'subtitle': ('Roboto-Bold', 14),

    # Body text
    'body': ('Roboto-Regular', 12),
    'body_bold': ('Roboto-Bold', 12),

    # Small text
    'small': ('Roboto-Regular', 10),
    'small_bold': ('Roboto-Bold', 10),

    # Tiny text (use sparingly, readability concern)
    'tiny': ('Roboto-Regular', 9),

    # Display text (large)
    'display': ('Roboto-Bold', 24),
    'display_huge': ('Roboto-Bold', 48),
}


def get_font_preset(preset: str) -> ImageFont.FreeTypeFont:
    """Get font using named preset for consistent typography

    Presets ensure consistent font usage across all applications.

    Available presets:
        - headline: Large bold headlines (20pt)
        - title: Section titles (16pt bold)
        - subtitle: Subsection titles (14pt bold)
        - body: Normal text (12pt regular)
        - body_bold: Emphasized text (12pt bold)
        - small: Small text (10pt regular)
        - small_bold: Small emphasized text (10pt bold)
        - tiny: Very small text (9pt regular)
        - display: Large display text (24pt bold)
        - display_huge: Extra large display (48pt bold)

    Args:
        preset: Preset name from FONT_PRESETS

    Returns:
        PIL ImageFont object

    Raises:
        KeyError: If preset name not found

    Example:
        >>> font = get_font_preset('headline')
        >>> draw.text((10, 10), "Title", font=font, fill=0)
    """
    if preset not in FONT_PRESETS:
        available = ', '.join(FONT_PRESETS.keys())
        raise KeyError(
            f"Unknown font preset '{preset}'. "
            f"Available presets: {available}"
        )

    name, size = FONT_PRESETS[preset]
    return get_font(name, size)


def list_presets() -> list:
    """Get list of available font preset names

    Returns:
        list: Sorted list of preset names

    Example:
        >>> presets = list_presets()
        >>> print("Available presets:", ", ".join(presets))
    """
    return sorted(FONT_PRESETS.keys())


# ============================================================================
# FONT PRELOADING
# ============================================================================

def preload_common_fonts() -> None:
    """Preload commonly used fonts into cache

    Call at application startup to load frequently used fonts
    into memory before they're needed, reducing first-draw latency.

    Example:
        >>> # At app startup
        >>> preload_common_fonts()
        >>> # Now all common fonts are cached
    """
    common_presets = ['headline', 'title', 'body', 'small']

    for preset in common_presets:
        get_font_preset(preset)


def preload_all_presets() -> None:
    """Preload all preset fonts into cache

    Loads all defined presets. Use if memory is not a concern
    and you want maximum performance.

    Example:
        >>> preload_all_presets()
    """
    for preset in FONT_PRESETS.keys():
        get_font_preset(preset)
