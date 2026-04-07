from machine import I2C, Pin
from vl53l1x.vl53l1x import VL53L1X
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
distance = VL53L1X(i2c)

while True:
    print("range: mm ", distance.read())
    time.sleep_ms(50)