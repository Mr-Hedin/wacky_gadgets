# This is device NFC0 - a little NFC scanning station meant to make the hedollar awarding process easier

import reader
import time
import espnow
import gc
import displayables
import digitalio
import board
import microcontroller
import displayio

# Button Setup
button_down = digitalio.DigitalInOut(board.BUTTON0)
button_up = digitalio.DigitalInOut(board.BUTTON2)
button_down.direction = digitalio.Direction.INPUT
button_up.direction = digitalio.Direction.INPUT
button_down.pull = digitalio.Pull.UP
button_up.pull = digitalio.Pull.UP


#Callsign stuff

device_callsign = "H$NFC0"
callsign_bytes = device_callsign.encode('utf-8')

# ESPNOW STUFF
esp = espnow.ESPNow()
broadcast_peer = espnow.Peer(b'\xff\xff\xff\xff\xff\xff')
esp.peers.append(broadcast_peer)

# I'm using this whacky custom encoding scheme - if it starts with H$ it's one of my devices, then the type of device, any data is after a '-'
esp.send(callsign_bytes, broadcast_peer)


def write_peer(peer_callsign, peer_mac):
    with open('peer_log.txt', 'a') as file:
        # check for dupes
        for line in file:
            if peer_mac in line:
                print("peer already registered")
                return
        # no dupes, register new friendo
        formatted_peer_data = f"{peer_callsign} : {peer_mac}"
        file.write(formatted_peer_data)

def read_and_send():
    data = reader.pn532.read_passive_target(timeout=.1)


    if data:
        esp_data = f'{device_callsign}-{data}'
        bytes_esp_data = bytearray(esp_data.encode('utf-8'))
        try:
            for peer in esp.peers:
                esp.send(bytes_esp_data, peer)
            return data
        except:
            return "failed"
    return None

def check_new_messages():
    current_time = time.monotonic()
    while time.monotonic() - current_time < .1:
        incoming_data = esp.read()
        if incoming_data:
            print("Received message")
            print(incoming_data)
            # If a receiver MCU is found, add it to peers and dip
            if "H$RESET" in incoming_data.msg:
                microcontroller.reset()
            if "H$RECEIVE" in incoming_data.msg:
                new_peer = espnow.Peer(incoming_data.mac)
                if new_peer in espnow.Peers:
                    break
                try:
                    esp.peers.append(new_peer)
                    print(f"\nESP Peer added with MAC {new_peer.mac}")
                    write_peer(incoming_data.msg.split('-')[0], incoming_data.mac)
                except Exception as e:
                    print("Couldn't add peer. Error: {e}")
                break
            

# Display init
display_group = displayio.Group()
board.DISPLAY.root_group = display_group
background_bitmap = displayio.Bitmap(128,128,3)
color_palette = displayio.Palette(3)
color_palette[0] = 0xFFFFFF
color_palette[1] = 0x00FF00
color_palette[2] = 0x0000FF
bg = displayio.TileGrid(background_bitmap, x=0,y=0,pixel_shader=color_palette)
display_group.append(bg)

# Create the x and check for later
check = displayables.check_mark(color=color_palette[1])
x = displayables.x_mark(color=color_palette[2])
points = displayables.display_points(point_value= "0")

# Append those fools to the main display group
display_group.append(check)
display_group[1].hidden = True # Hide the Checkmark
display_group.append(x)
display_group[2].hidden = True # Hide the X
display_group.append(points)
display_group[3].hidden = False




current_time = time.monotonic()
while time.monotonic() - current_time < 2:
    incoming_data = esp.read()
    if incoming_data:
        print("Received message")
        print(incoming_data)
        # If a receiver MCU is found, add it to peers and dip
        if "H$RECEIVE" in incoming_data.msg:
            new_peer = espnow.Peer(incoming_data.mac)
            esp.peers.append(new_peer)
            print(f"\nESP Peer added with MAC {new_peer.mac}")
            write_peer(incoming_data.msg.split('-')[0], incoming_data.mac)
            break



points_pending = 0
while True:
    # Handle button presses
    if not button_up.value:
        points_pending += 1
        print("UP")
        points.text = f"{points_pending}"
        if points_pending > 0:
            points.color = 0x00FF00
        elif points_pending < 0:
            points.color = 0x0000FF
        else:
            points.color = 0x000000
    if not button_down.value:
        points_pending -= 1
        print("DOWN")
        points.text = f"{points_pending}"
        if points_pending > 0:
            points.color = 0x00FF00
        elif points_pending < 0:
            points.color = 0x0000FF
        else:
            points.color = 0x000000
    
    

    # Handle new esp peers if needed or reset if the H$RESET command is received
    check_new_messages()
    
    # Handle NFC tags, then send them to peers
    success = read_and_send()
    if success == "failed":
        # If there's an error sending
        display_group[3].hidden = True # hide points
        display_group[2].hidden = False # unhide X
        time.sleep(1)
        points_pending = 0 # reset points counter
        points.text = f"{points_pending}"
        display_group[3].hidden = False # unhide points
        display_group[2].hidden = True # hide X
    elif success == None:
        # If there's no read
        if display_group[3].hidden:
            display_group[3].hidden = False # unhide text for points
    else:
        # If actually successful. What did I even do with this success check. How is it this backwards. Whateva.
        display_group[3].hidden = True # hide points
        display_group[1].hidden = False # unhide Check
        time.sleep(1)
        points_pending = 0 # reset points counter
        points.text = f"{points_pending}"
        display_group[3].hidden = False # unhide points
        display_group[1].hidden = True # hide Check
    



