import displayio
from adafruit_display_shapes.rect import Rect
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.triangle import Triangle
from adafruit_display_shapes.polygon import Polygon
from adafruit_display_shapes.filled_polygon import FilledPolygon
import terminalio
from adafruit_display_text.label import Label

def check_mark(left_most_pixel: tuple = (32,65), color = 0x00FF00):
    start_x, start_y = left_most_pixel
    # Draw a checkmark relative to the starter pixel
    check = FilledPolygon(
        points=[
        (start_x, start_y),
        (start_x + 20, start_y),
        (start_x + 25, start_y + 10),
        (start_x + 45, start_y - 20), # Top part of the checkmark
        (start_x + 65, start_y - 20),
        (start_x + 25, start_y + 20) # bottom of the checkmark
        ],
        outline=0x000000,
        stroke=2,
        fill=color
    )
    return check

def x_mark(position: tuple = (37, 42), color = 0xFF0000):
    start_x, start_y = position
    # Draw a checkmark relative to the starter pixel
    x = FilledPolygon(
        points=[
        (start_x, start_y), # topleft start
        (start_x + 20, start_y), # topleft end of x
        (start_x + 25, start_y + 10), # top mid-dip of x
        (start_x + 30, start_y), # topright start
        (start_x + 50, start_y), # topright of x
        (start_x + 30, start_y + 20), # mid-right of x
        (start_x + 50, start_y + 40), # bottomright of x
        (start_x + 30, start_y + 40),
        (start_x + 25, start_y + 30), # bottom mid-dip of x
        (start_x + 20, start_y + 40), # bottomleft end x
        (start_x, start_y + 40), # bottomleft start x
        (start_x + 20, start_y + 20)
        ],
        outline=0x000000,
        stroke=2,
        fill=color
    )
    return x

def display_points(position: tuple = (65,65), point_value = None):
    if int(point_value) > 0:
        color = 0x00FF00
    elif int(point_value) < 0:
        color = 0x0000FF # Red is backwards for whatever reason
    else:
        color = 0x000000
    display_label = Label(terminalio.FONT, text= f"{point_value}", color = color, scale = 3)
    display_label.x, display_label.y = position
    return display_label

def NFC_progress_boxes(position, color):
    #TODO: make boxes to show scan progress visually
    pass