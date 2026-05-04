from machine import I2C, Pin
from vl53l1x import VL53L1X
import time

i2c = I2C(0, sda=Pin(21), scl=Pin(22))
sensor = VL53L1X(i2c)

if sensor.init():
    print("Sensor initialized!")

def obj_ahead(sensor, distance, samples=15, min_valid_samples=13):
    valid_readings = []
    
    for _ in range(samples):
        dist, status = sensor.read()
        # Status 9 is valid reading
        if status == 9:
            print("Valid reading:   ", dist)
            valid_readings.append(dist)
        else:
            print("Invalid reading: ", status, ", ", dist);
        # Time between readings
        time.sleep_ms(15)
    # If not enough valid readings, too far away
    if (len(valid_readings) < min_valid_samples):
        return False
    
    print("Valid")
    average_distance = sum(valid_readings) / len(valid_readings)
    
    return average_distance <= distance
    

sensor.start_continuous(50) # 50ms between readings

while True:
    input("Start Next")
    print(obj_ahead(sensor, 300))
    