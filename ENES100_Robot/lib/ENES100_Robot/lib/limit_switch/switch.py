from machine import Pin


class Switch:
    def __init__(self, pin_num:int, active_low:bool = True):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP) if active_low else Pin(pin_num, Pin.IN, Pin.PULL_DOWN)
        self.active_low = active_low
    
    def pressed(self):
        return self.pin.value() == 0 if self.active_low else self.pin.value() == 1