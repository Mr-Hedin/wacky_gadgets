import board
from adafruit_pn532.i2c import PN532_I2C
import time
# I2C connection:
i2c = board.I2C()
pn532 = PN532_I2C(i2c, debug=False)
# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()
reading = False
def read_uid(timeout=2):
    reading = True
    print("Waiting for RFID/NFC card...")
    current_time = time.monotonic()
    while reading:
        if time.monotonic() - current_time > timeout:
            reading = False
            return None
        # Check if a card is available to read
        uid = pn532.read_passive_target(timeout=0.5)
        print(".", end="")
        # Try again if no card is available.
        if uid is None:
            continue
        else:
            print("Found card with UID:", [hex(i) for i in uid])
            reading = False
            return uid
        
def read_data(start_block: int = 1, end_block: int = 16):
    """
    Reads data from the card starting at the specified block.
    Data is split into 16 byte blocks.
    """
    print("Reading data from card...")
    data = []
    try:
        for i in range(start_block, end_block + 1):
            data.append(pn532.mifare_classic_read_block(i))
        print(data)
    except Exception as e:
        print(e)
    if len(data) == 0:
        print("No data found, returning")
        return None
    return data

def write_data(data: bytearray, start_block: int = 4):
    """
    Writes data to the card starting at the specified block.
    Data must be provided as a bytearray and will be split into 16 byte blocks.
    Returns True if write was successful, False otherwise.
    """
    print("Writing data to card...")
    
    # Convert to bytearray if needed
    if not isinstance(data, bytearray):
        try:
            data = bytearray(data)
        except Exception as e:
            print(f"Error converting data to bytearray: {e}")
            return False

    # Split data into 16-byte blocks
    blocks = []
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        # Pad the block with zeros if it's less than 16 bytes
        if len(block) < 16:
            block = block + bytearray([0] * (16 - len(block)))
        blocks.append(block)

    # Write each block
    try:
        for i, block in enumerate(blocks):
            block_num = start_block + i
            if not pn532.mifare_classic_write_block(block_num, block):
                print(f"\nError writing block {block_num}")
                return False
            print("✓", end="")
        print("\nData written successfully")
        return True
    except Exception as e:
        print(f"\nError during write: {e}")
        return False











