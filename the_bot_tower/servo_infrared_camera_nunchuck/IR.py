import board
import time
import displayio
import adafruit_amg88xx

# Initialize I2C and camera
i2c = board.I2C()
camera = adafruit_amg88xx.AMG88XX(i2c)

# Initialize display
display = board.DISPLAY
main_group = displayio.Group()
display.root_group = main_group

# Scale factor for the image (8x8 thermal camera)
SCALE = 20  # Can be changed to any value now
BITMAP_SIZE = 8 * SCALE  # 8 pixels * scale factor

# Create bitmap and palette
image = displayio.Bitmap(BITMAP_SIZE, BITMAP_SIZE, 64)  # Dynamic size based on scale
palette = displayio.Palette(64)

# Create a heat map palette (blue to red gradient)
for i in range(64):
    if i < 21:  # Blue to cyan
        palette[i] = (0, i * 12, 255 - i * 6)
    elif i < 42:  # Cyan to yellow
        i_adj = i - 21
        palette[i] = (i_adj * 12, 255 - i_adj * 6, 0)
    else:  # Yellow to red
        i_adj = i - 42
        palette[i] = (255, 255 - i_adj * 12, 0)

# Create TileGrid with the scaled size
tile_grid = displayio.TileGrid(image, pixel_shader=palette)
main_group.append(tile_grid)

def map_value(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def get_local_average(pixels, x, y):
    """Get average temperature of a pixel and its neighbors."""
    total = pixels[y][x]
    count = 1
    
    # Check all adjacent pixels
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            if 0 <= x + dx < 8 and 0 <= y + dy < 8:
                total += pixels[y + dy][x + dx]
                count += 1
    
    return total / count

def update_thermal_image():
    """Update the thermal image display with scaled blocks."""
    pixels = camera.pixels
    
    # Find temperature range
    temp_min = 255
    temp_max = 0
    for row in pixels:
        row_min = min(row)
        row_max = max(row)
        temp_min = min(temp_min, row_min)
        temp_max = max(temp_max, row_max)
    
    # Ensure minimum temperature difference
    if temp_max - temp_min < 2:
        temp_max = temp_min + 2

    # Update bitmap with scaled blocks
    for y in range(8):
        for x in range(8):
            # Get smoothed temperature value for this block
            #temp = get_local_average(pixels, x, y)
            temp = pixels[y][x]
            # Map temperature to color index
            color_index = map_value(temp, temp_min, temp_max, 0, 63)
            
            # Fill in the scaled block
            for dy in range(SCALE):
                for dx in range(SCALE):
                    image[x * SCALE + dx, y * SCALE + dy] = color_index
    
    print(f"Temperature range: {temp_min:.1f}°C to {temp_max:.1f}°C")

# Main loop
if __name__ == "__main__":
    while True:
        update_thermal_image()
        time.sleep(0.1)
