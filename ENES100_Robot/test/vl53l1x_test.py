from machine import I2C, Pin
from vl53l1x import VL53L1X
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
distance = VL53L1X(i2c)

distance.set_distance_mode(1)
print(distance.get_distance_mode());

while True:
#     mm, range_status, is_valid = distance.read()
    print("range: mm ", distance.read())
    time.sleep_ms(50)