# Imports
from machine import Pin, I2C
from vl53l1x import VL53L1X
from bno055 import BNO055
from rps40st import RPS40ST
from motor import Motor
from drivetrain import Drivetrain
from enes100 import Enes100
from navigation import get_path, nodes, graph
import math
import time
# SETUP:
#I2C Sensors
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
distance_sensor = VL53L1X(i2c)
imu = BNO055(i2c)

# Force sensor
force = RPS40ST(Pin(34))

# Drivetrain
left_in1 = Pin(5, Pin.OUT)
left_in2 = Pin(16, Pin.OUT)
left_pwm = Pin(17)

right_in1 = Pin(18, Pin.OUT)
right_in2 = Pin(19, Pin.OUT)
right_pwm = Pin(23)

l_motor = Motor(left_in1, left_in2, left_pwm)
r_motor = Motor(right_in1, right_in2, right_pwm)

robot = Drivetrain(l_motor, r_motor, imu);

# Enes100 lib
Enes100.begin("Material Madness", "MATERIAL", 10, 1120) # Update values

# Constants
PI = 3.14159265358979323
TO_DEGREE = 180/PI
VELOCITY = 0.08373378 # IN m/s
MOTOR_POWER = 50 # in percentage

# Functions

def get_turn_angle(currentAngle, targetAngle):
    turnAngle = currentAngle - targetAngle
    turnAngle = turnAngle - 2*PI if (turnAngle > PI) else turnAngle
    turnAngle = turnAngle + 2*PI if (turnAngle < -PI) else turnAngle
    return turnAngle

def compute_move(x_goal, y_goal):
    x_pos, y_pos, theta = get_position()
    # Change
    delta_x = x_goal - x_pos
    delta_y = y_goal - y_pos
    # Angle
    target_angle = math.atan2(y_goal - y_pos, x_goal - x_pos)
    turn_angle = get_turn_angle(theta, target_angle) * TO_DEGREE
    # Distance
    distance = math.sqrt(delta_x**2 + delta_y**2)
    
    return turn_angle, distance

def obj_ahead(distance, samples=15, min_valid_samples=13):
    valid_readings = []
    
    for _ in range(samples):
        dist, status = distance_sensor.read()
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

# Global position
def get_position():
    xPos, yPos, thetaPos = -1, -1, -1
    while (xPos == -1):
        xPos = Enes100.getX()
        time.sleep_ms(10)
    while (yPos == -1):
        yPos = Enes100.getY()
        time.sleep_ms(10)
    while (thetaPos == -1):
        thetaPos = Enes100.getTheta()
        time.sleep_ms(10)
    
    offset = 0
    xPos += math.cos(thetaPos) * offset
    yPos += math.sin(thetaPos) * offset
    return xPos, yPos, thetaPos



# Navigation to Mission
Enes100.print("Start navigation to mission")
x_pos, y_pos, theta = get_position();

target_angle = PI/2 if (y_pos <= 1) else -PI/2
turn_angle = get_turn_angle(theta, target_angle) * TO_DEGREE

time.sleep(5)
robot.turn(turn_angle, 50)

robot.drive(MOTOR_POWER, 0.85/VELOCITY) # Move right before mission


# Mission
Enes.print("Start mission tasks")

# Navigation to End
Enes100.print("Start navigation to end")
def execute_navigation(current_node, goal_node):
    path = get_path(graph, current_node, goal_node)
    
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        
        # turn in direction of next node
        x_goal, y_goal = nodes.get(v)
        
        turn_angle, distance = compute_move(x_goal, y_goal)
        
        # Turning
        robot.turn(turn_angle, 50)
        
        if (graph[u][v]['type'] == 1):
            
            if (obj_ahead(300)):
                del graph[u][v]
                return execute_navigation(u, goal_node)
        
        # move forward to next node
        robot.drive(MOTOR_POWER, distance/VELOCITY)
        
        # exit when reach goal node
        if v == goal_node:
            return
        
        
# Current position
x_pos, y_pos, theta = get_position();
# Coordinates of closest node
start_node = 'A1' if (y_pos >= 1) else 'A3'
x_goal, y_goal = nodes.get(start_node)
# Compute angle and distance to move to closest node
turn_angle, distance = compute_move(x_goal, y_goal)
# Excute move
robot.turn(turn_angle, 50)
robot.drive(MOTOR_POWER, distance/VELOCITY)

# Function to execute navigation
execute_navigation(start_node, 'GOAL')


# All tasks finished
Enes100.print("Finished")
