import time
import board
import busio
import wifi
import socketpool
import ssl
import adafruit_requests
import json

# -------------------------------
#  Configuration / Credentials
# -------------------------------
WIFI_SSID = "SSID"              # Replace with your WiFi SSID
WIFI_PASSWORD = "PASSWORD"      # Replace with your WiFi password
OPENAI_API_KEY = "OPENAI-KEY"  # Replace with your OpenAI API key
model = "gpt-4o-mini"

# -------------------------------
#  WiFi & HTTP Session Setup
# -------------------------------
print("Connecting to WiFi...")
try:
    wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connected to WiFi as:", WIFI_SSID)
except Exception as e:
    # Probably add some retries here if you care
    print("WiFi connection failed:", e)


# Create a socket pool and HTTPS (SSL) context for making secure requests.
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# -------------------------------
#  I2C Bus Initialization
# -------------------------------
# For many boards, board.SCL and board.SDA are predefined.
# If not, find a pinout diagram and find SCL and SDA - use those pin numbers
i2c = busio.I2C(board.SCL, board.SDA)

def test_address(address, buffer):
    print(f"attempting to read at address: {address}...")
    try:
        i2c.readfrom_into(address, buffer)
    except Exception as e:
        print(f"Error: {e}")
        print("Moving to next attempt")

def scan_i2c():
    """
    Scans the I2C bus for connected devices.
    
    Returns:
        A list of I2C addresses (in integer form) for devices found.
    """
    # Wait until the I2C bus is available.
    while not i2c.try_lock():
        pass
    try:
        devices = i2c.scan()
    finally:
        i2c.unlock()
    return devices

