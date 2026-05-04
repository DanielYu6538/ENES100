from machine import Pin, I2C
from vl53l1x import VL53L1X
from bno055 import BNO055
from rps40st import RPS40ST
from motor import Motor
from drivetrain import Drivetrain
# from enes100 import Enes100
from navigation import get_path, nodes, graph
import math
import time

while True:
    print("Test")
    time.sleep(2)