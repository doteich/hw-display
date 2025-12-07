import os
import time
import threading
from datetime import datetime
from PIL import ImageFont, Image, ImageDraw
import shared

from config import loadConfig
from webserver import run_flask_server

# import RPi.GPIO as GPIO

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.oled.device import ssd1322
from luma.core.virtual import viewport, snapshot
from luma.core.sprite_system import framerate_regulator

display_off = False

def makeFont(name, size):
    font_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'fonts',
            name
        )
    )
    return ImageFont.truetype(font_path, size, layout_engine=ImageFont.Layout.BASIC)


bitmapRenderCache = {}


def cachedBitmapText(text, font):
    # cache the bitmap representation of the stations string
    nameTuple = font.getname()
    fontKey = ''
    for item in nameTuple:
        fontKey = fontKey + item
    key = text + fontKey
    if key in bitmapRenderCache:
        # found in cache; re-use it
        pre = bitmapRenderCache[key]
        bitmap = pre['bitmap']
        txt_width = pre['txt_width']
        txt_height = pre['txt_height']
    else:
        # not cached; create a new image containing the string as a monochrome bitmap
        _, _, txt_width, txt_height = font.getbbox(text)
        bitmap = Image.new('L', [txt_width, txt_height], color=0)
        pre_render_draw = ImageDraw.Draw(bitmap)
        pre_render_draw.text((0, 0), text=text, font=font, fill=255)
        # save to render cache
        bitmapRenderCache[key] = {
            'bitmap': bitmap, 'txt_width': txt_width, 'txt_height': txt_height}
    return txt_width, txt_height, bitmap


pixelsLeft = 1
pixelsUp = 0
hasElevated = 0
pauseCount = 0


def drawTextByInput(text, width, start, offset, center):

    left_bound = 1

    if center:
        size = int(fontBold.getlength(text))
        left_bound = int(width - size)/2
    else:
        left_bound = start

    def drawText(draw, *_):
        draw.text((left_bound, offset), text=text,
                  font=fontBold, fill="yellow")
    return drawText


def drawRectangle(left, right, top, bottom):
    def drawRect(draw, *_):
        draw.rectangle((left, top, right, bottom),
                       outline="yellow", fill="black")
    return drawRect


def drawWelcomeText(width, height, text):

    w_offset = int((width-(fontBold.getlength(text)))/2)

    def welcome(draw, *_):
        draw.rectangle((5, 5, width-5, height-5),
                       outline="yellow", fill="black")
        draw.text((w_offset, (height/2)-5), text,
                  font=fontBold, fill="yellow")
    return welcome


def drawStartup(device, width, height):
    virtualViewport = viewport(device, width=width, height=height)

    with canvas(device):

        rowOne = snapshot(width, height, drawWelcomeText(
            width, height, "WELCOME FROM HW MONITOR"), interval=10)
        virtualViewport.add_hotspot(rowOne, (0, 0))

    return virtualViewport


def drawSplitBox(width, height, header1, content1, header2, content2):
    def drawSplit(draw, *_):

        w_offset_1 = int(((width / 2) - (fontBold.getlength(content1)))/2)
        w_offset_2 = int(
            ((width / 2) - (fontBold.getlength(content2)))/2) + width/2

        draw.rectangle((0, 0, width/2, height),
                       outline="yellow", fill="black")
        draw.rectangle(((width/2)+1, 0, width-1, height),
                       outline="yellow", fill="black")
        draw.text((5, 3), text=header1,
                  font=font, fill="yellow")
        draw.text((w_offset_1, height/2), text=content1,
                  font=fontBold, fill="yellow")
        draw.text(((width/2)+5, 3), text=header2,
                  font=font, fill="yellow")
        draw.text((w_offset_2, height/2), text=content2,
                  font=fontBold, fill="yellow")
    return drawSplit


def drawFullBox(width, height, header, content):
    w_offset = int((width - (fontBold.getlength(content)))/2)

    def drawBox(draw, *_):
        draw.rectangle((0, 0, width-1, height),
                       outline="yellow", fill="black")
        draw.text((5, 3), text=header,
                  font=font, fill="yellow")
        draw.text((w_offset, height/2), text=content,
                  font=fontBold, fill="yellow")
    return drawBox


