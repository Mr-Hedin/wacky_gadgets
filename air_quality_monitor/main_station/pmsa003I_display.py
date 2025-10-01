import time
import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
import adafruit_ili9341
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C

###############################################################################
# Setup the ILI9341 Display - probably going to change this to use the feather knockoff MCU with a builtin display to save some space!
###############################################################################

# IMPORTANT: this works on devices with external displays - it may cause problems if the display driver is built into the circuitpython firmware for that MCU
displayio.release_displays()

# spi = busio.SPI(MISO=board.IO37,MOSI=board.IO35,clock=board.IO36)
# tft_cs = board.IO34
# tft_dc = board.IO33

# Create the display bus and ILI9341 SPI display object.
# display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=board.IO21)
# display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240, rotation=270)
display = board.DISPLAY

# Create the main display group
splash = displayio.Group()

# Create a full-screen background (black in this example)
color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x000000  # Black
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Create a group for text labels.
text_group = displayio.Group()
splash.append(text_group)

# add it to the root group for display
display.root_group = splash

###############################################################################
# Set up labels for each row of data 
# TODO: make this dynamic based on  screen size.
###############################################################################

# Define the maximum number of lines that will be displayed.
max_lines = 15 

labels = []
start_y = 10
line_spacing = 12

for i in range(max_lines):
    # Create a whole buncha labels for the data
    text_area = label.Label(
        terminalio.FONT,
        text="",
        color=0xFFFFFF,
        x=10,  # Horizontal offset (in pixels)
        y=start_y + i * line_spacing
    )
    text_group.append(text_area)
    labels.append(text_area)

###############################################################################
# Setup the PM2.5 Sensor (I2C)
###############################################################################

# Initialize the I2C bus and PM2.5 sensor. - this first one is for the ESP32-S2 this was on before.
# i2c = busio.I2C(board.IO1, board.IO2, frequency=100000)
i2c = board.I2C()
pm25 = PM25_I2C(i2c)

###############################################################################
# Main Loop – Read Sensor and Update Display
###############################################################################

while True:
    time.sleep(1)

    try:
        aqdata = pm25.read()

        # Prepare the lines of text for display.
        text_lines = [
            "Concentration Units (standard)",
            "---------------------------------------",
            "PM 1.0: {}   PM2.5: {}   PM10: {}".format(
                aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"]
            ),
            "Concentration Units (environmental)",
            "---------------------------------------",
            "PM 1.0: {}   PM2.5: {}   PM10: {}".format(
                aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"]
            ),
            "---------------------------------------",
            "Particles > 0.3um: {}".format(aqdata["particles 03um"]),
            "Particles > 0.5um: {}".format(aqdata["particles 05um"]),
            "Particles > 1.0um: {}".format(aqdata["particles 10um"]),
            "Particles > 2.5um: {}".format(aqdata["particles 25um"]),
            "Particles > 5.0um: {}".format(aqdata["particles 50um"]),
            "Particles > 10um: {}".format(aqdata["particles 100um"]),
            "---------------------------------------",
        ]
        #print(text_lines)
    except RuntimeError:
        text_lines = ["Unable to read from sensor, retrying..."]

    # Update the text for each pre-created label.
    for i in range(max_lines):
        if i < len(text_lines):
            labels[i].text = text_lines[i]
        else:
            labels[i].text = ""  # Clear unused labels
