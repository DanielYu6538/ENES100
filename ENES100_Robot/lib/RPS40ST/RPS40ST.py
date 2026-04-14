from machine import Pin, ADC
import time


class RPS40ST:
    def __init__(self, pin:Pin, vcc=3.3, r_ext=10000, a=35000000, b=-1.4):
        self.adc = ADC(pin, atten=ADC.ATTN_11DB)
        self.vcc = vcc
        self.r_ext = r_ext
        self.a = a
        self.b = b
    
    def get_resistance(self):
        voltage = 3.6 * self.adc.read() / 65535
        if voltage <= 0.05:
            return float('inf')
        return self.vcc * self.r_ext / voltage - self.r_ext
    
    def get_force(self):
        r_sen = self.get_resistance()
        if r_sen == float('inf'):
            return 0.0
        
        return self.a * (r_sen ** self.b)
        
        