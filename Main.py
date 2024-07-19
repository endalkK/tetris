import time
import board
import displayio
import terminalio
import adafruit_displayio_sh1107
from adafruit_display_text import label
from digitalio import DigitalInOut, Direction, Pull
from adafruit_displayio_sh1107 import SH1107, DISPLAY_OFFSET_ADAFRUIT_FEATHERWING_OLED_4650

i2c = board.I2C()
rotation_angle = 90
w = 64
h = 128
displayio.release_displays()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
display = SH1107(display_bus, width=w, height=h, display_offset=DISPLAY_OFFSET_ADAFRUIT_FEATHERWING_OLED_4650, rotation=int(rotation_angle))

while True:
    group = displayio.Group()
    text = f"TETRIS"
    text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFF, x=0, y=5)

    group.append(text_area)
    display.show(group)
    time.sleep(0.8)
    group.pop()
