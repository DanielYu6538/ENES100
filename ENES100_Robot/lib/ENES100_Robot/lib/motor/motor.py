from machine import Pin, PWM
from enum import Enum

class Direction(Enum):
    CW = 1
    CCW = 2


class Motor:
    
    def __init__(self, pinINA:Pin, pinINB:Pin, pinPWM:Pin = None, minDuty:int=46000, maxDuty:int=65535):
        self.pin_a = pinINA
        self.pin_b = pinINB
        
        self.pwm_ext = PWM(pinPWM) if (pinPWM is not None) else None
        self.pwm_a = PWM(pinINA) if (pinPWM is None) else None
        self.pwm_b = PWM(pinINB) if (pinPWM is None) else None
        
        self.minDuty = minDuty
        self.maxDuty = maxDuty
        self.duty = 0
        self.direction = Direction.CW
        self.separate_pwm = pinPWM is not None
    
    def __update(self):
        if self.seperate_pwm:
            self.pwm_ext.duty(self.duty)
            if (self.direction == Direction.CW):
                self.pin_a.value(1)
                self.pin_b.value(0)
            elif (self.direction == Direction.CCW):
                self.pin_a.value(0)
                self.pin_b.value(1)
        else:
            if (self.direction == Direction.CW):
                self.pwm_a.duty(self.duty)
                self.pwm_b.duty(0)
            elif (self.direction == Direction.CCW):
                self.pwm_a.duty(0)
                self.pwm_b.duty(self.duty)
    
    def move(self, direction:Direction = None, speed:int = None):
        if (speed is not None and speed >= 0 and speed <= 100):
            self.duty = int(self.minDuty + (speed / 100) * (self.maxDuty - self.minDuty))
        if (direction is not None):
            self.direction = direction
        self.__update()
        
    def brake(self):
        if self.seperate_pwm:
            self.pin_a.value(1)
            self.pin_b.value(1)
        else:
            self.pwm_a.duty(self.maxDuty)
            self.pwm_b.duty(self.maxDuty)
    
    def stop(self):
        if self.separate_pwm:
            self.pin_a.value(0)
            self.pin_b.value(0)
        else:
            self.pwm_a.duty(0)
            self.pwm_b.duty(0)
        
            


