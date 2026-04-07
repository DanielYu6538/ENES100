import machine
import time
from bno055.bno055 import BNO055

# 1. Initialize I2C (Adjust pins if your Acebott board uses different ones)
# Typical ESP32: scl=22, sda=21
# Typical RP2040: scl=9, sda=8
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

# 2. Initialize the Sensor
try:
    imu = BNO055(i2c)
    print("BNO055 connected successfully!")
except Exception as e:
    print("Failed to find BNO055. Check wiring:", e)
    raise SystemExit

# 3. Main Loop
while True:
    # Read Euler angles (heading, roll, pitch) in degrees
    heading, roll, pitch = imu.euler()
    
    # Read calibration status (0=uncalibrated, 3=fully calibrated)
    # Returns (sys, gyro, accel, mag)
    cal_status = imu.cal_status()
    
    print("Heading: {:6.2f} | Roll: {:6.2f} | Pitch: {:6.2f}".format(heading, roll, pitch))
    print("Calibration Status (S, G, A, M): {}".format(cal_status))
    
    # Optional: Read temperature
    # temp = imu.temperature()
    # print("Temp: {}C".format(temp))

    time.sleep(0.5)