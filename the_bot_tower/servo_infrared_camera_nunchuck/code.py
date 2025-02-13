import motor
import IR
import time

while True:
    motor.motor_control()
    IR.update_thermal_image()

