from machine import Pin, I2C
from bno055 import BNO055
from motor import Motor
from drivetrain import Drivetrain
from enes100 import Enes100

import time
import math


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
imu = BNO055(i2c)

# Drivetrain
left_in1 = Pin(5, Pin.OUT)
left_in2 = Pin(16, Pin.OUT)
left_pwm = Pin(17)

right_in1 = Pin(18, Pin.OUT)
right_in2 = Pin(19, Pin.OUT)
right_pwm = Pin(23)

l_motor = Motor(left_in1, left_in2, left_pwm)
r_motor = Motor(right_in1, right_in2, right_pwm)

robot = Drivetrain(l_motor, r_motor, imu);

# Enes100 lib
Enes100.begin("Material Madness", "MATERIAL", 10, 1120) # Update values


def get_position():
    xPos, yPos, thetaPos = -1, -1, -1
    while (xPos == -1):
        xPos = Enes100.getX()
        time.sleep_ms(10)
    while (yPos == -1):
        yPos = Enes100.getY()
        time.sleep_ms(10)
    while (thetaPos == -1):
        thetaPos = Enes100.getTheta()
        time.sleep_ms(10)
    return xPos, yPos, thetaPos


initial_x, initial_y, initial_theta = get_position()

robot.turn(180)

final_x, final_y, final_theta = get_position()

print("Initial position: ", initial_x, initial_y, initial_theta)
print("Final position: ", final_x, final_y, final_theta)

delta_x = final_x - initial_x
delta_y = final_y - initial_y

offset = math.sqrt(delta_x**2 + delta_y**2) /2

print("Offset: ", offset)