def drawGPUScreen(device, width, height):
    virtualViewport = viewport(device, width=width, height=height)

    with canvas(device):

        rowOne = snapshot(width, 14, drawTextByInput(
            "GPU", width, 0, 1, True), interval=10)
        rowTwo = snapshot(width, 26, drawSplitBox(
            width, 26, "Load", str(shared.hardwareData["gpu_load"])+" %", "VRAM",  str(shared.hardwareData["gpu_mem_used"])+" MB"), interval=10)
        rowThree = snapshot(width, 26, drawFullBox(width, 25, "Temperature", str(
            shared.hardwareData["gpu_temp"])+" C"), interval=10)

        virtualViewport.add_hotspot(rowOne, (0, 0))
        virtualViewport.add_hotspot(rowTwo, (0, 10))
        virtualViewport.add_hotspot(rowThree, (0, 36))
    return virtualViewport


def drawCPUScreen(device, width, height):
    virtualViewport = viewport(device, width=width, height=height)

    with canvas(device):

        rowOne = snapshot(width, 14, drawTextByInput(
            "CPU", width, 0, 1, True), interval=10)
        rowTwo = snapshot(width, 26, drawSplitBox(
            width, 26, "Load", f"{shared.hardwareData["cpu_load"]:.2f} %", "RAM Used",  f"{shared.hardwareData["mem_used"]:.2f} GB"), interval=10)
        rowThree = snapshot(width, 25, drawFullBox(
            width, 26, "Temperature", f"{shared.hardwareData["cpu_temp"]:.2f} C"), interval=10)

        virtualViewport.add_hotspot(rowOne, (0, 0))
        virtualViewport.add_hotspot(rowTwo, (0, 10))
        virtualViewport.add_hotspot(rowThree, (0, 36))
    return virtualViewport


try:

    config = loadConfig()
    config["headless"] = True
    if config['headless']:
        print('Running in Emulator mode (Local Dev)')
        from luma.emulator.device import pygame
        # This creates a popup window on your PC simulating the 256x64 screen
        device = pygame(width=256, height=64, mode="1", transform="scale2x")
    else:
        GPIO.setwarnings(False)
        serial = spi(port=0)
        device = ssd1322(serial, mode="1", rotate=0)

    font = makeFont("Dot Matrix Regular.ttf", 10)
    fontBold = makeFont("Dot Matrix Bold.ttf", 10)
    fontBoldTall = makeFont("Dot Matrix Bold Tall.ttf", 10)
    fontBoldLarge = makeFont("Dot Matrix Bold.ttf", 20)

    widgetWidth = 256
    widgetHeight = 64

    pauseCount = 0
    loop_count = 0

    regulator = framerate_regulator(config['targetFPS'])

    server_thread = threading.Thread(target=run_flask_server)

    # Daemon threads automatically shut down when the main program exits
    server_thread.daemon = True
    server_thread.start()

    print("--- Starting Main ---")

    virtual = drawStartup(device, width=widgetWidth, height=widgetHeight)
    virtual.refresh()
    time.sleep(10)

    while True:
        delta = datetime.now() - shared.last_update
        print(delta.seconds)
        if delta.seconds > 20:
            print(f"received last update over {delta.seconds}s ago")
            if display_off == False:
                display_off = True
                device.hide()
            time.sleep(20)
        else:
            if display_off == True:
                device.show()
                display_off = False
            virtual = drawGPUScreen(device, width=widgetWidth, height=widgetHeight)
            virtual.refresh()
            time.sleep(10)
            virtual = drawCPUScreen(device, width=widgetWidth, height=widgetHeight)
            virtual.refresh()
            time.sleep(10)
      


    # while True:
    #     second = datetime.now().second
    #     virtual = drawTime(device, width=widgetWidth, height=widgetHeight, t=second)
    #     virtual.refresh()
    #     time.sleep(10)

except KeyboardInterrupt:
    pass
except ValueError as err:
    print(f"Error: {err}")
# except KeyError as err:
#     print(f"Error: Please ensure the {err} environment variable is set")
