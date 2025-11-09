# \!/usr/bin/python3
import medicine_app
import mbta_app
import disney_app
import pomodoro_app
import flights_app
import reboot_app
import weather_cal_app
import forbidden_app
import threading
import logging
from PIL import Image, ImageDraw, ImageFont
from TP_lib import gt1151, epd2in13_V4 as epd2in13_V3
import sys
import os
import time
picdir = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.realpath(__file__))),
    'python/pic/2in13')
fontdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'python/lib')
icondir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'icons')
sys.path.append(libdir)

logging.basicConfig(level=logging.INFO)

APPS = [
    {"name": "Weather &\nCalendar", "icon": "calendar.bmp", "func": "weather"},
    {"name": "Flights\nAbove Me", "icon": "flight.bmp", "func": "flights"},
    {"name": "MBTA\nTrains", "icon": "mbta.bmp", "func": "mbta"},
    {"name": "Disney\nWait Times", "icon": "disney.bmp", "func": "disney"},
    {"name": "Pomodoro\nTimer", "icon": "clock.bmp", "func": "pomodoro"},
    {"name": "Reboot\nSystem", "icon": "reboot.bmp", "func": "reboot"},
    {"name": "Sai\nCurioso", "icon": "forbidden.bmp", "func": "forbidden"}
]
current_app = 0
flag_t = 1


def pthread_irq():
    while flag_t == 1:
        if gt.digital_read(gt.INT) == 0:
            GT_Dev.Touch = 1
        else:
            GT_Dev.Touch = 0
        time.sleep(0.01)


def draw_menu():
    img = Image.new('1', (250, 122), 255)
    draw = ImageDraw.Draw(img)
    f_small = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 12)
    f_arrow = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 40)
    f_tiny = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Regular.ttf'), 10)

    draw.text((5, 5), "PiZero Menu", font=f_tiny, fill=0)
    draw.text((10, 45), "<", font=f_arrow, fill=0)
    draw.text((220, 45), ">", font=f_arrow, fill=0)

    app = APPS[current_app]

    try:
        icon_path = os.path.join(icondir, app["icon"])
        icon = Image.open(icon_path)
        img.paste(icon, ((250 - icon.width) // 2, 25))
    except BaseException:
        pass

    lines = app["name"].split("\n")
    y_offset = 90
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f_small)
        w = bbox[2] - bbox[0]
        draw.text(((250 - w) // 2, y_offset), line, font=f_small, fill=0)
        y_offset += 14

    return img


try:
    logging.info("Starting menu")
    epd = epd2in13_V3.EPD()
    gt = gt1151.GT1151()
    GT_Dev = gt1151.GT_Development()
    GT_Old = gt1151.GT_Development()

    epd.init(epd.FULL_UPDATE)
    gt.GT_Init()
    epd.Clear(0xFF)

    t = threading.Thread(target=pthread_irq)
    t.daemon = True
    t.start()

    image = draw_menu()
    epd.displayPartBaseImage(epd.getbuffer(image))
    epd.init(epd.PART_UPDATE)

    logging.info("Menu ready")

    while True:
        time.sleep(0.01)
        gt.GT_Scan(GT_Dev, GT_Old)

        if GT_Old.X[0] == GT_Dev.X[0] and GT_Old.Y[0] == GT_Dev.Y[0] and GT_Old.S[0] == GT_Dev.S[0]:
            continue

        if GT_Dev.TouchpointFlag:
            GT_Dev.TouchpointFlag = 0
            x, y = GT_Dev.X[0], GT_Dev.Y[0]

            if y < 70:
                current_app = (current_app - 1) % len(APPS)
                image = draw_menu()
                epd.displayPartial(epd.getbuffer(image))

            elif y > 180:
                current_app = (current_app + 1) % len(APPS)
                image = draw_menu()
                epd.displayPartial(epd.getbuffer(image))

            elif 70 <= y <= 180:
                app = APPS[current_app]
                logging.info(f"LAUNCH: {app['name'].replace(chr(10), ' ')}")

                if app["func"] == "weather":
                    weather_cal_app.run_weather_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "reboot":
                    reboot_app.draw_reboot_confirm(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "flights":
                    flights_app.run_flights_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "pomodoro":
                    pomodoro_app.run_pomodoro_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "disney":
                    disney_app.run_disney_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "mbta":
                    mbta_app.run_mbta_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "medicine":
                    medicine_app.run_medicine_app(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                elif app["func"] == "forbidden":
                    forbidden_app.draw_forbidden_message(epd, GT_Dev, GT_Old, gt)
                    GT_Old.X[0] = 0
                    GT_Old.Y[0] = 0
                    GT_Old.S[0] = 0
                    GT_Dev.TouchpointFlag = 0
                    epd.init(epd.FULL_UPDATE)
                    epd.Clear(0xFF)
                    image = draw_menu()
                    epd.displayPartBaseImage(epd.getbuffer(image))
                    epd.init(epd.PART_UPDATE)
                    logging.info("Back to menu")
                    time.sleep(1)

                else:
                    img = Image.new('1', (250, 122), 255)
                    draw = ImageDraw.Draw(img)
                    f = ImageFont.truetype(os.path.join(fontdir, 'Roboto-Bold.ttf'), 14)
                    draw.text((30, 50), "Coming soon\\!", font=f, fill=0)
                    epd.displayPartial(epd.getbuffer(img))
                    time.sleep(2)
                    image = draw_menu()
                    epd.displayPartial(epd.getbuffer(image))

            time.sleep(0.2)

except KeyboardInterrupt:
    flag_t = 0
    epd2in13_V3.epdconfig.module_exit()
