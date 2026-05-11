import machine
import time
from vl53l1x import VL53L1X 
from bno055 import BNO055   

i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21), freq=9600)

distance_sensor = VL53L1X(i2c)
imu_sensor = BNO055(i2c)

print("Sensors initialized!")

while True:
    # Read from Distance Sensor
    mm, status = distance_sensor.read()
    
    # Read from IMU
    heading, roll, pitch = imu_sensor.euler()
    
    print(f"Dist: {mm}mm | Heading: {heading}°")
    
    time.sleep_ms(100)
    
    
    