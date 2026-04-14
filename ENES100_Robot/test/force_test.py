from machine import Pin
from RPS40ST import RPS40ST
import time

force = RPS40ST(Pin(32))

while (True):
    print(force.get_resistance())
    time.sleep_ms(500)