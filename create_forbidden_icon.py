# \!/usr/bin/python3
from PIL import Image, ImageDraw


def create_forbidden_icon():
    """Forbidden/do not enter icon"""
    img = Image.new('1', (60, 60), 255)
    draw = ImageDraw.Draw(img)

    # Outer circle
    draw.ellipse([5, 5, 55, 55], outline=0, width=3)

    # Diagonal line (top-left to bottom-right)
    draw.line([15, 15, 45, 45], fill=0, width=4)

    img.save('icons/forbidden.bmp')
    print("Created forbidden icon")


create_forbidden_icon()
