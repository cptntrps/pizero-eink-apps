# \!/usr/bin/python3
from PIL import Image, ImageDraw


def create_weather_icon():
    """Sun with clouds icon"""
    img = Image.new('1', (60, 60), 255)
    draw = ImageDraw.Draw(img)

    # Sun circle
    draw.ellipse([10, 10, 30, 30], fill=0, outline=0)
    # Sun rays
    draw.line([20, 5, 20, 8], fill=0, width=2)
    draw.line([20, 32, 20, 35], fill=0, width=2)
    draw.line([5, 20, 8, 20], fill=0, width=2)
    draw.line([32, 20, 35, 20], fill=0, width=2)
    draw.line([10, 10, 12, 12], fill=0, width=2)
    draw.line([28, 28, 30, 30], fill=0, width=2)
    draw.line([10, 30, 12, 28], fill=0, width=2)
    draw.line([28, 12, 30, 10], fill=0, width=2)

    # Cloud
    draw.ellipse([15, 35, 30, 45], outline=0, width=2)
    draw.ellipse([25, 32, 40, 42], outline=0, width=2)
    draw.ellipse([35, 35, 50, 45], outline=0, width=2)

    img.save('icons/weather.bmp')
    print("Created weather icon")


def create_flight_icon():
    """Airplane with radar waves"""
    img = Image.new('1', (60, 60), 255)
    draw = ImageDraw.Draw(img)

    # Airplane body (side view)
    draw.polygon([
        (30, 25),  # nose
        (35, 30),  # top
        (35, 32),  # tail top
        (25, 32),  # tail bottom
        (25, 30),  # bottom
    ], fill=0)

    # Wings
    draw.polygon([(27, 30), (27, 20), (32, 28)], fill=0)

    # Tail wing
    draw.polygon([(32, 27), (32, 22), (34, 27)], fill=0)

    # Radar waves (concentric arcs)
    for r in range(15, 46, 10):
        draw.arc([30 - r, 30 - r, 30 + r, 30 + r], start=0, end=360, fill=0, width=1)

    img.save('icons/flight.bmp')
    print("Created flight icon")


def create_system_icon():
    """Cog/gear icon"""
    img = Image.new('1', (60, 60), 255)
    draw = ImageDraw.Draw(img)

    # Outer gear teeth (simplified)
    center_x, center_y = 30, 30
    outer_r = 22
    inner_r = 18

    # Draw gear as octagon with teeth
    import math
    points_outer = []
    points_inner = []

    for i in range(16):
        angle = i * (360 / 16)
        rad = math.radians(angle)
        r = outer_r if i % 2 == 0 else inner_r
        x = center_x + r * math.cos(rad)
        y = center_y + r * math.sin(rad)
        points_outer.append((x, y))

    draw.polygon(points_outer, outline=0, width=2)

    # Inner circle
    draw.ellipse([center_x - 8, center_y - 8, center_x + 8, center_y + 8], fill=0)
    # Center hole
    draw.ellipse([center_x - 4, center_y - 4, center_x + 4, center_y + 4], fill=255, outline=0)

    img.save('icons/system.bmp')
    print("Created system icon")


# Create all icons
create_weather_icon()
create_flight_icon()
create_system_icon()
print("All icons created\\!")
