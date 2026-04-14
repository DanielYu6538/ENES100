from machine import Pin
from motor import Motor
from drivetrain import Drivetrain, Direction
import time

# 1. Setup Pins for Motors (Adjust pin numbers based on your ENES100 wiring)
# Left Motor Pins
left_in1 = Pin(5, Pin.OUT)
left_in2 = Pin(16, Pin.OUT)
left_pwm = Pin(17) # Set to None if using 2-pin PWM mode

# Right Motor Pins
right_in1 = Pin(18, Pin.OUT)
right_in2 = Pin(19, Pin.OUT)
right_pwm = Pin(23) # Set to None if using 2-pin PWM mode

# 2. Initialize Motor Objects
# The minDuty and maxDuty are set based on your class defaults (46000 to 65535)
l_motor = Motor(left_in1, left_in2, left_pwm)
r_motor = Motor(right_in1, right_in2, right_pwm)

# 3. Initialize Drivetrain
drive = Drivetrain(l_motor, r_motor)

drive.move(Direction.FORWARD, 100)
time.sleep(24)
drive.stop()