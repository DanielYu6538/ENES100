from servo import Servo
import time

s = Servo(4)

s.set_angle(180)

time.sleep(2)

s.set_angle(0)

