from machine import Pin, I2C
from motor import Motor
from drivetrain import Drivetrain, Direction
from bno055 import BNO055
import time

i2c = I2C(0, scl=Pin(22), sda=Pin(21))

try:
    imu = BNO055(i2c)
    print("BNO055 connected successfully!")
except Exception as e:
    print("Failed to find BNO055. Check wiring:", e)
    raise SystemExit

left_in1 = Pin(5, Pin.OUT)
left_in2 = Pin(16, Pin.OUT)
left_pwm = Pin(17) # Set to None if using 2-pin PWM mode

# Right Motor Pins
right_in1 = Pin(18, Pin.OUT)
right_in2 = Pin(19, Pin.OUT)
right_pwm = Pin(23) # Set to None if using 2-pin PWM mode

# 2. Initialize Motor Objects
# The minDuty and maxDuty are set based on your class defaults (46000 to 65535)
l_motor = Motor(left_in1, left_in2, left_pwm)
r_motor = Motor(right_in1, right_in2, right_pwm)

# 3. Initialize Drivetrain
drive = Drivetrain(l_motor, r_motor)

def turn():
    heading, roll, pitch = imu.euler()
    initial_heading = heading;
    
    drive.move(Direction.RIGHT, 50);
    
#     while (not(heading > initial_heading + 80 and heading < initial_heading + 95)):
#         heading, roll, pitch = imu.euler();
#         print("Heading: {:6.2f} | Roll: {:6.2f} | Pitch: {:6.2f}".format(heading, roll, pitch))        
#         time.sleep_ms(1)
    time.sleep_ms(1500)
    
    drive.stop();

turn()

time.sleep(2)

turn()

time.sleep(2)

turn()
    

