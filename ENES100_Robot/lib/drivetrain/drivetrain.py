from motor import Motor, Direction as MotorDir

class Direction:
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4


class Drivetrain:
    
    def __init__(self, leftMotor:Motor, rightMotor:motor):
        self.left_motor = leftMotor
        self.right_motor = rightMotor
    
    
    def move(self, direction:Direction, speed:int):
        if (direction == Direction.FORWARD):
            self.left_motor.move(MotorDir.CCW, speed)
            self.right_motor.move(MotorDir.CW, speed)
        elif (direction == Direction.BACKWARD):
            self.left_motor.move(MotorDir.CW, speed)
            self.right_motor.move(MotorDir.CCW, speed)
        elif (direction == Direction.RIGHT):
            self.left_motor.move(MotorDir.CCW, speed)
            self.right_motor.move(MotorDir.CCW, speed)
        elif (direction == Direction.LEFT):
            self.left_motor.move(MotorDir.CW, speed)
            self.right_motor.move(MotorDir.CW, speed)
    
    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
        
    def brake(self):
        self.left_motor.brake()
        self.right_motor.brake()
