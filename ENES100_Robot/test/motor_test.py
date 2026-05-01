from motor import Motor, Direction
from machine import Pin
import time

left_in1 = Pin(5, Pin.OUT)
left_in2 = Pin(16, Pin.OUT)
left_pwm = Pin(17) # Set to None if using 2-pin PWM mode

left_motor = Motor(left_in1, left_in2, left_pwm, 0, 1023)


for i in range(0, 105, 5):
    print(i)
    left_motor.move(Direction.CW, i)
    time.sleep(1)