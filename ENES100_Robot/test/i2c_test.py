import machine
import time
from vl53l1x import VL53L1X # Adjust based on your final file structure
from bno055 import BNO055   # Adjust based on your final file structure

# 1. Initialize the I2C bus once
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

# 2. Initialize both sensors using the SAME i2c object
distance_sensor = VL53L1X(i2c)
imu_sensor = BNO055(i2c)

print("Sensors initialized!")

while True:
    # Read from Distance Sensor
    mm = distance_sensor.read()
    
    # Read from IMU
    heading, roll, pitch = imu_sensor.euler()
    
    print(f"Dist: {mm}mm | Heading: {heading}°")
    
    time.sleep_ms(100)