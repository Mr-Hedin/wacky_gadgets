import time
import board
import pwmio
from adafruit_motor import servo
import adafruit_nunchuk

i2c = board.I2C()
nunchuck = adafruit_nunchuk.Nunchuk(i2c)
pwm1 = pwmio.PWMOut(board.D1, duty_cycle=2**15, frequency=50)
pwm2 = pwmio.PWMOut(board.D2, duty_cycle=2**15, frequency=50)

servo1 = servo.Servo(pwm1)
servo2 = servo.Servo(pwm2)

# Helper function to map a value from one range to another
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def motor_control():    
    joystick_x = nunchuck.joystick[0]
    joystick_y = nunchuck.joystick[1]

    # Map the joystick readings to servo angles (0 to 180 degrees)
    angle1 = int(map_value(joystick_x, 0, 255, 0, 180))
    angle2 = int(map_value(joystick_y, 0, 255, 0, 180))
  
    # Update the servos with the new angles
    servo1.angle = angle1
    servo2.angle = angle2
    # Small delay to avoid overwhelming the I2C bus
    time.sleep(0.1) 

def accel_control():
    x_val = nunchuck.acceleration[0]
    y_val = nunchuck.acceleration[1]
    z_val = nunchuck.acceleration[2]
    return x_val, y_val, z_val

if __name__ == "__main__":
    motor_control()