# -------------------------------
#  OpenAI Chat API Interface
# -------------------------------
def chat_with_openai(system_prompt, user_prompt):
    """
    Sends a text prompt to the OpenAI ChatGPT API (o3-mini model) and returns the reply.
    
    Args:
        system_prompt (str): The text prompt for the system, specify I2C or ESPNOW
        user_prompt (str): The text prompt or command to send to the AI.
        
    Returns:
        The text response from OpenAI, or None if an error occurred.
    """
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + OPENAI_API_KEY,
    }
    
    response_format = {
        "type": "json_schema",
            "json_schema": {
              "name": "device_configurations",
              "schema": {
                "type": "object",
                "properties": {
                  "devices": {
                    "type": "array",
                    "description": "A list of devices found on the I2C bus. Each device includes its I2C address, a name, a confidence score, and register information.",
                    "items": {
                      "type": "object",
                      "properties": {
                        "i2c_address": {
                          "type": "string",
                          "description": "The hex address of the device on the I2C bus."
                        },
                        "device_name": {
                          "type": "string",
                          "description": "The name of the device as identified by the AI."
                        },
                        "confidence_score": {
                          "type": "number",
                          "description": "A confidence score out of 100 reflecting the AI's certainty regarding the device identification."
                        },
                        "registers": {
                          "type": "array",
                          "description": "A list of registers for this device.",
                          "items": {
                            "type": "object",
                            "properties": {
                              "register_address": {
                                "type": "string",
                                "description": "The hex address of the register."
                              },
                              "commands": {
                                "type": "array",
                                "description": "A list of commands that can be sent to this register (in hex format).",
                                "items": {
                                  "type": "object",
                                  "properties": {
                                    "command": {
                                      "type": "string",
                                      "description": "The command in hex format that can be sent to the register."
                                    },
                                    "description": {
                                      "type": "string",
                                      "description": "A description of what the command does."
                                    }
                                  },
                                  "required": [
                                    "command",
                                    "description"
                                  ],
                                  "additionalProperties": False
                                }
                              }
                            },
                            "required": [
                              "register_address",
                              "commands"
                            ],
                            "additionalProperties": False
                          }
                        }
                      },
                      "required": [
                        "i2c_address",
                        "device_name",
                        "confidence_score",
                        "registers"
                      ],
                      "additionalProperties": False
                    }
                  }
                },
                "required": [
                  "devices"
                ],
                "additionalProperties": False
              },
              "strict": False
            }
          }





    # Construct the message payload.
    data = {
        "model": f"{model}",
        "messages": [
            {"role": "system", "content": f"{system_prompt}"},
            {"role": "user", "content": f"{user_prompt}"},
        ],
        "response_format": response_format,
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        # Check for successful response
        if response.status_code == 200:
            result = response.json()
            # Extract and return the AI's reply
            chat_response = result["choices"][0]["message"]["content"]
            return chat_response
        else:
            print("OpenAI API error:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Exception during OpenAI API call:", e)
        return None

def format_device_info(json_str):
    """
    Parses the device configuration JSON (with multiple devices) and returns a formatted string.
    
    Args:
        json_str (str): A JSON string containing device configuration information.
    
    Returns:
        str: A nicely formatted string with information for each device.
    """
    try:
        data = json.loads(json_str)
    except Exception as e:
        return f"Error parsing JSON: {e}"
    
    devices = data.get("devices")
    if devices is None:
        return "No devices found in the provided JSON."

    lines = []
    lines.append("=" * 50)
    lines.append("Device Information")
    lines.append("=" * 50)
    
    # Process each device in the list
    for device in devices:
        # Extract information for the device
        i2c_address = device.get("i2c_address", "Unknown Address")
        device_name = device.get("device_name", "Unknown Device")
        confidence_score = device.get("confidence_score", "N/A")
        registers = device.get("registers", [])
        
        # Print a header for each device
        lines.append("")
        lines.append(f"Device Address: {i2c_address}")
        lines.append(f"Device Name: {device_name}")
        lines.append(f"Confidence Score: {confidence_score}")
        lines.append("")
        lines.append("Registers:")

        # Process each register for the device
        if registers:
            for reg in registers:
                register_address = reg.get("register_address", "Unknown Address")
                lines.append(f"  Register Address: {register_address}")
                commands = reg.get("commands", [])
                for cmd in commands:
                    command_text = cmd.get("command", "Unknown Command")
                    description = cmd.get("description", "No description provided.")
                    lines.append(f"    - Command: {command_text}")
                    lines.append(f"      Description: {description}")
                lines.append("")  # Blank line after each register
        else:
            lines.append("  No registers available.")
        
        # Add a divider between devices
        lines.append("-" * 50)
    
    return "\n".join(lines)


# -------------------------------
#  Testing the Interfaces
# -------------------------------
# 1. Test the I2C scan
devices = scan_i2c()
if devices:
    print("I2C devices detected at addresses:")
    for device in devices:
        print(" -", hex(device))
else:
    print("No I2C devices found on the bus.")

# 2. Test the OpenAI chat interface with a sample prompt
test_system_prompt = "You are an informational assistant. You are presented with a list of I2C addresses, then based on your expert knowledge of micrcontroller devices you list the possible registers and what commands can be read or written to those registers. For example, if presented with an 0x3C or 0x3D you could gather that the device is likely an SSD1306 OLED display - you would then provide a list of commands and registers for the SSD1306 in the structured format provided."
device_list = ""
if devices:
    devices = [hex(device) for device in devices]
    print("detected:")
    for device in devices:
        print(device)
    device_list = "".join(str(devices))

#device_list = "".join(str(device) for device in hex(devices))

test_user_prompt = f"Current I2C Devices: {device_list}"
print(f"\nSending prompt to OpenAI:\n\n SYS: {test_system_prompt}\n\n USR:{test_user_prompt}")
ai_reply = chat_with_openai(test_system_prompt, test_user_prompt)
print("OpenAI reply:")
print("-" * 40)
print("Raw Reply: ", ai_reply)
print("-" * 40)
print(format_device_info(ai_reply))

