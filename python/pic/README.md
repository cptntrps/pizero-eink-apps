# Font Directory

This directory contains TrueType fonts used by the Pi Zero 2W display applications.

## Fonts Included

- **Roboto Family** - Google's modern, friendly sans-serif font
  - Roboto-Regular.ttf - Standard weight
  - Roboto-Bold.ttf - Bold weight
  - Roboto-Light.ttf - Light weight
  - Roboto-Medium.ttf - Medium weight
  - Roboto-Italic.ttf - Italic variant
  - And additional variants

## Font Source

Fonts are from the Roboto font family by Google:
- Repository: https://github.com/googlefonts/roboto
- License: Apache License 2.0
- Free for commercial and personal use

## Usage

Fonts are loaded by the `display/fonts.py` module using the font cache system:

```python
from display.fonts import get_font

# Load font
font = get_font('Roboto-Bold', 16)
draw.text((10, 10), "Hello", font=font, fill=0)
```

## Display Sizes

Common font sizes for 250x122 e-ink display:
- Tiny: 8-10pt
- Small: 12-14pt
- Body: 16-18pt
- Title: 20-24pt
- Large: 28-32pt
