from machine import Pin, PWM

class Servo:

    def __init__(self, pin_num:int, max_deg=180, min_duty=30, max_duty=123):
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(50)
        self.max_deg = max_deg
        self.min_duty = min_duty
        self.max_duty = max_duty
        self.set_angle(0);

    def set_angle(self, degrees):
        if (degrees > self.max_deg):
            degrees = self.max_deg
        elif (degrees < 0):
            degrees = 0
        
        duty = int(self.min_duty + (degrees / self.max_deg) * (self.max_duty - self.min_duty))
        
        self.pwm.duty(duty)
    
    def deinit(self):
        self.pwm.deinit()