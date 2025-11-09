"""
TP_lib - Enhanced E-ink Display and Touch Controller Library
=============================================================

Improved version of Waveshare display drivers with:
- Hardware detection and automatic fallback to mock mode
- Better error handling and logging
- Performance optimizations
- Testing support with mock hardware

Compatible with Waveshare 2.13" V3/V4 e-ink displays and GT1151 touch controller.
"""

from .epd2in13_V3 import EPD as epd2in13_V3
from .epd2in13_V4 import EPD as epd2in13_V4
from .gt1151 import GT1151 as gt1151

__all__ = ['epd2in13_V3', 'epd2in13_V4', 'gt1151']
__version__ = '2.0.0'
