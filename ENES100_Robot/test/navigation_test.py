# Imports
# from machine import Pin, I2C
# from vl53l1x import VL53L1X
# from bno055 import BNO055
# from rps40st import RPS40ST
# from motor import Motor
# from drivetrain import Drivetrain
# from enes100 import Enes100
import sys
sys.path.append('./lib/nav')
from navigation import get_path, nodes, graph
import math
import time

import random

# SETUP:
#I2C Sensors
# i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=9600)
# distance_sensor = VL53L1X(i2c)
# imu = BNO055(i2c)
# print("i2c sensors init")

# Force sensor
# force = RPS40ST(Pin(34))

# Drivetrain
# left_in1 = Pin(5, Pin.OUT)
# left_in2 = Pin(16, Pin.OUT)
# left_pwm = Pin(17)

# right_in1 = Pin(18, Pin.OUT)
# right_in2 = Pin(19, Pin.OUT)
# right_pwm = Pin(23)

# l_motor = Motor(left_in1, left_in2, left_pwm)
# r_motor = Motor(right_in1, right_in2, right_pwm)

# robot = Drivetrain(l_motor, r_motor, imu);

# Enes100 lib
# Enes100.begin("Material Madness", "MATERIAL", 10, 1116) # Update values



# Constants
PI = 3.14159265358979323
TO_DEGREE = 180/PI
VELOCITY = 0.08373378 # IN m/s
MOTOR_POWER = 50 # in percentage

# Testing Values
obj_ahead_to_node = {'B2', 'B3', 'C1'}

global_x_pos, global_y_pos, global_theta_pos = 0.5, 1.5, 72/TO_DEGREE

class Robot():
    def drive(self, power, time):
        global global_x_pos, global_y_pos
        distance = VELOCITY * time
        global_x_pos += math.cos(global_theta_pos) * distance
        global_y_pos += math.sin(global_theta_pos) * distance
        print("Robot drove", distance, "m at", power, "% power for", time, "seconds.")
    
    def turn(self, angle, power):
        global global_theta_pos
        global_theta_pos -= angle/TO_DEGREE
        global_theta_pos = global_theta_pos - 2*PI if (global_theta_pos > PI) else global_theta_pos
        global_theta_pos = global_theta_pos + 2*PI if (global_theta_pos < -PI) else global_theta_pos
        print ("Robot turned", angle, "degrees at", power, "% power.")
        
robot = Robot()

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

def obj_ahead(node):
    return node in obj_ahead_to_node

# Global position
def get_position():
    xPos, yPos, thetaPos = global_x_pos, global_y_pos, global_theta_pos
    
    xPos += (random.random() - 0.5) * 0.05
    yPos += (random.random() - 0.5) * 0.05
    thetaPos += (random.random() - 0.5) * 0.05
    
    return xPos, yPos, thetaPos

def print_position():
    print("The current position is", global_x_pos, global_y_pos, global_theta_pos * TO_DEGREE)


# Print Testing Conditions
print_position()
print("Obstacles:", obj_ahead_to_node)

# Navigation to Mission
print("Navigating to mission")
x_pos, y_pos, theta = get_position();

target_angle = PI/2 if (y_pos <= 1) else -PI/2
turn_angle = get_turn_angle(theta, target_angle) * TO_DEGREE

robot.turn(turn_angle, 50)

robot.drive(MOTOR_POWER, 0.85/VELOCITY) # Move right before mission

print_position()


# Mission


# Navigation to End
print("Navigating to end")
def execute_navigation(current_node, goal_node):
    path = get_path(graph, current_node, goal_node)
    
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        
        print("At node", u)
        
        # turn in direction of next node
        x_goal, y_goal = nodes.get(v)
        turn_angle, distance = compute_move(x_goal, y_goal)
        
        # Turning
        robot.turn(turn_angle, 50)
        
        print_position()
        
        if (graph[u][v]['type'] == 1):
            print("Check path")
            if (obj_ahead(v)):
                print("Object detected. Removed edge from", u, "to", v, ". Recursive call.")
                del graph[u][v]
                return execute_navigation(u, goal_node)
        
        # move forward to next node
        robot.drive(MOTOR_POWER, distance/VELOCITY)
        
        print_position()
        
        # exit when reach goal node
        if v == goal_node:
            print("Finished at node", v)
            return
        
        
# Current position
x_pos, y_pos, theta = get_position();
# Coordinates of closest node
start_node = 'A1' if (y_pos >= 1) else 'A3'
x_goal, y_goal = nodes.get(start_node)
# Compute angle and distance to move to closest node
turn_angle, distance = compute_move(x_goal, y_goal)
# Excute move
print("Move to closest node", start_node)
robot.turn(turn_angle, 50)
robot.drive(MOTOR_POWER, distance/VELOCITY)

print_position()

# Function to execute navigation
execute_navigation(start_node, 'GOAL')

