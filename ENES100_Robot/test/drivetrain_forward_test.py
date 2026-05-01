from machine import Pin, I2C
from bno055 import BNO055
from motor import Motor
from drive import Drive, Direction
import time


i2c = I2C(0, scl=Pin(22), sda=Pin(21))

try:
    imu = BNO055(i2c)
    print("BNO055 connected successfully!")
except Exception as e:
    print("Failed to find BNO055. Check wiring:", e)
    raise SystemExit

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
d = Drive(l_motor, r_motor)

d.move(Direction.FORWARD, 100)

while True:
    heading, roll, pitch = imu.euler();
    print("Heading: {:6.2f} | Roll: {:6.2f} | Pitch: {:6.2f}".format(heading, roll, pitch))
    time.sleep_ms(200)
    
time.sleep(24)
d.stop()