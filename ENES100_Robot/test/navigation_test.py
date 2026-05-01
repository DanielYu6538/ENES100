# Imports
# from machine import Pin, I2C
# from vl53l1x import VL53L1X
# from bno055 import BNO055
# from rps40st import RPS40ST
# from motor import Motor
# from drivetrain import Drivetrain
# from enes100 import Enes100
from navigation import get_path, nodes, graph
import math
import time
# SETUP:
#I2C Sensors
# i2c = I2C(0, scl=Pin(22), sda=Pin(21))
# distance = VL53L1X(i2c)
# imu = BNO055(i2c)

# Force sensor
# force = RPS40ST(Pin(34))

# Drivetrain
# left_in1 = Pin(5, Pin.OUT)
# left_in2 = Pin(16, Pin.OUT)
# left_pwm = Pin(17)
# 
# right_in1 = Pin(18, Pin.OUT)
# right_in2 = Pin(19, Pin.OUT)
# right_pwm = Pin(23)
# 
# l_motor = Motor(left_in1, left_in2, left_pwm)
# r_motor = Motor(right_in1, right_in2, right_pwm)

# robot = Drivetrain(l_motor, r_motor, imu);

# Enes100 lib
# Enes100.begin("Material Madness", "MATERIAL", 10, 1120) # Update values

# Constants
PI = 3.14159265358979323
TO_DEGREE = 180/PI
VELOCITY = 0.3 # in m/s
MOTOR_POWER = 50 # in percentage

# Functions:
def get_float():
    while True:
        try:
            user_input = input("Enter value: ")
            data = float(user_input)
            return data
        except ValueError:
            print("Invalid type, enter value: ")

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

# Global position
def get_position():
#     xPos, yPos, thetaPos = -1, -1, -1
#     while (xPos == -1):
#         xPos = Enes100.getX()
#         time.sleep_ms(10)
#     while (yPos == -1):
#         yPos = Enes100.getY()
#         time.sleep_ms(10)
#     while (thetaPos == -1):
#         thetaPos = Enes100.getTheta()
#         time.sleep_ms(10)
    print("Enter x position")
    xPos = get_float()
    print("Enter y position")
    yPos = get_float()
    print("Enter theta position")
    thetaPos = get_float() / TO_DEGREE
    
    return xPos, yPos, thetaPos

x_pos, y_pos, theta = get_position();

def get_turn_angle(currentAngle, targetAngle):
    turnAngle = currentAngle - targetAngle
    turnAngle = turnAngle - 2*PI if (turnAngle > PI) else turnAngle
    turnAngle = turnAngle + 2*PI if (turnAngle < -PI) else turnAngle
    return turnAngle

# Navigation to Mission
target_angle = PI/2 if (y_pos <= 1) else -PI/2
turn_angle = get_turn_angle(theta, target_angle) * TO_DEGREE

print("Turn: ")
print(turn_angle)
print("Move: ")
print(1.0)
# robot.turn(turn_angle, 50)

# robot.drive(MOTOR_POWER, 1/VELOCITY)


# Mission

# Navigation to End

def execute_navigation(current_node, goal_node):
    path = get_path(graph, current_node, goal_node)
    
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        
        print("Current node")
        print(u)
        
        x_goal, y_goal = nodes.get(v)
        turn_angle, distance = compute_move(x_goal, y_goal)
        
        # Turning
#         robot.turn(turn_angle, 50)
        
        print("Turn: ")
        print(turn_angle)
        
        if (graph[u][v]['type'] == 1):
            
#             if (distance.obj_ahead(500)):
            print("Path available? 0.0=Yes; 1.0=No: ")
            if (get_float() > 0.5):
                del graph[u][v]
                return execute_navigation(u, goal_node)
        
        # move forward to next node
#         robot.drive(MOTOR_POWER, distance/VELOCITY)
        print("Move: ")
        print(distance)
        
        
# Current position
x_pos, y_pos, theta = get_position();
# Coordinates of closest node
start_node = 'A1' if (y_pos >= 1) else 'A3'
x_goal, y_goal = nodes.get(start_node)

turn_angle, distance = compute_move(x_goal, y_goal)

print("Turn: ")
print(turn_angle)
print("Move: ")
print(distance)

# robot.turn(turn_angle, 50)
# robot.drive(MOTOR_POWER, distance/VELOCITY)

execute_navigation(start_node, 'GOAL')

x_goal, y_goal = 3.7, 1.5

turn_angle, distance = compute_move(x_goal, y_goal)

print("Turn: ")
print(turn_angle)
print("Move: ")
print(distance)








